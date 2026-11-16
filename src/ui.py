"""Shared corporate interface for the CommunityLab workspace."""

from html import escape
from pathlib import Path

import streamlit as st
from src.design import FONT_STACK, LIGHT_PALETTE, OPERATIONAL_TONES

LOGO = Path(__file__).resolve().parents[1] / "docs/assets/logo-communitylab.svg"
SOURCE_LABELS = {"mastodon": "Mastodon", "hackernews": "Hacker News", "stackoverflow": "Stack Overflow"}
THEME_LABELS = {"artificial-intelligence": "Inteligência artificial", "docker": "Docker", "frontend": "Desenvolvimento de interfaces", "backend": "Desenvolvimento de sistemas", "devops": "DevOps", "mobile": "Desenvolvimento móvel", "machine-learning": "Aprendizado de máquina", "job": "Carreira e oportunidades"}
SENTIMENT_LABELS = {"Excited": "Entusiasmado", "Happy": "Satisfeito", "Neutral": "Neutro", "Disappointed": "Decepcionado", "Angry": "Irritado"}
EDITORIAL_LABELS = {"success_case": "Caso de sucesso", "faq": "FAQ", "newsletter": "Newsletter", "moderation": "Moderação", "discard": "Descarte", "other": "Outro", "fallback": "Encaminhamento alternativo"}


def tokens():
    return LIGHT_PALETTE.copy()


