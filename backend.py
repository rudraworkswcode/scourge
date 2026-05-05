from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from twilio.rest import Client
import os

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

@app.post("/api/activate-bot")
async def activate_bot(data: HealthData):
    try:
        # Format the message
        meds_summary = "\n".join(
            [f"- {m.medicine} (Frequency: {m.frequency}x/day at {m.time})" for m in data.medications]
        )
        
        message_body = (
            f"🚨 *HealthBot Activated!* 🚨\n\n"
            f"Symptoms: {data.symptoms}\n"
            f"Allergies: {data.allergies}\n\n"
            f"Your Medication Schedule:\n{meds_summary}\n\n"
            f"We will message you 1 hour before and call 15 minutes before dosing."
        )

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