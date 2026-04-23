import os
import pyodbc
import pandas as pd
import matplotlib.pyplot as plt


def get_connection_string() -> str:
    import dbMsSql
    return dbMsSql.connString


# =========================================================
# CONFIG
# =========================================================
OUTPUT_DIR = r"C:\Bikini Atoll\QUANTUM\BACKUP 20251120\projects\ex09\_out20260228\_graph2"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================================================
# LABEL MAPPING (DO NOT CHANGE FILTERING)
# =========================================================
LABEL_MAP = {
    "default": "SA",
    "multi_angle": "MA",
    "ka": "KA",
}

ORDER = ["MA", "KA", "SA"]

COLOUR_MAP = {
    "MA": "red",
    "KA": "orange",
    "SA": "blue",
}

MARKER_MAP = {
    "MA": "s",
    "KA": "o",
    "SA": "D",
}


def get_label(val: str) -> str:
    return LABEL_MAP.get(str(val).lower().strip(), val)


# =========================================================
# LOAD DATA
# =========================================================
sql = """
SELECT
    Layers,
    [Angle Study],
    AR_Min,
    AR_Max,
    AR_Avg,
    AR_StdDev,
    NFEV_Min,
    NFEV_Max,
    NFEV_Avg,
    NFEV_StdDev
FROM dbo.vw_Summary
ORDER BY Layers, [Angle Study];
"""

with pyodbc.connect(get_connection_string()) as conn:
    df = pd.read_sql(sql, conn)

# Clean + enforce numeric
df["Angle Study"] = df["Angle Study"].astype(str).str.strip()
df["Layers"] = pd.to_numeric(df["Layers"], errors="coerce").astype("Int64")

# Drop invalid rows
df = df.dropna(subset=["Layers"])

# Create display label
df["Label"] = df["Angle Study"].apply(get_label)

print("DEBUG mapping:")
print(df[["Angle Study", "Label"]].drop_duplicates())


# =========================================================
# EXPORT CSV
# =========================================================
csv_path = os.path.join(OUTPUT_DIR, "vw_Summary_export.csv")
df.to_csv(csv_path, index=False)
print(f"CSV exported: {csv_path}")


# =========================================================
# PLOTTING FUNCTIONS
# =========================================================
def setup_integer_xaxis(ax, x_values):
    unique_layers = sorted(set(int(x) for x in x_values))
    ax.set_xticks(unique_layers)
    ax.set_xticklabels(unique_layers)


def plot_min_max(df, avg, minv, maxv, title, filename, ylabel):
    fig, ax = plt.subplots(figsize=(10, 6))

    all_x = []

    for label in ORDER:
        d = df[df["Label"] == label].sort_values("Layers")

        if d.empty:
            continue

        x = d["Layers"].astype(int).to_numpy()
        y = d[avg].astype(float).to_numpy()
        ymin = d[minv].astype(float).to_numpy()
        ymax = d[maxv].astype(float).to_numpy()

        all_x.extend(x)

        ax.plot(
            x, y,
            label=label,
            color=COLOUR_MAP[label],
            marker=MARKER_MAP[label],
            linewidth=2,
            markersize=8
        )

        ax.fill_between(
            x, ymin, ymax,
            color=COLOUR_MAP[label],
            alpha=0.15
        )

    ax.set_title(title)
    ax.set_xlabel("Layers")
    ax.set_ylabel(ylabel)
    ax.grid(True)

    setup_integer_xaxis(ax, all_x)

    ax.legend()
    plt.tight_layout()

    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300)
    plt.close()

    print(f"Exported: {filename}")


def plot_std(df, avg, std, title, filename, ylabel):
    fig, ax = plt.subplots(figsize=(10, 6))

    all_x = []

    for label in ORDER:
        d = df[df["Label"] == label].sort_values("Layers")

        if d.empty:
            continue

        x = d["Layers"].astype(int).to_numpy()
        y = d[avg].astype(float).to_numpy()
        s = d[std].fillna(0).astype(float).to_numpy()

        all_x.extend(x)

        ax.plot(
            x, y,
            label=label,
            color=COLOUR_MAP[label],
            marker=MARKER_MAP[label],
            linewidth=2,
            markersize=8
        )

        ax.fill_between(
            x, y - s, y + s,
            color=COLOUR_MAP[label],
            alpha=0.15
        )

    ax.set_title(title)
    ax.set_xlabel("Layers")
    ax.set_ylabel(ylabel)
    ax.grid(True)

    setup_integer_xaxis(ax, all_x)

    ax.legend()
    plt.tight_layout()

    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300)
    plt.close()

    print(f"Exported: {filename}")


# =========================================================
# EXPORT CHARTS
# =========================================================
plot_min_max(df, "AR_Avg", "AR_Min", "AR_Max",
             "AR (Min/Max)", "AR_Min_Max.png", "AR")

plot_std(df, "AR_Avg", "AR_StdDev",
         "AR (Std Dev)", "AR_StdDev.png", "AR")

plot_min_max(df, "NFEV_Avg", "NFEV_Min", "NFEV_Max",
             "NFEV (Min/Max)", "NFEV_Min_Max.png", "NFEV")

plot_std(df, "NFEV_Avg", "NFEV_StdDev",
         "NFEV (Std Dev)", "NFEV_StdDev.png", "NFEV")

print("\nDONE.")