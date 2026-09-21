from pathlib import Path
import json, csv, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
PAPER=ROOT/'results'/'paper'
FIG=PAPER/'figures'
FIG.mkdir(parents=True, exist_ok=True)
D=json.loads((PAPER/'paper_tables.json').read_text())
plt.rcParams.update({'font.size':8.5,'axes.titlesize':9.5,'axes.labelsize':8.5,'legend.fontsize':7.5,'figure.dpi':160,'savefig.dpi':300,'axes.spines.top':False,'axes.spines.right':False})

def save(fig,name):
    fig.tight_layout()
    fig.savefig(FIG/f'{name}.png', bbox_inches='tight')
    fig.savefig(FIG/f'{name}.pdf', bbox_inches='tight')
    plt.close(fig)

# Figure RQ1/RQ2: FDR and power across calibration procedures at the headline
# CSE2018 cell, for both registered targets. Captions carry the message; the
# figure carries no title of its own (journal style).
rows=D['rq1_rq2_draws']['rows']
order=['marginal BH','Storey-BH','BY','e-BH','PACT conditional L=1','PACT conditional L=5','PACT conditional L=100 (shipped)']
labels=['Bates BH','Storey-BH','BY','e-BH','PACT $L$=1','PACT $L$=5','PACT $L$=100']
colors=['#555555','#777777','#777777','#777777','#176b87','#176b87','#d55e00']
fig,axes=plt.subplots(2,2,figsize=(8.2,5.6),sharex=True)
for row,q in enumerate((0.1,0.2)):
    lookup={r['arm']:r for r in rows if r['dataset']=='cse2018' and r['q']==q and r['prevalence']==0.01}
    x=np.arange(len(order))
    fdr=[lookup[o]['fdr']['mean'] for o in order]; fdrerr=[lookup[o]['fdr']['ci95'] for o in order]
    power=[lookup[o]['power']['mean'] for o in order]; powerr=[lookup[o]['power']['ci95'] for o in order]
    a,b=axes[row]
    a.bar(x,fdr,yerr=fdrerr,capsize=3,color=colors,edgecolor='black',linewidth=.3)
    a.axhline(q,color='#b2182b',ls='--',lw=1); a.set_ylim(0,max(.18,1.6*q)); a.set_ylabel('Stream FDR')
    a.text(.02,.95,f'({"ac"[row]}) $q$ = {q:.2f}: realised FDR',transform=a.transAxes,va='top',fontsize=8.5)
    b.bar(x,power,yerr=powerr,capsize=3,color=colors,edgecolor='black',linewidth=.3)
    b.set_ylim(0,1.12); b.set_ylabel('Power')
    b.text(.02,.97,f'({"bd"[row]}) $q$ = {q:.2f}: power',transform=b.transAxes,va='top',fontsize=8.5)
for a in axes.ravel(): a.grid(axis='y',alpha=.2)
for a in axes[1]: a.set_xticks(np.arange(len(order)),labels,rotation=35,ha='right')
save(fig,'fig_rq1_rq2_keepability')

# Figure RQ1: four-dataset small multiples. The detector-panel range is shown as
# a light envelope rather than eight overlapping lines; PCF is highlighted because
# it is the score used for the headline certification analysis. A log prevalence
# axis makes the one-order-of-magnitude change in pi explicit.
cells=D['rq1_panel_barrier']['cells']
methods=['hedl','closr','efc','renoir_dml','ori','docpp','ais_nids','usfad']
prevs=[0.001,0.01]
datasets=[('cicids2017','CICIDS2017'),('cse2018','CSE2018'),('ciciomt2024','CICIoMT2024'),('toniot','ToN-IoT')]
fig,axes=plt.subplots(2,2,figsize=(7.2,4.9),sharey=True)
for ax,(dataset,title) in zip(axes.ravel(),datasets):
    panel_means=[]
    for p in prevs:
        vals=[]
        for method in methods:
            rs=[r for r in cells if r['dataset']==dataset and r['method']==method and r['prevalence']==p]
            vals.append(rs[0]['training_conditional']['mean'] if rs else np.nan)
        panel_means.append(vals)
    panel_means=np.asarray(panel_means,dtype=float)
    lo=np.nanmin(panel_means,axis=1)
    hi=np.nanmax(panel_means,axis=1)
    med=np.nanmedian(panel_means,axis=1)
    x=np.asarray(prevs,dtype=float)
    ax.fill_between(x,lo,hi,color='#BDBDBD',alpha=.28,zorder=1,label='Detector-panel range')
    ax.plot(x,med,color='#7A7A7A',lw=1.1,ls='--',zorder=2,label='Panel median')
    pc=sorted([r for r in cells if r['dataset']==dataset and r['method']=='hedl'],key=lambda r:r['prevalence'])
    y=[r['training_conditional']['mean'] for r in pc]
    e=[r['training_conditional']['ci95'] for r in pc]
    ax.errorbar(x,y,yerr=e,color='#0072B2',marker='o',lw=2.0,ms=4.5,capsize=3,elinewidth=1.0,zorder=4,label='PCF')
    ax.set_title(title,loc='left',fontweight='bold')
    if dataset=='ciciomt2024': ax.text(.5,.55,'audit refuses: power not certified',transform=ax.transAxes,ha='center',fontsize=7.5,color='#b2182b')
    ax.set_xscale('log')
    ax.set_xlim(8e-4,1.25e-2)
    ax.set_xticks(prevs,[r'$10^{-3}$',r'$10^{-2}$'])
    ax.get_xaxis().set_minor_locator(plt.NullLocator())
    ax.set_ylim(-.03,1.05)
    ax.grid(axis='y',alpha=.22,linewidth=.7)
    ax.grid(axis='x',which='major',alpha=.12,linewidth=.7)
    if dataset in ('ciciomt2024','toniot'): ax.set_xlabel(r'Unknown-attack prevalence, $\pi$')
    if dataset in ('cicids2017','ciciomt2024'): ax.set_ylabel('Training-conditional power')
