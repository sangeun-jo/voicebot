import streamlit as st
from audiorecorder import audiorecorder
import openai
import os
import tempfile
from datetime import datetime
from gtts import gTTS
import base64


# 


def TTS(response):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
        filename = temp_audio.name
    
    tts = gTTS(text=response, lang="ko")
    tts.save(filename)

    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
        <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
    st.markdown(md, unsafe_allow_html=True,)
    
    try:
        os.remove(filename)
    except:
        pass

    

def STT(audio, apikey):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
        filename = temp_audio.name
    
    audio.export(filename, format="mp3")

    try:
        client = openai.OpenAI(api_key=apikey)
        with open(filename, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
    except Exception as e:
        st.error(f"STT 오류: {str(e)}")
        return "음성 인식에 실패했습니다."
    finally:
        try:
            os.remove(filename)
        except:
            pass
    
    return response.text

def ask_gpt(prompt, model, apikey):
    client = openai.OpenAI(api_key=apikey)
    response = client.chat.completions.create(
        model=model,
        messages=prompt
    )
    return response.choices[0].message.content

def main():
    st.set_page_config(
        page_title="음성 비서 프로그램",
        layout="wide"
    )

    st.header("음성 비서 프로그램")

    st.markdown("---")

    with st.expander("음성비서 프로그램에 관하여", expanded=True):
        st.write(
            """
            - 음성 비서 프로그램의 UI는 스트림릿을 활용했습니다.
            - STT(Speech-To-Text)는 OpenAI의 Whisper AI를 활용했습니다.
            - 답변은 OpenAI의 GPT 모델을 사용했습니다.
            - TTS(Text-To-Speech)는 구글의 Google Translate TTS를 활용했습니다.
            """
        )

        st.markdown("")

                # 세션 state 초기화
        if "chat" not in st.session_state:
            st.session_state["chat"] = []
        
        if "OPENAI_API" not in st.session_state:
            st.session_state["OPENAI_API"] = ""

        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role":"system", "content":"You are a thoughtful assistan. Response to all input 25 words and answer in korea"}]

        if "check_audio" not in st.session_state:
            st.session_state["check_reset"] = False


        # 사이드 바 생성 
        with st.sidebar:
            st.session_state["OPENAI_API"] = st.text_input(label="OPENAI API 키", placeholder="Enter Your API Key", value="", type="password")

            st.markdown("---")

            model = st.radio(label="GPT 모델", options=["gpt-4", "gpt-3.5-turbo"])

            st.markdown("---")

            if st.button(label="초기화"):
                print("버튼눌림")
                st.session_state["chat"] = []
                st.session_state["messages"] = [{"role":"system", "content":"You are a thoughtful assistan. Response to all input 25 words and answer in korea"}]
                st.session_state["check_reset"] = True
        
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("질문하기")
            audio = audiorecorder("클릭하여 녹음하기", "녹음 중...")
            if (audio.duration_seconds > 0) and (st.session_state["check_reset"]) == False:
                # 음성 재생
                st.audio(audio.export().read())

                question = STT(audio, st.session_state["OPENAI_API"])

                now = datetime.now().strftime("%H:%M")

                st.session_state["chat"] = st.session_state["chat"] + [("user", now, question)]
                st.session_state["messages"] = st.session_state["messages"] + [{"role":"user", "content":question}]
                
                
        with col2:
            st.subheader("질문/답변")

            if (audio.duration_seconds > 0) and (st.session_state["check_reset"]) == False:
                response = ask_gpt(st.session_state["messages"], model, st.session_state["OPENAI_API"])

                st.session_state["messages"] = st.session_state["messages"] + [{"role":"system", "content":response}]
                now = datetime.now().strftime("%H:%M")

                st.session_state["chat"] = st.session_state["chat"] + [("bot", now, response)]

                # 채팅 형식으로 시각화하기 
                for sender, time, message in st.session_state["chat"]:
                    if sender == "user":
                        st.write(
                            f'''<div style="display:flex;align-items:center;">
                                    <div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;"> 
                                        {message}
                                    </div>
                                    <div style="font-size:0.8rem;color:gray;">
                                        {time}
                                    </div>
                                </div>''', 
                            unsafe_allow_html=True)
                        st.write("")
                    else:
                        st.write(
                            f'''<div style="display:flex;align-items:center;justify-content:flex-end;">
                                    <div style="background-color:lightgrey; border-radius:12px;padding:8px 12px;margin-left:8px;"> 
                                        {message}
                                    </div>
                                    <div style="font-size:0.8rem;color:gray;">
                                        {time}
                                    </div>
                                </div>''', 
                            unsafe_allow_html=True)
                        st.write("")
                # gTTS를 활용하여 음성파일 생성 및 재생
                TTS(response)
if __name__ == "__main__":
    main()