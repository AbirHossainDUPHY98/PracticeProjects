import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from scipy.stats import pearsonr, spearmanr
from scipy import stats
from scipy.optimize import curve_fit

RESULTS_DIR = "../results"
os.makedirs(RESULTS_DIR, exist_ok=True)

MIN_PATENTS    = 500
MIN_INVENTORS  = 2_000
MIN_RD_GDP     = 1.0
MIN_POPULATION = 5_000_000

HIGH_INCOME = [
    "ABW", "AND", "ARE", "ATG", "AUS", "AUT", "BEL", "BHR", "BHS", "BMU",
    "BRB", "BRN", "CAN", "CHE", "CHL", "CUW", "CYM", "CYP", "CZE", "DEU",
    "DNK", "ESP", "EST", "FIN", "FRA", "FRO", "GBR", "GIB", "GRL", "GUM",
    "HKG", "HUN", "IMN", "IRL", "ISL", "ISR", "ITA", "JPN", "KOR", "KWT",
    "LIE", "LTU", "LUX", "LVA", "MAC", "MAF", "MCO", "MLT", "MNP", "NCL",
    "NLD", "NOR", "NZL", "OMN", "PAN", "POL", "PRI", "PRT", "PYF", "QAT",
    "ROU", "SAU", "SGP", "SMR", "SVK", "SVN", "SWE", "SXM", "SYC", "TCA",
    "TUV", "TWN", "URY", "USA", "VAT", "VGB", "VIR",
]
EMERGING_ECONOMIES = [
    "ARG", "BGD", "BRA", "BGR", "CHL", "CHN", "COL", "EGY", "GRC", "HUN",
    "IND", "IDN", "IRN", "ISR", "KAZ", "MYS", "MEX", "MAR", "NGA", "PAK",
    "PER", "PHL", "POL", "ROU", "RUS", "SAU", "ZAF", "THA", "TUR", "UKR",
    "ARE", "VNM",
]

def load_data():
    df_A = pd.read_parquet("../processed/analytical_data/subset_A.parquet")
    df_B = pd.read_parquet("../processed/analytical_data/subset_B.parquet")
    print(f"Loaded subset_A: {df_A.shape}")
    print(f"Loaded subset_B: {df_B.shape}")
    return df_A, df_B

def aggregate_subsets(df_A, df_B):
    df_B_agg = df_B.groupby(["country_code", "year"], observed=True).agg(
        patent_count=("patent_count", "sum"),
        inventor_count=("inventor_count", "sum"),
        patent_type=("patent_type", "count"),
        rd_gdp=("rd_gdp", "first"),
        gdp_growth=("gdp_growth", "first"),
        population=("population", "first"),
        tertiary_enrollment=("tertiary_enrollment", "first"),
    ).reset_index()

    df_A_agg = df_A.groupby(["country_code", "year"], observed=True).agg(
        patent_count=("patent_count", "sum"),
        population=("population", "first"),
        gdp_growth=("gdp_growth", "first"),
    ).reset_index()

    df_merged = pd.merge(
        df_A_agg[["country_code", "year", "patent_count", "population", "gdp_growth"]],
        df_B_agg[["country_code", "year", "rd_gdp"]],
        on=["country_code", "year"],
        how="inner",
    )

    return df_B_agg, df_merged

