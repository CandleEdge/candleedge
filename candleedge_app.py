
import streamlit as st
from PIL import Image
import numpy as np
import cv2

st.set_page_config(page_title="CandleEdge", layout="centered")
lang = st.sidebar.selectbox("Language / Idioma", ["English", "Español"])
st.title("🕯️ CandleEdge")
st.subheader("Structure-aware chart analysis and smart candle interpretation" if lang == "English"
             else "Análisis estructural del gráfico y lectura inteligente de velas")

uploaded_file = st.file_uploader("📤 Upload Chart Image", type=["png", "jpg", "jpeg"])

def detect_structure_and_candles(image_cv):
    h, w = image_cv.shape[:2]
    right = image_cv[:, int(w * 0.66):]

    gray = cv2.cvtColor(right, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    trend = "neutral"
    hammer_like = False
    engulfing_like = False
    structure = "flat"
    lows = []
    highs = []

    for cnt in contours:
        x, y, w_box, h_box = cv2.boundingRect(cnt)
        if h_box > 15 and w_box < 10:
            lows.append(y + h_box)
            highs.append(y)

    if len(lows) >= 3:
        diff_lows = np.diff(sorted(lows)[-3:])
        if all(d < 0 for d in diff_lows):
            structure = "higher_lows"
        elif all(d > 0 for d in diff_lows):
            structure = "lower_lows"

    if len(highs) >= 3:
        diff_highs = np.diff(sorted(highs)[:3])
        if all(d > 0 for d in diff_highs) and structure == "higher_lows":
            trend = "bullish"
        elif all(d < 0 for d in diff_highs) and structure == "lower_lows":
            trend = "bearish"
        else:
            trend = "neutral"

    if len(contours) > 0:
        largest = max(contours, key=cv2.contourArea)
        x, y, w_box, h_box = cv2.boundingRect(largest)
        aspect_ratio = h_box / (w_box + 1)
        if aspect_ratio > 3:
            if h_box > 40:
                engulfing_like = True
            elif h_box > 25:
                hammer_like = True

    return trend, structure, hammer_like, engulfing_like

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Chart", use_container_width=True)
    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    trend, structure, hammer, engulfing = detect_structure_and_candles(image_cv)

    st.markdown("### 📊 Technical Diagnosis" if lang == "English" else "### 📊 Diagnóstico Técnico")

    # Tendencia estructural
    if trend == "bullish":
        st.success("📈 Structure: Bullish reversal forming (higher lows and highs)" if lang == "English"
                   else "📈 Estructura: Reversión alcista en formación (mínimos y máximos crecientes)")
    elif trend == "bearish":
        st.error("📉 Structure: Bearish continuation (lower lows and highs)" if lang == "English"
                 else "📉 Estructura: Continuación bajista (mínimos y máximos decrecientes)")
    else:
        st.warning("🔁 Structure: Sideways / unconfirmed trend" if lang == "English"
                   else "🔁 Estructura: Lateral / sin tendencia clara")

    # Patrones
    if hammer:
        st.info("🕯️ Pattern: Hammer detected — possible reversal." if lang == "English"
                else "🕯️ Patrón: Martillo detectado — posible reversión.")
    if engulfing:
        st.info("🕯️ Pattern: Large engulfing candle — strong momentum." if lang == "English"
                else "🕯️ Patrón: Vela envolvente dominante — fuerte momentum.")

    # Comentario técnico final
    if trend == "bullish" and hammer:
        st.markdown("🔄 Confirmed reversal in progress. Watch for breakout continuation." if lang == "English"
                    else "🔄 Reversión confirmada en curso. Vigilar continuación alcista.")
    elif trend == "bearish" and engulfing:
        st.markdown("⚠️ Breakdown continuation likely. Momentum remains strong." if lang == "English"
                    else "⚠️ Probable continuación bajista. El momentum sigue fuerte.")
    elif trend == "neutral":
        st.markdown("📌 Price is in a range. Await clear breakout or breakdown." if lang == "English"
                    else "📌 Precio en rango. Esperar ruptura clara al alza o baja.")
