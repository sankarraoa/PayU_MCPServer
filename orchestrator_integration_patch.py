"""
Integration Patch for AI Orchestrator
Drop-in replacement for your current LLM response parsing
"""

from llm_response_fixer import LLMResponseFixer, EnhancedPromptBuilder

class PatchedAIOrchestrator:
    """Patched version of your AI orchestrator with fixed LLM handling"""
    
    def __init__(self, mcp_client):
        self.mcp_client = mcp_client
        self.llm_fixer = LLMResponseFixer()
        self.prompt_builder = EnhancedPromptBuilder()
    
    async def process_complex_query(self, user_query: str) -> dict:
        """Process complex query with enhanced LLM handling"""
        
        try:
            # Build enhanced prompt
            enhanced_prompt = self.prompt_builder.build_json_only_prompt(
                user_query, 
                self._get_available_tools()
            )
            
            # Call LLM with enhanced prompt
            raw_response = await self._call_llm(enhanced_prompt)
            
            # Parse response with fallback strategies
            parsed_response = self.llm_fixer.parse_llm_response(raw_response, user_query)
            
            # Execute tools
            results = await self._execute_tool_sequence(parsed_response)
            
            return {
                "success": True,
                "results": results,
                "query": user_query
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": user_query
            }
    
    def _get_available_tools(self) -> dict:
        """Get available tools metadata"""
        return {
            "search_users": "Search for users by phone/email/name",
            "get_user_details": "Get user profile information", 
            "get_user_kyc_info": "Get KYC verification details",
            "get_user_aml_status": "Get AML screening status",
            "get_user_address": "Get user address information"
        }
    
    async def _call_llm(self, prompt: str) -> str:
        """Call LLM - replace with your actual implementation"""
        # Replace this with your actual LLM calling code
        pass
    
    async def _execute_tool_sequence(self, parsed_response: dict) -> dict:
        """Execute the tool sequence - replace with your actual implementation"""
        # Replace this with your actual tool execution code
        pass

# QUICK FIX: Drop this into your existing code
def quick_fix_your_orchestrator():
    """Quick fix instructions for your existing orchestrator"""
    
    instructions = """
    🔧 QUICK FIX FOR YOUR AI ORCHESTRATOR:
    
    1. ADD IMPORT:
       from llm_response_fixer import LLMResponseFixer
    
    2. REPLACE YOUR JSON PARSING:
       
       # OLD CODE:
       response_data = json.loads(llm_response)
       
       # NEW CODE:
       fixer = LLMResponseFixer()
       response_data = fixer.parse_llm_response(llm_response, user_query)
    
    3. UPDATE YOUR PROMPT:
       Use EnhancedPromptBuilder.build_json_only_prompt() instead of your current prompt
    
    4. VARIABLE SUBSTITUTION FIX:
       Make sure you're using: "{{found_user_id.users[0].id}}" 
       NOT: "{{found_user_id}}"
    
    This should fix both the JSON parsing AND the variable substitution issues!
    """
    
    print(instructions)

if __name__ == "__main__":
    quick_fix_your_orchestrator()
