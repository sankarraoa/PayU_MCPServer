# File: http_server.py - Complete PayU Finance HTTP Server with AI Orchestrator
import logging
import os
from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
import traceback
from sqlalchemy import text

# Import your existing database components with aliases to avoid name collisions
from db.base_connector import load_db_config
from db.postgres_connector import PostgresConnector
from repository.user_repository import (
    get_users as repo_get_users, 
    get_additional_info as repo_get_additional_info, 
    get_user_pans as repo_get_user_pans, 
    get_user_aadhaar_kyc as repo_get_user_aadhaar_kyc,
    get_user_ckyc as repo_get_user_ckyc,
    get_user_header_details as repo_get_user_header_details,
    get_aml_details as repo_get_aml_details,
    get_user_address as repo_get_user_address
)

# Import AI Orchestrator
from ai_orchestrator import EnhancedAIOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("payu-fin-http")

# Simple HTML test page for testing individual APIs
TEST_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>PayU Finance API Tester</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; }
        .endpoint { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        button { background: #007bff; color: white; padding: 8px 15px; border: none; border-radius: 3px; cursor: pointer; }
        button:hover { background: #0056b3; }
        input { padding: 5px; margin: 5px; border: 1px solid #ddd; border-radius: 3px; }
        .result { margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 3px; white-space: pre-wrap; font-family: monospace; font-size: 12px; max-height: 300px; overflow-y: auto; }
        .error { background: #f8d7da; color: #721c24; }
        .success { background: #d4edda; color: #155724; }
        .loading { background: #fff3cd; color: #856404; }
        .nav-button { background: #28a745; margin: 10px 5px; }
        .nav-button:hover { background: #1e7e34; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏦 PayU Finance API Tester</h1>
        <p><strong>Status:</strong> <span id="serverStatus">Checking...</span></p>
        
        <div style="margin: 20px 0;">
            <button class="nav-button" onclick="window.location.href='/orchestrator'">🤖 AI Orchestrator Interface</button>
            <button class="nav-button" onclick="window.location.href='/'">🔧 API Tester</button>
        </div>
        
        <div class="endpoint">
            <h3>🔍 Search Users</h3>
            <input type="text" id="searchTerm" placeholder="Enter phone, email, name, or ID" value="9845267602">
            <button onclick="searchUsers()">Search</button>
            <div id="searchResult" class="result"></div>
        </div>
        
        <div class="endpoint">
            <h3>👤 Get User Details</h3>
            <input type="number" id="userId1" placeholder="User ID" value="">
            <button onclick="getUserDetails()">Get Details</button>
            <div id="detailsResult" class="result"></div>
        </div>
        
        <div class="endpoint">
            <h3>📋 Get KYC Info</h3>
            <input type="number" id="userId2" placeholder="User ID" value="">
            <button onclick="getKycInfo()">Get KYC</button>
            <div id="kycResult" class="result"></div>
        </div>
        
        <div class="endpoint">
            <h3>🚨 Get AML Status</h3>
            <input type="number" id="userId3" placeholder="User ID" value="">
            <button onclick="getAmlStatus()">Get AML</button>
            <div id="amlResult" class="result"></div>
        </div>
        
        <div class="endpoint">
            <h3>🏠 Get User Address</h3>
            <input type="number" id="userId4" placeholder="User ID" value="">
            <button onclick="getUserAddress()">Get Address</button>
            <div id="addressResult" class="result"></div>
        </div>
        
        <div class="endpoint">
            <h3>🤖 Test AI Orchestrator</h3>
            <input type="text" id="orchestratorQuery" placeholder="Enter complex query" value="Get KYC details for user with phone 9845267602" style="width: 400px;">
            <button onclick="testOrchestrator()">Process Query</button>
            <div id="orchestratorResult" class="result"></div>
        </div>
    </div>

    <script>
        async function apiCall(endpoint, data = null) {
            try {
                const options = {
                    method: data ? 'POST' : 'GET',
                    headers: {'Content-Type': 'application/json'}
                };
                if (data) options.body = JSON.stringify(data);
                
                const response = await fetch(endpoint, options);
                return await response.json();
            } catch (error) {
                return {error: error.message, success: false};
            }
        }
        
        function displayResult(elementId, result) {
            const element = document.getElementById(elementId);
            element.textContent = JSON.stringify(result, null, 2);
            element.className = 'result ' + (result.success === false || result.error ? 'error' : 'success');
        }
        
        function showLoading(elementId) {
            const element = document.getElementById(elementId);
            element.textContent = 'Loading...';
            element.className = 'result loading';
        }
        
        async function searchUsers() {
            showLoading('searchResult');
            const searchTerm = document.getElementById('searchTerm').value;
            const result = await apiCall('/api/tools/search_users', {search_term: searchTerm});
            displayResult('searchResult', result);
            
            // Auto-fill user IDs if users found
            if (result.users && result.users.length > 0) {
                const userId = result.users[0].id;
                document.getElementById('userId1').value = userId;
                document.getElementById('userId2').value = userId;
                document.getElementById('userId3').value = userId;
                document.getElementById('userId4').value = userId;
            }
        }
        
        async function getUserDetails() {
            showLoading('detailsResult');
            const userId = document.getElementById('userId1').value;
            const result = await apiCall('/api/tools/get_user_details', {user_id: parseInt(userId)});
            displayResult('detailsResult', result);
        }
        
        async function getKycInfo() {
            showLoading('kycResult');
            const userId = document.getElementById('userId2').value;
            const result = await apiCall('/api/tools/get_user_kyc_info', {user_id: parseInt(userId)});
            displayResult('kycResult', result);
        }
        
        async function getAmlStatus() {
            showLoading('amlResult');
            const userId = document.getElementById('userId3').value;
            const result = await apiCall('/api/tools/get_user_aml_status', {user_id: parseInt(userId)});
            displayResult('amlResult', result);
        }
        
        async function getUserAddress() {
            showLoading('addressResult');
            const userId = document.getElementById('userId4').value;
            const result = await apiCall('/api/tools/get_user_address', {user_id: parseInt(userId)});
            displayResult('addressResult', result);
        }
        
        async function testOrchestrator() {
            showLoading('orchestratorResult');
            const query = document.getElementById('orchestratorQuery').value;
            const result = await apiCall('/api/orchestrator/complex', {query: query});
            displayResult('orchestratorResult', result);
        }
        
        // Check server status on page load
        window.onload = async function() {
            const health = await apiCall('/health');
            const statusElement = document.getElementById('serverStatus');
            if (health.status === 'healthy') {
                statusElement.textContent = '✅ Server and Database Connected';
                statusElement.style.color = 'green';
            } else {
                statusElement.textContent = '❌ Server Issues: ' + (health.error || 'Unknown');
                statusElement.style.color = 'red';
            }
            
            const tools = await apiCall('/api/tools');
            console.log('Available tools:', tools);
        }
    </script>
</body>
</html>
"""

class PayUFinanceHTTPServer:
    """Complete HTTP server with AI Orchestrator integration"""
    
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.env = None
        self.db_conns = None
        
        # Initialize AI Orchestrator
        self.orchestrator = self._initialize_orchestrator()
        
        self._setup_routes()
        self._initialize_config()
        logger.info("PayU Finance HTTP Server with AI Orchestrator initialized")
    
    def _initialize_orchestrator(self):
        """Initialize the AI Orchestrator"""
        try:
            api_key = os.getenv('TOQAN_API_KEY', 'sk_f203979e694f67bb72ad235ba5fcb70976a41c87141a6d3386c3a7f3ef8bb61e0675f3cc25d0f12086dd2b472d4f9a045c1411bab04f18276dafefe50f9e')
            orchestrator = EnhancedAIOrchestrator(api_key)
            logger.info("✅ AI Orchestrator initialized successfully")
            return orchestrator
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI Orchestrator: {e}")
            logger.warning("🔧 Orchestrator will be disabled. Make sure ai_orchestrator_v2.py is available.")
            return None
    
    def _initialize_config(self):
        """Initialize database configuration"""
        try:
            self.env, self.db_conns = load_db_config()
            logger.info(f"✅ Database configuration loaded for environment: {self.env}")
        except Exception as e:
            logger.error(f"❌ Failed to load database configuration: {e}")
            raise
    
    def _get_fresh_connection(self):
        """Create a fresh database connection for each request"""
        try:
            pg_cfg = self.db_conns['pscore_postgres']
            connector = PostgresConnector(pg_cfg, environment=self.env)
            return connector
        except Exception as e:
            logger.error(f"❌ Failed to create database connection: {e}")
            raise
    
    def _setup_routes(self):
        """Setup all API routes"""
        
        @self.app.route('/')
        def home():
            """API test page"""
            return render_template_string(TEST_PAGE)
        
        @self.app.route('/orchestrator')
        def orchestrator_interface():
            """Serve the AI Orchestrator web interface"""
            try:
                return send_from_directory('.', 'orchestrator_web_interface.html')
            except FileNotFoundError:
                return jsonify({
                    "error": "orchestrator_web_interface.html not found",
                    "message": "Please make sure the orchestrator web interface file is in the same directory"
                }), 404
        
        @self.app.route('/health')
        def health_check():
            """Health check endpoint with database test"""
            try:
                connector = self._get_fresh_connection()
                with connector.get_conn() as conn:
                    result = conn.execute(text('SELECT 1 as test')).fetchone()
                    test_passed = result[0] == 1 if result else False
                
                connector.close()
                
                return jsonify({
                    "status": "healthy",
                    "service": "PayU Finance HTTP Server",
                    "version": "2.0.0",
                    "database": "connected" if test_passed else "connection_failed",
                    "environment": self.env,
                    "ai_orchestrator": "enabled" if self.orchestrator else "disabled",
                    "endpoints": {
                        "api_tester": "/",
                        "orchestrator_ui": "/orchestrator",
                        "health": "/health",
                        "tools": "/api/tools",
                        "orchestrator_api": "/api/orchestrator/complex"
                    }
                })
                
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return jsonify({
                    "status": "unhealthy",
                    "service": "PayU Finance HTTP Server",
                    "database": "disconnected",
                    "error": str(e)
                }), 500
        
        @self.app.route('/api/tools')
        def list_tools():
            """List available tools"""
            tools = [
                {
                    "name": "search_users",
                    "description": "Search for users by phone, email, name, or ID",
                    "endpoint": "/api/tools/search_users",
                    "method": "POST"
                },
                {
                    "name": "get_user_details", 
                    "description": "Get comprehensive user details",
                    "endpoint": "/api/tools/get_user_details",
                    "method": "POST"
                },
                {
                    "name": "get_user_kyc_info",
                    "description": "Get user KYC information", 
                    "endpoint": "/api/tools/get_user_kyc_info",
                    "method": "POST"
                },
                {
                    "name": "get_user_aml_status",
                    "description": "Get user AML status",
                    "endpoint": "/api/tools/get_user_aml_status", 
                    "method": "POST"
                },
                {
                    "name": "get_user_address",
                    "description": "Get user address information",
                    "endpoint": "/api/tools/get_user_address",
                    "method": "POST"
                }
            ]
            
            if self.orchestrator:
                tools.append({
                    "name": "ai_orchestrator",
                    "description": "Process complex queries with multi-tool coordination",
                    "endpoint": "/api/orchestrator/complex",
                    "method": "POST"
                })
            
            return jsonify({
                "tools": tools,
                "total_tools": len(tools),
                "ai_orchestrator_enabled": self.orchestrator is not None
            })
        
        # AI Orchestrator endpoint
        @self.app.route('/api/orchestrator/complex', methods=['POST'])
        def process_complex_query():
            """Process complex queries through the AI Orchestrator"""
            try:
                if not self.orchestrator:
                    return jsonify({
                        "success": False,
                        "error": "AI Orchestrator not initialized. Check server logs for details."
                    }), 503
                    
                data = request.get_json()
                if not data or 'query' not in data:
                    return jsonify({
                        "success": False,
                        "error": "Missing 'query' field in request body",
                        "expected_format": {"query": "Your complex query here"}
                    }), 400
                
                user_query = data['query'].strip()
                if not user_query:
                    return jsonify({
                        "success": False,
                        "error": "Query cannot be empty"
                    }), 400
                
                logger.info(f"🤖 Processing orchestrator query: {user_query}")
                
                # Process the query through the AI Orchestrator
                result = self.orchestrator.process_complex_query(user_query)
                
                # Log result
                if result.get('success'):
                    steps_completed = len(result.get('executed_steps', []))
                    logger.info(f"✅ Orchestrator query completed: {steps_completed} steps")
                else:
                    logger.error(f"❌ Orchestrator query failed: {result.get('error')}")
                
                return jsonify(result)
                
            except Exception as e:
                logger.error(f"❌ Error in orchestrator endpoint: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                return jsonify({
                    "success": False,
                    "error": f"Server error: {str(e)}",
                    "user_query": data.get('query', '') if 'data' in locals() else '',
                    "traceback": traceback.format_exc()
                }), 500
        
        # Existing API endpoints
        @self.app.route('/api/tools/search_users', methods=['POST'])
        def search_users():
            """Search for users"""
            connector = None
            try:
                data = request.get_json()
                search_term = data.get('search_term')
                
                if not search_term:
                    return jsonify({"error": "Missing search_term parameter", "success": False}), 400
                
                logger.info(f"🔍 Searching users with term: {search_term}")
                
                connector = self._get_fresh_connection()
                with connector.get_conn() as conn:
                    users = repo_get_users(conn, search_term)
                    
                    logger.info(f"✅ Found {len(users)} users")
                    
                    return jsonify({
                        "success": True,
                        "search_term": search_term,
                        "total_found": len(users),
                        "users": users
                    })
                    
            except Exception as e:
                logger.error(f"❌ Error in search_users: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }), 500
            finally:
                if connector:
                    connector.close()
        
        @self.app.route('/api/tools/get_user_details', methods=['POST'])
        def get_user_details():
            """Get user details"""
            connector = None
            try:
                data = request.get_json()
                user_id = data.get('user_id')
                
                if not user_id:
                    return jsonify({"error": "Missing user_id parameter", "success": False}), 400
                
                logger.info(f"👤 Getting user details for ID: {user_id}")
                
                connector = self._get_fresh_connection()
                with connector.get_conn() as conn:
                    header_details = repo_get_user_header_details(conn, user_id)
                    additional_info = repo_get_additional_info(conn, user_id)
                    
                    return jsonify({
                        "success": True,
                        "user_id": user_id,
                        "header_details": header_details,
                        "additional_info": additional_info
                    })
                    
            except Exception as e:
                logger.error(f"❌ Error in get_user_details: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }), 500
            finally:
                if connector:
                    connector.close()
        
        @self.app.route('/api/tools/get_user_kyc_info', methods=['POST'])
        def get_user_kyc_info():
            """Get user KYC info"""
            connector = None
            try:
                data = request.get_json()
                user_id = data.get('user_id')
                
                if not user_id:
                    return jsonify({"error": "Missing user_id parameter", "success": False}), 400
                
                logger.info(f"📋 Getting KYC info for user ID: {user_id}")
                
                connector = self._get_fresh_connection()
                with connector.get_conn() as conn:
                    pan_info = repo_get_user_pans(conn, user_id)
                    aadhaar_kyc = repo_get_user_aadhaar_kyc(conn, user_id)
                    ckyc_info = repo_get_user_ckyc(conn, user_id)
                    
                    return jsonify({
                        "success": True,
                        "user_id": user_id,
                        "pan_info": pan_info,
                        "aadhaar_kyc": aadhaar_kyc,
                        "ckyc_info": ckyc_info,
                        "summary": {
                            "pan_records": len(pan_info),
                            "has_aadhaar_kyc": bool(aadhaar_kyc),
                            "has_ckyc": bool(ckyc_info)
                        }
                    })
                    
            except Exception as e:
                logger.error(f"❌ Error in get_user_kyc_info: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }), 500
            finally:
                if connector:
                    connector.close()
        
        @self.app.route('/api/tools/get_user_aml_status', methods=['POST'])
        def get_user_aml_status():
            """Get user AML status"""
            connector = None
            try:
                data = request.get_json()
                user_id = data.get('user_id')
                
                if not user_id:
                    return jsonify({"error": "Missing user_id parameter", "success": False}), 400
                
                logger.info(f"🚨 Getting AML status for user ID: {user_id}")
                
                connector = self._get_fresh_connection()
                with connector.get_conn() as conn:
                    aml_details = repo_get_aml_details(conn, user_id)
                    
                    return jsonify({
                        "success": True,
                        "user_id": user_id,
                        "aml_details": aml_details,
                        "has_aml_data": bool(aml_details)
                    })
                    
            except Exception as e:
                logger.error(f"❌ Error in get_user_aml_status: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }), 500
            finally:
                if connector:
                    connector.close()
        
        @self.app.route('/api/tools/get_user_address', methods=['POST'])
        def get_user_address():
            """Get user address"""
            connector = None
            try:
                data = request.get_json()
                user_id = data.get('user_id')
                
                if not user_id:
                    return jsonify({"error": "Missing user_id parameter", "success": False}), 400
                
                logger.info(f"🏠 Getting address for user ID: {user_id}")
                
                connector = self._get_fresh_connection()
                with connector.get_conn() as conn:
                    address_info = repo_get_user_address(conn, user_id)
                    
                    return jsonify({
                        "success": True,
                        "user_id": user_id,
                        "addresses": address_info,
                        "address_count": len([addr for addr in address_info.values() if addr])
                    })
                    
            except Exception as e:
                logger.error(f"❌ Error in get_user_address: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }), 500
            finally:
                if connector:
                    connector.close()
    
    def run(self, host='127.0.0.1', port=5000, debug=True):
        """Run the Flask application"""
        print("🚀 PayU Finance HTTP Server with AI Orchestrator")
        print("=" * 55)
        print(f"📊 Server URL: http://{host}:{port}")
        print()
        print("📋 Available interfaces:")
        print(f"   🔧 API Tester:        http://{host}:{port}/")
        print(f"   🤖 AI Orchestrator:   http://{host}:{port}/orchestrator")
        print(f"   ❤️  Health Check:     http://{host}:{port}/health")
        print()
        print("📡 API Endpoints:")
        print("   • GET  /health - Health check")
        print("   • GET  /api/tools - List available tools")
        print("   • POST /api/tools/* - Individual tool endpoints")
        print("   • POST /api/orchestrator/complex - AI Orchestrator")
        print()
        if self.orchestrator:
            print("✅ AI Orchestrator: ENABLED")
        else:
            print("❌ AI Orchestrator: DISABLED (check logs)")
        print()
        print("🛑 Press Ctrl+C to stop")
        print("-" * 55)
        
        self.app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    try:
        server = PayUFinanceHTTPServer()
        server.run()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        print(f"❌ Server startup failed: {e}")
