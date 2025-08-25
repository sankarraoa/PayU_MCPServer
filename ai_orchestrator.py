# File: ai_orchestrator.py - Enhanced AI Orchestrator with multi-tool chaining
import json
import requests
import logging
from typing import Dict, Any, List, Optional
from llm_response_fixer import LLMResponseFixer


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-orchestrator-v2")

class ConversationAPI:
    """Integrate your existing ConversationAPI"""
    def __init__(self, api_key):
        self.headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "X-Api-Key": api_key
        }
    
    def create_conversation(self, user_message):
        url = "https://api.coco.prod.toqan.ai/api/create_conversation"
        payload = {"user_message": user_message}
        logger.info(f"Creating conversation with message: {self.headers}")
        response = requests.post(url, json=payload, headers=self.headers)
        logger.info(f"Received response: {response.text}")
        conversation_id = json.loads(response.text)["conversation_id"]
        logger.info(f"Conversation ID: {conversation_id}")
        response = self.find_new_conversation_response(conversation_id)
        logger.info(f"New conversation response: {response}")
        return conversation_id, response
    
    def find_new_conversation_response(self, conversation_id):
        url = "https://api.coco.prod.toqan.ai/api/find_conversation"
        payload = {"conversation_id": conversation_id}
        import time
        while True:
            response = requests.post(url, json=payload, headers=self.headers)
            conversations = response.json()
            if len(conversations) > 1:
                return conversations
            time.sleep(2)

