import os
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlencode

import requests
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))


def _clean_supabase_url(value: str) -> str:
    url = value.strip().rstrip("/")
    for suffix in ("/rest/v1", "/auth/v1"):
        if url.endswith(suffix):
            return url[: -len(suffix)]
    return url


SUPABASE_URL = _clean_supabase_url(
    os.getenv("SUPABASE_URL")
    or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    or ""
)
SUPABASE_ANON_KEY = (
    os.getenv("SUPABASE_ANON_KEY")
    or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    or ""
).strip()
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8501")


def is_configured() -> bool:
    return bool(SUPABASE_URL and SUPABASE_ANON_KEY)


def configuration_status() -> dict[str, str]:
    return {
        "url": "configured" if SUPABASE_URL else "missing",
        "anon_key": "configured" if SUPABASE_ANON_KEY else "missing",
        "redirect_url": APP_BASE_URL,
    }


def _headers(access_token: str | None = None) -> dict[str, str]:
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {access_token or SUPABASE_ANON_KEY}",
        "Content-Type": "application/json",
    }
    return headers


def _request(method: str, path: str, access_token: str | None = None, **kwargs: Any) -> dict[str, Any]:
    if not is_configured():
        raise RuntimeError("Supabase is not configured.")

    response = requests.request(
        method,
        f"{SUPABASE_URL}{path}",
        headers=_headers(access_token),
        timeout=20,
        **kwargs,
    )

    if response.status_code >= 400:
        try:
            detail = response.json().get("msg") or response.json().get("error_description")
        except ValueError:
            detail = response.text
        raise RuntimeError(detail or f"Supabase request failed with {response.status_code}.")

    if not response.content:
        return {}
    return response.json()


def google_oauth_url(redirect_to: str | None = None) -> str:
    query = urlencode({"provider": "google", "redirect_to": redirect_to or APP_BASE_URL})
    return f"{SUPABASE_URL}/auth/v1/authorize?{query}"


def sign_in_with_password(email: str, password: str) -> dict[str, Any]:
    return _request(
        "POST",
        "/auth/v1/token?grant_type=password",
        json={"email": email, "password": password},
    )


def sign_up_with_password(email: str, password: str, redirect_to: str | None = None) -> dict[str, Any]:
    return _request(
        "POST",
        "/auth/v1/signup",
        json={
            "email": email,
            "password": password,
            "options": {"email_redirect_to": redirect_to or APP_BASE_URL},
        },
    )


def get_user(access_token: str) -> dict[str, Any]:
    return _request("GET", "/auth/v1/user", access_token=access_token)


def sign_out(access_token: str) -> None:
    _request("POST", "/auth/v1/logout", access_token=access_token)


def record_sales_session(
    access_token: str | None,
    user: dict[str, Any] | None,
    target_url: str,
    sales_brief: str,
) -> None:
    if not access_token or not user or not is_configured():
        return

    payload = {
        "user_id": user.get("id"),
        "target_url": target_url,
        "sales_brief": sales_brief,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        _request("POST", "/rest/v1/sales_agent_sessions", access_token=access_token, json=payload)
    except Exception:
        # The app should still be usable if the optional activity table is not installed yet.
        return
