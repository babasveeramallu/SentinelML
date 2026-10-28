import json
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


def parse_input_file(uploaded_file):
    filename = uploaded_file.name if hasattr(uploaded_file, "name") else "sample.json"

    if filename.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        content = uploaded_file.read() if hasattr(uploaded_file, "read") else uploaded_file
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        data = json.loads(content) if isinstance(content, str) else content

        if isinstance(data, dict):
            for val in data.values():
                if isinstance(val, list):
                    data = val
                    break
        df = pd.DataFrame(data)

    return df


def detect_column_types(df):
    col_types = {}
    n_rows = len(df)

    for col in df.columns:
        col_lower = str(col).lower()
        n_unique = df[col].nunique(dropna=True)
        unique_ratio = n_unique / n_rows if n_rows > 0 else 0

        if any(term in col_lower for term in ["anomaly", "flag", "label", "target"]):
            val_set = set(df[col].dropna().unique())
            if val_set.issubset({0, 1, True, False, "0", "1", "true", "false", "True", "False"}):
                col_types[col] = "label"
                continue

        if any(term in col_lower for term in ["id", "ip", "uuid", "guid", "token", "hash"]):
            col_types[col] = "identifier"
            continue

        if any(term in col_lower for term in ["time", "date", "created", "timestamp"]):
            try:
                pd.to_datetime(df[col])
                col_types[col] = "timestamp"
                continue
            except Exception:
                pass

        if n_rows >= 20 and unique_ratio > 0.95 and not (pd.api.types.is_float_dtype(df[col])):
            col_types[col] = "identifier"
            continue

        if pd.api.types.is_numeric_dtype(df[col]) and not pd.api.types.is_bool_dtype(df[col]):
            col_types[col] = "numeric"
        elif pd.api.types.is_bool_dtype(df[col]):
            col_types[col] = "numeric"
        else:
            col_types[col] = "categorical"

    return col_types


def extract_features(df, col_types):
    df_feat = df.copy()
    feature_dfs = []
    feature_diagnostics = []

    numeric_cols = [c for c, t in col_types.items() if t == "numeric"]
    for c in numeric_cols:
        s = pd.to_numeric(df_feat[c], errors="coerce").fillna(0)
        feature_dfs.append(s.to_frame(name=f"num_{c}"))

    time_cols = [c for c, t in col_types.items() if t == "timestamp"]
    if time_cols:
        t_col = time_cols[0]
        parsed_dt = pd.to_datetime(df_feat[t_col], errors="coerce")
        feature_dfs.append(parsed_dt.dt.hour.fillna(12).to_frame(name="feat_hour_of_day"))
        feature_dfs.append(parsed_dt.dt.dayofweek.fillna(0).to_frame(name="feat_day_of_week"))

        id_cols = [c for c, t in col_types.items() if t == "identifier" or "user" in str(c).lower()]
        if id_cols:
            id_col = id_cols[0]
            df_temp = pd.DataFrame({"id": df_feat[id_col], "t": parsed_dt})
            df_temp = df_temp.sort_values(by=["id", "t"])
            time_diff = df_temp.groupby("id")["t"].diff().dt.total_seconds() / 3600.0
            time_diff = time_diff.reindex(df_feat.index).fillna(24.0)
            feature_dfs.append(time_diff.to_frame(name="feat_hours_since_last_event"))

    cat_cols = [c for c, t in col_types.items() if t == "categorical"]
    for c in cat_cols[:4]:
        freq = df_feat[c].value_counts(normalize=True)
        feature_dfs.append(df_feat[c].map(freq).fillna(0).to_frame(name=f"freq_{c}"))

    if not feature_dfs:
        raise ValueError("No usable numeric, timestamp, or categorical columns found for feature extraction.")

    X = pd.concat(feature_dfs, axis=1)

    n_rows = len(X)
    for col in X.columns:
        series = X[col]
        std_val = float(series.std(ddof=0))
        mean_val = float(series.mean())
        n_distinct = int(series.nunique())

        if std_val == 0.0 or n_distinct <= 1:
            feature_diagnostics.append(f"Feature '{col}' has zero variance (constant value) and adds no discriminative signal.")
        elif n_rows >= 50 and (n_distinct / n_rows) > 0.95:
            feature_diagnostics.append(f"Feature '{col}' has high unique cardinality ({n_distinct}/{n_rows}) and may act as uninformative random noise.")
        elif mean_val != 0.0 and abs(std_val / mean_val) < 0.01:
            feature_diagnostics.append(f"Feature '{col}' is near-constant (coefficient of variation < 0.01).")

    return X, feature_diagnostics


def generate_explanation(row, col_types, df_orig):
    reasons = []

    time_cols = [c for c, t in col_types.items() if t == "timestamp"]
    if time_cols:
        t_col = time_cols[0]
        try:
            dt_val = pd.to_datetime(row[t_col])
            if dt_val.hour in [1, 2, 3, 4, 5]:
                reasons.append(f"Off-hours activity ({dt_val.strftime('%I:%M %p')})")
        except Exception:
            pass

    for c in row.index:
        if "fail" in str(c).lower() and isinstance(row[c], (int, float, np.integer, np.floating)) and row[c] >= 3:
            reasons.append(f"Failure count elevated ({int(row[c])} attempts)")

    cat_cols = [c for c, t in col_types.items() if t == "categorical"]
    for c in cat_cols:
        val = row.get(c)
        if val is not None and c in df_orig:
            pct = (df_orig[c] == val).mean()
            if pct < 0.10:
                reasons.append(f"Rare {c} '{val}' ({pct:.1%} frequency)")

    if not reasons:
        reasons.append("Multi-feature outlier signature across tree partitions")

    return "; ".join(reasons)


def run_anomaly_detection(df, contamination=0.05):
    col_types = detect_column_types(df)
    known_label_columns = [c for c, t in col_types.items() if t == "label"]

    X, feature_diagnostics = extract_features(df, col_types)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    if contamination is None or contamination == "auto":
        contam_param = 0.05
    else:
        try:
            contam_param = float(contamination)
            if not (0.0 < contam_param <= 0.5):
                contam_param = 0.05
        except (ValueError, TypeError):
            contam_param = 0.05

    model = IsolationForest(
        n_estimators=100,
        contamination=contam_param,
        random_state=42
    )
    model.fit(X_scaled)

    scores = model.decision_function(X_scaled)
    preds = model.predict(X_scaled)

    df_result = df.copy()
    df_result["anomaly_score"] = np.round(scores, 4)
    df_result["is_flagged"] = np.where(preds == -1, 1, 0)

    df_result["risk_level"] = pd.cut(
        df_result["anomaly_score"],
        bins=[-np.inf, -0.08, 0.0, 0.08, np.inf],
        labels=["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    )

    df_result["why_flagged"] = df_result.apply(
        lambda r: generate_explanation(r, col_types, df) if r["is_flagged"] == 1 else "Normal pattern",
        axis=1
    )

    flagged_ratio = float(df_result["is_flagged"].mean())
    warnings = []

    if flagged_ratio > 0.25:
        warnings.append(
            f"High anomaly rate detected: {flagged_ratio:.1%} of records flagged. "
            "Feature space may be dominated by low-signal or discrete noise. "
            "Review feature distributions and reduce contamination setting."
        )

    diagnostics = {
        "flagged_percentage": flagged_ratio * 100.0,
        "contamination_used": contam_param,
        "known_label_columns": known_label_columns,
        "warnings": warnings,
        "feature_diagnostics": feature_diagnostics
    }

    return df_result, col_types, X.columns.tolist(), diagnostics
