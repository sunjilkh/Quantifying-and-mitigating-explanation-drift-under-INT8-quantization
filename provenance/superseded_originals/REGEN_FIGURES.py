# =============================================================================
# CELL 19-R2 : REGENERATE EVERY FIGURE - PUBLICATION QUALITY, ZERO COLLISIONS
# -----------------------------------------------------------------------------
# Reads ONLY the exported CSV tables. No GPU, no weights, no dataset needed.
# Runs on CPU in ~30 s. Attach the results bundle as a Kaggle dataset input.
#
# What changed vs CELL 19-R (the overlap fixes):
#   1. STRUCTURAL ANTI-COLLISION. Every figure is laid out on a GridSpec that
#      reserves its own row for the legend and its own row for the provenance
#      footer. Text is drawn INSIDE those reserved axes, never floated over the
#      plot with fig.text(). Overlap is therefore geometrically impossible.
#   2. constrained_layout=True everywhere - Matplotlib solves the spacing.
#   3. Shared x-axis on the 3-panel Spearman grid; only the bottom panel keeps
#      tick labels and an x-label, so panel titles can no longer sit on top of
#      the axis numbers of the panel above.
#   4. Legends moved OUT of the data area into their reserved row (fixes the
#      legend sitting on the curves in the k-sweep and lambda-sweep figures).
#   5. Larger, bolder type: base 11 pt, bold 12.5 pt titles, bold 11.5 pt axis
#      labels, 10.5 pt ticks (was 9/9/8).
#   6. Fonts embedded as TrueType (pdf.fonttype=42) - Scientific Reports
#      rejects Type-3. 600 dpi PNG + vector PDF + vector SVG for every figure.
# =============================================================================
import shutil, zipfile, platform
from pathlib import Path
#
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
#
# ----------------------------------------------------------------- knobs ----
DPI         = 600
VECTOR_EXTS = ("pdf", "svg")
K_MAIN      = 0.15
SIM_MAIN    = "qdq"
SEED        = 42
NGRID       = 240
OUTDIR      = Path("/kaggle/working/figures_v2")
#
NOTE_H   = 0.13   # reserved footer row height, relative to one panel
LEGEND_H = 0.13   # reserved legend row height, relative to one panel
#
ARCH_ORDER = ["tf_efficientnetv2_s", "resnet50", "mobilenetv3_large_100"]
XAI_ORDER  = ["gradcampp", "gradcam", "lime", "ig"]
ARCH_LABEL = {"tf_efficientnetv2_s": "EfficientNetV2-S",
              "resnet50": "ResNet-50",
              "mobilenetv3_large_100": "MobileNetV3-Large"}
XAI_LABEL  = {"gradcampp": "Grad-CAM++", "gradcam": "Grad-CAM",
              "lime": "LIME", "ig": "Integrated Gradients"}
CAM_LAYER  = {"tf_efficientnetv2_s": "bn2", "resnet50": "layer4",
              "mobilenetv3_large_100": "blocks"}
ARCH_COLOR = {"tf_efficientnetv2_s": "#4C78A8", "resnet50": "#F58518",
              "mobilenetv3_large_100": "#54A24B"}
#
matplotlib.rcParams.update({
    "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
    "savefig.dpi": DPI, "figure.dpi": 110,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.05,
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 11.0,
    "axes.titlesize": 12.5, "axes.titleweight": "bold",
    "axes.labelsize": 11.5, "axes.labelweight": "bold",
    "xtick.labelsize": 10.5, "ytick.labelsize": 10.5,
    "legend.fontsize": 10.5,
    "figure.titlesize": 13.5, "figure.titleweight": "bold",
    "axes.linewidth": 1.0, "lines.linewidth": 1.9, "lines.markersize": 5.0,
    "axes.grid": False, "axes.axisbelow": True,
})
#
MPL_CITE = "Matplotlib " + matplotlib.__version__ + " (https://matplotlib.org)"
STAMP    = (MPL_CITE + " | Python " + platform.python_version()
            + " | seed " + str(SEED) + " | k=" + str(K_MAIN) + " | sim=" + SIM_MAIN)
#
#
# ------------------------------------------------------- locate the data ----
def _looks_like_tables(p):
    return p.is_dir() and (p / "N10_lambda_sweep.csv").exists()
