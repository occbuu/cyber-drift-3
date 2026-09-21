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
plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','Times','DejaVu Serif'],'mathtext.fontset':'stix','font.size':8.5,'axes.titlesize':9.5,'axes.labelsize':8.5,'legend.fontsize':7.5,'figure.dpi':160,'savefig.dpi':300,'axes.spines.top':False,'axes.spines.right':False})

def save(fig,name,rect=None):
    # A figure-level legend or subtitle needs its own margin; tight_layout would
    # otherwise pull the axes over it.
    fig.tight_layout(rect=rect) if rect else fig.tight_layout()
    fig.savefig(FIG/f'{name}.png', bbox_inches='tight')
    fig.savefig(FIG/f'{name}.pdf', bbox_inches='tight')
    plt.close(fig)

# Figure RQ2: what a single calibration draw buys.  The mean FDR alone hides
# the claim: the marginal rule sits under the target on average and still
# exceeds it on a third of the draws an operator might have drawn.
rows=D['rq1_rq2_draws']['rows']
order=['marginal BH','Storey-BH','BY','e-BH','PACT conditional L=1','PACT conditional L=5','PACT conditional L=100 (shipped)']
labels=['Bates BH','Storey-BH','BY','e-BH','PACT L=1','PACT L=5','PACT L=100']
colors=['#555555','#777777','#777777','#777777','#176b87','#176b87','#d55e00']
fig,axes=plt.subplots(2,3,figsize=(9.6,5.4),sharex=True)
for row,q in enumerate((0.1,0.2)):
    lookup={r['arm']:r for r in rows if r['dataset']=='cse2018' and r['q']==q and r['prevalence']==0.01}
    x=np.arange(len(order))
    over=[100*lookup[o]['draws_over_q'] for o in order]
    fdr=[lookup[o]['fdr']['mean'] for o in order]; fdrerr=[lookup[o]['fdr']['ci95'] for o in order]
    power=[lookup[o]['power']['mean'] for o in order]; powerr=[lookup[o]['power']['ci95'] for o in order]
    a,b,c=axes[row]
    a.bar(x,over,color=colors,edgecolor='black',linewidth=.3)
    for xi,v in zip(x,over):
        a.text(xi,v+1.5,f'{v:.0f}%',ha='center',va='bottom',fontsize=7.5,
               fontweight='bold' if v==0 else 'normal')
    a.set_ylim(0,45); a.set_ylabel('Draws above target (%)')
    a.set_title(f'Calibration draws that exceed $q$ = {q:.2f}')
    b.bar(x,fdr,yerr=fdrerr,capsize=3,color=colors,edgecolor='black',linewidth=.3)
    b.axhline(q,color='#b2182b',ls='--',lw=1); b.set_ylim(0,max(.18,1.6*q))
    b.set_ylabel('Stream FDR'); b.set_title(f'Realised FDR, $q$ = {q:.2f}')
    c.bar(x,power,yerr=powerr,capsize=3,color=colors,edgecolor='black',linewidth=.3)
    c.set_ylim(0,1.12); c.set_ylabel('Power'); c.set_title(f'Detection power, $q$ = {q:.2f}')
    for ax_ in (a,b,c): ax_.grid(axis='y',alpha=.2)
for ax_ in axes[1]: ax_.set_xticks(np.arange(len(order)),labels,rotation=35,ha='right')
fig.suptitle('RQ2: the marginal rules sit under the target on average and still exceed it on 20-36% of draws',y=.995,fontsize=11,fontweight='bold')
fig.text(.5,.955,'CSE2018, unknown-attack prevalence = 1%, n = 12,000, 25 calibration draws; bars show mean ± 95% CI over seeds',ha='center',va='top',fontsize=8)
save(fig,'fig_rq1_rq2_keepability',rect=(0,0,1,.93))

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
fig.legend(handles=handles,loc='lower center',ncol=3,frameon=False,bbox_to_anchor=(.5,0.0),columnspacing=1.2)
fig.suptitle('RQ1: power is sensitive to unknown-attack prevalence',y=.995,fontsize=11,fontweight='bold')
fig.text(.5,.962,'Points show seed means; whiskers show 95% seed intervals; shaded band shows the range across eight detector scores',ha='center',va='top',fontsize=7.7,color='#444444')
save(fig,'fig_rq1_prevalence_barrier',rect=(0,.05,1,.95))

