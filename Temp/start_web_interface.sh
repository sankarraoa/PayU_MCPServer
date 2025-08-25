#!/bin/bash

# PayU Finance AI Orchestrator - Web Interface Startup Script

echo "🚀 Starting PayU Finance AI Orchestrator Web Interface..."
echo "================================================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment: $VIRTUAL_ENV"
else
    echo "⚠️  Warning: No virtual environment detected"
    echo "   Consider running: source .venv/bin/activate"
fi

# Install web requirements
echo "📦 Installing web server requirements..."
pip install -r requirements_web.txt

# Check if required files exist
echo "🔍 Checking required files..."

if [[ ! -f "ai_orchestrator_v2.py" ]]; then
    echo "❌ ai_orchestrator_v2.py not found!"
    echo "   Please make sure your orchestrator file is in this directory"
    exit 1
fi

if [[ ! -f "orchestrator_web_interface.html" ]]; then
    echo "❌ orchestrator_web_interface.html not found!"
    exit 1
fi

if [[ ! -f "llm_response_fixer.py" ]]; then
    echo "⚠️  llm_response_fixer.py not found - some queries may fail"
fi

echo "✅ All required files found"

# Check environment variables
echo "🔧 Checking environment..."
if [[ -z "$TOQAN_API_KEY" ]]; then
    echo "⚠️  TOQAN_API_KEY not set - using default"
    echo "   Set it with: export TOQAN_API_KEY=your_actual_key"
fi

# Start the servers
echo "🌐 Starting servers..."
echo "   🔧 Make sure your MCP server is running on port 5000"
echo "   📱 Web interface will be available at: http://localhost:8080"
echo "   🛑 Press Ctrl+C to stop"
echo ""

# Start the web server
python3 orchestrator_web_server.py