def apply_theme():
    p = tokens()
    variables = ";".join(f"--cl-{key}:{value}" for key, value in p.items())
    st.markdown("<style>:root{color-scheme:light;" + variables + "}" + """
    :root {--cl-font:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;}
    .stApp, input, textarea, button, [data-baseweb="select"] {font-family:var(--cl-font);}
    .stApp {background:var(--cl-bg); color:var(--cl-text);}
    [data-testid="stHeader"] {background:var(--cl-bg);}
    /* Reserve space for Streamlit's fixed header, including on narrow screens. */
    .stMainBlockContainer {max-width:1720px; padding:6rem 2.5rem 3rem;}
    h1,h2,h3,p,label,[data-testid="stMarkdownContainer"] {color:inherit;}
    .stMain [data-testid="stHeading"] {overflow:visible;}
    h1 {font-size:28px!important; line-height:1.3!important; padding-top:.25rem; padding-bottom:.75rem; letter-spacing:-.03em; font-weight:700!important;}
    h2,h3 {font-size:18px!important; color:var(--cl-text); font-weight:700!important;}
    [data-testid="stCaptionContainer"] {color:var(--cl-muted); font-size:12px;}
    .st-key-data_actions [data-testid="stCaptionContainer"] {color:var(--cl-tertiary);}
    .cl-description {font-size:14px; color:var(--cl-muted); line-height:1.5; margin:0 0 16px;}
    .stMain a:not([data-testid="stBaseButton-primary"]):not([data-testid="stBaseButton-secondary"]) {color:var(--cl-link);}
    .stMain [data-testid="stMarkdownContainer"] a {text-decoration:underline; text-underline-offset:3px;}
    .stMain a:hover {color:var(--cl-action);}
    [data-testid="stPageLink-NavLink"],[data-testid="stPageLink-NavLink"] p {color:var(--cl-link)!important;}
    [data-testid="stPageLink-NavLink"]:hover {background:var(--cl-soft);}
    [data-testid="stWidgetLabel"],[data-testid="stExpander"] {color:var(--cl-text);}
    [data-testid="stExpander"],[data-testid="stFileUploaderDropzone"],[data-testid="stChatMessage"] {background:var(--cl-surface); color:var(--cl-text); border:1px solid var(--cl-border); border-radius:8px;}
    [data-testid="stSidebar"] {background:var(--cl-surface); color:var(--cl-text); border-right:1px solid var(--cl-border); width:260px!important; min-width:260px!important; max-width:260px!important;}
    [data-testid="stSidebarUserContent"] {min-height:calc(100dvh - 5rem); display:flex; flex-direction:column;}
    [data-testid="stSidebarUserContent"]>[data-testid="stVerticalBlock"] {flex:1;}
    [data-testid="stSidebarUserContent"]>[data-testid="stVerticalBlock"]>.stElementContainer:has(.cl-sidebar-footer) {margin-top:auto;}
    .cl-sidebar-footer {border-top:1px solid var(--cl-border); padding-top:16px; margin-top:24px; color:var(--cl-tertiary); font-size:12px;}
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {border-radius:6px; color:var(--cl-muted)!important;}
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] p {color:inherit!important;}
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"],
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:has([aria-current="page"]),
    .st-key-navigation_current [data-testid="stPageLink-NavLink"] {background:var(--cl-soft); color:var(--cl-action)!important; font-weight:600;}
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {color:var(--cl-muted);}
    [data-testid="stSidebarNavLink"],[data-testid="stSidebarNavLink"] span {color:var(--cl-text)!important; border-radius:8px;}
    [data-testid="stSidebarNavLink"] {margin:4px 0;}
    [data-testid="stSidebarNavLink"]:hover {background:var(--cl-bg);}
    [data-testid="stSidebarNavLink"][aria-current="page"] {background:var(--cl-soft); border-left:3px solid var(--cl-action); font-weight:600;}
    [data-testid="stVerticalBlockBorderWrapper"]>div {border-color:var(--cl-border)!important; border-radius:8px!important;}
    [data-testid="stVerticalBlockBorderWrapper"] {background:var(--cl-surface); border-radius:8px;}
    .stButton>button,.stFormSubmitButton>button,.stDownloadButton>button,.stLinkButton>a {min-height:42px; border-radius:6px; font-weight:600;}
    .stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primaryFormSubmit"] {background:var(--cl-action); border-color:var(--cl-action); color:#FFFFFF;}
    .stButton>button[kind="primary"]:hover,.stFormSubmitButton>button[kind="primaryFormSubmit"]:hover {background:var(--cl-hover); border-color:var(--cl-hover); color:#FFFFFF;}
    .stButton>button[kind="primary"] p {color:inherit;}
    .stButton>button:disabled {opacity:1; background:#EDF1F3; border-color:var(--cl-border); color:#60717B; cursor:not-allowed;}
    .stButton>button[kind="secondary"],.stDownloadButton>button,.stLinkButton>a {background:var(--cl-surface); color:#334155; border-color:#CBD5E1;}
    [data-baseweb="input"],[data-baseweb="textarea"],[data-baseweb="select"]>div {background:var(--cl-surface); color:var(--cl-text); border-color:var(--cl-border);}
    input,textarea {color:var(--cl-text)!important; -webkit-text-fill-color:var(--cl-text)!important;}
    input::placeholder,textarea::placeholder {color:var(--cl-muted)!important; -webkit-text-fill-color:var(--cl-muted)!important; opacity:1;}
    [data-baseweb="tag"] {background:var(--cl-soft); color:var(--cl-text);}
    [data-baseweb="popover"],[data-baseweb="menu"],[role="listbox"],[role="option"] {color:var(--cl-text); background:var(--cl-surface);}
    [data-testid="stMetric"] {padding:16px 20px; background:var(--cl-surface); border:1px solid var(--cl-border); border-radius:8px;}
    .cl-topbar {display:flex; justify-content:space-between; align-items:center; gap:16px; border-bottom:1px solid var(--cl-border); padding:0 0 20px; margin-bottom:28px; font-size:12px; color:var(--cl-tertiary);}
    .cl-topbar strong {color:var(--cl-brand); font-size:14px;}
    .cl-eyebrow {color:var(--cl-action); font-size:11px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; margin-bottom:8px;}
    .cl-kpi {background:var(--cl-surface); border:1px solid var(--cl-border); border-radius:8px; padding:16px 20px; min-height:132px; margin-bottom:16px;}
    .cl-kpi-label {font-size:12px; color:var(--cl-muted);}
    .cl-kpi-value {font-size:26px; font-weight:700; line-height:1.3; letter-spacing:-.035em; padding:8px 0; overflow-wrap:anywhere;}
    .cl-kpi-note {font-size:11px; color:var(--cl-tertiary);}
    .cl-badge {display:inline-block; padding:4px 10px; margin:0 6px 6px 0; background:var(--cl-soft); color:var(--cl-text); border:1px solid var(--cl-border); border-radius:6px; font-size:12px;}
    .cl-footer {border-top:1px solid var(--cl-border); margin-top:40px; padding-top:16px; color:var(--cl-tertiary); font-size:12px;}
    [data-testid="stChatMessageAvatarUser"] {background:#F5DAD8; color:#7C3834;}
    [data-testid="stChatMessageAvatarAssistant"] {background:#F4E3C9; color:#7C5318;}
    button:focus-visible,a:focus-visible {outline:3px solid var(--cl-blue)!important; outline-offset:3px;}
    #MainMenu,[data-testid="stAppDeployButton"] {display:none;}
    @media(min-width:769px) and (max-width:1100px) {.stMainBlockContainer {padding-left:24px; padding-right:24px;} .st-key-workspace_kpis [data-testid="stHorizontalBlock"] {flex-wrap:wrap;} .st-key-workspace_kpis [data-testid="stColumn"] {min-width:calc(50% - 16px); flex:1 1 calc(50% - 16px);}}
    @media(max-width:768px) {.stMainBlockContainer {padding:5rem 16px 2rem;} .cl-topbar {flex-wrap:wrap;} h1 {font-size:24px!important;} .cl-kpi {min-height:120px;} .st-key-workspace_kpis [data-testid="stHorizontalBlock"] {flex-direction:column;} .st-key-workspace_kpis [data-testid="stColumn"] {width:100%!important; min-width:100%!important; flex:1 1 100%;} .st-key-treemap_controls [data-testid="stHorizontalBlock"] {flex-wrap:wrap;} .st-key-treemap_controls>[data-testid="stVerticalBlock"]>[data-testid="stHorizontalBlock"]>[data-testid="stColumn"] {min-width:calc(50% - 16px); flex:1 1 calc(50% - 16px);} [data-testid="stSidebarUserContent"] {min-height:calc(100dvh - 5rem);}}
    @media(prefers-reduced-motion:reduce) {* {animation:none!important; transition:none!important;}}
    </style>""", unsafe_allow_html=True)