# Figure RQ1: the requirement predicts where power can exist.  One point per
# operating cell over all ten datasets; x is the calibration set measured in
# units of what the conditional rule demands, so the barrier sits at 1.
pred=D['prediction_table']['records']; ext=D['rq1_extension']['records']
fig,ax=plt.subplots(figsize=(7.4,3.6))
ax.axvspan(1,60,color='#0072B2',alpha=.06,zorder=0)
ax.axvline(1,color='#b2182b',ls='--',lw=1.1,zorder=2)
groups={'certified, primary datasets':([],[],'o','#d55e00',34),
        'certified, six unseen datasets':([],[],'s','#0072B2',26),
        'below the requirement':([],[],'v','#7A7A7A',22),
        'audit refuses':([],[],'x','#b2182b',30)}
for r in pred:
    ratio=12000/r['required_calibration']
    key=('audit refuses' if not r['exchangeable_ok'] else
         'certified, primary datasets' if ratio>=1 else 'below the requirement')
    groups[key][0].append(ratio); groups[key][1].append(r['power'])
for r in ext:
    ratio=r['calibration_size']/r['required_calibration']
    key='certified, six unseen datasets' if r['state']=='certified' else 'below the requirement'
    groups[key][0].append(ratio); groups[key][1].append(r['pact_power'])
for label,(xs,ys,marker,color,size) in groups.items():
    ax.scatter(xs,ys,marker=marker,s=size,facecolor='none' if marker=='v' else color,
               edgecolor=color,linewidth=.9,label=f'{label} ({len(xs)})',zorder=3)
ax.set_xscale('log'); ax.set_xlim(.08,60); ax.set_ylim(-.04,1.04)
ax.set_xlabel(r'calibration set as a multiple of the requirement, $n\,/\,n_{\mathrm{cond}}$')
ax.set_ylabel('Realised power')
ax.axhline(.1,color='#7A7A7A',ls=':',lw=.8)
ax.text(.085,.13,'usable power',fontsize=7.5,color='#4D4D4D')
ax.text(1.15,.93,'certificate supported',fontsize=8,color='#b2182b')
ax.legend(frameon=False,loc='upper left',bbox_to_anchor=(.02,.88),fontsize=7.5)
ax.grid(alpha=.2)
fig.suptitle('RQ1: among cells the audit accepts, usable power appears only above the requirement',y=1.0,fontsize=11,fontweight='bold')
fig.text(.5,.955,'40 operating cells over ten datasets; six of the ten took no part in the design',ha='center',va='top',fontsize=8)
save(fig,'fig_rq1_requirement',rect=(0,0,1,.93))

# Figure RQ3: score ceiling ties and tail-lift TPR@1e-3
T=D['rq3_tail']['datasets']; ds=['cicids2017','ciciomt2024','cse2018','toniot']; names=['CICIDS2017','CICIoMT2024','CSE2018','ToN-IoT']
fig,ax=plt.subplots(1,2,figsize=(8,3.3))
x=np.arange(4); w=.36
floor_ties=[T[d]['floored_ties_at_max']['mean'] for d in ds]; tail_ties=[T[d]['tail_lifted_ties_at_max']['mean'] for d in ds]
ax[0].bar(x-w/2,floor_ties,w,label='Floored',color='#999999'); ax[0].bar(x+w/2,tail_ties,w,label='Tail-lifted',color='#0072B2'); ax[0].set_yscale('symlog',linthresh=1); ax[0].set_ylabel('Flows tied at score maximum'); ax[0].set_title('Ceiling ties'); ax[0].legend(frameon=False)
floor=[T[d]['floored_tpr@0.001']['mean'] for d in ds]; tail=[T[d]['tail_lifted_tpr@0.001']['mean'] for d in ds]
ax[1].bar(x-w/2,floor,w,label='Floored',color='#999999'); ax[1].bar(x+w/2,tail,w,label='Tail-lifted',color='#0072B2'); ax[1].set_ylim(0,1.05); ax[1].set_ylabel('TPR at FAR = 10⁻³'); ax[1].set_title('No reliable power gain');
for a in ax: a.set_xticks(x,names,rotation=25,ha='right'); a.grid(axis='y',alpha=.2)
fig.suptitle('RQ3: tail extension removes ties but does not establish a power improvement',y=1.02)
save(fig,'fig_rq3_tail_lift')

