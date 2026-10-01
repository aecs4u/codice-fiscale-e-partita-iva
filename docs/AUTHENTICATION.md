# Authentication Setup Guide

This guide explains how to set up and use Clerk authentication with the python-codice_fiscale FastAPI application.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Clerk Setup](#clerk-setup)
- [Environment Configuration](#environment-configuration)
- [Testing Authentication](#testing-authentication)
- [Using the API with Authentication](#using-the-api-with-authentication)
- [Development vs Production](#development-vs-production)
- [Troubleshooting](#troubleshooting)

## Prerequisites

1. **Install API dependencies**:
   ```bash
   uv sync --extra api
   # or
   pip install 'python-codice_fiscale[api]'
   ```

2. **Create a Clerk account** at [clerk.com](https://clerk.com)

## Clerk Setup

### 1. Create a New Clerk Application

1. Log in to your [Clerk Dashboard](https://dashboard.clerk.com/)
2. Click **"+ Create application"**
3. Choose your application name (e.g., "Fiscal Code Validator")
4. Select authentication methods:
   - **Email** (recommended)
   - **Phone** (optional)
   - **Social providers** (Google, GitHub, etc. - optional)
5. Click **"Create application"**

### 2. Get Your API Keys

After creating the application, you'll see your API keys:

1. **Publishable Key**: Starts with `pk_test_` (for test) or `pk_live_` (for production)
2. **Secret Key**: Starts with `sk_test_` (for test) or `sk_live_` (for production)

⚠️ **Important**: Keep your secret key private and never commit it to version control.

### 3. Configure Authentication Methods

1. In the Clerk Dashboard, go to **"User & Authentication"**
2. Configure your desired sign-in methods:
   - **Email addresses**: Enable email/password authentication
   - **Phone numbers**: Enable SMS authentication
   - **Social connections**: Add OAuth providers (Google, GitHub, etc.)
3. Customize your sign-in/sign-up forms as needed

## Environment Configuration

### Option 1: Environment Variables (Recommended)

Create a `.env` file in your project root:

```bash
# .env
CLERK_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
CLERK_SECRET_KEY=sk_test_your_secret_key_here

# Alternative name (also supported)
# NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
```

### Option 2: System Environment Variables

Export the variables in your shell:

```bash
export CLERK_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
export CLERK_SECRET_KEY=sk_test_your_secret_key_here
```

### Option 3: Docker Environment

If using Docker, add to your `docker-compose.yml`:

```yaml
services:
  api:
    environment:
      - CLERK_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
      - CLERK_SECRET_KEY=sk_test_your_secret_key_here
```

## Testing Authentication

### 1. Check Configuration

Use the included test script to verify your setup:

```bash
python test_clerk_auth.py
```

This script will:
- ✅ Verify environment variables are set
- ✅ Test Clerk authentication initialization
- ✅ Check API endpoints accessibility
- ✅ Provide debugging information

### 2. Start the API Server

```bash
# Start server with authentication enabled
uv run python -m codice_fiscale.__main_api__

# Or start without authentication for testing
CLERK_PUBLISHABLE_KEY="" uv run python -m codice_fiscale.__main_api__
```

### 3. Check Authentication Status

Visit the web interface at [http://localhost:8000](http://localhost:8000) to see the authentication status.

Or check via API:
```bash
curl http://localhost:8000/api | jq '.authentication'
```

## Using the API with Authentication

### 1. Obtain a JWT Token

You need to get a JWT token from Clerk. Here are several methods:

#### Method A: Using Clerk's Frontend SDKs

If you have a frontend application using Clerk:

```javascript
// React/Next.js example
import { useAuth } from '@clerk/nextjs';

function MyComponent() {
  const { getToken } = useAuth();
  
  const callAPI = async () => {
    const token = await getToken();
    
    const response = await fetch('http://localhost:8000/fiscal-code/validate', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ code: 'CCCFBA85D03L219P' })
    });
    
    return response.json();
  };
}
```

#### Method B: Using Clerk's Session Tokens

1. Go to your Clerk Dashboard
2. Navigate to "Sessions" tab
3. Find an active session and copy the JWT token
4. Use it directly in API calls

#### Method C: Programmatic Authentication

```python
import requests
import jwt
from datetime import datetime, timedelta

# For testing purposes - create a test JWT
# NOTE: In production, tokens should come from Clerk's authentication flow
def create_test_jwt(instance_id: str):
    payload = {
        'sub': 'user_test123',
        'iss': f'https://{instance_id}.clerk.accounts.dev',
        'email': 'test@example.com',
        'name': 'Test User',
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow()
    }
    
    # NOTE: This is for testing only - signature verification is disabled
    return jwt.encode(payload, 'secret', algorithm='HS256')

# Extract instance ID from publishable key
publishable_key = "pk_test_instance123_randomstring"
instance_id = publishable_key.split('_')[2]
token = create_test_jwt(instance_id)
```

### 2. Make Authenticated API Calls

#### Using cURL:

```bash
# Get your JWT token (replace with actual token)
TOKEN="your_jwt_token_here"

# Validate fiscal code
curl -X POST "http://localhost:8000/fiscal-code/validate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code": "CCCFBA85D03L219P"}'

# Encode fiscal code
curl -X POST "http://localhost:8000/fiscal-code/encode" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "lastname": "Rossi",
    "firstname": "Mario", 
    "gender": "M",
    "birthdate": "1985-03-04",
    "birthplace": "Roma"
  }'

# Validate VAT number
curl -X POST "http://localhost:8000/vat/validate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"partita_iva": "12345678901"}'
```

#### Using Python requests:

```python
import requests

TOKEN = "your_jwt_token_here"
BASE_URL = "http://localhost:8000"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Validate fiscal code
response = requests.post(
    f"{BASE_URL}/fiscal-code/validate",
    headers=headers,
    json={"code": "CCCFBA85D03L219P"}
)

print(response.json())
```

#### Using JavaScript/Node.js:

```javascript
const TOKEN = "your_jwt_token_here";
const BASE_URL = "http://localhost:8000";

const headers = {
    "Authorization": `Bearer ${TOKEN}`,
    "Content-Type": "application/json"
};

// Validate fiscal code
const response = await fetch(`${BASE_URL}/fiscal-code/validate`, {
    method: 'POST',
    headers: headers,
    body: JSON.stringify({ code: 'CCCFBA85D03L219P' })
});

const result = await response.json();
console.log(result);
```

## Development vs Production

### Development Environment

- Use `pk_test_` and `sk_test_` keys
- JWT signature verification is disabled for demo purposes
- Suitable for testing and development

### Production Environment

⚠️ **Important Security Notes**:

1. **Enable JWT signature verification**:
   ```python
   # In codice_fiscale/auth.py, replace line 57:
   # options={"verify_signature": False}  # DANGER: Only for demo!
   # With proper JWKS verification:
   
   import requests
   from cryptography.hazmat.primitives import serialization
   
   def get_jwks_keys(jwks_url):
       response = requests.get(jwks_url)
       jwks = response.json()
       return jwks['keys']
   
   # Use proper key verification in verify_token method
   ```

2. **Use production keys**: `pk_live_` and `sk_live_`
3. **Secure environment variables**: Use secure secret management
4. **Enable HTTPS**: Never use HTTP in production
5. **Configure CORS**: Restrict allowed origins

### Environment-Specific Configuration

```bash
# Development
CLERK_PUBLISHABLE_KEY=pk_test_xxxxx
CLERK_SECRET_KEY=sk_test_xxxxx
DEBUG=true

# Production  
CLERK_PUBLISHABLE_KEY=pk_live_xxxxx
CLERK_SECRET_KEY=sk_live_xxxxx
DEBUG=false
```

## Troubleshooting

### Common Issues

#### 1. "Not authenticated" (403 Forbidden)

**Cause**: Missing or invalid JWT token
**Solution**: 
- Verify JWT token is included in `Authorization: Bearer <token>` header
- Check token hasn't expired
- Ensure token is from correct Clerk instance

#### 2. "Invalid issuer" Error

**Cause**: JWT token issuer doesn't match Clerk instance
**Solution**:
- Verify `CLERK_PUBLISHABLE_KEY` matches the instance that issued the token
- Check token payload `iss` claim matches expected format

#### 3. Authentication Unexpectedly Disabled

**Cause**: Environment variables not set or empty
**Solution**:
```bash
# Check environment variables
echo "CLERK_PUBLISHABLE_KEY: $CLERK_PUBLISHABLE_KEY"
echo "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: $NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY"

# Ensure they're not empty strings
python test_clerk_auth.py
```

#### 4. Import Errors

**Cause**: Missing API dependencies
**Solution**:
```bash
# Install with API extras
uv sync --extra api
# or
pip install 'python-codice_fiscale[api]'
```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# In your application
logger = logging.getLogger(__name__)
logger.debug("Authentication status: %s", AUTH_ENABLED)
```

### Testing Different Scenarios

```bash
# Test without authentication
CLERK_PUBLISHABLE_KEY="" uv run python -m pytest tests/test_api.py

# Test with authentication
CLERK_PUBLISHABLE_KEY="pk_test_xxx" uv run python -m pytest tests/test_auth.py

# Run authentication diagnosis
python test_clerk_auth.py
```

## Security Best Practices

1. **Never commit secrets**: Use `.env` files and add them to `.gitignore`
2. **Use environment-specific keys**: Test keys for development, live keys for production
3. **Implement proper JWKS verification**: Don't disable signature verification in production
4. **Use HTTPS**: Always use secure connections in production
5. **Validate token claims**: Check `exp`, `iss`, `sub` claims
6. **Implement rate limiting**: Protect against abuse
7. **Monitor authentication logs**: Track failed authentication attempts

## Need Help?

- **Clerk Documentation**: [docs.clerk.com](https://docs.clerk.com)
- **Clerk Support**: Available through their dashboard
- **Project Issues**: [GitHub Issues](https://github.com/fabiocaccamo/python-codice_fiscale/issues)
- **Test Script**: Run `python test_clerk_auth.py` for diagnostic information

---

For more information about the python-codice_fiscale library, see the main [README.md](README.md).