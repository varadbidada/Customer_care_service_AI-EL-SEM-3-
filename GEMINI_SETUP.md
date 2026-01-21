# Google Gemini API Setup Guide

## Getting Your Free Gemini API Key

1. **Visit Google AI Studio**: Go to [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)

2. **Sign in**: Use your Google account to sign in

3. **Create API Key**:

   - Click "Create API Key"
   - Choose "Create API key in new project" (recommended)
   - Copy the generated API key

4. **Add to Environment**:
   - Open the `.env` file in your project
   - Replace `your_gemini_api_key_here` with your actual API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

## Free Tier Limits

Google Gemini offers generous free tier limits:

- **15 requests per minute**
- **1,500 requests per day**
- **1 million tokens per minute**
- **1.5 million tokens per day**

This is more than enough for development and testing!

## Benefits of Gemini over OpenAI

✅ **Free to use** - No credit card required  
✅ **High quality responses** - Comparable to GPT-3.5  
✅ **Fast response times** - Optimized for real-time chat  
✅ **Generous limits** - Perfect for development  
✅ **Easy setup** - Just need a Google account

## Security Note

- Keep your API key secure and never commit it to version control
- The `.env` file is already in `.gitignore` to protect your key
- If you accidentally expose your key, regenerate it immediately

## Testing Your Setup

Once you've added your API key:

1. Restart the Kiro application
2. Send a message that would trigger the LLM (like "What is artificial intelligence?")
3. You should see "✅ Google Gemini API initialized successfully" in the console
4. The bot will respond with AI-generated content instead of fallback responses

## Troubleshooting

**"Gemini API key not configured"**: Make sure you've added the key to `.env` and restarted the app

**"Failed to initialize Gemini API"**: Check that your API key is correct and you have internet connection

**Rate limit errors**: You've exceeded the free tier limits, wait a few minutes and try again