# Figure RQ3: supporting panel mean AUROC and mean rank
overall=D['rq3_panel']['overall']; methods_order=['hedl','usfad','ais_nids','renoir_dml','ori','closr','docpp','efc']; lab={'hedl':'PCF','usfad':'usfAD','ais_nids':'AIS-NIDS','renoir_dml':'RENOIR-DML','ori':'ORI','closr':'CLOSR','docpp':'DOC++','efc':'EFC'}
means=[overall[m]['mean'] for m in methods_order]; ci=[overall[m].get('ci95',0) for m in methods_order]
# (a) ranking quality; (b) ranking quality against certified power, per dataset.
fig=plt.figure(figsize=(9.2,5.6)); gs=fig.add_gridspec(2,4,height_ratios=[1,1.05],hspace=.55,wspace=.12)
ax=fig.add_subplot(gs[0,:]); x=np.arange(len(methods_order)); ax.bar(x,means,yerr=ci,capsize=3,color=['#d55e00']+['#999999']*7,edgecolor='black',linewidth=.3); ax.set_xticks(x,[lab[m] for m in methods_order],rotation=0); ax.set_ylim(0,1.05); ax.set_ylabel('Unknown AUROC'); ax.set_title('(a) Detector panel: 11 rotations, five seeds',loc='left'); ax.grid(axis='y',alpha=.2)
short={**lab,'renoir_dml':'RENOIR'}
first=None
for col,(dataset,title) in enumerate(datasets):
    a=fig.add_subplot(gs[1,col],sharey=first) if first else fig.add_subplot(gs[1,col]); first=first or a
    for r in cells:
        if r['dataset']!=dataset or r['prevalence']!=0.01: continue
        m,au,pw=r['method'],r['auroc']['mean'],r['training_conditional']['mean']
        a.scatter(au,pw,s=34 if m=='hedl' else 20,color='#d55e00' if m=='hedl' else '#666666',zorder=3,edgecolor='black',linewidth=.3)
        if pw>0.05 or m=='hedl': a.annotate(short[m],(au,pw),textcoords='offset points',xytext=(-4,5),fontsize=6.5,ha='right')
    a.axvline(0.9,color='#999999',ls=':',lw=.8); a.set_xlim(0,1.03); a.set_ylim(-.04,1.04); a.grid(alpha=.2)
    a.set_title(title,loc='left',fontsize=8.5,fontweight='bold'); a.set_xlabel('Unknown AUROC')
    if dataset=='ciciomt2024': a.text(.05,.55,'audit refuses',transform=a.transAxes,fontsize=7,color='#b2182b')
    if col: plt.setp(a.get_yticklabels(),visible=False)
    else: a.set_ylabel('Certified power, $\\pi$ = 0.01')
fig.text(.1,.47,'(b) AUROC against certified power at $\\pi$ = 0.01, primary rotation',fontsize=9.5)
fig.savefig(FIG/'fig_rq3_detector_panel.png',bbox_inches='tight'); fig.savefig(FIG/'fig_rq3_detector_panel.pdf',bbox_inches='tight'); plt.close(fig)

