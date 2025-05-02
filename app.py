import streamlit as st
import os, time, glob, base64
import cv2, numpy as np, pytesseract
from gtts import gTTS
from googletrans import Translator
from io import BytesIO

# ─── PREPARAR CARPETA TEMPORAL ──────────────────────────────
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)
def cleanup(days=7):
    now = time.time()
    for f in glob.glob(f"{TEMP_DIR}/*.mp3"):
        if os.stat(f).st_mtime < now - days*86400:
            os.remove(f)
cleanup(7)

# ─── CONFIGURACIÓN PÁGINA ──────────────────────────────────
st.set_page_config(page_title="OCR ➡️ Español ➡️ Voz", layout="wide")

# ─── CABECERA ───────────────────────────────────────────────
st.markdown("""
  <h1 style="text-align:center">📷 ➡️ 🔤 ➡️ 🗣️</h1>
  <p style="text-align:center">Extrae texto de imágenes, traduce al español y genera audio en español</p>
""", unsafe_allow_html=True)

# ─── SELECCIÓN DE IMAGEN ────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    use_cam = st.checkbox("🤳 Usar cámara", value=False)
    img_buf = st.camera_input("Toma una foto") if use_cam else st.file_uploader("Carga imagen", type=["png","jpg","jpeg"])
with col2:
    filtro = st.selectbox("🎨 Filtro (mejora OCR)", ["Ninguno", "Invertir", "Escala de grises"])

# ─── PROCESAR & EXTRAER TEXTO ───────────────────────────────
ocr_text = ""
if img_buf:
    data = img_buf.getvalue()
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if filtro=="Invertir":
        img = cv2.bitwise_not(img)
    elif filtro=="Escala de grises":
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
    st.image(img, caption="🖼 Imagen procesada")
    ocr_text = pytesseract.image_to_string(img)
    st.success("✅ Texto detectado por OCR")

# ─── TRADUCIR SIEMPRE A ESPAÑOL ─────────────────────────────
st.subheader("✍️ Texto (editable antes de audio)")
translator = Translator()
if ocr_text:
    # traducimos al español aunque el texto ya esté en español — así unificamos
    with st.spinner("🌐 Traduciendo al español..."):
        ocr_text = translator.translate(ocr_text, dest="es").text

text = st.text_area("Texto listo para TTS:", value=ocr_text, height=200)

# ─── GENERAR AUDIO EN ESPAÑOL ───────────────────────────────
if st.button("▶️ Generar Audio en Español"):
    if not text.strip():
        st.error("❌ No hay texto para convertir")
    else:
        with st.spinner("🔊 Generando audio..."):
            tts = gTTS(text, lang="es", slow=False)
            out = os.path.join(TEMP_DIR, "salida.mp3")
            tts.save(out)
        st.success("✅ Audio listo")
        audio_bytes = open(out,"rb").read()
        st.audio(audio_bytes, format="audio/mp3")
        b64 = base64.b64encode(audio_bytes).decode()
        st.markdown(
            f'<a href="data:audio/mp3;base64,{b64}" download="texto_español.mp3">📥 Descargar audio</a>',
            unsafe_allow_html=True
        )

# ─── FOOTER ─────────────────────────────────────────────────
st.markdown("---")
st.markdown("<p style='text-align:center; color:gray'>Hecho con ❤️</p>", unsafe_allow_html=True)
