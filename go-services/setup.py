#!/usr/bin/env python3
"""
ERPMax Go Services Installer
Auto-installs Go services with bench and supervisor
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


class GoServicesInstaller:
    def __init__(self):
        self.bench_path = self.get_bench_path()
        self.apps_path = os.path.join(self.bench_path, "apps")
        self.erpmax_path = os.path.join(self.apps_path, "erpmax")
        self.go_services_path = os.path.join(self.erpmax_path, "go-services")
        self.supervisor_conf = "/etc/supervisor/conf.d"
        
    def get_bench_path(self):
        """Get the bench path"""
        # Check if we're in a bench environment
        current_dir = os.getcwd()
        if "frappe-bench" in current_dir:
            return current_dir
        # Try to find bench
        for path in ["/home/dg/frappe-bench", "/opt/frappe-bench", os.path.expanduser("~/frappe-bench")]:
            if os.path.exists(path):
                return path
        return current_dir
    
    def check_prerequisites(self):
        """Check if all prerequisites are installed"""
        print("Checking prerequisites...")
        
        # Check Go
        try:
            result = subprocess.run(["go", "version"], capture_output=True, text=True)
            print(f"✓ Go installed: {result.stdout.strip()}")
        except FileNotFoundError:
            print("✗ Go not found. Installing...")
            self.install_go()
        
        # Check MySQL
        try:
            result = subprocess.run(["mysql", "--version"], capture_output=True, text=True)
            print(f"✓ MySQL installed: {result.stdout.strip()}")
        except FileNotFoundError:
            print("✗ MySQL not found")
        
        # Check Redis
        try:
            result = subprocess.run(["redis-cli", "ping"], capture_output=True, text=True)
            print(f"✓ Redis installed")
        except FileNotFoundError:
            print("✗ Redis not found. Installing...")
            self.install_redis()
        
        # Check Supervisor
        try:
            result = subprocess.run(["supervisord", "--version"], capture_output=True, text=True)
            print(f"✓ Supervisor installed")
        except FileNotFoundError:
            print("✗ Supervisor not found. Installing...")
            self.install_supervisor()
    
    def install_go(self):
        """Install Go"""
        print("Installing Go...")
        subprocess.run(["wget", "https://go.dev/dl/go1.21.0.linux-amd64.tar.gz"], check=True)
        subprocess.run(["sudo", "tar", "-C", "/usr/local", "-xzf", "go1.21.0.linux-amd64.tar.gz"], check=True)
        
        # Add to PATH
        path_export = 'export PATH=$PATH:/usr/local/go/bin'
        bashrc_path = os.path.expanduser("~/.bashrc")
        with open(bashrc_path, "a") as f:
            f.write(f"\n{path_export}\n")
        
        os.environ["PATH"] = os.environ.get("PATH", "") + ":/usr/local/go/bin"
        os.remove("go1.21.0.linux-amd64.tar.gz")
        print("✓ Go installed successfully")
    
    def install_redis(self):
        """Install Redis"""
        print("Installing Redis...")
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y", "redis-server"], check=True)
        subprocess.run(["sudo", "systemctl", "enable", "redis-server"], check=True)
        subprocess.run(["sudo", "systemctl", "start", "redis-server"], check=True)
        print("✓ Redis installed successfully")
    
    def install_supervisor(self):
        """Install Supervisor"""
        print("Installing Supervisor...")
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y", "supervisor"], check=True)
        subprocess.run(["sudo", "systemctl", "enable", "supervisor"], check=True)
        subprocess.run(["sudo", "systemctl", "start", "supervisor"], check=True)
        print("✓ Supervisor installed successfully")
    
    def build_go_services(self):
        """Build Go services"""
        print("Building Go services...")
        
        if not os.path.exists(self.go_services_path):
            print("✗ Go services directory not found")
            return False
        
        os.chdir(self.go_services_path)
        
        # Initialize Go module
        if not os.path.exists("go.sum"):
            subprocess.run(["go", "mod", "init", "erpmax-go"], check=True)
            subprocess.run(["go", "mod", "tidy"], check=True)
        
        # Build
        subprocess.run(["go", "build", "-o", "erpmax-go-services", "."], check=True)
        
        # Make executable
        os.chmod("erpmax-go-services", 0o755)
        
        print("✓ Go services built successfully")
        return True
    
    def create_supervisor_config(self):
        """Create supervisor configuration"""
        print("Creating supervisor configuration...")
        
        config_content = f"""[program:erpmax-go-services]
command={self.go_services_path}/erpmax-go-services
directory={self.go_services_path}
user=root
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=30
redirect_stderr=true
stdout_logfile=/var/log/erpmax-go-services.log
stderr_logfile=/var/log/erpmax-go-services-error.log
environment=
    PORT="8080",
    DB_HOST="localhost",
    DB_PORT="3306",
    DB_USER="root",
    DB_PASSWORD="",
    DB_NAME="erpmax",
    REDIS_ADDR="localhost:6379",
    REDIS_PASSWORD="",
    REDIS_DB="0",
    WORKER_COUNT="10",
    BATCH_SIZE="1000",
    CACHE_TTL="3600"
