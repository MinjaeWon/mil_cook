import openai
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import streamlit as st
import qrcode
import base64


# # Streamlit 페이지 설정
# st.set_page_config(layout="wide")  # 페이지를 wide 모드로 설정

# # 사이드바 설정
# with st.sidebar:
#     st.title("Image Generation Settings")

# OpenAI API 키 설정
openai.api_key = st.secrets["OPENAI_API_KEY"]

def create_prevention_image(prompt, size):
    response = openai.Image.create(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        n=1  # 생성할 이미지 수
    )
    return response.data[0].url

def download_and_save_image(image_url, text, font_size):
    response = requests.get(image_url)
    image = Image.open(io.BytesIO(response.content))
    draw = ImageDraw.Draw(image)
    # font = ImageFont.truetype("fonts/gulim.ttc", font_size)
    font = ImageFont.truetype("/gulim.ttc", font_size)

    # 텍스트의 경계 상자 계산 및 위치 조정
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (image.width - text_width) / 2
    text_y = (image.height - text_height) / 2

    # 흰색 배경 추가
    background_margin = 10
    background_area = [text_x - background_margin, text_y - background_margin,
                       text_x + text_width + background_margin, text_y + text_height + background_margin]
    draw.rectangle(background_area, fill="white")

    # 텍스트 그리기
    draw.text((text_x, text_y), text, font=font, fill="black")

    # 이미지를 바이트로 변환
    byte_io = io.BytesIO()
    image.save(byte_io, 'JPEG')
    byte_io.seek(0)

    return byte_io

# # 메인 화면 레이아웃
# col1, col2 = st.columns(2)

# with col1:
#     st.title("Image Generation Settings")
#     prompt = st.text_area("만들고 싶은 이미지 프롬프트(Promt)를 작성해주세요")
#     size = st.selectbox("이미지 크기 선택:", options=["256x256", "512x512", "1024x1024", "2048x2048"])
#     text_to_add = st.text_input("이미지에 작성하고 싶은 표어(문구)를 작성해주세요")
#     font_size = st.slider("Select font size:", min_value=20, max_value=100, value=60)
#     submit_button = st.button("이미지 생성")

# if submit_button:
#     with col2:
#         # 이미지 생성 및 URL 출력
#         image_url = create_prevention_image(prompt, size)
#         # 이미지 다운로드 및 메모리에 저장
#         image_byte_io = download_and_save_image(image_url, text_to_add, font_size)
#         # 원본 이미지 표시
#         st.image(image_url, caption="Original Image")
#         # 텍스트가 추가된 이미지 표시
#         st.image(image_byte_io, caption="Text Overlay Image")
#         # 이미지 다운로드 링크 제공
#         st.download_button(label="이미지 다운로드",
#                            data=image_byte_io.getvalue(),
#                            file_name="final_image.jpg",
#                            mime="image/jpeg")


# 위에는 이미지 만드는것!!

# 아래는 QR 코드 만드는 것!!!
# 설문지 URL (Google Forms 등에서 생성한 후 여기에 붙여넣기)
survey_url = ''

def create_qr_code(url):
    # QR 코드 생성
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # QR 코드 이미지 생성
    img = qr.make_image(fill='black', back_color='white')
    return img

# QR 코드 이미지 다운로드 링크 생성
def get_image_download_link(img, filename, text):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = buffered.getvalue()
    href = f'<a href="data:file/png;base64,{base64.b64encode(img_str).decode()}" download="{filename}">{text}</a>'
    return href