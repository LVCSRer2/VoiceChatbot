from fastapi import FastAPI
from pydantic import BaseModel
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)
app = FastAPI()

class ChatRequest(BaseModel):
    prompt: str

@app.get('/')
def hello():
    return 'chatbot service'

@app.post("/chatbot")
async def chatbot(request: ChatRequest):
  prompt = request.prompt

  response = client.chat.completions.create(
    model="gpt-4o-mini",
    
    messages=[
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": prompt
          }
        ]
      }
    ],
    temperature=1,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    response_format={
      "type": "text"
      # "type": "json_object"
    }
  )

  print(response.choices[0].message.content)
  return response.choices[0].message.content


if __name__ == "__main__":
    import uvicorn
    filename = os.path.splitext(os.path.basename(__file__))[0]
    uvicorn.run(f"{filename}:app", port=8002, reload=True)
