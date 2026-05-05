from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from twilio.rest import Client
import os
from telegram import Bot

app = FastAPI()

# Enable CORS so your frontend can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Update this to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Twilio Credentials (Replace with your actual credentials or load from environment variables)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "AC_your_account_sid")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "your_auth_token")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886") # Twilio Sandbox number

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

class Medication(BaseModel):
    medicine: str
    frequency: int
    time: str

class HealthData(BaseModel):
    symptoms: str
    allergies: str
    whatsapp: str
    emergency: str
    medications: List[Medication]

# Telegram Credentials
TELEGRAM_TOKEN = "8795699927:AAEzz3a8ZZwx6YNiSr0Q5ppWXHI_HYB4v2Q"
# Note: You need the user's Chat ID. For testing, you can find yours via @userinfobot
TELEGRAM_CHAT_ID = "1531807887" 

telegram_bot = Bot(token=TELEGRAM_TOKEN)

@app.post("/api/activate-bot")
async def activate_bot(data: HealthData):
    try:
        # 1. Search logic (already in your code)
        user_symptoms = data.symptoms.lower()
        match = next((item for item in medical_db if any(s in user_symptoms for s in item['symptoms'])), None)
        
        diagnosis_info = ""
        if match:
            diagnosis_info = f"\n*Suggested Identification:* {match['label']}\n*Recommended Treatment:* {match['med']}\n"

        # 2. Format the message
        meds_summary = "\n".join([f"- {m.medicine} ({m.frequency}x/day at {m.time})" for m in data.medications])
        
        message_body = (
            f"🚨 HealthBot Activated! 🚨\n"
            f"{diagnosis_info}\n"
            f"Patient Allergies: {data.allergies}\n"
            f"Current Schedule:\n{meds_summary}\n\n"
            f"Reminders scheduled via WhatsApp and Telegram."
        )

        # 4. Send Telegram Message
        # Telegram sends messages asynchronously
        await telegram_bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message_body, parse_mode='Markdown')

        return {"status": "success", "diagnosis": match['label'] if match else "None"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        # Send via Twilio WhatsApp API
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:+{data.whatsapp}"
        )

        return {"status": "success", "message_id": message.sid}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send WhatsApp: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)