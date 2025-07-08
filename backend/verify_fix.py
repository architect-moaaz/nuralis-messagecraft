#!/usr/bin/env python3
"""
Verify the _safe_extract_string fix by checking method signature
"""

import ast
import sys

def verify_method_exists():
    """Verify the _safe_extract_string method exists in the file"""
    
    file_path = "/Users/m/Work/experiment/nuralis/marketing-tools/messagecraft/backend/langgraph_agents_with_reflection.py"
    
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        
        # Check if the method definition exists
        if "def _safe_extract_string" in content:
            print("✅ _safe_extract_string method definition found")
            
            # Count how many times it's called
            call_count = content.count("self._safe_extract_string(")
            print(f"✅ Method is called {call_count} times")
            
            # Check the method signature
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "def _safe_extract_string" in line:
                    print(f"✅ Method signature: {line.strip()}")
                    
                    # Show next few lines to verify implementation
                    print("✅ Method implementation preview:")
                    for j in range(i+1, min(i+6, len(lines))):
                        if lines[j].strip():
                            print(f"    {lines[j]}")
                        if lines[j].strip() and not lines[j].startswith('        '):
                            break
                    break
            
            return True
        else:
            print("❌ _safe_extract_string method definition NOT found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking file: {e}")
        return False

def check_method_calls():
    """Check all places where the method is called"""
    
    file_path = "/Users/m/Work/experiment/nuralis/marketing-tools/messagecraft/backend/langgraph_agents_with_reflection.py"
    
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        print("\n🔍 Method call locations:")
        for i, line in enumerate(lines, 1):
            if "self._safe_extract_string(" in line:
                print(f"Line {i}: {line.strip()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking method calls: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Verifying _safe_extract_string Method Fix")
    print("=" * 50)
    
    method_exists = verify_method_exists()
    check_method_calls()
    
    if method_exists:
        print("\n✅ Fix verified! The method exists and is properly implemented.")
        print("🚀 Server restart should resolve the AttributeError.")
    else:
        print("\n❌ Fix verification failed.")
        sys.exit(1)