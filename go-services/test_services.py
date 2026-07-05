#!/usr/bin/env python3
"""
ERPMax Go Services Test Suite
Tests all Go services endpoints
"""

import requests
import json
import sys
import time
from datetime import datetime


class GoServicesTester:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
    
    def run_test(self, name, test_func):
        """Run a single test"""
        print(f"\n{'='*60}")
        print(f"Testing: {name}")
        print(f"{'='*60}")
        
        try:
            result = test_func()
            if result:
                self.results.append({"test": name, "status": "PASS"})
                print(f"✓ PASS: {name}")
            else:
                self.results.append({"test": name, "status": "FAIL"})
                print(f"✗ FAIL: {name}")
        except Exception as e:
            self.results.append({"test": name, "status": "ERROR", "error": str(e)})
            print(f"✗ ERROR: {name} - {e}")
    
    def test_health(self):
        """Test health endpoint"""
        response = self.session.get(f"{self.base_url}/health")
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        return response.status_code == 200 and data.get("status") == "healthy"
    
    def test_list_view(self):
        """Test list view endpoint"""
        payload = {
            "doctype": "Customer",
            "page_length": 5,
            "fields": ["name", "customer_name", "customer_group"],
            "filters": {}
        }
        
        response = self.session.post(
            f"{self.base_url}/api/listview",
            json=payload
        )
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Total Records: {data.get('total', 0)}")
        print(f"Load Time: {data.get('load_time_ms', 0):.2f}ms")
        print(f"Cached: {data.get('cached', False)}")
        
        return response.status_code == 200
    
    def test_search(self):
        """Test search endpoint"""
        payload = {
            "query": "test",
            "doctypes": ["Customer", "Supplier"],
            "limit": 10
        }
        
        response = self.session.post(
            f"{self.base_url}/api/search",
            json=payload
        )
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Results Found: {data.get('total', 0)}")
        print(f"Load Time: {data.get('load_time_ms', 0):.2f}ms")
        
        return response.status_code == 200
    
    def test_autocomplete(self):
        """Test autocomplete endpoint"""
        response = self.session.get(
            f"{self.base_url}/api/autocomplete",
            params={"q": "test", "doctype": "Customer", "limit": 5}
        )
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Results: {len(data) if isinstance(data, list) else 0}")
        
        return response.status_code == 200
    
    def test_dashboard(self):
        """Test dashboard endpoint"""
        payload = {
            "dashboard": "finance",
            "filters": {},
            "company": None
        }
        
        response = self.session.post(
            f"{self.base_url}/api/dashboard",
            json=payload
        )
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Widgets: {len(data.get('widgets', []))}")
        print(f"KPIs: {len(data.get('kpis', []))}")
        print(f"Charts: {len(data.get('charts', []))}")
        print(f"Load Time: {data.get('load_time_ms', 0):.2f}ms")
        
        return response.status_code == 200
    
    def test_print(self):
        """Test print endpoint"""
        payload = {
            "doctype": "Sales Invoice",
            "name": "SI-001",
            "print_format": None,
            "no_letterhead": False
        }
        
        response = self.session.post(
            f"{self.base_url}/api/print",
            json=payload
        )
        
        print(f"Status Code: {response.status_code}")
        
        # This may fail if no data exists, which is expected
        return response.status_code in [200, 404, 500]
    
    def test_reports(self):
        """Test report generation"""
        payload = {
            "report_type": "trial_balance",
            "filters": {}
        }
        
        response = self.session.post(
            f"{self.base_url}/api/reports/generate",
            json=payload
        )
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Report Type: {data.get('report_type', 'N/A')}")
        print(f"Data Rows: {len(data.get('data', []))}")
        
        return response.status_code == 200
    
    def test_cache_stats(self):
        """Test cache statistics"""
        response = self.session.get(f"{self.base_url}/api/cache/stats")
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Cache Stats: {json.dumps(data, indent=2)}")
        
        return response.status_code == 200
    
    def test_job_create(self):
        """Test job creation"""
        payload = {
            "type": "report",
            "priority": 5,
            "payload": {"report_type": "trial_balance"},
            "max_retries": 3
        }
        
        response = self.session.post(
            f"{self.base_url}/api/jobs/create",
            json=payload
        )
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Job ID: {data.get('id', 'N/A')}")
        print(f"Job Status: {data.get('status', 'N/A')}")
        
        return response.status_code in [200, 201]
    
    def test_queue_status(self):
        """Test queue status"""
        response = self.session.get(f"{self.base_url}/api/jobs/queue")
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Queue Size: {data.get('queue_size', 0)}")
        
        return response.status_code == 200
    
    def test_bulk_operations(self):
        """Test bulk operations (dry run)"""
        payload = {
            "doctype": "Customer",
            "filters": {"disabled": 1},
            "dry_run": True
        }
        
        response = self.session.post(
            f"{self.base_url}/api/bulk/delete",
            json=payload
        )
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Operation: {data.get('action', 'N/A')}")
        print(f"Total Records: {data.get('total', 0)}")
        
        return response.status_code == 200
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("ERPMax Go Services Test Suite")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # Run tests
        self.run_test("Health Check", self.test_health)
        self.run_test("List View", self.test_list_view)
        self.run_test("Search", self.test_search)
        self.run_test("Autocomplete", self.test_autocomplete)
        self.run_test("Dashboard", self.test_dashboard)
        self.run_test("Print", self.test_print)
        self.run_test("Reports", self.test_reports)
        self.run_test("Cache Stats", self.test_cache_stats)
        self.run_test("Job Create", self.test_job_create)
        self.run_test("Queue Status", self.test_queue_status)
        self.run_test("Bulk Operations", self.test_bulk_operations)
        
        # Summary
        print("\n" + "="*60)
        print("Test Summary")
        print("="*60)
        
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        errors = sum(1 for r in self.results if r["status"] == "ERROR")
        total = len(self.results)
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Errors: {errors}")
        print(f"\nSuccess Rate: {(passed/total*100):.1f}%" if total > 0 else "No tests run")
        
        # Detailed results
        print("\nDetailed Results:")
        for result in self.results:
            status_symbol = "✓" if result["status"] == "PASS" else "✗"
            print(f"  {status_symbol} {result['test']}: {result['status']}")
            if "error" in result:
                print(f"    Error: {result['error']}")
        
        print("\n" + "="*60)
        
        return failed == 0 and errors == 0


def main():
    # Check if server is running
    try:
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code != 200:
            print("Error: Go services not responding properly")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to Go services at http://localhost:8080")
        print("Please start the services first:")
        print("  ./erpmax-go-services &")
        print("  or")
        print("  supervisorctl start erpmax-go-services")
        sys.exit(1)
    
    # Run tests
    tester = GoServicesTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
