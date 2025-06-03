
import streamlit as st
from PIL import Image
import numpy as np
import cv2
import io

# Configuración inicial
st.set_page_config(page_title="CandleEdge", layout="centered")

# Selector de idioma
lang = st.sidebar.selectbox("Language / Idioma", ["English", "Español"])

# Título
st.title("🕯️ CandleEdge")
if lang == "English":
    st.subheader("Upload a chart to detect trend direction")
else:
    st.subheader("Sube una gráfica para detectar la dirección de la tendencia")

# Subida de imagen
uploaded_file = st.file_uploader("📤 Upload Chart Image", type=["png", "jpg", "jpeg"])

def detect_trend_direction(image):
    # Convertir a escala de grises
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Aplicar desenfoque para reducir ruido
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Detección de bordes
    edges = cv2.Canny(blurred, 50, 150)

    # Detectar líneas con Hough Transform
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=20)
    if lines is None:
        return "neutral"

    # Calcular ángulos de las líneas
    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
        angles.append(angle)

    if not angles:
        return "neutral"

    avg_angle = np.mean(angles)

    # Clasificar tendencia
    if avg_angle < -10:
        return "bullish"
    elif avg_angle > 10:
        return "bearish"
    else:
        return "neutral"

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Chart", use_column_width=True)

    # Convertir a formato OpenCV
    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    trend = detect_trend_direction(image_cv)

    st.markdown("### 🔍 Technical Diagnosis" if lang == "English" else "### 🔍 Diagnóstico Técnico")

    if trend == "bullish":
        st.success("📈 Trend: Strong bullish slope detected" if lang == "English"
                   else "📈 Tendencia: Pendiente alcista marcada")
    elif trend == "bearish":
        st.error("📉 Trend: Strong bearish slope detected" if lang == "English"
                 else "📉 Tendencia: Pendiente bajista marcada")
    else:
        st.warning("🔁 Trend: Sideways / neutral movement" if lang == "English"
                   else "🔁 Tendencia: Movimiento lateral / neutral")