def analyse_rd_vs_patents(df_B_agg):
    df = df_B_agg.copy()
    df["log_patents"] = np.log1p(df["patent_count"])

    r_raw,  p_raw  = pearsonr(df["rd_gdp"], df["patent_count"])
    rho,    p_rho  = spearmanr(df["rd_gdp"], df["patent_count"])
    r_log,  p_log  = pearsonr(df["rd_gdp"], df["log_patents"])

    print("\n[RD vs Patents]")
    print(f"  Pearson r (raw)   = {r_raw:.3f},  p = {p_raw:.3e}")
    print(f"  Spearman rho      = {rho:.3f},  p = {p_rho:.3e}")
    print(f"  Pearson r (log)   = {r_log:.3f},  p = {p_log:.3e}")

    # Plot 1 — raw scatter
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(data=df, x="rd_gdp", y="patent_count",
                    alpha=0.7, edgecolor="w", s=60, ax=ax)
    ax.set_xlabel("R&D Spending (% of GDP)")
    ax.set_ylabel("Total Patent Count")
    ax.set_title("R&D Spending vs Patent Output (Raw)")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, "fig1_rd_vs_patents_raw.png"), dpi=150)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.regplot(data=df, x="rd_gdp", y="patent_count",
                scatter_kws={"alpha": 0.6, "s": 40},
                line_kws={"color": "red"}, ax=axes[0])
    axes[0].set_xlabel("R&D Spending (% of GDP)")
    axes[0].set_ylabel("Total Patent Count")
    axes[0].set_title("Raw Scale")
    axes[0].grid(alpha=0.3)

    sns.regplot(data=df, x="rd_gdp", y="log_patents",
                scatter_kws={"alpha": 0.6, "s": 40},
                line_kws={"color": "green"}, ax=axes[1])
    axes[1].set_xlabel("R&D Spending (% of GDP)")
    axes[1].set_ylabel("Log(Patent Count + 1)")
    axes[1].set_title("Log-Transformed Scale")
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, "fig2_rd_vs_patents_regplot.png"), dpi=150)
    plt.close(fig)

    return df

def run_ols(df_merged):
    df = df_merged.dropna(subset=["rd_gdp", "population", "patent_count"]).copy()
    df["log_patents"]    = np.log1p(df["patent_count"])
    df["log_population"] = np.log(df["population"])

    y = df["log_patents"]
    X = sm.add_constant(df[["rd_gdp", "log_population"]])
    model = sm.OLS(y, X).fit()

    print("\n[OLS: log_patents ~ rd_gdp + log_population]")
    print(model.params)
    print(f"  R² = {model.rsquared:.3f}")

    residuals = model.resid
    fitted    = model.fittedvalues

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(fitted, residuals, alpha=0.6, edgecolor="w")
    ax.axhline(y=0, color="red", linestyle="--", linewidth=1)
    ax.set_xlabel("Fitted Values (predicted log(patents))")
    ax.set_ylabel("Residuals (actual − predicted)")
    ax.set_title("Residuals vs Fitted Values")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, "fig3_ols_residuals.png"), dpi=150)
    plt.close(fig)

    print(f"  Residuals — mean: {residuals.mean():.4f}, "
          f"std: {residuals.std():.4f}, "
          f"min/max: {residuals.min():.2f}/{residuals.max():.2f}")

def analyse_patents_vs_gdp(df_B_agg):
    df = df_B_agg.dropna(subset=["gdp_growth"]).copy()
    df["log_patents"] = np.log1p(df["patent_count"])

    r_raw,  p_raw  = pearsonr(df["rd_gdp"], df["patent_count"])
    rho,    p_rho  = spearmanr(df["patent_count"], df["gdp_growth"])
    r_log,  p_log  = pearsonr(df["log_patents"], df["gdp_growth"])
    rho_log, p_rho_log = spearmanr(df["log_patents"], df["gdp_growth"])

    print("\n[Patents vs GDP Growth]")
    print(f"  Pearson r (raw rd_gdp vs patents)  = {r_raw:.3f},  p = {p_raw:.3e}")
    print(f"  Spearman rho (patents vs gdp)       = {rho:.3f},  p = {p_rho:.3e}")
    print(f"  Pearson r (log_patents vs gdp)      = {r_log:.3f},  p = {p_log:.3e}")
    print(f"  Spearman rho (log_patents vs gdp)   = {rho_log:.3f},  p = {p_rho_log:.3e}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    sns.scatterplot(data=df, x="patent_count", y="gdp_growth",
                    alpha=0.6, ax=axes[0])
    axes[0].set_xlabel("Patent Count (raw)")
    axes[0].set_ylabel("GDP Growth (% of GDP)")
    axes[0].set_title(f"Raw Scale\nPearson r={r_raw:.2f}, Spearman ρ={rho:.2f}")
    axes[0].axhline(0, color="gray", linestyle="--", linewidth=0.5)

    sns.scatterplot(data=df, x="log_patents", y="gdp_growth",
                    alpha=0.6, ax=axes[1])
    axes[1].set_xlabel("Log(Patents + 1)")
    axes[1].set_ylabel("GDP Growth (%)")
    axes[1].set_title(f"Log Scale\nPearson r={r_log:.2f}, Spearman ρ={rho_log:.2f}")
    axes[1].axhline(0, color="gray", linestyle="--", linewidth=0.5)

    plt.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, "fig4_patents_vs_gdp_raw_log.png"), dpi=150)
    plt.close(fig)

    return df

