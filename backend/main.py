from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request
from openai import OpenAI
from dotenv import load_dotenv
import os

# Import additional router
from risk_score_api import router as risk_router

# Load OpenAI credentials
load_dotenv()
client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

# Initialize FastAPI
app = FastAPI()

# CORS config (for frontend compatibility)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific domains in production
    allow_methods=["*"],
    allow_headers=["*"],
)


# === Chat Endpoint ===
@app.post("/api/chat")
async def chat_with_ai(payload: dict):
    user_prompt = payload.get("prompt", "")
    if not user_prompt:
        return JSONResponse(status_code=400, content={"error": "Prompt is required."})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # or "gpt-4"
            messages=[
                {
                    "role": "system",
                    "content": 'You are a helpful policy assistant. If the user asks to compare countries, return a JSON list of those countries as: {"compare": ["CountryA", "CountryB"]} followed by your explanation.',
                },
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=300,
        )
        reply = response.choices[0].message.content
        return {"reply": reply}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# === Import the risk score API ===
app.include_router(risk_router, prefix="/api")
