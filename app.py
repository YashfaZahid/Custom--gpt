import json
import os
import uuid
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv, set_key, unset_key
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

APP_NAME = "Origin"
APP_TAGLINE = "Classical Precision • Autonomous Reasoning"

BASE_DIR = Path(__file__).parent
ENV_PATH = BASE_DIR / ".env"
HISTORY_PATH = BASE_DIR / "chats.json"

st.set_page_config(
    page_title=f"{APP_NAME} | Intelligence",
    page_icon="Ø",
    layout="centered",
    initial_sidebar_state="expanded",
)

load_dotenv(ENV_PATH, override=True)

USER_AVATAR = "user"
ASSISTANT_AVATAR = "assistant"


def html_block(s: str) -> str:
    """Strip indentation/blank lines so Markdown never treats HTML as a code block."""
    return "\n".join(line.strip() for line in s.splitlines() if line.strip())


# Inline vector mark (no image files are used anywhere in this app)
LOGO_HTML = html_block(
    """<svg class="brand-mark" width="30" height="30" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs><linearGradient id="markGrad" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
    <stop stop-color="#FFFFFF"/><stop offset="1" stop-color="#8E939E"/></linearGradient></defs>
    <circle cx="16" cy="16" r="12" stroke="url(#markGrad)" stroke-width="2.2"/>
    <path d="M8 21L24 11" stroke="url(#markGrad)" stroke-width="2.2" stroke-linecap="round"/></svg>"""
)


# =============================================================================
# CHARCOAL GRADIENT PREMIUM THEME
# =============================================================================
STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg-0: #0a0b0d;
    --bg-1: #111215;
    --bg-2: #181a1e;
    --bg-3: #20232a;
    --line: rgba(255, 255, 255, 0.07);
    --line-strong: rgba(255, 255, 255, 0.15);
    --text: #f3f4f6;
    --text-2: #9a9fa9;
    --text-3: #646873;
    --platinum: #e8eaee;
    --platinum-grad: linear-gradient(180deg, #f6f7f9 0%, #c5c9d1 100%);
    --glow: rgba(214, 190, 205, 0.14);
    --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --font-mono: 'JetBrains Mono', Consolas, monospace;
    --r-sm: 6px;
    --r-md: 10px;
    --r-lg: 14px;
    --ease: cubic-bezier(0.2, 0.7, 0.2, 1);
}

