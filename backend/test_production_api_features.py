"""
Test script to verify production API has all required features
"""
import sys
import importlib
import inspect

def test_api_features():
    """Test that production API has all required features"""
    
    # Import the production API
    try:
        prod_api = importlib.import_module("production_api")
        print("✅ Production API imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import production API: {e}")
        return False
    
    # Check for required endpoints
    required_endpoints = [
        "get_user_playbooks",
        "get_user_playbooks_alt", 
        "get_playbook",
        "download_playbook",
        "delete_playbook",
        "get_playbook_status",
        "get_generation_progress"
    ]
    
    missing_endpoints = []
    for endpoint in required_endpoints:
        if not hasattr(prod_api, endpoint):
            missing_endpoints.append(endpoint)
    
    if missing_endpoints:
        print(f"❌ Missing endpoints: {missing_endpoints}")
        return False
    else:
        print("✅ All required endpoints present")
    
    # Check for required imports
    required_imports = ["io", "json", "PlaybookGenerator"]
    
    # Check io and json imports
    if not hasattr(prod_api, 'io'):
        print("❌ Missing io import")
        return False
    
    if not hasattr(prod_api, 'json'):
        print("❌ Missing json import")
        return False
    
    # Check PlaybookGenerator
    if not hasattr(prod_api, 'playbook_generator'):
        print("❌ Missing playbook_generator instance")
        return False
    
    print("✅ All required imports present")
    
    # Check endpoint signatures
    app_routes = []
    for name, obj in inspect.getmembers(prod_api):
        if hasattr(obj, '__wrapped__') and hasattr(obj, '__name__'):
            app_routes.append(obj.__name__)
    
    print(f"✅ Found {len(app_routes)} API endpoints")
    
    # Check for StreamingResponse usage in download endpoint
    try:
        source = inspect.getsource(prod_api.download_playbook)
        if "StreamingResponse" in source and "application/pdf" in source:
            print("✅ Download endpoint properly configured")
        else:
            print("❌ Download endpoint missing StreamingResponse or PDF config")
            return False
    except:
        print("❌ Could not verify download endpoint")
        return False
    
    return True

if __name__ == "__main__":
    success = test_api_features()
    if success:
        print("\n🎉 Production API successfully updated with all enhanced features!")
    else:
        print("\n❌ Production API update incomplete")
        sys.exit(1)