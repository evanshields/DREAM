# OpenAI API Setup Guide

This guide will help you set up OpenAI API access for use with ChatGPT/Codex while waiting for Cursor to reconnect with Claude.

## Step 1: Get Your OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to **API Keys** section: https://platform.openai.com/api-keys
4. Click **"Create new secret key"**
5. Give it a name (e.g., "Dream AI Development")
6. **Copy the key immediately** - you won't be able to see it again!

## Step 2: Add API Key to Environment

### Option A: Add to existing `.env` file

If you have a `backend/.env` file, add this line:

```bash
OPENAI_API_KEY="sk-your-key-here"
```

### Option B: Create new `.env` file

Create `backend/.env` with:

```bash
# OpenAI API
OPENAI_API_KEY="sk-your-key-here"

# Other existing keys (if you have them)
ANTHROPIC_API_KEY="sk-ant-..."
PERPLEXITY_API_KEY="pplx-..."
```

**Important:** Never commit `.env` files to git! They should already be in `.gitignore`.

## Step 3: Install OpenAI Python Package

```bash
# Activate your virtual environment first
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install openai
```

Or add to `requirements.txt`:

```bash
echo "openai>=1.0.0" >> backend/requirements.txt
pip install -r backend/requirements.txt
```

## Step 4: Test the Connection

Create a test script `backend/test_openai.py`:

```python
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Test the connection
try:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful coding assistant."},
            {"role": "user", "content": "Say 'API connection successful!' if you can read this."}
        ],
        max_tokens=50
    )
    
    print("✅ API Connection Successful!")
    print(f"Response: {response.choices[0].message.content}")
    print(f"Model: {response.model}")
    print(f"Tokens used: {response.usage.total_tokens}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check that OPENAI_API_KEY is set in .env")
    print("2. Verify your API key is valid at https://platform.openai.com/api-keys")
    print("3. Check your account has credits/billing set up")
```

Run the test:

```bash
python backend/test_openai.py
```

## Step 5: Usage Examples

### Basic Chat Completion

```python
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a Python coding assistant."},
        {"role": "user", "content": "Write a function to calculate factorial"}
    ]
)

print(response.choices[0].message.content)
```

### Code Generation (Codex-style)

```python
response = client.chat.completions.create(
    model="gpt-4",  # or "gpt-3.5-turbo" for faster/cheaper
    messages=[
        {"role": "system", "content": "You are an expert Python developer. Write clean, well-documented code."},
        {"role": "user", "content": "Create a FastAPI endpoint that accepts a POST request with JSON data and returns a processed result."}
    ],
    temperature=0.7,
    max_tokens=1000
)

code = response.choices[0].message.content
print(code)
```

### Streaming Responses (for longer outputs)

```python
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Explain how FastAPI works"}
    ],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
```

## Step 6: Integration with Your Backend

If you want to add OpenAI endpoints to your FastAPI backend, you can add this to `backend/api/endpoints.py`:

```python
from openai import OpenAI
import os

# Initialize OpenAI client (do this once, maybe in a config module)
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Add a new router
ai_router = APIRouter(prefix="/api/ai", tags=["AI"])

@ai_router.post("/chat")
async def chat_with_openai(request: ChatRequest):
    """Chat with OpenAI GPT models"""
    try:
        response = openai_client.chat.completions.create(
            model=request.model or "gpt-4",
            messages=request.messages,
            temperature=request.temperature or 0.7,
            max_tokens=request.max_tokens or 1000
        )
        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ChatRequest(BaseModel):
    messages: List[dict]
    model: Optional[str] = "gpt-4"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
```

## Pricing & Usage Limits

- **GPT-4**: ~$0.03 per 1K input tokens, ~$0.06 per 1K output tokens
- **GPT-3.5-turbo**: ~$0.0015 per 1K input tokens, ~$0.002 per 1K output tokens
- Check your usage at: https://platform.openai.com/usage
- Set spending limits at: https://platform.openai.com/account/billing/limits

## Troubleshooting

### "Invalid API Key"
- Verify the key starts with `sk-`
- Check for extra spaces when copying
- Ensure the key is in your `.env` file

### "Insufficient quota"
- Add payment method at https://platform.openai.com/account/billing
- Check your usage limits

### "Rate limit exceeded"
- You're making too many requests too quickly
- Add delays between requests or implement retry logic

### Module not found
- Make sure you installed: `pip install openai python-dotenv`
- Check your virtual environment is activated

## Next Steps

Once set up, you can:
1. Use OpenAI API for code generation and assistance
2. Integrate it into your FastAPI backend
3. Use it as a fallback when Claude is unavailable
4. Build custom AI features for your Dream AI platform

## Resources

- [OpenAI Python SDK Docs](https://github.com/openai/openai-python)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [OpenAI Pricing](https://openai.com/pricing)
- [OpenAI Platform Dashboard](https://platform.openai.com/)







