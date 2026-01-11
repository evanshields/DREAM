"""
Quick test script to verify Claude API setup
Run: python test_claude.py
"""

import sys
import io
# Fix encoding for Windows terminals
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from anthropic import Anthropic
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_claude_connection():
    """Test Claude API connection and basic functionality"""
    
    # Get API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("[X] Error: ANTHROPIC_API_KEY not found in environment")
        print("\nTroubleshooting:")
        print("1. Create backend/.env file")
        print("2. Add: ANTHROPIC_API_KEY='sk-ant-your-key-here'")
        print("3. Make sure python-dotenv is installed: pip install python-dotenv")
        return False
    
    if not api_key.startswith("sk-ant-"):
        print("[X] Error: API key format looks incorrect")
        print("Expected format: sk-ant-...")
        print(f"Got: {api_key[:10]}...")
        return False
    
    print("[OK] API Key found!")
    print(f"   Key starts with: {api_key[:10]}...")
    
    # Initialize Claude client
    try:
        client = Anthropic(api_key=api_key)
        print("[OK] Claude client initialized")
    except Exception as e:
        print(f"[X] Error initializing client: {e}")
        return False
    
    # Test API call
    print("\n[TEST] Testing API call...")
    try:
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=100,
            messages=[
                {
                    "role": "user", 
                    "content": "Say 'Hello! Claude API is working correctly.' in exactly one sentence."
                }
            ]
        )
        
        print("[OK] Claude API Connection Successful!")
        print(f"\n[RESPONSE]")
        print(f"   {response.content[0].text}")
        print(f"\n[USAGE]")
        print(f"   Input tokens: {response.usage.input_tokens}")
        print(f"   Output tokens: {response.usage.output_tokens}")
        return True
        
    except Exception as e:
        print(f"[X] API Call Failed: {e}")
        print("\nTroubleshooting:")
        print("1. Verify your API key is correct at https://console.anthropic.com/settings/keys")
        print("2. Check your internet connection")
        print("3. Verify you have API credits/usage available")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Claude API Connection Test")
    print("=" * 60)
    print()
    
    success = test_claude_connection()
    
    print()
    print("=" * 60)
    if success:
        print("[SUCCESS] All tests passed! Claude API is ready to use.")
    else:
        print("[FAILED] Tests failed. Please check the errors above.")
    print("=" * 60)

