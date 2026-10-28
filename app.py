import streamlit as st
import pandas as pd
import json
import os
import detector

st.set_page_config(
    page_title="SENTINEL_ML // ROOT_SHELL",
    page_icon="📟",
    layout="wide"
)

# Custom Styling for Terminal Aesthetic without breaking Streamlit's native dataframes/multiselects
TERMINAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

/* Base typography */
html, body, [class*="css"], .stMarkdown, p, label {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Subtle CRT background overlay */
.stApp::before {
    content: " ";
    display: block;
    position: fixed;
    top: 0; left: 0; bottom: 0; right: 0;
    background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.2) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.02), rgba(0, 255, 0, 0.01), rgba(0, 255, 0, 0.02));
    z-index: 999999;
    background-size: 100% 3px, 6px 100%;
    pointer-events: none;
    opacity: 0.45;
}

/* Phosphor text highlights */
.glow-title {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 2.4rem !important;
    font-weight: 800 !important;
    color: #33ff00 !important;
    letter-spacing: 3px !important;
    text-shadow: 0 0 10px rgba(51, 255, 0, 0.8), 0 0 20px rgba(51, 255, 0, 0.4);
    margin: 0;
    padding: 0;
}
.glow-text {
    color: #33ff00 !important;
    text-shadow: 0 0 6px rgba(51, 255, 0, 0.6);
}
.glow-amber {
    color: #ffb000 !important;
    text-shadow: 0 0 6px rgba(255, 176, 0, 0.6);
}
.glow-red {
    color: #ff3333 !important;
    text-shadow: 0 0 6px rgba(255, 51, 51, 0.7);
}

/* Blinking cursor */
@keyframes blink {
    0%, 49% { opacity: 1; }
    50%, 100% { opacity: 0; }
}
.cursor-block {
    display: inline-block;
    width: 12px;
    height: 22px;
    background-color: #33ff00;
    vertical-align: middle;
    animation: blink 1s infinite;
    box-shadow: 0 0 8px #33ff00;
    margin-left: 6px;
}

/* CLI Panes & Windows */
.cli-pane {
    border: 1px solid #1f521f;
    background: #0d140d;
    padding: 12px 16px;
    margin-bottom: 15px;
}
.cli-pane-header {
    border-bottom: 1px dashed #1f521f;
    padding-bottom: 6px;
    margin-top: 18px;
    margin-bottom: 14px;
    font-weight: 700;
    font-size: 0.9rem;
    color: #ffb000 !important;
    letter-spacing: 1px;
}

/* Custom button styling */
.stButton > button {
    background-color: #0a0a0a !important;
    color: #33ff00 !important;
    border: 1px solid #33ff00 !important;
    border-radius: 0px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    padding: 8px 18px !important;
    transition: all 0.15s ease-in-out !important;
}
.stButton > button:hover {
    background-color: #33ff00 !important;
    color: #000000 !important;
    box-shadow: 0 0 14px #33ff00 !important;
}
.stButton > button:active {
    background-color: #ffb000 !important;
    color: #000000 !important;
}

/* Metric values */
[data-testid="stMetricValue"] {
    color: #33ff00 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 2.2rem !important;
    text-shadow: 0 0 8px rgba(51, 255, 0, 0.5);
}
[data-testid="stMetricLabel"] {
    color: #ffb000 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
}

/* Multiselect tag fix */
[data-baseweb="tag"] {
    background-color: #1a331a !important;
    border: 1px solid #33ff00 !important;
}
[data-baseweb="tag"] span {
    color: #33ff00 !important;
    font-family: 'JetBrains Mono', monospace !important;
}
</style>
"""
st.markdown(TERMINAL_CSS, unsafe_allow_html=True)

# 1. Clean Vector Terminal Header (Crisp & Readable)
st.markdown("""
<div style="border: 1px solid #1f521f; background: #070c07; padding: 20px 24px; margin-bottom: 20px;">
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
        <div>
            <h1 class="glow-title">> SENTINEL_ML<span class="cursor-block"></span></h1>
            <p style="color: #88aa88; margin-top: 6px; font-size: 0.9rem; font-family: 'JetBrains Mono', monospace;">
                [SYS_INIT] ANOMALY_DETECTION_DAEMON v1.0.0 // UNSUPERVISED BEHAVIORAL TRIAGE
            </p>
        </div>
        <div style="text-align: right; color: #ffb000; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; border: 1px dashed #1f521f; padding: 8px 14px;">
            HOST: 127.0.0.1:8501<br>
            STATUS: ACTIVE_LISTENING
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<p style='color: #88aa88 !important; font-size: 0.85rem; font-family: monospace;'>[PROMPT]: Ingest log vectors (JSON / CSV) -> auto-engineer behavioral features -> isolate threats.</p>", unsafe_allow_html=True)