#
#
def find_tables():
    roots = [Path("/kaggle/working")]
    if Path("/kaggle/input").exists():
        roots += sorted(Path("/kaggle/input").glob("*"))
    roots += [Path(".")]
    for r in roots:
        if not r.exists():
            continue
        if _looks_like_tables(r / "tables"):
            return r / "tables"
        for cand in list(r.glob("*/tables")) + list(r.glob("*/*/tables")):
            if _looks_like_tables(cand):
                return cand
    for r in roots:
        if not r.exists():
            continue
        for z in list(r.glob("*.zip")) + list(r.glob("*/*.zip")):
            try:
                with zipfile.ZipFile(z) as zf:
                    if any(n.endswith("N10_lambda_sweep.csv") for n in zf.namelist()):
                        dst = Path("/kaggle/working/_unzipped")
                        dst.mkdir(parents=True, exist_ok=True)
                        zf.extractall(dst)
                        print("  [unzip] " + z.name)
                        for cand in dst.rglob("tables"):
                            if _looks_like_tables(cand):
                                return cand
            except Exception as e:
                print("  [warn] " + z.name + ": " + type(e).__name__)
    raise SystemExit("Could not find tables/. Attach the results bundle as a dataset input.")
#
#
TABLES = find_tables()
FIGSRC = TABLES.parent / "figures"
OUTDIR.mkdir(parents=True, exist_ok=True)
print("[src] tables : " + str(TABLES))
print("[src] figures: " + str(FIGSRC) + (" (present)" if FIGSRC.exists() else " (absent)"))
print("[out]        : " + str(OUTDIR))
print("[env] " + MPL_CITE + " | pandas " + pd.__version__ + " | numpy " + np.__version__)
print()
#
#
def T(name):
    p = TABLES / (name + ".csv")
    if not p.exists():
        print("  [skip] missing table " + name + ".csv")
        return None
    return pd.read_csv(p)
#
#
MADE = []
#
#
# ------------------------------------------------- collision-proof canvas ----
def make_fig(figsize, nrows=1, ncols=1, legend_row=False, sharex=False,
             height_ratios=None, width_ratios=None):
    """Figure whose GridSpec reserves rows for the legend and the footer.

    Returns (fig, axes[nrows][ncols], ax_legend_or_None, ax_note).
    Because the legend and footer live in their own axes, constrained_layout
    allocates real space for them and nothing can ever overlap the plots.
    """
    fig = plt.figure(figsize=figsize, constrained_layout=True)
    extra = ([LEGEND_H] if legend_row else []) + [NOTE_H]
    hr = (list(height_ratios) if height_ratios else [1.0] * nrows) + extra
    gs = fig.add_gridspec(nrows + len(extra), ncols,
                          height_ratios=hr, width_ratios=width_ratios)
    axes = []
    for i in range(nrows):
        row = []
        for j in range(ncols):
            kw = {}
            if sharex and i > 0:
                kw["sharex"] = axes[0][j]
            row.append(fig.add_subplot(gs[i, j], **kw))
        axes.append(row)
    idx = nrows
    axl = None
    if legend_row:
        axl = fig.add_subplot(gs[idx, :])
        axl.axis("off")
        idx += 1
    axn = fig.add_subplot(gs[idx, :])
    axn.axis("off")
    return fig, axes, axl, axn
#
#
def put_legend(axl, src_ax, ncol=None):
    h, l = src_ax.get_legend_handles_labels()
    if not h:
        return
    axl.legend(h, l, loc="center", ncol=ncol or len(h), frameon=False,
               handlelength=1.9, columnspacing=1.6, borderpad=0.0)
#
#
def finish(fig, axn, name, source):
    axn.text(0.0, 0.62, STAMP, fontsize=6.6, color="#555",
             ha="left", va="center", transform=axn.transAxes)
    axn.text(0.0, 0.14, "source: " + source, fontsize=6.6, color="#555",
             ha="left", va="center", transform=axn.transAxes)
    fig.savefig(OUTDIR / (name + ".png"), dpi=DPI)
    outs = [str(DPI) + "dpi png"]
    for ext in VECTOR_EXTS:
        try:
            fig.savefig(OUTDIR / (name + "." + ext))
            outs.append(ext)
        except Exception as e:
            print("    [warn] " + ext + " failed: " + type(e).__name__)
    plt.close(fig)
    MADE.append(name)
    print("  [ok] " + name.ljust(32) + " (" + ", ".join(outs) + ")")
