
import streamlit as st
from PIL import Image
import numpy as np
import cv2

st.set_page_config(page_title="CandleEdge", layout="centered")
lang = st.sidebar.selectbox("Language / Idioma", ["English", "Español"])
st.title("🕯️ CandleEdge")
st.subheader("Context-aware chart analysis and candle pattern detection" if lang == "English"
             else "Análisis gráfico con contexto visual y detección de patrones de vela")

uploaded_file = st.file_uploader("📤 Upload Chart Image", type=["png", "jpg", "jpeg"])

def analyze_context_and_pattern(image_cv):
    h, w = image_cv.shape[:2]
    left = image_cv[:, :int(w * 0.33)]
    middle = image_cv[:, int(w * 0.33):int(w * 0.66)]
    right = image_cv[:, int(w * 0.66):]

    gray_right = cv2.cvtColor(right, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray_right, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, 50, 20)

    trend = "neutral"
    hammer_like = False
    engulfing_like = False
    avg_angle = 0

    if lines is not None:
        angles = []
        lengths = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            length = np.hypot(x2 - x1, y2 - y1)
            angles.append(angle)
            lengths.append(length)

        if angles:
            avg_angle = np.mean(angles)
            # Nuevas reglas más realistas
            if avg_angle < -10:
                trend = "bearish"
            elif avg_angle > 10:
                trend = "bullish"
            else:
                trend = "neutral"

            # Detectar vela martillo (aproximada)
            long_down = [a for a in angles if a < -75]
            if len(long_down) == 1 and max(lengths) > 40:
                hammer_like = True
            if len(long_down) >= 3:
                engulfing_like = True

    return trend, avg_angle, hammer_like, engulfing_like

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Chart", use_container_width=True)
    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    trend, angle, hammer, engulfing = analyze_context_and_pattern(image_cv)

    st.markdown("### 📊 Technical Diagnosis" if lang == "English" else "### 📊 Diagnóstico Técnico")

    # Sección Trend
    if trend == "bearish":
        st.error("📉 Trend: Strong bearish structure. Angle avg: {:.2f}°".format(angle)
                 if lang == "English" else
                 "📉 Tendencia: Estructura fuertemente bajista. Ángulo promedio: {:.2f}°".format(angle))
    elif trend == "bullish":
        st.success("📈 Trend: Emerging bullish momentum. Angle avg: {:.2f}°".format(angle)
                   if lang == "English" else
                   "📈 Tendencia: Momento alcista emergente. Ángulo promedio: {:.2f}°".format(angle))
    else:
        st.warning("🔁 Trend: Sideways / neutral. Angle avg: {:.2f}°".format(angle)
                   if lang == "English" else
                   "🔁 Tendencia: Lateral / neutra. Ángulo promedio: {:.2f}°".format(angle))

    # Sección de patrones
    if hammer:
        st.info("🕯️ Pattern: Hammer detected after decline — possible reversal."
                if lang == "English" else
                "🕯️ Patrón: Martillo detectado tras caída — posible reversión.")
    elif engulfing:
        st.info("🕯️ Pattern: Large engulfing candle — strong momentum."
                if lang == "English" else
                "🕯️ Patrón: Vela envolvente dominante — fuerte momentum.")

    # Comentario técnico
    if trend == "bearish" and not hammer:
        st.markdown("⚠️ Breakdown confirmed. No reversal signal at this time." if lang == "English"
                    else "⚠️ Ruptura confirmada. Sin señales de reversión por ahora.")
    elif trend == "bullish" and hammer:
        st.markdown("🔄 Reversal underway. Monitor for confirmation breakout." if lang == "English"
                    else "🔄 Reversión en proceso. Vigilar confirmación de ruptura.")
    elif trend == "neutral":
        st.markdown("📌 Consolidation zone. Wait for breakout or breakdown." if lang == "English"
                    else "📌 Zona de consolidación. Esperar ruptura o quiebre.")
