import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
import numpy as np

def plot_donor_data(df, x_col):
    """
    Plot donor data side-by-side for Black and White cohorts
    TP-1 -> red circle, TP-2 -> purple circle
    """
    df["PID"] = df["PID"].astype(str)
    races = ["Black", "White"]
    fig, axes = plt.subplots(1, 2, figsize=(14, 10), sharex=True)  # remove sharey=True

    for ax, race in zip(axes, races):
        race_df = df[df["Race"] == race].dropna(subset=[x_col])

        for donor, group in race_df.groupby("PID"):
            # Sort by Donation Year to determine older vs newer
            group_sorted = group.sort_values("Donation Year")
            colors = ["purple", "red"]  # TP-1 -> red, TP-2 -> purple

            # Plot gray lines connecting the points
            ax.plot(group_sorted[x_col], [donor]*len(group_sorted),
                    color="gray", alpha=0.5, linewidth=2, zorder=1)

            # Scatter points with colors based on order
            for x, color in zip(group_sorted[x_col], colors):
                ax.scatter(x, donor, color=color, edgecolor="black", s=300, zorder=2)

                # Special markers
                if donor == "AAAADB":
                    x_color = "#00FFFF"
                elif donor in ["AAAACJ", "AAAADK", "AAAAEH", "AAAAEN"]:
                    x_color = "lime"  # fluorescent green
                else:
                    x_color = "black"

                ax.scatter(x, donor, color=x_color, marker="x", s=250, zorder=3)

        ax.set_title(f"{race} Cohort")
        ax.set_ylabel("PID")
        ax.set_xlabel(x_col)
        ax.grid(True, linestyle="--", alpha=0.5)

    # Add a single legend for the color meaning
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=15, label='TP-1'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='purple', markersize=15, label='TP-2'),
        Line2D([0], [0], marker='x', color='#00FFFF', markersize=15, linestyle='None', label='1 year TP diff'),
        Line2D([0], [0], marker='x', color='lime', markersize=15, linestyle='None', label='Age group 60-70'),
    ]
    axes[1].legend(handles=legend_elements, loc='upper left')

    plt.suptitle(f"Donor Trajectories by Race: {x_col} (All subjects)", fontsize=14)
    plt.tight_layout()
    plt.savefig(f"data/hari_BC/{x_col.replace(' ', '')}_all_subjects.png", dpi=300)


