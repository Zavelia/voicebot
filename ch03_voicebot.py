import streamlit as st
from audiorecorder import audiorecorder
#OpenAI 패키지 추가 
import openai 
#파일 삭제를 위한 패키지 추가 
import os 
#시간 정보를 위한 패키지 추가
from datetime import datetime
# TTS 패키지 추가
from gtts import gTTS
#음원 파일을 재생하기 위한 패키지 추가
import base64

# region Method 
## 기능 구현 함수 ## 
def STT(audio,apikey):
    #파일 저장
    filename= 'input.mp3'
    audio.export(filename,format="mp3")

    #음원 파일 열기
    audio_file = open(filename,"rb")
    #Whisper 모델을 활용하여 텍스트 얻기 
    client = openai.OpenAI(api_key=apikey)
    respons = client.audio.transcriptions.create(model="whisper-1",file=audio_file)
    audio_file.close()
    #파일 삭제
    os.remove(filename)
    return respons.text 

def ask_gpt(prompt,model,apikey):
    client = openai.OpenAI(api_key=apikey)
    response = client.chat.completions.create(
        model= model,
        messages= prompt
    )
    gptResponse = response.choices[0].message.content #gpt 응답
    return gptResponse

def TTS(response):
    #gTTS를 활용하여 음성 파일 생성
    filename = "output.mp3"
    tts = gTTS(text=response,lang="ko")
    tts.save(filename)

    #음원 파일 자동 재생
    with open(filename,"rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="True">
            <source src = "data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md,unsafe_allow_html=True)
    #파일 삭제
    os.remove(filename)

#endregion


## 메인 함수 ## 
def main():
    #region 기본 설정
    # 기본 설정
    # st.set_page_config() 함수를 활용하여 기본 설정을 한다. 
    # 기본 설정에서는 웹 브라우저에 표시할 타이틀과 레이아웃을 설정 가능 
    # page_title은 웹 브라우저의 탭에 표시할 제목을 설정 
    #layout="wide"는 콘탠츠를 넓게 배치하도록 설정
    st.set_page_config(
        page_title="음성 비서 프로그램", layout="wide"
    )

    # 제목
    st.header("음성 비서 프로그램")

    # 구분선
    #아래 함수를 이용하여 제목과 설명 사이를 구분하는 선을 추가
    st.markdown("---")
    #endregion

    # session state 초기화 
    if "chat" not in st.session_state:
        st.session_state["chat"] = [] 

    if "OPENAI_API" not in st.session_state:
        st.session_state["OPENAI_API"] =""
    
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]

    if "check_audio" not in st.session_state:
        st.session_state["check_reset"] = False
    
    #region 기본 설명
    #기본 설명
    #st.write 함수를 활용해 프로그램의 설명을 입력한다. 
    #st.write 함수를 with st.expander()로 감싸 설명 영역에 있는 내용들을 접거나 펼쳐서 볼 수 있도록 구현
    # 설명 영역의 오른쪽 상단에 있는 화살표를 클릭하면 설명을 접거나 펼칠 수 있다. 
    with st.expander("음성비서 프로그램에 관하여", expanded=True):
        st.write(
            """
            - 음성 비서 프로그램의 UI는 스트림릿을 활용했다.
            - STT(Speech to text)는 OpenAI의 Whisper AI를 활용했다.
            - 답변은 OpenAI의 GPT 모델을 활용했다.
            - TTS(Text to Speech)는 구글의 Google Translate TTS를 활용했다. 
            """
        )

        st.markdown("")

    #endregion

    #region 사이드바 생성
    #사이드바 생성 78페이지 참고
    with st.sidebar:
        #OpenAI API 키 입력받기 
        st.session_state["OPENAI_API"] = st.text_input(label="OPENAI API 키",
                                                       placeholder="Enter Your API Key", value="", type="password")
        
        st.markdown("---")

        #GPT 모델을 선택하기 위한 라디오 버튼 생성 
        model = st.radio(label="GPT 모델",options=["gpt-4","gpt-3.5-turbo"])

        st.markdown("---")

        #리셋 버튼 생성 
        #st.button(label="초기화")
        if st.button(label="초기화"):
             # 리셋 코드
             st.session_state["chat"] = [] 
             st.session_state["messages"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]
             st.session_state["check_reset"] = True
    #endregion

    #region 기능 구현 공간
    #기능 구현 공간, 83페이지 참고
    col1, col2 = st.columns(2)
    with col1:
        #왼쪽 영역 작성
        st.subheader("질문하기")
        #음성 녹음 아이콘 추가
        audio = audiorecorder("클릭하여 녹음하기","녹음 중...")
        if(audio.duration_seconds > 0) and (st.session_state["check_reset"] == False): #녹음을 실행하면? 
            # 음성 재생
            st.audio(audio.export().read())
            # 음원 파일에서 텍스트 추출 
            question = STT(audio,st.session_state["OPENAI_API"])

            #채팅을 시각화하기 위해 질문 내용 저장 
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("user",now,question)]
            #GPT 모델에 넣을 프롬프트를 위해 질문 내용 저장 
            st.session_state["messages"] = st.session_state["messages"] + [{"role":"user", "content":question}]
    
    with col2:
        #오른쪽 영역 작성
        st.subheader("질문/답변")
        if(audio.duration_seconds > 0) and (st.session_state["check_reset"] == False):
            #ChatGPT에게 답변 얻기 
            response = ask_gpt(st.session_state["messages"],model,st.session_state["OPENAI_API"])

            #GPT 모델에 넣을 프롬프트를 위해 답변 내용 저장 
            st.session_state["messages"] = st.session_state["messages"] + [{"role":"system","content":response}]

            #채팅 시각화를 위한 답변 내용 저장 
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("bot",now,response)]

            #채팅 형식으로 시각화하기 
            for sender, time , message in st.session_state["chat"]:
                if sender == "user":
                    st.write(f'''
            <div style="display:flex;align-items:center;">
                <div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">
                    {message}
                </div>
                <div style="font-size:0.8rem;color:gray;">
                    {time}
                </div>
            </div>
            ''',
            unsafe_allow_html=True) #sender가 user라면 파란색 배경으로 질문을 시각화한다. HTML문법 사용 
                    st.write("")
                
                else:
                    st.write(  f'''
            <div style="display:flex;align-items:center;justify-content:flex-end;">
                <div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">
                    {message}
                </div>
                <div style="font-size:0.8rem;color:gray;">
                    {time}
                </div>
            </div>
            ''',
            unsafe_allow_html=True) #sender가 user가 아니라면 회색 배경으로 ChatGPT의 답변을 시각화 
                    st.write("")
            
            #gTTS를 활용하여 음성 파일 생성 및 재생 
            TTS(response)

    #endregion


# 파이썬 스크립트를 실행하면 해당 부분이 먼저 실행되어 메인 함수가 동작
if __name__ == "__main__":
    main()
