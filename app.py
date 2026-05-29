import base64
import hashlib
import os
import tempfile

import streamlit as st
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.chains import LLMChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_groq import ChatGroq

import supabase_auth
from audio_processor import transcribe_audio
from audio_recorder_streamlit import audio_recorder
from sales_brief import generate_sales_brief
from voice_generator import text_to_speech_bytes

load_dotenv()

st.set_page_config(page_title="SignalDesk Revenue OS", page_icon="S", layout="wide")


APP_CSS = """
<style>
html, body, [class*="css"] {
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

#MainMenu, header, footer {visibility: hidden;}

.stApp {
    background:
        linear-gradient(135deg, rgba(35, 111, 121, 0.10), rgba(226, 91, 76, 0.08) 42%, rgba(45, 48, 71, 0.06)),
        #f7f8f6;
    color: #202124;
}

[data-testid="stSidebar"] {
    background: #111315 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.10);
}

[data-testid="stSidebar"] * {
    color: #f7f8f6;
}

[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] select {
    color: #101214 !important;
}

[data-testid="stSidebar"] .stButton > button {
    background: #1b2426 !important;
    border-color: rgba(255, 255, 255, 0.16) !important;
    color: #f7f8f6 !important;
}

[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #236f79 !important;
    border-color: #236f79 !important;
    color: #ffffff !important;
}

[data-testid="stSidebar"] div[data-baseweb="select"],
[data-testid="stSidebar"] div[data-baseweb="select"] *,
[data-testid="stSidebar"] input::placeholder {
    color: #1f2527 !important;
}

[data-testid="stSidebar"] input::placeholder {
    opacity: 0.62;
}

.block-container {
    padding-top: 1.35rem;
    padding-bottom: 3rem;
    max-width: 1440px;
}

.app-shell {
    border: 1px solid rgba(32, 33, 36, 0.10);
    background: rgba(255, 255, 255, 0.82);
    border-radius: 8px;
    padding: 18px 20px;
    box-shadow: 0 18px 50px rgba(28, 32, 36, 0.08);
}

.topbar {
    display: flex;
    justify-content: space-between;
    gap: 18px;
    align-items: flex-start;
}

.brand-mark {
    width: 38px;
    height: 38px;
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #153f44;
    color: #ffffff;
    font-weight: 800;
    margin-right: 12px;
}

.brand-row {
    display: flex;
    align-items: center;
}

.eyebrow {
    color: #6c756f;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0;
    text-transform: uppercase;
}

.headline {
    font-size: clamp(2.0rem, 4vw, 4.2rem);
    line-height: 0.95;
    font-weight: 850;
    letter-spacing: 0;
    margin: 18px 0 10px;
    max-width: 920px;
    color: #17191b;
}

.subhead {
    color: #53605a;
    max-width: 780px;
    font-size: 1.04rem;
    line-height: 1.55;
}

.status-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: flex-end;
}

.chip {
    border: 1px solid rgba(32, 33, 36, 0.12);
    border-radius: 999px;
    padding: 7px 10px;
    font-size: 0.78rem;
    font-weight: 700;
    background: #ffffff;
    color: #29302d;
}

.chip.good {border-color: rgba(35, 111, 121, 0.35); color: #153f44; background: #eaf5f3;}
.chip.warn {border-color: rgba(217, 151, 63, 0.35); color: #7d5112; background: #fff6e7;}
.chip.hot {border-color: rgba(226, 91, 76, 0.35); color: #8f2d25; background: #fff0ec;}

.metric-card, .panel, .brief-card, .login-card {
    border: 1px solid rgba(32, 33, 36, 0.10);
    background: rgba(255, 255, 255, 0.88);
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 14px 34px rgba(28, 32, 36, 0.07);
}

.metric-value {
    font-size: 2.0rem;
    font-weight: 850;
    color: #17191b;
    line-height: 1;
}

.metric-label {
    margin-top: 8px;
    color: #68736d;
    font-size: 0.86rem;
    font-weight: 650;
}

.section-title {
    color: #17191b;
    font-weight: 800;
    font-size: 1.02rem;
    margin-bottom: 8px;
}

.muted {
    color: #69746e;
    font-size: 0.92rem;
    line-height: 1.45;
}

.brief-card {
    white-space: pre-wrap;
    border-left: 4px solid #236f79;
}

.pipeline-row {
    display: grid;
    grid-template-columns: 1.2fr 0.7fr 0.7fr;
    gap: 10px;
    padding: 10px 0;
    border-bottom: 1px solid rgba(32, 33, 36, 0.08);
}

.pipeline-row:last-child {border-bottom: 0;}
.pipeline-row strong {color: #17191b;}
.pipeline-row span {color: #69746e;}

.stButton > button, .stLinkButton > a {
    border-radius: 8px !important;
    border: 1px solid rgba(32, 33, 36, 0.12) !important;
    background: #153f44 !important;
    color: #ffffff !important;
    font-weight: 750 !important;
    min-height: 42px;
    transition: transform 150ms ease, box-shadow 150ms ease;
}

.stButton > button:hover, .stLinkButton > a:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 22px rgba(21, 63, 68, 0.18);
}

button[kind="secondary"] {
    background: #ffffff !important;
    color: #202124 !important;
}

.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
    border-radius: 8px !important;
}

[data-testid="stChatMessage"] {
    border-radius: 8px;
    border: 1px solid rgba(32, 33, 36, 0.10);
    background: rgba(255, 255, 255, 0.82);
    padding: 12px;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: #eef7f5;
    border-color: rgba(35, 111, 121, 0.22);
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: #fff7f1;
    border-color: rgba(217, 151, 63, 0.24);
}

.divider {
    height: 1px;
    background: rgba(32, 33, 36, 0.10);
    margin: 18px 0;
}

@media (max-width: 760px) {
    .topbar {
        display: block;
    }
    .status-row {
        justify-content: flex-start;
        margin-top: 14px;
    }
    .headline {
        font-size: 2.25rem;
    }
    .pipeline-row {
        grid-template-columns: 1fr;
    }
}
</style>
"""