# Figure RQ4: temporal audit and alerting
A=D['temporal']['audit']; L=D['temporal']['alerting']
labels=['CSE random','CSE temporal','ToN-IoT random','ToN-IoT temporal']; keys=['cse2018::random (Z1)','cse2018::temporal (T2)','toniot::random (Z1)','toniot::temporal (T2)']; viol=[A[k]['violation']['mean'] for k in keys]; bound=[A[k]['bound'] for k in keys]
fdr_keys=['cse2018::marginal BH','cse2018::PACT conditional L=100 (shipped)']; fdr_random=[L[k]['Z1']['fdr'] for k in fdr_keys]; fdr_temp=[L[k]['T2']['fdr'] for k in fdr_keys]
fig,ax=plt.subplots(1,2,figsize=(7.6,3.0)); x=np.arange(4); ax[0].bar(x,viol,color=['#4daf4a','#d73027','#4daf4a','#d73027']); ax[0].errorbar(x,viol,yerr=[A[k]['violation']['ci95'] for k in keys],fmt='none',ecolor='black',capsize=3); ax[0].scatter(x,bound,marker='_',s=400,color='black',zorder=4,label='DKW bound'); ax[0].set_xticks(x,labels,rotation=20,ha='right'); ax[0].set_ylabel('Audit violation'); ax[0].set_title('(a) Exchangeability audit'); ax[0].legend(frameon=False)
x2=np.arange(2); width=.35; ax[1].bar(x2-width/2,fdr_random,width,label='Random split',color='#4daf4a'); ax[1].bar(x2+width/2,fdr_temp,width,label='Temporal split',color='#d73027'); ax[1].axhline(.1,color='black',ls='--',lw=1,label='q = 0.10'); ax[1].set_xticks(x2,['Bates BH','PACT L=100']); ax[1].set_ylabel('Stream FDR'); ax[1].set_title('(b) CSE2018 alerting under shift'); ax[1].set_ylim(0,.95); ax[1].legend(frameon=False,loc='upper center',ncol=3,fontsize=7)
for a in ax: a.grid(axis='y',alpha=.2)
fig.suptitle('RQ4: the audit withdraws a certificate under temporal shift',y=1.02,fontsize=11,fontweight='bold'); fig.text(.5,.965,'Red: time-ordered split, all six captures refused; horizontal marks: audit threshold',ha='center',va='top',fontsize=8); save(fig,'fig_rq4_temporal_shift')

# Figure RQ4: the gate holds its nominal size, so the refusals it adds on real
# captures are a property of the benchmarks rather than of the test.
N=D['rq4_audit_null']
fig,ax=plt.subplots(1,2,figsize=(7.8,3.0))
bars=[('exchangeable\nnull, closed form','dkw::calibration'),
      ('exchangeable\nnull, permutation','permutation::calibration'),
      ('held-out known\ntraffic, closed form','dkw::test'),
      ('held-out known\ntraffic, permutation','permutation::test')]
vals=[100*N[k]['fire_rate'] for _,k in bars]
ax[0].bar(np.arange(4),vals,color=['#0072B2','#176b87','#d55e00','#b2182b'],edgecolor='black',linewidth=.3)
for i,v in enumerate(vals): ax[0].text(i,v+0.8,f'{v:.1f}%',ha='center',fontsize=7.5)
ax[0].axhline(5,color='#b2182b',ls='--',lw=1,label=r'nominal $\alpha$ = 5%')
ax[0].set_xticks(np.arange(4),[b for b,_ in bars],fontsize=7)
ax[0].set_ylabel('Gate fires (%)'); ax[0].set_ylim(0,34); ax[0].legend(frameon=False)
ax[0].set_title('(a) Size of the audit')
names=[('cse2018','CSE2018'),('cicids2017','CICIDS2017'),('toniot','ToN-IoT'),('ciciomt2024','CICIoMT2024')]
per=N['per_dataset']
x=np.arange(4); w=.38
ax[1].bar(x-w/2,[100*per[k]['calibration'] for k,_ in names],w,label='exchangeable null',color='#0072B2')
ax[1].bar(x+w/2,[100*per[k]['test'] for k,_ in names],w,label='held-out known traffic',color='#d55e00')
ax[1].axhline(5,color='#b2182b',ls='--',lw=1)
ax[1].set_xticks(x,[n for _,n in names],rotation=20,ha='right')
ax[1].set_ylabel('Gate fires (%)'); ax[1].legend(frameon=False)
ax[1].set_title('(b) Where the refusals come from')
for a_ in ax: a_.grid(axis='y',alpha=.2)
fig.suptitle('RQ4: the audit is calibrated; the public captures are not exchangeable',y=1.02,fontsize=11,fontweight='bold')
save(fig,'fig_rq4_audit_size')

# Figure ablations
M=D['method_components']; labels=['Encoder removed','KNN removed','Curvature 0.5','Evidential term']
vals=[min(r['difference'] for r in M['encoder']['records']), -M['knn']['difference'], M['curvature']['difference'], M['evidential_pooled']['difference']]
fig,ax=plt.subplots(figsize=(6.5,3.1)); x=np.arange(4); ax.bar(x,vals,color=['#d73027','#d55e00','#999999','#999999']); ax.axhline(0,color='black',lw=.8); ax.set_xticks(x,labels,rotation=25,ha='right'); ax.set_ylabel('Change in unknown AUROC'); ax.set_title('Ablations: only the encoder has a material effect'); ax.grid(axis='y',alpha=.2); save(fig,'fig_ablation_components')

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
