# File: test_http_client.py
import requests
import json

class PayUFinanceHTTPClient:
    """Client for testing PayU Finance HTTP API"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def health_check(self):
        """Check if server is healthy"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def list_tools(self):
        """Get list of available tools"""
        response = requests.get(f"{self.base_url}/api/tools")
        return response.json()
    
    def search_users(self, search_term):
        """Search for users"""
        response = requests.post(
            f"{self.base_url}/api/tools/search_users",
            json={"search_term": search_term}
        )
        return response.json()
    
    def get_user_details(self, user_id):
        """Get user details"""
        response = requests.post(
            f"{self.base_url}/api/tools/get_user_details",
            json={"user_id": user_id}
        )
        return response.json()
    
    def get_user_kyc_info(self, user_id):
        """Get user KYC information"""
        response = requests.post(
            f"{self.base_url}/api/tools/get_user_kyc_info",
            json={"user_id": user_id}
        )
        return response.json()
    
    def get_user_aml_status(self, user_id):
        """Get user AML status"""
        response = requests.post(
            f"{self.base_url}/api/tools/get_user_aml_status",
            json={"user_id": user_id}
        )
        return response.json()
    
    def get_user_address(self, user_id):
        """Get user address"""
        response = requests.post(
            f"{self.base_url}/api/tools/get_user_address",
            json={"user_id": user_id}
        )
        return response.json()

def main():
    """Test the HTTP API"""
    client = PayUFinanceHTTPClient()
    
    print("🔍 Testing PayU Finance HTTP API\n")
    
    # Test health check
    print("1. Health Check:")
    try:
        health = client.health_check()
        print(f"   ✅ Status: {health.get('status')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test list tools
    print("\n2. List Tools:")
    try:
        tools = client.list_tools()
        print(f"   ✅ Available tools: {len(tools.get('tools', []))}")
        for tool in tools.get('tools', []):
            print(f"      • {tool['name']}: {tool['description']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test search users (replace with actual search term)
    print("\n3. Search Users:")
    try:
        search_result = client.search_users("9845267602")  # Use your test phone
        print(f"   ✅ Found {search_result.get('total_found', 0)} users")
        
        # If users found, test other endpoints with first user
        users = search_result.get('users', [])
        if users:
            user_id = users[0].get('id')
            print(f"   📋 Testing with User ID: {user_id}")
            
            # Test user details
            print("\n4. User Details:")
            details = client.get_user_details(user_id)
            print(f"   ✅ Got user details: {details.get('success')}")
            
            # Test KYC info
            print("\n5. KYC Info:")
            kyc = client.get_user_kyc_info(user_id)
            print(f"   ✅ Got KYC info: {kyc.get('success')}")
            
            # Test AML status
            print("\n6. AML Status:")
            aml = client.get_user_aml_status(user_id)
            print(f"   ✅ Got AML status: {aml.get('success')}")
            
            # Test address
            print("\n7. User Address:")
            address = client.get_user_address(user_id)
            print(f"   ✅ Got address info: {address.get('success')}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    main()
