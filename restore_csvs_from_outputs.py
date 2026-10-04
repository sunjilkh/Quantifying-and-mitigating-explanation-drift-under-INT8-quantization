"""Restore rounded summary exports from saved notebook output; no model inference."""
from pathlib import Path
import argparse, csv, hashlib, json, math, re, shutil, zipfile


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def outputs(p):
    nb = json.loads(Path(p).read_text(encoding='utf-8'))
    texts = []
    for i, cell in enumerate(nb['cells']):
        for j, output in enumerate(cell.get('outputs', [])):
            text = output.get('text', output.get('data', {}).get('text/plain', []))
            text = ''.join(text) if isinstance(text, list) else text
            if text:
                texts.append((i, j, text))
    return nb, texts


def readcsv(p):
    with Path(p).open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def writecsv(p, fields, rows):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)


def printed_table(text, fields, expected_rows):
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.split() == fields:
            result = []
            for item in lines[i + 1:]:
                parts = item.split()
                if len(parts) != len(fields):
                    break
                result.append(dict(zip(fields, parts)))
                if len(result) == expected_rows:
                    return result
    raise ValueError('Complete stored output table not found: ' + ','.join(fields))


def equivalent(a, b, tolerance=0.000051):
    try:
        return abs(float(a) - float(b)) <= tolerance
    except (ValueError, TypeError):
        return str(a) == str(b)


def compare_table(path, fields, rows, keyfields):
    oldfields, oldrows = readcsv(path)
    oldmap = {tuple(r[k] for k in keyfields): r for r in oldrows}
    changes = []
    for row in rows:
        key = tuple(row[k] for k in keyfields)
        old = oldmap.get(key)
        if old is None:
            changes.append({'file': str(path), 'key': '|'.join(key), 'column': '(row)', 'original': '(missing)', 'restored': json.dumps(row)})
        else:
            for field in fields:
                if field in old and not equivalent(old[field], row[field]):
                    changes.append({'file': str(path), 'key': '|'.join(key), 'column': field, 'original': old[field], 'restored': row[field]})
    return changes