"""
        
        config_path = os.path.join(self.supervisor_conf, "erpmax-go-services.conf")
        
        try:
            with open(config_path, "w") as f:
                f.write(config_content)
            subprocess.run(["sudo", "supervisorctl", "reread"], check=True)
            subprocess.run(["sudo", "supervisorctl", "update"], check=True)
            print(f"✓ Supervisor config created: {config_path}")
        except PermissionError:
            # Create in local directory if no sudo
            local_config = os.path.join(self.go_services_path, "erpmax-go-services.conf")
            with open(local_config, "w") as f:
                f.write(config_content)
            print(f"✓ Supervisor config created (local): {local_config}")
            print("  Run: sudo supervisorctl reread && sudo supervisorctl update")
    
    def create_bench_command(self):
        """Create bench command for Go services"""
        print("Creating bench command...")
        
        bench_cmd = """#!/bin/bash
# ERPMax Go Services bench command

case "$1" in
    start)
        echo "Starting ERPMax Go Services..."
        if command -v supervisord &> /dev/null; then
            sudo supervisorctl start erpmax-go-services
        else
            cd {go_services_path}
            ./erpmax-go-services &
            echo $! > erpmax-go-services.pid
        fi
        echo "✓ ERPMax Go Services started on port 8080"
        ;;
    stop)
        echo "Stopping ERPMax Go Services..."
        if command -v supervisord &> /dev/null; then
            sudo supervisorctl stop erpmax-go-services
        else
            if [ -f erpmax-go-services.pid ]; then
                kill $(cat erpmax-go-services.pid)
                rm erpmax-go-services.pid
            fi
        fi
        echo "✓ ERPMax Go Services stopped"
        ;;
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    status)
        if command -v supervisord &> /dev/null; then
            sudo supervisorctl status erpmax-go-services
        else
            if [ -f erpmax-go-services.pid ] && kill -0 $(cat erpmax-go-services.pid) 2>/dev/null; then
                echo "ERPMax Go Services is running (PID: $(cat erpmax-go-services.pid))"
            else
                echo "ERPMax Go Services is not running"
            fi
        fi
        ;;
    logs)
        if command -v supervisord &> /dev/null; then
            sudo tail -f /var/log/erpmax-go-services.log
        else
            tail -f {go_services_path}/erpmax-go-services.log
        fi
        ;;
    build)
        cd {go_services_path}
        go build -o erpmax-go-services .
        chmod +x erpmax-go-services
        echo "✓ ERPMax Go Services built"
        ;;
    install)
        cd {go_services_path}
        python3 setup.py
        ;;
    *)
        echo "Usage: $0 {{start|stop|restart|status|logs|build|install}}"
        exit 1
        ;;
esac
""".format(go_services_path=self.go_services_path)
        
        cmd_path = os.path.join(self.bench_path, "erpmax-go-services")
        with open(cmd_path, "w") as f:
            f.write(bench_cmd)
        os.chmod(cmd_path, 0o755)
        
        print(f"✓ Bench command created: {cmd_path}")
    
    def add_to_erpmax_settings(self):
        """Add Go services settings to ERPMax"""
        print("Adding Go services settings...")
        
        settings_content = """
# Go Services Configuration
go_services_enabled = True
go_services_url = "http://localhost:8080"
go_services_timeout = 30
"""
        
        sites_path = os.path.join(self.bench_path, "sites")
        common_site_config = os.path.join(sites_path, "common_site_config.json")
        
        import json
        
        if os.path.exists(common_site_config):
            with open(common_site_config, "r") as f:
                config = json.load(f)
        else:
            config = {}
        
        config["go_services_enabled"] = True
        config["go_services_url"] = "http://localhost:8080"
        config["go_services_timeout"] = 30
        
        with open(common_site_config, "w") as f:
            json.dump(config, f, indent=2)
        
        print("✓ Go services settings added to common_site_config.json")
    
    def install(self):
        """Main installation"""
        print("=" * 60)
        print("ERPMax Go Services Installer")
        print("=" * 60)
        
        self.check_prerequisites()
        
        if not self.build_go_services():
            print("Build failed!")
            return
        
        self.create_supervisor_config()
        self.create_bench_command()
        self.add_to_erpmax_settings()
        
        print("\n" + "=" * 60)
        print("Installation Complete!")
        print("=" * 60)
        print("\nTo start Go services:")
        print("  bench erpmax-go-services start")
        print("\nTo check status:")
        print("  bench erpmax-go-services status")
        print("\nTo view logs:")
        print("  bench erpmax-go-services logs")
        print("\nAPI will be available at: http://localhost:8080")
        print("Health check: http://localhost:8080/health")


if __name__ == "__main__":
    installer = GoServicesInstaller()
    installer.install()
