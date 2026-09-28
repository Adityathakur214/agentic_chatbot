import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000').rstrip('/')

st.set_page_config(
    page_title='Agentic Chatbot',
    page_icon='🤖',
    layout='centered',
)

GLASS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --glass-bg: rgba(255, 255, 255, 0.08);
    --glass-bg-strong: rgba(255, 255, 255, 0.14);
    --glass-border: rgba(255, 255, 255, 0.22);
    --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
    --accent-1: #7c5cff;
    --accent-2: #22d3ee;
    --accent-3: #ff5ecb;
}

html, body, [class*="css"], .stApp {
    font-family: 'Space Grotesk', sans-serif;
    color: #f1f3ff;
}

/* ---------- Animated aurora background ---------- */
.stApp {
    background: linear-gradient(135deg, #0b0d1f 0%, #150f33 45%, #0a1a2f 100%);
    background-attachment: fixed;
}
.stApp::before, .stApp::after {
    content: "";
    position: fixed;
    border-radius: 50%;
    filter: blur(90px);
    opacity: 0.55;
    z-index: 0;
    pointer-events: none;
}
.stApp::before {
    width: 480px; height: 480px;
    top: -120px; left: -120px;
    background: radial-gradient(circle, var(--accent-1), transparent 70%);
    animation: floatA 18s ease-in-out infinite alternate;
}
.stApp::after {
    width: 520px; height: 520px;
    bottom: -160px; right: -140px;
    background: radial-gradient(circle, var(--accent-3), transparent 70%);
    animation: floatB 22s ease-in-out infinite alternate;
}
@keyframes floatA {
    to { transform: translate(260px, 200px) scale(1.25); }
}
@keyframes floatB {
    to { transform: translate(-280px, -180px) scale(1.15); }
}

/* keep content above blobs */
[data-testid="stAppViewContainer"] > .main,
[data-testid="stMain"],
.block-container { position: relative; z-index: 1; }

[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }

.block-container { padding-top: 2.2rem; max-width: 780px; }

/* ---------- Title ---------- */
h1 {
    font-weight: 700 !important;
    letter-spacing: -0.02em;
    background: linear-gradient(90deg, var(--accent-2), var(--accent-1), var(--accent-3), var(--accent-2));
    background-size: 300% 100%;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 8s linear infinite;
    text-shadow: 0 0 40px rgba(124, 92, 255, 0.35);
}
@keyframes shimmer { to { background-position: 300% 0; } }

[data-testid="stCaptionContainer"] { color: rgba(241, 243, 255, 0.6); }

/* ---------- Glass chat bubbles ---------- */
[data-testid="stChatMessage"] {
    background: var(--glass-bg);
    backdrop-filter: blur(18px) saturate(160%);
    -webkit-backdrop-filter: blur(18px) saturate(160%);
    border: 1px solid var(--glass-border);
    border-radius: 22px;
    box-shadow: var(--glass-shadow), inset 0 1px 0 rgba(255, 255, 255, 0.25);
    padding: 1rem 1.2rem;
    margin-bottom: 0.9rem;
    animation: popIn 0.45s cubic-bezier(.2,.9,.3,1.2);
}
@keyframes popIn {
    from { opacity: 0; transform: translateY(14px) scale(0.97); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}
/* user bubble gets a tinted glass */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: linear-gradient(135deg, rgba(124, 92, 255, 0.28), rgba(34, 211, 238, 0.12));
    border-color: rgba(124, 92, 255, 0.45);
}
[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] {
    background: var(--glass-bg-strong);
    border: 1px solid var(--glass-border);
    box-shadow: 0 0 18px rgba(124, 92, 255, 0.5);
}

/* ---------- Chat input ---------- */
[data-testid="stBottom"], [data-testid="stBottom"] > div {
    background: transparent !important;
}
[data-testid="stChatInput"] {
    background: var(--glass-bg-strong);
    backdrop-filter: blur(22px);
    -webkit-backdrop-filter: blur(22px);
    border: 1px solid var(--glass-border);
    border-radius: 999px;
    box-shadow: var(--glass-shadow), 0 0 0 0 rgba(124, 92, 255, 0);
    transition: box-shadow 0.3s ease, border-color 0.3s ease;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--accent-2);
    box-shadow: var(--glass-shadow), 0 0 28px rgba(34, 211, 238, 0.45);
}
[data-testid="stChatInput"] textarea {
    color: #fff !important;
    background: transparent !important;
}
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, var(--accent-1), var(--accent-3)) !important;
    border-radius: 50% !important;
    color: #fff !important;
}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(26px);
    -webkit-backdrop-filter: blur(26px);
    border-right: 1px solid var(--glass-border);
}
[data-testid="stSidebar"] pre, [data-testid="stSidebar"] code {
    background: rgba(0, 0, 0, 0.3) !important;
    color: var(--accent-2) !important;
    border-radius: 12px;
}
[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    background: var(--glass-bg-strong);
    color: #fff;
    border: 1px solid var(--glass-border);
    border-radius: 14px;
    backdrop-filter: blur(10px);
    transition: all 0.25s ease;
}
[data-testid="stSidebar"] .stButton > button:hover {
    transform: translateY(-2px);
    border-color: var(--accent-3);
    box-shadow: 0 0 22px rgba(255, 94, 203, 0.45);
}