def main(archive, primary, reanalysis, oneshot, out):
    archive, primary, reanalysis, oneshot, out = map(Path, [archive, primary, reanalysis, oneshot, out])
    if out.exists():
        raise FileExistsError('Choose a new output directory; existing output is preserved: ' + str(out))
    if archive.is_dir():
        original = archive
    else:
        original = out.parent / (out.name + '_original_extracted')
        if original.exists():
            raise FileExistsError(str(original))
        original.mkdir(parents=True)
        with zipfile.ZipFile(archive) as z:
            for member in z.namelist():
                resolved = (original / member).resolve()
                if not resolved.is_relative_to(original.resolve()):
                    raise ValueError('Unsafe ZIP path: ' + member)
            z.extractall(original)
        matches = list(original.rglob('tables/RAW_drift_all.csv'))
        if len(matches) != 1:
            raise ValueError('Expected exactly one original tables/RAW_drift_all.csv')
        original = matches[0].parent.parent
    shutil.copytree(original, out)
    evidence = out / 'provenance'; evidence.mkdir(exist_ok=True)
    legacy = evidence / 'superseded_originals'; legacy.mkdir(exist_ok=True)
    changes = []
    replacements = []
    sources = [primary, reanalysis, oneshot]
    notebooks = {}
    for source in sources:
        shutil.copy2(source, evidence / source.name)
        nb, txts = outputs(source)
        notebooks[source.name] = (nb, txts)
    _, reout = notebooks[reanalysis.name]
    printed = next(t for _, _, t in reout if 'N26_fullsplit_cam.csv' in t and '0.7285' in t)
    sourcecell, sourceoutput, _ = next(x for x in reout if x[2] == printed)
    (evidence / 'reanalysis_stored_stdout.txt').write_text(printed, encoding='utf-8')
    primarytext = '\n'.join(t for _, _, t in notebooks[primary.name][1])
    (evidence / 'primary_stored_stdout.txt').write_text(primarytext, encoding='utf-8')
    mainrel = Path('tables/onnx all')

    def restore(rel, fields, rows, keyfields, reason):
        target = out / rel
        if target.exists():
            original_copy = legacy / rel
            original_copy.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, original_copy)
            changes.extend(compare_table(target, fields, rows, keyfields))
        writecsv(target, fields, rows)
        replacements.append({'file': str(rel), 'source': reanalysis.name, 'cell_index': sourcecell, 'output_index': sourceoutput, 'reason': reason, 'rows': len(rows), 'precision': 'stored rounded values; not exact original export bytes'})

    fields = 'arch xai n iou dice rho agreement collapse_rate'.split()
    fullrows = printed_table(printed, fields, 6)
    assert {r['n'] for r in fullrows} == {'2082'}
    restore(mainrel / 'N26_fullsplit_cam.csv', fields, fullrows, ['arch', 'xai'], 'six summary rows transcribed from complete stored output')
    primarymeans = {(r['arch'], r['xai']): r['iou'] for r in readcsv(out / 'tables/T6_drift_by_model_method.csv')[1] if r['sim'] == 'qdq'}
    gatefields = 'arch xai n reproduced_iou published_iou abs_delta'.split()
    gates = []
    arch = None
    for line in printed.splitlines():
        match = re.search(r'\]\s+(tf_efficientnetv2_s|resnet50|mobilenetv3_large_100) CAM layer=', line)
        if match:
            arch = match.group(1)
        match = re.search(r'GATE (gradcampp|gradcam)\s+reproduced=([\d.]+) published=([\d.]+)', line)
        if match:
            method, value, baseline = match.groups()
            assert arch is not None and equivalent(primarymeans[(arch, method)], baseline)
            gates.append(dict(arch=arch, xai=method, n=320, reproduced_iou=value, published_iou=baseline, abs_delta=f'{abs(float(value)-float(baseline)):.4f}'))
    assert len(gates) == 6
    restore(mainrel / 'N26_fullsplit_cam_gate.csv', gatefields, gates, ['arch', 'xai'], 'six gate values copied from logs; absolute differences derived from displayed four-decimal values')
    fields = 'arch engine calib_source calib_method n_calib n_eval agreement int8_acc fp32_acc size_mb published_n_calib published_agreement published_int8_acc delta_vs_published rebuild_fidelity_maxabs_delta_at_matched_n'.split()
    calrows = printed_table(printed, fields, 9)
    m = re.search(r'calibration tensor: \((\d+), 3, 224, 224\)', printed)
    assert m and m.group(1) == '60'
    for row in calrows:
        row['n_calib_requested'] = row['n_calib']
        row['n_calib'] = 60
    restore(mainrel / 'N25_calibration_matched64.csv', fields + ['n_calib_requested'], calrows, ['arch', 'calib_method'], 'newly recovered summary; actual n_calib=60 from tensor log, requested cap64 retained separately')
    fields = ['task', 'status', 'detail']
    tail = printed.split('CELL 23 COMPLETE', 1)[1]
    statuses = []
    for line in tail.splitlines():
        m = re.match(r'\s*(SPLIT_reconstruction|D_calib_matched64|E_fullsplit_cam)\s+(OK|FAILED|SKIPPED)\s+(.+)', line)
        if m:
            statuses.append(dict(zip(fields, m.groups())))
    assert len(statuses) == 3
    restore(mainrel / 'N00_rev3_status.csv', fields, statuses, ['task'], 'only the three tasks printed by the selected execution; status details retain original requested64 wording')
    inv = out / mainrel / 'N23_sample_size_inventory.csv'
    fields, rows = readcsv(inv)
    oldcopy = legacy / mainrel / inv.name; oldcopy.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(inv, oldcopy)
    for row in rows:
        if row['analysis'] == 'Calibration subset':
            row['n'] = '60'; row['justification'] = 'actual matched-calibration tensor has60 images (six per class); requested cap64'
        if row['analysis'].startswith('Paired drift observations'):
            row['analysis'] = 'Paired drift observations (3 arch x [3 xai x 320 + LIME x 120])'
            row['justification'] = '3240 repeated observations on320 images (120 for LIME), not independent images'
    writecsv(inv, fields, rows)
    replacements.append({'file': str(mainrel / inv.name), 'source': 'notebook calibration tensor log and primary recorded sample sizes', 'reason': 'correct actual calibration count and pooled-count formula; no result means changed', 'rows': len(rows)})
    # Incorrect comparator names refer to lambda0, not lambda0.5. Rename, without changing observations.
    control = out / mainrel / 'N21_qat_vs_lambda0.csv'
    fields, rows = readcsv(control)
    oldcopy = legacy / mainrel / control.name; shutil.copy2(control, oldcopy)
    rename = {'d_qat_vs_ptq': 'd_lam0_vs_ptq', 'pct_qat_vs_ptq': 'pct_lam0_vs_ptq'}
    for row in rows:
        for before, after in rename.items():
            row[after] = row.pop(before)
        row['paired_test_seed'] = '42'
    fields = [rename.get(field, field) for field in fields] + ['paired_test_seed']
    writecsv(control, fields, rows)
    replacements.append({'file': str(mainrel / control.name), 'source': 'RAW_qat_drift.csv and notebook comparison convention', 'reason': 'rename lambda0-versus-PTQ delta fields and explicitly mark paired seed42; values retained', 'rows': len(rows)})
    # Per-image records cannot be recovered from six rounded means. Keep originals separate and unchanged.
    rawrel = mainrel / 'RAW_fullsplit_cam.csv'
    raw = out / rawrel
    historical = legacy / rawrel; historical.parent.mkdir(parents=True, exist_ok=True); shutil.move(raw, historical)
    assert digest(historical) == digest(original / rawrel)
    (out / mainrel / 'RAW_fullsplit_cam_UNAVAILABLE.md').write_text('''# Full-split raw records not recoverable from notebook output
The selected notebook prints six aggregate rows and six reproduction-gate logs, not12492 individual image records. No replacement RAW_fullsplit_cam.csv has been created. The v1.3 raw file belongs to the conflicting CSV-backed run and is preserved byte-for-byte at provenance/superseded_originals/tables/onnx all/RAW_fullsplit_cam.csv. It must not be used to validate the restored notebook-summary values. The matching raw export or a fresh model/calibration rerun is still needed for per-image reproducibility.\n''')
    replacements.append({'file': str(rawrel), 'status': 'UNRECOVERABLE', 'reason': 'matching per-image values absent from stored output; original conflicting-run records preserved separately'})
    # Export LaTeX bodies only for recovered/clarified tables; primary figures use unchanged source CSVs.
    for item in replacements:
        rel = item['file']
        if item.get('status') == 'UNRECOVERABLE':
            continue
        fields, rows = readcsv(out / rel)
        esc = lambda x: str(x).replace('\\', r'\textbackslash{}').replace('_', r'\_').replace('%', r'\%').replace('&', r'\&')
        body = ['% Rounded summary restored or metadata clarified; see provenance/RESTORATION_MANIFEST.json', '\\begin{tabular}{' + 'l' * len(fields) + '}', ' & '.join(map(esc, fields)) + r' \\']
        body += [' & '.join(esc(row[field]) for field in fields) + r' \\' for row in rows]
        body += ['\\end{tabular}']
        target = out / 'tables_latex/onnx all' / (Path(rel).stem + '.tex'); target.parent.mkdir(parents=True, exist_ok=True); target.write_text('\n'.join(body) + '\n')
    # Primary stdout checks: all21 QAT logs agree with archived raw means and F1; all9 ORT summary rows match.
    qfields, qrows = readcsv(out / 'tables/RAW_qat_drift.csv')
    groups = {}
    for row in qrows:
        if float(row['k']) == 0.15:
            key = (row['arch'], float(row['lam']), int(row['seed']))
            groups.setdefault(key, []).append(float(row['topk_iou']))
    n12map = {(r['arch'], float(r['lam']), int(r['seed'])): r for r in readcsv(out / 'tables/N12_post_qat_performance.csv')[1] if r['stage'] == 'QAT-INT8'}
    logged = re.findall(r'\[(\w+) lam=([0-9.]+) s=(\d+)\] f1=([0-9.]+) IoU=([0-9.]+) collapse=([0-9.]+)', primarytext)
    assert len(logged) == 21
    for arch, lam, seed, f1, iou, collapse in logged:
        key = (arch, float(lam), int(seed))
        assert equivalent(sum(groups[key]) / len(groups[key]), iou)
        assert equivalent(n12map[key]['macro_f1'], f1)
    n20fields = 'arch engine calib n fp32_acc int8_acc agreement logit_mae logit_max logit_cos agreement_n320 delta_vs_subset'.split()
    n20rows = printed_table(primarytext, n20fields, 9)
    assert not compare_table(out / 'tables/N20_ort_full_equivalence.csv', n20fields, n20rows, ['arch', 'calib'])
    # Identical copies of the two deposited notebooks; third combined notebook is not a duplicate.
    bytecheck = []
    for source in sources:
        bytecheck.append({'file': source.name, 'size_bytes': source.stat().st_size, 'sha256': digest(source)})
    an = notebooks[primary.name][0]; bn = notebooks[oneshot.name][0]; rn = notebooks[reanalysis.name][0]
    comparison = {'files': bytecheck, 'primary_vs_oneshot_byte_identical': primary.read_bytes() == oneshot.read_bytes(), 'primary_cells': len(an['cells']), 'oneshot_cells': len(bn['cells']), 'first24_cell_sources_equal': all(a['cell_type']==b['cell_type'] and a['source']==b['source'] for a,b in zip(an['cells'][:24],bn['cells'][:24])), 'additional_oneshot_cell24_has_same_reanalysis_stdout': ''.join(bn['cells'][24]['outputs'][0]['text']) == printed, 'primary_final_plotting_source_equals_oneshot_final_plotting_source': ''.join(an['cells'][25]['source']).strip() == ''.join(bn['cells'][26]['source']).strip(), 'recommendation': 'KEEP oneshot: not a duplicate; it contains the additional full-split/calibration source and stored output.'}
    (evidence / 'NOTEBOOK_COMPARISON.json').write_text(json.dumps(comparison, indent=2) + '\n')
    # Original evidence is retained; old manifests/indexes do not remain authoritative.
    for name in ['README.md', 'MANIFEST.json', 'TABLE_INDEX.csv']:
        shutil.copy2(out / name, legacy / name)
    idx = []
    for file in sorted((out / 'tables').rglob('*.csv')):
        fields, rows = readcsv(file)
        idx.append({'table': file.stem, 'rows': len(rows), 'cols': len(fields), 'csv': str(file.relative_to(out)), 'tex': str(Path('tables_latex') / file.relative_to(out / 'tables').with_suffix('.tex')) if (out / 'tables_latex' / file.relative_to(out / 'tables').with_suffix('.tex')).exists() else ''})
    writecsv(out / 'TABLE_INDEX.csv', ['table','rows','cols','csv','tex'], idx)
    manifest = {'date': '2026-10-03', 'mode': 'offline rounded summary restoration; no inference', 'base_release_doi': '10.5281/zenodo.21887946', 'sources': bytecheck, 'restored_or_clarified': replacements, 'raw_fullsplit_status': 'matching raw records unavailable; no invented or adjusted per-image values', 'validation': {'qat_logged_runs_checked': 21, 'ort_summary_rows_checked': 9, 'maximum_gate_difference_from_displayed_values': max(float(r['abs_delta']) for r in gates)}, 'active_csv_count': len(idx), 'tables': {x['csv']: [x['rows'],x['cols']] for x in idx}}
    (out / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (evidence / 'RESTORATION_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    for row in changes:
        row['file'] = str(Path(row['file']).relative_to(out))
    writecsv(evidence / 'CHANGED_VALUES.csv', ['file','key','column','original','restored'], changes)
    audit = []
    replaced = {item['file']: item for item in replacements}
    for file in sorted((original / 'tables').rglob('*.csv')):
        rel = str(file.relative_to(original))
        if rel in replaced:
            item = replaced[rel]; status = item.get('status','RESTORED_OR_CLARIFIED'); basis=item['reason']
        elif file.name in ['RAW_qat_drift.csv', 'N12_post_qat_performance.csv']:
            status='RETAINED_CHECKED';basis='21 logged QAT F1/pooled-IoU values agree within output rounding; individual records not printed'
        elif file.name=='N20_ort_full_equivalence.csv':
            status='RETAINED_CHECKED';basis='all9 complete stored ORT summary rows match within rounding'
        else:
            status='RETAINED_NO_PROVEN_MISMATCH';basis='complete table values not printed in stored outputs; original bytes retained, not independently recovered'
        audit.append(dict(file=rel,action=status,basis=basis,original_sha256=digest(file),final_sha256=digest(out/rel) if (out/rel).exists() else '',rows=len(readcsv(file)[1])))
    audit.append(dict(file=str(mainrel/'N25_calibration_matched64.csv'),action='ADDED_FROM_OUTPUT',basis='9 complete rows; actual n60 versus requested64',original_sha256='',final_sha256=digest(out/mainrel/'N25_calibration_matched64.csv'),rows=9))
    writecsv(evidence/'CSV_AUDIT.csv', ['file','action','basis','original_sha256','final_sha256','rows'], audit)
    (out/'README.md').write_text('''# QuantXAI — notebook-output restoration package

Author: Sunzil Khandaker, BSc, Department of CSE, Daffodil International University. Contact: khandaker15-5383@diu.edu.bd.

This is a local replacement-package candidate based on Zenodo v1.3 (https://doi.org/10.5281/zenodo.21887946), not a published new release. Stored notebook summaries, rather than conflicting CSV summaries, are the selected source for the full-split results reported in the original manuscript. No experiments have been rerun. Values recovered from printed output are rounded and are not byte-exact recreations of the original exports.

## What was restored
- tables/onnx all/N26_fullsplit_cam.csv: six rows matching the notebook and original manuscript Table24.
- tables/onnx all/N26_fullsplit_cam_gate.csv: six gate values from logs; differences computed from four-decimal displayed values, maximum0.0064.
- tables/onnx all/N25_calibration_matched64.csv: missing nine-row summary recovered. n_calib is actual60; n_calib_requested preserves nominal64.
- tables/onnx all/N00_rev3_status.csv: the three statuses printed by the selected run.
- N23 sample inventory: actual calibration count and pooled sample formula clarified.
- N21 control summary: lambda0-versus-PTQ column names corrected; paired seed42 explicitly marked. Numeric result values are unchanged.
- TABLE_INDEX.csv, MANIFEST.json and the six associated LaTeX table bodies reflect the replacements.

## Matching full-split raw data remains missing
The notebook output does not contain the12492 individual image records. No replacement RAW_fullsplit_cam.csv was created. Its old conflicting-run version is preserved unchanged in provenance/superseded_originals/tables/onnx all/. Do not use it to validate the restored six summary rows. A matching original per-image export or model/calibration rerun is needed for full per-image reproducibility. This package restores reported summaries, not missing observations, model checkpoints or ONNX binaries.

## Files retained and checked
Original notebooks, primary figures, figure-generation script, requirements, licence and unrelated CSV bytes are preserved.21 primary QAT log values and9 complete ONNX Runtime summary rows match archived CSVs within displayed rounding. Other retained tables often have only filenames/shapes, not every value, in notebook stdout; no claim of complete output verification is made. CSV_AUDIT.csv records the status of every original table.

Figure5 still uses the unchanged tables/RAW_drift_all.csv. Its image, the other primary figures and REGEN_FIGURES.py need no numerical update for these full-split summary corrections. The archived main.tex is preserved as an existing source file, not presented as the newly edited manuscript.

## Notebook identity
quantxai-revision.ipynb and qat_calibration_reanalysis.ipynb are preserved byte-for-byte. The supplied quantxai-revision-oneshot-3.ipynb is separately preserved under provenance/: it is not a duplicate of the primary notebook. It adds the calibration/full-split analysis and has the same relevant reanalysis stdout. Keep it. NOTEBOOK_COMPARISON.json includes SHA256 hashes and source/output comparisons.

## Recreate this package
Use Restore_Zenodo_CSVs_from_Notebook_Outputs.ipynb or restore_csvs_from_outputs.py with the original archive and supplied notebooks. It reads stored outputs only, uses the Python standard library, and requires no GPU or model training. The recovery notebook is a new utility, not an experimentally executed replacement for either research notebook.

Detailed provenance and original conflicting files are preserved under provenance/. Do not describe the restored aggregate rows as raw per-image results or an end-to-end reproduced experiment.
''',encoding='utf-8')
    checksums = [{'file':str(f.relative_to(out)),'sha256':digest(f)} for f in sorted(out.rglob('*')) if f.is_file()]
    writecsv(evidence/'SHA256SUMS.csv',['file','sha256'],checksums)
    return manifest


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', required=True); parser.add_argument('--primary', required=True)
    parser.add_argument('--reanalysis', required=True); parser.add_argument('--oneshot', required=True); parser.add_argument('--out', required=True)
    args=parser.parse_args()
    result=main(args.archive,args.primary,args.reanalysis,args.oneshot,args.out)
    print(json.dumps({'active_csv_count':result['active_csv_count'],'restored_or_clarified':[x['file'] for x in result['restored_or_clarified']],'raw_fullsplit_status':result['raw_fullsplit_status']},indent=2))
