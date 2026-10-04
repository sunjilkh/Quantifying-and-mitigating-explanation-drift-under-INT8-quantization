# QuantXAI final consistency audit

Audit date: 4 October 2026. Submission ID: eb9a1278-f10a-473a-81a8-8a3524df27df.

The supplied minor-revision package is substantially corrected. This audit preserves its experimental numbers, independently verifies the recoverable results, fixes additional Methods and packaging errors, and compiles the revised manuscript. It does not establish a complete independent reproduction. Publication of the corrected Zenodo release and verification of the public files remain pending.

## Original verdict and scope

The decision email says **minor revision**, with a deadline of **10 October 2026**. The submission-page capture confirms Reviewer 2 had no remaining concerns; Reviewer 3 recommends acceptance conditionally on addressing remaining concerns. This is not an acceptance decision. The editor requests accurate results, qualified conclusions and limitations, DOI-archived custom code, and clarification/citation of Figure 5 generation. The email capture is horizontally clipped; the readable submission-page capture was also inspected to establish the verdict and reviewer wording.

Original.zip contains the original manuscript PDF and the two verdict/submission captures. It contains no experimental notebook. The authoritative saved notebooks are in the supplied corrected repository. The original manuscript's Table 24 values match the retained saved-output summaries; the conflicting old per-image CSV must not be used to manufacture a different backing dataset.

## Verified results

| Check | Finding | Strength of evidence |
|---|---|---|
| Primary QDQ comparisons at k=0.15 | 3,240 repeated comparisons on 320 distinct images; LIME uses 120 | Archived per-image CSV |
| Primary mean IoU range | 0.365905–0.789973, correctly reported as 0.366–0.790 | Recomputed |
| Median Spearman rho | 0.8499018, correctly reported as 0.850 | Recomputed |
| Primary collapse count | 0 of 3,240 | Archived per-image CSV |
| T5, T6, T7, T8, N5, N7, N10, N11 | All numeric aggregates agree within displayed rounding | Eight raw-derived tables |
| N14a–N14d | Bootstrap intervals, paired method/QAT tests and power tables exactly match stored precision | Four additional recalculated tables |
| N21 QAT controls | Nine seed-42 mean contrasts and paired Wilcoxon/Holm tests agree within displayed precision; six significant | Raw QAT records; continuity-corrected normal approximation |
| N25 calibration | All nine restored summary rows match saved output; actual 60 images, requested 64 | Rounded stdout, not individual predictions |
| N26 full-split CAM | All six restored rows match saved output; 2,082 observations per row | Rounded stdout, not matching per-image records |
| Figure 5 software | Matplotlib 3.10.0 | Saved notebook environment AND original figure PDF metadata |
| Figure 5 data handling | qdq, k=0.15, 320 observations per group/120 LIME; sorted separately, interpolated to 240 display positions; RdYlBu_r with [0,1] limits | Plotting code and CSV |
| Negative rho values | Two primary records below zero; retained in CSV, saturated at lower colour limit | Recomputed; no data alteration |
| Original notebooks and experimental CSVs | Preserved byte-for-byte relative to the uploaded corrected repository | Hash comparison |

The original Spearman maps are not archived; the audit checks recorded coefficients and their aggregation, not recomputation from original saliency arrays. Agreement among files does not itself establish experimental validity.

## Corrections already present and retained

- Correct DOI URL once, rather than a duplicated https://doi.org/ prefix.
- Formal Hunter (2007) Matplotlib citation and a reproducible Figure 5 procedure.
- Five QAT epochs; seed-42 controls separated from lambda=0.5 three-seed summaries.
- Correct lambda=0 versus PTQ comparator labels; corrected repeated-comparison count.
- Sixty actual matched-calibration images distinguished from the requested cap of 64.
- Notebook-consistent Table 24 summaries; conflicting old raw CSV quarantined under superseded provenance.
- Explicit simulation/deployment, three-architecture, shared-image, seed, localisation and missing-data limitations.

## Additional corrections made in this audit

| Issue found in uploaded revision | Correction |
|---|---|
| Training description omits actual scheduler/label smoothing | OneCycleLR with cosine annealing, three-epoch rising phase, maximum LR 0.001 and label smoothing 0.1 |
| Explicit bfloat16 claim not supported by training call | Describes CUDA autocast with unspecified/default dtype, matching source |
| 512-image calibration incorrectly described as 51–52 per class | Proportional class-stratified sampling, matching train_test_split |
| Top-k count written as exact kN | Uses round(kN), matching mask construction |
| Abstract could imply deployed integer saliency | Explicitly names fake-quantized INT8 simulation |
| Conclusion could imply causal/deployment guarantee | Restricts overlap findings to simulation and describes the observed seed-42 control direction |
| SIIM abstract statement stronger than available provenance | Qualifies auxiliary execution provenance |
| requirements header says one environment produced every result | Restricts environment provenance to primary saved run |
| Plot script writes only to /kaggle/working | Adds --tables and --output; fixes ZIP output path; retains original script under provenance |
| Old response page/line references could drift | Uses stable manuscript section/table references; updates audit details and date |
| CITATION.cff could identify candidate with historical release DOI | Proposed version 2.0.0; no new/old DOI falsely assigned to the unpublished release |
| No consolidated repeatable audit | Adds audit_release.py and executed Audit_Notebook_Results.ipynb |

Original Matplotlib 3.10.0 figures remain in the manuscript. The portability test regenerated eight statistical figures using the available Matplotlib 3.10.8 environment, without changing the originals. A regenerated figure is not asserted to be byte-identical across software versions.

## Remaining evidence limits

1. **Full-split per-image records are missing.** The saved summary covers 12,492 repeated CAM comparisons (3 architectures × 2 methods × 2,082 images). The older raw file conflicts with that summary and is preserved only as historical evidence. A matching original export or a documented fresh rerun is needed to close this gap.
2. **Matched-calibration per-image predictions are missing.** The rounded nine-row output is recoverable; individual predictions and thresholds are not.
3. **SIIM repaired execution is unverified.** The primary notebook shows a failed CAM-layer call; the later repair cell has no execution count or output. The retained N17/N17b CSVs are internally consistent but not verified execution evidence.
4. **Other auxiliary diagnostics lack full recovery evidence.** Their presence in a hydrated notebook or CSV is not proof of fresh execution. CSV_AUDIT.csv distinguishes the evidence. No replacement experimental numbers were invented.
5. **Public hosting was not verified.** Retrieval of the stated Zenodo record and GitHub repository was unavailable during this audit. This is not evidence that they do not exist. Check the actual public downloadable files before asserting that the deposit includes them.

The above are evidence limitations, not merely typographical issues. The revision discloses them; an editor can still request original records or further validation. This audit cannot guarantee acceptance or complete reproducibility.

## Deliverables and final action

- QuantXAI_Zenodo_Final.zip: release source, unchanged research notebooks/data, corrected Methods, original figures, audit notebook/script, provenance and hashes.
- Scientific_Reports_Submission_Final.zip: clean and line-numbered PDFs, LaTeX source and figures, revised response/cover letter, Supplementary Data 1, and release guide.
- The manuscript currently uses the historical v1.3 DOI plus corrected Supplementary Data 1, avoiding an invented new DOI. If citing the new release, update the DOI/version and release wording after publishing, then recompile. Instructions and the metadata finalizer are included.

Run `python audit_release.py` inside the extracted release folder for offline checks. No GPU or source images are required. The supplementary tables and notebooks are the same evidence used in this audit; no missing observations have been synthesised.
