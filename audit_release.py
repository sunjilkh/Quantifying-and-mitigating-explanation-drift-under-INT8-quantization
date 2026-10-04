"""Offline checks of supplied results; never trains models or changes result tables."""
from pathlib import Path
import argparse, ast, contextlib, hashlib, json, types
import numpy as np
import pandas as pd
from scipy import stats as sstats

def audit(root):
    root=Path(root).resolve()
    d=pd.read_csv(root/'tables/RAW_drift_all.csv')
    q=pd.read_csv(root/'tables/RAW_qat_drift.csv')
    results=[]
    def compare(name,calc,keys):
        a=pd.read_csv(root/'tables'/f'{name}.csv').set_index(keys).sort_index()
        b=calc.set_index(keys).sort_index()
        assert a.index.equals(b.index),name
        dif={c:float((a[c].astype(float)-b[c].astype(float)).abs().max()) for c in b.columns if pd.api.types.is_numeric_dtype(b[c])}
        assert all(v<=0.000051 for v in dif.values()),(name,dif)
        results.append({'table':name,'rows':len(a),'max_absolute_difference':max(dif.values()),'status':'PASS'})
    m=d[d.k==.15];v=m[~m.collapsed];qm=q[q.k==.15];vq=qm[~qm.collapsed]
    a=v.groupby(['sim','arch','xai']).agg(n=('topk_iou','size'),iou=('topk_iou','mean'),iou_sd=('topk_iou','std'),dice=('topk_dice','mean'),dice_sd=('topk_dice','std'),rho=('spearman','mean'),rho_sd=('spearman','std')).reset_index().merge(m.groupby(['sim','arch','xai']).collapsed.mean().rename('collapse_rate').reset_index());compare('T6_drift_by_model_method',a,['sim','arch','xai'])
    a=v.groupby(['sim','xai']).agg(n=('topk_iou','size'),iou=('topk_iou','mean'),iou_sd=('topk_iou','std'),dice=('topk_dice','mean'),rho=('spearman','mean'),rho_sd=('spearman','std')).reset_index();a['cv_iou']=(a.iou_sd/a.iou).round(3);a['iou_over_chance']=(a.iou/(.15/1.85)).round(3);compare('T7_drift_by_method',a,['sim','xai'])
    a=d[~d.collapsed].groupby(['sim','arch','xai','k']).agg(iou=('topk_iou','mean'),dice=('topk_dice','mean'),rho=('spearman','mean'),n=('topk_iou','size')).reset_index();compare('N5_k_sweep',a,['sim','arch','xai','k'])
    a=m.groupby(['sim','arch','xai']).agg(n=('collapsed','size'),collapse_rate=('collapsed','mean'),fp32_collapsed=('collapsed_fp32','mean'),int8_collapsed=('collapsed_int8','mean'),mean_levels_int8=('n_levels_int8','mean')).reset_index();compare('N7_collapse_rates',a,['sim','arch','xai'])
    a=m.drop_duplicates(['sim','arch','image']).groupby(['sim','arch']).agg(n=('pred_match','size'),agreement=('pred_match','mean'),fp32_accuracy=('fp32_correct','mean')).reset_index();compare('T5_prediction_agreement',a,['sim','arch'])
    agg=vq.groupby(['arch','xai','lam']).agg(n=('topk_iou','size'),iou=('topk_iou','mean'),dice=('topk_dice','mean'),rho=('spearman','mean')).reset_index().merge(qm.groupby(['arch','xai','lam']).collapsed.mean().rename('collapse_rate').reset_index());compare('N10_lambda_sweep',agg,['arch','xai','lam'])
    b=v[v.sim=='qdq'].groupby(['arch','xai']).agg(base_iou=('topk_iou','mean'),base_dice=('topk_dice','mean'),base_rho=('spearman','mean'),base_n=('topk_iou','size')).reset_index();a=b.merge(agg[agg.lam==.5].drop(columns='lam').rename(columns={'n':'mit_n','iou':'mit_iou','dice':'mit_dice','rho':'mit_rho'}),on=['arch','xai'])
    for met in ['iou','dice','rho']:a[f'delta_{met}_pct']=((a[f'mit_{met}']-a[f'base_{met}'])/a[f'base_{met}'].abs()*100).round(1)
    compare('T8_qat_mitigation',a,['arch','xai'])
    a=vq[vq.lam==.5].groupby(['arch','xai','seed']).topk_iou.mean().reset_index().groupby(['arch','xai']).topk_iou.agg(['mean','std','count']).reset_index();compare('N11_seed_variability',a,['arch','xai'])
    nbpath=root/'quantxai-revision.ipynb'
    assert hashlib.sha256(nbpath.read_bytes()).hexdigest()=='1ac02c99eddcbd3c650b6039a503ef3fc3a5df7da8603a56787abd1edc9a8e39','Original notebook changed; review before executing its statistics cell'
    nb=json.loads(nbpath.read_text());generated={}
    ns=dict(np=np,pd=pd,sstats=sstats,DRIFT=d,CFG=types.SimpleNamespace(k_main=.15,seed=42,lambda_main=.5),RESULTS={'RAW_qat_drift':q},stage=lambda _:contextlib.nullcontext(),save=lambda name,df:generated.update({name:df}))
    exec(compile(''.join(nb['cells'][16]['source']),'saved_notebook_statistics','exec'),ns)
    for name,calc in generated.items():
        keys=[x for x in ['arch','xai','metric','comparison','target_delta'] if x in calc.columns];compare(name,calc,keys)
    rnb=json.loads((root/'qat_calibration_reanalysis.ipynb').read_text())
    text='\n'.join(''.join(o.get('text',[])) for c in rnb['cells'] for o in c.get('outputs',[]))
    from restore_csvs_from_outputs import printed_table
    fields='arch xai n iou dice rho agreement collapse_rate'.split()
    calc=pd.DataFrame(printed_table(text,fields,6))
    for c in fields[2:]:calc[c]=pd.to_numeric(calc[c])
    compare('onnx all/N26_fullsplit_cam',calc,['arch','xai'])
    fields='arch engine calib_source calib_method n_calib n_eval agreement int8_acc fp32_acc size_mb published_n_calib published_agreement published_int8_acc delta_vs_published rebuild_fidelity_maxabs_delta_at_matched_n'.split()
    calc=pd.DataFrame(printed_table(text,fields,9));assert 'calibration tensor: (60, 3, 224, 224)' in text
    calc['n_calib_requested']=calc.n_calib;calc['n_calib']=60
    for c in fields[4:]+['n_calib_requested']:calc[c]=pd.to_numeric(calc[c])
    compare('onnx all/N25_calibration_matched64',calc,['arch','calib_method'])
    n21=pd.read_csv(root/'tables/onnx all/N21_qat_vs_lambda0.csv');ps=[]
    for row in n21.itertuples():
        a=q[(q.k==.15)&(q.seed==42)&(q.arch==row.arch)&(q.xai==row.xai)]
        p=a.pivot(index='image',columns='lam',values='topk_iou')
        w,pval=sstats.wilcoxon(p[.5]-p[0],correction=True,method='approx');ps.append(pval)
        assert abs(w-row.W)<1e-8
        assert np.isclose(pval,row.p_raw,rtol=.006,atol=1e-30)
        assert abs(p[0].mean()-row.qat_lam0_iou)<.000051
        assert abs(p[.5].mean()-row.qat_lam05_iou)<.000051
    adjusted=ns['holm'](ps);assert np.allclose(adjusted,n21.p_holm,rtol=.006,atol=1e-30)
    results.append({'table':'onnx all/N21_qat_vs_lambda0','rows':9,'status':'PASS seed42 means and paired tests; rounded p-value tolerance 0.6%'})
    main=m[m.sim=='qdq'];means=main.groupby(['arch','xai']).topk_iou.mean()
    report={'date':'2026-10-04','model_inference_performed':False,'checks':results,'headline_checks':{'primary_pairs':len(main),'distinct_images':main.image.nunique(),'collapsed':int(main.collapsed.sum()),'median_spearman':float(main.spearman.median()),'mean_iou_min':float(means.min()),'mean_iou_max':float(means.max()),'negative_spearman_records':int((main.spearman<0).sum())},'limitations':['Full-split and matched-calibration validation is against rounded saved output only; matching per-image records absent.','SIIM repair execution is not substantiated by saved outputs.','No model inference, original saliency-map recomputation, or public-deposit verification.','Some auxiliary tables have no recoverable source records; retained with provenance, not declared independently reproduced.']}
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',default=str(Path(__file__).resolve().parent));parser.add_argument('--output');args=parser.parse_args();result=audit(args.root);print(json.dumps(result,indent=2))
    if args.output:Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
