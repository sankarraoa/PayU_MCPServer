# File: test_step3.py

#!/usr/bin/env python3
"""
Test script for PayU Finance MCP Server - Step 3
Tests the database integration
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

async def test_database_integration():
    """Test the database-integrated MCP server"""
    print("🧪 Testing Database-Integrated MCP Server...")
    print("-" * 50)
    
    try:
        # Import the integrated server
        from integrated_mcp_server import PayUFinanceMCPServer
        
        print("✅ Successfully imported PayUFinanceMCPServer")
        
        # Create server instance
        server = PayUFinanceMCPServer()
        print("✅ Server instance created")
        
        # Test database initialization
        print("🔌 Testing database initialization...")
        await server.initialize_db()
        print("✅ Database connection successful")
        
        # Test with actual database query (using your search term)
        print("👥 Testing user search...")
        
        # We'll test if we can access the database functions
        from repository.user_repository import get_users
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Test with a connection
        with server.db_connector.get_conn() as conn:
            users = get_users(conn, "9845267602")  # Your test phone number
            print(f"✅ Database query successful - Found {len(users)} users")
        
        # Clean up
        await server.cleanup()
        print("✅ Database connection closed")
        
        print("\n🎉 Database integration test passed!")
        print("✅ MCP server can connect to database")
        print("✅ Repository functions work with MCP server")
        print("✅ Connection management working")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🚀 PayU Finance MCP Server - Step 3 Test")
    print("Testing database integration...")
    print("=" * 60)
    
    # Run the async test
    result = asyncio.run(test_database_integration())
    
    if result:
        print("\n📋 STEP 3 COMPLETE!")
        print("✅ Database integration working")
        print("✅ MCP server can access PayU Finance data")
        print("🎯 Ready for Step 4: Full functionality testing")
    else:
        print("\n❌ STEP 3 FAILED!")
        print("🔧 Fix the issues above before proceeding")

if __name__ == "__main__":
    main()