def analyse_lag_effects(df_B_agg):
    df = df_B_agg.dropna(subset=["gdp_growth"]).copy()
    df["log_patents"] = np.log1p(df["patent_count"])
    df = df.sort_values(["country_code", "year"]).reset_index(drop=True)

    # Build lag columns 1–12
    for lag in range(1, 13):
        df[f"log_patents_lag{lag}"] = (
            df.groupby("country_code", observed=True)["log_patents"].shift(lag)
        )
    df["gdp_growth_lag1"] = (
        df.groupby("country_code", observed=True)["gdp_growth"].shift(1)
    )

    results = []
    for lag in list(range(1, 6)) + list(range(7, 13)):
        col = f"log_patents_lag{lag}"
        tmp = df.dropna(subset=[col, "gdp_growth"])
        if len(tmp) < 100:
            continue
        r, p = spearmanr(tmp[col], tmp["gdp_growth"])
        results.append({"lag": lag, "spearman_r": r, "p_value": p, "n": len(tmp)})

    df_results = pd.DataFrame(results)
    print("\n[Lag Analysis — log_patents_lagN → gdp_growth]")
    print(df_results.to_string(index=False))

    tmp_rev = df.dropna(subset=["gdp_growth_lag1", "log_patents"])
    r_rev, p_rev = spearmanr(tmp_rev["gdp_growth_lag1"], tmp_rev["log_patents"])
    print(f"\n  Reverse lag (gdp_growth_lag1 → log_patents): "
          f"rho={r_rev:.4f}, p={p_rev:.4f}")

    df["rd_group"] = df["rd_gdp"].apply(lambda x: "High_RnD" if x >= 1.0 else "Low_RnD")
    print("\n  By R&D group (lag=1):")
    for group in ["High_RnD", "Low_RnD"]:
        sub = df[df["rd_group"] == group].dropna(subset=["log_patents_lag1", "gdp_growth"])
        r, p = spearmanr(sub["log_patents_lag1"], sub["gdp_growth"])
        print(f"    {group}: rho={r:.4f}, p={p:.4f}, n={len(sub)}")

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(df_results["lag"], df_results["spearman_r"],
            marker="o", color="steelblue", linewidth=2)
    ax.axhline(0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_xlabel("Lag (years)")
    ax.set_ylabel("Spearman ρ")
    ax.set_title("Spearman ρ — log_patents(T) → gdp_growth(T+lag)")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, "fig5_lag_spearman_profile.png"), dpi=150)
    plt.close(fig)

    results2 = []
    for lag in range(6):
        if lag == 0:
            tmp2 = df.dropna(subset=["rd_gdp", "log_patents"])
            r, p = spearmanr(tmp2["rd_gdp"], tmp2["log_patents"])
        else:
            col = f"log_patents_lag{lag}"
            tmp2 = df.dropna(subset=["rd_gdp", col])
            r, p = spearmanr(tmp2["rd_gdp"], tmp2[col])
        results2.append({"lag_years": lag, "spearman_r": r, "p_value": p, "n": len(tmp2)})

    print("\n[R&D → log_patents stability across lags 0–5]")
    print(pd.DataFrame(results2).to_string(index=False))

    return df

def compute_efficiencies(df_B_agg):
    df = df_B_agg[
        (df_B_agg["patent_count"]   >= MIN_PATENTS) &
        (df_B_agg["inventor_count"] >= MIN_INVENTORS) &
        (df_B_agg["rd_gdp"]         >= MIN_RD_GDP) &
        (df_B_agg["population"]     >= MIN_POPULATION)
    ].copy()

    print(f"\n[Efficiency] Rows after filter: {len(df)}  "
          f"| Countries: {df['country_code'].nunique()}")

    df["Efficiency_1"] = (
        df["patent_count"] / (df["rd_gdp"] * df["inventor_count"])
    ) * 1e6

    df["Efficiency_2"] = (
        df["gdp_growth"] / (df["patent_count"] / df["population"])
    ) * 1e6

    ranked1 = (df.groupby("country_code", observed=True)
               .agg(Efficiency_1=("Efficiency_1", "mean"),
                    patent_count=("patent_count", "sum"),
                    rd_gdp=("rd_gdp", "mean"),
                    inventor_count=("inventor_count", "mean"))
               .round(2)
               .sort_values("Efficiency_1", ascending=False))
    print("\nTop 10 — R&D → Patent Efficiency (Efficiency_1):")
    print(ranked1.head(10))

    ranked2 = (df.groupby("country_code", observed=True)
               .agg(Efficiency_2=("Efficiency_2", "mean"),
                    patent_count=("patent_count", "sum"),
                    rd_gdp=("rd_gdp", "mean"),
                    inventor_count=("inventor_count", "mean"))
               .round(2)
               .sort_values("Efficiency_2", ascending=False))
    print("\nTop 10 — Patent → GDP Growth Efficiency (Efficiency_2):")
    print(ranked2.head(10))

    return df

