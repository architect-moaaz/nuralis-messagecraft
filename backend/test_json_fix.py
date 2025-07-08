#!/usr/bin/env python3
"""
Test JSON parsing fix for percentage values
"""

import re
import json

def test_percentage_fix():
    """Test the regex fix for percentage values"""
    
    # Test case with the problematic JSON
    problematic_json = '''{
    "premium_quality_scores": {
        "messaging_quality_score": 9.2,
        "differentiation_score": 9.4,
        "emotional_resonance_score": 8.8,
        "rational_strength_score": 9.6,
        "clarity_score": 9.5,
        "credibility_score": 9.3,
        "urgency_score": 8.9,
        "proof_score": 9.4,
        "relevance_score": 9.7,
        "conversion_score": 9.2
    },
    "overall_quality_score": 9.3,
    "quality_percentage": 93%,
    "framework_analysis": {
        "aida_effectiveness": "Strong AIDA implementation",
        "pas_effectiveness": "Excellent PAS framework usage",
        "bab_effectiveness": "Good BAB structure",
        "emotional_rational_balance": "Strong rational appeal"
    }
}'''
    
    print("🧪 Testing JSON parsing fix")
    print("=" * 50)
    
    print("\n1️⃣ Original JSON (with error):")
    print(problematic_json[:200] + "...")
    
    # Apply the fix
    fixed_json = re.sub(r':\s*(\d+(?:\.\d+)?%)', r': "\1"', problematic_json)
    
    print("\n2️⃣ Fixed JSON:")
    print(fixed_json[:200] + "...")
    
    # Try to parse it
    print("\n3️⃣ Parsing test:")
    try:
        parsed = json.loads(fixed_json)
        print("✅ JSON parsed successfully!")
        print(f"   Quality percentage: {parsed['quality_percentage']}")
        print(f"   Overall score: {parsed['overall_quality_score']}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        return False
    
    # Test other percentage patterns
    print("\n4️⃣ Testing various percentage patterns:")
    test_cases = [
        ('{"score": 95%}', '{"score": "95%"}'),
        ('{"value": 85.5%}', '{"value": "85.5%"}'),
        ('{"rate": 100%, "other": "text"}', '{"rate": "100%", "other": "text"}'),
        ('{"mixed": 75%, "quoted": "50%"}', '{"mixed": "75%", "quoted": "50%"}'),
    ]
    
    for original, expected in test_cases:
        fixed = re.sub(r':\s*(\d+(?:\.\d+)?%)', r': "\1"', original)
        print(f"   {original} → {fixed}")
        assert fixed == expected, f"Expected {expected}, got {fixed}"
    
    print("\n✅ All tests passed!")
    return True

if __name__ == "__main__":
    test_percentage_fix()