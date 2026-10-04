# Minimal revision and repository update

## What changed
The corrected manuscript retains the original paper/notebook results, including all six Table 24 IoU/Dice/rho/agreement/collapse rows. Changes concern the five-epoch QAT schedule, correct lambda0 comparator, seed42 tests versus three-seed means, actual calibration count, explicit limitations, and concise Figure 5/source/code documentation. Matching missing raw records have not been recreated.

## Upload these repository changes
| Files | Action |
|---|---|
| main.tex and references.bib | Use corrected manuscript source and archive/software citations. |
| tables/onnx all/N26_fullsplit_cam.csv and N26_fullsplit_cam_gate.csv | Replace conflicting summaries with saved notebook transcriptions. |
| tables/onnx all/N25_calibration_matched64.csv | Add restored summary; retain actual60/requested64 columns. |
| tables/onnx all/N21_qat_vs_lambda0.csv, N23_sample_size_inventory.csv and N00_rev3_status.csv | Use corrected comparators, counts and historical-status labels; original result values retained where applicable. |
| Corresponding tables_latex/onnx all/*.tex | Update the six affected generated table bodies together. |
| README.md, CITATION.cff, MANIFEST.json, PROGRESS.json, TABLE_INDEX.csv and provenance/ | Replace/add the aligned metadata and evidence notes. |
| tables/onnx all/RAW_fullsplit_cam.csv | Remove from active results; retain unchanged under provenance/superseded_originals/. It backs the older conflicting run only. |

Research notebooks, primary figures and existing primary/QAT raw CSVs remain unchanged. Keep the oneshot notebook: it is not byte-identical to quantxai-revision.ipynb. Do not delete original research code or historical evidence.

## Release steps
1. Use the corrected package as a new commit/release. Preserve v1.3 as the historical release.
2. Create a new Zenodo version of the existing record and upload the corrected package. Do not claim a new model execution or complete missing raw data.
3. After publication, use the actual assigned version and DOI in CITATION.cff and the manuscript's software reference/Code Availability if citing that release. Recompile and refresh page/line references if these edits change pagination. No new DOI has been invented in these files.
4. The supplied manuscript can instead cite the existing v1.3 for code and submit the included Supplementary_Data_1.zip for corrected tables; its wording already distinguishes these sources. Submit clean/main_review PDFs and the updated response and cover letter together.

## Remaining evidence limits
Matching full-split and calibration per-image exports are unavailable. SIIM's saved repaired execution is unverified. They are explicitly disclosed, so do not describe the package as a complete independently reproduced experiment. An original matching export or a documented fresh rerun is required to close these gaps.

## Final audit and publishing guide
See FINAL_AUDIT.md for the additional 4 October corrections and ZENODO_RELEASE_GUIDE.md for the current GitHub/Zenodo workflow. The release candidate is version 2.0.0; no new DOI is assigned.
