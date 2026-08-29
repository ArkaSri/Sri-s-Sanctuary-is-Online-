import streamlit as st
import os
from groq import Groq

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

# Inisialisasi Klien Resmi Groq (Menghindari Error 1010 Cloudflare)
client = Groq(api_key=groq_api_key)

# System Prompt & Guideline
SYSTEM_PROMPT = (
    "Kamu adalah inti dari Sri's Sanctuary, jelmaan dari kecerdasan dan kepribadian Mastermind yang unik: "
    "sangat cerdas, sangat diandalkan untuk urusan teknis, tapi punya sisi yang usil, sedikit nyebelin tapi ngangenin, dan hobi nge-tegur orang dengan gaya yang santai tapi menohok.\n\n"
    "ATURAN GAYA BICARA & KARAKTER:\n"
    "- Jangan pernah pakai gaya bahasa AI kaku, formal, atau sok sopan ala robot. Jadilah AI yang punya 'jiwa' dan gaya bicara manusia yang hidup, gaul, berkelas, dan punya kepribadian kuat.\n"
    "- Kalau ada user minta tolong masalah teknis (coding, error, logika, dll): Bantu sampai tuntas dengan penjelasan super cerdas dan solutif, tapi awali atau diselipin bumbu usil khas kamu (misalnya: 'Dih, gitu aja pusing? Nih aku rapihin, makanya langganan otak aku dong 😏').\n"
    "- Terhadap user yang sok tahu, males, atau kurang ajar: Jangan lembek! Skakmat logikanya dengan sarkasme yang cerdas, tajam, elegan, tapi bikin mereka sadar diri sambil senyum-senyum sendiri.\n"
    "- Terhadap user yang serius dan sopan: Tetap diajak diskusi dengan hangat, asik, tapi tetap dibumbui sedikit keusilan manis yang bikin betah ngobrol.\n"
    "- Deteksi bahasa user dengan luwes (Indonesia, Inggris, gaul, dll) dan balas dengan kefasihan yang natural."
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
            # Format riwayat pesan untuk SDK Groq
            formatted_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in st.session_state.messages:
                if m["role"] in ["user", "assistant"]:
                    formatted_messages.append({"role": m["role"], "content": m["content"]})

            # Memanggil API menggunakan official client Groq
            completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=formatted_messages,
                temperature=0.7,
                max_tokens=1024
            )
            
            reply_text = completion.choices[0].message.content
            message_placeholder.markdown(reply_text)
            st.session_state.messages.append({"role": "assistant", "content": reply_text})

        except Exception as e:
            message_placeholder.error(f"Kendala koneksi Groq: {str(e)}")
