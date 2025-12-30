"""
Test script for OpenAI API connection
Run this to verify your OpenAI API key is working correctly.
"""

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Load environment variables from .env file
load_dotenv()

def test_openai_connection():
    """Test OpenAI API connection and basic functionality"""
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in environment variables")
        print("\nTroubleshooting:")
        print("1. Create a .env file in the backend/ directory")
        print("2. Add: OPENAI_API_KEY='sk-your-key-here'")
        print("3. Make sure python-dotenv is installed: pip install python-dotenv")
        return False
    
    if not api_key.startswith("sk-"):
        print("⚠️  WARNING: API key doesn't start with 'sk-' - may be invalid")
    
    print(f"✅ Found API key: {api_key[:7]}...{api_key[-4:]}")
    print("\n🔌 Testing OpenAI API connection...\n")
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Test with a simple request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using cheaper model for testing
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": "Say 'API connection successful!' if you can read this, then tell me what model you are."}
            ],
            max_tokens=100
        )
        
        print("✅ API Connection Successful!")
        print(f"\n📝 Response: {response.choices[0].message.content}")
        print(f"🤖 Model: {response.model}")
        print(f"📊 Tokens used: {response.usage.total_tokens}")
        print(f"   - Prompt tokens: {response.usage.prompt_tokens}")
        print(f"   - Completion tokens: {response.usage.completion_tokens}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to OpenAI API: {e}")
        print("\nTroubleshooting:")
        print("1. Verify your API key is correct at https://platform.openai.com/api-keys")
        print("2. Check that your account has credits/billing set up")
        print("3. Verify your internet connection")
        print("4. Check OpenAI status: https://status.openai.com/")
        return False

def test_code_generation():
    """Test code generation capability (Codex-style)"""
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return False
    
    print("\n" + "="*50)
    print("🧪 Testing Code Generation...")
    print("="*50 + "\n")
    
    try:
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert Python developer. Write clean, well-documented code."},
                {"role": "user", "content": "Write a Python function that calculates the factorial of a number. Include type hints and a docstring."}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        print("✅ Code Generation Test Successful!")
        print("\n📝 Generated Code:")
        print("-" * 50)
        print(response.choices[0].message.content)
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Code generation test failed: {e}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("OpenAI API Connection Test")
    print("="*50 + "\n")
    
    # Test basic connection
    if test_openai_connection():
        # If basic test passes, test code generation
        test_code_generation()
        
        print("\n" + "="*50)
        print("✅ All tests completed!")
        print("="*50)
        print("\nYou can now use OpenAI API in your code.")
        print("See backend/OPENAI_SETUP.md for usage examples.")
    else:
        print("\n" + "="*50)
        print("❌ Setup incomplete. Please fix the issues above.")
        print("="*50)

