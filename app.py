import streamlit as st
from PIL import Image, ImageFilter
import numpy as np
import io
import cv2
from rembg import remove
import streamlit.components.v1 as components

# =========================
# ✅ FAVICON (REPLACE STREAMLIT LOGO)
# =========================
favicon = Image.open("favicon.png")

st.set_page_config(
    page_title="AI Image Dashboard",
    page_icon=favicon,  # 👈 YOUR ICON HERE
    layout="wide"
)

# =========================
# 🎨 GLOBAL CSS
# =========================
st.markdown("""
<style>

/* SIDEBAR BACKGROUND */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2196F3, #64B5F6);
    color: white;
}

/* SIDEBAR TEXT */
section[data-testid="stSidebar"] * {
    color: white !important;
}

/* SELECTED RADIO */
div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
    background-color: red !important;
    border-color: red !important;
}

/* INNER DOT */
div[role="radiogroup"] svg {
    fill: white !important;
}

/* BUTTON STYLE */
section[data-testid="stSidebar"] button {
    background-color: #1976D2 !important;
    color: white !important;
    border-radius: 10px;
}

/* FILE UPLOADER */
section[data-testid="stSidebar"] .stFileUploader {
    background: rgba(255,255,255,0.15);
    border-radius: 12px;
    padding: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# 🖼 LOGO + TITLE (PRO LOOK)
# =========================
st.image("logo.png", width=180)
st.title("✨ AI Image Dashboard")

# =========================
# SIDEBAR
# =========================
st.sidebar.title("🧰 Tools")

uploaded_file = st.sidebar.file_uploader(
    "📤 Upload Image", type=["png", "jpg", "jpeg"]
)

tool = st.sidebar.radio(
    "Select Tool",
    [
        "🎨 Background Change",
        "✨ Enhance Image",
        "🧍 Auto Person Remove",
        "🌄 Background Removal",
        "✨ Blur Object Tool",
        "🖌 Manual Object Eraser"
    ]
)

# =========================
# NORMAL TOOLS
# =========================
if uploaded_file and tool not in ["✨ Blur Object Tool", "🖌 Manual Object Eraser"]:

    image = Image.open(uploaded_file).convert("RGB")
    image.thumbnail((600, 600))
    st.image(image)

    if tool == "🎨 Background Change":
        color_hex = st.sidebar.color_picker("Pick Background Color", "#00ffaa")
        color = tuple(int(color_hex[i:i+2], 16) for i in (1, 3, 5))

        if st.sidebar.button("Apply"):
            arr = np.array(image)
            mask = np.mean(arr, axis=2) > 200
            arr[mask] = color
            result = Image.fromarray(arr)

            st.image(result)
            buf = io.BytesIO()
            result.save(buf, format="PNG")
            st.download_button("Download", buf.getvalue())

    elif tool == "✨ Enhance Image":
        strength = st.sidebar.slider("Sharpness", 1, 5, 2)

        if st.sidebar.button("Enhance"):
            result = image
            for _ in range(strength):
                result = result.filter(ImageFilter.SHARPEN)

            st.image(result)
            buf = io.BytesIO()
            result.save(buf, format="PNG")
            st.download_button("Download", buf.getvalue())

    elif tool == "🧍 Auto Person Remove":
        if st.sidebar.button("Remove"):
            mask_img = remove(image)
            mask = np.array(mask_img)

            alpha = mask[:, :, 3] if mask.shape[2] == 4 else cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY)
            _, binary = cv2.threshold(alpha, 10, 255, cv2.THRESH_BINARY)

            result = cv2.inpaint(np.array(image), binary, 3, cv2.INPAINT_TELEA)

            st.image(result)
            st.download_button("Download", cv2.imencode(".png", result)[1].tobytes())

    elif tool == "🌄 Background Removal":
        if st.sidebar.button("Remove BG"):
            out = remove(image.convert("RGBA"))

            st.image(out)
            buf = io.BytesIO()
            out.save(buf, format="PNG")
            st.download_button("Download", buf.getvalue())

# =========================
# (YOUR OTHER TOOLS SAME — NO CHANGE)
# =========================

else:
    st.info("👈 Upload image or select tool")

st.markdown("---")
st.caption("🚀 All-in-One AI Image Dashboard")
