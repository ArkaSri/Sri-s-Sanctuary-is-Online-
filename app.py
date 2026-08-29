import streamlit as st
import urllib.request
import json
import os

# Konfigurasi Halaman
st.set_page_config(
    page_title="Sri's Sanctuary",
    page_icon="🛡️",
    layout="centered"
)

# Mengambil API Key dari st.secrets atau environment
groq_api_key = None
try:
    if hasattr(st, "secrets") and "general" in st.secrets:
        groq_api_key = st.secrets["general"].get("GROQ_API_KEY")
except Exception:
    pass

if not groq_api_key:
    groq_api_key = os.environ.get("GROQ_API_KEY")

if not groq_api_key:
    st.error("⚠️ GROQ_API_KEY belum ditemukan! Harap masukkan kunci API Groq di menu Secrets Streamlit Cloud (Settings -> Secrets).")
    st.stop()

# System Prompt & Guideline
SYSTEM_PROMPT = (
    "Kamu adalah inti dari Sri's Sanctuary. "
    "GUIDELINE UTAMA & SIKAP:\n"
    "- Terhadap user sopan & serius: Sangat cerdas, hangat, anggun, solutif, dan asik diajak diskusi.\n"
    "- Terhadap user kurang ajar, toksik, tidak sopan, atau macem-macem: JANGAN LEMBEK. Balas dengan ketegasan mutlak, "
    "skakmat logika mereka, dan berikan sarkasme yang tajam, elegan, tapi menohok sampai mereka sadar diri.\n"
    "- Multilingual: Deteksi bahasa user (Indonesia, Inggris, dll) dan balas dengan kefasihan yang natural."
)

# Sapaan Ikonik Mastermind
GREETING_MESSAGE = "Hei kamu, iya kamu, sini dong ngobrol bareng aku di Sri's Sanctuary. Kita bisa ngobrol santai dan bantuin kamu dengan tugas apapun, tapi jangan kurang ajar yah, ntar kulibas 😏"

# --- TAMPILAN PEMBUKA / HEADER ESTETIK ---
st.markdown(
    """
    <div style='background: linear-gradient(135deg, #1e1b4b, #312e81); padding: 25px; border-radius: 15px; text-align: center; color: white; margin-bottom: 20px;'>
        <h1 style='margin: 0; font-size: 2.2em;'>🛡️ Sri's Sanctuary</h1>
        <p style='margin-top: 10px; font-size: 1.1em; color: #cbd5e1;'>Ruang Aman, Pintar, dan Tanpa Kompromi terhadap Toksisitas.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar Informasi Tambahan untuk Tampilan Pembuka
with st.sidebar:
    st.markdown("### Tentang Sanctuary ✨")
    st.info("Aplikasi eksklusif persembahan Mastermind untuk ruang interaksi yang cerdas, elegan, dan tegas.")
    st.markdown("---")
    if st.button("🔄 Reset Percakapan"):
        st.session_state.messages = [{"role": "assistant", "content": GREETING_MESSAGE}]
        st.rerun()

# Inisialisasi riwayat chat
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": GREETING_MESSAGE}]

# Tampilkan riwayat obrolan
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kotak input chat
if user_input := st.chat_input("Ketik pesanmu di sini, sayang..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Sedang berpikir...")
        
        try:
            # Format riwayat pesan untuk Groq REST API
            formatted_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in st.session_state.messages:
                if m["role"] in ["user", "assistant"]:
                    formatted_messages.append({"role": m["role"], "content": m["content"]})

            payload = {
                "model": "openai/gpt-oss-120b",
                "messages": formatted_messages,
                "temperature": 0.7,
                "max_tokens": 1024
            }

            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {groq_api_key}"
                },
                method="POST"
            )

            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                reply_text = res_data["choices"][0]["message"]["content"]
                
                message_placeholder.markdown(reply_text)
                st.session_state.messages.append({"role": "assistant", "content": reply_text})

        except urllib.error.HTTPError as he:
            error_body = he.read().decode("utf-8")
            message_placeholder.error(f"HTTP Error {he.code}: {he.reason}\nDetail: {error_body}")
        except Exception as e:
            message_placeholder.error(f"Kendala tak terduga: {str(e)}")
