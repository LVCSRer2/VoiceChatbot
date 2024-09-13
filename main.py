from fastapi import FastAPI, File, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
from pydub import AudioSegment
import numpy as np
from scipy.io import wavfile



# 녹음 설정
SAMPLING_RATE = 16000  # 샘플링 레이트 (Hz)
CHANNELS = 1           # 채널 수
CHUNK = 512            # 데이터 청크 크기


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처에서의 요청 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)


@app.get('/')
def hello():
    return 'voice chatbot backend'


@app.post("/audio")
async def asr(file: UploadFile = File(...)):
    contents = await file.read()
    
    with open('audio.wav', 'wb') as file:
        file.write(contents)
    
    audio = AudioSegment.from_file('audio.wav').set_channels(1).set_frame_rate(16000).set_sample_width(2)
    audio_samples = np.array(audio.get_array_of_samples())
    wavfile.write('audio.wav', 16000, audio_samples)
    
    with open('audio.wav', 'rb') as f:
        response = requests.post("http://service-asr:8001/asr", files={"file": f})
    
    transcription = response.json().get("transcription")
    print(transcription)

    return {"transcription": transcription}


@app.websocket("/ws/chatbot")
async def websocket_chatbot(websocket: WebSocket):
    await websocket.accept()
    
    while True:
        # 클라이언트에서 transcription을 전달받음
        transcription = await websocket.receive_text()
        
        # 챗봇 서버에 transcription을 전송
        chatbot_response = requests.post("http://service-chatbot:8002/chatbot", json={'prompt': transcription})
        
        # 챗봇 응답을 클라이언트로 전송
        await websocket.send_text(chatbot_response.text)



if __name__ == "__main__":
    import uvicorn
    filename = os.path.splitext(os.path.basename(__file__))[0]
    uvicorn.run(f"{filename}:app", reload=True)