class EnhancedAIOrchestrator:
    """Enhanced AI Orchestrator with multi-tool chaining and reasoning"""
    
    def __init__(self, api_key: str, base_url: str = "http://127.0.0.1:5000"):
        self.conversation_api = ConversationAPI(api_key)
        self.base_url = base_url
        self.tools_catalog = self._build_enhanced_tools_catalog()
        logger.info("Enhanced AI Orchestrator initialized with multi-tool support")
    
    def _build_enhanced_tools_catalog(self) -> Dict[str, Any]:
        """Build enhanced tools catalog with detailed descriptions"""
        return {
            "search_users": {
                "display_name": "User Search",
                "function_name": "search_users",
                "description": "Searches for users in the PayU Finance database using various search criteria. The tool can find users by phone number, email address, full name, or user ID. Returns a list of matching users with basic information including user ID, name, phone, email, and customer ID. This is typically the first tool to use when you need to identify a specific user before retrieving detailed information.",
                "parameters": {
                    "search_term": {
                        "type": "string",
                        "description": "Search term to find users (phone number, email, name, or user ID)",
                        "required": True,
                        "examples": ["9845267602", "+919845267602", "john@example.com", "John Doe", "12345"]
                    }
                },
                "instructions": "Use this tool when you need to find a user before accessing their detailed information. Always search by the most specific identifier available (phone number or email preferred). The tool returns user IDs which are required for all other user-specific tools. If multiple users are found, choose the most relevant one based on context. Phone numbers should be provided as entered by the user (with or without country code).",
                "endpoint": "/api/tools/search_users",
                "returns": "List of users with id, name, phone, email, PAN, customer_id"
            },
            "get_user_details": {
                "display_name": "User Details",
                "function_name": "get_user_details",
                "description": "Retrieves comprehensive user information including header details and additional profile information. Returns personal details such as name, date of birth, gender, contact information, and extended profile data. This tool provides the most complete view of a user's profile in the PayU Finance system.",
                "parameters": {
                    "user_id": {
                        "type": "integer",
                        "description": "Unique identifier of the user to fetch details for",
                        "required": True,
                        "examples": [32049152, 12345]
                    }
                },
                "instructions": "Use this tool after finding a user with search_users to get their complete profile. The user_id must be obtained from a previous search_users call. This tool is ideal when you need general user information or want to verify user identity. Use this before more specific tools like KYC or AML if you need to confirm you have the right user.",
                "endpoint": "/api/tools/get_user_details",
                "returns": "User header details and additional information"
            },
            "get_user_kyc_info": {
                "display_name": "User KYC Information",
                "function_name": "get_user_kyc_info",
                "description": "Retrieves Know Your Customer (KYC) verification details including PAN card information, Aadhaar KYC records, and Central KYC (CKYC) data. Returns verification status, document details, gender information from KYC documents, and compliance records. Essential for regulatory compliance and identity verification processes.",
                "parameters": {
                    "user_id": {
                        "type": "integer",
                        "description": "Unique identifier of the user to fetch KYC information for",
                        "required": True,
                        "examples": [32049152, 12345]
                    }
                },
                "instructions": "Use this tool when you need to verify a user's identity documents or check their KYC compliance status. The user_id must be obtained from search_users first. This tool is crucial for compliance-related queries, document verification, or when processing financial services that require KYC validation. Note that sensitive information like Aadhaar numbers may be masked for privacy.",
                "endpoint": "/api/tools/get_user_kyc_info",
                "returns": "PAN info, Aadhaar KYC, CKYC information and summary"
            },
            "get_user_aml_status": {
                "display_name": "User AML Status",
                "function_name": "get_user_aml_status",
                "description": "Retrieves Anti-Money Laundering (AML) screening details and compliance status. Returns AML alert counts, screening results, risk assessment status, and regulatory compliance information. Critical for risk assessment and regulatory reporting requirements.",
                "parameters": {
                    "user_id": {
                        "type": "integer",
                        "description": "Unique identifier of the user to fetch AML status for",
                        "required": True,
                        "examples": [32049152, 12345]
                    }
                },
                "instructions": "Use this tool for risk assessment, compliance checks, or when regulatory reporting requires AML status verification. The user_id must be obtained from search_users first. This tool is essential for high-risk transaction processing, account monitoring, or when compliance teams need to review a user's AML standing. Always use this tool for users involved in large transactions or when risk flags are raised.",
                "endpoint": "/api/tools/get_user_aml_status",
                "returns": "AML screening details and alert information"
            },
            "get_user_address": {
                "display_name": "User Address Information",
                "function_name": "get_user_address",
                "description": "Retrieves user address information including current address, communication address, and address verification details. Returns address type, complete address lines, city, state, and pincode information. Useful for address verification, delivery coordination, and location-based services.",
                "parameters": {
                    "user_id": {
                        "type": "integer",
                        "description": "Unique identifier of the user to fetch address information for",
                        "required": True,
                        "examples": [32049152, 12345]
                    }
                },
                "instructions": "Use this tool when you need to verify a user's address, coordinate deliveries, or perform location-based verification. The user_id must be obtained from search_users first. This tool is particularly useful for address verification during onboarding, updating delivery information, or when geographic risk assessment is required. Multiple address types may be returned (current, communication, etc.).",
                "endpoint": "/api/tools/get_user_address",
                "returns": "User address details with address count"
            }
        }
    
    def _build_enhanced_master_prompt(self, user_query: str) -> str:
        """Build enhanced master prompt with detailed tools and reasoning request"""
        
        # Build detailed tools description
        tools_description = "AVAILABLE TOOLS:\n\n"
        for tool_name, tool_info in self.tools_catalog.items():
            tools_description += f"**{tool_info['display_name']}** (`{tool_info['function_name']}`)\n"
            tools_description += f"Description: {tool_info['description']}\n"
            tools_description += f"Parameters: {json.dumps(tool_info['parameters'], indent=2)}\n"
            tools_description += f"Instructions: {tool_info['instructions']}\n"
            tools_description += f"Returns: {tool_info['returns']}\n\n"
        
        master_prompt = f"""You are an AI assistant for PayU Finance with advanced reasoning capabilities. You help users query financial data using available tools. You can chain multiple tools together to answer complex queries.

{tools_description}

USER QUERY: {user_query}

INSTRUCTIONS:
1. **REASON THROUGH THE QUERY**: Think step-by-step about what the user wants
2. **IDENTIFY REQUIRED TOOLS**: Determine which tools are needed and in what order
3. **PLAN TOOL CHAINING**: If you need data from one tool to use in another, plan the sequence
4. **RESPOND WITH JSON**: Provide your reasoning and tool execution plan

RESPONSE FORMAT - Return ONLY a JSON object in this exact format:

{{
    "reasoning": {{
        "analysis": "Your step-by-step analysis of what the user wants",
        "strategy": "Your strategy for answering the query",
        "tool_sequence": "Explanation of why you chose these tools in this order"
    }},
    "tools": [
        {{
            "step": 1,
            "tool": "tool_name",
            "parameters": {{
                "param1": "value1"
            }},
            "purpose": "Why this tool is needed",
            "save_result_as": "variable_name"
        }},
        {{
            "step": 2,
            "tool": "tool_name",
            "parameters": {{
                "user_id": "{{{{user_id_from_step_1}}}}"
            }},
            "purpose": "Why this tool is needed",
            "depends_on": "variable_name"
        }}
    ]
}}

TOOL CHAINING RULES:
- Always use search_users FIRST if you need to find a user by phone, email, or name
- Use the user_id from search_users results for all subsequent tools
- Use {{{{variable_name}}}} syntax to reference results from previous tools
- For phone numbers, use them exactly as provided (with or without +91)
- Plan the minimum number of tools needed to answer the query completely

EXAMPLE COMPLEX QUERIES:

Query: "Get KYC details for user with phone 9845267602"
Strategy: First find the user, then get their KYC info

Query: "Show me everything about user with email john@example.com" 
Strategy: First find user, then get details, KYC, AML status, and address

Query: "Find Sankar Rao and check his AML status"
Strategy: First search for user by name, then get AML status

Now analyze the user query and respond with your reasoning and tool execution plan:"""

        return master_prompt
    
    def _execute_tool_sequence(self, tool_sequence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a sequence of tools, passing data between them"""
        results = {}
        tool_results = []
        
        for tool_step in tool_sequence:
            try:
                step_num = tool_step.get('step', 0)
                tool_name = tool_step['tool']
                parameters = tool_step['parameters'].copy()  # Copy to avoid modifying original
                purpose = tool_step.get('purpose', '')
                save_as = tool_step.get('save_result_as', f'step_{step_num}_result')
                
                logger.info(f"Executing Step {step_num}: {tool_name} - {purpose}")
                
                # Replace parameter references with actual values from previous results
                # Enhanced variable resolution with dot notation support
                for param_key, param_value in parameters.items():
                    if isinstance(param_value, str) and '{{' in param_value and '}}' in param_value:
                        import re
                        var_match = re.search(r'\{\{(.+?)\}\}', param_value)
                        if var_match:
                            var_ref = var_match.group(1)
                            
                            # Handle dot notation like "user_search_result.user_id"
                            if '.' in var_ref:
                                parts = var_ref.split('.', 1)
                                var_name = parts[0]
                                path = parts[1]
                                
                                if var_name in results:
                                    try:
                                        current = results[var_name]
                                        
                                        # 🎯 SMART MAPPING for different Claude expectations
                                        if path == "user_id" and 'users' in current and len(current['users']) > 0:
                                            # Claude expects user_id but we have users[0].id
                                            resolved_value = current['users'][0]['id']
                                            logger.info(f"🎯 SMART MAPPING: {var_ref} → users[0].id = {resolved_value}")
                                        elif path == "users[0].id" and 'users' in current and len(current['users']) > 0:
                                            # Direct access to users[0].id
                                            resolved_value = current['users'][0]['id']
                                            logger.info(f"🎯 DIRECT ACCESS: {var_ref} → {resolved_value}")
                                        else:
                                            # Try generic path navigation
                                            resolved_value = current
                                            for part in path.split('.'):
                                                if '[' in part and ']' in part:
                                                    # Handle array access like users[0]
                                                    key = part.split('[')[0]
                                                    index = int(part.split('[')[1].split(']')[0])
                                                    resolved_value = resolved_value[key][index]
                                                else:
                                                    resolved_value = resolved_value[part]
                                            logger.info(f"🎯 GENERIC PATH: {var_ref} → {resolved_value}")
                                            
                                        parameters[param_key] = resolved_value
                                        logger.info(f"✅ Resolved {param_key}: {param_value} → {resolved_value}")
                                        
                                    except (KeyError, IndexError, TypeError) as e:
                                        logger.error(f"❌ Error resolving path {var_ref}: {e}")
                                        return {
                                            "success": False,
                                            "error": f"Cannot resolve variable path {var_ref} for step {step_num}",
                                            "completed_steps": tool_results
                                        }
                            else:
                                # Handle "_from_" pattern like "user_id_from_user_search_result"
                                resolved_value = None
                                
                                # Method 1: Direct variable lookup
                                if var_ref in results:
                                    resolved_value = results[var_ref]
                                    logger.info(f"🎯 Direct match: {var_ref} = {resolved_value}")
                                
                                # Method 2: Pattern matching for "_from_" variables
                                else:
                                    for saved_key, saved_value in results.items():
                                        if var_ref.endswith(f"_from_{saved_key}"):
                                            # Extract field name (e.g., "user_id" from "user_id_from_user_search_result")
                                            field_name = var_ref.replace(f"_from_{saved_key}", "")
                                            logger.info(f"🔍 Looking for field '{field_name}' in saved result '{saved_key}'")
                                            
                                            # Look for the field in the saved result
                                            if isinstance(saved_value, dict):
                                                if field_name in saved_value:
                                                    resolved_value = saved_value[field_name]
                                                    logger.info(f"✅ Found in dict: {field_name} = {resolved_value}")
                                                elif 'users' in saved_value and len(saved_value['users']) > 0:
                                                    # Handle search_users result format
                                                    if field_name == 'user_id' and 'id' in saved_value['users'][0]:
                                                        resolved_value = saved_value['users'][0]['id']
                                                        logger.info(f"✅ Found user_id in users[0]: {resolved_value}")
                                            elif isinstance(saved_value, list) and len(saved_value) > 0:
                                                if isinstance(saved_value[0], dict) and field_name in saved_value[0]:
                                                    resolved_value = saved_value[0][field_name]
                                                    logger.info(f"✅ Found in list[0]: {field_name} = {resolved_value}")
                                            
                                            if resolved_value is not None:
                                                break
                                                # Apply the replacement
                                if resolved_value is not None:
                                    parameters[param_key] = resolved_value
                                    logger.info(f"✅ Resolved {param_key}: {param_value} → {resolved_value}")
                                else:
                                    logger.error(f"❌ Variable {var_ref} not found in results: {list(results.keys())}")
                                    return {
                                        "success": False,
                                        "error": f"Cannot resolve variable {var_ref} for step {step_num}",
                                        "completed_steps": tool_results
                                    }


                # Execute the tool
                tool_result = self._execute_single_tool(tool_name, parameters)
                
                if tool_result.get('success'):
                    # Save key results for next tools
                    api_result = tool_result.get('result', {})
                    
                    # Save user_id if this was a search
                    if tool_name == 'search_users' and api_result.get('users'):
                        users = api_result['users']
                        if users:
                            user_id = users[0].get('id')
                            results['user_id_from_search'] = user_id
                            results[f'user_id_from_step_{step_num}'] = user_id
                            logger.info(f"Saved user_id: {user_id}")
                    
                    # Save the full result
                    results[save_as] = api_result
                    
                    # Add to results list
                    tool_results.append({
                        "step": step_num,
                        "tool": tool_name,
                        "purpose": purpose,
                        "parameters": parameters,
                        "result": api_result,
                        "success": True
                    })
                    
                else:
                    # Tool failed
                    logger.error(f"Step {step_num} failed: {tool_result.get('error')}")
                    tool_results.append({
                        "step": step_num,
                        "tool": tool_name,
                        "purpose": purpose,
                        "parameters": parameters,
                        "error": tool_result.get('error'),
                        "success": False
                    })
                    
                    # Stop execution on failure
                    return {
                        "success": False,
                        "error": f"Step {step_num} ({tool_name}) failed: {tool_result.get('error')}",
                        "completed_steps": tool_results
                    }
                    
            except Exception as e:
                logger.error(f"Error executing step {step_num}: {e}")
                return {
                    "success": False,
                    "error": f"Step execution failed: {str(e)}",
                    "completed_steps": tool_results
                }
        
        return {
            "success": True,
            "completed_steps": tool_results,
            "total_steps": len(tool_sequence)
        }
    
    def _execute_single_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single tool via HTTP API call"""
        try:
            if tool_name not in self.tools_catalog:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}",
                    "available_tools": list(self.tools_catalog.keys())
                }
            
            # Get endpoint for the tool
            endpoint = self.tools_catalog[tool_name]['endpoint']
            url = f"{self.base_url}{endpoint}"
            
            logger.info(f"HTTP POST to {url} with parameters: {parameters}")
            
            # Make HTTP POST request
            response = requests.post(url, json=parameters, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "tool": tool_name,
                    "parameters": parameters,
                    "result": result
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "tool": tool_name,
                    "parameters": parameters
                }
                
        except requests.RequestException as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}",
                "tool": tool_name,
                "parameters": parameters
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution failed: {str(e)}",
                "tool": tool_name,
                "parameters": parameters
            }
    
    def process_complex_query(self, user_query: str) -> Dict[str, Any]:
        """Enhanced method to process complex queries with multi-tool chaining"""
        try:
            logger.info(f"Processing complex query: {user_query}")
            
            # Step 1: Build enhanced master prompt
            master_prompt = self._build_enhanced_master_prompt(user_query)
            logger.info(f"Enhanced master prompt built")

            # Step 2: Send to LLM
            logger.info("Sending to Claude Sonnet 4...")
            conversation_id, llm_response = self.conversation_api.create_conversation(master_prompt)
            logger.info(f"LLM response received for conversation: {conversation_id}")
            
            # Step 3: Parse enhanced LLM response
            parsed_response = self._parse_enhanced_llm_response(llm_response)
            if not parsed_response:
                return {
                    "success": False,
                    "error": "Failed to parse LLM response into valid tool sequence",
                    "raw_response": str(llm_response)
                }
            
            logger.info(f"Parsed reasoning: {parsed_response.get('reasoning')}")
            logger.info(f"Tool sequence: {len(parsed_response.get('tools', []))} tools")
            
            # Step 4: Execute tool sequence
            execution_result = self._execute_tool_sequence(parsed_response['tools'])
            
            # Step 5: Build final response
            final_result = {
                "success": execution_result.get('success'),
                "user_query": user_query,
                "conversation_id": conversation_id,
                "reasoning": parsed_response.get('reasoning'),
                "planned_tools": parsed_response.get('tools'),
                "executed_steps": execution_result.get('completed_steps', []),
                "total_steps_completed": len(execution_result.get('completed_steps', [])),
                "total_steps_planned": len(parsed_response.get('tools', []))
            }
            
            if not execution_result.get('success'):
                final_result["error"] = execution_result.get('error')
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error processing complex query: {e}")
            return {
                "success": False,
                "error": f"Processing failed: {str(e)}",
                "user_query": user_query
            }

    def _parse_enhanced_llm_response(self, llm_response: Any) -> Optional[Dict[str, Any]]:
        """Parse enhanced LLM response with reasoning and multiple tools - FIXED VERSION"""
        try:
            # Extract the AI message from response
            if isinstance(llm_response, list) and len(llm_response) > 1:
                ai_message = llm_response[1].get('message', '')
            else:
                ai_message = str(llm_response)
            
            logger.info(f"Raw LLM response: {ai_message}")
            
            # Try to find JSON in the response first
            import re
            json_match = re.search(r'\{.*\}', ai_message, re.DOTALL)
            
            if json_match:
                # Found JSON, try direct parsing first
                json_str = json_match.group(0)
                try:
                    parsed_response = json.loads(json_str)
                    # Validate required fields
                    if 'reasoning' in parsed_response and 'tools' in parsed_response:
                        return parsed_response
                except json.JSONDecodeError:
                    # JSON parsing failed, fall through to LLMResponseFixer
                    pass
            
            # 🎯 KEY FIX: Use LLMResponseFixer when no JSON found OR when JSON parsing fails
            logger.info("Using LLMResponseFixer for non-JSON or malformed response")
            fixer = LLMResponseFixer()
            parsed_response = fixer.parse_llm_response(ai_message, "")
            
            if parsed_response and 'reasoning' in parsed_response and 'tools' in parsed_response:
                return parsed_response
            else:
                logger.error("LLMResponseFixer could not generate valid response")
                return None
                    
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return None

# Helper function for easy testing
def create_enhanced_orchestrator(api_key: str) -> EnhancedAIOrchestrator:
    """Create and return an Enhanced AIOrchestrator instance"""
    return EnhancedAIOrchestrator(api_key)
