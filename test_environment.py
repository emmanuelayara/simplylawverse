#!/usr/bin/env python
"""Test script to verify the Flask environment is working"""

try:
    from app import create_app
    print("✅ App imported successfully")
    
    app = create_app()
    print("✅ App created successfully")
    
    print("\n" + "="*50)
    print("✅ ENVIRONMENT FIXED!")
    print("="*50)
    print("\nYour Flask environment is now working correctly.")
    print("\nTo start the development server, run:")
    print("  flask run --debug")
    print("\nThe app will be available at:")
    print("  http://localhost:5000")
    print("\n" + "="*50)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
