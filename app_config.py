import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))


def secret_value(*names: str) -> str:
    for name in names:
        value = os.getenv(name)
        if value:
            return value

    try:
        import streamlit as st

        for name in names:
            value = st.secrets.get(name)
            if value:
                return str(value)
    except Exception:
        pass

    return ""


def clean_supabase_url(value: str) -> str:
    url = value.strip().rstrip("/")
    for suffix in ("/rest/v1", "/auth/v1"):
        if url.endswith(suffix):
            return url[: -len(suffix)]
    return url
