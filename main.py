import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

MENU = [
    ("Run core system (ex09_x.py)",                 "ex09_x.py"),
    ("Plot magic graph",                            "plot/plot_magic_graph.py"),
    ("Plot magic graph (average normalised)",       "plot/plot_magic_graph_average_normalised.py"),
    ("Plot summary",                                "plot/plot_summary.py"),
    ("Dante to SQL",                                "dante_to_SQL.py"),
]


def run(script):
    path = os.path.join(HERE, script)
    if not os.path.isfile(path):
        print(f"[error] script not found: {path}")
        return
    result = subprocess.run([sys.executable, path], cwd=HERE)
    print(f"\n[{script} exited with code {result.returncode}]")


def main():
    while True:
        print("\n=== ex09 menu ===")
        for i, (label, _) in enumerate(MENU, 1):
            print(f"  {i}. {label}")
        print("  0. Exit")

        choice = input("Select: ").strip()
        if choice == "0" or choice.lower() in ("q", "quit", "exit"):
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(MENU)):
            print("Invalid selection.")
            continue
        run(MENU[int(choice) - 1][1])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
