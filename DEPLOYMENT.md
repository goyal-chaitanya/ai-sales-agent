# Deployment Notes

This project is currently a Streamlit application. It should not be deployed directly to Vercel as-is.

Why: Vercel's Python runtime is for serverless functions such as FastAPI, Flask, Django, or basic request handlers. Streamlit runs as a persistent interactive app server and relies on live browser-server communication, so a direct Vercel deploy is likely to fail or produce a non-working app.

Use one of these paths instead:

1. Streamlit Community Cloud
   - Push this folder to GitHub.
   - Create a new app at Streamlit Community Cloud.
   - Entrypoint: `app.py`.
   - Add the values from `.env` as app secrets/environment variables.

2. Render/Railway/Fly.io
   - Use `requirements.txt`.
   - Start command:

```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

3. Vercel
   - Rebuild the frontend as Next.js/React.
   - Keep Supabase auth in the frontend.
   - Move scraping, Groq, transcription, and ElevenLabs calls into API routes or a separate backend.

Before deploying anywhere, add the final hosted URL to Supabase Authentication > URL Configuration > Redirect URLs.
