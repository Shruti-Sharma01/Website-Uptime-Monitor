"""
Website Uptime Monitor - Enhanced UI (Streamlit)
---------------------------------------------------
Run with:
    streamlit run streamlit_uptime_monitor.py
"""

import streamlit as st
import requests
import time
import pandas as pd
from datetime import datetime

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Uptime Monitor",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ================= CUSTOM CSS =================
st.markdown("""
<style>

/* ---------- Global ---------- */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.stApp {
    background: radial-gradient(circle at top left, #0f172a 0%, #020617 60%);
}

.hero {
    padding: 28px 32px;
    border-radius: 18px;
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid rgba(148,163,184,0.15);
    margin-bottom: 24px;
}
.hero h1 { font-size: 32px; font-weight: 800; color: #f8fafc; margin: 0; }
.hero p { color: #94a3b8; margin-top: 6px; font-size: 15px; }

.stat-card {
    background: linear-gradient(145deg, #1e293b, #111827);
    border: 1px solid rgba(148,163,184,0.12);
    border-radius: 16px;
    padding: 18px 20px;
    text-align: center;
    transition: transform 0.15s ease;
}
.stat-card:hover { transform: translateY(-3px); }
.stat-card .label {
    color: #94a3b8; font-size: 13px; font-weight: 600;
    letter-spacing: 0.5px; text-transform: uppercase;
}
.stat-card .value { font-size: 30px; font-weight: 800; margin-top: 4px; }
.value-up { color: #4ade80; }
.value-down { color: #f87171; }
.value-total { color: #60a5fa; }
.value-avg { color: #facc15; }

.result-card {
    border-radius: 16px;
    padding: 18px 22px;
    margin-bottom: 14px;
    border: 1px solid rgba(148,163,184,0.12);
    background: linear-gradient(145deg, #1e293b, #111827);
}
.result-card.up { border-left: 5px solid #4ade80; }
.result-card.down { border-left: 5px solid #f87171; }

.result-top { display: flex; justify-content: space-between; align-items: center; }
.result-url { font-size: 17px; font-weight: 700; color: #f1f5f9; }
.badge { padding: 4px 14px; border-radius: 999px; font-size: 12px; font-weight: 700; letter-spacing: 0.5px; }
.badge-up { background: rgba(74,222,128,0.15); color: #4ade80; }
.badge-down { background: rgba(248,113,113,0.15); color: #f87171; }

.result-meta { margin-top: 10px; display: flex; gap: 26px; color: #94a3b8; font-size: 13px; }
.result-meta b { color: #e2e8f0; }

.error-text {
    margin-top: 8px; color: #fca5a5; font-size: 13px;
    background: rgba(248,113,113,0.08); padding: 6px 10px; border-radius: 8px;
}

.url-chip {
    display: inline-flex; align-items: center; background: #1e293b;
    border: 1px solid rgba(148,163,184,0.2); color: #e2e8f0;
    padding: 6px 14px; border-radius: 999px; margin: 4px; font-size: 13px;
}

.section-title {
    color: #f1f5f9; font-size: 18px; font-weight: 700;
    margin: 22px 0 12px 0; display: flex; align-items: center; gap: 8px;
}

.stButton button { border-radius: 10px; font-weight: 600; border: 1px solid rgba(148,163,184,0.2); }

section[data-testid="stSidebar"] {
    background: #0b1120;
    border-right: 1px solid rgba(148,163,184,0.1);
}

[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

</style>
""", unsafe_allow_html=True)

# ================= SESSION STATE =================
if "history" not in st.session_state:
    st.session_state.history = []
if "urls" not in st.session_state:
    st.session_state.urls = []


# ================= CORE FUNCTION =================
def check_website(url: str, timeout: int = 5):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    result = {
        "URL": url,
        "Status": "DOWN",
        "Status Code": None,
        "Response Time (ms)": None,
        "Checked At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Error": None,
    }

    try:
        start = time.time()
        response = requests.get(url, timeout=timeout)
        elapsed_ms = round((time.time() - start) * 1000, 2)
        result["Status Code"] = response.status_code
        result["Response Time (ms)"] = elapsed_ms
        result["Status"] = "UP" if 200 <= response.status_code < 400 else "DOWN"
    except requests.exceptions.Timeout:
        result["Error"] = "Request timed out"
    except requests.exceptions.ConnectionError:
        result["Error"] = "Connection failed"
    except requests.exceptions.RequestException as e:
        result["Error"] = str(e)

    return result


def render_result_card(res: dict):
    status_class = "up" if res["Status"] == "UP" else "down"
    badge_class = "badge-up" if res["Status"] == "UP" else "badge-down"
    dot = "🟢" if res["Status"] == "UP" else "🔴"
    rt = f"{res['Response Time (ms)']} ms" if res["Response Time (ms)"] else "N/A"
    code = res["Status Code"] if res["Status Code"] else "N/A"

    error_html = f'<div class="error-text">⚠️ {res["Error"]}</div>' if res["Error"] else ""

    st.markdown(f"""
    <div class="result-card {status_class}">
        <div class="result-top">
            <div class="result-url">{dot} {res['URL']}</div>
            <div class="badge {badge_class}">{res['Status']}</div>
        </div>
        <div class="result-meta">
            <div>Status Code: <b>{code}</b></div>
            <div>Response Time: <b>{rt}</b></div>
            <div>Checked: <b>{res['Checked At']}</b></div>
        </div>
        {error_html}
    </div>
    """, unsafe_allow_html=True)


# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("### ⚙️ Controls")

    with st.form("add_url_form", clear_on_submit=True):
        new_url = st.text_input("Website URL", placeholder="e.g. google.com")
        add_btn = st.form_submit_button("➕ Add URL", use_container_width=True)
        if add_btn and new_url.strip():
            if new_url.strip() not in st.session_state.urls:
                st.session_state.urls.append(new_url.strip())
                st.success(f"Added {new_url.strip()}")
            else:
                st.warning("Already tracked.")

    st.markdown("#### Tracked URLs")
    if st.session_state.urls:
        for i, url in enumerate(st.session_state.urls):
            c1, c2 = st.columns([4, 1])
            c1.markdown(f'<div class="url-chip">{url}</div>', unsafe_allow_html=True)
            if c2.button("✕", key=f"rm_{i}"):
                st.session_state.urls.pop(i)
                st.rerun()
    else:
        st.caption("No URLs added yet.")

    st.divider()

    check_now = st.button("🔍 Check All Now", use_container_width=True, type="primary",
                           disabled=not st.session_state.urls)
    clear_hist = st.button("🗑️ Clear History", use_container_width=True)

    st.divider()
    st.markdown("#### Auto Monitoring")
    auto_monitor = st.toggle("Enable auto-refresh")
    interval = st.number_input("Interval (seconds)", min_value=5, max_value=600, value=30, step=5)

if clear_hist:
    st.session_state.history = []
    st.toast("History cleared", icon="🗑️")


# ================= HERO HEADER =================
st.markdown("""
<div class="hero">
    <h1>🌐 Website Uptime Monitor</h1>
    <p>Track the health of your websites in real time — status codes, response times, and history, all in one dashboard.</p>
</div>
""", unsafe_allow_html=True)

# ================= STATS ROW =================
df_hist = pd.DataFrame(st.session_state.history) if st.session_state.history else pd.DataFrame(
    columns=["URL", "Status", "Status Code", "Response Time (ms)", "Checked At", "Error"]
)

total_checks = len(df_hist)
up_count = int((df_hist["Status"] == "UP").sum()) if total_checks else 0
down_count = int((df_hist["Status"] == "DOWN").sum()) if total_checks else 0
avg_rt = round(df_hist["Response Time (ms)"].dropna().mean(), 1) if total_checks and df_hist["Response Time (ms)"].notna().any() else 0

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="stat-card"><div class="label">Tracked URLs</div><div class="value value-total">{len(st.session_state.urls)}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-card"><div class="label">Up Checks</div><div class="value value-up">{up_count}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-card"><div class="label">Down Checks</div><div class="value value-down">{down_count}</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="stat-card"><div class="label">Avg Response</div><div class="value value-avg">{avg_rt} ms</div></div>', unsafe_allow_html=True)

# ================= MAIN CONTENT TABS =================
tab1, tab2 = st.tabs(["📍 Live Status", "📊 History"])

with tab1:
    if check_now:
        results = []
        with st.spinner("Checking websites..."):
            for url in st.session_state.urls:
                res = check_website(url)
                results.append(res)
                st.session_state.history.append(res)

        st.markdown('<div class="section-title">✅ Latest Results</div>', unsafe_allow_html=True)
        for res in results:
            render_result_card(res)

    elif st.session_state.urls:
        st.info("Click **🔍 Check All Now** in the sidebar to run a fresh check.")
    else:
        st.warning("Add a website URL from the sidebar to get started.")

    if auto_monitor and st.session_state.urls:
        placeholder = st.empty()
        results = []
        for url in st.session_state.urls:
            res = check_website(url)
            results.append(res)
            st.session_state.history.append(res)

        with placeholder.container():
            st.markdown(f"**Auto-refreshed at {datetime.now().strftime('%H:%M:%S')}**")
            for res in results:
                render_result_card(res)

        time.sleep(interval)
        st.rerun()

with tab2:
    st.markdown('<div class="section-title">📊 Check History</div>', unsafe_allow_html=True)
    if not df_hist.empty:
        st.dataframe(df_hist.sort_values("Checked At", ascending=False), use_container_width=True, hide_index=True)

        st.markdown('<div class="section-title">📈 Response Time Trend</div>', unsafe_allow_html=True)
        chart_df = df_hist.dropna(subset=["Response Time (ms)"])
        if not chart_df.empty:
            for url in chart_df["URL"].unique():
                site_df = chart_df[chart_df["URL"] == url]
                st.caption(url)
                st.line_chart(site_df.set_index("Checked At")["Response Time (ms)"])
    else:
        st.caption("No checks performed yet. Run a check to see history here.")