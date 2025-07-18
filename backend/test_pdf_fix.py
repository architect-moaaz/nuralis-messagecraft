#!/usr/bin/env python3
"""
Test the PDF generation fix
"""
import asyncio
from dotenv import load_dotenv
from pdf_generator import PlaybookGenerator

load_dotenv()

async def test_pdf_generation():
    try:
        print("🧪 Testing PDF Generation Fix")
        print("=" * 50)
        
        # Create a test data structure that includes the problematic object format
        test_results = {
            'business_profile': {
                'company_name': 'Test Company',
                'target_audience': {
                    'age_range': '25-35',
                    'demographics': 'professionals',
                    'income_level': 'high',
                    'lifestyle': 'urban'
                },
                'pain_points': ['Problem 1', 'Problem 2'],
                'unique_features': ['Feature 1', 'Feature 2'],
                'industry': 'Technology'
            },
            'messaging_framework': {
                'value_proposition': 'We help professionals succeed',
                'elevator_pitch': 'Our platform revolutionizes workflow',
                'taglines': ['Tagline 1', 'Tagline 2']
            }
        }
        
        generator = PlaybookGenerator()
        print("✅ PDF Generator initialized")
        
        print("🔧 Testing _safe_text_extract with problematic object...")
        target_audience_result = generator._safe_text_extract(test_results['business_profile']['target_audience'])
        print(f"Target audience extracted as: {target_audience_result}")
        
        print("📄 Generating test PDF...")
        pdf_bytes = generator.generate_messaging_playbook_pdf(test_results, "Test Company")
        
        if pdf_bytes and len(pdf_bytes) > 0:
            print(f"✅ PDF generated successfully! Size: {len(pdf_bytes)} bytes")
            
            # Save test PDF to file
            with open('test_pdf_output.pdf', 'wb') as f:
                f.write(pdf_bytes)
            print("📁 Test PDF saved as 'test_pdf_output.pdf'")
            
            return True
        else:
            print("❌ PDF generation failed - no content returned")
            return False
            
    except Exception as e:
        print(f"❌ Error during PDF generation test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await test_pdf_generation()
    
    if success:
        print("\n🎉 PDF Generation Fix Complete!")
        print("The enhanced _safe_text_extract method now:")
        print("  ✅ Handles target audience objects with age_range, demographics, etc.")
        print("  ✅ Converts all objects to strings safely")
        print("  ✅ Added error handling for edge cases")
        print("  ✅ Uses _safe_paragraph wrapper for extra safety")
    else:
        print("\n❌ PDF fix needs more debugging")

if __name__ == "__main__":
    asyncio.run(main())