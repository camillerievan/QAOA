import os
import sys
import warnings

import pandas as pd
import pyodbc
import matplotlib.pyplot as plt


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
LAYERS = 5
OUTPUT_DIR = r"C:\Bikini Atoll\QUANTUM\BACKUP 20251120\projects\ex09\_out20260228\_graph"
SAVE_PNG = True
DISPLAY = True

# Shaded band mode: "minmax" or "std"
BAND_MODE = "std"


def get_connection_string() -> str:
    """
    Reads the connection string from dbMsSql.py.
    """
    try:
        import dbMsSql
    except ImportError as exc:
        raise ImportError(
            "Could not import dbMsSql.py. Make sure this file is in the same folder "
            "as this script, or available on PYTHONPATH."
        ) from exc

    if not hasattr(dbMsSql, "connString"):
        raise AttributeError("dbMsSql.py does not contain a variable named connString.")

    return dbMsSql.connString


def read_sql_df(sql: str, params=None) -> pd.DataFrame:
    """
    Executes SQL and returns a DataFrame.
    Suppresses the common pandas/pyodbc warning.
    """
    conn_string = get_connection_string()

    with pyodbc.connect(conn_string) as conn:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="pandas only supports SQLAlchemy connectable.*",
                category=UserWarning,
            )
            df = pd.read_sql(sql, conn, params=params)

    return df


def get_all_graph_ids() -> list[int]:
    """
    Gets all graph primary keys from the graph table.
    """
    sql = """
    select g.graph_pk
    from dbo.tb_Graph g
    order by g.graph_pk;
    """

    df = read_sql_df(sql)

    if df.empty:
        return []

    return df["graph_pk"].astype(int).tolist()


def load_data(graph_pk: int, layers: int) -> pd.DataFrame:
    sql = """
    select
          t.graph_fk
        , std.Code
        , rl.[layer]
        , rl.[renyientropy]
        , std.[Order] as study_order
        , t.AR
    from dbo.tb_Test t
        inner join dbo.tb_Test_RenyiEntropyByLayer rl
            on t.[test_pk] = rl.[test_fk]
        inner join dbo.tb_C_AngleStudy std
            on t.angle_study = std.pk
    where t.layers = ?
      and t.graph_fk = ?
    order by
          t.graph_fk
        , std.[Order]
        , rl.[layer];
    """

    return read_sql_df(sql, params=[layers, graph_pk])


