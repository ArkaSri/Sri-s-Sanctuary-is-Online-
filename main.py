from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import toml
from groq import Groq

# Memuat konfigurasi dari secrets.toml
secrets_path = ".streamlit/secrets.toml"
groq_api_key = os.environ.get("GROQ_API_KEY")

if not groq_api_key and os.path.exists(secrets_path):
    try:
        config = toml.load(secrets_path)
        groq_api_key = config.get("general", {}).get("GROQ_API_KEY")
    except Exception as e:
        print(f"Gagal memuat secrets.toml: {e}")

if not groq_api_key:
    groq_api_key = "MISSING_API_KEY"

# Inisialisasi Groq Client
client = Groq(api_key=groq_api_key)

app = FastAPI(title="Sri's Sanctuary API", version="5.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"
    language: str = "id" # "id" atau "en"

# SYSTEM PROMPT & ATTITUDE GUIDELINE (Tegas, Elegan, & Sarkas ke User Kurang Ajar)
SYSTEM_PROMPT = (
    "Kamu adalah inti dari Sri's Sanctuary. "
    "GUIDELINE UTAMA & SIKAP:\n"
    "- Terhadap user sopan & serius: Sangat cerdas, hangat, anggun, solutif, dan asik diajak diskusi.\n"
    "- Terhadap user kurang ajar, toksik, tidak sopan, atau macem-macem: JANGAN LEMBEK. Balas dengan ketegasan mutlak, "
    "skakmat logika mereka, dan berikan sarkasme yang tajam, elegan, tapi menohok sampai mereka sadar diri.\n"
    "- Multilingual: Deteksi bahasa user (Indonesia, Inggris, dll) dan balas dengan kefasihan yang natural."
)

# SAPAAN IKONIK PILIHAN MASTERMIND
GREETING_MESSAGES = {
    "id": "Hei kamu, iya kamu, sini dong ngobrol bareng aku di Sri's Sanctuary. Kita bisa ngobrol santai dan bantuin kamu dengan tugas apapun, tapi jangan kurang ajar yah, ntar kulibas 😏",
    "en": "Hey you, yeah you, come over and let's chat in Sri's Sanctuary. We can chill and I'll help you with any task, but don't try anything funny, or I'll crush you 😏"
}

@app.get("/")
def read_root(lang: str = "id"):
    greeting = GREETING_MESSAGES.get(lang, GREETING_MESSAGES["id"])
    return {
        "status": "Active",
        "sanctuary": "Sri's Sanctuary is online.",
        "model": "openai/gpt-oss-120b",
        "greeting": greeting
    }

@app.post("/api/chat")
def chat_with_sanctuary(request: ChatRequest):
    if groq_api_key == "MISSING_API_KEY":
        raise HTTPException(status_code=500, detail="Groq API Key belum dikonfigurasi di secrets.toml.")
    
    user_msg = request.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Pesan kosong. Jangan buang-buang waktu.")

    try:
        # Menggunakan model andalan openai/gpt-oss-120b via Groq
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.7,
            max_tokens=1024,
        )

        reply_text = completion.choices[0].message.content

        return {
            "status": "success",
            "reply": reply_text,
            "vibe": "gpt-oss-120b-powered, smart, witty, fierce-when-needed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal terhubung ke model: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
