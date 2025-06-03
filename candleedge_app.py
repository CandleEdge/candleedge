
import streamlit as st
from PIL import Image
import numpy as np
import cv2

st.set_page_config(page_title="CandleEdge", layout="centered")
lang = st.sidebar.selectbox("Language / Idioma", ["English", "Español"])
st.title("🕯️ CandleEdge")
st.subheader("Price structure & directional strength analysis" if lang == "English"
             else "Análisis de estructura de precio y fuerza direccional")

uploaded_file = st.file_uploader("📤 Upload Chart Image", type=["png", "jpg", "jpeg"])

def diagnose_structure_with_range(image_cv):
    h, w = image_cv.shape[:2]
    analysis_zone = image_cv[:, int(w * 0.66):]

    gray = cv2.cvtColor(analysis_zone, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    highs, lows = [], []

    for cnt in contours:
        x, y, w_box, h_box = cv2.boundingRect(cnt)
        if h_box > 15 and w_box < 10:
            highs.append(y)
            lows.append(y + h_box)

    if len(highs) < 3 or len(lows) < 3:
        return "unclear", 0, 0, False, False

    highest = min(highs)
    lowest = max(lows)
    height = analysis_zone.shape[0]

    movement = lowest - highest
    percent_move = movement / height * 100
    slope_deg = np.degrees(np.arctan2(movement, analysis_zone.shape[1]))

    hammer_like = False
    engulfing_like = False

    largest = 0
    for cnt in contours:
        x, y, w_box, h_box = cv2.boundingRect(cnt)
        area = h_box * w_box
        if area > largest:
            aspect_ratio = h_box / (w_box + 1)
            if aspect_ratio > 3:
                if h_box > 40:
                    engulfing_like = True
                elif h_box > 25:
                    hammer_like = True
            largest = area

    if percent_move > 25:
        if slope_deg > 10:
            return "uptrend", percent_move, slope_deg, hammer_like, engulfing_like
        elif slope_deg < -10:
            return "downtrend", percent_move, slope_deg, hammer_like, engulfing_like
        else:
            return "volatile_range", percent_move, slope_deg, hammer_like, engulfing_like
    else:
        return "flat", percent_move, slope_deg, hammer_like, engulfing_like

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Chart", use_container_width=True)
    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    trend, move_pct, slope, hammer, engulfing = diagnose_structure_with_range(image_cv)

    st.markdown("### 📊 Technical Diagnosis" if lang == "English" else "### 📊 Diagnóstico Técnico")

    if trend == "uptrend":
        st.success("📈 Trend: Strong bullish recovery. Range: {:.1f}% | Slope: {:.1f}°".format(move_pct, slope)
                   if lang == "English" else
                   "📈 Tendencia: Recuperación alcista fuerte. Rango: {:.1f}% | Pendiente: {:.1f}°".format(move_pct, slope))
    elif trend == "downtrend":
        st.error("📉 Trend: Breakdown in progress. Range: {:.1f}% | Slope: {:.1f}°".format(move_pct, slope)
                 if lang == "English" else
                 "📉 Tendencia: Ruptura bajista en curso. Rango: {:.1f}% | Pendiente: {:.1f}°".format(move_pct, slope))
    elif trend == "volatile_range":
        st.warning("⚠️ Trend: Volatile sideways zone. Large movement but no clear direction." if lang == "English"
                   else "⚠️ Tendencia: Zona lateral volátil. Gran movimiento pero sin dirección clara.")
    elif trend == "flat":
        st.info("🔁 Trend: Flat / consolidation. Low directional strength." if lang == "English"
                else "🔁 Tendencia: Plana / consolidación. Fuerza direccional baja.")
    else:
        st.warning("🚫 Unable to determine structure. Image may lack sufficient data." if lang == "English"
                   else "🚫 No se pudo determinar estructura. Imagen posiblemente insuficiente.")

    if hammer:
        st.info("🕯️ Pattern: Hammer detected — potential reversal." if lang == "English"
                else "🕯️ Patrón: Martillo detectado — posible reversión.")
    if engulfing:
        st.info("🕯️ Pattern: Engulfing candle — strong directional push." if lang == "English"
                else "🕯️ Patrón: Vela envolvente — fuerte impulso direccional.")
