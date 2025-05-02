import streamlit as st
import os, time, glob
import cv2, numpy as np, pytesseract
from PIL import Image
from gtts import gTTS
from googletrans import Translator
from io import BytesIO

# ──────────────── Preparar carpeta temporal ────────────────
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

def cleanup_old_files(days=7):
    now = time.time()
    for f in glob.glob(f"{TEMP_DIR}/*.mp3"):
        if os.stat(f).st_mtime < now - days * 86400:
            os.remove(f)

cleanup_old_files(7)

# ──────────────── Configuración de la página ────────────────
st.set_page_config(
    page_title="📸->🔤->🔊 OCR + TTS App",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────── Cabecera ────────────────
st.markdown(
    """
    <div style='text-align:center'>
      <h1>📷📝🔊 OCR & Text-to-Speech</h1>
      <p>💡 Captura texto de imágenes y conviértelo en voz con un solo clic</p>
    </div>
    """, unsafe_allow_html=True
)

# ──────────────── Selección de fuente ────────────────
col1, col2 = st.columns(2)
with col1:
    st.subheader("1️⃣ Origen de la imagen")
    use_cam = st.checkbox("🤳 Usar cámara")
    if use_cam:
        img_buffer = st.camera_input("🎥 Toma una foto")
    else:
        img_buffer = st.file_uploader("📂 Carga imagen", type=["png", "jpg", "jpeg"])
with col2:
    st.subheader("2️⃣ Opciones de preprocesado")
    apply_filter = st.selectbox("🔍 Contraste/Invertir", ["Normal", "Invertir", "Escala de grises"])
    st.caption("Puedes mejorar lectura de texto con filtros simples")

# ──────────────── Mostrar imagen y extraer texto ────────────────
extracted_text = ""
if img_buffer:
    img_bytes = img_buffer.getvalue()
    img_arr = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
    
    # aplicar filtro
    if apply_filter == "Invertir":
        img_arr = cv2.bitwise_not(img_arr)
    elif apply_filter == "Escala de grises":
        img_arr = cv2.cvtColor(img_arr, cv2.COLOR_BGR2GRAY)
        img_arr = cv2.cvtColor(img_arr, cv2.COLOR_GRAY2BGR)
    
    st.image(img_arr, caption="🖼️ Imagen procesada", use_column_width=True)
    extracted_text = pytesseract.image_to_string(img_arr)
    st.success("✅ Texto detectado con OCR")

# ──────────────── Mostrar y editar texto ────────────────
st.subheader("3️⃣ Revisa y edita el texto extraído ✍️")
text = st.text_area("✂️ Texto OCR", value=extracted_text, height=200)

# ──────────────── Traducción opcional ────────────────
st.sidebar.header("🌐 Traducción")
translator = Translator()
if st.sidebar.checkbox("Traducir texto"):
    src = st.sidebar.selectbox("Idioma origen", ["auto", "en", "es", "fr", "de", "zh-cn", "ja", "ko"])
    dest = st.sidebar.selectbox("Idioma destino", ["en", "es", "fr", "de", "zh-cn", "ja", "ko"])
    if st.sidebar.button("🔄 Traducir"):
        with st.spinner("📝 Traduciendo..."):
            text = translator.translate(text, src=src, dest=dest).text
        st.sidebar.success(f"Traducido a {dest}")

# ──────────────── Text-to-Speech ────────────────
st.sidebar.header("🔊 Text-to-Speech")
lang = st.sidebar.selectbox("🆔 Idioma TTS", ["en", "es", "fr", "de", "zh-cn", "ja", "ko"])
accent = st.sidebar.selectbox("🎙️ Acento Inglés", ["com", "co.uk", "com.au", "ca", "com"])
if st.sidebar.button("▶️ Generar Audio"):
    if not text.strip():
        st.sidebar.error("❌ El texto está vacío")
    else:
        with st.spinner("🎧 Generando audio..."):
            tts = gTTS(text, lang=lang, tld=accent, slow=False)
            fn = f"{TEMP_DIR}/tts_output.mp3"
            tts.save(fn)
        st.sidebar.success("✅ Audio listo")

        audio_bytes = open(fn, "rb").read()
        st.audio(audio_bytes, format="audio/mp3")
        b64 = base64.b64encode(audio_bytes).decode()
        download_md = f'<a href="data:audio/mp3;base64,{b64}" download="ocr_tts.mp3">📥 Descargar MP3</a>'
        st.markdown(download_md, unsafe_allow_html=True)

# ──────────────── Footer ────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:gray'>"
    "👨‍💻 Hecho con ❤️ por tu nombre · Proyecto de la Universidad EAFIT"
    "</div>",
    unsafe_allow_html=True
)
