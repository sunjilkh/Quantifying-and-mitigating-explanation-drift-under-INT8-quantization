# Publish the corrected QuantXAI release

Prepared 4 October 2026. The corrected package is not yet published. The old DOI, https://doi.org/10.5281/zenodo.21887946, must not be presented as identifying these new files. Version 2.0.0 is proposed; choose the next unused tag if it already exists, and make CITATION.cff agree.

## First check how the old record was created

Open the existing record while signed in. In Zenodo, profile menu → GitHub, find the repository and inspect its archived releases. Confirm that the old v1.3 entry links to the existing record. If it does, use the automatic GitHub route below. If it does not, use New version on the existing record to preserve its version history; enabling GitHub now should not be assumed to attach to a manually uploaded record.

Public record URL to inspect: https://zenodo.org/records/21887946
Repository URL supplied with the files: https://github.com/sunjilkh/Quantifying-and-mitigating-explanation-drift-under-INT8-quantization

## Route A Existing GitHub integration

1. Extract QuantXAI_Zenodo_Final.zip. Put the contents of QuantXAI_Zenodo_Release into the repository root, preserving unrelated project files and the historical Git history. Do not merely add the ZIP as the only new repository file.
2. Replace corrected files together. Remove the obsolete active `tables/onnx all/RAW_fullsplit_cam.csv` if it remains in the repository; its original bytes are already preserved under `provenance/superseded_originals/`. Keep the original notebooks.
3. Check for an existing `.zenodo.json`: Zenodo prioritises it over CITATION.cff. Update stale title/version/DOI metadata there, or remove it if you deliberately choose to use CITATION.cff. Do not supply the old version DOI as the new release DOI.
4. Commit the update to the intended release branch. A browser upload can handle selected files, but a local Git checkout or browser-based GitHub Codespace is more practical for the whole folder. Review the diff and ensure CSVs, notebooks and provenance are committed, not just attached release assets.
5. In Zenodo → profile menu → GitHub → Sync now, ensure this repository is enabled and that its previous archived release is the record you intend to version.
6. In GitHub → Releases → Draft a new release, choose a **new unused tag** such as v2.0.0, targeting the corrected commit. Title: `QuantXAI 2.0.0 — Scientific Reports minor revision`. Use the release notes below. Attach the final ZIP as an optional convenient asset; the committed repository contents remain essential.
7. Publish the release. A commit or tag by itself does not trigger the release workflow. Wait for processing in Zenodo's GitHub page; inspect any reported metadata error.
8. Open the resulting DOI. Confirm the new version appears in the same version history as v1.3, then download its archive and inspect its contents. Do not assume that an attached GitHub asset was automatically included.
9. Copy the actual **version DOI**, version and release tag. Use the supplied `finalize_submission_metadata.py` on the extracted submission folder, or edit the files specified below. Then recompile both manuscripts and regenerate the letters' PDFs. Keep the historical v1.3 DOI in provenance; do not globally replace historical records.
10. Do not move or overwrite the released tag just to add its own newly minted DOI. A subsequent citation-only commit on the working branch can record it; the already published archive is immutable. A future substantive release gets another version.

## Route B Existing record was uploaded manually

1. Commit the corrected source to GitHub and create the intended release for traceability.
2. On the existing Zenodo record, click **New version**, not New upload. Confirm the form identifies a new version draft of the existing record.
3. Upload QuantXAI_Zenodo_Final.zip. Remove superseded imported ZIPs from this new draft, retaining historical versions. Set resource type Software, actual version, authors and CC-BY-4.0 licence consistently with the supplied metadata. Link the exact GitHub release.
4. Use any DOI reserved by this draft only after confirming it belongs to this version. Never reuse the prior version DOI. Publish when the metadata and files are correct.
5. Verify the public download and version history, then update the submission as in Route A step 9. Avoid creating a second automatic GitHub deposit for the same release.

## Release notes

This release aligns the manuscript, tables and provenance with saved notebook outputs for the Scientific Reports minor revision. It preserves original research notebooks and experimental numbers, restores rounded full-split and matched-calibration summaries, clarifies QAT controls and seeds, corrects Methods descriptions, and adds a CPU-only consistency audit and portable figure-generation paths. Twelve raw-derived summary/statistical tables and nine seed-42 control tests were checked. No new model training or inference was performed. Matching full-split/calibration per-image records are unavailable, and SIIM repaired execution remains incompletely verified. These limits are documented in FINAL_AUDIT.md.

## Verify the public download

Confirm it contains the two original research notebooks, the oneshot notebook under provenance, RAW_drift_all.csv, RAW_qat_drift.csv, N25/N26 summaries, REGEN_FIGURES.py, requirements.txt, audit_release.py, Audit_Notebook_Results.ipynb, provenance and the licence. Confirm the conflicting full-split raw file is absent from active tables. Check hashes against provenance/SHA256SUMS.csv. Source images, trained checkpoints and ONNX binaries are intentionally not included.

## Final journal files

The present manuscript cites historical v1.3 for base code and Supplementary Data 1 for corrected tables. This wording can only be submitted after verifying the historical public archive actually contains the claimed code. To instead cite your newly published corrected release, run the supplied finalizer with its actual DOI/version/tag; it updates main.tex, main_review.tex, references.bib and both DOCX letters in the submission folder. Recompile with `latexmk -pdf main.tex main_review.tex` and export the two updated letters to PDF. Do not submit stale PDFs from before a metadata edit.

Upload main.pdf as the clean manuscript, the source ZIP if requested, main_review.pdf where a line-numbered review copy is accepted, the response and cover letter, and Supplementary_Data_1.zip. Follow the portal's exact file categories. The requested revision deadline in the supplied verdict is 10 October 2026.

## Official instructions checked for this guide

- https://help.zenodo.org/docs/github/enable-repository/
- https://help.zenodo.org/docs/github/archive-software/github-upload/
- https://help.zenodo.org/docs/github/describe-software/citation-file/
- https://help.zenodo.org/docs/deposit/manage-versions/

These sources describe enabling the integration, publishing a release, metadata precedence and versioning. The actual integration/ownership state of this repository was not observable during the audit.