def compare_income_groups(df_filtered):
    def assign_group(code):
        if code in HIGH_INCOME:
            return "High Income"
        elif code in EMERGING_ECONOMIES:
            return "Emerging"
        return "Other"

    df = df_filtered.copy()
    df["group"] = df["country_code"].apply(assign_group)

    yearly = (
        df[df["group"] != "Other"]
        .groupby(["year", "group"], observed=True)[["Efficiency_1", "Efficiency_2"]]
        .mean()
        .reset_index()
    )
    hi = yearly[yearly["group"] == "High Income"]
    em = yearly[yearly["group"] == "Emerging"]

    fig, axes = plt.subplots(1, 2, figsize=(13, 4))
    for ax, col, title in zip(axes,
                               ["Efficiency_1", "Efficiency_2"],
                               ["R&D → Patent (Efficiency_1)",
                                "Patent → GDP Growth (Efficiency_2)"]):
        ax.plot(hi["year"], hi[col], marker="o", label="High Income", color="steelblue")
        ax.plot(em["year"], em[col], marker="o", label="Emerging",    color="seagreen")
        ax.set_title(title)
        ax.set_xlabel("Year")
        ax.set_ylabel("Mean Efficiency")
        ax.legend()
        ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, "fig6_efficiency_over_time.png"), dpi=150)
    plt.close(fig)

    print("\n[Efficiency Trends — linear regression on year]")
    for group_name, gdf in [("High Income", hi), ("Emerging", em)]:
        for col in ["Efficiency_1", "Efficiency_2"]:
            slope, intercept, r, p, se = stats.linregress(gdf["year"], gdf[col])
            print(f"  {group_name} | {col} | slope={slope:.4f} | "
                  f"p={p:.3f} | R²={r**2:.3f}")

    hi_df = df[df["group"] == "High Income"].dropna(subset=["rd_gdp", "patent_count"])
    em_df = df[df["group"] == "Emerging"].dropna(subset=["rd_gdp", "patent_count"])

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(hi_df["rd_gdp"], hi_df["patent_count"],
               alpha=0.4, label="High Income", color="steelblue", s=20)
    ax.scatter(em_df["rd_gdp"], em_df["patent_count"],
               alpha=0.4, label="Emerging",    color="seagreen",  s=20)
    ax.set_xlabel("R&D spend (% of GDP)")
    ax.set_ylabel("Patent count")
    ax.set_title("R&D spend vs Patent output by Income Group")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, "fig7_rd_vs_patents_by_group.png"), dpi=150)
    plt.close(fig)

    return df, hi_df, em_df

def compare_efficiency_per_dollar(df_with_groups):
    df = df_with_groups.copy()
    df["eff1_per_rd"] = df["Efficiency_1"] / df["rd_gdp"]

    hi_df = df[df["group"] == "High Income"].dropna(subset=["eff1_per_rd"])
    em_df = df[df["group"] == "Emerging"].dropna(subset=["eff1_per_rd"])

    print("\n[Efficiency_1 per unit R&D]")
    print(f"  High Income mean : {hi_df['eff1_per_rd'].mean():.4f}")
    print(f"  Emerging mean    : {em_df['eff1_per_rd'].mean():.4f}")

    plot_df = df[df["group"].isin(["High Income", "Emerging"])].dropna(
        subset=["eff1_per_rd", "Efficiency_1"]
    )

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].boxplot(
        [hi_df["eff1_per_rd"], em_df["eff1_per_rd"]],
        tick_labels=["High Income", "Emerging"],
        patch_artist=True,
        boxprops=dict(facecolor="steelblue", alpha=0.5),
        medianprops=dict(color="black", linewidth=2),
    )
    axes[0].set_title("Efficiency_1 per unit R&D spend")
    axes[0].set_ylabel("Efficiency_1 / rd_gdp")
    axes[0].grid(True, alpha=0.3)

    sns.boxplot(data=plot_df, x="group", y="Efficiency_1",
                palette={"High Income": "steelblue", "Emerging": "seagreen"},
                ax=axes[1])
    axes[1].set_title("Raw Efficiency_1 (for reference)")
    axes[1].set_xlabel("")
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, "fig8_efficiency_per_rd_boxplot.png"), dpi=150)
    plt.close(fig)

