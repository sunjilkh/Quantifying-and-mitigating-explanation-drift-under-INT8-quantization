# Quantifying and mitigating explanation drift under INT8 quantization in plant disease image classification

Code, result tables and figures accompanying the *Scientific Reports* submission of the same name.

**Author** Sunzil Khandaker, Department of Computer Science and Engineering, Daffodil International University, Dhaka, Bangladesh
**Contact** khandaker15-5383@diu.edu.bd

---

## What this is

Deploying a CNN on an edge device usually means quantizing it to INT8. This study asks a narrow question: when you do that, does the *explanation* stay the same?

Three ImageNet-pretrained backbones -- EfficientNetV2-S, ResNet-50 and MobileNetV3-Large -- are fine-tuned on the Paddy Doctor dataset (10 classes, 10,407 images; 8,325 train / 2,082 validation), quantized by post-training quantization and by quantization-aware training, then compared FP32 against INT8 through four attribution methods: Grad-CAM, Grad-CAM++, LIME and Integrated Gradients. Agreement is measured with top-k IoU, top-k Dice and Spearman rank correlation over 320 validation images (120 for LIME), giving 3,240 paired comparisons.

Every number in the paper is produced by the notebook in this repository and exported to `tables/`. Nothing is transcribed by hand.

## Headline findings

| Finding | Evidence |
|---|---|
| INT8 largely preserves explanations. Mean top-k IoU is 0.718 (Grad-CAM++), 0.662 (Grad-CAM), 0.625 (LIME) and 0.446 (Integrated Gradients), against a random-overlap baseline of 0.081 at k = 0.15 | `T7_drift_by_method.csv`, `N6_random_baselines.csv` |
| No attribution collapse anywhere: the collapse rate is 0.00 in all 24 model x method cells | `N7_collapse_rates.csv` |
| A naive "last convolutional layer" CAM target returns a degenerate 1x1 map on all three backbones. Choosing the last *spatial* layer instead (`bn2`, `layer4`, `blocks`) removes the collapse a naive picker appears to show | `N2_cam_target_layers.csv`, `N16_cam_layer_sweep.csv` |
| Calibration matters more than the quantizer. Under ONNX Runtime, MinMax calibration drops INT8 accuracy to 0.634 (EfficientNetV2-S) and 0.547 (MobileNetV3-Large); Percentile calibration recovers 0.916 and 0.891. Percentile is the deployed configuration | `N3_calibration_ablation.csv` |
| A CAM-consistency term in QAT helps the weakest model and harms the strongest: MobileNetV3-Large +16.3% top-k IoU with Grad-CAM, EfficientNetV2-S -26.0% with Integrated Gradients. ResNet-50 shows no significant change | `T8_qat_mitigation.csv`, `N14d_qat_paired_tests.csv` |
| Against SIIM-ACR pneumothorax masks, FP32 and INT8 localisation are statistically indistinguishable (n = 87, Wilcoxon p = 0.63). Reported as a null result | `N17b_siim_summary.csv` |
| INT8 shrinks the models 3.5-3.9x, but CPU latency improves for only two of the three (1.09x, 1.28x, 0.67x) | `N1_efficiency.csv` |

## Repository layout

```
.
|-- README.md
|-- LICENSE                     CC BY 4.0
|-- CITATION.cff
|-- .gitignore
|-- requirements.txt            17 pinned packages
|-- quantxai_full_run.ipynb     the complete study, cell outputs retained
|-- qat_calibration_reanalysis.ipynb re-analysis of calibration configurations
|-- REGEN_FIGURES.py            rebuilds every figure from tables/ (CPU, ~30 s)
|-- MANIFEST.json               run configuration and environment
|-- PROGRESS.json               per-stage timings
|-- TABLE_INDEX.csv             index of all 34 tables
|-- tables/                     34 CSVs holding every reported number
|   `-- onnx all/               9 additional CSVs from ONNX Runtime re-runs and revision analyses (see below)
|-- tables_latex/               the same tables as LaTeX table bodies
`-- figures/                    8 figures, each as PDF + PNG + SVG
```

Model checkpoints (`ckpt/`, 24 files) and ONNX graphs (`onnx/`, 12 files) are **not** in this repository: they exceed GitHub's 100 MB per-file limit. They are in the Zenodo record linked above.

### `tables/onnx all/` — Revision and ONNX Runtime supplementary tables

Nine CSVs produced during revision, including re-running analyses directly through ONNX Runtime and providing additional robustness checks:

