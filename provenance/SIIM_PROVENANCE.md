# SIIM execution-record limitation

The original deposited N17 per-image CSV (174 records: 87 images × two precisions) and N17b summary are retained unchanged. Their mean IoU values agree internally within displayed rounding. This is a CSV consistency check, not verification of model execution.

The saved primary notebook records a failed SIIM CAM-layer call. Its subsequent repair cell has execution_count=null and no saved outputs. The original MANIFEST/PROGRESS metadata describes recovery but the supplied executed notebook does not substantiate successful repair. No new SIIM inference was performed. Preserve the results with this qualification; do not claim an independently reproduced successful run.