def detect_plateau(df_with_groups):
    df = df_with_groups.copy()

    df["rd_bin"] = pd.qcut(df["rd_gdp"].dropna(), q=10, duplicates="drop")
    threshold_df = (
        df[df["group"] != "Other"]
        .groupby(["rd_bin", "group"], observed=False)["patent_count"]
        .mean()
        .reset_index()
    )
    threshold_df["rd_bin_mid"] = threshold_df["rd_bin"].apply(lambda x: x.mid)
    threshold_df = threshold_df.sort_values("rd_bin_mid")

    fig, ax = plt.subplots(figsize=(9, 4))
    for group, color in [("High Income", "steelblue"), ("Emerging", "seagreen")]:
        sub = threshold_df[threshold_df["group"] == group]
        ax.plot(sub["rd_bin_mid"], sub["patent_count"],
                marker="o", label=group, color=color)
    ax.set_xlabel("R&D spend (% of GDP) — binned midpoint")
    ax.set_ylabel("Mean patent count")
    ax.set_title("Patent output vs R&D spend — plateau detection")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, "fig9_plateau_detection.png"), dpi=150)
    plt.close(fig)

    def log_model(x, a, b):
        return a * np.log(x) + b

    hi_clean = (df[df["group"] == "High Income"]
                .dropna(subset=["rd_gdp", "patent_count"]))
    hi_clean = hi_clean[hi_clean["rd_gdp"] > 0]

    x = hi_clean["rd_gdp"].values
    y = hi_clean["patent_count"].values

    try:
        popt, _ = curve_fit(log_model, x, y, maxfev=5000)
        x_range = np.linspace(x.min(), x.max(), 300)
        y_hat   = log_model(x_range, *popt)

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(x, y, alpha=0.3, s=15, color="steelblue",
                   label="High Income (observed)")
        ax.plot(x_range, y_hat, color="crimson", linewidth=2,
                label=f"Log fit: {popt[0]:.2f}·ln(x) + {popt[1]:.2f}")
        ax.set_xlabel("R&D spend (% of GDP)")
        ax.set_ylabel("Patent count")
        ax.set_title("Log curve fit — High Income: R&D vs Patent output")
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        fig.savefig(os.path.join(RESULTS_DIR, "fig10_log_curve_fit_high_income.png"), dpi=150)
        plt.close(fig)

        print(f"\n[Log curve fit] a={popt[0]:.4f}, b={popt[1]:.4f}")
    except RuntimeError as e:
        print(f"\n[Log curve fit] Optimisation failed: {e}")

def main():
    print("=" * 60)
    print("Running model.py — R&D / Patent / GDP Analysis Pipeline")
    print("=" * 60)

    df_A, df_B = load_data()

    df_B_agg, df_merged = aggregate_subsets(df_A, df_B)

    df_B_agg = analyse_rd_vs_patents(df_B_agg)

    run_ols(df_merged)

    df_B_agg_gdp = analyse_patents_vs_gdp(df_B_agg)

    analyse_lag_effects(df_B_agg_gdp)

    df_filtered = compute_efficiencies(df_B_agg)

    # Income group comparison
    df_with_groups, hi_df, em_df = compare_income_groups(df_filtered)

    # Efficiency per dollar
    compare_efficiency_per_dollar(df_with_groups)

    # Plateau detection
    detect_plateau(df_with_groups)

    print("\n" + "=" * 60)
    print(f"Done. All plots saved to {RESULTS_DIR}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
