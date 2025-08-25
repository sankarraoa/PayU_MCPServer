import asyncio
import logging
from typing import Any, Dict

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
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("payu-fin-mcp")

class BasicPayUMCPServer:
    """Basic MCP Server for PayU Finance - Step 2"""
    
    def __init__(self):
        self.server = Server("payu-fin-mcp")
        self._setup_handlers()
        logger.info("PayU Finance MCP Server initialized")
    
    def _setup_handlers(self):
        """Setup MCP request handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available tools"""
            logger.info("Listing available tools")
            return ListToolsResult(
                tools=[
                    Tool(
                        name="hello_payu",
                        description="A simple hello world test for PayU Finance MCP server",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "message": {
                                    "type": "string",
                                    "description": "Message to echo back"
                                }
                            },
                            "required": ["message"]
                        }
                    ),
                    Tool(
                        name="server_status",
                        description="Get server status and configuration info",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool execution requests"""
            logger.info(f"Executing tool: {name} with arguments: {arguments}")
            
            try:
                if name == "hello_payu":
                    message = arguments.get("message", "Hello from PayU Finance!")
                    response = f"PayU MCP Server says: {message}"
                    
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=response
                        )]
                    )
                
                elif name == "server_status":
                    status = {
                        "server_name": "PayU Finance MCP Server",
                        "version": "1.0.0-step2",
                        "status": "running",
                        "step": "Basic MCP server without database integration"
                    }
                    
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"Server Status: {status}"
                        )]
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

async def main():
    """Main entry point for the MCP server"""
    server_instance = BasicPayUMCPServer()
    
    logger.info("Starting PayU Finance MCP Server...")
    
    try:
        # Run the server using stdio (standard input/output)
        async with stdio_server() as (read_stream, write_stream):
            await server_instance.server.run(
                read_stream, 
                write_stream, 
                InitializationOptions(
                    server_name="payu-fin-mcp",
                    server_version="1.0.0-step2",
                    capabilities=server_instance.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    print("🚀 Starting PayU Finance MCP Server (Step 2)...")
    print("📡 Server will communicate via stdin/stdout")
    print("🛑 Press Ctrl+C to stop")
    print("📋 This is a basic MCP server without database integration yet")
    print("-" * 60)
    
    asyncio.run(main())
