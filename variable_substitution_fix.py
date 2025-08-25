"""
CRITICAL FIX: Variable Substitution in AI Orchestrator
=====================================================

The current issue is in the variable substitution logic where template variables
like {{user_id_from_user_search_result}} are not being replaced with actual values.

The problem is in the execute_tool_sequence method where variables need to be
properly substituted before making API calls.
"""

import re
import json
import logging

def substitute_variables(parameters, saved_results):
    """
    Substitute template variables in parameters with actual values from saved results.
    
    Args:
        parameters (dict): Parameters that may contain template variables
        saved_results (dict): Dictionary of saved results from previous steps
    
    Returns:
        dict: Parameters with variables substituted
    """
    if not isinstance(parameters, dict):
        return parameters
    
    # Convert parameters to JSON string for easier substitution
    param_str = json.dumps(parameters)
    
    # Find all template variables like {{variable_name}}
    template_pattern = r'\{\{([^}]+)\}\}'
    matches = re.findall(template_pattern, param_str)
    
    for match in matches:
        variable_name = match.strip()
        template = f"{{{{{variable_name}}}}}"
        
        # Look for the variable in saved results
        replacement_value = None
        
        # First, try direct variable name match
        if variable_name in saved_results:
            replacement_value = saved_results[variable_name]
        
        # Then try pattern matching for complex variable names
        else:
            for saved_key, saved_value in saved_results.items():
                if variable_name.endswith(f"_from_{saved_key}"):
                    # Extract the field name (e.g., "user_id" from "user_id_from_user_search_result")
                    field_name = variable_name.replace(f"_from_{saved_key}", "")
                    
                    # Look for the field in the saved result
                    if isinstance(saved_value, dict) and field_name in saved_value:
                        replacement_value = saved_value[field_name]
                    elif isinstance(saved_value, list) and len(saved_value) > 0:
                        if isinstance(saved_value[0], dict) and field_name in saved_value[0]:
                            replacement_value = saved_value[0][field_name]
                    break
        
        if replacement_value is not None:
            # Convert to string for substitution
            if isinstance(replacement_value, (int, float)):
                replacement_str = str(replacement_value)
            elif isinstance(replacement_value, str):
                replacement_str = replacement_value
            else:
                replacement_str = json.dumps(replacement_value)
            
            # Replace the template with actual value
            param_str = param_str.replace(f'"{template}"', replacement_str)
            param_str = param_str.replace(template, replacement_str)
            
            logging.info(f"✅ Substituted {template} with {replacement_str}")
        else:
            logging.warning(f"⚠️ Variable {variable_name} not found in saved results")
    
    try:
        return json.loads(param_str)
    except json.JSONDecodeError:
        logging.error(f"❌ Failed to parse substituted parameters: {param_str}")
        return parameters

# Example of how to integrate this into the AI orchestrator
def execute_tool_sequence_fixed(self, tools, reasoning):
    """
    Fixed version of execute_tool_sequence with proper variable substitution
    """
    results = []
    saved_results = {}
    
    for tool_config in tools:
        step = tool_config.get('step', len(results) + 1)
        tool_name = tool_config['tool']
        parameters = tool_config.get('parameters', {})
        purpose = tool_config.get('purpose', '')
        save_as = tool_config.get('save_result_as')
        
        logging.info(f"Executing Step {step}: {tool_name} - {purpose}")
        
        # ⭐ CRITICAL FIX: Substitute variables before making API call
        substituted_params = substitute_variables(parameters, saved_results)
        
        logging.info(f"Original parameters: {parameters}")
        logging.info(f"Substituted parameters: {substituted_params}")
        
        # Make the API call with substituted parameters
        try:
            response = self.http_client.post(
                f"{self.base_url}/api/tools/{tool_name}",
                json=substituted_params,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Save result if save_as is specified
                if save_as:
                    saved_results[save_as] = result
                    logging.info(f"💾 Saved result as '{save_as}': {result}")
                
                # Also save individual fields for easier access
                if isinstance(result, dict):
                    for key, value in result.items():
                        saved_results[f"{key}"] = value
                        logging.info(f"💾 Saved {key}: {value}")
                elif isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
                    # For list results, save the first item's fields
                    for key, value in result[0].items():
                        saved_results[f"{key}"] = value
                        logging.info(f"💾 Saved {key}: {value}")
                
                results.append({
                    'step': step,
                    'tool': tool_name,
                    'parameters': substituted_params,
                    'purpose': purpose,
                    'success': True,
                    'result': result
                })
                
            else:
                error_text = response.text
                logging.error(f"❌ Step {step} failed: HTTP {response.status_code}: {error_text}")
                
                results.append({
                    'step': step,
                    'tool': tool_name,
                    'parameters': substituted_params,
                    'purpose': purpose,
                    'success': False,
                    'error': f"HTTP {response.status_code}: {error_text}"
                })
                break  # Stop execution on failure
                
        except Exception as e:
            logging.error(f"❌ Step {step} failed with exception: {str(e)}")
            results.append({
                'step': step,
                'tool': tool_name,
                'parameters': substituted_params,
                'purpose': purpose,
                'success': False,
                'error': str(e)
            })
            break  # Stop execution on failure
    
    return results, saved_results

print("🔧 Variable substitution fix created!")