#
#
# =============================================================================
# F1 - Spearman grid : REPLACES original Figures 7, 8, 9
# =============================================================================
raw = T("RAW_drift_all")
if raw is not None:
    d = raw[(raw["k"] == K_MAIN) & (raw["sim"] == SIM_MAIN)]
    archs = [a for a in ARCH_ORDER if a in set(d["arch"])]
    fig, axes, _, axn = make_fig((10.2, 3.05 * len(archs)), nrows=len(archs),
                                 ncols=1, sharex=True)
    im = None
    panels = [axes[r][0] for r in range(len(archs))]
    for r, a in enumerate(archs):
        ax = panels[r]
        rows, labels = [], []
        for x in XAI_ORDER:
            s = d[(d["arch"] == a) & (d["xai"] == x)]["spearman"].dropna().values
            if s.size == 0:
                continue
            s = np.sort(s)
            q = np.linspace(0, 1, NGRID)
            rows.append(np.interp(q, np.linspace(0, 1, s.size), s))
            labels.append(XAI_LABEL[x] + "  (n=" + str(s.size) + ")")
        if not rows:
            continue
        M = np.vstack(rows)
        im = ax.imshow(M, aspect="auto", cmap="RdYlBu_r", vmin=0, vmax=1,
                       interpolation="nearest")
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels, fontsize=10.0)
        ax.set_xticks(np.linspace(0, NGRID - 1, 5))
        ax.set_xticklabels(["0", "25", "50", "75", "100"])
        ax.tick_params(axis="x", labelbottom=(r == len(archs) - 1))
        ax.set_title(ARCH_LABEL.get(a, a) + "   \u2014   CAM layer '"
                     + CAM_LAYER.get(a, "?") + "'", loc="left", pad=7)
        if r == len(archs) - 1:
            ax.set_xlabel("image percentile (sorted by \u03c1)")
    if im is not None:
        cb = fig.colorbar(im, ax=panels, shrink=0.92, pad=0.015, aspect=32)
        cb.set_label("Spearman \u03c1  (FP32 vs INT8 saliency)", fontsize=11.0,
                     fontweight="bold")
        cb.ax.tick_params(labelsize=10.0)
    fig.suptitle("Per-image FP32 vs INT8 saliency rank correlation at the corrected CAM layers")
    finish(fig, axn, "fig_spearman_grid", "RAW_drift_all.csv")
    sub = d["spearman"].dropna()
    print("       min \u03c1 = " + format(sub.min(), ".4f")
          + " | frac(\u03c1<0.2) = " + format((sub < 0.2).mean(), ".4f")
          + " | median = " + format(sub.median(), ".4f"))
#
#
# =============================================================================
# F2 - bootstrap-CI bars (top-k IoU, Spearman rho)
# =============================================================================
n14a = T("N14a_bootstrap_ci")
if n14a is not None:
    for met, nice in (("topk_iou", "top-k IoU"), ("spearman", "Spearman \u03c1")):
        s = n14a[n14a["metric"] == met]
        if s.empty:
            continue
        g = (s.groupby("xai")[["mean", "ci_lo", "ci_hi"]].mean()
               .sort_values("mean", ascending=False)).rename(index=XAI_LABEL)
        fig, axes, axl, axn = make_fig((6.6, 4.5), legend_row=True)
        ax = axes[0][0]
        ax.bar(g.index, g["mean"], color="#4C78A8", width=0.62,
               yerr=[g["mean"] - g["ci_lo"], g["ci_hi"] - g["mean"]],
               capsize=5, error_kw=dict(lw=1.1))
        if met == "topk_iou":
            ch = K_MAIN / (2 - K_MAIN)
            ax.axhline(ch, ls="--", c="crimson", lw=1.4,
                       label="random overlap = " + format(ch, ".3f"))
            put_legend(axl, ax)
        else:
            ax.axhline(0, ls="--", c="crimson", lw=1.4)
        ax.set_ylabel(nice)
        ax.set_title(nice + " by XAI method (95% bootstrap CI)")
        ax.grid(axis="y", alpha=0.28)
        ax.set_ylim(0, max(g["ci_hi"].max() * 1.16, 0.1))
        plt.setp(ax.get_xticklabels(), rotation=16, ha="right",
                 rotation_mode="anchor")
        finish(fig, axn, "fig_" + met + "_by_method_ci", "N14a_bootstrap_ci.csv")