with st.expander("[?] MAN_PAGE // SENTINEL_ML(8) -- SPECIFICATION"):
    st.markdown("""
```
NAME
     sentinel_ml -- Unsupervised behavioral anomaly isolation daemon

PIPELINE
     1. [SCHEMA_INSPECT]  Infers roles: Numeric, Timestamp, Categorical, Identifier, Label.
     2. [FEAT_ENGINEER]   Calculates hour-of-day, inter-event interval, frequency encodings.
     3. [TREE_ISOLATION]  Builds Isolation Forest. Outliers isolate in shallower tree depths.
     4. [AUDIT_REPORT]    Produces human-readable diagnostic tags (off-hours, failure bursts).
```
    """)

# Sidebar Controls
st.sidebar.markdown("<div class='glow-text'>[CONFIG_SYS] PARAMETERS</div>", unsafe_allow_html=True)
st.sidebar.markdown("---")

use_custom_contam = st.sidebar.checkbox("[--override-contamination]", value=False)
if use_custom_contam:
    contamination_val = st.sidebar.slider("ALPHA_CONTAMINATION_RATE", min_value=0.01, max_value=0.25, value=0.05, step=0.01)
    st.sidebar.caption(f"[CONF] RATE = {contamination_val:.2f}")
else:
    contamination_val = 0.05
    st.sidebar.markdown("`[STATUS]: DEFAULT_CALIBRATED (0.05)`")

st.sidebar.markdown("---")
st.sidebar.markdown("<div style='color: #ffb000; font-size: 0.8rem; font-family: monospace;'>[AUTH]: ROOT_PRIVILEGES<br>[KERNEL]: LOCAL_DAEMON</div>", unsafe_allow_html=True)

# 01. Buffer Ingestion
st.markdown("<div class='cli-pane-header'>// 01. BUFFER_INGESTION</div>", unsafe_allow_html=True)
col_upload, col_sample = st.columns([3, 1])

with col_upload:
    uploaded_file = st.file_uploader("[INPUT_STREAM]: UPLOAD LOG (.JSON / .CSV)", type=["json", "csv"])

with col_sample:
    st.write("[TEST_PAYLOAD]:")
    use_sample = st.button("[ LOAD_SAMPLE_DATA ]")

df_raw = None

if use_sample:
    sample_path = os.path.join(os.path.dirname(__file__), "sample_data.json")
    if os.path.exists(sample_path):
        with open(sample_path, "r", encoding="utf-8") as f:
            sample_json = json.load(f)
        df_raw = pd.DataFrame(sample_json)
        st.session_state["active_df"] = df_raw
        st.markdown("<p class='glow-text'>[OK] 20 SAMPLE LOG ENTRIES LOADED INTO MEMORY_BUFFER.</p>", unsafe_allow_html=True)
elif uploaded_file is not None:
    try:
        df_raw = detector.parse_input_file(uploaded_file)
        st.session_state["active_df"] = df_raw
        st.markdown(f"<p class='glow-text'>[OK] STREAM PARSED: {len(df_raw):,} RECORDS INGESTED.</p>", unsafe_allow_html=True)
    except Exception as e:
        st.markdown(f"<p class='glow-red'>[ERR] STREAM_PARSE_FAILURE: {e}</p>", unsafe_allow_html=True)

if "active_df" in st.session_state and df_raw is None:
    df_raw = st.session_state["active_df"]