def add_origin_point(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensures each angle study starts from (0, 0).
    """
    if df.empty:
        return df

    base_rows = (
        df[["graph_fk", "Code", "study_order", "AR"]]
        .drop_duplicates()
        .copy()
    )
    base_rows["layer"] = 0
    base_rows["renyientropy"] = 0.0

    combined = pd.concat([base_rows, df], ignore_index=True)
    combined = (
        combined
        .drop_duplicates(subset=["graph_fk", "Code", "layer"], keep="first")
        .sort_values(["study_order", "Code", "layer"])
        .reset_index(drop=True)
    )
    return combined


def normalise_graph(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalises one graph so that its maximum renyientropy becomes 1.
    This is done per graph (across all MA/KA/SA lines together).
    """
    if df.empty:
        return df

    graph_max = df["renyientropy"].max()

    if pd.isna(graph_max) or graph_max <= 0:
        df = df.copy()
        df["magic_norm"] = 0.0
        return df

    df = df.copy()
    df["magic_norm"] = df["renyientropy"] / graph_max
    return df


def build_all_normalised_graphs(layers: int) -> pd.DataFrame:
    """
    Loads every graph, adds origin points, normalises each graph to max=1,
    and returns one combined DataFrame.
    """
    graph_ids = get_all_graph_ids()

    if not graph_ids:
        return pd.DataFrame()

    all_parts = []

    for graph_pk in graph_ids:
        print(f"Processing graph {graph_pk}...")
        df_graph = load_data(graph_pk=graph_pk, layers=layers)

        if df_graph.empty:
            print(f"Skipping graph {graph_pk}: no data found.")
            continue

        df_graph = add_origin_point(df_graph)
        df_graph = normalise_graph(df_graph)
        all_parts.append(df_graph)

    if not all_parts:
        return pd.DataFrame()

    return pd.concat(all_parts, ignore_index=True)


def compute_summary(df_all: pd.DataFrame) -> pd.DataFrame:
    """
    Computes average, min, max, std and counts per layer/code across graphs.
    """
    if df_all.empty:
        return pd.DataFrame()

    summary = (
        df_all.groupby(["Code", "layer"], as_index=False)
        .agg(
            magic_mean=("magic_norm", "mean"),
            magic_min=("magic_norm", "min"),
            magic_max=("magic_norm", "max"),
            magic_std=("magic_norm", "std"),
            sample_count=("magic_norm", "count"),
        )
    )

    summary["magic_std"] = summary["magic_std"].fillna(0.0)
    summary["band_low_std"] = (summary["magic_mean"] - summary["magic_std"]).clip(lower=0.0)
    summary["band_high_std"] = (summary["magic_mean"] + summary["magic_std"]).clip(upper=1.0)

    return summary


def plot_average_normalised(
    summary_df: pd.DataFrame,
    layers: int,
    output_dir: str = ".",
    save_png: bool = True,
    display: bool = True,
    band_mode: str = "minmax",
) -> None:
    """
    Plots the average normalised curves for MA / KA / SA with shaded bands.
    band_mode:
        - "minmax": shade from min to max
        - "std": shade mean ± std
    """
    if summary_df.empty:
        print("No summary data found.")
        return

    plt.figure(figsize=(10, 6))

    desired_order = ["ma", "ka", "sa"]

    style_map = {
        "ma": ("red", "s"),
        "ka": ("orange", "o"),
        "sa": ("blue", "D"),
    }

    label_map = {
        "ma": "MA",
        "ka": "KA",
        "sa": "SA",
    }

    available_codes = {
        str(code).strip().lower(): code
        for code in summary_df["Code"].drop_duplicates()
    }

    ordered_codes = [available_codes[c] for c in desired_order if c in available_codes]

    for code in ordered_codes:
        subset = summary_df[summary_df["Code"] == code].sort_values("layer")
        code_key = str(code).strip().lower()
        colour, marker = style_map.get(code_key, ("black", "x"))
        short_label = label_map.get(code_key, str(code).upper())

        x = subset["layer"].to_numpy()
        y = subset["magic_mean"].to_numpy()

        if band_mode.lower() == "std":
            y_low = subset["band_low_std"].to_numpy()
            y_high = subset["band_high_std"].to_numpy()
            label = f"{short_label} mean ± std"
        else:
            y_low = subset["magic_min"].to_numpy()
            y_high = subset["magic_max"].to_numpy()
            label = f"{short_label} mean (min-max band)"

        plt.fill_between(x, y_low, y_high, color=colour, alpha=0.18)
        plt.plot(
            x,
            y,
            color=colour,
            marker=marker,
            linewidth=2,
            markersize=6,
            label=label,
        )

    plt.title(f"Average normalised magic across all graphs (layers = {layers})")
    plt.xlabel("p = layer")
    plt.ylabel("normalised magic")
    plt.xlim(left=0)
    plt.ylim(0, 1.02)
    plt.xticks(sorted(summary_df["layer"].dropna().unique()))
    plt.grid(True)
    plt.axhline(0, linewidth=1)
    plt.axvline(0, linewidth=1)
    plt.legend(loc="upper right")
    plt.tight_layout()

    if save_png:
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(
            output_dir,
            f"all_graphs_average_normalised_p{layers}_{band_mode.lower()}.png"
        )
        plt.savefig(output_file, dpi=150)
        print(f"Saved image to: {output_file}")

    if display:
        plt.show()
    else:
        plt.close()


def save_summary_csv(summary_df: pd.DataFrame, layers: int, output_dir: str) -> None:
    """
    Saves the summary table to CSV.
    """
    if summary_df.empty:
        return

    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"all_graphs_average_normalised_p{layers}.csv")
    summary_df.to_csv(output_file, index=False)
    print(f"Saved CSV to: {output_file}")


def main() -> None:
    layers = LAYERS
    output_dir = OUTPUT_DIR
    save_png = SAVE_PNG
    display = DISPLAY
    band_mode = BAND_MODE

    # Optional command line usage:
    #   python plot_magic_graph_average_normalised.py
    #   python plot_magic_graph_average_normalised.py 5
    #   python plot_magic_graph_average_normalised.py 5 "C:\\temp"
    #   python plot_magic_graph_average_normalised.py 5 "C:\\temp" true false minmax
    if len(sys.argv) >= 2:
        layers = int(sys.argv[1])
    if len(sys.argv) >= 3:
        output_dir = sys.argv[2]
    if len(sys.argv) >= 4:
        save_png = sys.argv[3].strip().lower() in ("1", "true", "yes", "y")
    if len(sys.argv) >= 5:
        display = sys.argv[4].strip().lower() in ("1", "true", "yes", "y")
    if len(sys.argv) >= 6:
        band_mode = sys.argv[5].strip().lower()

    df_all = build_all_normalised_graphs(layers=layers)

    if df_all.empty:
        print("No graph data found.")
        return

    summary_df = compute_summary(df_all)

    if summary_df.empty:
        print("No summary could be computed.")
        return

    save_summary_csv(summary_df=summary_df, layers=layers, output_dir=output_dir)

    plot_average_normalised(
        summary_df=summary_df,
        layers=layers,
        output_dir=output_dir,
        save_png=save_png,
        display=display,
        band_mode=band_mode,
    )


if __name__ == "__main__":
    main()