#
#
# =============================================================================
# F3 - k-sweep robustness (R1#3 / R2#2)
# =============================================================================
n5 = T("N5_k_sweep")
if n5 is not None:
    d = n5[n5["sim"] == SIM_MAIN] if SIM_MAIN in set(n5["sim"]) else n5
    fig, axes, axl, axn = make_fig((11.4, 4.6), ncols=2, legend_row=True)
    for ax, met, nice in ((axes[0][0], "iou", "top-k IoU"),
                          (axes[0][1], "rho", "Spearman \u03c1")):
        for x in XAI_ORDER:
            g = d[d["xai"] == x]
            if g.empty:
                continue
            gg = g.groupby("k")[met].mean()
            ax.plot(gg.index, gg.values, marker="o", label=XAI_LABEL[x])
        if met == "iou":
            ks = sorted(d["k"].unique())
            ax.plot(ks, [k / (2 - k) for k in ks], "k--", lw=1.5, label="chance")
        ax.axvline(K_MAIN, color="#999", ls=":", lw=1.4)
        ax.set_xlabel("top-k fraction")
        ax.set_ylabel(nice)
        ax.grid(alpha=0.28)
    put_legend(axl, axes[0][0], ncol=5)
    fig.suptitle("Drift metrics vs top-k threshold (dotted line = reported k)")
    finish(fig, axn, "fig_k_sweep", "N5_k_sweep.csv")
#
#
# =============================================================================
# F4 - collapse-rate heatmap (every cell is zero)
# =============================================================================
n7 = T("N7_collapse_rates")
if n7 is not None:
    d = n7[n7["sim"] == SIM_MAIN] if SIM_MAIN in set(n7["sim"]) else n7
    p = d.pivot_table(index="arch", columns="xai", values="collapse_rate")
    p = p.reindex(index=[a for a in ARCH_ORDER if a in p.index],
                  columns=[x for x in XAI_ORDER if x in p.columns])
    fig, axes, _, axn = make_fig((7.6, 3.5))
    ax = axes[0][0]
    im = ax.imshow(p.values, cmap="Reds", vmin=0, vmax=1)
    ax.set_xticks(range(p.shape[1]))
    ax.set_xticklabels([XAI_LABEL.get(c, c) for c in p.columns],
                       rotation=16, ha="right", rotation_mode="anchor")
    ax.set_yticks(range(p.shape[0]))
    ax.set_yticklabels([ARCH_LABEL.get(i, i) for i in p.index])
    for i in range(p.shape[0]):
        for j in range(p.shape[1]):
            v = p.values[i, j]
            ax.text(j, i, format(v, ".2f"), ha="center", va="center",
                    fontsize=11.0, fontweight="bold",
                    color="white" if v > 0.5 else "black")
    cb = fig.colorbar(im, ax=ax, shrink=0.9, pad=0.02)
    cb.set_label("collapse rate", fontsize=11.0, fontweight="bold")
    ax.set_title("Saliency collapse rate under INT8: 0.00 in every cell")
    finish(fig, axn, "fig_collapse_heatmap", "N7_collapse_rates.csv")
#
#
# =============================================================================
# F5 - QAT lambda dose-response (R3#7)
# =============================================================================
n10 = T("N10_lambda_sweep")
if n10 is not None:
    fig, axes, axl, axn = make_fig((13.2, 4.6), ncols=3, legend_row=True)
    for col, a in enumerate(ARCH_ORDER):
        ax = axes[0][col]
        g = n10[n10["arch"] == a]
        if g.empty:
            continue
        for x in XAI_ORDER:
            gg = g[g["xai"] == x]
            if gg.empty:
                continue
            m = gg.groupby("lam")["iou"].mean()
            ax.plot(m.index, m.values, marker="o", label=XAI_LABEL[x])
        ax.set_title(ARCH_LABEL.get(a, a))
        ax.set_xlabel("\u03bb  (CAM-consistency weight)")
        ax.set_ylabel("top-k IoU")
        ax.grid(alpha=0.28)
    put_legend(axl, axes[0][0])
    fig.suptitle("QAT dose-response: explanation stability vs \u03bb  (\u03bb=0 is the control)")
    finish(fig, axn, "fig_lambda_sweep", "N10_lambda_sweep.csv")