def first_query_value(name: str) -> str | None:
    value = st.query_params.get(name)
    if isinstance(value, list):
        return value[0] if value else None
    return value


def current_app_url() -> str:
    try:
        url = str(st.context.url)
        if url and url != "None":
            return url.split("?")[0].split("#")[0].rstrip("/")
    except Exception:
        pass
    return supabase_auth.APP_BASE_URL


def capture_oauth_fragment() -> None:
    st.html(
        """
        <script>
        (function () {
            try {
                const currentUrl = new URL(window.location.href);
                if (!currentUrl.hash || !currentUrl.hash.includes("access_token")) return;
                const hashParams = new URLSearchParams(currentUrl.hash.slice(1));
                const queryParams = currentUrl.searchParams;
                ["access_token", "refresh_token", "expires_at", "expires_in", "token_type"].forEach((key) => {
                    const value = hashParams.get(key);
                    if (value) queryParams.set("auth_" + key, value);
                });
                queryParams.set("auth_provider", "google");
                currentUrl.hash = "";
                window.location.replace(currentUrl.toString());
            } catch (error) {
                console.warn("OAuth handoff failed", error);
            }
        })();
        </script>
        """,
        unsafe_allow_javascript=True,
    )


def initialize_state() -> None:
    defaults = {
        "sales_brief": None,
        "conversation": None,
        "messages": [],
        "last_audio_hash": None,
        "final_input": None,
        "auth_session": None,
        "auth_user": None,
        "preview_mode": False,
        "sessions_created": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def sync_auth_from_query() -> None:
    token = first_query_value("auth_access_token")
    refresh_token = first_query_value("auth_refresh_token")
    if not token or not supabase_auth.is_configured():
        return

    try:
        user = supabase_auth.get_user(token)
        st.session_state.auth_session = {
            "access_token": token,
            "refresh_token": refresh_token,
            "provider": first_query_value("auth_provider") or "google",
        }
        st.session_state.auth_user = user
        st.session_state.preview_mode = False
        st.query_params.clear()
        st.rerun()
    except Exception as exc:
        st.error(f"Could not complete Google sign-in: {exc}")


def current_access_token() -> str | None:
    session = st.session_state.get("auth_session") or {}
    return session.get("access_token")


def current_user_label() -> str:
    user = st.session_state.get("auth_user") or {}
    email = user.get("email") or user.get("user_metadata", {}).get("email")
    return email or "Workspace user"


def configured_chip() -> str:
    if supabase_auth.is_configured():
        return '<span class="chip good">Supabase configured</span>'
    return '<span class="chip warn">Supabase setup pending</span>'


def render_setup_hint() -> None:
    status = supabase_auth.configuration_status()
    missing = [
        label
        for key, label in [
            ("url", "Supabase URL"),
            ("anon_key", "Supabase anon key"),
        ]
        if status[key] != "configured"
    ]
    if missing:
        st.warning(
            "Missing app config: "
            + ", ".join(missing)
            + ". The app accepts SUPABASE_URL/SUPABASE_ANON_KEY or NEXT_PUBLIC_SUPABASE_URL/NEXT_PUBLIC_SUPABASE_ANON_KEY."
        )
        return

    st.info(
        "Supabase keys are loaded. If Google sign-in fails, add "
        f"{current_app_url()} to Supabase Authentication > URL Configuration > Redirect URLs."
    )


def auth_chip() -> str:
    if st.session_state.get("auth_user"):
        return '<span class="chip good">Authenticated</span>'
    if st.session_state.get("preview_mode"):
        return '<span class="chip warn">Preview mode</span>'
    return '<span class="chip hot">Sign-in required</span>'


def render_login() -> None:
    st.markdown(APP_CSS, unsafe_allow_html=True)
    capture_oauth_fragment()
    sync_auth_from_query()

    st.markdown(
        f"""
        <div class="app-shell">
            <div class="topbar">
                <div>
                    <div class="brand-row">
                        <span class="brand-mark">S</span>
                        <div>
                            <div class="eyebrow">SignalDesk Revenue OS</div>
                            <strong>Secure workspace</strong>
                        </div>
                    </div>
                    <div class="headline">A sharper cockpit for outbound intelligence.</div>
                    <div class="subhead">
                        Account research, pitch generation, voice responses, and authenticated workspace activity in one focused operating surface.
                    </div>
                </div>
                <div class="status-row">
                    {configured_chip()}
                    {auth_chip()}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        st.markdown(
            """
            <div class="login-card">
                <div class="section-title">Workspace access</div>
                <div class="muted">Use Google through Supabase, or email/password if it is enabled in your Supabase Auth providers.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if supabase_auth.is_configured():
            st.link_button(
                "Continue with Google",
                supabase_auth.google_oauth_url(current_app_url()),
                use_container_width=True,
            )
            tab_signin, tab_signup = st.tabs(["Sign in", "Create account"])

            with tab_signin:
                with st.form("signin_form"):
                    email = st.text_input("Email", autocomplete="email")
                    password = st.text_input("Password", type="password")
                    submitted = st.form_submit_button("Sign in", use_container_width=True)
                if submitted:
                    try:
                        session = supabase_auth.sign_in_with_password(email, password)
                        st.session_state.auth_session = session
                        st.session_state.auth_user = session.get("user")
                        st.session_state.preview_mode = False
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Sign-in failed: {exc}")

            with tab_signup:
                with st.form("signup_form"):
                    new_email = st.text_input("Work email", autocomplete="email")
                    new_password = st.text_input("Create password", type="password")
                    created = st.form_submit_button("Create account", use_container_width=True)
                if created:
                    try:
                        session = supabase_auth.sign_up_with_password(new_email, new_password, current_app_url())
                        st.session_state.auth_session = session if session.get("access_token") else None
                        st.session_state.auth_user = session.get("user")
                        st.success("Account created. Check your inbox if email confirmation is enabled.")
                    except Exception as exc:
                        st.error(f"Account creation failed: {exc}")
        else:
            render_setup_hint()

        if st.button("Open preview workspace", use_container_width=True):
            st.session_state.preview_mode = True
            st.rerun()

    with right:
        st.markdown(
            """
            <div class="panel">
                <div class="section-title">Live workspace snapshot</div>
                <div class="pipeline-row"><strong>Target intelligence</strong><span>Ready</span><span>Website research</span></div>
                <div class="pipeline-row"><strong>Voice call loop</strong><span>Ready</span><span>Text and mic input</span></div>
                <div class="pipeline-row"><strong>Activity storage</strong><span>Optional</span><span>Supabase table</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def require_access() -> bool:
    return bool(st.session_state.get("auth_user") or st.session_state.get("preview_mode"))


def autoplay_audio(audio_bytes: bytes) -> None:
    encoded = base64.b64encode(audio_bytes).decode()
    st.markdown(
        f"""
        <audio autoplay="true" style="display:none;">
            <source src="data:audio/mp3;base64,{encoded}" type="audio/mp3">
        </audio>
        """,
        unsafe_allow_html=True,
    )


def build_conversation(brief: str, segment: str, offer: str, tone: str) -> LLMChain:
    llm = ChatGroq(temperature=0.72, model_name="llama-3.1-8b-instant")
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a senior revenue operator for CBG Consultancy Services. "
                "You are speaking with a prospect after researching their company. "
                f"Target segment: {segment}. Offer motion: {offer}. Conversation tone: {tone}. "
                "Use the account profile below to make every response specific and useful.\n\n"
                f"{brief}\n\n"
                "Pitch CBG's AI automation services only when it fits the prospect's likely bottlenecks. "
                "Keep replies natural, consultative, and concise. Ask one strong question when the prospect gives limited detail.",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{user_input}"),
        ]
    )
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    return LLMChain(llm=llm, prompt=prompt, memory=memory)


def process_text_input() -> None:
    if st.session_state.user_text_input:
        st.session_state.final_input = st.session_state.user_text_input
        st.session_state.user_text_input = ""


def reset_workspace() -> None:
    st.session_state.sales_brief = None
    st.session_state.conversation = None
    st.session_state.messages = []
    st.session_state.final_input = None
    st.session_state.last_audio_hash = None


def handle_sign_out() -> None:
    token = current_access_token()
    if token and supabase_auth.is_configured():
        try:
            supabase_auth.sign_out(token)
        except Exception:
            pass
    st.session_state.auth_session = None
    st.session_state.auth_user = None
    st.session_state.preview_mode = False
    reset_workspace()
    st.rerun()


def render_sidebar() -> tuple[str, str, str, str]:
    with st.sidebar:
        st.markdown("### SignalDesk")
        st.caption(current_user_label() if st.session_state.get("auth_user") else "Preview workspace")

        if st.button("Sign out", use_container_width=True):
            handle_sign_out()

        st.divider()
        st.markdown("#### Account setup")
        target_url = st.text_input("Company URL", placeholder="https://stripe.com")
        segment = st.selectbox(
            "Target segment",
            ["B2B SaaS", "Services firm", "Marketplace", "Healthcare", "Financial services", "Ecommerce"],
        )
        offer = st.selectbox(
            "Offer motion",
            ["AI workflow automation", "Lead qualification", "Customer support automation", "Ops analytics", "Custom agent build"],
        )
        tone = st.select_slider(
            "Conversation tone",
            options=["Direct", "Consultative", "Warm", "Executive"],
            value="Consultative",
        )

        build_clicked = st.button("Build account workspace", type="primary", use_container_width=True)
        if build_clicked:
            if not target_url:
                st.error("Enter a company URL first.")
            else:
                with st.spinner("Researching account and drafting opening line..."):
                    brief = generate_sales_brief(target_url)
                    st.session_state.sales_brief = brief
                    st.session_state.conversation = build_conversation(brief, segment, offer, tone)
                    st.session_state.messages = []
                    opening_line = st.session_state.conversation.predict(user_input="Hello?")
                    opening_audio = text_to_speech_bytes(opening_line)
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": opening_line,
                            "audio": opening_audio,
                            "autoplay": True,
                        }
                    )
                    supabase_auth.record_sales_session(
                        current_access_token(),
                        st.session_state.get("auth_user"),
                        target_url,
                        brief,
                    )
                    st.session_state.sessions_created += 1
                    st.rerun()

        st.divider()
        if st.button("Reset workspace", use_container_width=True):
            reset_workspace()
            st.rerun()

        st.caption("Supabase stores activity when the optional table is installed.")

    return target_url, segment, offer, tone


def render_header() -> None:
    st.markdown(
        f"""
        <div class="app-shell">
            <div class="topbar">
                <div>
                    <div class="brand-row">
                        <span class="brand-mark">S</span>
                        <div>
                            <div class="eyebrow">SignalDesk Revenue OS</div>
                            <strong>{current_user_label()}</strong>
                        </div>
                    </div>
                    <div class="headline">Research, pitch, and run the conversation from one desk.</div>
                    <div class="subhead">
                        A polished outbound workspace with target intelligence, authenticated sessions, voice interaction, and live talk-track generation.
                    </div>
                </div>
                <div class="status-row">
                    {configured_chip()}
                    {auth_chip()}
                    <span class="chip good">Voice enabled</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metrics() -> None:
    has_brief = bool(st.session_state.get("sales_brief"))
    has_call = bool(st.session_state.get("conversation"))
    auth_status = "Live" if st.session_state.get("auth_user") else "Preview"
    metric_data = [
        ("Account plans", str(st.session_state.sessions_created), "Saved this session"),
        ("Readiness", "92%" if has_brief else "18%", "Brief and talk track"),
        ("Call state", "Active" if has_call else "Standby", "Voice loop"),
        ("Auth", auth_status, "Supabase workspace"),
    ]
    cols = st.columns(4)
    for col, (value_label, value, label) in zip(cols, metric_data):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="eyebrow">{value_label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_empty_state() -> None:
    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        st.markdown(
            """
            <div class="panel">
                <div class="section-title">Pipeline command center</div>
                <div class="pipeline-row"><strong>Stripe</strong><span>Expansion ops</span><span>Automation angle</span></div>
                <div class="pipeline-row"><strong>Notion</strong><span>Team workflows</span><span>Qualification angle</span></div>
                <div class="pipeline-row"><strong>Ramp</strong><span>Finance ops</span><span>Back-office angle</span></div>
                <div class="pipeline-row"><strong>Vercel</strong><span>Developer platform</span><span>Support angle</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            """
            <div class="panel">
                <div class="section-title">Workspace state</div>
                <div class="muted">Choose a company URL in the sidebar to create an account brief and begin a live AI-assisted conversation.</div>
                <div class="divider"></div>
                <div class="pipeline-row"><strong>Research</strong><span>Waiting</span><span>Website scrape</span></div>
                <div class="pipeline-row"><strong>Brief</strong><span>Waiting</span><span>3-point summary</span></div>
                <div class="pipeline-row"><strong>Call</strong><span>Waiting</span><span>Voice response</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_brief_and_chat() -> None:
    brief_col, chat_col = st.columns([0.88, 1.12], gap="large")

    with brief_col:
        st.markdown('<div class="section-title">Target intelligence brief</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="brief-card">{st.session_state.sales_brief}</div>', unsafe_allow_html=True)

        st.write("")
        st.markdown(
            """
            <div class="panel">
                <div class="section-title">Deal posture</div>
                <div class="pipeline-row"><strong>Opening</strong><span>Specific</span><span>Company context</span></div>
                <div class="pipeline-row"><strong>Questioning</strong><span>Consultative</span><span>Bottleneck led</span></div>
                <div class="pipeline-row"><strong>Next step</strong><span>Demo path</span><span>Automation audit</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with chat_col:
        st.markdown('<div class="section-title">Live conversation</div>', unsafe_allow_html=True)
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    if msg.get("audio") and msg.get("autoplay"):
                        autoplay_audio(msg["audio"])
                        msg["autoplay"] = False

        input_col, mic_col = st.columns([5, 1])
        with input_col:
            st.text_input(
                "Response",
                key="user_text_input",
                on_change=process_text_input,
                label_visibility="collapsed",
                placeholder="Type a prospect reply and press Enter...",
            )
        with mic_col:
            audio_bytes = audio_recorder(text="", icon_size="2x")

        if audio_bytes:
            audio_hash = hashlib.sha256(audio_bytes).hexdigest()
            if audio_hash != st.session_state.last_audio_hash:
                st.session_state.last_audio_hash = audio_hash
                if len(audio_bytes) > 5000:
                    with st.spinner("Transcribing voice input..."):
                        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                            temp_file.write(audio_bytes)
                            temp_path = temp_file.name
                        try:
                            transcript = transcribe_audio(temp_path)
                        finally:
                            if os.path.exists(temp_path):
                                os.remove(temp_path)

                    if transcript.startswith("Transcription Error"):
                        st.error(f"Voice error: {transcript}")
                    else:
                        st.session_state.final_input = transcript

        if st.session_state.final_input:
            user_msg = st.session_state.final_input
            st.session_state.final_input = None
            st.session_state.messages.append({"role": "user", "content": user_msg})

            with st.spinner("Drafting response..."):
                response = st.session_state.conversation.predict(user_input=user_msg)
                audio = text_to_speech_bytes(response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response, "audio": audio, "autoplay": True}
                )
            st.rerun()


def render_app() -> None:
    st.markdown(APP_CSS, unsafe_allow_html=True)
    capture_oauth_fragment()
    sync_auth_from_query()
    render_sidebar()
    render_header()
    st.write("")
    render_metrics()
    st.write("")

    if st.session_state.get("conversation"):
        render_brief_and_chat()
    else:
        render_empty_state()


initialize_state()

if require_access():
    render_app()
else:
    render_login()
