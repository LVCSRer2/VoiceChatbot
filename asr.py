from fastapi import FastAPI, UploadFile, File
import os

# from pydantic import BaseModel
import os
from openai import OpenAI
from dotenv import load_dotenv
import shutil

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)

app = FastAPI()

# class ASRRequest(BaseModel):
#     prompt: str


@app.get('/')
def hello():
    return 'asr service'

@app.post("/asr")
async def transcribe(file: UploadFile = File(...)):
    filename = 'received_audio.wav'
    with open(filename, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    audio_file = open(filename, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    
    print(transcript)
    return {"transcription": transcript.text}



if __name__ == "__main__":
    import uvicorn
    filename = os.path.splitext(os.path.basename(__file__))[0]
    uvicorn.run(f"{filename}:app", port=8001, reload=True)
