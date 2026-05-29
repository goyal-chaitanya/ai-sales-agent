# SignalDesk Revenue OS

SignalDesk Revenue OS is an AI-powered outbound sales workspace built with Streamlit. It researches a target company from its website, generates a concise account brief, starts a consultative sales conversation, supports typed or microphone responses, and can speak the agent's replies with ElevenLabs text-to-speech.

The app is designed to feel like a complete revenue cockpit rather than a simple chatbot: it includes Supabase authentication, Google sign-in support, account setup controls, target intelligence, live conversation history, voice input, voice playback, and optional activity logging.

## Features

- Supabase authentication with Google OAuth and email/password support
- Polished Streamlit UI for an outbound sales workflow
- Website scraping for target-company research
- Groq-powered account brief generation
- LangChain conversation memory for an ongoing sales call
- Microphone input with Groq Whisper transcription
- ElevenLabs text-to-speech for assistant replies
- Preview mode for testing the app before signing in
- Optional Supabase table logging for generated account sessions

## Tech Stack

- Python
- Streamlit
- Supabase Auth
- Groq / OpenAI-compatible API
- LangChain
- ElevenLabs
- BeautifulSoup
- audio-recorder-streamlit

## Project Structure

```text
app.py                Main Streamlit application
app_config.py         Shared config/secrets loader
supabase_auth.py      Supabase Auth and optional session logging helpers
sales_brief.py        Website-to-sales-brief generation
scraper.py            Website text scraper
audio_processor.py    Microphone audio transcription
voice_generator.py    ElevenLabs text-to-speech
requirements.txt      Python dependencies
SUPABASE_SETUP.md     Supabase setup notes
DEPLOYMENT.md         Hosting notes
```

## Environment Variables

Create a `.env` file for local development, or add the same values to Streamlit Cloud Secrets when deployed.

```env
GROQ_API_KEY=your_groq_key
ELEVENLABS_API_KEY=your_elevenlabs_key
SERPER_API_KEY=your_serper_key

NEXT_PUBLIC_SUPABASE_URL=https://your-project-ref.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_or_publishable_key
APP_BASE_URL=http://localhost:8501
```

The app also accepts these Supabase names:

```env
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_or_publishable_key
```

Do not include `/rest/v1` at the end of the Supabase URL.

## Local Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add your `.env` file.

4. Run the app:

```bash
streamlit run app.py
```

5. Open the local Streamlit URL in your browser.

## Supabase Setup

1. Create a Supabase project.
2. Enable Google in Authentication > Providers.
3. Add your Google OAuth client ID and secret.
4. In Supabase Authentication > URL Configuration, add your local and deployed app URLs.

For local development:

```text
http://localhost:8501
```

For Streamlit Cloud:

```text
https://your-app-name.streamlit.app
```

In Google Cloud, the authorized redirect URI should be:

```text
https://your-project-ref.supabase.co/auth/v1/callback
```

## Optional Supabase Activity Table

If you want the app to store generated account sessions, create this table in Supabase:

```sql
create table if not exists public.sales_agent_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  target_url text not null,
  sales_brief text,
  status text default 'active',
  created_at timestamptz default now()
);

alter table public.sales_agent_sessions enable row level security;

create policy "Users can insert their own sessions"
on public.sales_agent_sessions
for insert
with check (auth.uid() = user_id);

create policy "Users can read their own sessions"
on public.sales_agent_sessions
for select
using (auth.uid() = user_id);
```

## Deployment

The recommended deployment target is Streamlit Community Cloud.

1. Push the project to GitHub.
2. Create a Streamlit app from the repository.
3. Set the entrypoint to `app.py`.
4. Add all secrets in Streamlit Cloud using TOML format:

```toml
GROQ_API_KEY = "your_groq_key"
ELEVENLABS_API_KEY = "your_elevenlabs_key"
SERPER_API_KEY = "your_serper_key"

NEXT_PUBLIC_SUPABASE_URL = "https://your-project-ref.supabase.co"
NEXT_PUBLIC_SUPABASE_ANON_KEY = "your_supabase_anon_or_publishable_key"
APP_BASE_URL = "https://your-app-name.streamlit.app"
```

5. Add the deployed URL to Supabase Auth redirect URLs.
6. Deploy or reboot the app.

## Troubleshooting

If the app says "Supabase setup pending", your deployed app cannot see the Supabase keys. Add them in Streamlit Cloud Secrets and redeploy.

If the agent does not speak, check that `ELEVENLABS_API_KEY` is configured. Some browsers block autoplay, so the app also shows an audio player under assistant messages.

If microphone input fails, make sure the browser has microphone permission and that `GROQ_API_KEY` is configured for transcription.

If Google sign-in does not redirect back to the app, confirm that both Supabase and Google Cloud have the correct redirect URLs.

## Security

Never commit `.env` or API keys. Rotate any keys that were accidentally shared in screenshots, logs, or public commits.
