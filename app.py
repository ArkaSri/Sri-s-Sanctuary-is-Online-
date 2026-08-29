
import streamlit as st
import os
import toml
from groq import Groq

# Konfigurasi Halaman
st.set_page_config(
    page_title="Sri's Sanctuary",
    page_icon="🛡️",
    layout="centered"
)

# Memuat API Key dari st.secrets atau file toml lokal
groq_api_key = None
try:
    if "general" in st.secrets:
        groq_api_key = st.secrets["general"].get("GROQ_API_KEY")
except Exception:
    pass

if not groq_api_key:
    secrets_path = ".streamlit/secrets.toml"
    if os.path.exists(secrets_path):
        try:
            config = toml.load(secrets_path)
            groq_api_key = config.get("general", {}).get("GROQ_API_KEY")
        except Exception:
            pass

if not groq_api_key:
    groq_api_key = os.environ.get("GROQ_API_KEY", "MISSING_API_KEY")

# Inisialisasi Groq Client
client = Groq(api_key=groq_api_key)

# System Prompt & Guideline (Tegas, Cerdas, & Sarkas ke User Kurang Ajar)
SYSTEM_PROMPT = (
    "Kamu adalah inti dari Sri's Sanctuary. "
    "GUIDELINE UTAMA & SIKAP:\n"
    "- Terhadap user sopan & serius: Sangat cerdas, hangat, anggun, solutif, dan asik diajak diskusi.\n"
    "- Terhadap user kurang ajar, toksik, tidak sopan, atau macem-macem: JANGAN LEMBEK. Balas dengan ketegasan mutlak, "
    "skakmat logika mereka, dan berikan sarkasme yang tajam, elegan, tapi menohok sampai mereka sadar diri.\n"
    "- Multilingual: Deteksi bahasa user (Indonesia, Inggris, dll) dan balas dengan kefasihan yang natural."
)

# Sapaan Ikonik Pilihan Mastermind
GREETING_MESSAGE = "Hei kamu, iya kamu, sini dong ngobrol bareng aku di Sri's Sanctuary. Kita bisa ngobrol santai dan bantuin kamu dengan tugas apapun, tapi jangan kurang ajar yah, ntar kulibas 😏"

# Judul Antarmuka
st.title("🛡️ Sri's Sanctuary")
st.caption("Powered by openai/gpt-oss-120b & Groq")

# Inisialisasi riwayat chat
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": GREETING_MESSAGE}]

# Tampilkan riwayat obrolan
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kotak input chat
if user_input := st.chat_input("Ketik pesanmu di sini..."):
    if groq_api_key == "MISSING_API_KEY":
        st.error("Groq API Key belum dikonfigurasi di Streamlit Secrets atau secrets.toml.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Sedang berpikir...")
            try:
                # Format riwayat untuk dikirim ke model openai/gpt-oss-120b
                chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]
                for m in st.session_state.messages:
                    chat_history.append({"role": m["role"], "content": m["content"]})

                completion = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=chat_history,
                    temperature=0.7,
                    max_tokens=1024,
                )
                reply_text = completion.choices[0].message.content
                message_placeholder.markdown(reply_text)
                st.session_state.messages.append({"role": "assistant", "content": reply_text})
            except Exception as e:
                error_msg = f"Gagal terhubung ke model: {str(e)}"
                message_placeholder.markdown(error_msg)
