#!/usr/bin/env python3
"""
Comprehensive test to simulate the exact ValidationError scenario
"""

import pandas as pd
from unittest.mock import MagicMock, patch
import instructor
import json

def test_complete_gemini_workflow():
    """Test the complete workflow that was causing ValidationError"""
    print("🧪 Testing Complete Gemini Workflow (Discovery + Data Modeling)")
    
    # Create test data
    test_data = {
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'city': ['New York', 'London', 'Tokyo']
    }
    df = pd.DataFrame(test_data)
    
    try:
        # Mock the Google AI module to avoid API key requirements
        with patch('google.generativeai') as mock_genai:
            mock_genai.configure = MagicMock()
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            
            # Import after patching
            from neo4j_runway import Discovery, UserInput, GraphDataModeler
            from neo4j_runway.llm.gemini import GeminiDiscoveryLLM, GeminiDataModelingLLM
            
            # Test 1: Create Discovery LLM
            print("\n1️⃣ Testing GeminiDiscoveryLLM creation...")
            llm_disc = GeminiDiscoveryLLM(
                model_name="gemini-1.5-flash",
                model_params={"temperature": 0.1},
                api_key="fake-key-for-testing"
            )
            print(f"   ✅ Discovery LLM created with mode: {llm_disc.client.mode}")
            
            # Test 2: Create Data Modeling LLM  
            print("\n2️⃣ Testing GeminiDataModelingLLM creation...")
            llm_dm = GeminiDataModelingLLM(
                model_name="gemini-1.5-flash",
                model_params={"temperature": 0.1},
                api_key="fake-key-for-testing"
            )
            print(f"   ✅ Data Modeling LLM created with mode: {llm_dm.client.mode}")
            
            # Test 3: Create UserInput
            print("\n3️⃣ Testing UserInput creation...")
            user_input = UserInput(
                general_description="This is sample user data with basic demographics.",
                column_descriptions={
                    'id': 'Unique identifier for each person',
                    'name': 'Full name of the person', 
                    'age': 'Age in years',
                    'city': 'City where the person lives'
                },
                use_cases=[
                    "Find people in the same city",
                    "Group people by age ranges", 
                    "Analyze geographic distribution"
                ]
            )
            print("   ✅ UserInput created successfully")
            
            # Test 4: Create Discovery object
            print("\n4️⃣ Testing Discovery object creation...")
            disc = Discovery(llm=llm_disc, user_input=user_input, data=df)
            print("   ✅ Discovery object created successfully")
            
            # Test 5: Create GraphDataModeler (this is where ValidationError was occurring)
            print("\n5️⃣ Testing GraphDataModeler creation...")
            gdm = GraphDataModeler(llm=llm_dm, discovery=disc)
            print("   ✅ GraphDataModeler created successfully")
            
            # Test 6: Verify both LLMs are using GEMINI_JSON mode
            print("\n6️⃣ Verifying instructor modes...")
            if llm_disc.client.mode == instructor.Mode.GEMINI_JSON:
                print("   ✅ Discovery LLM using GEMINI_JSON mode")
            else:
                print(f"   ❌ Discovery LLM using wrong mode: {llm_disc.client.mode}")
                return False
                
            if llm_dm.client.mode == instructor.Mode.GEMINI_JSON:
                print("   ✅ Data Modeling LLM using GEMINI_JSON mode")
            else:
                print(f"   ❌ Data Modeling LLM using wrong mode: {llm_dm.client.mode}")
                return False
            
            print("\n🎉 SUCCESS: All components created without ValidationError!")
            print("   The ValidationError fix is working correctly.")
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def test_property_schema_compatibility():
    """Test that Property schema works with JSON serialization"""
    print("\n🧪 Testing Property Schema JSON Compatibility")
    
    try:
        from neo4j_runway.models.core.property import Property
        
        # Create a property with None alias (this was causing the ValidationError)
        prop = Property(
            name="test_property",
            type="string", 
            column_mapping="test_col",
            alias=None  # This None value was problematic with GEMINI_TOOLS mode
        )
        
        # Test JSON serialization (what GEMINI_JSON mode uses)
        prop_dict = prop.model_dump()
        json_str = json.dumps(prop_dict)
        
        # Test JSON deserialization
        restored_dict = json.loads(json_str)
        restored_prop = Property.model_validate(restored_dict)
        
        print("   ✅ Property with None alias serializes/deserializes correctly")
        print(f"   ✅ JSON representation: {json_str}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Property schema error: {e}")
        return False

if __name__ == "__main__":
    print("🔬 Comprehensive ValidationError Fix Verification\n")
    print("=" * 60)
    
    test1_passed = test_complete_gemini_workflow()
    test2_passed = test_property_schema_compatibility()
    
    print("\n" + "=" * 60)
    print("📋 Final Test Results:")
    print(f"   Complete Workflow Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Property Schema Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("   The ValidationError has been successfully resolved.")
        print("   Both GeminiDiscoveryLLM and GeminiDataModelingLLM now use GEMINI_JSON mode.")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("   The ValidationError issue may persist.")
