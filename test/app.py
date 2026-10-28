import streamlit as st
import pandas as pd
import json
import os
import detector

st.set_page_config(
    page_title="SentinelML: Log Anomaly Detector",
    page_icon="🛡️",
    layout="wide"
)

# Header & tagline
st.title("🛡️ SentinelML")
st.caption("Upload any log. Find what doesn't belong — unsupervised machine learning for security.")

with st.expander("ℹ️ How it works"):
    st.markdown("""
    **SentinelML** automatically scans tabular or JSON log files without needing labeled training data:
    1. **Auto-Classification**: Detects column roles (timestamps, categories, numeric counters, IDs).
    2. **Feature Engineering**: Extracts signals like hour of day, inter-event time deltas, and frequency encodings.
    3. **Isolation Forest**: Identifies data points that isolate in fewest random splits.
    4. **Explanations**: Translates math distances back into readable security explanations.
    """)

# Sidebar
st.sidebar.header("⚙️ Detection Settings")
use_custom_contam = st.sidebar.checkbox("Custom Contamination Rate", value=False)
if use_custom_contam:
    contamination_val = st.sidebar.slider("Contamination (expected outlier %)", min_value=0.01, max_value=0.25, value=0.05, step=0.01)
else:
    contamination_val = "auto"
    st.sidebar.info("Contamination is currently set to `auto` (adaptive threshold).")

# Data loading section
st.subheader("1. Load Security Logs")
col_upload, col_sample = st.columns([3, 1])

with col_upload:
    uploaded_file = st.file_uploader("Upload .json or .csv log file", type=["json", "csv"])

with col_sample:
    st.write("Or test instantly:")
    use_sample = st.button("🧪 Try with sample data")

df_raw = None

if use_sample:
    sample_path = os.path.join(os.path.dirname(__file__), "sample_data.json")
    if os.path.exists(sample_path):
        with open(sample_path, "r", encoding="utf-8") as f:
            sample_json = json.load(f)
        df_raw = pd.DataFrame(sample_json)
        st.session_state["active_df"] = df_raw
        st.success("Loaded sample dataset (20 security login events).")
elif uploaded_file is not None:
    try:
        df_raw = detector.parse_input_file(uploaded_file)
        st.session_state["active_df"] = df_raw
    except Exception as e:
        st.error(f"Error parsing uploaded file: {e}")

if "active_df" in st.session_state and df_raw is None:
    df_raw = st.session_state["active_df"]

if df_raw is not None and not df_raw.empty:
    # 2. Auto-detection preview
    st.subheader("2. Auto-Detection Preview")
    col_types = detector.detect_column_types(df_raw)
    
    col_prev1, col_prev2 = st.columns([1, 2])
    with col_prev1:
        st.write("**Inferred Column Types:**")
        type_df = pd.DataFrame(list(col_types.items()), columns=["Column", "Inferred Type"])
        st.dataframe(type_df, use_container_width=True, hide_index=True)
    with col_prev2:
        st.write(f"**Raw Data Sample ({len(df_raw)} records):**")
        st.dataframe(df_raw.head(5), use_container_width=True)

    # 3. Run Detection Button
    st.write("")
    if st.button("🚀 Run Anomaly Detection", type="primary"):
        with st.spinner("Engineering features and isolating anomalies..."):
            try:
                df_result, _, engineered_cols, diagnostics = detector.run_anomaly_detection(df_raw, contamination=contamination_val)
                st.session_state["detection_results"] = df_result
                st.session_state["engineered_cols"] = engineered_cols
                st.session_state["diagnostics"] = diagnostics
            except Exception as err:
                st.error(f"Detection failed: {err}")

    # 4. Results Dashboard
    if "detection_results" in st.session_state:
        df_res = st.session_state["detection_results"]
        diagnostics = st.session_state.get("diagnostics", {})
        total_records = len(df_res)
        flagged_count = int(df_res["is_flagged"].sum())
        flagged_pct = (flagged_count / total_records) * 100 if total_records > 0 else 0

        st.markdown("---")

        # Surface any data-quality warnings from the detection engine before the results,
        # since a high flag rate or feature-quality issue changes how much to trust the numbers below
        if diagnostics.get("warnings"):
            for w in diagnostics["warnings"]:
                st.warning(f"⚠️ {w}")

        if diagnostics.get("known_label_columns"):
            cols_str = ", ".join(diagnostics["known_label_columns"])
            st.info(f"ℹ️ Excluded from features (looks like a ground-truth label): {cols_str}")

        with st.expander("🔍 Feature quality diagnostics"):
            if diagnostics.get("feature_diagnostics"):
                for note in diagnostics["feature_diagnostics"]:
                    st.write(f"- {note}")
            else:
                st.write("No feature quality issues detected.")

        st.subheader("3. Results & Risk Summary")

        # Top summary metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Records", f"{total_records:,}")
        m2.metric("Anomalies Flagged", f"{flagged_count}", delta=f"{flagged_pct:.1f}% of logs", delta_color="inverse")
        critical_count = int((df_res["risk_level"] == "CRITICAL").sum())
        m3.metric("Critical Alerts", f"{critical_count}")
        normal_count = total_records - flagged_count
        m4.metric("Normal Events", f"{normal_count}")

        # Risk distribution chart
        st.write("")
        st.write("**Risk Level Breakdown:**")
        risk_counts = df_res["risk_level"].value_counts().reindex(["CRITICAL", "HIGH", "MEDIUM", "LOW"]).fillna(0)
        st.bar_chart(risk_counts)

        # Filterable Flagged Records Table
        st.write("")
        st.subheader("4. Flagged Incidents & Plain-Language Explanations")
        
        df_flagged = df_res[df_res["is_flagged"] == 1].sort_values("anomaly_score")
        
        if df_flagged.empty:
            st.info("No anomalous events detected at current contamination threshold.")
        else:
            filter_risk = st.multiselect("Filter by Risk Level:", ["CRITICAL", "HIGH", "MEDIUM", "LOW"], default=["CRITICAL", "HIGH", "MEDIUM"])
            filtered_view = df_flagged[df_flagged["risk_level"].isin(filter_risk)]

            display_cols = [c for c in ["anomaly_score", "risk_level", "why_flagged", "user_id", "location", "timestamp"] if c in filtered_view.columns]
            if len(display_cols) < 3:
                display_cols = ["anomaly_score", "risk_level", "why_flagged"] + [c for c in filtered_view.columns if c not in ["anomaly_score", "risk_level", "why_flagged", "is_flagged"]][:3]
                
            st.dataframe(filtered_view[display_cols], use_container_width=True)

            # Interactive inspection per row
            st.write("")
            st.write("**Inspect Full Record Details:**")
            selected_idx = st.selectbox(
                "Choose a flagged record to expand:",
                options=filtered_view.index,
                format_func=lambda idx: f"Row #{idx} | Score: {filtered_view.loc[idx, 'anomaly_score']} | Reason: {filtered_view.loc[idx, 'why_flagged']}"
            )
            
            if selected_idx is not None:
                st.json(df_res.loc[selected_idx].to_dict())

            # Export button
            st.write("")
            csv_export = df_res.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Full Results as CSV",
                data=csv_export,
                file_name="sentinelml_results.csv",
                mime="text/csv"
            )
