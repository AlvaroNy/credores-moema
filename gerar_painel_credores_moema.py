# -*- coding: utf-8 -*-
"""
Gera um painel HTML self-contained dos CREDORES da Prefeitura de Moema/MG
(despesas por credor) a partir de credores_moema_<ano>.json.

Saída: index.html (pronto para GitHub Pages).
"""
import json, os, sys, glob

try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

HERE = os.path.dirname(os.path.abspath(__file__))
PLOTLY = os.path.join(HERE, "plotly.min.js")
SAIDA = os.path.join(HERE, "index.html")

AZUL="#1A73E8"; VERDE="#34A853"; LARANJA="#EE4D2D"; ROXO="#7C4DFF"; CINZA="#607D8B"; TEXTO="#1f2933"

def categoria(nome):
    n=(nome or "").upper()
    enc=["INSS","FGTS","PASEP","IRRF","RPPS","I.N.S.S","IMPOSTO","TRIBUT","DARF","GPS ",
         "SIMPLES NACIONAL","RECEITA FEDERAL","CONTRIBUI","FGTS/","IPVA","ISS "]
    pub=["MUNICIPIO DE","MUNICÍPIO DE","CAMARA MUNICIPAL","CÂMARA MUNICIPAL","SAAE",
         "SERVICO AUTONOMO DE AGUA","SERVIÇO AUTONOMO","FUNDACAO","FUNDAÇÃO","PREFEITURA",
         "ESTADO DE","FUNDO MUNICIPAL","FUNDO DE","INSTITUTO DE PREVIDENCIA","IPREM",
         "CONSORCIO","CONSÓRCIO","SECRETARIA DE ESTADO","TESOURO"]
    if any(k in n for k in enc): return "Encargos/Tributos"
    if any(k in n for k in pub): return "Ente público/Repasse"
    return "Fornecedor"

CORES={"Fornecedor":AZUL,"Ente público/Repasse":ROXO,"Encargos/Tributos":LARANJA}
ORDEM=["Fornecedor","Ente público/Repasse","Encargos/Tributos"]

def fmt(v): return "R$ "+f"{v:,.2f}".replace(",","X").replace(".",",").replace("X",".")

