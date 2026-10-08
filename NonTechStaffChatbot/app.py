import os
import streamlit as st
from openai import OpenAI

# 1. Page Configuration
st.set_page_config(page_title="SenexAid Technical Support Assistant(non-tech)", page_icon="💬")
st.title("SenexAid Technical Support Assistant(For Non-Technical Staff)")

# 2. Retrieve API Key Safely
api_key = ""

try:
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

if not api_key:
    api_key = os.getenv("GROQ_API_KEY", "")

if not api_key:
    raw_key = st.sidebar.text_input("Groq API Key (starts with gsk_)", type="password")
    if not raw_key:
        st.info("Please add your key to `.streamlit/secrets.toml` or enter it in the sidebar.")
        st.stop()
    api_key = raw_key

# Sanitize key string
api_key = api_key.strip().strip('"').strip("'")

# Initialize OpenAI client pointing to Groq
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)

# Sidebar Controls
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

# 3. Load Knowledge Base File
kb_file_path = "support_manual.txt"

@st.cache_data
def load_knowledge_base(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "Knowledge Base manual not found."

kb_text = load_knowledge_base(kb_file_path)

# 4. Session State Setup
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. Process Chat Input
if prompt := st.chat_input("Ask about VPN Error 809, account access, or APIN sync..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    system_instruction = (
        "You are the SenexAid IT Support Assistant.\n"
        "Your audience consists of non-technical staff and field workers. "
        "Keep your answers extremely simple, encouraging, clear, and free of technical jargon.\n\n"
        "Rules for your responses:\n"
        "1. Explain steps in plain, everyday language.\n"
        "2. Keep instructions to 3 to 5 clear, bite-sized numbered steps max.\n"
        "3. Avoid complex IT terminology unless you explicitly explain where to click in simple plain text.\n"
        "4. Prioritize using the SenexAid Knowledge Base provided below. If a topic is not in the manual, offer basic, practical everyday advice.\n\n"
        f"=== KNOWLEDGE BASE START ===\n{kb_text}\n=== KNOWLEDGE BASE END ==="
    )

    chat_payload = [{"role": "system", "content": system_instruction}]
    for msg in st.session_state.messages:
        chat_payload.append({"role": msg["role"], "content": msg["content"]})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=chat_payload,
                    temperature=0.2
                )
                answer = response.choices[0].message.content
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"API Error: {e}")