| File | Contents |
|---|---|
| `N00_rev3_status.csv` | Revision tracking and status |
| `N21_qat_vs_lambda0.csv` | QAT mitigation metrics compared directly against a lambda=0 control, with statistical tests |
| `N21b_lambda_monotonicity.csv` | Verification of top-k IoU monotonicity across the lambda sweep |
| `N22_agreement_reconciliation.csv` | Reconciliation of top-1 prediction agreement across evaluated subsets |
| `N23_sample_size_inventory.csv` | Complete inventory of evaluation sample sizes and justifications |
| `N24_compute_budget.csv` | Estimates of computational overhead for different simulation scopes |
| `N26_fullsplit_cam.csv` | Full validation-split (2,082 images) Grad-CAM / Grad-CAM++ drift metrics |
| `N26_fullsplit_cam_gate.csv` | Gating check confirming reproducibility against the 320-image subset |
| `RAW_fullsplit_cam.csv` | Per-image raw records underlying `N26_fullsplit_cam.csv` |

## Reproducing

### The figures alone -- 30 seconds, CPU only

```
pip install numpy pandas matplotlib
python REGEN_FIGURES.py
```

The script locates `tables/` automatically (working directory, any Kaggle input, or a zip alongside it) and writes `figures_v2/` containing a 600 dpi PNG plus vector PDF and SVG for each figure. No GPU, no weights, no dataset. The identical code is the final cell of the notebook.

### The full study -- Kaggle, one NVIDIA T4

1. Open `quantxai_full_run.ipynb` as a Kaggle notebook.
2. Attach `paddy-disease-classification` and `jesperdramsch/siim-acr-pneumothorax-segmentation-data` (and RoCoLe if running supplementary checks) as inputs.
3. Accelerator GPU T4, Internet on. Leave `PROFILE = "full"` in CELL 1.
4. Run all. Expect roughly one GPU-day; intermediate state is checkpointed, so an interrupted session resumes rather than restarts.

The last cell of the notebook is a self-contained recovery cell that rebuilds the run context from an exported bundle and recomputes only the SIIM-ACR analysis and the qualitative CAM panel. It is kept for provenance and is not part of the main sequence.

## Figure map

| Manuscript | File | Built from |
|---|---|---|
| Figure 5 | `fig_spearman_grid` | `RAW_drift_all.csv` |
| Figure 6a | `fig_topk_iou_by_method_ci` | `N14a_bootstrap_ci.csv` |
| Figure 6b | `fig_spearman_by_method_ci` | `N14a_bootstrap_ci.csv` |
| Figure 7 | `fig_k_sweep` | `N5_k_sweep.csv` |
| Figure 8a | `fig_lambda_sweep` | `N10_lambda_sweep.csv` |
| Figure 8b | `fig_accuracy_vs_lambda` | `N12_post_qat_performance.csv` |
| Supplementary | `fig_collapse_heatmap` | `N7_collapse_rates.csv` |
| Supplementary | `fig_dataset_distribution` | `N19_dataset_composition.csv` |
| Supplementary | `fig_qualitative_cams` | requires GPU and checkpoints |

Figures 1-4 of the manuscript are TikZ drawings in the LaTeX source, not image files.

Every generated figure carries a provenance footer naming the plotting library and its version, the Python version, the random seed, the top-k fraction, the quantization simulation mode, and the CSV it was built from.

## Table naming

- `T*` tables that appear in the manuscript
- `N*` analyses added during revision
- `S2` supplementary, labelled exploratory
- `RAW_*` per-image records (`RAW_drift_all` 38,880 rows; `RAW_qat_drift` 120,960 rows)

`TABLE_INDEX.csv` lists all 34 with their row and column counts.

## Data

Neither dataset is redistributed here.

- Paddy Doctor: https://www.kaggle.com/competitions/paddy-disease-classification
- SIIM-ACR Pneumothorax Segmentation: https://www.kaggle.com/datasets/jesperdramsch/siim-acr-pneumothorax-segmentation-data
- RoCoLe Robusta Coffee Leaf Images: https://doi.org/10.17632/c5yvn32dzg.2

## Environment

Python 3.12.13, torch 2.10.0+cu128, timm 1.0.26, onnx 1.22.0, onnxruntime 1.28.0, numpy 2.0.2, pandas 2.3.3, scikit-learn 1.6.1, scikit-image 0.25.2, matplotlib 3.10.0, pydicom 3.0.2. Hardware: one NVIDIA Tesla T4. Seeds 42, 1337 and 2024.

```
pip install -r requirements.txt
```

## Citation

See `CITATION.cff`. If you use this code or these results, please cite the article and the archived release.

## License

The contents of this repository are released under the Creative Commons Attribution 4.0 International licence (`LICENSE`). The datasets remain under their own terms.