handles=[plt.Rectangle((0,0),1,1,color='#BDBDBD',alpha=.45,label='Detector-panel range'),plt.Line2D([0],[0],color='#7A7A7A',lw=1.1,ls='--',label='Panel median'),plt.Line2D([0],[0],color='#0072B2',lw=2.0,marker='o',label='PCF')]
fig.legend(handles=handles,loc='upper center',ncol=3,frameon=False,bbox_to_anchor=(.5,1.0),columnspacing=1.2)
fig.tight_layout(rect=(0,0,1,.94))
save(fig,'fig_rq1_prevalence_barrier')

# Figure RQ3: score ceiling ties and tail-lift TPR@1e-3
T=D['rq3_tail']['datasets']; ds=['cicids2017','ciciomt2024','cse2018','toniot']; names=['CICIDS2017','CICIoMT2024','CSE2018','ToN-IoT']
fig,ax=plt.subplots(1,2,figsize=(8,3.3))
x=np.arange(4); w=.36
floor_ties=[T[d]['floored_ties_at_max']['mean'] for d in ds]; tail_ties=[T[d]['tail_lifted_ties_at_max']['mean'] for d in ds]
ax[0].bar(x-w/2,floor_ties,w,label='Floored',color='#999999'); ax[0].bar(x+w/2,tail_ties,w,label='Tail-lifted',color='#0072B2'); ax[0].set_yscale('symlog',linthresh=1); ax[0].set_ylabel('Flows tied at score maximum'); ax[0].set_title('(a) Flows tied at the score maximum'); ax[0].legend(frameon=False)
floor=[T[d]['floored_tpr@0.001']['mean'] for d in ds]; tail=[T[d]['tail_lifted_tpr@0.001']['mean'] for d in ds]
ax[1].bar(x-w/2,floor,w,label='Floored',color='#999999'); ax[1].bar(x+w/2,tail,w,label='Tail-lifted',color='#0072B2'); ax[1].set_ylim(0,1.05); ax[1].set_ylabel('TPR at FAR = 10⁻³'); ax[1].set_title('(b) TPR at FPR $10^{-3}$');
for a in ax: a.set_xticks(x,names,rotation=25,ha='right'); a.grid(axis='y',alpha=.2)
save(fig,'fig_rq3_tail_lift')

# Figure RQ3: ranking quality against certifiable power. Each point is one
# detector on one dataset's primary rotation at pi = 0.01, full calibration set.
overall=D['rq3_panel']['overall']; methods_order=['hedl','usfad','ais_nids','renoir_dml','ori','closr','docpp','efc']; lab={'hedl':'PCF','usfad':'usfAD','ais_nids':'AIS-NIDS','renoir_dml':'RENOIR','ori':'ORI','closr':'CLOSR','docpp':'DOC++','efc':'EFC'}
cells=D['rq1_panel_barrier']['cells']
fig,axes=plt.subplots(1,4,figsize=(9.2,2.9),sharey=True)
for ax,(dataset,title) in zip(axes,datasets):
    pts=[(r['method'],r['auroc']['mean'],r['training_conditional']['mean']) for r in cells if r['dataset']==dataset and r['prevalence']==0.01]
    for m,au,pw in pts:
        ax.scatter(au,pw,s=34 if m=='hedl' else 20,color='#d55e00' if m=='hedl' else '#666666',zorder=3,edgecolor='black',linewidth=.3)
        if pw>0.05 or m=='hedl': ax.annotate(lab[m],(au,pw),textcoords='offset points',xytext=(-4,5),fontsize=6.5,ha='right')
    ax.axvline(0.9,color='#999999',ls=':',lw=.8)
    ax.set_title(title,loc='left',fontweight='bold',fontsize=9); ax.set_xlim(0,1.02); ax.set_ylim(-.04,1.04)
    ax.set_xlabel('Unknown AUROC'); ax.grid(alpha=.2)
    if dataset=='ciciomt2024': ax.text(.05,.55,'audit refuses',transform=ax.transAxes,fontsize=7,color='#b2182b')
