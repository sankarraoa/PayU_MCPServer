# File: integrated_mcp_server_final.py

import asyncio
import logging
import os
from typing import Any, Dict
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ServerCapabilities,
    ToolsCapability,
)

# Import your existing database components
from db.base_connector import load_db_config
from db.postgres_connector import PostgresConnector
from repository.user_repository import (
    get_users, 
    get_additional_info, 
    get_user_pans, 
    get_user_aadhaar_kyc,
    get_user_ckyc,
    get_user_header_details,
    get_aml_details,
    get_user_address
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("payu-fin-mcp")

class PayUFinanceMCPServer:
    """PayU Finance MCP Server with Database Integration"""
    
    def __init__(self):
        self.server = Server("payu-fin-mcp")
        self.db_connector = None
        self._setup_handlers()
        logger.info("PayU Finance MCP Server initialized")
    
    async def initialize_db(self):
        """Initialize database connection"""
        try:
            # Set environment variables (as in your original main.py)
            os.environ['APP_ENV'] = os.getenv('APP_ENV', 'DEV')
            os.environ['DB_PASSWORD'] = os.getenv('DB_PASSWORD', '')
            os.environ['SSH_USER'] = os.getenv('SSH_USER', '')
            os.environ['SSH_PASSWORD'] = os.getenv('SSH_PASSWORD', '')
            os.environ['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
            
            # Load database configuration
            env, db_conns = load_db_config()
            pg_cfg = db_conns['pscore_postgres']
            
            # Create database connector
            self.db_connector = PostgresConnector(pg_cfg, environment=env)
            logger.info("Database connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _setup_handlers(self):
        """Setup MCP request handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available tools for PayU Finance operations"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="search_users",
                        description="Search for users by phone number, email, name, or ID",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "search_term": {
                                    "type": "string",
                                    "description": "Search term (phone, email, name, or user ID)"
                                }
                            },
                            "required": ["search_term"]
                        }
                    ),
                    Tool(
                        name="get_user_details",
                        description="Get comprehensive user details including header information",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {
                                    "type": "integer",
                                    "description": "User ID to fetch details for"
                                }
                            },
                            "required": ["user_id"]
                        }
                    ),
                    Tool(
                        name="get_user_kyc_info",
                        description="Get user KYC information including PAN, Aadhaar, and CKYC details",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {
                                    "type": "integer",
                                    "description": "User ID to fetch KYC information for"
                                }
                            },
                            "required": ["user_id"]
                        }
                    ),
                    Tool(
                        name="get_user_aml_status",
                        description="Get user AML (Anti-Money Laundering) screening details",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {
                                    "type": "integer",
                                    "description": "User ID to fetch AML status for"
                                }
                            },
                            "required": ["user_id"]
                        }
                    ),
                    Tool(
                        name="get_user_address",
                        description="Get user address information",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {
                                    "type": "integer", 
                                    "description": "User ID to fetch address for"
                                }
                            },
                            "required": ["user_id"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool execution requests"""
            
            # Initialize database if not already done
            if not self.db_connector:
                await self.initialize_db()
            
            try:
                with self.db_connector.get_conn() as conn:
                    
                    if name == "search_users":
                        search_term = arguments.get("search_term")
                        logger.info(f"Searching users with term: {search_term}")
                        
                        users = get_users(conn, search_term)
                        
                        # Format the response nicely
                        if users:
                            result_text = f"Found {len(users)} users matching '{search_term}':\n\n"
                            for i, user in enumerate(users, 1):
                                result_text += f"{i}. User ID: {user.get('id', 'N/A')}\n"
                                result_text += f"   Name: {user.get('name', 'N/A')}\n"
                                result_text += f"   Phone: {user.get('phone_id', 'N/A')}\n"
                                result_text += f"   Email: {user.get('email_id', 'N/A')}\n"
                                result_text += f"   Customer ID: {user.get('customer_id', 'N/A')}\n\n"
                        else:
                            result_text = f"No users found matching '{search_term}'"
                        
                        return CallToolResult(
                            content=[TextContent(type="text", text=result_text)]
                        )
                    
                    elif name == "get_user_details":
                        user_id = arguments.get("user_id")
                        logger.info(f"Getting user details for ID: {user_id}")
                        
                        header_details = get_user_header_details(conn, user_id)
                        additional_info = get_additional_info(conn, user_id)
                        
                        result_text = f"User Details for ID {user_id}:\n\n"
                        result_text += "Header Information:\n"
                        if header_details:
                            for key, value in header_details[0].items() if header_details else {}:
                                result_text += f"  {key}: {value}\n"
                        
                        result_text += "\nAdditional Information:\n"
                        if additional_info:
                            for key, value in additional_info[0].items() if additional_info else {}:
                                result_text += f"  {key}: {value}\n"
                        
                        return CallToolResult(
                            content=[TextContent(type="text", text=result_text)]
                        )
                    
                    elif name == "get_user_kyc_info":
                        user_id = arguments.get("user_id")
                        logger.info(f"Getting KYC info for user ID: {user_id}")
                        
                        pan_info = get_user_pans(conn, user_id)
                        aadhaar_kyc = get_user_aadhaar_kyc(conn, user_id)
                        ckyc_info = get_user_ckyc(conn, user_id)
                        
                        result_text = f"KYC Information for User {user_id}:\n\n"
                        result_text += f"PAN Information: {len(pan_info)} records found\n"
                        result_text += f"Aadhaar KYC: {len(aadhaar_kyc)} records found\n"
                        result_text += f"CKYC Information: {len(ckyc_info)} records found\n\n"
                        
                        # Add detailed info if available
                        if pan_info:
                            result_text += "PAN Details:\n"
                            for pan in pan_info:
                                result_text += f"  PAN: {pan.get('pan_number', 'N/A')}\n"
                                result_text += f"  Status: {pan.get('status', 'N/A')}\n"
                        
                        return CallToolResult(
                            content=[TextContent(type="text", text=result_text)]
                        )
                    
                    elif name == "get_user_aml_status":
                        user_id = arguments.get("user_id")
                        logger.info(f"Getting AML status for user ID: {user_id}")
                        
                        aml_details = get_aml_details(conn, user_id)
                        
                        result_text = f"AML Status for User {user_id}:\n\n"
                        if aml_details:
                            result_text += f"AML Records: {len(aml_details)} found\n"
                            for aml in aml_details:
                                result_text += f"  Alert Count: {aml.get('alert_count', 'N/A')}\n"
                                result_text += f"  Status: {aml.get('status', 'N/A')}\n"
                        else:
                            result_text += "No AML records found"
                        
                        return CallToolResult(
                            content=[TextContent(type="text", text=result_text)]
                        )
                    
                    elif name == "get_user_address":
                        user_id = arguments.get("user_id")
                        logger.info(f"Getting address for user ID: {user_id}")
                        
                        address_info = get_user_address(conn, user_id)
                        
                        result_text = f"Address Information for User {user_id}:\n\n"
                        if address_info:
                            for addr in address_info:
                                result_text += f"Address Type: {addr.get('address_type', 'N/A')}\n"
                                result_text += f"Address: {addr.get('address_line_1', 'N/A')}\n"
                                result_text += f"City: {addr.get('city', 'N/A')}\n"
                                result_text += f"State: {addr.get('state', 'N/A')}\n"
                                result_text += f"Pincode: {addr.get('pincode', 'N/A')}\n\n"
                        else:
                            result_text += "No address records found"
                        
                        return CallToolResult(
                            content=[TextContent(type="text", text=result_text)]
                        )
                    
                    else:
                        return CallToolResult(
                            content=[TextContent(
                                type="text",
                                text=f"Unknown tool: {name}"
                            )]
                        )
                        
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Error executing {name}: {str(e)}"
                    )]
                )
    
    async def cleanup(self):
        """Cleanup database connections"""
        if self.db_connector:
            self.db_connector.close()
            logger.info("Database connection closed")

async def main():
    """Main entry point for the MCP server"""
    server_instance = PayUFinanceMCPServer()
    
    try:
        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            # Create proper capabilities
            capabilities = ServerCapabilities(
                tools=ToolsCapability(listChanged=False)
            )
            
            await server_instance.server.run(
                read_stream, 
                write_stream, 
                InitializationOptions(
                    server_name="payu-fin-mcp",
                    server_version="1.0.0",
                    capabilities=capabilities
                ),
            )
    finally:
        await server_instance.cleanup()

if __name__ == "__main__":
    print("🚀 Starting PayU Finance MCP Server...")
    print("📊 Database-integrated MCP server ready")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 60)
    
    asyncio.run(main())
