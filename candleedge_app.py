
import streamlit as st
from PIL import Image
import numpy as np
import cv2

# Configuración
st.set_page_config(page_title="CandleEdge", layout="centered")

# Idioma
lang = st.sidebar.selectbox("Language / Idioma", ["English", "Español"])

# Título
st.title("🕯️ CandleEdge")
st.subheader("Detect visual trend and structure from your chart" if lang == "English"
             else "Detecta la tendencia y estructura visual de tu gráfico")

uploaded_file = st.file_uploader("📤 Upload Chart Image", type=["png", "jpg", "jpeg"])

def analyze_trend(image_cv):
    gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=50, maxLineGap=30)

    if lines is None:
        return "neutral", 0

    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
        angles.append(angle)

    avg_angle = np.mean(angles)
    if avg_angle < -12:
        return "bullish", avg_angle
    elif avg_angle > 12:
        return "bearish", avg_angle
    else:
        return "neutral", avg_angle

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Chart", use_container_width=True)

    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    trend, angle = analyze_trend(image_cv)

    st.markdown("### 🔍 Technical Diagnosis" if lang == "English" else "### 🔍 Diagnóstico Técnico")

    # Diagnóstico mejorado
    if trend == "bullish":
        st.success("📈 Trend: Bullish structure detected with upward momentum. "
                   "Angle avg: {:.2f}°".format(angle) if lang == "English"
                   else "📈 Tendencia: Estructura alcista con pendiente positiva. "
                        "Ángulo promedio: {:.2f}°".format(angle))
        st.info("Potential breakout if volume supports the move." if lang == "English"
                else "Posible ruptura si el volumen lo acompaña.")
    elif trend == "bearish":
        st.error("📉 Trend: Bearish pattern visible with downward pressure. "
                 "Angle avg: {:.2f}°".format(angle) if lang == "English"
                 else "📉 Tendencia: Estructura bajista con presión descendente. "
                      "Ángulo promedio: {:.2f}°".format(angle))
        st.warning("Risk of continuation unless support is confirmed." if lang == "English"
                   else "Riesgo de continuación bajista salvo que se confirme soporte.")
    else:
        st.warning("🔁 Trend: Sideways movement, no dominant direction. "
                   "Angle avg: {:.2f}°".format(angle) if lang == "English"
                   else "🔁 Tendencia: Movimiento lateral, sin dirección dominante. "
                        "Ángulo promedio: {:.2f}°".format(angle))
        st.info("Watch for breakout or breakdown near consolidation zone." if lang == "English"
                else "Esperar ruptura o quiebre en zona de consolidación.")
