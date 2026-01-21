#!/usr/bin/env python3
"""
Quick test to verify the ValidationError fix
Run this in a fresh Python session
"""

def quick_test():
    import instructor
    
    # Test that both classes use GEMINI_JSON mode
    try:
        from neo4j_runway.llm.gemini.discovery import GeminiDiscoveryLLM
        from neo4j_runway.llm.gemini.data_modeling import GeminiDataModelingLLM
        
        print("✅ Successfully imported Gemini LLMs")
        print(f"Expected mode: {instructor.Mode.GEMINI_JSON}")
        
        # Check source code for the mode
        import inspect
        
        dm_source = inspect.getsource(GeminiDataModelingLLM.__init__)
        disc_source = inspect.getsource(GeminiDiscoveryLLM.__init__)
        
        dm_has_json = "GEMINI_JSON" in dm_source
        disc_has_json = "GEMINI_JSON" in disc_source
        
        print(f"GeminiDataModelingLLM uses GEMINI_JSON: {dm_has_json}")
        print(f"GeminiDiscoveryLLM uses GEMINI_JSON: {disc_has_json}")
        
        if dm_has_json and disc_has_json:
            print("\n🎉 SUCCESS: ValidationError fix is properly applied!")
            print("If you're still seeing the error, restart your Jupyter kernel.")
        else:
            print("\n❌ ISSUE: Fix not properly applied")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_test()
