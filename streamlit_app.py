from openai import OpenAI
import os
import streamlit as st
import tempfile as tf
import httpx

# 임시 폴더 생성
def create_temp_dir():
    set_temp_dir = tf.TemporaryDirectory()
    temp_dir = set_temp_dir.name
    os.chmod(temp_dir, 0o700)
    return temp_dir, set_temp_dir

def make_file(filehead, voice, text):
    temp_dir, set_temp_dir = create_temp_dir()
    audio_filename = os.path.join(temp_dir, filehead + ".mp3")
    print("audio filename: ", audio_filename)
    
    client = OpenAI()
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text,
    )

    try:
        with open(audio_filename, 'wb') as f:
            for chunk in response.iter_bytes():
                f.write(chunk)
        
        if os.path.exists(audio_filename):
            print("파일 생성 성공")
        else:
            print("파일 생성 실패")
    except Exception as e:
        print("오류: ", e)
    
    return audio_filename, set_temp_dir

def app():
    if "audio_file" not in st.session_state:
        st.session_state.audio_file = None
    if "filename" not in st.session_state:
        st.session_state.filename = None
    if "article_text" not in st.session_state:
        st.session_state.article_text = ''

    st.set_page_config(
        page_title="Simple Text-to-Speech",
        page_icon="https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Speaker_Icon.svg/1024px-Speaker_Icon.svg.png"
    )
    
    col1, col2 = st.columns([8, 2])
    with col1:
        st.title("simple text-to-speech")
    with col2:
        if st.button("clear ↺"):
            st.session_state.audio_file = None
            st.session_state.filename = None
            st.session_state.article_text = ''
            st.experimental_rerun()

    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Speaker_Icon.svg/1024px-Speaker_Icon.svg.png", width=150)
    OPENAI_API_KEY = st.text_input("OpenAI API-Key", placeholder="sk-...", type="password")
    article_text = st.text_area('본문 넣기', height=200, value=st.session_state.article_text, placeholder='별이 빛나는 밤하늘을 보며 갈 수가 있고 또 가야만 하는 길의 지도를 읽을 수 있던 시대는 얼마나 행복했던가.')
    filehead = st.text_input('파일명', placeholder='lukacs')
    tts_button = st.button("mp3 만들기")
    
    voice_select = st.radio(
            "목소리를 선택하세요.",
            ("Alloy", "Echo", "Fable", "Onyx", "Nova", "Shimmer")
        )
    voices = {
        "Alloy": "alloy", 
        "Echo": "echo", 
        "Fable": "fable",
        "Onyx": "onyx", 
        "Nova": "nova",
        "Shimmer": "shimmer"
    }
    voice = voices[voice_select]
    if OPENAI_API_KEY is not None:
        if tts_button or st.session_state.audio_file is not None:
            if tts_button:
                with st.spinner("오디오 파일을 생성하고 있어요... 🧐"):
                    try:
                        mp3_filepath, temp_dir_handle = make_file(filehead, voice, article_text)
                        print("mp3_filepath : ", mp3_filepath)
                        with open(mp3_filepath, 'rb') as f:
                            mp3_file = f.read()
                        st.session_state.audio_file = mp3_file
                        st.session_state.filename = filehead + '.mp3'
                        st.session_state.article_text = article_text
                        temp_dir_handle.cleanup()  # Ensure the temporary directory is cleaned up
                    except Exception as e:
                        st.error("오류가 발생했습니다.")
                        st.error(e)
            if st.session_state.audio_file is not None:
                st.audio(st.session_state.audio_file, format='audio/mp3')
                st.success("오디오 파일 생성 완료! 🥳")
                st.download_button(
                    label="오디오 파일(mp3) 내려받기",
                    data=st.session_state.audio_file,
                    file_name=st.session_state.filename,
                    mime='audio/mp3'
                )
    else:
        st.error("Put your OpenAI API-Key")

if __name__ == "__main__":
    app()