#
#
# =============================================================================
# F6 - post-QAT accuracy vs lambda
# =============================================================================
n12 = T("N12_post_qat_performance")
if n12 is not None:
    fig, axes, axl, axn = make_fig((7.4, 4.7), legend_row=True)
    ax = axes[0][0]
    for a in ARCH_ORDER:
        g = n12[n12["arch"] == a]
        if g.empty:
            continue
        q = g[g["stage"] == "QAT-INT8"].groupby("lam")["macro_f1"].mean()
        if not q.empty:
            ax.plot(q.index, q.values, marker="o", color=ARCH_COLOR.get(a),
                    label=ARCH_LABEL.get(a, a))
        f = g[g["stage"] == "FP32"]["macro_f1"].mean()
        if pd.notna(f):
            ax.axhline(f, ls=":", lw=1.2, alpha=0.65, color=ARCH_COLOR.get(a))
    ax.set_xlabel("\u03bb  (CAM-consistency weight)")
    ax.set_ylabel("macro-F1 (validation)")
    ax.set_title("Post-QAT accuracy vs \u03bb  (dotted = FP32 baseline)")
    ax.grid(alpha=0.28)
    put_legend(axl, ax)
    finish(fig, axn, "fig_accuracy_vs_lambda", "N12_post_qat_performance.csv")
#
#
# =============================================================================
# F7 - dataset composition
# =============================================================================
n19 = T("N19_dataset_composition")
if n19 is not None:
    fig, axes, _, axn = make_fig((max(7.0, 0.72 * len(n19)), 4.6))
    ax = axes[0][0]
    ax.bar(n19["class_name"].astype(str), n19["n"], color="#72B7B2", width=0.66)
    ax.set_ylabel("images")
    ds = str(n19["dataset"].iloc[0]) if "dataset" in n19 else "dataset"
    ax.set_title(ds + ": class distribution (n=" + str(int(n19["n"].sum())) + ")")
    plt.setp(ax.get_xticklabels(), rotation=32, ha="right", rotation_mode="anchor")
    ax.grid(axis="y", alpha=0.28)
    finish(fig, axn, "fig_dataset_distribution", "N19_dataset_composition.csv")
#
#
# =============================================================================
# F8 - qualitative CAM panel : needs GPU + weights, so carry it over unchanged
# =============================================================================
SEARCH = [FIGSRC, FIGSRC / "Old", OUTDIR.parent / "figures", Path("/kaggle/working/figures")]
got = False
for stem in ("fig_qualitative_cams",):
    for src_dir in SEARCH:
        if not src_dir.exists():
            continue
        for ext in ("png", "pdf", "svg"):
            src = src_dir / (stem + "." + ext)
            if src.exists() and not (OUTDIR / src.name).exists():
                shutil.copy2(src, OUTDIR / src.name)
                got = True
    if got:
        MADE.append(stem + " (carried over)")
        print("  [cp] " + stem.ljust(32) + " (needs GPU+weights; copied unchanged)")
    else:
        print("  [!!] " + stem + " NOT FOUND - copy it from your Old/ figures folder by hand")
#
#
# =============================================================================
# package + report
# =============================================================================
zip_path = Path("/kaggle/working/figures_v2.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for f in sorted(OUTDIR.iterdir()):
        if f.is_file():
            zf.write(f, f.name)
#
files = sorted(p.name for p in OUTDIR.iterdir() if p.is_file())
total = sum(p.stat().st_size for p in OUTDIR.iterdir() if p.is_file())
print()
print("=" * 70)
print("FIGURES WRITTEN : " + str(len(MADE)))
print("FILES           : " + str(len(files)) + "  (" + format(total / 1048576, ".1f") + " MB)")
print("ZIP             : " + str(zip_path))
print("=" * 70)
for n in files:
    print("   " + n)
#