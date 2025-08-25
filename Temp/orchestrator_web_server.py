#!/usr/bin/env python3
"""
Web Server for PayU Finance AI Orchestrator
Serves the web interface and handles orchestrator API calls
"""

from flask import Flask, request, jsonify, send_from_directory
import os
import json
import logging
from flask_cors import CORS

# Import your existing orchestrator
from ai_orchestrator import EnhancedAIOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orchestrator-web-server")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the orchestrator
TOQAN_API_KEY = os.getenv('TOQAN_API_KEY', 'your_api_key_here')
orchestrator = EnhancedAIOrchestrator(TOQAN_API_KEY)

@app.route('/')
def index():
    """Serve the main web interface"""
    return send_from_directory('.', 'orchestrator_web_interface.html')

@app.route('/api/orchestrator/complex', methods=['POST'])
def process_complex_query():
    """
    Process complex queries through the AI Orchestrator
    
    Expected JSON body:
    {
        "query": "Get KYC details for user with phone 9845267602"
    }
    
    Returns:
    {
        "success": true/false,
        "user_query": "original query",
        "conversation_id": "uuid",
        "reasoning": {...},
        "executed_steps": [...],
        "total_steps_completed": 2,
        "total_steps_planned": 2,
        "error": "error message if failed"
    }
    """
    try:
        # Get request data
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'query' field in request body"
            }), 400
        
        user_query = data['query'].strip()
        if not user_query:
            return jsonify({
                "success": False,
                "error": "Query cannot be empty"
            }), 400
        
        logger.info(f"Processing web query: {user_query}")
        
        # Process the query through the orchestrator
        result = orchestrator.process_complex_query(user_query)
        
        # Log the result
        if result.get('success'):
            steps_completed = len(result.get('executed_steps', []))
            logger.info(f"Query processed successfully: {steps_completed} steps completed")
        else:
            logger.error(f"Query failed: {result.get('error')}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}",
            "user_query": data.get('query', '') if 'data' in locals() else ''
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "PayU Finance AI Orchestrator Web Server",
        "orchestrator_ready": orchestrator is not None
    })

@app.route('/api/tools', methods=['GET'])
def list_tools():
    """List available tools"""
    tools = list(orchestrator.tools_catalog.keys()) if orchestrator else []
    return jsonify({
        "tools": tools,
        "total_tools": len(tools)
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Check if required files exist
    if not os.path.exists('orchestrator_web_interface.html'):
        logger.error("orchestrator_web_interface.html not found!")
        print("❌ Please make sure orchestrator_web_interface.html is in the same directory")
        exit(1)
    
    if not os.path.exists('ai_orchestrator_v2.py'):
        logger.error("ai_orchestrator_v2.py not found!")
        print("❌ Please make sure ai_orchestrator_v2.py is in the same directory")
        exit(1)
    
    print("🚀 Starting PayU Finance AI Orchestrator Web Server...")
    print("📱 Web Interface: http://localhost:8080")
    print("🔧 API Health Check: http://localhost:8080/api/health")
    print("📊 Tools List: http://localhost:8080/api/tools")
    print("\n💡 Make sure your MCP server is running on port 5000")
    print("🛑 Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=8080, debug=True)