def plot_donor_data_by_age(df, x_col):
    """
    Plot donor data side-by-side for Black and White cohorts,
    separately for donors with older donation age in 0–40 and 40–60.
    Older donation year -> purple circle (first donation), newer donation year -> red circle (last donation).
    Vertical lines showing average values for older (purple) and newer (red) donations per race.
    Only plots donors with at least two timepoints (paired values).
    """
    df = df.copy()
    df["PID"] = df["PID"].astype(str)

    # Determine the older (first) donation age for each donor
    older_ages = (
        df.sort_values("Donation Year")
          .groupby("PID")
          .first()["Age"]
          .rename("OlderAge")
    )
    df = df.merge(older_ages, on="PID", how="left")

    # Define age bins
    age_bins = [(20, 40), (40, 60), (25, 55), (0, 100)]

    for low, high in age_bins:
        subset = df[(df["OlderAge"] >= low) & (df["OlderAge"] < high)]
        if subset.empty:
            print(f"No donors in age range {low}-{high}")
            continue

        races = ["Black", "White"]
        fig, axes = plt.subplots(1, 2, figsize=(14, 10), sharex=True)

        for ax, race in zip(axes, races):
            race_df = subset[subset["Race"] == race].dropna(subset=[x_col])

            older_values = []
            newer_values = []

            for donor, group in race_df.groupby("PID"):
                # Sort by donation year
                group_sorted = group.sort_values("Donation Year")
                values = group_sorted[x_col].values
                n_vals = len(values)

                # Only plot if the donor has both timepoints
                if n_vals < 2:
                    continue
                if donor == "AAAADB" and high != 100:
                    continue  # Exclude AAAADB except in the all-subjects plot

                # Connect points
                ax.plot(values, [donor]*n_vals, color="gray", alpha=0.5, linewidth=2, zorder=1)

                # Older (first)
                x_old = values[0]
                ax.scatter(x_old, donor, color="purple", edgecolor="black", s=300, zorder=2)

                # Special markers
                if donor == "AAAADB":
                    x_color = "#00FFFF"
                elif donor in ["AAAACJ", "AAAADK", "AAAAEH", "AAAAEN"]:
                    x_color = "lime"  # fluorescent green
                else:
                    x_color = "black"

                ax.scatter(x_old, donor, color=x_color, marker="x", s=250, zorder=3)
                older_values.append(x_old)

                # Newer (last)
                x_new = values[-1]
                ax.scatter(x_new, donor, color="red", edgecolor="black", s=300, zorder=2)

                # Special markers
                if donor == "AAAADB":
                    x_color = "#00FFFF"
                elif donor in ["AAAACJ", "AAAADK", "AAAAEH", "AAAAEN"]:
                    x_color = "lime"  # fluorescent green
                else:
                    x_color = "black"

                ax.scatter(x_new, donor, color=x_color, marker="x", s=250, zorder=3)
                newer_values.append(x_new)

            # Plot average vertical lines
            if older_values:
                avg_older = np.mean(older_values)
                ax.axvline(avg_older, color="purple", linestyle="--", linewidth=2)
                ax.text(avg_older, 0.95, f"Avg older: {avg_older:.2f}", transform=ax.get_xaxis_transform(),
                        color="purple", ha="left", va="top", fontsize=10,
                        backgroundcolor='white', alpha=0.8)

            if newer_values:
                avg_newer = np.mean(newer_values)
                ax.axvline(avg_newer, color="red", linestyle="--", linewidth=2)
                ax.text(avg_newer, 0.95, f"Avg newer: {avg_newer:.2f}", transform=ax.get_xaxis_transform(),
                        color="red", ha="left", va="top", fontsize=10,
                        backgroundcolor='white', alpha=0.8)

            ax.set_title(f"{race} Cohort")
            ax.set_ylabel("PID")
            ax.set_xlabel(x_col)
            ax.grid(True, linestyle="--", alpha=0.5)

        # Legend and title
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=15, label='TP-1'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='purple', markersize=15, label='TP-2'),
            Line2D([0], [0], color='red', linestyle='--', linewidth=2, label='Average (TP-1)'),
            Line2D([0], [0], color='purple', linestyle='--', linewidth=2, label='Average (TP-2)'),
        ]
        if low == 0 and high == 100:
            legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=15, label='TP-1'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='purple', markersize=15, label='TP-2'),
            Line2D([0], [0], color='red', linestyle='--', linewidth=2, label='Average (TP-1)'),
            Line2D([0], [0], color='purple', linestyle='--', linewidth=2, label='Average (TP-2)'),
            Line2D([0], [0], marker='x', color='#00FFFF', markersize=15, linestyle='None', label='1 year TP diff'),
            Line2D([0], [0], marker='x', color='lime', markersize=15, linestyle='None', label='Age group 60-70'),
        ]
        axes[1].legend(handles=legend_elements, loc='upper left')

        plt.suptitle(f"Donor Trajectories by Race: {x_col} (Ages {low}–{high})", fontsize=14)
        if low == 0 and high == 100:
            plt.suptitle(f"Donor Trajectories by Race: {x_col} (All subjects)", fontsize=14)
        plt.tight_layout()
        out_file = f"data/hari_BC/{x_col.replace(' ', '')}_age_{low}-{high}.png"
        if low == 0 and high == 100:
            out_file = f"data/hari_BC/{x_col.replace(' ', '')}_all_subjects_no_exclusions.png"
        plt.savefig(out_file, dpi=300)
        plt.close(fig)
        print(f"Saved plot: {out_file}")


# Example usage

# Load your CSV
df = pd.read_csv("data/hari_BC/csv/BnW_combined_with_IHC.csv")

# plot_donor_data(df, "Donation Year")
# plot_donor_data_by_age(df, "Stromal_Mean")

stains = ["ZEB1_", "FOXA1_", "ELF5 HN1+2_", "ER HN1+2_", "p63 DAK HN1+2_", "CK14 HN1+2_", "EHF HN1+2_", "cKIT HN1+2_"]
scores = ["Positivity", "H-Score"]

for stain in stains:
    for score in scores:
        col_name = f"{stain}{score}"
        if col_name in df.columns:
            plot_donor_data(df, col_name)
        else:
            print(f"Column {col_name} not found in DataFrame.")