if df_raw is not None and not df_raw.empty:
    # 02. Schema Preview
    st.markdown("<div class='cli-pane-header'>// 02. SCHEMA_INSPECTION_TABLE</div>", unsafe_allow_html=True)
    col_types = detector.detect_column_types(df_raw)

    col_prev1, col_prev2 = st.columns([1, 2])
    with col_prev1:
        st.markdown("**[INFERRED_COLUMN_TYPES]:**")
        type_df = pd.DataFrame(list(col_types.items()), columns=["FIELD_NAME", "DETECTED_TYPE"])
        st.dataframe(type_df, use_container_width=True, hide_index=True)
    with col_prev2:
        st.markdown(f"**[RAW_DATA_PREVIEW] ({len(df_raw):,} ROWS):**")
        st.dataframe(df_raw.head(8), use_container_width=True)

    # 03. Execution
    st.markdown("<div class='cli-pane-header'>// 03. EXECUTION_VECTOR</div>", unsafe_allow_html=True)
    if st.button("[ INITIATE_ISOLATION_SCAN ]", type="primary"):
        with st.spinner(">> RUNNING ISOLATION FOREST ENSEMBLE..."):
            try:
                df_result, _, engineered_cols, diagnostics = detector.run_anomaly_detection(df_raw, contamination=contamination_val)
                st.session_state["detection_results"] = df_result
                st.session_state["engineered_cols"] = engineered_cols
                st.session_state["diagnostics"] = diagnostics
                st.markdown("<p class='glow-text'>[OK] SCAN COMPLETE // RESULTS BUFFER COMPILED.</p>", unsafe_allow_html=True)
            except Exception as err:
                st.markdown(f"<p class='glow-red'>[FATAL] SCAN_EXECUTION_ERROR: {err}</p>", unsafe_allow_html=True)

    # 04. Dashboard & Telemetry
    if "detection_results" in st.session_state:
        df_res = st.session_state["detection_results"]
        diagnostics = st.session_state.get("diagnostics", {})
        total_records = len(df_res)
        flagged_count = int(df_res["is_flagged"].sum())
        flagged_pct = (flagged_count / total_records) * 100 if total_records > 0 else 0

        st.markdown("<div class='cli-pane-header'>// 04. TELEMETRY & DIAGNOSTICS</div>", unsafe_allow_html=True)

        if diagnostics.get("warnings"):
            for w in diagnostics["warnings"]:
                st.markdown(f"<div class='cli-pane glow-amber'>[WARN] {w}</div>", unsafe_allow_html=True)

        if diagnostics.get("known_label_columns"):
            st.markdown(f"<div class='cli-pane'>[GUARD]: Ground-truth label column(s) isolated from model: <code>{', '.join(diagnostics['known_label_columns'])}</code></div>", unsafe_allow_html=True)

        if diagnostics.get("feature_diagnostics"):
            with st.expander("[?] FEATURE_QUALITY_REPORT"):
                for fd in diagnostics["feature_diagnostics"]:
                    st.markdown(f"`[-]` {fd}")

        # Metric stats
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("TOTAL_RECORDS", f"{total_records:,}")
        m2.metric("ISOLATED_THREATS", f"{flagged_count}", delta=f"{flagged_pct:.1f}% RATIO", delta_color="inverse")
        critical_count = int((df_res["risk_level"] == "CRITICAL").sum())
        m3.metric("CRITICAL_ALERTS", f"{critical_count}")
        normal_count = total_records - flagged_count
        m4.metric("BENIGN_EVENTS", f"{normal_count:,}")

        # Threat breakdown
        st.markdown("**[THREAT_LEVEL_DISTRIBUTION]:**")
        risk_counts = df_res["risk_level"].value_counts().reindex(["CRITICAL", "HIGH", "MEDIUM", "LOW"]).fillna(0)
        
        for lvl, cnt in risk_counts.items():
            bar_len = int((cnt / total_records) * 35) if total_records > 0 else 0
            bar_str = "[" + "#" * bar_len + "." * (35 - bar_len) + "]"
            col_tag = "glow-red" if lvl == "CRITICAL" else ("glow-amber" if lvl == "HIGH" else "glow-text")
            st.markdown(f"<p style='margin: 3px 0; font-family: monospace;'><code>{lvl:<8}</code> <span class='{col_tag}'>{bar_str}</span> <strong>{int(cnt):>5}</strong> ({cnt/total_records*100:.1f}%)</p>", unsafe_allow_html=True)

        # 05. Flagged incidents table
        st.markdown("<div class='cli-pane-header'>// 05. INCIDENT_TRIAGE_LOG</div>", unsafe_allow_html=True)

        df_flagged = df_res[df_res["is_flagged"] == 1].sort_values("anomaly_score")

        if df_flagged.empty:
            st.markdown("<div class='cli-pane'>[STATUS]: NO_OUTLIERS_DETECTED_AT_CURRENT_THRESHOLD.</div>", unsafe_allow_html=True)
        else:
            filter_risk = st.multiselect("[FILTER_RISK_LEVELS]:", ["CRITICAL", "HIGH", "MEDIUM", "LOW"], default=["CRITICAL", "HIGH", "MEDIUM"])
            filtered_view = df_flagged[df_flagged["risk_level"].isin(filter_risk)]

            priority_cols = ["anomaly_score", "risk_level", "why_flagged"]
            other_cols = [c for c in filtered_view.columns if c not in priority_cols and c != "is_flagged"]
            display_cols = priority_cols + other_cols

            st.write(f"Showing **{len(filtered_view):,}** flagged records matching filter:")
            st.dataframe(filtered_view[display_cols], use_container_width=True, height=350)

            # 06. Payload inspector
            st.markdown("<div class='cli-pane-header'>// 06. RECORD_PAYLOAD_INSPECTOR</div>", unsafe_allow_html=True)
            if not filtered_view.empty:
                selected_idx = st.selectbox(
                    "[SELECT_INCIDENT_ROW]:",
                    options=filtered_view.index,
                    format_func=lambda idx: f">> ROW_{idx:05d} | SCORE: {filtered_view.loc[idx, 'anomaly_score']} | REASON: {filtered_view.loc[idx, 'why_flagged']}"
                )

                if selected_idx is not None:
                    st.json(df_res.loc[selected_idx].to_dict())

            # Export button
            st.write("")
            csv_export = df_res.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="[ DUMP_FULL_AUDIT_LOG_CSV ]",
                data=csv_export,
                file_name="sentinelml_audit_dump.csv",
                mime="text/csv"
            )
