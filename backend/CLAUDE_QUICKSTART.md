# Claude API - Quick Start (5 minutes)

## Step 1: Get Your API Key

1. Go to https://console.anthropic.com/settings/keys
2. Click **"Create Key"**
3. Copy the key (starts with `sk-ant-`)
4. **Important:** Save it immediately - you won't be able to see it again!

## Step 2: Add to .env

Create or edit `backend/.env`:

```bash
ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

**Note:** If you're using PowerShell on Windows, you may need to use single quotes or escape the quotes:
```powershell
ANTHROPIC_API_KEY='sk-ant-your-key-here'
```

## Step 3: Install Package

Open your terminal in Cursor (`` Ctrl+` ``) and run:

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment (if you have one)
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install anthropic package
pip install anthropic python-dotenv
```

## Step 4: Test It

Create a test file to verify your setup:

```bash
# In backend directory
python test_claude.py
```

If you see "✅ Claude API Connection Successful!", you're all set!

## Quick Usage Example

Create `backend/test_claude.py`:

```python
from anthropic import Anthropic
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Claude client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Test the connection
try:
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=100,
        messages=[
            {"role": "user", "content": "Say 'Hello, Claude is working!' in one sentence."}
        ]
    )
    
    print("✅ Claude API Connection Successful!")
    print(f"Response: {response.content[0].text}")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check that ANTHROPIC_API_KEY is set in backend/.env")
    print("2. Verify your API key is correct (starts with sk-ant-)")
    print("3. Make sure you've installed: pip install anthropic python-dotenv")
```

## Using Claude in Your Code

### Basic Example

```python
from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

response = client.messages.create(
    model="claude-3-5-haiku-20241022",  # Fast, cost-effective
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Extract the property address from this text: ..."}
    ]
)

print(response.content[0].text)
```

### Available Models

| Model | Use Case | Cost (Input/Output) |
|-------|----------|---------------------|
| `claude-3-5-haiku-20241022` | Fast, routine tasks | $0.25/$1.25 per 1M tokens |
| `claude-3-5-sonnet-20241022` | Complex reasoning | $3/$15 per 1M tokens |
| `claude-3-opus-20240229` | Premium, edge cases | $15/$75 per 1M tokens |

### For Document Extraction (DREAM AI)

```python
from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Extract data from document text
response = client.messages.create(
    model="claude-3-5-haiku-20241022",
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": f"""
            Extract the following information from this offering memorandum:
            - Property address
            - Number of units
            - Asking price
            - Current rent
            
            Document text:
            {document_text}
            """
        }
    ]
)

extracted_data = response.content[0].text
```

## Troubleshooting

### Error: "API key not found"
- Make sure `backend/.env` exists and contains `ANTHROPIC_API_KEY="sk-ant-..."`
- Verify you're loading the .env file with `load_dotenv()`
- Check that you're in the correct directory when running Python

### Error: "Invalid API key"
- Verify your key starts with `sk-ant-`
- Check that you copied the entire key (they're long!)
- Make sure there are no extra spaces or quotes in your .env file

### Error: "Module 'anthropic' not found"
```bash
pip install anthropic python-dotenv
```

### PowerShell Issues on Windows
If you have issues with quotes in PowerShell, try:
```powershell
# Use single quotes
$env:ANTHROPIC_API_KEY='sk-ant-your-key'
```

Or set it directly in your .env file without quotes:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## Next Steps

1. ✅ **You are here** - Claude API is set up
2. 🔄 **Test with a real document** - Try extracting data from a sample OM
3. 🔄 **Integrate into FastAPI** - Add Claude calls to your API endpoints
4. 🔄 **Add error handling** - Handle rate limits and API errors gracefully

## Full Documentation

- **Anthropic Python SDK:** https://github.com/anthropics/anthropic-sdk-python
- **API Reference:** https://docs.anthropic.com/claude/reference
- **Model Pricing:** https://www.anthropic.com/pricing

---

**Ready to use Claude!** 🚀


