# Supabase and Google Auth Setup

1. Create a Supabase project.
2. Copy the project URL and anon key into `.env`. The URL should be the project root, not the REST endpoint, so it should not end with `/rest/v1`.

```env
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
APP_BASE_URL=http://localhost:8501
```

The app also accepts the browser-style names below, so you do not need to duplicate keys if you already added them:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project-ref.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

3. In Supabase, open Authentication > Providers > Google and enable Google.
4. Add the Google OAuth client ID and secret from Google Cloud Console.
5. Add your current Streamlit URL to the Supabase redirect URLs while developing. If Streamlit is running on `localhost:8502`, add `http://localhost:8502`.
6. Add your production app URL to redirect URLs before deploying.

Optional activity table:

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
