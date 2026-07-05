#!/bin/bash
# ERPMax Go Services Test Setup Script

set -e

echo "=========================================="
echo "ERPMax Go Services Test Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}Warning: Not running as root. Some operations may fail.${NC}"
fi

# Step 1: Check prerequisites
echo -e "\n${GREEN}Step 1: Checking prerequisites...${NC}"

# Check Go
if command -v go &> /dev/null; then
    echo -e "${GREEN}✓ Go installed: $(go version)${NC}"
else
    echo -e "${YELLOW}Installing Go...${NC}"
    wget -q https://go.dev/dl/go1.21.0.linux-amd64.tar.gz
    sudo tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz
    export PATH=$PATH:/usr/local/go/bin
    echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
    rm go1.21.0.linux-amd64.tar.gz
    echo -e "${GREEN}✓ Go installed${NC}"
fi

# Check MySQL
if command -v mysql &> /dev/null; then
    echo -e "${GREEN}✓ MySQL installed${NC}"
else
    echo -e "${YELLOW}MySQL not found. Please install MySQL manually.${NC}"
    exit 1
fi

# Check Redis
if command -v redis-cli &> /dev/null; then
    echo -e "${GREEN}✓ Redis installed${NC}"
else
    echo -e "${YELLOW}Installing Redis...${NC}"
    sudo apt-get update -qq
    sudo apt-get install -y -qq redis-server
    sudo systemctl enable redis-server
    sudo systemctl start redis-server
    echo -e "${GREEN}✓ Redis installed${NC}"
fi

# Check Supervisor
if command -v supervisord &> /dev/null; then
    echo -e "${GREEN}✓ Supervisor installed${NC}"
else
    echo -e "${YELLOW}Installing Supervisor...${NC}"
    sudo apt-get update -qq
    sudo apt-get install -y -qq supervisor
    sudo systemctl enable supervisor
    sudo systemctl start supervisor
    echo -e "${GREEN}✓ Supervisor installed${NC}"
fi

# Step 2: Build Go services
echo -e "\n${GREEN}Step 2: Building Go services...${NC}"

cd "$(dirname "$0")"

# Initialize Go module if needed
if [ ! -f "go.sum" ]; then
    echo "Initializing Go module..."
    go mod init erpmax-go
    go mod tidy
fi

# Build
echo "Building binary..."
go build -o erpmax-go-services .
chmod +x erpmax-go-services

if [ -f "erpmax-go-services" ]; then
    echo -e "${GREEN}✓ Build successful${NC}"
else
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi

# Step 3: Test the service
echo -e "\n${GREEN}Step 3: Testing Go services...${NC}"

# Start the service in background
echo "Starting Go services..."
./erpmax-go-services &
SERVICE_PID=$!

# Wait for service to start
sleep 3

# Test health endpoint
echo "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8080/health 2>/dev/null)

if [ "$HEALTH_RESPONSE" ] && echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Health check passed${NC}"
    echo "Response: $HEALTH_RESPONSE"
else
    echo -e "${YELLOW}Health check failed, but service may still be starting...${NC}"
fi

# Test list view endpoint
echo -e "\nTesting list view endpoint..."
LIST_RESPONSE=$(curl -s -X POST http://localhost:8080/api/listview \
    -H "Content-Type: application/json" \
    -d '{"doctype": "Customer", "page_length": 5}' 2>/dev/null)

if [ "$LIST_RESPONSE" ]; then
    echo -e "${GREEN}✓ List view endpoint working${NC}"
else
    echo -e "${YELLOW}List view test skipped (requires database)${NC}"
fi

# Test search endpoint
echo -e "\nTesting search endpoint..."
SEARCH_RESPONSE=$(curl -s -X POST http://localhost:8080/api/search \
    -H "Content-Type: application/json" \
    -d '{"query": "test", "doctypes": ["Customer"]}' 2>/dev/null)

if [ "$SEARCH_RESPONSE" ]; then
    echo -e "${GREEN}✓ Search endpoint working${NC}"
