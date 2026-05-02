import streamlit as st
import joblib
import pandas as pd
import numpy as np
import os
import time
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(
    page_title="CINERATE AI | Premium Movie Intelligence",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Premium UI/UX with Royal Blue Gradient and Glassmorphism
st.markdown("""
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap" rel="stylesheet">
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #001f3f 0%, #003366 50%, #001f3f 100%);
        font-family: 'Poppins', sans-serif;
        color: #f8fafc;
    }

    /* Film Grain Overlay */
    .film-grain-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 9999;
        opacity: 0.03;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
    }

    /* Spotlight Glow Effect */
    .spotlight-glow {
        position: fixed;
        top: -50%;
        left: 50%;
        transform: translateX(-50%);
        width: 150%;
        height: 100%;
        background: radial-gradient(ellipse at center, rgba(0, 242, 255, 0.08) 0%, transparent 60%);
        pointer-events: none;
        z-index: 0;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        z-index: 1;
    }

    .glass-card:hover {
        transform: translateY(-8px) scale(1.02);
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(0, 242, 255, 0.4);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 0 20px rgba(0, 242, 255, 0.2);
    }

    /* Glowing Header Animation */
    @keyframes shine {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }

    .shining-title {
        text-align: center;
        font-size: 4.5rem;
        font-weight: 800;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #00f2ff, #7d2ae8, #00f2ff);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 3s linear infinite;
        letter-spacing: -2px;
        filter: drop-shadow(0 0 10px rgba(0, 242, 255, 0.3));
    }

    /* Cinematic Banner */
    .cinematic-banner {
        background: linear-gradient(135deg, rgba(0, 242, 255, 0.1) 0%, rgba(125, 42, 232, 0.1) 100%);
        border: 1px solid rgba(0, 242, 255, 0.2);
        border-radius: 15px;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        position: relative;
        z-index: 1;
    }

    .cinematic-banner h2 {
        margin: 0;
        font-weight: 700;
        font-size: 1.3rem;
    }

    /* Metric Styling */
    .metric-value {
        font-size: 3.5rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
        line-height: 1;
        text-shadow: 0 0 15px rgba(255, 255, 255, 0.2);
    }
    
    .metric-label {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #94a3b8;
        margin-bottom: 0.5rem;
    }

    /* Metric Icon */
    .metric-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    /* Neon Accents */
    .neon-cyan { color: #00f2ff; text-shadow: 0 0 10px rgba(0, 242, 255, 0.5); }
    .neon-purple { color: #7d2ae8; text-shadow: 0 0 10px rgba(125, 42, 232, 0.5); }
    .neon-gold { color: #ffd700; text-shadow: 0 0 10px rgba(255, 215, 0, 0.5); }

    /* Modern AI Prediction Button */
    .predict-btn {
        background: linear-gradient(135deg, #00f2ff 0%, #7d2ae8 50%, #ff3366 100%);
        background-size: 200% 200%;
        color: white;
        border: none;
        padding: 1.2rem 2.5rem;
        border-radius: 16px;
        font-weight: 700;
        font-size: 1.2rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: all 0.4s ease;
        width: 100%;
        margin-top: 1.5rem;
        position: relative;
        overflow: hidden;
        animation: gradient-shift 3s ease infinite;
    }

    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .predict-btn:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 15px 35px rgba(0, 242, 255, 0.4), 0 0 30px rgba(125, 42, 232, 0.3);
        color: #ffffff !important;
    }

    .predict-btn::before {
        content: '⚡';
        margin-right: 10px;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .sidebar-header {
        font-weight: 700;
        color: #00f2ff;
        margin-bottom: 1rem;
        font-size: 1.2rem;
    }

    /* Custom Input Labels with Icons */
    .custom-label-wrapper {
        margin-bottom: -8px; /* Reduces gap between html label and input */
    }
    .custom-label {
        font-size: 0.9rem;
        color: #f8fafc;
        display: flex;
        align-items: center;
        font-family: inherit;
        font-weight: 400;
    }
    .icon-glow {
        margin-right: 10px;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    .icon-glow.cyan { color: #00f2ff; }
    .icon-glow.purple { color: #7d2ae8; }
    .icon-glow.pink { color: #ff3366; }
    .icon-glow.gold { color: #ffd700; }
    
    .custom-label:hover .icon-glow {
        transform: scale(1.15);
    }
    .custom-label:hover .icon-glow.cyan { text-shadow: 0 0 12px rgba(0, 242, 255, 0.8); }
    .custom-label:hover .icon-glow.purple { text-shadow: 0 0 12px rgba(125, 42, 232, 0.8); }
    .custom-label:hover .icon-glow.pink { text-shadow: 0 0 12px rgba(255, 51, 102, 0.8); }
    .custom-label:hover .icon-glow.gold { text-shadow: 0 0 12px rgba(255, 215, 0, 0.8); }

    /* Hide standard UI elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}

    /* Custom Input Styling */
    .stSelectbox, .stNumberInput, .stSlider {
        margin-bottom: 1rem;
    }

    /* Movie Reel Decoration */
    .movie-reel-decoration {
        position: fixed;
        right: 10px;
        top: 50%;
        transform: translateY(-50%);
        opacity: 0.05;
        font-size: 8rem;
        color: #00f2ff;
        z-index: 0;
        pointer-events: none;
    }

    /* Hero Section */
    .hero-section {
        text-align: center;
        padding: 3rem 2rem;
        position: relative;
        z-index: 1;
    }

    .hero-icons {
        font-size: 3rem;
        margin-bottom: 1rem;
    }

    /* Result Card Enhancement */
    .result-card {
        background: linear-gradient(135deg, rgba(0, 242, 255, 0.08) 0%, rgba(125, 42, 232, 0.08) 100%);
        border: 1px solid rgba(0, 242, 255, 0.15);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }

    .result-card:hover {
        border-color: rgba(0, 242, 255, 0.3);
        box-shadow: 0 0 25px rgba(0, 242, 255, 0.15);
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .fade-in-up {
        animation: fadeInUp 0.6s ease-out forwards;
    }

    @keyframes countUp {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }

    .glass-card {
        backdrop-filter: blur(20px);
        background: rgba(15, 23, 42, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 24px !important;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 0 0 1px rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
    }

    .glass-card:hover {
        border-color: rgba(0, 242, 255, 0.2);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5), 0 0 30px rgba(0, 242, 255, 0.1);
    }

    /* Clapperboard Animation Overlay */
    .clapper-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.85);
        z-index: 10000;
        display: none;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        perspective: 1000px;
    }

    .clapper-overlay.active {
        display: flex;
        animation: fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }

    @keyframes fadeIn {
        from { opacity: 0; background: rgba(0,0,0,0); }
        to { opacity: 1; background: rgba(0,0,0,0.85); }
    }

    .clapper-container {
        position: relative;
        width: 320px;
        height: 280px;
        transform-style: preserve-3d;
        filter: drop-shadow(0 30px 50px rgba(0,0,0,0.8));
    }

    .clapperboard {
        position: absolute;
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        transform: rotateY(-5deg) rotateX(5deg);
    }

    /* Clapper Top (movable part) */
    .clapper-top {
        width: 300px;
        height: 50px;
        background: #1a1a1a;
        border: 2px solid #333;
        border-bottom: none;
        border-radius: 6px 6px 0 0;
        position: relative;
        transform-origin: center bottom;
        display: flex;
        overflow: hidden;
        z-index: 2;
        box-shadow: inset 0 2px 5px rgba(255,255,255,0.1);
    }

    .clapper-top::before {
        content: '';
        position: absolute;
        top: 0;
        left: -50px;
        right: -50px;
        bottom: 0;
        background: repeating-linear-gradient(
            -45deg,
            #1a1a1a 0px,
            #1a1a1a 30px,
            #eeeeee 30px,
            #eeeeee 60px
        );
        box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
    }

    /* Clapper Bottom (fixed part) */
    .clapper-bottom {
        width: 300px;
        height: 160px;
        background: linear-gradient(135deg, #222 0%, #111 100%);
        border: 2px solid #333;
        border-radius: 0 0 6px 6px;
        display: flex;
        flex-direction: column;
        padding: 20px;
        box-sizing: border-box;
        position: relative;
        z-index: 1;
        box-shadow: inset 0 0 30px rgba(0,0,0,0.6);
    }

    /* Realistic Hinge */
    .clapper-hinge {
        position: absolute;
        left: 10px;
        bottom: -5px;
        width: 15px;
        height: 15px;
        background: #444;
        border-radius: 50%;
        border: 2px solid #222;
        z-index: 3;
    }

    .clapper-row {
        display: flex;
        gap: 10px;
        margin-bottom: 12px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        padding-bottom: 5px;
    }

    .clapper-cell {
        flex: 1;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.75rem;
        font-weight: 800;
        color: #ddd;
        text-transform: uppercase;
    }

    .clapper-value {
        color: #00f2ff;
        font-size: 0.9rem;
        margin-top: 2px;
        text-shadow: 0 0 10px rgba(0, 242, 255, 0.3);
    }

    /* Clapper Animation with Sharp Snap and Bounce */
    .clapper-top.animating {
        animation: realisticClap 1.4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
    }

    @keyframes realisticClap {
        0% {
            transform: rotateZ(0deg);
            filter: blur(0px);
        }
        20% {
            transform: rotateZ(-35deg);
            filter: blur(1px);
        }
        35% {
            transform: rotateZ(0deg); /* Sharp Snap */
            filter: blur(2px);
        }
        40% {
            transform: rotateZ(-5deg); /* Bounce Up */
            filter: blur(0px);
        }
        50% {
            transform: rotateZ(0deg); /* Final Settle */
        }
        100% {
            transform: rotateZ(0deg);
        }
    }

    /* Dust Particles when claps */
    .dust-container {
        position: absolute;
        top: 60px;
        width: 100%;
        height: 20px;
        pointer-events: none;
        display: flex;
        justify-content: center;
        overflow: visible;
    }

    .particle {
        width: 4px;
        height: 4px;
        background: rgba(255,255,255,0.4);
        border-radius: 50%;
        position: absolute;
        opacity: 0;
    }

    .particle.active {
        animation: particleFly 0.6s ease-out forwards;
    }

    @keyframes particleFly {
        0% { transform: translateY(0) scale(1); opacity: 0.8; }
        100% { transform: translateY(-40px) translateX(var(--x)) scale(0); opacity: 0; }
    }

    .clapper-text {
        margin-top: 40px;
        color: #f8fafc;
        font-size: 1.4rem;
        font-weight: 700;
        letter-spacing: 5px;
        text-transform: uppercase;
        text-shadow: 0 0 20px rgba(0, 242, 255, 0.5);
    }

    .scene-text {
        color: #00f2ff;
        font-size: 0.8rem;
        margin-top: 10px;
        letter-spacing: 3px;
        opacity: 0.8;
    }
</style>

<!-- Film Grain Overlay -->
<div class="film-grain-overlay"></div>

<!-- Spotlight Glow -->
<div class="spotlight-glow"></div>

<!-- Movie Reel Decoration -->
<div class="movie-reel-decoration">🎬</div>

<!-- Clapperboard Animation Overlay -->
<div id="clapperOverlay" class="clapper-overlay">
    <div class="clapper-container">
        <div class="clapperboard">
            <div class="clapper-top" id="clapperTop"></div>
            <div class="clapper-hinge"></div>
            <div class="clapper-bottom">
                <div class="clapper-row">
                    <div class="clapper-cell">PROD. <div class="clapper-value">CINERATE AI</div></div>
                    <div class="clapper-cell">ROLL <div class="clapper-value">A-001</div></div>
                </div>
                <div class="clapper-row">
                    <div class="clapper-cell">SCENE <div class="clapper-value">PREDICT</div></div>
                    <div class="clapper-cell">TAKE <div class="clapper-value">01</div></div>
                </div>
                <div class="clapper-row">
                    <div class="clapper-cell">DIRECTOR <div class="clapper-value">AI ENGINE</div></div>
                </div>
                <div class="clapper-row">
                    <div class="clapper-cell">DATE <div class="clapper-value" id="clapperDate">2026</div></div>
                    <div class="clapper-cell">FPS <div class="clapper-value">24.0</div></div>
                </div>
            </div>
            <div class="dust-container" id="dustContainer"></div>
        </div>
    </div>
    <div class="clapper-text">Processing...</div>
    <div class="scene-text">🎬 CAMERA ROLLING • ACTION</div>
</div>

<script>
// Audio context for realistic clap sound
let audioCtx = null;
function playClapSound() {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    
    osc.type = 'square';
    osc.frequency.setValueAtTime(150, audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(40, audioCtx.currentTime + 0.1);
    
    gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.15);
    
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    
    osc.start();
    osc.stop(audioCtx.currentTime + 0.15);
    
    // Noise burst for "snap"
    const bufferSize = audioCtx.sampleRate * 0.05;
    const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) data[i] = Math.random() * 2 - 1;
    
    const noise = audioCtx.createBufferSource();
    noise.buffer = buffer;
    const noiseGain = audioCtx.createGain();
    noiseGain.gain.setValueAtTime(0.2, audioCtx.currentTime);
    noiseGain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.05);
    noise.connect(noiseGain);
    noiseGain.connect(audioCtx.destination);
    noise.start();
}

function createDust() {
    const container = document.getElementById('dustContainer');
    if (!container) return;
    container.innerHTML = '';
    for (let i = 0; i < 15; i++) {
        const p = document.createElement('div');
        p.className = 'particle active';
        p.style.setProperty('--x', (Math.random() * 200 - 100) + 'px');
        p.style.left = (Math.random() * 100) + '%';
        container.appendChild(p);
    }
}

function showClapper() {
    const overlay = document.getElementById('clapperOverlay');
    const clapperTop = document.getElementById('clapperTop');
    const dateEl = document.getElementById('clapperDate');
    
    if (overlay) {
        dateEl.textContent = new Date().toLocaleDateString();
        clapperTop.classList.remove('animating');
        overlay.classList.add('active');
        
        // Trigger animation after a small delay
        setTimeout(() => {
            clapperTop.classList.add('animating');
            
            // Sync sound with "snap" at 35% of 1.4s = ~490ms
            setTimeout(() => {
                playClapSound();
                createDust();
            }, 490);
        }, 100);
    }
}

function hideClapper() {
    const overlay = document.getElementById('clapperOverlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

window.showClapper = showClapper;
window.hideClapper = hideClapper;
</script>
""", unsafe_allow_html=True)

# Helper: Load Models
@st.cache_resource
def load_premium_artifacts():
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        rating_model = joblib.load(os.path.join(BASE_DIR, "models", "rating_model_pro.joblib"))
        collection_model = joblib.load(os.path.join(BASE_DIR, "models", "collection_model_pro.joblib"))
        success_model = joblib.load(os.path.join(BASE_DIR, "models", "success_model_pro.joblib"))
        metadata = joblib.load(os.path.join(BASE_DIR, "models", "metadata_pro.joblib"))
        return rating_model, collection_model, success_model, metadata
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None, None, None, None

rating_model, collection_model, success_model, metadata = load_premium_artifacts()

# Header Section
st.markdown('<h1 class="shining-title">CINERATE AI</h1>', unsafe_allow_html=True)

# Cinematic Banner
st.markdown("""
<div class="cinematic-banner">
    <span style="font-size: 1.5rem;">🎬</span>
    <h2>🎯 AI-Powered Movie Analytics Dashboard</h2>
    <span style="font-size: 1.5rem;">🍿</span>
</div>
""", unsafe_allow_html=True)

# Sidebar Inputs
with st.sidebar:
    st.markdown('<div class="sidebar-header">🎬 MOVIE PARAMETERS</div>', unsafe_allow_html=True)
    
    genre = st.selectbox("Genre", metadata['genres'])
    industry = st.selectbox("Industry", metadata['industries'])
    release_month = st.selectbox("Release Month", metadata['months'])
    
    st.markdown("---")
    budget = st.number_input("Budget ($ Millions)", min_value=1.0, max_value=500.0, value=50.0)
    runtime = st.number_input("Runtime (Mins)", min_value=30, max_value=300, value=120)
    
    st.markdown("---")
    st.markdown('<div class="sidebar-header">🎬 ADVANCED INPUTS</div>', unsafe_allow_html=True)

    cast_name = st.text_input("Lead Actor/Actress", value="")
    
    st.markdown('<div class="custom-label-wrapper"><div class="custom-label"><i class="fa-solid fa-eye icon-glow cyan"></i> Trailer Views (M)</div></div>', unsafe_allow_html=True)
    trailer_views = st.number_input("Trailer Views (M)", min_value=0.0, max_value=1000.0, value=50.0, label_visibility="collapsed")
    
    st.markdown('<div class="custom-label-wrapper"><div class="custom-label"><i class="fa-solid fa-heart icon-glow pink"></i> Trailer Likes (Lakhs)</div></div>', unsafe_allow_html=True)
    trailer_likes = st.number_input("Trailer Likes (Lakhs)", min_value=0.0, max_value=100.0, value=5.0, label_visibility="collapsed")

    st.markdown('<div class="custom-label-wrapper"><div class="custom-label"><i class="fa-solid fa-star icon-glow gold"></i> Star Power Index</div></div>', unsafe_allow_html=True)
    star_power = st.slider("Star Power Index", 0.0, 1.0, 0.5, label_visibility="collapsed")
    
    st.markdown('<div class="custom-label-wrapper"><div class="custom-label"><i class="fa-solid fa-film icon-glow purple"></i> Director Popularity</div></div>', unsafe_allow_html=True)
    director_pop = st.slider("Director Popularity", 0.0, 1.0, 0.5, label_visibility="collapsed")
    
    st.markdown('<div class="custom-label-wrapper"><div class="custom-label"><i class="fa-solid fa-bullhorn icon-glow cyan"></i> Social Buzz Index</div></div>', unsafe_allow_html=True)
    social_buzz = st.slider("Social Buzz Index", 0.0, 1.0, 0.5, label_visibility="collapsed")
    
    st.markdown('<div class="custom-label-wrapper"><div class="custom-label"><i class="fa-solid fa-file-lines icon-glow purple"></i> Estimated Critic Score</div></div>', unsafe_allow_html=True)
    critic_score = st.slider("Estimated Critic Score", 0, 100, 70, label_visibility="collapsed")

    st.markdown("""
    <style>
    .stButton > button {
        background: linear-gradient(135deg, #00f2ff 0%, #7d2ae8 50%, #ff3366 100%);
        background-size: 200% 200%;
        color: white;
        border: none;
        padding: 1.2rem 1.5rem;
        border-radius: 16px;
        font-weight: 700;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: all 0.4s ease;
        width: 100%;
        margin-top: 1.5rem;
        animation: gradient-shift 3s ease infinite;
    }
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .stButton > button:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 15px 35px rgba(0, 242, 255, 0.4), 0 0 30px rgba(125, 42, 232, 0.3);
    }
    .stButton > button::before {
        content: '⚡ ';
    }
    </style>
    """, unsafe_allow_html=True)
    predict_btn = st.button("RUN AI PREDICTION")

# Main Content Area
if predict_btn:
    st.markdown('<script>showClapper();</script>', unsafe_allow_html=True)
    time.sleep(1.8) # Wait for animation (1.4s) + buffer

    with st.spinner("🧠 AI Engine processing metadata and market trends..."):
        time.sleep(1.5) # Smooth loading feel
        
        # Prepare Input
        input_data = pd.DataFrame({
            'genre': [genre],
            'industry': [industry],
            'budget': [budget],
            'runtime': [runtime],
            'star_power': [star_power],
            'director_popularity': [director_pop],
            'social_buzz': [social_buzz],
            'critic_score': [critic_score],
            'release_month': [release_month]
        })
        
        # Run Predictions
        try:
            preds = rating_model.predict(input_data)
            rating_pred = float(preds[0])
            collection_pred_usd = float(collection_model.predict(input_data)[0])
            
            USD_TO_INR = 83.0
            collection_pred_inr = collection_pred_usd * USD_TO_INR
            
            def format_inr(amount):
                if amount >= 1000:
                    return f"₹{amount/1000:.2f} Billion"
                else:
                    return f"₹{amount:.2f} Cr"
            
            collection_display = format_inr(collection_pred_inr)
            
            # Success Probability Logic
            probability = (rating_pred / 10) * 100
            probability = max(0, min(probability, 100))
            success_prob = probability / 100.0
            
            # Market Outlook Logic (Smash/Fade/Midrun format)
            if collection_pred_inr > 300 * USD_TO_INR:
                success_label = "Blockbuster"
            elif collection_pred_inr > 150 * USD_TO_INR:
                success_label = "Smash"
            elif collection_pred_inr > 50 * USD_TO_INR:
                success_label = "Midrun"
            else:
                success_label = "Fade"
                
        except Exception as e:
            rating_pred = 0.0
            collection_display = "₹0 Cr"
            success_prob = 0.5
            success_label = "N/A"
        
        # 1. Prediction Results Row
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        res_col1, res_col2, res_col3 = st.columns(3)
        
        with res_col1:
            st.markdown(f"""
                <div class="result-card">
                    <div class="metric-icon">👥</div>
                    <div class="metric-label">Audience Score</div>
                    <div class="metric-value neon-cyan">{rating_pred:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
            
        with res_col2:
            st.markdown(f"""
                <div class="result-card">
                    <div class="metric-icon">💰</div>
                    <div class="metric-label">Estimated Collection</div>
                    <div class="metric-value neon-purple" style="font-size: 2.8rem;">{collection_display}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with res_col3:
            status_color = "#ffd700" if success_label == "BLOCKBUSTER" else ("#00f2ff" if success_label == "SMASH" else ("#7d2ae8" if success_label == "MIDRUN" else "#ff3366"))
            st.markdown(f"""
                <div class="result-card">
                    <div class="metric-icon">🎯</div>
                    <div class="metric-label">Market Outlook</div>
                    <div class="metric-value" style="color: {status_color}; font-size: 2.5rem;">{success_label}</div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 2. Charts Section
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center; margin-bottom: 1.5rem;'>🎬 Cinematic Outlook</h3>", unsafe_allow_html=True)
            
            # Dynamic Movie-Style Image Logic
            if rating_pred >= 8:
                img_url = "https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&w=800&q=80"
                img_caption = "🔥 Blockbuster Potential"
            elif rating_pred >= 6:
                img_url = "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=800&q=80"
                img_caption = "⚡ Hit Movie Vibes"
            elif rating_pred >= 4:
                img_url = "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?auto=format&fit=crop&w=800&q=80"
                img_caption = "⚠️ Risky Territory"
            else:
                img_url = "https://images.unsplash.com/photo-1594909122845-11baa439b7bf?auto=format&fit=crop&w=800&q=80"
                img_caption = "🛑 Low Interest"
            
            st.markdown("""
                <style>
                    .stImage > img {
                        border-radius: 15px;
                        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
                        border: 1px solid rgba(0, 242, 255, 0.2);
                    }
                </style>
            """, unsafe_allow_html=True)
            st.image(img_url, use_container_width=True)
            st.markdown(f"""
                <div style="text-align: center; margin-top: 15px; color: #94a3b8; font-weight: 600; font-size: 1.1rem;">
                    {img_caption}
                </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with chart_col2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center; margin-bottom: 1.5rem;'>⭐ Factor Impact Analysis</h3>", unsafe_allow_html=True)
            # Feature impact visual
            features = ['Star Power', 'Social Buzz', 'Critic Score', 'Budget']
            impacts = [star_power * 10, social_buzz * 10, critic_score / 10, budget / 30]
            
            fig_impact = px.line_polar(
                r=impacts,
                theta=features,
                line_close=True,
                color_discrete_sequence=['#00f2ff']
            )
            fig_impact.update_traces(fill='toself', fillcolor='rgba(0, 242, 255, 0.3)')
            fig_impact.update_layout(
                polar=dict(
                    bgcolor='rgba(0,0,0,0)',
                    radialaxis=dict(visible=True, range=[0, 10], gridcolor="rgba(255,255,255,0.1)"),
                    angularaxis=dict(gridcolor="rgba(255,255,255,0.1)")
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': "white", 'family': "Poppins"},
                margin=dict(l=50, r=50, t=50, b=50)
            )
            st.plotly_chart(fig_impact, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # 3. Advanced Analytics Section
        st.markdown('<div class="glass-card" style="margin-top: 2rem;">', unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; margin-bottom: 2rem;'>💰 Advanced Commercial Analysis</h3>", unsafe_allow_html=True)
        
        # Budget Conversion
        budget_inr_cr = budget * 8.3  # 1M USD = 8.3 Crore INR
        budget_inr = budget_inr_cr * 10**7
        
        # Collection Conversion to Crores
        total_collection_cr = (collection_pred_usd * 83.0) / 10
        
        # Budget vs Collection Analysis
        profit_loss_cr = total_collection_cr - budget_inr_cr
        roi_pct = (profit_loss_cr / budget_inr_cr) * 100 if budget_inr_cr > 0 else 0
        
        profit_display = f"₹{profit_loss_cr:.1f} Cr" if profit_loss_cr >= 0 else f"-₹{abs(profit_loss_cr):.1f} Cr"
        roi_display = f"{roi_pct:.1f}%"
        
        # Risk Meter Calculation
        risk_score = 30 + (1 - star_power) * 20 + social_buzz * 10 + (budget / 500) * 20
        risk_score = min(100, max(0, risk_score))
        
        if risk_score < 35:
            risk_level = "LOW RISK"
            risk_color = "#00ff88"
        elif risk_score < 65:
            risk_level = "MEDIUM RISK"
            risk_color = "#ffd700"
        else:
            risk_level = "HIGH RISK"
            risk_color = "#ff3366"
        
        # Cast Impact Score
        if cast_name:
            cast_base = hash(cast_name) % 40 + 50
            cast_score_final = min(100, cast_base + int(star_power * 30) + int(social_buzz * 20))
        else:
            cast_score_final = int(star_power * 80) + 20
        
        # Release Timing Analysis
        festival_months = [1, 3, 4, 5, 10, 11, 12]
        diwali_holidays = [10, 11]
        clash_risk_months = [1, 5, 10]
        
        if release_month in festival_months:
            timing_status = "EXCELLENT TIMING 🎉"
            timing_color = "#00ff88"
            timing_boost = 15
        elif release_month in clash_risk_months:
            timing_status = "RISKY RELEASE ⚠️"
            timing_color = "#ff3366"
            timing_boost = -10
        else:
            timing_status = "AVERAGE TIMING"
            timing_color = "#ffd700"
            timing_boost = 0
        
        # Genre Trend Analysis
        genre_trends = {
            "Action": ("🔥 Trending", "#ff3366"),
            "Comedy": ("👍 Stable", "#00ff88"),
            "Drama": ("👍 Stable", "#00ff88"),
            "Horror": ("📉 Declining", "#ff6b6b"),
            "Romance": ("👍 Stable", "#00ff88"),
            "Thriller": ("🔥 Trending", "#ff3366"),
            "Sci-Fi": ("🔥 Trending", "#ff3366"),
            "Animation": ("🔥 Trending", "#ff3366"),
        }
        trend_status, trend_color = genre_trends.get(genre, ("👍 Stable", "#00ff88"))
        
        # AI Confidence Score
        ai_confidence = min(95, 60 + int(star_power * 20) + int(director_pop * 15) + int(social_buzz * 10))
        
        # Similar Movies Reference
        similar_movies_db = {
            "Action": ["KGF", "Leo", "Jailer", "RRR"],
            "Comedy": ["Bhool Bhulaiyaa", "Welcome", "Golmaal"],
            "Drama": ["12th Fail", "Dangal", "PK"],
            "Horror": ["Bhool Bhulaiyaa 2", "Raaz", "Tumbbad"],
            "Romance": ["Laila", "Rockstar", "Aashiqui 2"],
            "Thriller": ["Drishyam", "Andhadhun", "Talaash"],
            "Sci-Fi": ["Adipurush", "Robot", "Enthiran"],
            "Animation": ["Baahubali", "Hanuman", "Mufasa"],
        }
        similar_movies = similar_movies_db.get(genre, ["KGF", "Leo", "Jailer"])[:3]
        
        # Trailer Hype Meter
        hype_score = min(100, int((trailer_views / 100) * 40 + (trailer_likes / 10) * 60))
        
        # Region-wise Collection Split
        tamil_share, roi_share, overseas_share = 0.20, 0.55, 0.25
        
        if total_collection_cr > 0:
            tamil_collection_display = f"₹{total_collection_cr * tamil_share:.1f} Cr"
            roi_collection_display = f"₹{total_collection_cr * roi_share:.1f} Cr"
            overseas_collection_display = f"₹{total_collection_cr * overseas_share:.1f} Cr"
        else:
            tamil_collection_display = "No data"
            roi_collection_display = "No data"
            overseas_collection_display = "No data"
        
        # Break-even Indicator
        break_even = budget_inr_cr
        break_even_safe = total_collection_cr > break_even * 1.5
        break_even_status = "Safe ✅" if break_even_safe else "Risky ⚠️"
        
        # Display Advanced Analytics Cards
        adv_col1, adv_col2, adv_col3 = st.columns(3)
        
        with adv_col1:
            st.markdown(f"""
                <div class="result-card" style="background: linear-gradient(135deg, rgba(0,255,136,0.1), rgba(0,242,255,0.1));">
                    <div class="metric-icon">💰</div>
                    <div class="metric-label">Budget vs Collection</div>
                    <div style="margin-top: 1rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="color: #94a3b8;">Budget:</span>
                            <span style="color: white;">₹{budget_inr_cr:.1f} Cr</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="color: #94a3b8;">Collection:</span>
                            <span style="color: white;">₹{total_collection_cr:.1f} Cr</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="color: #94a3b8;">Profit:</span>
                            <span style="color: {'#00ff88' if profit_loss_cr >= 0 else '#ff3366'};">{profit_display}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color: #94a3b8;">ROI:</span>
                            <span style="color: {'#00ff88' if roi_pct >= 0 else '#ff3366'};">{roi_display}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        with adv_col2:
            st.markdown(f"""
                <div class="result-card" style="background: linear-gradient(135deg, rgba(255,51,102,0.1), rgba(255,215,0,0.1));">
                    <div class="metric-icon">🎯</div>
                    <div class="metric-label">Risk Meter</div>
                    <div style="margin-top: 1rem;">
                        <div style="font-size: 1.8rem; color: {risk_color}; font-weight: 700; text-align: center;">{risk_level}</div>
                        <div style="margin-top: 1rem; height: 12px; background: rgba(255,255,255,0.1); border-radius: 6px; overflow: hidden;">
                            <div style="width: {risk_score}%; height: 100%; background: {risk_color}; border-radius: 6px; transition: width 1s ease;"></div>
                        </div>
                        <div style="text-align: center; margin-top: 0.5rem; color: #94a3b8; font-size: 0.9rem;">Score: {risk_score:.0f}/100</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        with adv_col3:
            st.markdown(f"""
                <div class="result-card" style="background: linear-gradient(135deg, rgba(255,215,0,0.1), rgba(125,42,232,0.1));">
                    <div class="metric-icon">🎭</div>
                    <div class="metric-label">Cast Impact Score</div>
                    <div style="margin-top: 1rem; text-align: center;">
                        <div style="font-size: 2.5rem; color: #ffd700;">⭐</div>
                        <div style="font-size: 2.2rem; color: #ffd700; font-weight: 700;">{cast_score_final}/100</div>
                        <div style="color: #94a3b8; font-size: 0.9rem; margin-top: 0.5rem;">Star Power Index</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        adv_col4, adv_col5, adv_col6 = st.columns(3)
        
        with adv_col4:
            st.markdown(f"""
                <div class="result-card" style="background: linear-gradient(135deg, rgba(0,242,255,0.1), rgba(0,255,136,0.1));">
                    <div class="metric-icon">📅</div>
                    <div class="metric-label">Release Timing</div>
                    <div style="margin-top: 1rem; text-align: center;">
                        <div style="font-size: 1.5rem; color: {timing_color}; font-weight: 700;">{timing_status}</div>
                        <div style="color: #94a3b8; font-size: 0.9rem; margin-top: 0.5rem;">{release_month} Month</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        with adv_col5:
            st.markdown(f"""
                <div class="result-card" style="background: linear-gradient(135deg, rgba(255,51,102,0.1), rgba(255,215,0,0.1));">
                    <div class="metric-icon">🎥</div>
                    <div class="metric-label">Genre Trend</div>
                    <div style="margin-top: 1rem; text-align: center;">
                        <div style="font-size: 1.3rem; color: {trend_color}; font-weight: 700;">{trend_status}</div>
                        <div style="color: #94a3b8; font-size: 0.9rem; margin-top: 0.5rem;">{genre}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        with adv_col6:
            st.markdown(f"""
                <div class="result-card" style="background: linear-gradient(135deg, rgba(125,42,232,0.1), rgba(0,242,255,0.1));">
                    <div class="metric-icon">🤖</div>
                    <div class="metric-label">AI Confidence</div>
                    <div style="margin-top: 1rem; text-align: center;">
                        <div style="font-size: 2.2rem; color: #00f2ff; font-weight: 700;">{ai_confidence}%</div>
                        <div style="margin-top: 0.5rem; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden;">
                            <div style="width: {ai_confidence}%; height: 100%; background: linear-gradient(90deg, #00f2ff, #7d2ae8); border-radius: 4px;"></div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        # Second Row - Additional Analytics
        adv2_col1, adv2_col2, adv2_col3 = st.columns(3)
        
        with adv2_col1:
            st.markdown(f"""
                <div class="result-card" style="background: linear-gradient(135deg, rgba(255,215,0,0.1), rgba(255,51,102,0.1));">
                    <div class="metric-icon">🎞</div>
                    <div class="metric-label">Similar Movies</div>
                    <div style="margin-top: 1rem; text-align: center;">
                        <div style="color: #00f2ff; font-size: 1.1rem; font-weight: 600;">{', '.join(similar_movies)}</div>
                        <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 0.5rem;">Based on {genre} genre</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        with adv2_col2:
            st.markdown(f"""
                <div class="result-card" style="background: linear-gradient(135deg, rgba(0,255,136,0.1), rgba(0,242,255,0.1));">
                    <div class="metric-icon">🚀</div>
                    <div class="metric-label">Trailer Hype Meter</div>
                    <div style="margin-top: 1rem;">
                        <div style="font-size: 2rem; color: #00ff88; font-weight: 700; text-align: center;">{hype_score}/100</div>
                        <div style="margin-top: 0.5rem; height: 10px; background: rgba(255,255,255,0.1); border-radius: 5px; overflow: hidden;">
                            <div style="width: {hype_score}%; height: 100%; background: linear-gradient(90deg, #00ff88, #00f2ff, #7d2ae8); border-radius: 5px;"></div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; color: #94a3b8; font-size: 0.8rem;">
                            <span>Views: {trailer_views}M</span>
                            <span>Likes: {trailer_likes}L</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        with adv2_col3:
            st.markdown(f"""
                <div class="result-card" style="background: linear-gradient(135deg, rgba(125,42,232,0.1), rgba(255,215,0,0.1));">
                    <div class="metric-icon">💼</div>
                    <div class="metric-label">Break-even Indicator</div>
                    <div style="margin-top: 1rem; text-align: center;">
                        <div style="font-size: 1.4rem; color: white; font-weight: 600;">₹{break_even:.1f} Cr</div>
                        <div style="color: {'#00ff88' if break_even_safe else '#ff3366'}; font-size: 1rem; font-weight: 700; margin-top: 0.5rem;">{break_even_status}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        # Region-wise Collection Split
        st.markdown("<h3 style='text-align: center; margin: 2rem 0 1.5rem;'>🌍 Region-wise Collection Split</h3>", unsafe_allow_html=True)
        
        region_col1, region_col2, region_col3 = st.columns(3)
        
        with region_col1:
            st.markdown(f"""
                <div class="result-card" style="background: linear-gradient(135deg, rgba(255,51,102,0.15), rgba(255,51,102,0.05)); border: 1px solid rgba(255,51,102,0.3);">
                    <div style="text-align: center;">
                        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🇮🇳</div>
                        <div class="metric-label">Tamil Nadu</div>
                        <div style="font-size: 1.8rem; color: #ff3366; font-weight: 700;">{tamil_collection_display}</div>
                        <div style="color: #94a3b8; font-size: 0.85rem;">{tamil_share * 100:.0f}% share</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        with region_col2:
            st.markdown(f"""
                <div class="result-card" style="background: linear-gradient(135deg, rgba(0,242,255,0.15), rgba(0,242,255,0.05)); border: 1px solid rgba(0,242,255,0.3);">
                    <div style="text-align: center;">
                        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🇮🇳</div>
                        <div class="metric-label">Rest of India</div>
                        <div style="font-size: 1.8rem; color: #00f2ff; font-weight: 700;">{roi_collection_display}</div>
                        <div style="color: #94a3b8; font-size: 0.85rem;">{roi_share * 100:.0f}% share</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        with region_col3:
            st.markdown(f"""
                <div class="result-card" style="background: linear-gradient(135deg, rgba(125,42,232,0.15), rgba(125,42,232,0.05)); border: 1px solid rgba(125,42,232,0.3);">
                    <div style="text-align: center;">
                        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🌍</div>
                        <div class="metric-label">Overseas</div>
                        <div style="font-size: 1.8rem; color: #7d2ae8; font-weight: 700;">{overseas_collection_display}</div>
                        <div style="color: #94a3b8; font-size: 0.85rem;">{overseas_share * 100:.0f}% share</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<script>hideClapper();</script>', unsafe_allow_html=True)

else:
    st.markdown('<div class="glass-card hero-section">', unsafe_allow_html=True)
    st.markdown('<div class="hero-icons">🎬 🍿 ⭐ 🎥</div>', unsafe_allow_html=True)
    st.markdown("""
        <h2 style="font-weight: 700; font-size: 2rem; margin-bottom: 1rem;">Welcome to the Premium Suite</h2>
        <p style="color: #94a3b8; font-size: 1.2rem; max-width: 600px; margin: 0 auto;">
            Configure your movie parameters in the sidebar and trigger the
            AI engine to generate predictive intelligence and commercial analysis.
        </p>
        <div style="margin-top: 2rem; font-size: 3rem;">🎬</div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; margin-top: 4rem; padding: 2rem; color: #475569; font-size: 0.9rem; border-top: 1px solid rgba(255,255,255,0.05);">
        🎬 © 2026 CINERATE AI PLATFORM • ENTERPRISE GRADE INTELLIGENCE 🍿
    </div>
""", unsafe_allow_html=True)
