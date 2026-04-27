# Insighta Labs+ — CLI

A globally installable command-line tool for interacting with the Insighta Labs+ platform. Supports full GitHub OAuth login with PKCE, profile management, and CSV export.

## Installation

**Requirements:** Python 3.12+, [uv](https://github.com/astral-sh/uv)

```bash
git clone https://github.com/HNG-Backend-Tasks/insighta-cli
cd insighta-cli
uv tool install .
```

After installation, `insighta` is available globally from any directory.

For development (changes reflect immediately without reinstalling):
```bash
uv pip install -e .
```

## Configuration

Create a `.env` file in the repo root or set environment variables:

```env
API_BASE_URL=https://your-deployed-backend-url.koyeb.app
GITHUB_CLIENT_ID_CLI=your_cli_github_client_id
```

For local development:
```env
API_BASE_URL=http://localhost:8000
GITHUB_CLIENT_ID_CLI=your_cli_github_client_id
```

## Authentication Flow

`insighta login` implements the full OAuth 2.0 PKCE flow:

```
1. CLI generates:
   - state         → random string to prevent CSRF
   - code_verifier → random secret (never sent to GitHub)
   - code_challenge → base64url(sha256(code_verifier))

2. CLI starts a local callback server on port 8765

3. CLI opens GitHub OAuth in the browser:
   https://github.com/login/oauth/authorize
     ?client_id=...
     &code_challenge=...
     &code_challenge_method=S256
     &state=...
     &redirect_uri=http://localhost:8765/callback

4. User authenticates on GitHub

5. GitHub redirects to http://localhost:8765/callback?code=...&state=...

6. CLI validates state matches what was generated (CSRF check)

7. CLI sends code + code_verifier to backend:
   GET /auth/github/callback?code=...&code_verifier=...&client_source=cli

8. Backend exchanges with GitHub, creates/updates user, returns tokens

9. CLI stores tokens at ~/.insighta/credentials.json
   Prints: Logged in as @username
```

## Token Handling

Tokens are stored at `~/.insighta/credentials.json`:

```json
{
  "access_token": "eyJ...",
  "refresh_token": "abc123...",
  "username": "danielpopoola"
}
```

The shared HTTP client automatically handles token expiry:

- Every request attaches `Authorization: Bearer <access_token>` and `X-API-Version: 1`
- On 401 response: client automatically calls `POST /auth/refresh` with the refresh token
- On successful refresh: new token pair is saved and the original request is retried once
- If refresh also fails (expired or already used): credentials are cleared and user is prompted to run `insighta login`

Access tokens expire in 3 minutes. Refresh tokens expire in 5 minutes. After 5 minutes of inactivity a fresh login is required.

## Commands

### Auth

```bash
# Login with GitHub (opens browser)
insighta login

# Show logged in user
insighta whoami

# Logout and clear credentials
insighta logout
```

### Profiles

```bash
# List all profiles (paginated)
insighta profiles list

# Filter by gender
insighta profiles list --gender male

# Filter by country and age group
insighta profiles list --country NG --age-group adult

# Filter by age range
insighta profiles list --min-age 25 --max-age 40

# Sort results
insighta profiles list --sort-by age --order desc

# Pagination
insighta profiles list --page 2 --limit 20

# Combine filters
insighta profiles list --gender male --country NG --min-age 25 --sort-by age --order desc

# Get a single profile by ID
insighta profiles get <id>

# Natural language search
insighta profiles search "young males from nigeria"
insighta profiles search "females above 30"
insighta profiles search "adult males from south africa"

# Create a profile (admin only)
insighta profiles create --name "Harriet Tubman"

# Export to CSV (saved to current directory)
insighta profiles export --format csv

# Export with filters
insighta profiles export --format csv --gender male --country NG
```

## Output

All list and search results render as a structured table:

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┓
┃ ID                                   ┃ Name           ┃ Gender ┃ Age ┃ Age Group ┃ Country ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━╇━━━━━━━━━━━╇━━━━━━━━━┩
│ 019dcab5-b7f3-7194-be44-7b76c23360ca │ Kwame Mensah   │ male   │ 25  │ adult     │ NG      │
│ 019dcab5-b7f3-7194-be44-7b76c23360cb │ Amina Diallo   │ female │ 17  │ teenager  │ KE      │
└──────────────────────────────────────┴────────────────┴────────┴─────┴───────────┴─────────┘

Page 1 of 203 (2026 total)
```

A loading spinner is shown while requests are in flight.

## Running Tests

```bash
uv run pytest tests/ -v
```

## Project Structure

```
insighta/
├── __init__.py
├── main.py       ← typer app, command registration
├── auth.py       ← login, logout, whoami, PKCE helpers, token storage
├── http.py       ← shared APIClient with auto-refresh
├── profiles.py   ← all profiles commands
└── display.py    ← rich table rendering
tests/
├── test_auth.py
├── test_http.py
└── test_profiles.py
```