axes[0].set_ylabel(r'Certified power, $\pi$ = 0.01')
save(fig,'fig_rq3_detector_panel')

# Figure RQ4: temporal audit and alerting
A=D['temporal']['audit']; L=D['temporal']['alerting']
labels=['CSE2018\nrandom','CSE2018\ntemporal','ToN-IoT\nrandom','ToN-IoT\ntemporal']; keys=['cse2018::random (Z1)','cse2018::temporal (T2)','toniot::random (Z1)','toniot::temporal (T2)']; viol=[A[k]['violation']['mean'] for k in keys]; bound=[A[k]['bound'] for k in keys]
fdr_keys=['cse2018::marginal BH','cse2018::PACT conditional L=100 (shipped)']; fdr_random=[L[k]['Z1']['fdr'] for k in fdr_keys]; fdr_temp=[L[k]['T2']['fdr'] for k in fdr_keys]
fig,ax=plt.subplots(1,2,figsize=(8.0,3.0)); x=np.arange(4); ax[0].bar(x,viol,color=['#4daf4a','#d73027','#4daf4a','#d73027']); ax[0].errorbar(x,viol,yerr=[A[k]['violation']['ci95'] for k in keys],fmt='none',ecolor='black',capsize=3); ax[0].scatter(x,bound,marker='_',s=500,color='black',zorder=4,label='audit threshold'); ax[0].set_xticks(x,labels); ax[0].set_ylabel('Audit violation'); ax[0].set_title('(a) Exchangeability audit'); ax[0].legend(frameon=False)
x2=np.arange(2); width=.35; ax[1].bar(x2-width/2,fdr_random,width,label='Random split',color='#4daf4a'); ax[1].bar(x2+width/2,fdr_temp,width,label='Temporal split',color='#d73027'); ax[1].axhline(.1,color='black',ls='--',lw=1,label='q = 0.10'); ax[1].set_xticks(x2,['Bates BH','PACT L=100']); ax[1].set_ylabel('Stream FDR'); ax[1].set_title('(b) CSE2018 stream FDR, $q$ = 0.10'); ax[1].legend(frameon=False,loc='center')
for a in ax: a.grid(axis='y',alpha=.2)
save(fig,'fig_rq4_temporal_shift')

# Figure ablations
M=D['method_components']; labels=['Encoder removed','KNN removed','Curvature 0.5','Evidential term']
vals=[min(r['difference'] for r in M['encoder']['records']), -M['knn']['difference'], M['curvature']['difference'], M['evidential_pooled']['difference']]
fig,ax=plt.subplots(figsize=(6.5,3.1)); x=np.arange(4); ax.bar(x,vals,color=['#d73027','#d55e00','#999999','#999999']); ax.axhline(0,color='black',lw=.8); ax.set_xticks(x,labels,rotation=25,ha='right'); ax.set_ylabel('Change in unknown AUROC'); ax.grid(axis='y',alpha=.2); save(fig,'fig_ablation_components')

# Curated CSVs for Prism
OUT=PAPER/'prism_summaries'; OUT.mkdir(exist_ok=True)
with (OUT/'rq1_rq2_keepability.csv').open('w',newline='') as f:
 w=csv.writer(f); w.writerow(['dataset','q','prevalence','arm','calibration_size','fdr_mean','fdr_ci95','power_mean','power_ci95','draws_over_q','seeds_over_q'])
 for r in rows: w.writerow([r['dataset'],r['q'],r['prevalence'],r['arm'],r['calibration_size'],r['fdr']['mean'],r['fdr']['ci95'],r['power']['mean'],r['power']['ci95'],r['draws_over_q'],r['seeds_over_q']])
with (OUT/'rq3_panel_overall.csv').open('w',newline='') as f:
 w=csv.writer(f); w.writerow(['method','mean_unknown_auroc','ci95','mean_rank'])
 ranks=D['rq3_panel']['tests']['mean_rank']
 for m in methods_order: w.writerow([lab[m],overall[m]['mean'],overall[m].get('ci95',0),ranks[m]])
with (OUT/'rq4_temporal.csv').open('w',newline='') as f:
 w=csv.writer(f); w.writerow(['condition','audit_violation_mean','audit_ci95','dkw_bound','refused','bates_bh_fdr','pact_fdr'])
 for k,label in zip(keys,labels): w.writerow([label,A[k]['violation']['mean'],A[k]['violation']['ci95'],A[k]['bound'],A[k]['refused'],L.get('cse2018::marginal BH',{}).get('Z1' if 'random' in k else 'T2',{}).get('fdr'),L.get('cse2018::PACT conditional L=100 (shipped)',{}).get('Z1' if 'random' in k else 'T2',{}).get('fdr')])
print('wrote',len(list(FIG.glob('*.pdf'))),'PDF figures and',len(list(OUT.glob('*.csv'))),'CSV summaries')