def page_header(title, description, section="Área de trabalho"):
    st.markdown(f'<div class="cl-eyebrow">{escape(section)}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<p class="cl-description">{escape(description)}</p>', unsafe_allow_html=True)


def metric_card(label, value, note=""):
    st.markdown(f'<div class="cl-kpi"><div class="cl-kpi-label">{escape(str(label))}</div><div class="cl-kpi-value">{escape(str(value))}</div><div class="cl-kpi-note">{escape(str(note))}</div></div>', unsafe_allow_html=True)


def badges(items, states=None):
    states = states or []
    parts = []
    for index, item in enumerate(items):
        tone = OPERATIONAL_TONES.get(states[index]) if index < len(states) else None
        style = f' style="background:{tone[0]};color:{tone[1]}"' if tone else ""
        parts.append(f'<span class="cl-badge"{style}>{escape(str(item))}</span>')
    st.markdown("".join(parts), unsafe_allow_html=True)


def style_chart(figure):
    p = tokens()
    figure.update_layout(paper_bgcolor=p["surface"], plot_bgcolor=p["surface"], font=dict(color=p["text"], family=FONT_STACK), colorway=[p["action"], p["blue"], "#7C5318", "#4B326B"], margin=dict(l=16, r=16, t=40, b=16))
    figure.update_layout(hoverlabel=dict(bgcolor=p["surface"], font_color=p["text"], bordercolor=p["border"]))
    figure.update_layout(separators=",.")
    figure.update_xaxes(color=p["muted"], gridcolor=p["border"])
    figure.update_yaxes(color=p["muted"], gridcolor=p["border"])
    return figure
