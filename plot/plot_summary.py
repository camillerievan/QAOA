import os
import pyodbc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def get_connection_string() -> str:
    import dbMsSql
    return dbMsSql.connString


# =========================================================
# CONFIG
# =========================================================
OUTPUT_DIR = r"C:\Bikini Atoll\QUANTUM\BACKUP 20251120\projects\ex09\_out20260228\_graph"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================================================
# LABEL MAPPING (DO NOT CHANGE FILTERING)
# =========================================================
LABEL_MAP = {
    "default": "SA-QAOA",
    "multi_angle": "MA-QAOA",
    "ka": r"$k$A-QAOA",
}

ORDER = ["MA-QAOA", r"$k$A-QAOA", "SA-QAOA"]

COLOUR_MAP = {
    "MA-QAOA": "red",
    r"$k$A-QAOA": "orange",
    "SA-QAOA": "blue",
}

MARKER_MAP = {
    "MA-QAOA": "s",
    r"$k$A-QAOA": "o",
    "SA-QAOA": "D",
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


def plot_combined(df, avg, minv, maxv, std, filename, ylabel,
                  yscale=1, ymax_cap=None, legend_loc="best"):
    """
    Combined chart:
      - Light-coloured vertical bar:  mean ± std
      - Black error-bar line:         min .. max
      - Coloured line + markers:      mean
    Series are offset horizontally so the bars don't overlap.
    """
    plt.rcParams.update({
        "font.size": 20,
        "axes.labelsize": 20,
        "xtick.labelsize": 20,
        "ytick.labelsize": 20,
        "legend.fontsize": 20,
    })
    fig, ax = plt.subplots(figsize=(10, 6))

    all_x = []

    # horizontal offsets: MA stays on the integer x, KA shifts right,
    # SA shifts further right. Each series' marker AND its bar use the
    # same x so the marker is always centred on its bar.
    bar_width = 0.15
    step = bar_width + 0.02
    offsets = [i * step for i in range(len(ORDER))]

    for i, label in enumerate(ORDER):
        d = df[df["Label"] == label].sort_values("Layers")

        if d.empty:
            continue

        x = d["Layers"].astype(int).to_numpy()
        y = d[avg].astype(float).to_numpy() / yscale
        ymin = d[minv].astype(float).to_numpy() / yscale
        ymax = d[maxv].astype(float).to_numpy() / yscale
        s = d[std].fillna(0).astype(float).to_numpy() / yscale

        all_x.extend(x)
        x_off = x + offsets[i]
        colour = COLOUR_MAP[label]

        # truncate bars / errorbars at ymax_cap if provided
        bar_top = y + s
        err_top = ymax
        if ymax_cap is not None:
            bar_top = np.minimum(bar_top, ymax_cap)
            err_top = np.minimum(err_top, ymax_cap)
        bar_bottom = y - s

        # ±1 std bar (light shade)
        ax.bar(
            x_off,
            height=bar_top - bar_bottom,
            bottom=bar_bottom,
            width=bar_width,
            color=colour,
            alpha=0.25,
            edgecolor="none",
            zorder=1,
        )

        # min / max black error bars
        ax.errorbar(
            x_off, y,
            yerr=[y - ymin, err_top - y],
            fmt="none",
            ecolor="black",
            elinewidth=1,
            capsize=0,
            zorder=2,
        )

        # mean line + marker (same x as the bar)
        ax.plot(
            x_off, y,
            label=label,
            color=colour,
            marker=MARKER_MAP[label],
            linewidth=2,
            markersize=8,
            zorder=3,
        )

    ax.set_xlabel(r"$p$")
    ax.set_ylabel(ylabel)
    ax.grid(True)

    setup_integer_xaxis(ax, all_x)

    ax.legend(loc=legend_loc)
    plt.tight_layout()

    svg_filename = os.path.splitext(filename)[0] + ".svg"
    plt.savefig(os.path.join(OUTPUT_DIR, svg_filename), format="svg")
    plt.close()

    print(f"Exported: {svg_filename}")


# =========================================================
# EXPORT CHARTS
# =========================================================
plot_combined(df, "AR_Avg", "AR_Min", "AR_Max", "AR_StdDev",
              "AR.svg", "AR", ymax_cap=1.0)

plot_combined(df, "NFEV_Avg", "NFEV_Min", "NFEV_Max", "NFEV_StdDev",
              "NFEV.svg", r"nfev ($\times 10^3$)", yscale=1000,
              legend_loc="upper left")

print("\nDONE.")