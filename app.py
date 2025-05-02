import streamlit as st
import os, time, glob, base64            # <- Importamos base64 aquí
import cv2, numpy as np, pytesseract
from PIL import Image
from gtts import gTTS
from googletrans import Translator
from io import BytesIO

# Preparar carpeta temporal
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

def cleanup_old_files(days=7):
    now = time.time()
    for f in glob.glob(f"{TEMP_DIR}/*.mp3"):
        if os.stat(f).st_mtime < now - days * 86400:
            os.remove(f)

cleanup_old_files(7)

# Configuración de la página
st.set_page_config(
    page_title="📸📝🔊 OCR & TTS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cabecera
st.markdown(
    """
    <h1 style='text-align:center'>📷 ➡️ 🔤 ➡️ 🔊 
    OCR & Text-to-Speech</h1>
    <p style='text-align:center'>
      Captura texto de imágenes y conviértelo en voz
    </p>
    """, unsafe_allow_html=True
)

# 1️⃣ Origen de la imagen
col1, col2 = st.columns(2)
with col1:
    st.subheader("1️⃣ Elige la imagen")
    use_cam = st.checkbox("🤳 Usar cámara", value=False)
    if use_cam:
        img_buffer = st.camera_input("Toma una foto")
    else:
        img_buffer = st.file_uploader("Carga imagen", type=["png","jpg","jpeg"])
with col2:
    st.subheader("2️⃣ Filtro (opcional)")
    filtro = st.selectbox(
        "Mejora OCR con filtro",
        ["Ninguno", "Invertir", "Escala de grises"]
    )

# Procesar imagen y extraer texto
extracted_text = ""
if img_buffer:
    # Leer en OpenCV
    data = img_buffer.getvalue()
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if filtro == "Invertir":
        img = cv2.bitwise_not(img)
    elif filtro == "Escala de grises":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    st.image(img, caption="Imagen procesada", use_column_width=True)
    extracted_text = pytesseract.image_to_string(img)
    st.success("✅ Texto detectado")

# 3️⃣ Revisar / editar texto
st.subheader("3️⃣ Revisa el texto")
text = st.text_area("Texto OCR extraído:", value=extracted_text, height=200)

# Simplificar traducción: origen siempre 'es'
st.sidebar.header("🌐 Traducción (opcional)")
if st.sidebar.checkbox("Traducir texto"):
    target_lang = st.sidebar.selectbox(
        "Idioma destino",
        ("en","fr","de","zh-cn","ja","ko"),
        index=0
    )
    if st.sidebar.button("🔄 Traducir"):
        with st.spinner("Traduciendo..."):
            translator = Translator()
            text = translator.translate(text, src="es", dest=target_lang).text
        st.sidebar.success(f"Traducido a {target_lang}")

# 🔊 Text-to-Speech
st.sidebar.header("🔉 Text-to-Speech")
tts_lang = st.sidebar.selectbox(
    "Idioma TTS",
    ("es","en","fr","de","zh-cn","ja","ko"),
    index=0  # por defecto español
)
english_accent = st.sidebar.selectbox(
    "Acento Inglés (solo si es en)",
    ("com","co.uk","com.au","ca","ie","co.za"),
    index=0
)
if st.sidebar.button("▶️ Generar Audio"):
    if not text.strip():
        st.sidebar.error("El texto está vacío")
    else:
        with st.spinner("Generando audio..."):
            tts = gTTS(text, lang=tts_lang, tld=english_accent, slow=False)
            out_path = os.path.join(TEMP_DIR, "output.mp3")
            tts.save(out_path)
        st.sidebar.success("Audio listo ✅")
        audio_bytes = open(out_path, "rb").read()
        st.audio(audio_bytes, format="audio/mp3")
        # Link de descarga
        b64 = base64.b64encode(audio_bytes).decode()
        href = (
            f'<a href="data:audio/mp3;base64,{b64}" '
            f'download="ocr_tts.mp3">📥 Descargar MP3</a>'
        )
        st.markdown(href, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center; color:gray'>Hecho con ❤️</p>", unsafe_allow_html=True)
