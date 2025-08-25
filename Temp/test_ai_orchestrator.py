# File: test_ai_orchestrator_v2.py - Test enhanced multi-tool chaining
import sys
import json
from ai_orchestrator import EnhancedAIOrchestrator

def test_enhanced_orchestrator():
    """Test the Enhanced AI Orchestrator with complex multi-tool queries"""
    
    print("🚀 Testing Enhanced AI Orchestrator (Multi-Tool)")
    print("=" * 60)
    
    # Initialize with your API key
    API_KEY = "sk_eafa89be3fa975821790e02d3cd192386ab03a5ec9edf75b2021fd9cf3b462731667df5ab9a60140e86c21b9ec3fc5192f08b98808af74c2c96e9abb6e70"
    orchestrator = EnhancedAIOrchestrator(API_KEY)
    
    # Enhanced test cases - Complex queries requiring multiple tools
    complex_queries = [
        "Get KYC details for user with phone number 9845267602",
        "Find user with email asankarrao+1755756277203627@gmail.com and show their complete profile",
        "Show me everything about user with phone 9845267602 - details, KYC, AML status, and address",
        "Find Sankar Rao and check his AML status and address information",
        "Get complete compliance information (KYC and AML) for user with phone 9845267602",
        "Search for user by phone 9845267602 and verify their identity documents"
    ]
    
    print(f"🔧 Testing {len(complex_queries)} complex multi-tool queries...")
    print("⚠️  Make sure your HTTP server is running at http://127.0.0.1:5000")
    print()
    
    for i, query in enumerate(complex_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 50)
        
        try:
            # Process the complex query
            result = orchestrator.process_complex_query(query)
            
            # Display results
            if result.get('success'):
                print(f"✅ SUCCESS")
                
                # Show reasoning
                reasoning = result.get('reasoning', {})
                print(f"\n🧠 AI Reasoning:")
                print(f"   Analysis: {reasoning.get('analysis', 'N/A')}")
                print(f"   Strategy: {reasoning.get('strategy', 'N/A')}")
                print(f"   Tool Sequence: {reasoning.get('tool_sequence', 'N/A')}")
                
                # Show execution summary
                print(f"\n📊 Execution Summary:")
                print(f"   Steps Planned: {result.get('total_steps_planned', 0)}")
                print(f"   Steps Completed: {result.get('total_steps_completed', 0)}")
                
                # Show each step
                executed_steps = result.get('executed_steps', [])
                for step in executed_steps:
                    step_num = step.get('step', 0)
                    tool_name = step.get('tool', 'unknown')
                    purpose = step.get('purpose', 'No purpose specified')
                    success = step.get('success', False)
                    
                    status = "✅" if success else "❌"
                    print(f"\n   {status} Step {step_num}: {tool_name}")
                    print(f"      Purpose: {purpose}")
                    print(f"      Parameters: {json.dumps(step.get('parameters', {}), indent=6)}")
                    
                    if success:
                        step_result = step.get('result', {})
                        if 'users' in step_result:
                            print(f"      Result: Found {step_result.get('total_found', 0)} users")
                        elif 'user_id' in step_result:
                            print(f"      Result: Data for user {step_result.get('user_id')}")
                        elif step_result.get('success'):
                            print(f"      Result: SUCCESS")
                    else:
                        print(f"      Error: {step.get('error', 'Unknown error')}")
                    
            else:
                print(f"❌ FAILED")
                print(f"🚨 Error: {result.get('error')}")
                if 'raw_response' in result:
                    print(f"🔍 Raw LLM Response: {result.get('raw_response')}")
                    
        except Exception as e:
            print(f"💥 EXCEPTION: {str(e)}")
        
        # Wait for user input before next test
        if i < len(complex_queries):
            input("\n⏸️  Press Enter to continue to next test...")
    
    print("\n🎉 All enhanced tests completed!")
    return True

def test_single_complex_query():
    """Test a single user-provided complex query"""
    
    print("🧪 Enhanced Single Query Test Mode")
    print("=" * 40)
    
    API_KEY = "sk_eafa89be3fa975821790e02d3cd192386ab03a5ec9edf75b2021fd9cf3b462731667df5ab9a60140e86c21b9ec3fc5192f08b98808af74c2c96e9abb6e70"
    orchestrator = EnhancedAIOrchestrator(API_KEY)
    
    print("💡 Example complex queries:")
    print("   • Get KYC details for user with phone 9845267602")
    print("   • Show me everything about user with email john@example.com")
    print("   • Find Sankar Rao and check his compliance status")
    print("   • Get complete profile for user with phone 9845267602")
    
    while True:
        print("\n💬 Enter your complex query (or 'quit' to exit):")
        user_query = input("> ")
        
        if user_query.lower() in ['quit', 'exit', 'q']:
            break
            
        if not user_query.strip():
            continue
            
        print(f"\n🔍 Processing: {user_query}")
        print("-" * 50)
        
        try:
            result = orchestrator.process_complex_query(user_query)
            print(f"\n📋 Full Result:")
            print(json.dumps(result, indent=2, default=str))
            
        except Exception as e:
            print(f"💥 Error: {str(e)}")

def test_enhanced_prompt_generation():
    """Test the enhanced prompt generation"""
    
    print("🧪 Testing Enhanced Prompt Generation")
    print("=" * 40)
    
    API_KEY = "sk_eafa89be3fa975821790e02d3cd192386ab03a5ec9edf75b2021fd9cf3b462731667df5ab9a60140e86c21b9ec3fc5192f08b98808af74c2c96e9abb6e70"
    orchestrator = EnhancedAIOrchestrator(API_KEY)
    
    test_query = "Get KYC details for user with phone number 9845267602"
    prompt = orchestrator._build_enhanced_master_prompt(test_query)
    
    print("Generated Enhanced Prompt:")
    print("=" * 60)
    print(prompt)
    print("=" * 60)
    
    return prompt

if __name__ == "__main__":
    print("🚀 Enhanced AI Orchestrator Test Suite (Multi-Tool)")
    print("Choose test mode:")
    print("1. Full enhanced test suite (recommended)")
    print("2. Single complex query test")  
    print("3. Test enhanced prompt generation")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        test_enhanced_orchestrator()
    elif choice == "2":
        test_single_complex_query()
    elif choice == "3":
        test_enhanced_prompt_generation()
    else:
        print("Invalid choice. Running full enhanced test suite...")
        test_enhanced_orchestrator()
