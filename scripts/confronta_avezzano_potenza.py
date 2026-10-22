"""Confronto riproducibile fra le raccolte di Avezzano e Potenza, solo kit Roma."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from reportlab.pdfgen import canvas
from hepscape.workbook import read_workbook
from hepscape.schema import OPTIONS
from hepscape.words import grouped_tokens
from hepscape.cover import draw_cover
from hepscape.sample_summary import draw_sample_summary, sample_counts

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/confronto-avezzano-potenza/kit-roma'
SOURCES = ['data/ern2026/questionari.xlsx', 'data/LIC2026/questionari.xlsx']
CITIES = ['Avezzano', 'Potenza']
COLORS = ['#234A8C', '#7BBA48']
OUTCOMES = [(1,'Gradimento: tantissimo'),(3,'Apprendimento: sì, molto'),(4,'Più curiosità'),(5,'Più interesse'),(6,'Facilità: sì, molto')]

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    groups = [[r for r in read_workbook(ROOT / src) if r[12].casefold()==city.casefold() and r[13].casefold()=='roma'] for src,city in zip(SOURCES,CITIES)]
    assert all(groups)
    ids=[r[0] for rs in groups for r in rs]
    assert len(ids)==len(set(ids)), 'ID duplicati fra le raccolte'
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':'#18304F','axes.labelcolor':'#18304F','axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    figures=[]; table=[]; summary=[]
    def save(fig,name,title,subtitle,foot='999 esclusi per domanda; percentuali sulle risposte valide. Confronto descrittivo, non causale.'):
        fig.suptitle(title,x=.04,y=.97,ha='left',fontsize=23,fontweight='bold')
        fig.text(.04,.92,subtitle,fontsize=11)
        fig.text(.04,.035,foot,fontsize=9)
        fig.text(.04,.014,'Kit Roma | Avezzano: ERN2026 | Potenza: Lucania is comics',fontsize=9)
        path=OUT/(name+'.png');fig.savefig(path,dpi=160);fig.savefig(OUT/(name+'.svg'));plt.close(fig);figures.append(path)
    def counts(rs,q,code=0):
        vals=[r[q] for r in rs if r[q]!=999]
        return vals.count(code),len(vals)
    def paired(ax,labels,series):
        for j,(city,values) in enumerate(zip(CITIES,series)):
            for k,(x,n) in enumerate(values):
                y=k+(j-.5)*.34
                if n:
                    pc=100*x/n;ax.barh(y,pc,height=.30,color=COLORS[j])
                    ax.text(pc+1,y,f'{pc:.1f}% ({x}/{n})',va='center',fontsize=9)
                else: ax.text(1,y,'n=0',va='center',fontsize=9,color=COLORS[j])
        ax.set_yticks(range(len(labels)),labels);ax.invert_yaxis();ax.set_xlim(0,138);ax.set_xticks([0,25,50,75,100]);ax.set_xlabel('% delle risposte valide')
    def legend(fig,y=.07):
        fig.legend([plt.Rectangle((0,0),1,1,color=c) for c in COLORS],CITIES,loc='lower center',bbox_to_anchor=(.5,y),ncol=2,frameon=False)
    fig,ax=plt.subplots(figsize=(16,10))
    series=[[counts(rs,q) for q,_ in OUTCOMES] for rs in groups]
    paired(ax,[t for _,t in OUTCOMES],series);legend(fig)
    fig.subplots_adjust(left=.26,right=.97,top=.86,bottom=.18)
    for k,(q,title) in enumerate(OUTCOMES):
        a,na=series[0][k];b,nb=series[1][k]
        summary.append(dict(domanda=f'Q{q}',indicatore=title,Avezzano=100*a/na,Potenza=100*b/nb,differenza_punti_Potenza_meno_Avezzano=100*b/nb-100*a/na))
    save(fig,'01_esiti','Stesso kit, due raccolte: gli esiti principali',f'Avezzano: {len(groups[0])} schede (109 cartacee + 49 online) | Potenza: {len(groups[1])} schede fotografiche')
    for page,qs in enumerate([[1,3,4,5,6],[10,9,7,8,11]],2):
        fig,axs=plt.subplots(2,3,figsize=(20,12))
        for ax,q in zip(axs.flat,qs):
            labels=OPTIONS[f'Q{q}']
            short={'Mi è piaciuta tantissimo':'Tantissimo','Non mi è piaciuta molto':'Non molto','Curioso/a come prima':'Come prima','Interessato/a come prima':'Come prima','Preferisco non rispondere':'Non risponde'}
            series=[[counts(rs,q,k) for k in range(len(labels))] for rs in groups]
            paired(ax,[short.get(v,v) for v in labels],series)
            title=dict(OUTCOMES).get(q,{7:'Occasioni',8:'Già stato/a nel luogo',9:'Genere',10:'Età',11:'Residente in città'}.get(q,''))
            ax.set_title(f'Q{q} - '+title.split(':')[0],loc='left',fontweight='bold')
            ax.tick_params(axis='y',labelsize=9)
            for city,rs,vals in zip(CITIES,groups,series):
                for label,(x,n) in zip(labels,vals):table.append([f'Q{q}',city,label,x,n,len(rs)-n,100*x/n if n else None])
        axs.flat[-1].set_visible(False);legend(fig,.06)
        fig.subplots_adjust(left=.1,right=.98,top=.84,bottom=.17,hspace=.5,wspace=.65)
        save(fig,f'0{page}_distribuzioni','Tutte le risposte' if page==2 else 'Chi ha partecipato e in quale contesto','Le etichette riportano percentuale e conteggio/risposte valide; 999 esclusi.')
    fig,axs=plt.subplots(2,2,figsize=(18,13));age_table=[]
    for ax,(q,title) in zip(axs.flat,OUTCOMES[:4]):
        series=[]
        for city,rs in zip(CITIES,groups):
            vals=[]
            for age in range(7):
                x,n=counts([r for r in rs if r[10]==age],q);vals.append((x,n))
                age_table.append([f'Q{q}',city,OPTIONS['Q10'][age],x,n,100*x/n if n else None])
            series.append(vals)
        paired(ax,OPTIONS['Q10'][:7],series);ax.set_title(title,loc='left',fontweight='bold')
    legend(fig,.06);fig.subplots_adjust(left=.11,right=.98,top=.85,bottom=.17,hspace=.42,wspace=.35)
    save(fig,'04_eta','Confronto nelle stesse fasce di età','Esiti favorevoli Q1, Q3, Q4 e Q5: percentuale e conteggio/validi in ciascuna fascia.','Molti sottogruppi hanno meno di 10 risposte: leggere i conteggi. Nessuna standardizzazione o conclusione causale.')
    texts=[[r[2] for r in rs if r[2]!=999] for rs in groups]
    counters=[Counter(t for text in ts for t in set(grouped_tokens(text))) for ts in texts]
    top=[w for w,_ in sum(counters,Counter()).most_common(12)]
    fig,ax=plt.subplots(figsize=(16,11));paired(ax,top,[[(c[w],len(ts)) for w in top] for c,ts in zip(counters,texts)])
    legend(fig);fig.subplots_adjust(left=.24,right=.97,top=.86,bottom=.17)
    save(fig,'05_parole','Le parole dell’esperienza','12 forme accorpate più frequenti nel totale. Una parola conta al massimo una volta per scheda.','Denominatore: risposte Q2 non vuote. Accorpamenti del repository; frequenze di parole, non classificazione del sentimento.')
    for name,header,rows in [('risposte',['domanda','citta','risposta','conteggio','validi','mancanti','percentuale'],table),('per_eta',['domanda','citta','eta','conteggio','validi','percentuale'],age_table)]:
        with (OUT/(name+'.csv')).open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f);w.writerow(header);w.writerows(rows)
    manifest={'kit':'Roma','groups':[{ 'city':city,'n':len(rs),'source':src,'sha256':hashlib.sha256((ROOT/src).read_bytes()).hexdigest(),'ids':[r[0] for r in rs]} for city,rs,src in zip(CITIES,groups,SOURCES)],'summary':summary}
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    pdf=OUT/'HEPscape_Avezzano_Potenza_kit_Roma.pdf'
    c=canvas.Canvas(str(pdf),pagesize=(1008,756))
    draw_cover(c,'Roma','Avezzano e Potenza','ERN2026 / Lucania is comics',sum(map(len,groups)),len(figures)+3);c.showPage()
    draw_sample_summary(c,sample_counts(groups,['ERN2026','Lucania is comics']),len(figures)+3);c.showPage()
    for i,path in enumerate(figures,3):
        c.drawImage(str(path),0,25,width=1008,height=710,preserveAspectRatio=True,anchor='c')
        c.setFont('Helvetica',9);c.drawRightString(980,12,f'{i} / {len(figures)+3}');c.showPage()
    c.setFillColorRGB(.094,.188,.310);c.setFont('Helvetica-Bold',28);c.drawString(55,680,'Metodo e limiti del confronto')
    lines=[
        'Selezione: solo kit Roma; Avezzano dal workbook ERN2026, Potenza dal workbook LIC2026.',
        f'Avezzano: {len(groups[0])} schede (109 cartacee e 49 online). Potenza: {len(groups[1])} fotografie distinte.',
        'Gli ID sono univoci. I numeri manoscritti duplicati a Potenza non sono ID duplicati.',
        'I codici 999 sono esclusi dal denominatore della singola domanda; gli zeri sono risposte valide.',
        'Q2: percentuali sulle risposte testuali; una stessa parola conta una volta per scheda.',
        'Q3 misura apprendimento dichiarato, senza prova oggettiva prima/dopo.',
        'Q4 e Q5 misurano aumenti dichiarati; Q6 riguarda la facilita di partecipazione.',
        'Q7 misura occasioni disponibili; Q8 riguarda precedenti attivita didattiche nello stesso luogo.',
        'I due gruppi appartengono a eventi diversi e hanno eta, contesto e modalita di raccolta diversi.',
        'Le differenze osservate non dimostrano un effetto della citta o una diversa efficacia del kit.',
        'La lettura per eta e descrittiva: gruppi piccoli, nessun aggiustamento per altri fattori.',
        'Campioni di rispondenti, non campioni casuali; nessun test di significativita applicato.',
        '',
        'Fonti nel repository:',*SOURCES,
        'Tabelle complete: risposte.csv e per_eta.csv nella cartella di questo report.',
        'manifest.json conserva selezione degli ID e impronte SHA256 dei workbook di origine.',
    ]
    c.setFont('Helvetica',13)
    for i,line in enumerate(lines):c.drawString(55,625-i*27,line)
    c.setFont('Helvetica',9);c.drawRightString(980,12,f'{len(figures)+3} / {len(figures)+3}');c.showPage();c.save()
    print(json.dumps(summary,ensure_ascii=False,indent=2));print(pdf)

if __name__=='__main__':main()
