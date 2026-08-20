# #6 — Adding an API Key
> 🔗 [Watch Video](https://www.youtube.com/watch?v=RXOPjpvTEZM) | **Status:** ☐ Watched

---

## 📝 Summary
By default, Gemini CLI uses your Google account login for free access. However, you can optionally add a **Gemini API key** from Google AI Studio to get higher rate limits, access to newer models, or to avoid browser-based authentication (useful in CI/CD or headless environments). This video shows how to get the key and configure it.

## 🔑 Key Concepts
- **Default**: Google account auth (OAuth) — free, limited rate
- **API Key**: higher limits, programmatic access, no browser login needed
- Get your free API key from: [Google AI Studio](https://aistudio.google.com/apikey)
- API key is stored as an **environment variable** — never hardcode it
- Free tier includes: 15 requests/min, 1 million tokens/min (Gemini 2.0 Flash)

## 💻 Setting Up the API Key
```bash
# Step 1: Get key from https://aistudio.google.com/apikey

# Step 2: Set as environment variable (Windows - permanent)
# Open PowerShell as Admin:
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "your-key-here", "User")

# Step 3: Verify it's set
echo $env:GEMINI_API_KEY

# Step 4: Restart terminal, then launch Gemini CLI
gemini
# It will now use the API key instead of OAuth
```

## 🔧 Alternative: .env file (project-level)
```bash
# Create .env in project root
echo "GEMINI_API_KEY=your-key-here" > .env

# Add to .gitignore immediately!
echo ".env" >> .gitignore
```

## ⚠️ Security Rules
- **NEVER** commit your API key to Git
- **NEVER** hardcode it in any script or file
- Always use environment variables or secret managers
- Rotate the key if you accidentally expose it

## 📊 Free Tier Limits (as of 2025)
| Model | RPM | TPM | RPD |
|-------|-----|-----|-----|
| Gemini 2.0 Flash | 15 | 1,000,000 | 1,500 |
| Gemini 2.5 Pro | 5 | 250,000 | 50 |

## ❓ Questions / Unclear Points
- Can you use the API key in CI/CD pipelines? (Yes — set as a secret env variable)
- Which is better — OAuth or API key? (API key for automation; OAuth for daily dev use)

## ✅ Action Items
- [ ] Get a free API key from https://aistudio.google.com/apikey
- [ ] Set as `GEMINI_API_KEY` environment variable
- [ ] Add `.env` to your `.gitignore`
