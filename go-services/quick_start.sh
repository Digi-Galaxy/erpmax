#!/bin/bash
# ERPMax Go Services Quick Start Demo

echo "=========================================="
echo "ERPMax Go Services - Quick Start Demo"
echo "=========================================="

# Make scripts executable
chmod +x test_setup.sh
chmod +x test_services.py

echo ""
echo "This script will:"
echo "1. Build Go services"
echo "2. Start the service"
echo "3. Run tests"
echo "4. Show demo results"
echo ""

read -p "Press Enter to continue..."

# Step 1: Build
echo ""
echo "Step 1: Building Go services..."
go build -o erpmax-go-services .
chmod +x erpmax-go-services

if [ ! -f "erpmax-go-services" ]; then
    echo "Build failed!"
    exit 1
fi

echo "✓ Build successful"

# Step 2: Start service
echo ""
echo "Step 2: Starting Go services..."

# Kill any existing instance
pkill -f erpmax-go-services 2>/dev/null || true

# Start in background
./erpmax-go-services &
SERVICE_PID=$!

echo "Service started with PID: $SERVICE_PID"

# Wait for service to start
echo "Waiting for service to start..."
sleep 3

# Step 3: Test health
echo ""
echo "Step 3: Testing health endpoint..."
HEALTH=$(curl -s http://localhost:8080/health)
echo "Health Response: $HEALTH"

# Step 4: Demo operations
echo ""
echo "Step 4: Running demo operations..."

echo ""
echo "--- List View Demo ---"
curl -s -X POST http://localhost:8080/api/listview \
    -H "Content-Type: application/json" \
    -d '{"doctype": "Customer", "page_length": 3}' | python3 -m json.tool 2>/dev/null || echo "Demo requires database"

echo ""
echo "--- Search Demo ---"
curl -s -X POST http://localhost:8080/api/search \
    -H "Content-Type: application/json" \
    -d '{"query": "test", "doctypes": ["Customer"]}' | python3 -m json.tool 2>/dev/null || echo "Demo requires database"

echo ""
echo "--- Dashboard Demo ---"
curl -s -X POST http://localhost:8080/api/dashboard \
    -H "Content-Type: application/json" \
    -d '{"dashboard": "finance"}' | python3 -m json.tool 2>/dev/null || echo "Demo requires database"

echo ""
echo "--- Cache Stats Demo ---"
curl -s http://localhost:8080/api/cache/stats | python3 -m json.tool 2>/dev/null || echo "Cache stats unavailable"

echo ""
echo "--- Job Queue Demo ---"
curl -s http://localhost:8080/api/jobs/queue | python3 -m json.tool 2>/dev/null || echo "Job queue unavailable"

# Step 5: Show status
echo ""
echo "Step 5: Service Status"
echo "PID: $SERVICE_PID"
echo "Port: 8080"
echo "Health: http://localhost:8080/health"

# Step 6: Cleanup prompt
echo ""
echo "=========================================="
echo "Demo Complete!"
echo "=========================================="
echo ""
echo "The Go services are running on port 8080."
echo ""
echo "To stop the service:"
echo "  kill $SERVICE_PID"
echo ""
echo "To run full tests:"
echo "  python3 test_services.py"
echo ""
echo "To install with supervisor:"
echo "  sudo ./test_setup.sh"
echo ""
echo "API Endpoints:"
echo "  http://localhost:8080/health"
echo "  http://localhost:8080/api/listview"
echo "  http://localhost:8080/api/search"
echo "  http://localhost:8080/api/dashboard"
echo "  http://localhost:8080/api/reports/generate"
echo ""

read -p "Press Enter to stop the demo service..."
kill $SERVICE_PID 2>/dev/null || true
echo "Service stopped."
