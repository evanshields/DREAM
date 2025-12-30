# OpenAI API - Quick Start (5 minutes)

## Step 1: Get Your API Key

1. Go to https://platform.openai.com/api-keys
2. Click **"Create new secret key"**
3. Copy the key (starts with `sk-`)

## Step 2: Add to .env

Create or edit `backend/.env`:

```bash
OPENAI_API_KEY="sk-your-key-here"
```

## Step 3: Install Package

```bash
pip install openai python-dotenv
```

## Step 4: Test It

```bash
python backend/test_openai.py
```

If you see "✅ API Connection Successful!", you're all set!

## Quick Usage Example

```python
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Write a Python function to calculate factorial"}
    ]
)

print(response.choices[0].message.content)
```

## Full Documentation

See `backend/OPENAI_SETUP.md` for:                      
- Detailed setup instructions
- Advanced usage examples
- Integration with FastAPI
- Troubleshooting guide

