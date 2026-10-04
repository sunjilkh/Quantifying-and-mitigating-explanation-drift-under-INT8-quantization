# Recovery summary

Six CSVs restored or clarified; unrelated CSV values retained. The restored N26 full-split mean IoU values match the original paper: EfficientNetV2-S0.7285/0.6678; ResNet-500.7703/0.7781; MobileNetV3-Large0.4591/0.6841. The recovered reproduction gate has maximum displayed difference0.0064.

N25 matched calibration (9 rows) was missing from v1.3; restored from complete stored output, with actual60 images and requested64 recorded separately. N00 status now identifies the selected recorded run. N21 comparator labels and N23 sample metadata are clarified without changing model result values.

RAW_fullsplit_cam.csv cannot be recovered: no individual records are embedded in the notebook. Its conflicting old version is preserved unchanged under superseded_originals and is excluded from active tables. No per-image values were fabricated, adjusted or inferred from aggregate means.

Keep quantxai-revision-oneshot-3.ipynb. It has27 cells versus26 in the primary notebook, includes the additional reanalysis cell, and differs in bytes and source. Its relevant stored reanalysis stdout matches the standalone reanalysis notebook. The new recovery utility is a separate tool and is also not a duplicate of the primary notebook.

This is an offline summary restoration, not a new model experiment, a completed raw-data reproduction, or a published Zenodo update. No remote repository files were modified.
