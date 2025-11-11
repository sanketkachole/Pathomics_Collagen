import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

def assign_age_color(row):
    # keep the special-case color assignment you had
    age = row["Age"]
    if 20 <= age <= 40:
        return "green"
    elif 40 < age <= 60:
        return "blue"
    else:
        return "red"


if __name__ == "__main__":
    # Read the CSV file
    df = pd.read_csv("data/hari_BC/csv/BnW_combined.csv")

    df_black = df[df["Race"] == "Black"].copy()
    df_white = df[df["Race"] == "White"].copy()

    dfs = [df_black, df_white]
    save_names = ["Black", "White"]

    for df, save_name in zip(dfs, save_names):
        # Drop missing
        df = df.dropna(subset=["Age", "Stromal_Mean"]).copy()

        # Apply color assignment
        df["Color"] = df.apply(assign_age_color, axis=1)

        ################## YEARS VS ENTROPY CHANGE PLOT ##################
        # Create scatter plot (s=300 circles)
        plt.figure(figsize=(8, 6))
        plt.scatter(df["Stromal_Mean"], df["Age"],
                    c=df["Color"], alpha=0.7, edgecolors="black", s=200)

        # ---- Overlay special 'x' markers for PIDs on this race-level scatter ----
        for _, row in df.iterrows():
            pid = str(row["PID"])
            x_val = row["Stromal_Mean"]
            y_val = row["Age"]

            if pid == "AAAADB":
                x_color = "#00FFFF"
            elif pid in ["AAAACJ", "AAAADK", "AAAAEH", "AAAAEN"]:
                x_color = "lime"
            else:
                x_color = "black"

            plt.scatter(x_val, y_val, color=x_color, marker="x", s=250, zorder=3)

        # ---- Add trend arrow (only if >=2 points) ----
        x = df["Stromal_Mean"].values
        y = df["Age"].values
        if len(x) >= 2:
            m, b = np.polyfit(x, y, 1)
            x_min, x_max = np.min(x), np.max(x)
            y_min, y_max = m * x_min + b, m * x_max + b

            # Draw arrow from (x_min, y_min) → (x_max, y_max)
            plt.arrow(
                x_min, y_min,
                (x_max - x_min), (y_max - y_min),
                color="black", width=0.001, head_width=0.02,
                length_includes_head=True, alpha=0.7,
                label="Trend"
            )
        else:
            plt.gca().text(0.02, 0.95, "Trend: n<2", transform=plt.gca().transAxes, fontsize=9,
                           verticalalignment='top')

        # Add labels, title, grid
        plt.xlabel("Stromal_Mean")
        plt.ylabel("Age")
        plt.title(f"Age vs Stromal_Mean — Race: {save_name}")
        plt.grid(True, linestyle="--", alpha=0.5)

        # Unified legend for the race-level plot
        legend_elements = [
            Line2D([0], [0], marker='x', color='#00FFFF',
                   markersize=10, linestyle='None', label='1 year TP diff'),
            Line2D([0], [0], marker='x', color='lime',
                   markersize=10, linestyle='None', label='Age group 60-70'),
        ]
        plt.legend(handles=legend_elements, loc='best', frameon=True)

        # Save figure
        plt.savefig(f"data/hari_BC/plots/otsu4_{save_name}_age_vs_entropy.png",
                    dpi=300, bbox_inches="tight")
        plt.close()

        # Ensure numeric types
        df["Donation Year"] = pd.to_numeric(df["Donation Year"], errors="coerce")
        df["Stromal_Mean"] = pd.to_numeric(df["Stromal_Mean"], errors="coerce")

        # Prepare lists to collect per-subject metrics
        pids = []
        year_diffs = []
        stromal_diffs = []
        abs_stromal_diffs = []
        colors = []

        # Group by subject (PID)
        for pid, grp in df.groupby("PID"):
            grp = grp.dropna(subset=["Donation Year", "Stromal_Mean"])
            if len(grp) < 2:
                continue  # need at least two timepoints

            grp_sorted = grp.sort_values("Donation Year", kind="mergesort")
            first = grp_sorted.iloc[0]
            second = grp_sorted.iloc[1]

            year1 = int(first["Donation Year"])
            year2 = int(second["Donation Year"])
            s1 = float(first["Stromal_Mean"])
            s2 = float(second["Stromal_Mean"])

            year_diff = year2 - year1
            stromal_diff = s1 - s2
            abs_diff = abs(stromal_diff)

            if stromal_diff > 0:
                col = "green"   # entropy increased
            elif stromal_diff < 0:
                col = "red"     # entropy decreased
            else:
                col = "gray"

            pids.append(pid)
            year_diffs.append(year_diff)
            stromal_diffs.append(stromal_diff)
            abs_stromal_diffs.append(abs_diff)
            colors.append(col)

        summary = pd.DataFrame({
            "PID": pids,
            "year_diff": year_diffs,
            "stromal_diff": stromal_diffs,
            "abs_stromal_diff": abs_stromal_diffs,
            "color": colors
        })

        if not summary.empty:
            plt.figure(figsize=(8, 6))
            plt.scatter(summary["abs_stromal_diff"], summary["year_diff"],
                        c=summary["color"], alpha=0.8, edgecolors="black", s=200)

            # Overlay special 'x' markers for PIDs on the summary scatter
            for _, row in summary.iterrows():
                pid = str(row["PID"])
                x_val = row["abs_stromal_diff"]
                y_val = row["year_diff"]

                if pid == "AAAADB":
                    x_color = "#00FFFF"
                elif pid in ["AAAACJ", "AAAADK", "AAAAEH", "AAAAEN"]:
                    x_color = "lime"
                else:
                    x_color = "black"

                plt.scatter(x_val, y_val, color=x_color, marker="x", s=250, zorder=3)

            # --- Add general trend line (if at least 2 summary points) ---
            if len(summary) >= 2:
                m, b = np.polyfit(summary["abs_stromal_diff"], summary["year_diff"], 1)
                xs = np.linspace(summary["abs_stromal_diff"].min(), summary["abs_stromal_diff"].max(), 100)
                plt.plot(xs, m * xs + b, linestyle="--", linewidth=1, color="magenta")

            # --- Second trend line excluding special PIDs ---
            special_pids = ["AAAADB", "AAAACJ", "AAAADK", "AAAAEH", "AAAAEN"]
            summary_filtered = summary[~summary["PID"].isin(special_pids)]
            if len(summary_filtered) >= 2:
                m2, b2 = np.polyfit(summary_filtered["abs_stromal_diff"], summary_filtered["year_diff"], 1)
                xs2 = np.linspace(summary_filtered["abs_stromal_diff"].min(), summary_filtered["abs_stromal_diff"].max(), 100)
                plt.plot(xs2, m2 * xs2 + b2, linestyle="--", linewidth=1, color="dodgerblue",
                        label=f"Trend (no x-PIDs): y={m2:.2f}x+{b2:.2f}")

            # --- Legend: include color patches + trend + special 'x' markers + TP-1/TP-2 markers ---
            green_patch = mpatches.Patch(color="green", label="Entropy increased")
            red_patch = mpatches.Patch(color="red", label="Entropy decreased")

            special_legend = [
                Line2D([0], [0], marker='x', color='#00FFFF',
                    markersize=10, linestyle='None', label='1 year TP diff'),
                Line2D([0], [0], marker='x', color='lime',
                    markersize=10, linestyle='None', label='Age group 60-70'),
                Line2D([0], [0], color="magenta", linestyle="--",
                    label=f"Trend (all subjects)"),
                Line2D([0], [0], color="dodgerblue", linestyle="--",
                    label=f"Trend (w/o excluded subjects)")
            ]

            plt.legend(handles=[green_patch, red_patch] + special_legend, loc="best", frameon=True)

            # Labels and formatting
            plt.xlabel("Stromal entropy change")
            plt.ylabel("Years between two timepoints")
            plt.title(f"Year difference vs Stromal Entropy Change: {save_name}")
            plt.grid(True, linestyle="--", alpha=0.5)

            outpath = f"data/hari_BC/plots/otsu_4_{save_name}_years_vs_entropy_change.png"
            plt.savefig(outpath, dpi=300, bbox_inches="tight")
            plt.close()

            print(f"Saved: {outpath}")
        else:
            print("No subjects with ≥2 timepoints found.")