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
DISPLAY = False


def get_connection_string() -> str:
    """
    Reads the connection string from dbMsSql.py.

    Expected in dbMsSql.py:
        connString = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=...'
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
    The pandas warning about pyodbc is harmless, so we suppress it.
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
    Ensures each angle study starts from (0, 0), i.e.:
      layer = 0
      renyientropy = 0
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


def format_ratio(value) -> str:
    """
    Formats approximation ratio for legend display.
    """
    if pd.isna(value):
        return "N/A"
    return f"{float(value):.4f}"


def plot_graph(
    df: pd.DataFrame,
    graph_pk: int,
    output_dir: str = ".",
    save_png: bool = True,
    display: bool = True,
    layers: int = 5,
) -> None:
    if df.empty:
        print(f"Skipping graph {graph_pk}: no data found.")
        return

    df = add_origin_point(df)

    # ------------------------------------------------------------------
    # FORCE ORDER: MA -> KA -> SA
    # ------------------------------------------------------------------
    desired_order = ["ma", "ka", "sa"]

    # Map actual codes present
    code_map = {
        str(code).strip().lower(): code
        for code in df["Code"].drop_duplicates()
    }

    ordered_codes = [
        code_map[c] for c in desired_order if c in code_map
    ]

    plt.rcParams.update({
        "font.size": 13.5,
        "axes.labelsize": 15,
        "xtick.labelsize": 13.5,
        "ytick.labelsize": 13.5,
        "legend.fontsize": 13.5,
    })

    plt.figure(figsize=(10, 6))

    style_map = {
        "ma": ("red", "s"),
        "ka": ("orange", "o"),
        "sa": ("blue", "D"),
    }

    label_map = {
        "ma": "MA-QAOA",
        "ka": r"$k$A-QAOA",
        "sa": "SA-QAOA",
    }

    ratio_map = (
        df[["Code", "AR"]]
        .drop_duplicates(subset=["Code"])
        .set_index("Code")["AR"]
        .to_dict()
    )

    # ------------------------------------------------------------------
    # PLOT IN FIXED ORDER
    # ------------------------------------------------------------------
    for code in ordered_codes:
        subset = df[df["Code"] == code].sort_values("layer")

        code_key = str(code).strip().lower()
        colour, marker = style_map.get(code_key, ("black", "x"))
        base_label = label_map.get(code_key, str(code))
        approx_ratio = ratio_map.get(code, None)

        label = f"{base_label} (AR={format_ratio(approx_ratio)})"

        plt.plot(
            subset["layer"],
            subset["renyientropy"],
            color=colour,
            marker=marker,
            linewidth=2,
            markersize=8,
            label=label,
        )

    plt.xlabel(r"$p$")
    plt.ylabel(r"$M_2$")
    plt.xticks(sorted(df["layer"].dropna().unique()))
    plt.xlim(left=0)
    plt.ylim(bottom=0)
    plt.grid(True)
    plt.axhline(0)
    plt.axvline(0)
    plt.legend(loc="upper right")
    plt.tight_layout()

    if save_png:
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"graph_{graph_pk}_p{layers}_magic.png")
        plt.savefig(output_file, dpi=150)
        print(f"Saved image to: {output_file}")

    if display:
        plt.show()
    else:
        plt.close()


def main() -> None:
    layers = LAYERS
    output_dir = OUTPUT_DIR
    save_png = SAVE_PNG
    display = DISPLAY

    # Optional command line usage:
    #   python plot_magic_graph_with_ratio.py
    #   python plot_magic_graph_with_ratio.py 5
    #   python plot_magic_graph_with_ratio.py 5 "C:\\temp"
    #   python plot_magic_graph_with_ratio.py 5 "C:\\temp" true false
    if len(sys.argv) >= 2:
        layers = int(sys.argv[1])
    if len(sys.argv) >= 3:
        output_dir = sys.argv[2]
    if len(sys.argv) >= 4:
        save_png = sys.argv[3].strip().lower() in ("1", "true", "yes", "y")
    if len(sys.argv) >= 5:
        display = sys.argv[4].strip().lower() in ("1", "true", "yes", "y")

    graph_ids = get_all_graph_ids()

    if not graph_ids:
        print("No graphs found.")
        return

    print(f"Found {len(graph_ids)} graphs: {graph_ids}")

    for graph_pk in graph_ids:
        print(f"Processing graph {graph_pk}...")
        df = load_data(graph_pk=graph_pk, layers=layers)
        plot_graph(
            df=df,
            graph_pk=graph_pk,
            output_dir=output_dir,
            save_png=save_png,
            display=display,
            layers=layers,
        )


if __name__ == "__main__":
    main()