/* ---------- Custom components ---------- */
.glass-hero {
    text-align: center;
    padding: 2.2rem 1.5rem;
    margin: 1rem 0 1.4rem;
    background: var(--glass-bg);
    backdrop-filter: blur(20px) saturate(170%);
    -webkit-backdrop-filter: blur(20px) saturate(170%);
    border: 1px solid var(--glass-border);
    border-radius: 28px;
    box-shadow: var(--glass-shadow), inset 0 1px 0 rgba(255, 255, 255, 0.28);
}
.glass-hero .orb {
    width: 74px; height: 74px;
    margin: 0 auto 1rem;
    border-radius: 50%;
    background: radial-gradient(circle at 30% 30%, #fff 0%, var(--accent-2) 25%, var(--accent-1) 60%, var(--accent-3) 100%);
    box-shadow: 0 0 40px rgba(124, 92, 255, 0.8), inset -6px -8px 18px rgba(0, 0, 0, 0.35);
    animation: orb 4s ease-in-out infinite;
}
@keyframes orb {
    0%, 100% { transform: translateY(0) scale(1); }
    50%      { transform: translateY(-10px) scale(1.06); }
}
.glass-hero h3 { margin: 0 0 0.3rem; font-weight: 600; }
.glass-hero p  { margin: 0 0 1rem; color: rgba(241, 243, 255, 0.65); }

.chip {
    display: inline-block;
    margin: 4px 4px 0 0;
    padding: 6px 14px;
    font-size: 0.82rem;
    border-radius: 999px;
    background: var(--glass-bg-strong);
    border: 1px solid var(--glass-border);
    backdrop-filter: blur(8px);
}
.chip.tool {
    color: var(--accent-2);
    border-color: rgba(34, 211, 238, 0.5);
    box-shadow: 0 0 14px rgba(34, 211, 238, 0.25);
}

/* spinner + alerts */
[data-testid="stSpinner"] { color: var(--accent-2); }
[data-testid="stAlert"] {
    background: rgba(255, 80, 100, 0.15);
    border: 1px solid rgba(255, 80, 100, 0.4);
    border-radius: 16px;
    backdrop-filter: blur(12px);
}

/* scrollbar */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.2); border-radius: 8px; }
</style>
"""

st.markdown(GLASS_CSS, unsafe_allow_html=True)

st.title('🤖 Agentic Chatbot')
st.caption('Streamlit UI → FastAPI → LangGraph Agent → Tools → Response')

with st.sidebar:
    st.subheader('🔌 Backend')
    st.code(BACKEND_URL)
    st.subheader('🧰 Tools')
    st.markdown(
        '<span class="chip tool">🧮 calculator</span>'
        '<span class="chip tool">🕒 current time</span>'
        '<span class="chip tool">🌦️ weather</span>',
        unsafe_allow_html=True,
    )
    st.write('')
    if st.button('🧹 Clear chat'):
        st.session_state.messages = []
        st.rerun()

if 'messages' not in st.session_state:
    st.session_state.messages = []

# Empty-state hero card
if not st.session_state.messages:
    st.markdown(
        """
        <div class="glass-hero">
            <div class="orb"></div>
            <h3>Namaste! Kya poochna hai?</h3>
            <p>Main tools use karke jawab deta hoon — try karo:</p>
            <span class="chip">🧮 What is 245 * 18 + 7?</span>
            <span class="chip">🕒 What time is it now?</span>
            <span class="chip">🌦️ Weather in Indore?</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])
        if message.get('tools'):
            st.markdown(
                ''.join(f'<span class="chip tool">⚙️ {t}</span>' for t in message['tools']),
                unsafe_allow_html=True,
            )

prompt = st.chat_input('Ask something...')

if prompt:
    with st.chat_message('user'):
        st.markdown(prompt)

    # backend ko sirf role/content bhejna hai (tools key nahi)
    history = [
        {'role': m['role'], 'content': m['content']}
        for m in st.session_state.messages
    ]
    st.session_state.messages.append({'role': 'user', 'content': prompt})

    with st.chat_message('assistant'):
        with st.spinner('Agent is working...'):
            try:
                response = requests.post(
                    f'{BACKEND_URL}/chat',
                    json={'message': prompt, 'history': history},
                    timeout=120,
                )
                response.raise_for_status()
                data = response.json()
                answer = data['answer']
                tool_calls = data.get('tool_calls', [])

                st.markdown(answer)
                if tool_calls:
                    st.markdown(
                        ''.join(f'<span class="chip tool">⚙️ {t}</span>' for t in tool_calls),
                        unsafe_allow_html=True,
                    )

                st.session_state.messages.append(
                    {'role': 'assistant', 'content': answer, 'tools': tool_calls}
                )
            except requests.RequestException as exc:
                st.error(f'Backend connection failed: {exc}')
            except Exception as exc:
                st.error(f'Unexpected error: {exc}')