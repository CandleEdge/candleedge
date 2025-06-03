
import streamlit as st
from PIL import Image
import numpy as np
import cv2

st.set_page_config(page_title="CandleEdge", layout="centered")

lang = st.sidebar.selectbox("Language / Idioma", ["English", "Español"])
st.title("🕯️ CandleEdge")
st.subheader("Accurate trend detection and dominant candle recognition" if lang == "English"
             else "Detección precisa de tendencia y velas dominantes")

uploaded_file = st.file_uploader("📤 Upload Chart Image", type=["png", "jpg", "jpeg"])

def analyze_critical_zone(image_cv):
    h, w = image_cv.shape[:2]
    final_zone = image_cv[:, int(w * 2 / 3):]
    gray = cv2.cvtColor(final_zone, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, 50, 20)

    if lines is None:
        return "neutral", 0, False, False

    angles = []
    verticals = 0

    for line in lines:
        x1, y1, x2, y2 = line[0]
        length = np.hypot(x2 - x1, y2 - y1)
        angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
        angles.append(angle)

        if abs(angle) > 75 and length > 40:
            verticals += 1

    avg_angle = np.mean(angles)

    # Corrección clave: ahora ángulo negativo indica caída = bearish
    if avg_angle < -12:
        trend = "bearish"
    elif avg_angle > 12:
        trend = "bullish"
    else:
        trend = "neutral"

    hammer_like = verticals == 1
    engulfing_like = verticals >= 3

    return trend, avg_angle, hammer_like, engulfing_like

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Chart", use_container_width=True)

    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    trend, angle, hammer, engulfing = analyze_critical_zone(image_cv)

    st.markdown("### 🔍 Technical Diagnosis" if lang == "English" else "### 🔍 Diagnóstico Técnico")

    if trend == "bearish":
        st.error("📉 Bearish breakdown in progress. Angle avg: {:.2f}°".format(angle)
                 if lang == "English" else
                 "📉 Ruptura bajista en curso. Ángulo promedio: {:.2f}°".format(angle))
        st.warning("Dominant downward pressure. Watch for continuation unless reversal pattern appears." 
                   if lang == "English" else
                   "Presión bajista dominante. Posible continuación salvo reversión clara.")
    elif trend == "bullish":
        st.success("📈 Upward slope detected in final zone. Angle avg: {:.2f}°".format(angle)
                   if lang == "English" else
                   "📈 Pendiente alcista en zona final. Ángulo promedio: {:.2f}°".format(angle))
    else:
        st.warning("🔁 Neutral/sideways price action. Angle avg: {:.2f}°".format(angle)
                   if lang == "English" else
                   "🔁 Movimiento lateral o neutro. Ángulo promedio: {:.2f}°".format(angle))

    if hammer:
        st.info("🕯️ Pattern: Hammer-like structure — possible reversal."
                if lang == "English" else
                "🕯️ Patrón: Vela tipo martillo — posible reversión.")
    if engulfing:
        st.info("🕯️ Pattern: Large engulfing candle detected — strong momentum."
                if lang == "English" else
                "🕯️ Patrón: Vela envolvente dominante — fuerte momentum.")
