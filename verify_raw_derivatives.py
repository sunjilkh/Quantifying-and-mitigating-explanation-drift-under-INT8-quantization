from pathlib import Path
import json
import numpy as np
import pandas as pd
import sys
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
d=pd.read_csv(root/'tables/RAW_drift_all.csv');q=pd.read_csv(root/'tables/RAW_qat_drift.csv')
main=d[d.k==.15];valid=main[~main.collapsed];qm=q[q.k==.15];vqm=qm[~qm.collapsed]
results=[]
def check(name,calc,keys):
 stored=pd.read_csv(root/'tables'/f'{name}.csv').set_index(keys).sort_index();calc=calc.set_index(keys).sort_index();assert stored.index.equals(calc.index)
 cols=[c for c in calc.columns if pd.api.types.is_numeric_dtype(calc[c])];a=stored[cols].astype(float);b=calc[cols].astype(float)
 diff=(a-b).abs();assert diff.max().max()<.000051,(name,diff.max().to_dict())
 results.append({'table':name,'rows':len(stored),'numeric_columns':cols,'maximum_absolute_difference':float(diff.max().max()),'status':'verified against archived raw data, not a new inference run'})
c=valid.groupby(['sim','arch','xai']).agg(n=('topk_iou','size'),iou=('topk_iou','mean'),iou_sd=('topk_iou','std'),dice=('topk_dice','mean'),dice_sd=('topk_dice','std'),rho=('spearman','mean'),rho_sd=('spearman','std')).reset_index();c=c.merge(main.groupby(['sim','arch','xai']).collapsed.mean().rename('collapse_rate').reset_index());check('T6_drift_by_model_method',c,['sim','arch','xai'])
c=valid.groupby(['sim','xai']).agg(n=('topk_iou','size'),iou=('topk_iou','mean'),iou_sd=('topk_iou','std'),dice=('topk_dice','mean'),rho=('spearman','mean'),rho_sd=('spearman','std')).reset_index();c['cv_iou']=(c.iou_sd/c.iou).round(3);c['iou_over_chance']=(c.iou/(.15/(2-.15))).round(3);check('T7_drift_by_method',c,['sim','xai'])
c=d[~d.collapsed].groupby(['sim','arch','xai','k']).agg(iou=('topk_iou','mean'),dice=('topk_dice','mean'),rho=('spearman','mean'),n=('topk_iou','size')).reset_index();check('N5_k_sweep',c,['sim','arch','xai','k'])
c=main.groupby(['sim','arch','xai']).agg(n=('collapsed','size'),collapse_rate=('collapsed','mean'),fp32_collapsed=('collapsed_fp32','mean'),int8_collapsed=('collapsed_int8','mean'),mean_levels_int8=('n_levels_int8','mean')).reset_index();check('N7_collapse_rates',c,['sim','arch','xai'])
c=main.drop_duplicates(['sim','arch','image']).groupby(['sim','arch']).agg(n=('pred_match','size'),agreement=('pred_match','mean'),fp32_accuracy=('fp32_correct','mean')).reset_index();check('T5_prediction_agreement',c,['sim','arch'])
agg=vqm.groupby(['arch','xai','lam']).agg(n=('topk_iou','size'),iou=('topk_iou','mean'),dice=('topk_dice','mean'),rho=('spearman','mean')).reset_index();agg=agg.merge(qm.groupby(['arch','xai','lam']).collapsed.mean().rename('collapse_rate').reset_index());check('N10_lambda_sweep',agg,['arch','xai','lam'])
b=valid[valid.sim=='qdq'].groupby(['arch','xai']).agg(base_iou=('topk_iou','mean'),base_dice=('topk_dice','mean'),base_rho=('spearman','mean'),base_n=('topk_iou','size')).reset_index();m=agg[agg.lam==.5].drop(columns=['lam']).rename(columns={'iou':'mit_iou','dice':'mit_dice','rho':'mit_rho','n':'mit_n'});c=b.merge(m,on=['arch','xai'])
for metric in ['iou','dice','rho']:c[f'delta_{metric}_pct']=((c[f'mit_{metric}']-c[f'base_{metric}'])/c[f'base_{metric}'].abs()*100).round(1)
check('T8_qat_mitigation',c,['arch','xai'])
c=vqm[vqm.lam==.5].groupby(['arch','xai','seed']).topk_iou.mean().reset_index().groupby(['arch','xai']).topk_iou.agg(['mean','std','count']).reset_index();check('N11_seed_variability',c,['arch','xai'])
(root/'provenance/RAW_DERIVATIVE_VALIDATION.json').write_text(json.dumps(results,indent=2)+'\n');print('All8 primary/QAT derivative tables agree with raw data within rounding.')
a=pd.read_csv(root/'provenance/CSV_AUDIT.csv').fillna('')
for r in results:
 sel=a.file==f"tables/{r['table']}.csv";a.loc[sel,'action']='RETAINED_RAW_DERIVATIVE_VERIFIED';a.loc[sel,'basis']='Every numeric aggregate checked against archived raw data using source-code grouping; within four-decimal rounding. No new model inference.'
a.to_csv(root/'provenance/CSV_AUDIT.csv',index=False)
