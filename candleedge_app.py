
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
st.subheader("Advanced visual chart analysis with dominant candles and patterns" if lang == "English"
             else "Análisis avanzado de gráficos con velas dominantes y patrones")

uploaded_file = st.file_uploader("📤 Upload Chart Image", type=["png", "jpg", "jpeg"])

def detect_right_zone_pressure(image_cv):
    h, w = image_cv.shape[:2]
    right_third = image_cv[:, int(w * 2 / 3):]
    gray = cv2.cvtColor(right_third, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, 50, 20)

    if lines is None:
        return "neutral", 0, False, False

    angles = []
    long_red_bars = 0
    hammer_like = False
    engulfing_like = False

    for line in lines:
        x1, y1, x2, y2 = line[0]
        length = np.hypot(x2 - x1, y2 - y1)
        angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
        angles.append(angle)

        # Velas verticales largas
        if abs(angle) > 75 and length > 40:
            long_red_bars += 1

    avg_angle = np.mean(angles)

    trend = "neutral"
    if avg_angle < -12:
        trend = "bullish"
    elif avg_angle > 12:
        trend = "bearish"

    # Simular patrón martillo / envolvente (lógica simple basada en cantidad de líneas verticales)
    if long_red_bars >= 3:
        engulfing_like = True
    elif long_red_bars == 1:
        hammer_like = True

    return trend, avg_angle, hammer_like, engulfing_like

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Chart", use_container_width=True)

    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    trend, angle, hammer, engulfing = detect_right_zone_pressure(image_cv)

    st.markdown("### 🔍 Technical Diagnosis" if lang == "English" else "### 🔍 Diagnóstico Técnico")

    if trend == "bullish":
        st.success("📈 Trend: Bullish bias in final structure. Angle avg: {:.2f}°".format(angle) if lang == "English"
                   else "📈 Tendencia: Sesgo alcista en zona final. Ángulo promedio: {:.2f}°".format(angle))
    elif trend == "bearish":
        st.error("📉 Trend: Bearish pressure detected in final zone. Angle avg: {:.2f}°".format(angle) if lang == "English"
                 else "📉 Tendencia: Presión bajista en la zona final. Ángulo promedio: {:.2f}°".format(angle))
    else:
        st.warning("🔁 Trend: No dominant direction detected. Angle avg: {:.2f}°".format(angle) if lang == "English"
                   else "🔁 Tendencia: Sin dirección dominante. Ángulo promedio: {:.2f}°".format(angle))

    if hammer:
        st.info("🕯️ Pattern: Hammer-like candle detected — possible reversal." if lang == "English"
                else "🕯️ Patrón: Vela tipo martillo detectada — posible reversión.")
    if engulfing:
        st.info("🕯️ Pattern: Large engulfing candle detected — high momentum." if lang == "English"
                else "🕯️ Patrón: Vela envolvente dominante — alto momentum.")
