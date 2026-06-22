"""
Streamlit Chatbot Frontend
Connects to the Azure Function App backend.
"""
 
import os
import random
import requests
import streamlit as st
 
### Config 
BACKEND_URL  = os.getenv("BACKEND_URL",  "http://localhost:7071/api")
FUNCTION_KEY = os.getenv("FUNCTION_KEY", "")
 
HEADERS = {
    "Content-Type": "application/json",
    **({"x-functions-key": FUNCTION_KEY} if FUNCTION_KEY else {}),
}

### User id
def _get_user_id() -> str:
    try:
        headers = st.context.headers
        aad_user = headers.get("X-Ms-Client-Principal-Name", "")
        if aad_user:
            return aad_user
    except AttributeError:
        pass
    return f'user_{random.randint(1, 3)}'

### page layout
st.set_page_config(
    page_title="Financial analyst",
    page_icon="🤖",
    layout="centered",
)
 
st.title("🤖 CC Financial Analyst")
st.caption("Powered by Thoughtworks · last K turns remembered per session")

### Session setup
user_id = _get_user_id()
if "session_id" not in st.session_state:
    st.session_state.session_id = user_id
 
session_id = st.session_state.session_id
if "messages" not in st.session_state:
    try:
        resp = requests.get(
            f"{BACKEND_URL}/session/{user_id}/history",
            headers=HEADERS,
            timeout=5,
        )
        resp.raise_for_status()
        st.session_state.messages = resp.json().get("messages", [])
        st.session_state.history_length = f'{len(st.session_state.messages)}'
    except requests.RequestException:
        st.session_state.messages = []
        st.session_state.history_length = "—"


if "window_k" not in st.session_state:
    st.session_state.window_k = "—"
if "history_length" not in st.session_state:
    st.session_state.history_length = "—"
 
 

with st.sidebar:
    st.header("Session info")
 
    # Show whether we identified the user via Easy Auth or anonymous UUID
    is_authenticated = "@" in user_id or "." in user_id  # crude heuristic
    id_label = "👤 Signed in as" if is_authenticated else "🔑 Anonymous ID"
    st.caption(id_label)
    st.code(user_id[:40] + ("…" if len(user_id) > 40 else ""), language=None)
 
    st.metric("LLM context window (K)", st.session_state.window_k)
    st.metric("Messages in DB", st.session_state.history_length)
 
    st.divider()
 
    if st.button("🗑️ Clear this conversation", use_container_width=True):
        try:
            requests.delete(
                f"{BACKEND_URL}/session/{session_id}",
                headers=HEADERS,
                timeout=5,
            )
        except requests.RequestException:
            pass
        st.session_state.messages = []
        st.session_state.history_length = 0
        st.rerun()
 
    st.divider()
    st.caption(
        "**Azure Web App**: set `BACKEND_URL` and `FUNCTION_KEY` in "
        "*Settings → Environment variables*.\n\n"
        "**Local dev**: export them as shell env vars or add to "
        "`.streamlit/secrets.toml`."
    )
 
# ── Chat display ──────────────────────────────────────────────────────────────
 
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
 
# ── Input ─────────────────────────────────────────────────────────────────────
 
if prompt := st.chat_input("Type a message…"):
 
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
 
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"session_id": session_id, "message": prompt},
                    headers=HEADERS,
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                reply = data["reply"]
                st.session_state.window_k      = data.get("window_k", "—")
                st.session_state.history_length = data.get("history_length", "—")
            except requests.exceptions.Timeout:
                reply = "⚠️ The backend took too long to respond. Please try again."
            except requests.exceptions.RequestException as exc:
                reply = f"⚠️ Could not reach the backend: {exc}"
 
        st.markdown(reply)
 
    st.session_state.messages.append({"role": "ai", "content": reply})
    st.rerun()
 