import openai 
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# API 키 가져오기
API_KEY = os.getenv("OPENAI_KEY")
client = openai.OpenAI(api_key=API_KEY)

audio_file = open("output.mp3", 'rb')

transcript = client.audio.transcriptions.create(model = "whisper-1", file=audio_file)

print(transcript.text)