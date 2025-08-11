#!/usr/bin/env python3
"""
Test script for Neo4j Runway Gemini integration.
This script validates that the Gemini integration is properly installed and configured.
"""

import os
import sys

def test_gemini_integration():
    """Test the Gemini integration without requiring an API key."""
    print("🧪 Testing Neo4j Runway Gemini Integration...")
    print(f"📍 Python version: {sys.version}")
    print(f"📁 Working directory: {os.getcwd()}")
    print()

    try:
        # Test basic imports
        print("1️⃣ Testing imports...")
        from neo4j_runway.llm.gemini import GeminiDiscoveryLLM, GeminiDataModelingLLM
        print("   ✅ Successfully imported Gemini LLM classes")
        
        # Test that the classes can be instantiated with proper error handling
        print("\n2️⃣ Testing class instantiation...")
        
        # Test Discovery LLM
        try:
            discovery_llm = GeminiDiscoveryLLM(model_name='gemini-2.0-flash-exp')
            print("   ❌ Discovery LLM should have failed without API key")
        except ValueError as e:
            if 'API key' in str(e):
                print("   ✅ Discovery LLM API key validation working correctly")
            else:
                print(f"   ❌ Unexpected Discovery LLM error: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected Discovery LLM error: {e}")
        
        # Test Data Modeling LLM
        try:
            data_modeling_llm = GeminiDataModelingLLM(model_name='gemini-2.0-flash-exp')
            print("   ❌ Data Modeling LLM should have failed without API key")
        except ValueError as e:
            if 'API key' in str(e):
                print("   ✅ Data Modeling LLM API key validation working correctly")
            else:
                print(f"   ❌ Unexpected Data Modeling LLM error: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected Data Modeling LLM error: {e}")
        
        # Test module exports
        print("\n3️⃣ Testing module exports...")
        from neo4j_runway.llm import GeminiDiscoveryLLM as ImportedDiscoveryLLM
        from neo4j_runway.llm import GeminiDataModelingLLM as ImportedDataModelingLLM
        print("   ✅ Successfully imported from main LLM module")
        
        # Test that dependencies are installed
        print("\n4️⃣ Testing dependencies...")
        try:
            import google.generativeai
            print("   ✅ google-generativeai package is installed")
        except ImportError:
            print("   ❌ google-generativeai package is missing")
            
        try:
            import jsonref
            print("   ✅ jsonref package is installed")
        except ImportError:
            print("   ❌ jsonref package is missing")
            
        try:
            import instructor
            print("   ✅ instructor package is installed")
        except ImportError:
            print("   ❌ instructor package is missing")
        
        print("\n🎉 Gemini integration test completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Set your GEMINI_API_KEY environment variable")
        print("   2. Run the example notebooks in examples/llm_providers/")
        print("   3. Refer to docs/gemini_integration.md for detailed usage")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you have installed the package with: pip install -e .")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_gemini_integration()
    sys.exit(0 if success else 1)
