import json
import os
import random
import time
from datetime import datetime

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

UI_VERSION = 'v3.0 🎨'
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000').rstrip('/')

USER_AVATAR = '🧑‍💻'
BOT_AVATAR = '🤖'

# name -> (primary, secondary, accent, soft background)
THEMES = {
    '🌊 Ocean': ('#0ea5e9', '#6366f1', '#22d3ee', '#eef6ff'),
    '🌅 Sunset': ('#f97316', '#ec4899', '#facc15', '#fff5ee'),
    '🌿 Forest': ('#10b981', '#059669', '#a3e635', '#effcf5'),
    '🔮 Neon': ('#a855f7', '#ec4899', '#22d3ee', '#f7f0ff'),
    '🍬 Candy': ('#f43f5e', '#8b5cf6', '#fb923c', '#fff0f5'),
}

# tool name -> (icon, color)
TOOL_STYLES = {
    'calculator': ('🧮', '#f59e0b'),
    'current_time': ('🕒', '#3b82f6'),
    'get_current_time': ('🕒', '#3b82f6'),
    'time': ('🕒', '#3b82f6'),
    'weather': ('⛅', '#06b6d4'),
    'get_weather': ('⛅', '#06b6d4'),
}
DEFAULT_TOOL_STYLE = ('🔧', '#8b5cf6')

EXAMPLE_PROMPTS = [
    ('🧮', 'Calculator', 'What is (125 * 48) / 6 + 77?', '#f59e0b'),
    ('🕒', 'World clock', 'What is the current time in Tokyo?', '#3b82f6'),
    ('⛅', 'Weather', 'What is the weather in Indore right now?', '#06b6d4'),
    ('🔗', 'Multi-tool', 'What is the weather in Delhi and what time is it there?', '#ec4899'),
]

FOLLOW_UPS = {
    'calculator': ['Now divide that result by 7', 'Show it as a percentage of 1000'],
    'weather': ['What about tomorrow?', 'Should I carry an umbrella?'],
    'time': ['What time is it in London?', 'Convert that to IST'],
    'default': ['Explain how you got that', 'Try a different example'],
}

st.set_page_config(
    page_title='Agentic Chatbot',
    page_icon='🤖',
    layout='centered',
    initial_sidebar_state='expanded',
)


