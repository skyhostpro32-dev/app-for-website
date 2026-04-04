import streamlit as st
from PIL import Image, ImageFilter
import numpy as np
import io
import cv2
from rembg import remove
import streamlit.components.v1 as components

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="AI Image Dashboard", layout="wide")

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

/* 🔴 SELECTED RADIO BUTTON */
div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
    background-color: red !important;
    border-color: red !important;
}

/* INNER DOT WHITE */
div[role="radiogroup"] > label[data-baseweb="radio"] svg {
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
# BLUR TOOL (UPDATED BUTTONS)
# =========================
elif tool == "✨ Blur Object Tool":

    st.subheader("✨ Blur Object Tool")

    components.html("""
    <html><body style="text-align:center; font-family:Arial;">

    <h3>Upload → Click → Blur</h3>

    <input type="file" id="upload"><br><br>

    Brush Size:
    <input type="range" id="brush" min="10" max="80" value="30"><br><br>

    <style>
    .btn {
        border: none;
        padding: 14px 32px;
        font-size: 16px;
        border-radius: 10px;
        cursor: pointer;
        margin: 5px;
        color: white;
        font-weight: 500;
        width: 180px;
    }

    .apply { background-color: #4CAF50; }
    .apply:hover { background-color: #43a047; }

    .undo { background-color: #f1c40f; }
    .undo:hover { background-color: #d4ac0d; }

    .download { background-color: #3498db; }
    .download:hover { background-color: #2c80b4; }
    </style>

    <button id="apply" class="btn apply">✨ Apply Blur</button>
    <button id="undo" class="btn undo">↩ Undo</button>
    <button id="download" class="btn download">⬇ Download</button>

    <br><br>
    <canvas id="c" style="border:1px solid #ccc;"></canvas>

    <script>
    const upload = document.getElementById("upload");
    const canvas = document.getElementById("c");
    const ctx = canvas.getContext("2d");

    let img = new Image();
    let pts = [];

    upload.onchange = e => {
        img.src = URL.createObjectURL(e.target.files[0]);
        img.onload = () => {
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);

            let scale = Math.min(window.innerWidth / img.width, 0.8);
            canvas.style.width = img.width * scale + "px";
            canvas.style.height = img.height * scale + "px";
            pts = [];
        }
    }

    canvas.onclick = e => {
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;

        const x = (e.clientX - rect.left) * scaleX;
        const y = (e.clientY - rect.top) * scaleY;
        const size = parseInt(document.getElementById("brush").value);

        pts.push({x, y, size});
        redraw();
    }

    function redraw() {
        ctx.drawImage(img, 0, 0);
        pts.forEach(p => {
            ctx.fillStyle = "rgba(255,0,0,0.3)";
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fill();
        });
    }

    document.getElementById("apply").onclick = () => {
        ctx.drawImage(img, 0, 0);
        pts.forEach(p => {
            ctx.save();
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.clip();
            ctx.filter = "blur(12px)";
            ctx.drawImage(img, 0, 0);
            ctx.restore();
        });
        ctx.filter = "none";
        img.src = canvas.toDataURL();
        pts = [];
    }

    document.getElementById("undo").onclick = () => {
        pts.pop();
        redraw();
    }

    document.getElementById("download").onclick = () => {
        let link = document.createElement("a");
        link.download = "blur.png";
        link.href = canvas.toDataURL();
        link.click();
    }
    </script>
    </body></html>
    """, height=750)

# =========================
# DEFAULT
# =========================
else:
    st.info("👈 Upload image or select tool")

st.markdown("---")
st.caption("🚀 All-in-One AI Image Dashboard")