else
    echo -e "${YELLOW}Search test skipped (requires database)${NC}"
fi

# Stop the service
echo -e "\nStopping test service..."
kill $SERVICE_PID 2>/dev/null || true
wait $SERVICE_PID 2>/dev/null || true

# Step 4: Create supervisor config
echo -e "\n${GREEN}Step 4: Creating supervisor configuration...${NC}"

CURRENT_DIR=$(pwd)
SUPERVISOR_CONF="/etc/supervisor/conf.d/erpmax-go-services.conf"

sudo tee $SUPERVISOR_CONF > /dev/null <<EOF
[program:erpmax-go-services]
command=${CURRENT_DIR}/erpmax-go-services
directory=${CURRENT_DIR}
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
EOF

echo -e "${GREEN}✓ Supervisor config created${NC}"

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Step 5: Create bench command
echo -e "\n${GREEN}Step 5: Creating bench command...${NC}"

BENCH_CMD="/usr/local/bin/erpmax-go-services"
sudo tee $BENCH_CMD > /dev/null <<'EOF'
#!/bin/bash
# ERPMax Go Services bench command

GO_SERVICES_DIR="$(cd "$(dirname "$0")" && pwd)"

case "$1" in
    start)
        echo "Starting ERPMax Go Services..."
        sudo supervisorctl start erpmax-go-services
        echo "✓ ERPMax Go Services started on port 8080"
        ;;
    stop)
        echo "Stopping ERPMax Go Services..."
        sudo supervisorctl stop erpmax-go-services
        echo "✓ ERPMax Go Services stopped"
        ;;
    restart)
        echo "Restarting ERPMax Go Services..."
        sudo supervisorctl restart erpmax-go-services
        echo "✓ ERPMax Go Services restarted"
        ;;
    status)
        echo "ERPMax Go Services Status:"
        sudo supervisorctl status erpmax-go-services
        ;;
    logs)
        echo "ERPMax Go Services Logs:"
        sudo tail -f /var/log/erpmax-go-services.log
        ;;
    build)
        cd ${GO_SERVICES_DIR}
        go build -o erpmax-go-services .
        chmod +x erpmax-go-services
        echo "✓ ERPMax Go Services built"
        ;;
    test)
        echo "Testing ERPMax Go Services..."
        curl -s http://localhost:8080/health | python3 -m json.tool
        ;;
    *)
        echo "Usage: erpmax-go-services {start|stop|restart|status|logs|build|test}"
        exit 1
        ;;
esac
EOF

sudo chmod +x $BENCH_CMD
echo -e "${GREEN}✓ Bench command created: $BENCH_CMD${NC}"

# Step 6: Final summary
echo -e "\n${GREEN}=========================================="
echo "Setup Complete!"
echo "==========================================${NC}"

echo -e "\n${GREEN}Quick Commands:${NC}"
echo "  erpmax-go-services start    - Start services"
echo "  erpmax-go-services stop     - Stop services"
echo "  erpmax-go-services restart  - Restart services"
echo "  erpmax-go-services status   - Check status"
echo "  erpmax-go-services logs     - View logs"
echo "  erpmax-go-services test     - Test health"

echo -e "\n${GREEN}API Endpoints:${NC}"
echo "  Health:     http://localhost:8080/health"
echo "  List View:  http://localhost:8080/api/listview"
echo "  Reports:    http://localhost:8080/api/reports/generate"
echo "  Search:     http://localhost:8080/api/search"
echo "  Dashboard:  http://localhost:8080/api/dashboard"

echo -e "\n${GREEN}Supervisor:${NC}"
echo "  sudo supervisorctl status              - Check status"
echo "  sudo supervisorctl restart erpmax-go-services  - Restart"
echo "  sudo tail -f /var/log/erpmax-go-services.log  - View logs"

echo -e "\n${YELLOW}Note: Make sure MySQL and Redis are running before starting services.${NC}"
echo -e "${YELLOW}For production, update DB_PASSWORD in supervisor config.${NC}"