# ---------- State ----------
def init_state():
    defaults = {
        'messages': [],
        'pending_prompt': None,
        'failed_prompt': None,
        'backend_status': None,
        'toast': None,
        'balloons': False,
        'theme': '🌊 Ocean',
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()

# one-shot celebrations from the previous run
if st.session_state.toast:
    st.toast(st.session_state.toast, icon='✨')
    st.session_state.toast = None
if st.session_state.balloons:
    st.balloons()
    st.session_state.balloons = False


# ---------- Theme / CSS ----------
def inject_css(theme_name):
    primary, secondary, accent, soft = THEMES[theme_name]
    st.markdown(
        f"""
        <style>
            :root {{
                --primary: {primary};
                --secondary: {secondary};
                --accent: {accent};
                --soft: {soft};
            }}
            .block-container {{ padding-top: 1.5rem; max-width: 820px; }}

            /* Animated hero */
            .hero {{
                padding: 1.4rem 1.6rem;
                border-radius: 20px;
                background: linear-gradient(120deg, var(--primary), var(--secondary), var(--accent));
                background-size: 300% 300%;
                animation: gradientShift 10s ease infinite;
                color: white;
                box-shadow: 0 10px 30px rgba(0,0,0,0.18);
                margin-bottom: 1rem;
            }}
            .hero h1 {{ margin: 0; font-size: 2rem; color: white; }}
            .hero p {{ margin: 0.3rem 0 0; opacity: 0.92; font-size: 0.95rem; }}
            .flow {{
                display: flex; flex-wrap: wrap; gap: 6px; margin-top: 0.7rem;
            }}
            .flow span {{
                background: rgba(255,255,255,0.22);
                padding: 3px 12px; border-radius: 999px; font-size: 0.78rem;
                backdrop-filter: blur(4px);
            }}
            @keyframes gradientShift {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
            @keyframes fadeUp {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}

            /* Chat bubbles */
            div[data-testid="stChatMessage"] {{
                border-radius: 18px;
                padding: 0.9rem 1rem;
                margin-bottom: 0.7rem;
                animation: fadeUp 0.35s ease;
                border: 1px solid rgba(128,128,128,0.15);
            }}
            div[data-testid="stChatMessage"]:has(span[data-testid="stChatMessageAvatarUser"]) {{
                background: linear-gradient(135deg, var(--primary)22, var(--secondary)22);
                border-left: 5px solid var(--primary);
            }}
            div[data-testid="stChatMessage"]:has(span[data-testid="stChatMessageAvatarAssistant"]) {{
                background: linear-gradient(135deg, var(--accent)18, transparent);
                border-left: 5px solid var(--secondary);
            }}

            /* Tool badges */
            .tool-badge {{
                display: inline-block; padding: 3px 12px; margin: 4px 6px 2px 0;
                border-radius: 999px; font-size: 0.78rem; font-weight: 600; color: white;
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            }}
            .meta {{ font-size: 0.75rem; opacity: 0.65; margin-top: 6px; }}

            /* Buttons */
            .stButton > button, .stDownloadButton > button {{
                border-radius: 12px;
                border: 1px solid rgba(128,128,128,0.25);
                transition: all 0.18s ease;
            }}
            .stButton > button:hover, .stDownloadButton > button:hover {{
                transform: translateY(-2px) scale(1.02);
                border-color: var(--primary);
                color: var(--primary);
                box-shadow: 0 6px 16px rgba(0,0,0,0.15);
            }}

            /* Example cards */
            .ex-title {{ font-weight: 700; margin-bottom: 2px; }}

            /* Sidebar stat cards */
            .stat-card {{
                padding: 0.7rem 0.9rem; border-radius: 14px; color: white;
                margin-bottom: 0.5rem;
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }}
            .stat-card .num {{ font-size: 1.5rem; font-weight: 800; line-height: 1.1; }}
            .stat-card .lbl {{ font-size: 0.75rem; opacity: 0.9; }}

            /* Chat input focus glow */
            div[data-testid="stChatInput"] textarea:focus {{
                box-shadow: 0 0 0 2px var(--primary) !important;
            }}
            section[data-testid="stSidebar"] > div {{
                background: linear-gradient(180deg, var(--soft), transparent 60%);
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------- Helpers ----------
def check_backend():
    for path in ('/health', '/docs'):
        try:
            r = requests.get(f'{BACKEND_URL}{path}', timeout=5)
            if r.status_code < 500:
                return True, f'Online ({path} → {r.status_code})'
        except requests.RequestException:
            continue
    return False, 'Unreachable'


def call_backend(prompt, history, timeout):
    start = time.perf_counter()
    response = requests.post(
        f'{BACKEND_URL}/chat',
        json={'message': prompt, 'history': history},
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    return data, time.perf_counter() - start


def clean_history(messages):
    return [{'role': m['role'], 'content': m['content']} for m in messages]


def stream_text(text, delay=0.012):
    for word in text.split(' '):
        yield word + ' '
        time.sleep(delay)


def tool_badges_html(tool_calls):
    out = ''
    for t in tool_calls:
        icon, color = TOOL_STYLES.get(t, DEFAULT_TOOL_STYLE)
        out += f'<span class="tool-badge" style="background:{color}">{icon} {t}</span>'
    return out


def suggest_follow_ups(tool_calls):
    for t in tool_calls:
        for key in FOLLOW_UPS:
            if key in t.lower():
                return FOLLOW_UPS[key]
    return FOLLOW_UPS['default']


def stat_card(number, label):
    return (
        f'<div class="stat-card"><div class="num">{number}</div>'
        f'<div class="lbl">{label}</div></div>'
    )


def export_markdown(messages):
    lines = [f'# Chat export - {datetime.now():%Y-%m-%d %H:%M}\n']
    for m in messages:
        who = 'You' if m['role'] == 'user' else 'Assistant'
        lines.append(f'**{who}:** {m["content"]}\n')
        if m.get('tool_calls'):
            lines.append(f'_Tools used: {", ".join(m["tool_calls"])}_\n')
    return '\n'.join(lines)


def render_message(idx, message, show_tools=True, show_meta=True, interactive=True):
    avatar = USER_AVATAR if message['role'] == 'user' else BOT_AVATAR
    with st.chat_message(message['role'], avatar=avatar):
        st.markdown(message['content'])
        if message['role'] != 'assistant':
            return
        if show_tools and message.get('tool_calls'):
            st.markdown(tool_badges_html(message['tool_calls']), unsafe_allow_html=True)
        if show_meta and message.get('latency') is not None:
            st.markdown(
                f'<div class="meta">⏱ {message["latency"]:.2f}s · {message.get("ts", "")}</div>',
                unsafe_allow_html=True,
            )
        if interactive:
            fb = message.get('feedback')
            c1, c2, c3, _ = st.columns([1, 1, 1, 6])
            if c1.button('👍' if fb != 'up' else '💚', key=f'up_{idx}', help='Good answer'):
                message['feedback'] = None if fb == 'up' else 'up'
                st.session_state.toast = 'Thanks for the feedback!'
                st.rerun()
            if c2.button('👎' if fb != 'down' else '💔', key=f'down_{idx}', help='Bad answer'):
                message['feedback'] = None if fb == 'down' else 'down'
                st.session_state.toast = 'Feedback noted — we will do better.'
                st.rerun()
            with c3.popover('📋', help='Copy answer'):
                st.code(message['content'], language=None)


inject_css(st.session_state.theme)

# ---------- Sidebar ----------
with st.sidebar:
    st.header('🎛️ Control Panel')

    st.selectbox('🎨 Theme', list(THEMES.keys()), key='theme')

    st.subheader('🔌 Backend')
    st.code(BACKEND_URL)
    if st.button('Check connection', use_container_width=True):
        with st.spinner('Pinging backend...'):
            st.session_state.backend_status = check_backend()
    status = st.session_state.backend_status
    if status is not None:
        ok, msg = status
        (st.success if ok else st.error)(msg)

    st.divider()
    st.subheader('🧰 Settings')
    show_tools = st.toggle('Show tools used', value=True)
    show_meta = st.toggle('Show response time', value=True)
    typing_effect = st.toggle('Typing effect', value=True)
    show_followups = st.toggle('Suggest follow-ups', value=True)
    celebrate = st.toggle('Celebrate multi-tool answers 🎉', value=True)
    timeout = st.slider('Timeout (sec)', 10, 300, 120, step=10)

    st.divider()
    st.subheader('📊 Session')
    msgs = st.session_state.messages
    assistant_msgs = [m for m in msgs if m['role'] == 'assistant']
    tools_total = sum(len(m.get('tool_calls', [])) for m in assistant_msgs)
    latencies = [m['latency'] for m in assistant_msgs if m.get('latency') is not None]
    likes = sum(1 for m in assistant_msgs if m.get('feedback') == 'up')
    c1, c2 = st.columns(2)
    c1.markdown(stat_card(len(msgs), 'Messages'), unsafe_allow_html=True)
    c2.markdown(stat_card(tools_total, 'Tool calls'), unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    avg = f'{sum(latencies) / len(latencies):.1f}s' if latencies else '—'
    c3.markdown(stat_card(avg, 'Avg response'), unsafe_allow_html=True)
    c4.markdown(stat_card(f'{likes} 👍', 'Liked'), unsafe_allow_html=True)

    # tool usage breakdown
    usage = {}
    for m in assistant_msgs:
        for t in m.get('tool_calls', []):
            usage[t] = usage.get(t, 0) + 1
    if usage:
        st.caption('Tool usage')
        st.bar_chart(usage, height=140)

    st.divider()
    if msgs:
        st.download_button(
            '⬇️ Export Markdown',
            data=export_markdown(msgs),
            file_name='chat_export.md',
            mime='text/markdown',
            use_container_width=True,
        )
        st.download_button(
            '⬇️ Export JSON',
            data=json.dumps(msgs, indent=2),
            file_name='chat_export.json',
            mime='application/json',
            use_container_width=True,
        )
    if st.button('🗑️ Clear chat', use_container_width=True):
        st.session_state.messages = []
        st.session_state.failed_prompt = None
        st.session_state.toast = 'Chat cleared'
        st.rerun()

    st.caption(f'UI {UI_VERSION}')

# ---------- Hero ----------
st.markdown(
    """
    <div class="hero">
        <h1>🤖 Agentic Chatbot</h1>
        <p>An AI agent that reasons, picks the right tool, and answers — live.</p>
        <div class="flow">
            <span>🖥️ Streamlit UI</span><span>➜</span>
            <span>⚡ FastAPI</span><span>➜</span>
            <span>🧠 LangGraph Agent</span><span>➜</span>
            <span>🧰 Tools</span><span>➜</span>
            <span>💬 Response</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Empty state ----------
if not st.session_state.messages:
    st.markdown('#### 👋 Try one of these')
    cols = st.columns(2)
    for i, (icon, title, text, color) in enumerate(EXAMPLE_PROMPTS):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(
                    f'<div class="ex-title" style="color:{color}">{icon} {title}</div>',
                    unsafe_allow_html=True,
                )
                st.caption(text)
                if st.button('Try it', key=f'example_{i}', use_container_width=True):
                    st.session_state.pending_prompt = text
                    st.rerun()
    if st.button('🎲 Surprise me', use_container_width=True):
        st.session_state.pending_prompt = random.choice(EXAMPLE_PROMPTS)[2]
        st.rerun()

# ---------- History ----------
for i, message in enumerate(st.session_state.messages):
    is_last = i == len(st.session_state.messages) - 1
    render_message(i, message, show_tools, show_meta, interactive=True)

# ---------- Actions + follow-ups under last reply ----------
messages = st.session_state.messages
if messages and messages[-1]['role'] == 'assistant':
    last = messages[-1]

    if show_followups:
        st.caption('💡 Suggested follow-ups')
        fcols = st.columns(2)
        for j, text in enumerate(suggest_follow_ups(last.get('tool_calls', []))):
            if fcols[j % 2].button(text, key=f'follow_{j}', use_container_width=True):
                st.session_state.pending_prompt = text
                st.rerun()

    a, b, _ = st.columns([1.2, 1, 4])
    if a.button('🔄 Regenerate', key='regen'):
        messages.pop()
        last_user = messages.pop()
        st.session_state.pending_prompt = last_user['content']
        st.rerun()
    if b.button('↩️ Undo', key='undo'):
        messages.pop()
        messages.pop()
        st.session_state.toast = 'Last exchange removed'
        st.rerun()

# ---------- Retry ----------
if st.session_state.failed_prompt:
    st.warning('⚠️ The last request failed.')
    if st.button('🔁 Retry last message'):
        st.session_state.pending_prompt = st.session_state.failed_prompt
        st.session_state.failed_prompt = None
        st.rerun()

# ---------- Input ----------
typed_prompt = st.chat_input('Ask something... e.g. "weather in Pune and 15% of 2400"')
prompt = st.session_state.pending_prompt or typed_prompt
st.session_state.pending_prompt = None

if prompt:
    st.session_state.failed_prompt = None
    history = clean_history(st.session_state.messages)

    user_msg = {'role': 'user', 'content': prompt}
    st.session_state.messages.append(user_msg)
    render_message(len(st.session_state.messages) - 1, user_msg, interactive=False)

    with st.chat_message('assistant', avatar=BOT_AVATAR):
        try:
            with st.status('🧠 Agent is working...', expanded=True) as status_box:
                st.write('📨 Sending your message to the backend')
                st.write('🔍 Agent is reasoning and choosing tools')
                data, latency = call_backend(prompt, history, timeout)
                tool_calls = data.get('tool_calls', [])
                if tool_calls:
                    st.write('🧰 Tools used: ' + ', '.join(tool_calls))
                status_box.update(
                    label=f'✅ Done in {latency:.2f}s', state='complete', expanded=False
                )

            answer = data['answer']
            if typing_effect:
                st.write_stream(stream_text(answer))
            else:
                st.markdown(answer)

            ts = f'{datetime.now():%H:%M:%S}'
            st.session_state.messages.append(
                {
                    'role': 'assistant',
                    'content': answer,
                    'tool_calls': tool_calls,
                    'latency': latency,
                    'ts': ts,
                    'feedback': None,
                }
            )
            if celebrate and len(tool_calls) >= 2:
                st.session_state.balloons = True
                st.session_state.toast = 'Multi-tool answer! 🎉'
            st.rerun()

        except requests.Timeout:
            st.session_state.messages.pop()
            st.session_state.failed_prompt = prompt
            st.error(f'⏳ Timed out after {timeout}s. Retry or raise the timeout in the sidebar.')
        except requests.RequestException as exc:
            st.session_state.messages.pop()
            st.session_state.failed_prompt = prompt
            st.error(f'🔌 Backend connection failed: {exc}')
        except Exception as exc:
            st.session_state.messages.pop()
            st.session_state.failed_prompt = prompt
            st.error(f'💥 Unexpected error: {exc}')