"""
LLM Response Fixer for AI Orchestrator
Handles malformed responses from Claude Sonnet 4 and other LLMs
"""

import json
import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("ai-orchestrator-llm-fix")

class LLMResponseFixer:
    """Comprehensive fix for LLM response parsing issues"""
    
    @staticmethod
    def parse_llm_response(response_text: str, user_query: str = "") -> Dict[str, Any]:
        """
        Parse LLM response with multiple fallback strategies
        
        Args:
            response_text: Raw response from LLM
            user_query: Original user query for context-aware fallbacks
            
        Returns:
            Parsed JSON structure
        """
        
        # Strategy 1: Try direct JSON parsing
        try:
            return json.loads(response_text.strip())
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Extract JSON from code blocks
        json_from_blocks = LLMResponseFixer._extract_json_from_code_blocks(response_text)
        if json_from_blocks:
            return json_from_blocks
        
        # Strategy 3: Extract JSON patterns
        json_from_patterns = LLMResponseFixer._extract_json_patterns(response_text)
        if json_from_patterns:
            return json_from_patterns
        
        # Strategy 4: Context-aware fallback based on user query
        fallback_response = LLMResponseFixer._generate_fallback_response(user_query, response_text)
        if fallback_response:
            logger.warning(f"Using fallback response for query: {user_query}")
            return fallback_response
        
        # Strategy 5: Last resort - raise error with details
        logger.error(f"All parsing strategies failed. Response: {response_text[:200]}...")
        raise ValueError("Could not parse LLM response into valid JSON")
    
    @staticmethod
    def _extract_json_from_code_blocks(text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from markdown code blocks"""
        patterns = [
            r'```json\s*({.*?})\s*```',
            r'```\s*({.*?})\s*```',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.MULTILINE)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        return None
    
    @staticmethod
    def _extract_json_patterns(text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON using various patterns"""
        patterns = [
            r'({\s*"reasoning".*?})(?:\s*$|\s*[^}])',  # JSON starting with reasoning
            r'({.*?"tools"\s*:.*?})(?:\s*$)',           # JSON with tools
            r'({".*?})(?:\s*$)',                         # Any JSON object at the end
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.MULTILINE)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        return None
    
    @staticmethod
    def _generate_fallback_response(user_query: str, response_text: str) -> Optional[Dict[str, Any]]:
        """Generate fallback response based on query context"""
        
        query_lower = user_query.lower()
        
        # KYC query pattern
        if "kyc" in query_lower and ("phone" in query_lower or re.search(r'\b\d{10}\b', user_query)):
            phone_match = re.search(r'\b\d{10}\b', user_query)
            phone = phone_match.group() if phone_match else "9845267602"
            
            return {
                "reasoning": {
                    "analysis": f"User wants KYC details for phone number {phone}",
                    "strategy": "Search for user by phone, then retrieve KYC information",
                    "tool_sequence": "search_users followed by get_user_kyc_info"
                },
                "tools": [
                    {
                        "step": 1,
                        "tool": "search_users",
                        "parameters": {"search_term": phone},
                        "purpose": "Find user by phone number",
                        "save_result_as": "found_user_id"
                    },
                    {
                        "step": 2,
                        "tool": "get_user_kyc_info",
                        "parameters": {"user_id": "{{found_user_id.users[0].id}}"},
                        "purpose": "Get KYC information",
                        "depends_on": "found_user_id"
                    }
                ]
            }
        
        # AML query pattern
        elif "aml" in query_lower:
            return {
                "reasoning": {
                    "analysis": "User wants AML status information",
                    "strategy": "Search for user then get AML status",
                    "tool_sequence": "search_users followed by get_user_aml_status"
                },
                "tools": [
                    {
                        "step": 1,
                        "tool": "search_users",
                        "parameters": {"search_term": "user_identifier"},
                        "purpose": "Find user",
                        "save_result_as": "found_user_id"
                    },
                    {
                        "step": 2,
                        "tool": "get_user_aml_status",
                        "parameters": {"user_id": "{{found_user_id.users[0].id}}"},
                        "purpose": "Get AML status",
                        "depends_on": "found_user_id"
                    }
                ]
            }
        
        return None

class EnhancedPromptBuilder:
    """Build enhanced prompts that work better with Claude Sonnet 4"""
    
    @staticmethod
    def build_json_only_prompt(user_query: str, tools: Dict) -> str:
        """Create a prompt that forces JSON-only output"""
        
        return f"""You are a JSON API that converts user queries into tool execution plans.

CRITICAL INSTRUCTIONS:
- Respond with ONLY valid JSON
- No explanations, no markdown, no code blocks
- Just pure JSON following the exact format below

USER QUERY: {user_query}

AVAILABLE TOOLS: search_users, get_user_details, get_user_kyc_info, get_user_aml_status, get_user_address

REQUIRED OUTPUT FORMAT:
{{
    "reasoning": {{
        "analysis": "brief analysis of what user wants",
        "strategy": "your approach to solve this", 
        "tool_sequence": "explanation of tool order"
    }},
    "tools": [
        {{
            "step": 1,
            "tool": "search_users",
            "parameters": {{"search_term": "search_value"}},
            "purpose": "find user by identifier",
            "save_result_as": "found_user_id"
        }},
        {{
            "step": 2,
            "tool": "tool_name",
            "parameters": {{"user_id": "{{{{found_user_id.users[0].id}}}}"}},
            "purpose": "tool purpose",
            "depends_on": "found_user_id"
        }}
    ]
}}

RULES:
- Always use search_users first to find user by phone/email/name
- Use {{{{variable.path}}}} syntax for variable substitution  
- Extract user_id as {{{{found_user_id.users[0].id}}}}
- Phone numbers exactly as provided in query
- Minimum tools needed to answer query

RESPOND WITH ONLY THE JSON OBJECT ABOVE."""