def main():
    arqs=sorted(glob.glob(os.path.join(HERE,"credores_moema_*.json")), reverse=True)
    if not arqs:
        print("Nenhum credores_moema_*.json encontrado. Rode extrair_credores_moema.py antes."); return
    d=json.load(open(arqs[0],encoding="utf-8"))
    ano=d["ano"]; entidade=d["entidade"]; periodo=d["periodo"]
    regs=[]
    for r in d["registros"]:
        cat=categoria(r["nome"])
        pago=float(r.get("pago",0) or 0); liq=float(r.get("liquidado",0) or 0)
        emp=float(r.get("empenhado",0) or 0)
        ref=max(pago,liq)   # referência de gasto
        regs.append([r["nome"].title() if r["nome"].isupper() else r["nome"],
                     r["cnpj"], ORDEM.index(cat), round(emp,2), round(liq,2), round(pago,2), round(ref,2)])
    regs.sort(key=lambda x:-x[6])

    tot_emp=sum(r[3] for r in regs); tot_liq=sum(r[4] for r in regs); tot_pago=sum(r[5] for r in regs)
    tot_falta=max(tot_emp-tot_pago, 0)   # empenhado (comprometido) que ainda nao foi pago
    n=len(regs)
    porcat={}
    for r in regs:
        c=ORDEM[r[2]]; a=porcat.setdefault(c,{"n":0,"pago":0.0,"liq":0.0,"ref":0.0})
        a["n"]+=1; a["pago"]+=r[5]; a["liq"]+=r[4]; a["ref"]+=r[6]
    cats=[c for c in ORDEM if c in porcat]

    # top 15 por ref
    top=regs[:15]
    top_nomes=[r[0][:38] for r in top][::-1]
    top_vals=[r[6] for r in top][::-1]
    top_cols=[CORES[ORDEM[r[2]]] for r in top][::-1]

    donut_labels=cats
    donut_vals=[round(porcat[c]["ref"],2) for c in cats]
    donut_cols=[CORES[c] for c in cats]

    plotly=open(PLOTLY,encoding="utf-8").read()
    J=lambda o: json.dumps(o, ensure_ascii=False)

    # concentração top 10
    top10=sum(r[6] for r in regs[:10]); share10=100*top10/ (sum(r[6] for r in regs) or 1)

    page=f"""<!DOCTYPE html><html lang="pt-BR"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Credores · Prefeitura de Moema — {ano}</title>
<script>{plotly}</script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',system-ui,Arial,sans-serif;background:#f4f6f9;color:{TEXTO};padding:24px;max-width:1280px;margin:auto}}
h1{{font-size:26px;font-weight:800}} .sub{{color:#607d8b;margin:4px 0 18px;font-size:14px}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin-bottom:22px}}
.kpi{{background:#fff;border-radius:14px;padding:16px 18px;box-shadow:0 2px 10px rgba(0,0,0,.05);border-left:5px solid {AZUL}}}
.kpi .v{{font-size:22px;font-weight:800;margin-top:4px}} .kpi .l{{font-size:12px;color:#607d8b;text-transform:uppercase;letter-spacing:.4px}}
.kpi.green{{border-color:{VERDE}}} .kpi.purple{{border-color:{ROXO}}} .kpi.gray{{border-color:{CINZA}}} .kpi.orange{{border-color:{LARANJA}}}
.grid2{{display:grid;grid-template-columns:1.4fr 1fr;gap:18px;margin-bottom:22px}}
@media(max-width:900px){{.grid2{{grid-template-columns:1fr}}}}
.card{{background:#fff;border-radius:14px;padding:16px 18px;box-shadow:0 2px 10px rgba(0,0,0,.05)}}
.card h3{{font-size:15px;margin-bottom:8px}}
.toolbar{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:12px}}
#busca{{flex:1;min-width:220px;padding:10px 14px;border:1px solid #d0d7de;border-radius:10px;font-size:14px}}
.chip{{cursor:pointer;border:1px solid #d0d7de;background:#fff;border-radius:20px;padding:6px 13px;font-size:13px;font-weight:600;user-select:none}}
.chip.active{{color:#fff;border-color:transparent}}
table{{width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.05)}}
th,td{{padding:9px 12px;text-align:left;font-size:13.5px;border-bottom:1px solid #eef1f4}}
th{{background:#f0f3f7;cursor:pointer;font-size:12px;text-transform:uppercase;letter-spacing:.3px;white-space:nowrap}}
td.num{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
.tag{{display:inline-block;padding:2px 9px;border-radius:20px;font-size:11px;font-weight:700;color:#fff}}
tr:hover td{{background:#fafbfc}}
.count{{color:#607d8b;font-size:13px;margin:8px 2px}}
.foot{{color:#90a4ae;font-size:12px;margin-top:18px;text-align:center;line-height:1.6}}
</style></head><body>

<h1>Credores · {entidade.title()} — {ano}</h1>
<div class="sub">Despesas por credor · período {periodo} · Portal da Transparência de Moema/MG · {n} credores</div>

<div class="kpis">
  <div class="kpi gray"><div class="l">Credores</div><div class="v">{n}</div></div>
  <div class="kpi"><div class="l">Empenhado</div><div class="v">{fmt(tot_emp)}</div></div>
  <div class="kpi green"><div class="l">Liquidado</div><div class="v">{fmt(tot_liq)}</div></div>
  <div class="kpi green"><div class="l">Pago</div><div class="v">{fmt(tot_pago)}</div></div>
  <div class="kpi orange"><div class="l">Falta pagar</div><div class="v">{fmt(tot_falta)}</div></div>
  <div class="kpi purple"><div class="l">Top 10 concentram</div><div class="v">{share10:.0f}%</div></div>
</div>

<div class="grid2">
  <div class="card"><h3>Top 15 maiores credores</h3><div id="top" style="height:430px"></div></div>
  <div class="card"><h3>Gasto por tipo de credor</h3><div id="donut" style="height:430px"></div></div>
</div>

<div class="card" style="margin-bottom:22px">
  <div class="toolbar">
    <input id="busca" placeholder="🔎 Buscar por nome ou CNPJ/CPF...">
    <span id="chips"></span>
  </div>
  <div class="count" id="contador"></div>
  <div style="overflow-x:auto">
  <table id="tab"><thead><tr>
    <th data-k="0">Credor</th><th data-k="1">CNPJ/CPF</th><th data-k="2">Tipo</th>
    <th data-k="3" class="num">Empenhado</th><th data-k="4" class="num">Liquidado</th><th data-k="5" class="num">Pago</th>
  </tr></thead><tbody id="corpo"></tbody></table>
  </div>
</div>

<div class="foot">
  Dados extraídos do Portal da Transparência de Moema/MG · Despesas › Credores.<br>
  "Empenhado" = comprometido · "Liquidado" = despesa efetivada · "Pago" = efetivamente pago · "Falta pagar" = Empenhado − Pago (o que já foi comprometido mas ainda não saiu do caixa). Tipo é uma classificação automática por heurística no nome (repasses a entes públicos e encargos separados dos fornecedores).
</div>

<script>
const DADOS={J(regs)};   // [nome,cnpj,catIdx,emp,liq,pago,ref]
const CATS={J(ORDEM)};
const CORES={J(CORES)};
const fmt=v=>"R$ "+v.toLocaleString('pt-BR',{{minimumFractionDigits:2,maximumFractionDigits:2}});
const fmtk=v=>v>=1e6?("R$ "+(v/1e6).toFixed(2)+" mi"):(v>=1e3?("R$ "+(v/1e3).toFixed(0)+" mil"):("R$ "+v.toFixed(0)));

Plotly.newPlot('top',[{{type:'bar',orientation:'h',y:{J(top_nomes)},x:{J(top_vals)},
  marker:{{color:{J(top_cols)}}},text:{J(top_vals)}.map(fmtk),textposition:'auto'}}],
  {{margin:{{t:10,b:30,l:180,r:20}}}},{{displayModeBar:false,responsive:true}});

Plotly.newPlot('donut',[{{type:'pie',hole:.55,labels:{J(donut_labels)},values:{J(donut_vals)},
  marker:{{colors:{J(donut_cols)}}},textinfo:'label+percent',textposition:'inside',sort:false}}],
  {{margin:{{t:10,b:10,l:10,r:10}},showlegend:false}},{{displayModeBar:false,responsive:true}});

let filtro='TODOS', busca='', sortk=5, sortdir=-1;
function tag(ci){{const c=CATS[ci];return `<span class="tag" style="background:${{CORES[c]}}">${{c}}</span>`;}}
function render(){{
  let rows=DADOS.filter(r=>filtro==='TODOS'||CATS[r[2]]===filtro);
  if(busca){{const q=busca.toLowerCase();rows=rows.filter(r=>r[0].toLowerCase().includes(q)||(r[1]||'').toLowerCase().includes(q));}}
  rows=rows.slice().sort((a,b)=>{{let x=a[sortk],y=b[sortk];if(typeof x==='string'){{x=x.toLowerCase();y=y.toLowerCase();}}return x<y?-sortdir:x>y?sortdir:0;}});
  document.getElementById('corpo').innerHTML=rows.map(r=>`<tr><td>${{r[0]}}</td><td>${{r[1]||''}}</td><td>${{tag(r[2])}}</td><td class="num">${{fmt(r[3])}}</td><td class="num">${{fmt(r[4])}}</td><td class="num"><b>${{fmt(r[5])}}</b></td></tr>`).join('');
  const sp=rows.reduce((s,r)=>s+r[5],0), sl=rows.reduce((s,r)=>s+r[4],0);
  document.getElementById('contador').innerHTML=`<b>${{rows.length}}</b> credor(es) · liquidado ${{fmt(sl)}} · pago ${{fmt(sp)}}`;
}}
const chips=['TODOS'].concat(CATS);
const box=document.getElementById('chips');
chips.forEach(c=>{{const el=document.createElement('span');el.className='chip'+(c==='TODOS'?' active':'');el.textContent=c;
  if(c==='TODOS'){{el.style.background='#1f2933';el.style.color='#fff';el.style.borderColor='transparent';}}
  el.onclick=()=>{{filtro=c;document.querySelectorAll('.chip').forEach(x=>{{x.classList.remove('active');if(x.textContent!=='TODOS'){{x.style.background='#fff';x.style.color='#1f2933';}}}});el.classList.add('active');if(c!=='TODOS'){{el.style.background=CORES[c];el.style.color='#fff';}}render();}};
  box.appendChild(el);}});
document.getElementById('busca').addEventListener('input',e=>{{busca=e.target.value;render();}});
document.querySelectorAll('#tab th').forEach(th=>th.onclick=()=>{{const k=+th.dataset.k;if(sortk===k)sortdir*=-1;else{{sortk=k;sortdir=(k<3)?1:-1;}}render();}});
render();
</script>
</body></html>"""
    open(SAIDA,"w",encoding="utf-8").write(page)
    print(f"OK -> {SAIDA}  ({os.path.getsize(SAIDA)/1048576:.1f} MB · {n} credores · ano {ano})")

if __name__=="__main__":
    main()