/* ---------------- Animations ---------------- */
@keyframes gradientShift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
@keyframes orbDrift {
    0%   { transform: translate3d(0, 0, 0) scale(1); }
    50%  { transform: translate3d(2.5%, -3%, 0) scale(1.06); }
    100% { transform: translate3d(-3%, 2.5%, 0) scale(1.02); }
}
@keyframes riseIn { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }
@keyframes slideDown { from { opacity: 0; transform: translateY(-14px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes pulseDot { 0%, 100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.55); } 50% { box-shadow: 0 0 0 6px rgba(34, 197, 94, 0); } }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes ringPulse { 0% { transform: translate(-50%, -50%) scale(0.85); opacity: 0.0; } 30% { opacity: 0.9; } 100% { transform: translate(-50%, -50%) scale(1.5); opacity: 0; } }
@keyframes textShimmer { 0% { background-position: 0% 50%; } 100% { background-position: 200% 50%; } }
@keyframes sheen { 0% { left: -60%; } 55%, 100% { left: 140%; } }
@keyframes floatY { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
@keyframes breathe { 0%, 100% { opacity: 0.55; } 50% { opacity: 1; } }
@keyframes lineSweep { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation: none !important; transition: none !important; }
}

::selection { background: rgba(232, 234, 238, 0.25); color: #fff; }

/* ---------------- Canvas: animated charcoal gradient ---------------- */
.stApp {
    background: linear-gradient(135deg, #0a0b0d 0%, #121417 38%, #1c1b20 62%, #2a0f1b 90%, #14080d 100%) !important;
    background-size: 220% 220% !important;
    animation: gradientShift 28s ease-in-out infinite;
    color: var(--text) !important;
    font-family: var(--font-sans) !important;
    -webkit-font-smoothing: antialiased;
}

/* Soft drifting light */
.stApp::before {
    content: "";
    position: fixed;
    inset: -10%;
    pointer-events: none;
    z-index: 0;
    background:
        radial-gradient(620px circle at 15% 20%, rgba(190, 198, 214, 0.075), transparent 60%),
        radial-gradient(720px circle at 85% 78%, rgba(140, 40, 80, 0.11), transparent 60%),
        radial-gradient(520px circle at 62% 8%, rgba(255, 255, 255, 0.035), transparent 60%);
    animation: orbDrift 34s ease-in-out infinite alternate;
}

/* Brushed-metal texture + vignette (pure CSS, no images) */
.stApp::after {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    background:
        radial-gradient(ellipse at center, transparent 55%, rgba(0, 0, 0, 0.5) 100%),
        repeating-linear-gradient(115deg, rgba(255, 255, 255, 0.012) 0 1px, transparent 1px 3px);
}

[data-testid="stAppViewContainer"] { position: relative; z-index: 1; background: transparent !important; }
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer { visibility: hidden; }

.block-container {
    max-width: 840px;
    padding-top: 1.6rem;
    padding-bottom: 7.5rem;
    position: relative;
    z-index: 1;
}

/* ---------------- Top bar ---------------- */
.top-nav {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.8rem 1.25rem;
    background: linear-gradient(145deg, #1d1f24, #111215);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid var(--line);
    border-radius: var(--r-md);
    margin-bottom: 1.8rem;
    box-shadow: 0 10px 34px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.05);
    overflow: hidden;
    animation: slideDown 0.7s var(--ease) both;
}
.top-nav::after {
    content: "";
    position: absolute;
    left: 0; right: 0; bottom: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.55), transparent);
    animation: lineSweep 5s ease-in-out infinite;
}
.brand-wrapper { display: flex; align-items: center; gap: 12px; }
.brand-info { display: flex; align-items: center; gap: 9px; }
/* Animated brand mark: orbiting ring + drawing slash + soft glow */
.brand-mark { overflow: visible; transition: transform 0.6s var(--ease); animation: logoGlow 3.6s ease-in-out infinite; }
.top-nav:hover .brand-mark { transform: rotate(180deg); }
.brand-mark circle { transform-box: view-box; transform-origin: 16px 16px; stroke-dasharray: 58 17.4; animation: logoOrbit 9s linear infinite; }
.brand-mark path { stroke-dasharray: 20; animation: logoSlash 3.6s ease-in-out infinite; }
.auth-logo-box svg { animation: boltPulse 3s ease-in-out infinite; }
@keyframes logoOrbit { to { transform: rotate(360deg); } }
@keyframes logoSlash {
    0%   { stroke-dashoffset: 20;  opacity: 0.35; }
    35%  { stroke-dashoffset: 0;   opacity: 1; }
    75%  { stroke-dashoffset: 0;   opacity: 1; }
    100% { stroke-dashoffset: -20; opacity: 0.35; }
}
@keyframes logoGlow {
    0%, 100% { filter: drop-shadow(0 0 0 rgba(255, 255, 255, 0)); }
    50%      { filter: drop-shadow(0 0 7px rgba(255, 255, 255, 0.45)); }
}
@keyframes boltPulse {
    0%, 100% { transform: scale(1);    filter: drop-shadow(0 0 0 rgba(255, 255, 255, 0)); }
    50%      { transform: scale(1.12); filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.55)); }
}
.brand-title {
    font-size: 1.1rem; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: #fff; margin: 0;
}
.badge-tag {
    font-size: 0.62rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase;
    padding: 2px 8px; border-radius: 4px;
    background: linear-gradient(180deg, #2a2d34, #1b1d22);
    border: 1px solid var(--line-strong); color: var(--platinum);
}
.status-cluster { display: flex; align-items: center; gap: 12px; }
.status-pill {
    display: flex; align-items: center; gap: 7px;
    font-size: 0.76rem; font-weight: 500; color: var(--text-2);
    background: rgba(255, 255, 255, 0.03); border: 1px solid var(--line);
    padding: 3px 10px; border-radius: 4px;
}
.status-dot {
    width: 6px; height: 6px; background-color: #22c55e; border-radius: 50%;
    display: inline-block; animation: pulseDot 2.2s infinite;
}
.model-pill {
    font-size: 0.74rem; font-weight: 600; color: #fff;
    background: linear-gradient(180deg, #23262c, #17181c);
    border: 1px solid var(--line-strong);
    padding: 3px 10px; border-radius: 4px; letter-spacing: 0.03em;
}

/* ---------------- Hero ---------------- */
.hero-container { text-align: center; padding: 1.6rem 1.5rem 1.6rem; animation: fadeIn 0.9s ease both; }
.hero-emblem {
    position: relative; width: 84px; height: 84px; margin: 0 auto 1.4rem;
    display: flex; align-items: center; justify-content: center;
    animation: floatY 6s ease-in-out infinite;
}
.hero-emblem::before {
    content: ""; position: absolute; inset: 0; border-radius: 50%;
    background: conic-gradient(from 0deg, rgba(255,255,255,0.0), rgba(255,255,255,0.75), rgba(255,255,255,0.0) 70%);
    -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 2px), #000 calc(100% - 1px));
            mask: radial-gradient(farthest-side, transparent calc(100% - 2px), #000 calc(100% - 1px));
    animation: spin 7s linear infinite;
}
.hero-emblem::after {
    content: ""; position: absolute; inset: 9px; border-radius: 50%;
    background: radial-gradient(circle at 35% 30%, #2b2e35, #121316 70%);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 0 40px var(--glow);
}
.hero-emblem .glyph {
    position: relative; z-index: 2; font-size: 1.9rem; font-weight: 300; color: var(--platinum);
}
.hero-pill {
    display: inline-flex; align-items: center; gap: 8px;
    font-size: 0.72rem; font-weight: 600; color: var(--text-2);
    background: rgba(255, 255, 255, 0.03); border: 1px solid var(--line);
    padding: 5px 13px; border-radius: 999px; margin-bottom: 1.2rem;
    letter-spacing: 0.12em; text-transform: uppercase;
    animation: riseIn 0.8s var(--ease) 0.1s both;
}
.pill-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--platinum); animation: breathe 2.4s ease-in-out infinite; }
.hero-container h1 {
    font-size: 2.55rem; font-weight: 700; letter-spacing: -0.03em; line-height: 1.15; margin: 0 0 0.9rem;
    background: linear-gradient(100deg, #8d929d 0%, #ffffff 25%, #b8bcc6 50%, #ffffff 75%, #8d929d 100%);
    background-size: 200% auto;
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent; color: transparent;
    animation: riseIn 0.8s var(--ease) 0.2s both, textShimmer 7s linear 1s infinite;
}
.hero-container p {
    font-size: 1rem; color: var(--text-2); max-width: 520px; margin: 0 auto 2rem; line-height: 1.65;
    animation: riseIn 0.8s var(--ease) 0.3s both;
}
.prompt-grid-label {
    font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em;
    color: var(--text-3); margin-bottom: 0.75rem; text-align: left;
    animation: fadeIn 1s ease 0.4s both;
}

/* Starter cards */
.st-key-starter_1 button, .st-key-starter_2 button, .st-key-starter_3 button, .st-key-starter_4 button {
    text-align: left !important;
    background: linear-gradient(145deg, #1d1f24, #121316) !important;
    border: 1px solid var(--line) !important;
    border-radius: var(--r-md) !important;
    padding: 0.85rem 1.1rem !important;
    height: auto !important; min-height: 72px !important; max-height: 84px !important;
    overflow: hidden !important;
    display: flex !important; flex-direction: column !important; justify-content: center !important;
    transition: transform 0.3s var(--ease), border-color 0.3s ease, box-shadow 0.3s ease, background 0.3s ease !important;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.04) !important;
}
.st-key-starter_1, .st-key-starter_2, .st-key-starter_3, .st-key-starter_4 { animation: riseIn 0.8s var(--ease) both; }
.st-key-starter_1 { animation-delay: 0.35s; }
.st-key-starter_2 { animation-delay: 0.45s; }
.st-key-starter_3 { animation-delay: 0.55s; }
.st-key-starter_4 { animation-delay: 0.65s; }
.st-key-starter_1 button *, .st-key-starter_2 button *, .st-key-starter_3 button *, .st-key-starter_4 button * {
    overflow: hidden !important; text-overflow: ellipsis !important; white-space: pre-line !important; scrollbar-width: none !important;
}
.st-key-starter_1 button p, .st-key-starter_2 button p, .st-key-starter_3 button p, .st-key-starter_4 button p {
    text-align: left !important; color: #fff !important; font-size: 0.85rem !important; line-height: 1.45 !important;
}
.st-key-starter_1 button:hover, .st-key-starter_2 button:hover, .st-key-starter_3 button:hover, .st-key-starter_4 button:hover {
    background: linear-gradient(145deg, #2b2429, #17181c) !important;
    border-color: rgba(255, 255, 255, 0.28) !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 14px 30px rgba(0, 0, 0, 0.5), 0 0 24px var(--glow) !important;
}

/* ---------------- Sidebar ---------------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0e0f12 0%, #14161a 62%, #1b0f15 100%) !important;
    border-right: 1px solid var(--line) !important;
}
/* Make the whole sidebar reliably scrollable when its content is taller than the window */
[data-testid="stSidebar"] > div:first-child { height: 100vh !important; overflow-y: auto !important; overflow-x: hidden !important; }
[data-testid="stSidebarContent"] {
    height: 100% !important;
    overflow-y: auto !important; overflow-x: hidden !important;
    padding-top: 0.75rem !important; padding-bottom: 2.5rem !important;
    scrollbar-width: thin; scrollbar-color: #4a4e59 transparent;
}
[data-testid="stSidebarUserContent"] { overflow: visible !important; padding-bottom: 2rem !important; }
[data-testid="stSidebarContent"]::-webkit-scrollbar { width: 6px; }
[data-testid="stSidebarContent"]::-webkit-scrollbar-thumb { background: #4a4e59; border-radius: 4px; }
[data-testid="stSidebarContent"]::-webkit-scrollbar-thumb:hover { background: #666b78; }

.sidebar-header { display: flex; align-items: center; gap: 12px; padding: 0.4rem 0.2rem 0.9rem; }
.sidebar-title { font-size: 1.15rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #fff; }
.sidebar-sub { font-size: 0.68rem; color: var(--text-3); letter-spacing: 0.1em; }
.sidebar-section-title {
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--text-3); margin: 0.9rem 0 0.4rem;
}

/* Generic sidebar buttons */
[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] [data-testid="stDownloadButton"] button {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid var(--line) !important;
    border-radius: var(--r-md) !important;
    padding: 0.55rem 0.9rem !important;
    transition: transform 0.25s var(--ease), background 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease !important;
}
[data-testid="stSidebar"] .stButton > button p,
[data-testid="stSidebar"] [data-testid="stDownloadButton"] button p { color: var(--text-2) !important; font-weight: 500 !important; }
[data-testid="stSidebar"] .stButton > button:hover,
[data-testid="stSidebar"] [data-testid="stDownloadButton"] button:hover {
    background: rgba(255, 255, 255, 0.07) !important;
    border-color: var(--line-strong) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stSidebar"] .stButton > button:hover p,
[data-testid="stSidebar"] [data-testid="stDownloadButton"] button:hover p { color: #fff !important; }

/* New conversation: platinum call-to-action with sheen */
[data-testid="stSidebar"] .st-key-new_chat button {
    position: relative; overflow: hidden;
    background: var(--platinum-grad) !important;
    border: 1px solid rgba(255, 255, 255, 0.5) !important;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.8) !important;
    padding: 0.7rem 1rem !important;
    justify-content: center !important;
}
[data-testid="stSidebar"] .st-key-new_chat button::after {
    content: ""; position: absolute; top: 0; bottom: 0; left: -60%; width: 40%;
    background: linear-gradient(100deg, transparent, rgba(255, 255, 255, 0.75), transparent);
    transform: skewX(-18deg);
    animation: sheen 5s ease-in-out infinite;
}
[data-testid="stSidebar"] .st-key-new_chat button p { color: #0c0d0f !important; font-weight: 700 !important; letter-spacing: 0.03em !important; text-align: center !important; }
[data-testid="stSidebar"] .st-key-new_chat button:hover {
    background: linear-gradient(180deg, #ffffff 0%, #d3d6dd 100%) !important;
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.5), 0 0 26px var(--glow) !important;
    transform: translateY(-2px) !important;
}
[data-testid="stSidebar"] .st-key-new_chat button:hover p { color: #000 !important; }

/* Conversation list */
.st-key-chat_history_box { scrollbar-width: thin; }
[data-testid="stSidebar"] .st-key-chat_history_box .stButton > button {
    text-align: left !important; justify-content: flex-start !important;
    overflow: hidden !important; text-overflow: ellipsis !important; white-space: nowrap !important;
}
[data-testid="stSidebar"] .st-key-chat_history_box .stButton > button p {
    text-align: left !important; overflow: hidden !important; text-overflow: ellipsis !important;
    white-space: nowrap !important; width: 100% !important;
}
[data-testid="stSidebar"] .st-key-chat_history_box .stButton > button:hover { transform: translateX(3px) !important; }

/* Active conversation */
[data-testid="stSidebar"] button[kind="primary"],
[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(90deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.03)) !important;
    border: 1px solid var(--line-strong) !important;
    border-left: 3px solid #fff !important;
}
[data-testid="stSidebar"] button[kind="primary"] p,
[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] p { color: #fff !important; font-weight: 600 !important; }

/* Logout */
[data-testid="stSidebar"] .st-key-logout button p { text-align: center !important; }
[data-testid="stSidebar"] .st-key-logout button:hover { border-color: rgba(248, 113, 113, 0.5) !important; }
[data-testid="stSidebar"] .st-key-logout button:hover p { color: #fca5a5 !important; }

/* Sidebar inputs */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid var(--line) !important;
    border-radius: var(--r-md) !important;
    color: #fff !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
}
[data-testid="stSidebar"] input:focus,
[data-testid="stSidebar"] textarea:focus {
    border-color: rgba(255, 255, 255, 0.6) !important;
    box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.35), 0 0 18px var(--glow) !important;
}
[data-testid="stSidebar"] .stSlider label, [data-testid="stSidebar"] .stSlider p { color: var(--text-2) !important; }
[data-testid="stSidebar"] div[role="slider"] { background-color: var(--platinum) !important; box-shadow: 0 0 12px var(--glow) !important; }
[data-testid="stSliderThumbValue"], [data-testid="stSidebar"] [data-testid="stSliderThumbValue"] { color: var(--platinum) !important; }

/* ---------------- Chat messages (avatar-free keyed bubbles) ---------------- */
/* Safety net in case any built-in chat avatar is ever rendered */
[data-testid^="stChatMessageAvatar"], [data-testid^="chatAvatarIcon"] { display: none !important; }

@keyframes bubbleInRight { from { opacity: 0; transform: translate3d(24px, 10px, 0) scale(0.97); } to { opacity: 1; transform: none; } }
@keyframes bubbleInLeft  { from { opacity: 0; transform: translate3d(-24px, 10px, 0) scale(0.97); } to { opacity: 1; transform: none; } }

[class*="st-key-msg_user_"], [class*="st-key-msg_assistant_"] {
    gap: 0.4rem !important; box-sizing: border-box !important; min-width: 0 !important;
}

/* Human: wine bubble, right side */
[class*="st-key-msg_user_"] {
    align-self: flex-end !important;
    width: fit-content !important; max-width: 78% !important;
    margin: 0.35rem 0 !important;
    padding: 0.8rem 1.3rem !important;
    background: linear-gradient(145deg, #4d2133 0%, #2f1c25 55%, #1f1a1e 100%) !important;
    border: 1px solid rgba(255, 200, 215, 0.18) !important;
    border-radius: 20px 20px 6px 20px !important;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5), 0 0 22px rgba(176, 40, 90, 0.14), inset 0 1px 0 rgba(255, 220, 230, 0.2) !important;
    animation: bubbleInRight 0.5s var(--ease) both;
    transition: transform 0.3s var(--ease), box-shadow 0.3s ease, border-color 0.3s ease !important;
}
[class*="st-key-msg_user_"]:hover {
    transform: translateY(-2px);
    border-color: rgba(255, 200, 216, 0.45) !important;
    box-shadow: 0 16px 36px rgba(0, 0, 0, 0.55), 0 0 28px rgba(196, 52, 108, 0.12), inset 0 1px 0 rgba(255, 220, 230, 0.26) !important;
}
[class*="st-key-msg_user_"] * { color: #ffffff !important; text-align: left !important; }

/* Assistant: deep wine glass bubble with a rose accent edge, left side */
[class*="st-key-msg_assistant_"] {
    position: relative; overflow: hidden;
    align-self: flex-start !important;
    width: 100% !important; max-width: 94% !important;
    margin: 0.35rem 0 0.6rem !important;
    padding: 1.15rem 1.5rem 1.15rem 1.7rem !important;
    background: linear-gradient(150deg, rgba(52, 54, 62, 0.96) 0%, rgba(32, 34, 40, 0.96) 100%) !important;
    backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 20px 20px 20px 6px !important;
    box-shadow: 0 14px 36px rgba(0, 0, 0, 0.5), 0 2px 6px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 220, 230, 0.12) !important;
    color: #f6eef1 !important;
    animation: bubbleInLeft 0.55s var(--ease) both;
    transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
}
[class*="st-key-msg_assistant_"]::before {
    content: ""; position: absolute; left: 0; top: 16px; bottom: 16px; width: 3px; border-radius: 3px;
    background: linear-gradient(180deg, #ffd3df 0%, rgba(214, 80, 120, 0.2) 100%);
    opacity: 0.85;
}
[class*="st-key-msg_assistant_"]:hover {
    border-color: rgba(255, 255, 255, 0.22) !important;
    box-shadow: 0 18px 42px rgba(0, 0, 0, 0.55), 0 0 30px rgba(196, 52, 108, 0.22), inset 0 1px 0 rgba(255, 220, 230, 0.16) !important;
}
[class*="st-key-msg_assistant_"] :is(p, li, h1, h2, h3, h4, h5, h6, strong, em, td, th, blockquote) { color: #f6eef1 !important; }
[class*="st-key-msg_assistant_"] a { color: #e8c6d2 !important; text-decoration: underline; text-underline-offset: 2px; }
[class*="st-key-msg_assistant_"] :not(pre) > code { background: rgba(255, 255, 255, 0.12) !important; color: #fbeaf0 !important; }
[class*="st-key-msg_assistant_"] pre { background: #17181c !important; border-color: rgba(255, 255, 255, 0.08) !important; border-radius: 12px !important; }
[class*="st-key-msg_assistant_"] pre code { color: #f4f4f5 !important; }
[class*="st-key-msg_assistant_"] :is(table, th, td) { border-color: rgba(255, 255, 255, 0.18) !important; }
[class*="st-key-msg_assistant_"] hr { border-color: rgba(255, 255, 255, 0.15) !important; }
[class*="st-key-msg_assistant_"] [data-testid="stSpinner"] * { color: #c3c7d0 !important; }

/* Spinner */
[data-testid="stSpinner"] { animation: breathe 1.6s ease-in-out infinite; }
[data-testid="stSpinner"] * { color: var(--text-2) !important; }

/* Code */
pre, code { font-family: var(--font-mono) !important; }
code { background: rgba(255, 255, 255, 0.08) !important; color: #e4e4e7 !important; padding: 2px 6px !important; border-radius: 4px !important; font-size: 0.88em !important; }
pre {
    background: #08090b !important; border: 1px solid var(--line) !important;
    border-radius: var(--r-md) !important; padding: 1rem !important;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4) !important;
}
pre code { background: transparent !important; color: #f4f4f5 !important; padding: 0 !important; }

/* ---------------- Chat input dock ---------------- */
[data-testid="stBottom"], [data-testid="stBottom"] > div {
    background: linear-gradient(180deg, transparent 0%, rgba(10, 11, 13, 0.97) 30%, #0a0b0d 100%) !important;
    backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
}
[data-testid="stChatInput"] {
    background: linear-gradient(145deg, #1a1c21, #121316) !important;
    border: 1px solid var(--line) !important;
    border-radius: var(--r-md) !important;
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.04) !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s var(--ease) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(255, 255, 255, 0.55) !important;
    box-shadow: 0 14px 40px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(255, 255, 255, 0.3), 0 0 30px var(--glow) !important;
    transform: translateY(-1px);
}
[data-testid="stChatInput"] > div { background: transparent !important; border: none !important; }
[data-testid="stChatInput"] textarea { color: var(--text) !important; caret-color: #fff !important; font-family: var(--font-sans) !important; font-size: 0.95rem !important; }
[data-testid="stChatInput"] textarea::placeholder { color: var(--text-3) !important; }
[data-testid="stChatInput"] button { color: #fff !important; transition: transform 0.2s ease !important; }
[data-testid="stChatInput"] button:hover { transform: scale(1.12); }

input, textarea { color: var(--text) !important; font-family: var(--font-sans) !important; }

/* Scrollbars */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2a2d34; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #3d414b; }

hr { border-color: var(--line) !important; margin: 0.85rem 0 !important; }
.stCaption { color: var(--text-3) !important; font-size: 0.75rem !important; }
</style>
"""

st.markdown(STYLE, unsafe_allow_html=True)


# =============================================================================
# LOGIN SCREEN (split card; right panel is a CSS-only animated gradient)
# =============================================================================
if not os.getenv("OPENAI_API_KEY"):
    LOGIN_STYLE = """
<style>
[data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"] { display: none !important; }

.block-container {
    max-width: 890px !important;
    padding-top: 3.5vh !important; padding-bottom: 3.5vh !important;
    min-height: 94vh !important;
    display: flex !important; flex-direction: column !important; justify-content: center !important;
    position: relative !important; z-index: 10 !important;
}

.st-key-auth_card { width: 100% !important; max-width: 860px !important; margin: 0 auto !important; box-sizing: border-box !important; animation: riseIn 0.9s var(--ease) both; }
.st-key-auth_card, .st-key-auth_card * { box-sizing: border-box !important; }
.st-key-auth_card [data-testid="stVerticalBlock"],
.st-key-auth_card [data-testid="stElementContainer"],
.st-key-auth_card [data-testid="element-container"],
.st-key-auth_card [data-testid="stTextInput"],
.st-key-auth_card [data-testid="stForm"],
.st-key-auth_card [data-testid="stFormSubmitButton"] { min-width: 0 !important; max-width: 100% !important; }

.st-key-auth_card [data-testid="stHorizontalBlock"] {
    background: linear-gradient(145deg, #181a1f, #0e0f12) !important;
    border-radius: 20px !important; overflow: hidden !important;
    box-shadow: 0 30px 70px -15px rgba(0, 0, 0, 0.9), 0 0 0 1px rgba(255, 255, 255, 0.08), 0 0 60px rgba(205, 212, 228, 0.05) !important;
    gap: 0 !important; align-items: stretch !important; min-height: 540px !important; flex-wrap: nowrap !important;
}

/* Left: form */
.st-key-auth_card :is([data-testid="column"], [data-testid="stColumn"]):nth-of-type(1) {
    background: transparent !important;
    padding: 3rem clamp(1.4rem, 3.5vw, 3rem) 2.4rem !important;
    min-width: 0 !important; flex: 1 1 0 !important; width: 50% !important;
    display: flex !important; flex-direction: column !important; justify-content: center !important;
    overflow: hidden !important;
}
.st-key-auth_card :is([data-testid="column"], [data-testid="stColumn"]):nth-of-type(1) * { font-family: var(--font-sans) !important; }

/* Right: art */
.st-key-auth_card :is([data-testid="column"], [data-testid="stColumn"]):nth-of-type(2) {
    padding: 0 !important; margin: 0 !important; background: #0b0b0d !important;
    min-width: 0 !important; flex: 1 1 0 !important; width: 50% !important;
    overflow: hidden !important; display: flex !important; align-items: stretch !important;
}
.st-key-auth_card :is([data-testid="column"], [data-testid="stColumn"]):nth-of-type(2) > div,
.st-key-auth_card :is([data-testid="column"], [data-testid="stColumn"]):nth-of-type(2) [data-testid="stVerticalBlock"],
.st-key-auth_card :is([data-testid="column"], [data-testid="stColumn"]):nth-of-type(2) [data-testid="element-container"],
.st-key-auth_card :is([data-testid="column"], [data-testid="stColumn"]):nth-of-type(2) [data-testid="stMarkdownContainer"] { height: 100% !important; width: 100% !important; }

.auth-art-box {
    position: relative; width: 100%; height: 100%; min-height: 540px; overflow: hidden;
    background: linear-gradient(160deg, #23262c 0%, #14161a 50%, #1c0d14 100%);
    background-size: 160% 160%;
    animation: gradientShift 18s ease-in-out infinite;
    display: flex; align-items: center; justify-content: center;
}
.art-grid {
    position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px);
    background-size: 42px 42px;
    -webkit-mask: radial-gradient(circle at center, #000 10%, transparent 72%);
            mask: radial-gradient(circle at center, #000 10%, transparent 72%);
}
.art-orb { position: absolute; border-radius: 50%; filter: blur(46px); opacity: 0.9; }
.art-orb-a { width: 260px; height: 260px; top: -60px; right: -60px; background: radial-gradient(circle, rgba(200, 208, 226, 0.30), transparent 70%); animation: orbDrift 14s ease-in-out infinite alternate; }
.art-orb-b { width: 300px; height: 300px; bottom: -90px; left: -80px; background: radial-gradient(circle, rgba(150, 40, 85, 0.26), transparent 70%); animation: orbDrift 18s ease-in-out infinite alternate-reverse; }
.art-ring { position: absolute; top: 50%; left: 50%; width: 220px; height: 220px; border-radius: 50%; border: 1px solid rgba(255, 255, 255, 0.22); animation: ringPulse 6s ease-out infinite; }
.art-ring:nth-of-type(2) { animation-delay: 2s; }
.art-ring:nth-of-type(3) { animation-delay: 4s; }
.art-core {
    position: relative; width: 120px; height: 120px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    background: radial-gradient(circle at 35% 30%, #343841, #121316 72%);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.12), 0 0 60px rgba(205, 212, 228, 0.18);
    font-size: 3.2rem; font-weight: 300; color: #f1f2f5;
    animation: floatY 6s ease-in-out infinite;
}
.art-core::before {
    content: ""; position: absolute; inset: -6px; border-radius: 50%;
    background: conic-gradient(from 0deg, rgba(255,255,255,0), rgba(255,255,255,0.8), rgba(255,255,255,0) 65%);
    -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 2px), #000 calc(100% - 1px));
            mask: radial-gradient(farthest-side, transparent calc(100% - 2px), #000 calc(100% - 1px));
    animation: spin 8s linear infinite;
}
.art-caption { position: absolute; left: 0; right: 0; bottom: 2rem; text-align: center; animation: riseIn 1s var(--ease) 0.5s both; }
.art-caption-title { font-size: 0.95rem; font-weight: 700; letter-spacing: 0.3em; text-transform: uppercase; color: #fff; }
.art-caption-sub { font-size: 0.72rem; color: var(--text-2); letter-spacing: 0.08em; margin-top: 0.4rem; }

.auth-logo-box { display: flex; justify-content: center; align-items: center; margin-bottom: 1rem; animation: riseIn 0.8s var(--ease) 0.15s both; }
.auth-title {
    font-size: 1.85rem !important; font-weight: 700 !important; text-align: center !important;
    letter-spacing: -0.025em !important; margin: 0 0 0.45rem 0 !important; line-height: 1.2 !important;
    background: linear-gradient(100deg, #9a9fa9, #fff 40%, #b8bcc6 70%, #fff);
    background-size: 200% auto;
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; color: transparent !important;
    animation: riseIn 0.8s var(--ease) 0.25s both, textShimmer 8s linear 1s infinite;
}
.auth-subtitle {
    font-size: 0.88rem !important; color: var(--text-2) !important; text-align: center !important;
    margin: 0 auto 1.5rem auto !important; line-height: 1.55 !important; max-width: 330px !important;
    animation: riseIn 0.8s var(--ease) 0.35s both;
}

/* Form */
.st-key-auth_card [data-testid="stForm"] { background: transparent !important; border: none !important; padding: 0 !important; margin: 0.5rem 0 0 0 !important; box-shadow: none !important; width: 100% !important; animation: riseIn 0.8s var(--ease) 0.45s both; }
.st-key-auth_card [data-testid="stForm"] > div { padding: 0 !important; gap: 0.85rem !important; width: 100% !important; }
.st-key-auth_card [data-testid="stTextInput"], .st-key-auth_card [data-testid="stTextInputRootElement"] { width: 100% !important; margin: 0 !important; padding: 0 !important; }

.st-key-auth_card div[data-baseweb="input"] {
    width: 100% !important; min-width: 0 !important; max-width: 100% !important;
    background-color: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important; border-radius: 10px !important;
    padding: 0 0.5rem 0 0.9rem !important; gap: 0.25rem !important; height: 48px !important;
    display: flex !important; align-items: center !important; overflow: hidden !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease, background-color 0.25s ease !important;
}
.st-key-auth_card div[data-baseweb="input"]:focus-within {
    border-color: rgba(255, 255, 255, 0.65) !important; background-color: rgba(255, 255, 255, 0.07) !important;
    box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1), 0 0 24px rgba(205, 212, 228, 0.15) !important;
}
.st-key-auth_card div[data-baseweb="base-input"] { width: auto !important; min-width: 0 !important; flex: 1 1 0 !important; padding: 0 !important; margin: 0 !important; background: transparent !important; border: none !important; height: 100% !important; display: flex !important; align-items: center !important; overflow: hidden !important; }
.st-key-auth_card div[data-baseweb="input"] input {
    width: 100% !important; min-width: 0 !important; background: transparent !important; border: none !important; box-shadow: none !important; outline: none !important;
    color: #fff !important; font-size: 0.92rem !important; padding: 0 !important; margin: 0 !important; height: 100% !important; line-height: 48px !important;
}
.st-key-auth_card div[data-baseweb="input"] input::placeholder { color: var(--text-3) !important; }

/* Hide the show/hide (eye) toggle on the API key field */
.st-key-auth_card div[data-baseweb="input"] button,
.st-key-auth_card [data-testid="stTextInput"] button { display: none !important; }
.st-key-auth_card div[data-baseweb="input"] { padding-right: 0.9rem !important; }

/* Platinum pill button with sheen */
.st-key-auth_card [data-testid="stFormSubmitButton"] { width: 100% !important; margin: 0.5rem 0 0 0 !important; padding: 0 !important; }
.st-key-auth_card [data-testid="stFormSubmitButton"] button {
    position: relative; overflow: hidden;
    background: var(--platinum-grad) !important; border: 1px solid rgba(255, 255, 255, 0.55) !important;
    border-radius: 9999px !important; padding: 0.75rem 1.25rem !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.85) !important;
    transition: transform 0.25s var(--ease), box-shadow 0.25s ease !important;
    display: flex !important; justify-content: center !important; align-items: center !important; width: 100% !important;
}
.st-key-auth_card [data-testid="stFormSubmitButton"] button::after {
    content: ""; position: absolute; top: 0; bottom: 0; left: -60%; width: 40%;
    background: linear-gradient(100deg, transparent, rgba(255, 255, 255, 0.8), transparent);
    transform: skewX(-18deg); animation: sheen 4.5s ease-in-out infinite;
}
.st-key-auth_card [data-testid="stFormSubmitButton"] button:hover { transform: translateY(-2px) !important; box-shadow: 0 14px 34px rgba(0, 0, 0, 0.55), 0 0 30px rgba(205, 212, 228, 0.2) !important; }
.st-key-auth_card [data-testid="stFormSubmitButton"] button:active { transform: translateY(0) !important; }
.st-key-auth_card [data-testid="stFormSubmitButton"] button *, .st-key-auth_card [data-testid="stFormSubmitButton"] button p { color: #0c0d0f !important; font-weight: 700 !important; font-size: 0.92rem !important; text-align: center !important; }

.auth-note { text-align: center; font-size: 0.72rem; color: var(--text-3); margin-top: 0.9rem; line-height: 1.5; animation: fadeIn 1s ease 0.55s both; }
.auth-helper-row { text-align: center; font-size: 0.8rem; color: var(--text-2); margin-top: 1.4rem; margin-bottom: 2.2rem; animation: fadeIn 1s ease 0.6s both; }
.auth-helper-row a { color: #fff; font-weight: 600; text-decoration: underline; text-underline-offset: 3px; transition: color 0.2s ease; }
.auth-helper-row a:hover { color: #c5c9d1; }
.auth-footer-links { display: flex; align-items: center; justify-content: center; gap: 12px; font-size: 0.72rem; color: var(--text-3); margin-top: auto; animation: fadeIn 1s ease 0.7s both; }
.auth-footer-links a { color: var(--text-3); text-decoration: none; transition: color 0.15s ease; }
.auth-footer-links a:hover { color: #b4b8c1; }
.auth-footer-links span { color: #3a3d46; }

.st-key-auth_card [data-testid="stAlert"] { background-color: rgba(127, 29, 29, 0.25) !important; border: 1px solid rgba(248, 113, 113, 0.4) !important; border-radius: 8px !important; padding: 0.6rem 0.85rem !important; font-size: 0.82rem !important; margin-top: 0.6rem !important; animation: riseIn 0.4s var(--ease) both; }
.st-key-auth_card [data-testid="stAlert"] * { color: #fca5a5 !important; }

@media (max-width: 768px) {
    .st-key-auth_card [data-testid="stHorizontalBlock"] { flex-direction: column !important; }
    .st-key-auth_card :is([data-testid="column"], [data-testid="stColumn"]):nth-of-type(1) { padding: 2.2rem 1.6rem !important; }
    .auth-art-box { min-height: 260px; }
    .st-key-auth_card :is([data-testid="column"], [data-testid="stColumn"]) { width: 100% !important; flex: 1 1 100% !important; }
}
</style>
"""
    st.markdown(LOGIN_STYLE, unsafe_allow_html=True)

    with st.container(key="auth_card"):
        col_form, col_art = st.columns([1, 1], gap="small")

        with col_form:
            st.markdown(
                html_block(
                    """
                    <div class="auth-logo-box">
                    <svg width="26" height="26" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M13 2L3 14H12L11 22L21 10H12L13 2Z" fill="#FFFFFF" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    </div>
                    <h2 class="auth-title">Welcome back!</h2>
                    <p class="auth-subtitle">Enter your OpenAI API key to access high-precision reasoning and intelligence.</p>
                    """
                ),
                unsafe_allow_html=True,
            )

            with st.form("api_key_login_form"):
                key = st.text_input(
                    "OpenAI API Key",
                    type="password",
                    placeholder="Enter your API key",
                    label_visibility="collapsed",
                )
                submitted = st.form_submit_button("Sign in with API Key", use_container_width=True)

            if submitted:
                if key.strip():
                    ENV_PATH.touch(exist_ok=True)
                    set_key(str(ENV_PATH), "OPENAI_API_KEY", key.strip())
                    os.environ["OPENAI_API_KEY"] = key.strip()
                    st.rerun()
                else:
                    st.warning("Please provide a valid OpenAI API key to proceed.")

            st.markdown(
                html_block(
                    """
                    <div class="auth-note">🔒 Saved locally in .env and sent only to OpenAI with your requests.</div>
                    <div class="auth-helper-row">
                    Don't have an account? <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer">Sign Up</a>
                    </div>
                    <div class="auth-footer-links">
                    <a href="https://help.openai.com" target="_blank" rel="noopener noreferrer">Help</a>
                    <span>/</span>
                    <a href="https://openai.com/policies/terms-of-use" target="_blank" rel="noopener noreferrer">Terms</a>
                    <span>/</span>
                    <a href="https://openai.com/policies/privacy-policy" target="_blank" rel="noopener noreferrer">Privacy</a>
                    </div>
                    """
                ),
                unsafe_allow_html=True,
            )

        with col_art:
            st.markdown(
                html_block(
                    f"""
                    <div class="auth-art-box">
                    <div class="art-grid"></div>
                    <div class="art-orb art-orb-a"></div>
                    <div class="art-orb art-orb-b"></div>
                    <div class="art-ring"></div>
                    <div class="art-ring"></div>
                    <div class="art-ring"></div>
                    <div class="art-core">Ø</div>
                    <div class="art-caption">
                    <div class="art-caption-title">{APP_NAME}</div>
                    <div class="art-caption-sub">{APP_TAGLINE}</div>
                    </div>
                    </div>
                    """
                ),
                unsafe_allow_html=True,
            )

    st.stop()


# =============================================================================
# CHAT STORAGE & SESSION SETUP
# =============================================================================
def load_chats():
    if HISTORY_PATH.exists():
        try:
            return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            st.error("Could not read chats.json. Check file permissions.")
    return {}


def save_chats(chats_data):
    HISTORY_PATH.write_text(
        json.dumps(chats_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def render_user_message(content: str):
    st.markdown(content)


def chat_bubble(role: str, idx: int):
    """Avatar-free message bubble: a plain keyed container instead of st.chat_message."""
    return st.container(key=f"msg_{role}_{st.session_state.current[:8]}_{idx}")


if "chats" not in st.session_state:
    st.session_state.chats = load_chats()

if "current" not in st.session_state:
    st.session_state.current = str(uuid.uuid4())

if "system_role" not in st.session_state:
    st.session_state.system_role = (
        "You are Origin, an elite AI assistant engineered for deep technical problem-solving, "
        "concise precision, and high-impact analysis. Respond clearly, thoroughly, and objectively."
    )

if "model_name" not in st.session_state:
    st.session_state.model_name = "gpt-5.2"

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.5

if "staged_prompt" not in st.session_state:
    st.session_state.staged_prompt = None

chats = st.session_state.chats
current = st.session_state.current


# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown(
        html_block(
            f"""
            <div class="sidebar-header">
            {LOGO_HTML}
            <div>
            <div class="sidebar-title">{APP_NAME}</div>
            <div class="sidebar-sub">SYSTEM v2.5</div>
            </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    if st.button("＋  New Conversation", key="new_chat", use_container_width=True):
        st.session_state.current = str(uuid.uuid4())
        st.rerun()

    st.markdown('<div class="sidebar-section-title">Conversations</div>', unsafe_allow_html=True)

    with st.container(height=180, border=False, key="chat_history_box"):
        if not chats:
            st.caption("No conversations yet.")
        else:
            for chat_id, chat_data in reversed(list(chats.items())):
                is_active = chat_id == current
                title = chat_data.get("title", "New Conversation")
                if st.button(
                    f"💬  {title}",
                    key=f"chat_{chat_id}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                ):
                    st.session_state.current = chat_id
                    st.rerun()

    if current in chats:
        col_del, col_exp = st.columns(2)
        with col_del:
            if st.button("🗑️ Delete", use_container_width=True, help="Delete active chat"):
                del chats[current]
                save_chats(chats)
                st.session_state.current = str(uuid.uuid4())
                st.rerun()
        with col_exp:
            active_msgs = chats[current].get("messages", [])
            transcript = f"# Conversation: {chats[current].get('title', 'Transcript')}\n\n"
            for m in active_msgs:
                transcript += f"### {m['role'].capitalize()}\n{m['content']}\n\n"
            st.download_button(
                "📥 Export",
                data=transcript,
                file_name=f"origin_chat_{current[:8]}.md",
                mime="text/markdown",
                use_container_width=True,
                help="Export conversation to Markdown",
            )

    st.divider()

    st.markdown('<div class="sidebar-section-title">Model Configuration</div>', unsafe_allow_html=True)

    model_options = ["gpt-5.2", "gpt-4o", "gpt-4o-mini"]
    current_idx = model_options.index(st.session_state.model_name) if st.session_state.model_name in model_options else 0
    st.session_state.model_name = st.selectbox(
        "Model Engine",
        options=model_options,
        index=current_idx,
        label_visibility="collapsed",
        help="Select the underlying OpenAI language model.",
    )

    st.session_state.temperature = st.slider(
        "Creativity (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=float(st.session_state.temperature),
        step=0.05,
        help="0.0 = Precise/Code, 1.0 = Exploratory",
    )

    st.markdown('<div class="sidebar-section-title">System Persona</div>', unsafe_allow_html=True)
    st.text_area(
        "Persona",
        key="system_role",
        height=68,
        placeholder="Define system behavior...",
        label_visibility="collapsed",
        help="Define behavioral guidelines and role for Origin.",
    )

    st.divider()

    if st.button("↪  Log Out & Lock", key="logout", use_container_width=True):
        if ENV_PATH.exists():
            unset_key(str(ENV_PATH), "OPENAI_API_KEY")
        os.environ.pop("OPENAI_API_KEY", None)
        for key_name in ("system_role", "chats", "current", "model_name", "temperature", "staged_prompt"):
            st.session_state.pop(key_name, None)
        st.rerun()

    st.markdown(
        '<div style="font-size:0.68rem;color:#4a4d57;text-align:center;margin-top:0.6rem;letter-spacing:0.12em;">'
        "ORIGIN CORE • MONOLITHIC ISOLATION</div>",
        unsafe_allow_html=True,
    )


# =============================================================================
# TOP APP BAR
# =============================================================================
st.markdown(
    html_block(
        f"""
        <div class="top-nav">
        <div class="brand-wrapper">
        {LOGO_HTML}
        <div class="brand-info">
        <span class="brand-title">{APP_NAME}</span>
        <span class="badge-tag">PRO</span>
        </div>
        </div>
        <div class="status-cluster">
        <div class="status-pill"><span class="status-dot"></span><span>Active</span></div>
        <div class="model-pill">{st.session_state.model_name}</div>
        </div>
        </div>
        """
    ),
    unsafe_allow_html=True,
)


# =============================================================================
# MAIN CHAT AREA
# =============================================================================
history = chats.get(current, {}).get("messages", [])

staged_prompt = st.session_state.get("staged_prompt")
if staged_prompt:
    st.session_state.staged_prompt = None

user_input = st.chat_input(f"Ask {APP_NAME} anything or paste code...")
prompt_to_send = user_input or staged_prompt

# A single placeholder holds the hero + suggestion cards. When a prompt is being
# processed we leave it empty, which replaces (removes) the old cards immediately
# instead of leaving them on screen, dimmed, while the model is thinking.
hero_slot = st.empty()

if not history and not prompt_to_send:
    with hero_slot.container():
        st.markdown(
            html_block(
                f"""
                <div class="hero-container">
                <div class="hero-emblem"><span class="glyph">Ø</span></div>
                <div class="hero-pill"><span class="pill-dot"></span><span>Autonomous Reasoning Engine</span></div>
                <h1>{APP_TAGLINE}</h1>
                <p>Classical architectural precision, multi-turn system synthesis, and deep reasoning.
                Select an engineering focus below or enter your inquiry.</p>
                </div>
                """
            ),
            unsafe_allow_html=True,
        )

        st.markdown('<div class="prompt-grid-label">Quick Suggestions</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "⚡ Architecture Review\nScalable concurrency & system patterns.",
                key="starter_1",
                use_container_width=True,
            ):
                st.session_state.staged_prompt = "Review modern software architecture patterns for scalable concurrency and optimize memory performance."
                st.rerun()

            if st.button(
                "📊 Strategic Briefing\nExecutive technical synthesis & tradeoffs.",
                key="starter_2",
                use_container_width=True,
            ):
                st.session_state.staged_prompt = "Draft an executive technical memo summarizing the tradeoffs between microservices and modular monoliths."
                st.rerun()

        with col2:
            if st.button(
                "🔍 Deep Code Debug\nTrace race conditions & algorithmic bugs.",
                key="starter_3",
                use_container_width=True,
            ):
                st.session_state.staged_prompt = "Provide a systematic methodology for tracing race conditions in distributed multi-threaded applications."
                st.rerun()

            if st.button(
                "💡 System Innovation\nHigh-leverage engineering workflow ideas.",
                key="starter_4",
                use_container_width=True,
            ):
                st.session_state.staged_prompt = "Generate 5 high-impact AI-driven workflow tools designed for senior software engineering teams."
                st.rerun()


for i, msg in enumerate(history):
    if msg["role"] == "user":
        with chat_bubble("user", i):
            render_user_message(msg["content"])
    else:
        with chat_bubble("assistant", i):
            st.markdown(msg["content"])


# =============================================================================
# MODEL + MESSAGE PIPELINE
# =============================================================================
llm = ChatOpenAI(
    model=st.session_state.model_name,
    temperature=st.session_state.temperature,
)


if prompt_to_send:
    if current not in chats:
        chats[current] = {
            "title": prompt_to_send[:32].strip(),
            "messages": [],
        }

    history = chats[current]["messages"]
    history.append({"role": "user", "content": prompt_to_send})

    with chat_bubble("user", len(history) - 1):
        render_user_message(prompt_to_send)

    lc_messages = [SystemMessage(content=st.session_state.system_role)]
    for msg in history:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        else:
            lc_messages.append(AIMessage(content=msg["content"]))

    with chat_bubble("assistant", len(history)):
        try:
            with st.spinner("Synthesizing reasoning..."):
                response = llm.invoke(lc_messages)
                reply = response.content

            st.markdown(reply)

        except Exception as e:
            history.pop()
            st.error(f"Execution error: {e}")

        else:
            history.append({"role": "assistant", "content": reply})
            save_chats(chats)
            st.rerun()