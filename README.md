# QuantXAI corrected repository — unpublished correction candidate

Sunzil Khandaker, Department of CSE, Daffodil International University

This package aligns the manuscript and deposited summaries to saved notebook output. It preserves the original paper's primary results and Table 24 full-split summary; no new training, model inference or invented per-image records are included. The existing base code release is https://doi.org/10.5281/zenodo.21887946 (v1.3). This correction candidate is not yet publicly deposited at that DOI.

## Minimal corrections
- `main.tex`: five QAT epochs; seed-42/control column and three-seed distinctions; original Table 24 summary; qualified interpretation and provenance; concise DOI-linked Figure 5 instructions.
- `tables/onnx all/N26_fullsplit_cam.csv` and `N26_fullsplit_cam_gate.csv`: six rounded rows restored from `qat_calibration_reanalysis.ipynb` saved output. Full-split IoU differs from the primary subset by at most 0.0140; gate difference is at most 0.0064. These checks do not prove identical-model reproduction.
- `N25_calibration_matched64.csv`: nine summary rows transcribed from saved output, with 60 actual and 64 requested calibration images. The historical filename is retained for traceability.
- `N21_qat_vs_lambda0.csv`: numeric results preserved; final comparator correctly named lambda0 versus PTQ, with seed42 recorded. `lam05_seed_sd` and `lam05_n_seeds` describe separate three-seed dispersion; `qat_lam05_iou` is the seed42 mean. All nine paired tests reproduce from existing raw records within displayed precision.
- `N23_sample_size_inventory.csv`: 3×(3×320+120)=3240 repeated comparisons; matched calibration count is 60. These are not 3240 independent images.
- `N00_rev3_status.csv`: historical statuses labeled RECORDED_OK, actual versus requested budget distinguished; not evidence of a newly successful run.
- Companion LaTeX table bodies, index, manifest, progress metadata and citation corrected. No invented publication citation, GitHub placeholder, or claim of deposited checkpoint/ONNX binaries remains in active metadata.

## Evidence limits
Matching 12,492 full-split per-image records for the retained paper/notebook summary are absent. The conflicting older raw CSV is kept only under `provenance/superseded_originals/tables/onnx all/RAW_fullsplit_cam.csv`; do not aggregate it to validate active N26. Matching per-image calibration outputs are also absent. SIIM CSVs are retained unchanged but the saved repair cell has no execution count or outputs; see `provenance/SIIM_PROVENANCE.md`. Unverified tables are retained rather than manufactured: `provenance/CSV_AUDIT.csv` states each basis.

## Code, figures and identity
`quantxai-revision.ipynb` and `qat_calibration_reanalysis.ipynb` remain byte-for-byte identical to the supplied originals. The oneshot notebook is preserved under provenance and differs in bytes; keep it. The existing primary raw tables, figures and licence are unchanged. The final audit makes plotting paths portable and clarifies the requirements header; the historical plotting script is retained under provenance. Figure 5 uses `tables/RAW_drift_all.csv` (qdq, k=0.15); its figure does not require regeneration for the N26 correction. The restoration utility reads saved stdout only and produces the initial restoration package; the final manuscript/citation/provenance edits here are documented separately and are not new experimental notebook outputs.

## Submission and release
`Supplementary_Data_1.zip` in the manuscript delivery contains aligned CSVs and source/provenance notes; this supports manuscript references without implying the public v1.3 already contains corrections. Follow `REPOSITORY_UPDATE.md` to publish a new version. Do not overwrite the historical release or use its conflicting raw CSV as backing data for the restored summary. After publication, set the real new version/DOI in CITATION and manuscript references before submission if you cite that new release.

File hashes are in `provenance/SHA256SUMS.csv`; original notebook comparisons, eight primary/QAT raw-derived aggregate checks and nine QAT paired-test checks are included. Detailed missing-data limitations remain explicit.

## Final audit on 4 October 2026
Twelve raw-derived tables now pass independent offline recalculation, including bootstrap intervals and paired tests. Methods additionally corrects the OneCycleLR schedule, label smoothing, unspecified CUDA autocast dtype, and proportional 512-image calibration sampling. Original research notebooks and experimental CSV numbers are unchanged. Figure PDF metadata independently confirms Matplotlib 3.10.0. Use `Audit_Notebook_Results.ipynb` or `python audit_release.py` from this directory. This is an offline audit, not new inference. See `FINAL_AUDIT.md` and `ZENODO_RELEASE_GUIDE.md`.

The release version in CITATION.cff is 2.0.0, proposed for the next unused GitHub tag. No DOI identifies this unpublished package yet. The historical DOI is deliberately absent from CITATION.cff identifiers to avoid assigning it to the new release. The manuscript currently cites historical v1.3 plus corrected Supplementary Data 1. Verify that public record before submission, or update the manuscript to the actual new DOI after publishing.
