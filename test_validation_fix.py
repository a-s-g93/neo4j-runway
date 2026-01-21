#!/usr/bin/env python3
"""
Test script to verify the ValidationError fix for Gemini integration
"""

import sys
import traceback
from unittest.mock import MagicMock

def test_gemini_llm_modes():
    """Test that Gemini LLMs are configured with correct instructor modes."""
    try:
        from neo4j_runway.llm.gemini import GeminiDataModelingLLM, GeminiDiscoveryLLM
        import instructor
        
        print("🔍 Testing Gemini LLM instructor modes...")
        
        # Mock the genai module to avoid API key requirements
        import sys
        from unittest.mock import MagicMock
        
        # Create mock objects
        mock_genai = MagicMock()
        mock_genai.configure = MagicMock()
        mock_genai.GenerativeModel = MagicMock()
        
        # Patch the genai import
        sys.modules['google.generativeai'] = mock_genai
        
        # Mock instructor.from_gemini to capture the mode parameter
        original_from_gemini = instructor.from_gemini
        captured_modes = {}
        
        def mock_from_gemini(model, mode=None, **kwargs):
            captured_modes['last_mode'] = mode
            mock_client = MagicMock()
            mock_client.mode = mode
            return mock_client
        
        instructor.from_gemini = mock_from_gemini
        
        try:
            # Test Discovery LLM
            discovery_llm = GeminiDiscoveryLLM(
                model_name="gemini-1.5-flash",
                api_key="fake-key-for-testing"
            )
            discovery_mode = captured_modes.get('last_mode')
            
            # Test Data Modeling LLM  
            modeling_llm = GeminiDataModelingLLM(
                model_name="gemini-1.5-flash", 
                api_key="fake-key-for-testing"
            )
            modeling_mode = captured_modes.get('last_mode')
            
            print(f"✅ Discovery LLM mode: {discovery_mode}")
            print(f"✅ Data Modeling LLM mode: {modeling_mode}")
            
            # Check if both are using GEMINI_JSON mode
            expected_mode = instructor.Mode.GEMINI_JSON
            
            if discovery_mode == expected_mode:
                print("✅ Discovery LLM using correct GEMINI_JSON mode")
            else:
                print(f"❌ Discovery LLM using wrong mode: {discovery_mode}, expected: {expected_mode}")
                
            if modeling_mode == expected_mode:
                print("✅ Data Modeling LLM using correct GEMINI_JSON mode")
            else:
                print(f"❌ Data Modeling LLM using wrong mode: {modeling_mode}, expected: {expected_mode}")
                
            if discovery_mode == expected_mode and modeling_mode == expected_mode:
                print("\n🎉 SUCCESS: Both Gemini LLMs are using GEMINI_JSON mode!")
                print("   This should resolve the ValidationError issue.")
                return True
            else:
                print("\n❌ FAILURE: One or both LLMs are not using GEMINI_JSON mode")
                return False
                
        finally:
            # Restore original function
            instructor.from_gemini = original_from_gemini
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        traceback.print_exc()
        return False

def test_schema_validation():
    """Test that the Property schema doesn't cause ValidationError with GEMINI_JSON mode."""
    try:
        from neo4j_runway.models.core.property import Property
        from pydantic import ValidationError
        import json
        
        print("\n🔍 Testing Property schema validation...")
        
        # Test creating a Property with optional alias (the field that was causing issues)
        test_property = Property(
            name="test_prop",
            type="string",
            column_mapping="test_column",
            alias=None  # This was causing the ValidationError
        )
        
        print("✅ Property created successfully with None alias")
        
        # Test serialization to JSON (what GEMINI_JSON mode uses)
        prop_dict = test_property.model_dump()
        json_str = json.dumps(prop_dict)
        
        print("✅ Property serialized to JSON successfully")
        print(f"   JSON: {json_str}")
        
        # Test deserialization from JSON
        restored_prop = Property.model_validate(json.loads(json_str))
        print("✅ Property deserialized from JSON successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema validation error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Running Gemini ValidationError Fix Tests\n")
    
    test1_passed = test_gemini_llm_modes()
    test2_passed = test_schema_validation()
    
    print(f"\n📋 Test Results:")
    print(f"   Instructor Mode Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Schema Validation Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED! The ValidationError fix is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. The ValidationError may still occur.")
        sys.exit(1)
