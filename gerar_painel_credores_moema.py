# -*- coding: utf-8 -*-
"""
Gera um painel HTML self-contained dos CREDORES da Prefeitura de Moema/MG
(despesas por credor) a partir de TODOS os credores_moema_<ano>.json presentes.

Adiciona um SELETOR DE ANO no topo (alterna entre os anos disponíveis).
Saída: index.html (pronto para GitHub Pages).
"""
import json, os, sys, glob, unicodedata

def _sa(s):  # strip acentos + upper, para casar nomes
    return ''.join(c for c in unicodedata.normalize('NFD', s or '') if unicodedata.category(c)!='Mn').upper().strip()

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

def parse_regs(d):
    regs=[]
    for r in d["registros"]:
        cat=categoria(r["nome"])
        pago=float(r.get("pago",0) or 0); liq=float(r.get("liquidado",0) or 0); emp=float(r.get("empenhado",0) or 0)
        ref=max(pago,liq); falta=max(emp-pago,0)
        if _sa(r["nome"])=="MUNICIPIO DE MOEMA":
            nome="Município de Moema — Folha de Pagamento"
        else:
            nome=r["nome"].title() if r["nome"].isupper() else r["nome"]
        regs.append([nome, r["cnpj"], ORDEM.index(cat), round(emp,2), round(liq,2), round(pago,2), round(ref,2), round(falta,2)])
    regs.sort(key=lambda x:-x[6])
    return regs

def main():
    arqs=glob.glob(os.path.join(HERE,"credores_moema_*.json"))
    if not arqs:
        print("Nenhum credores_moema_*.json encontrado. Rode extrair_credores_moema.py antes."); return
    REGP={}; META={}
    for a in arqs:
        d=json.load(open(a,encoding="utf-8"))
        ano=str(d["ano"])
        REGP[ano]=parse_regs(d)
        META[ano]={"entidade":d["entidade"].title(),"periodo":d["periodo"]}
    anos=sorted(REGP.keys(), reverse=True)

    plotly=open(PLOTLY,encoding="utf-8").read()
    J=lambda o: json.dumps(o, ensure_ascii=False)

    page=f"""<!DOCTYPE html><html lang="pt-BR"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-WMZMY29YL0"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-WMZMY29YL0');
</script>
<title>Credores · Prefeitura de Moema</title>
<script>{plotly}</script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',system-ui,Arial,sans-serif;background:#f4f6f9;color:{TEXTO};padding:24px;max-width:1280px;margin:auto}}
h1{{font-size:26px;font-weight:800}} .sub{{color:#607d8b;margin:4px 0 14px;font-size:14px}}
.topbar{{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin-bottom:18px}}
.yearsel{{display:flex;align-items:center;gap:8px;background:{AZUL};color:#fff;padding:8px 14px;border-radius:12px;font-weight:700;box-shadow:0 3px 12px rgba(26,115,232,.28)}}
.yearsel select{{font-size:17px;font-weight:800;border:none;border-radius:8px;padding:6px 10px;cursor:pointer;color:{TEXTO}}}
.topbar .switchlink{{margin-left:auto;color:{AZUL};cursor:pointer;text-decoration:underline;font-size:13px}}
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
/* --- telas de boas-vindas --- */
.overlay{{position:fixed;inset:0;background:rgba(15,23,42,.80);display:flex;align-items:center;justify-content:center;z-index:9999;padding:20px}}
.overlay .box{{background:#fff;border-radius:18px;max-width:460px;width:100%;padding:28px 26px;box-shadow:0 20px 60px rgba(0,0,0,.35);text-align:center}}
.overlay h2{{font-size:20px;margin-bottom:12px;color:{TEXTO}}}
.overlay p{{font-size:14.5px;color:#4b5563;line-height:1.6;margin-bottom:22px}}
.ov-btns{{display:flex;flex-direction:column;gap:10px}}
.ov-btn{{border:none;border-radius:12px;padding:14px 18px;font-size:15px;font-weight:700;cursor:pointer;background:{AZUL};color:#fff}}
.ov-btn:hover{{filter:brightness(1.07)}}
.ov-btn.alt{{background:#eef2f7;color:{TEXTO}}}
.ov-btns.dev{{flex-direction:row}}
.ov-btns.dev .ov-btn{{flex:1;display:flex;flex-direction:column;align-items:center;gap:6px;padding:20px 10px}}
.ov-btn .ic{{font-size:30px}}
/* --- mini-cards (celular) --- */
#cardsWrap{{display:none}}
body.modo-mobile #tabWrap{{display:none}}
body.modo-mobile #cardsWrap{{display:block}}
body.modo-mobile #chips{{display:none}}
body.modo-mobile #graficos{{display:none}}
.ccard{{background:#fff;border:1px solid #e6eaef;border-radius:12px;margin-bottom:8px;overflow:hidden}}
.ccard-head{{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:12px 14px;cursor:pointer}}
.ccard-head .nm{{font-weight:700;font-size:14px}}
.ccard-head .cj{{font-size:12px;color:#607d8b;margin-top:2px}}
.ccard-head .chev{{color:#9aa7b4;font-size:16px;transition:transform .15s}}
.ccard.open .chev{{transform:rotate(180deg)}}
.ccard-body{{padding:0 14px 12px;font-size:13.5px}}
.ccard-body .lin{{display:flex;justify-content:space-between;gap:12px;padding:6px 0;border-top:1px solid #f0f3f7}}
.ccard-body .lin .k{{color:#607d8b}}
.ccard-body .lin .val{{font-weight:700;font-variant-numeric:tabular-nums;text-align:right}}
.ccard-body .lin .val.emp{{color:{AZUL}}}
.ccard-body .lin .val.liq{{color:{VERDE}}}
.ccard-body .lin .val.pago{{color:#137333}}
.ccard-body .lin .val.falta{{color:{LARANJA}}}
.ccard-body .lin .val.zero{{color:#9aa7b4}}
</style></head><body>

<div class="overlay" id="ov">
  <div class="box" id="ovStep1">
    <h2>⚠️ Aviso</h2>
    <p>Todos os dados exibidos neste site foram obtidos no <b>Portal da Transparência</b> da Prefeitura Municipal de Moema/MG. É informação pública, reproduzida aqui apenas para facilitar a consulta.</p>
    <div class="ov-btns"><button class="ov-btn" id="btnCiente">Sim, Estou Ciente</button></div>
  </div>
  <div class="box" id="ovStep2" hidden>
    <h2>Como você está acessando?</h2>
    <p>Escolha o dispositivo para ver o site no melhor formato.</p>
    <div class="ov-btns dev">
      <button class="ov-btn alt" id="btnCel"><span class="ic">📱</span>Celular</button>
      <button class="ov-btn" id="btnPc"><span class="ic">💻</span>Computador</button>
    </div>
  </div>
</div>

<h1 id="titulo">Credores · Prefeitura de Moema</h1>
<div class="sub" id="sub"></div>

<div class="topbar">
  <div class="yearsel"><label for="ano">Ano:</label><select id="ano"></select></div>
  <a id="switchLink" class="switchlink"></a>
</div>

<div class="kpis" id="kpis"></div>

<div class="grid2" id="graficos">
  <div class="card"><h3>Top 15 maiores credores</h3><div id="top" style="height:430px"></div></div>
  <div class="card"><h3>Gasto por tipo de credor</h3><div id="donut" style="height:430px"></div></div>
</div>

<div class="card" style="margin-bottom:22px">
  <div class="toolbar">
    <input id="busca" placeholder="🔎 Buscar por nome ou CNPJ/CPF...">
    <span id="chips"></span>
  </div>
  <div class="count" id="contador"></div>
  <div id="tabWrap" style="overflow-x:auto">
  <table id="tab"><thead><tr>
    <th data-k="0">Credor</th><th data-k="1">CNPJ/CPF</th><th data-k="2">Tipo</th>
    <th data-k="3" class="num">Empenhado</th><th data-k="4" class="num">Liquidado</th><th data-k="5" class="num">Pago</th><th data-k="7" class="num">Falta pagar (aprox.)</th>
  </tr></thead><tbody id="corpo"></tbody></table>
  </div>
  <div id="cardsWrap"></div>
</div>

<div class="foot">
  Dados extraídos do Portal da Transparência de Moema/MG · Despesas › Credores.<br>
  "Empenhado" = comprometido · "Liquidado" = despesa efetivada · "Pago" = efetivamente pago · "Falta pagar (aprox.)" = Empenhado − Pago — estimativa, pois o Pago também inclui contas de anos anteriores (restos a pagar), que o portal não separa nesta tela. Tipo é uma classificação automática por heurística no nome (repasses a entes públicos e encargos separados dos fornecedores).
</div>

<script>
const ANOS={J(anos)};
const REGP={J(REGP)};      // ano -> [[nome,cnpj,catIdx,emp,liq,pago,ref,falta], ...]
const META={J(META)};      // ano -> {{entidade,periodo}}
const CATS={J(ORDEM)};
const CORES={J(CORES)};
const fmt=v=>"R$ "+v.toLocaleString('pt-BR',{{minimumFractionDigits:2,maximumFractionDigits:2}});
const fmtk=v=>v>=1e6?("R$ "+(v/1e6).toFixed(2)+" mi"):(v>=1e3?("R$ "+(v/1e3).toFixed(0)+" mil"):("R$ "+v.toFixed(0)));

let ano=ANOS[0], filtro='TODOS', busca='', sortk=5, sortdir=-1;
function tag(ci){{const c=CATS[ci];return `<span class="tag" style="background:${{CORES[c]}}">${{c}}</span>`;}}
function dados(){{return REGP[ano];}}

function renderResumo(){{
  const rows=dados();
  let emp=0,liq=0,pago=0; const porcat={{}};
  rows.forEach(r=>{{emp+=r[3];liq+=r[4];pago+=r[5];const c=CATS[r[2]];(porcat[c]=porcat[c]||{{n:0,ref:0}}).n++;porcat[c].ref+=r[6];}});
  const n=rows.length, falta=Math.max(emp-pago,0);
  const byref=rows.slice().sort((a,b)=>b[6]-a[6]);
  const totref=byref.reduce((s,r)=>s+r[6],0)||1, top10=byref.slice(0,10).reduce((s,r)=>s+r[6],0);
  document.getElementById('titulo').textContent=`Credores · ${{META[ano].entidade}} — ${{ano}}`;
  document.getElementById('sub').textContent=`Despesas por credor · período ${{META[ano].periodo}} · Portal da Transparência de Moema/MG · ${{n}} credores`;
  document.getElementById('kpis').innerHTML=`
    <div class="kpi gray"><div class="l">Credores</div><div class="v">${{n}}</div></div>
    <div class="kpi"><div class="l">Empenhado</div><div class="v">${{fmt(emp)}}</div></div>
    <div class="kpi green"><div class="l">Liquidado</div><div class="v">${{fmt(liq)}}</div></div>
    <div class="kpi green"><div class="l">Pago</div><div class="v">${{fmt(pago)}}</div></div>
    <div class="kpi orange"><div class="l">Falta pagar (aprox.)</div><div class="v">${{fmt(falta)}}</div></div>
    <div class="kpi purple"><div class="l">Top 10 concentram</div><div class="v">${{Math.round(100*top10/totref)}}%</div></div>`;
  const cats=CATS.filter(c=>porcat[c]);
  const t15=byref.slice(0,15);
  Plotly.react('top',[{{type:'bar',orientation:'h',y:t15.map(r=>r[0].slice(0,38)).reverse(),x:t15.map(r=>r[6]).reverse(),
    marker:{{color:t15.map(r=>CORES[CATS[r[2]]]).reverse()}},text:t15.map(r=>fmtk(r[6])).reverse(),textposition:'auto'}}],
    {{margin:{{t:10,b:30,l:180,r:20}}}},{{displayModeBar:false,responsive:true}});
  Plotly.react('donut',[{{type:'pie',hole:.55,labels:cats,values:cats.map(c=>porcat[c].ref),
    marker:{{colors:cats.map(c=>CORES[c])}},textinfo:'label+percent',textposition:'inside',sort:false}}],
    {{margin:{{t:10,b:10,l:10,r:10}},showlegend:false}},{{displayModeBar:false,responsive:true}});
}}

function render(){{
  let rows=dados().filter(r=>filtro==='TODOS'||CATS[r[2]]===filtro);
  if(busca){{const q=busca.toLowerCase();rows=rows.filter(r=>r[0].toLowerCase().includes(q)||(r[1]||'').toLowerCase().includes(q));}}
  rows=rows.slice().sort((a,b)=>{{let x=a[sortk],y=b[sortk];if(typeof x==='string'){{x=x.toLowerCase();y=y.toLowerCase();}}return x<y?-sortdir:x>y?sortdir:0;}});
  document.getElementById('corpo').innerHTML=rows.map(r=>`<tr><td>${{r[0]}}</td><td>${{r[1]||''}}</td><td>${{tag(r[2])}}</td><td class="num">${{fmt(r[3])}}</td><td class="num">${{fmt(r[4])}}</td><td class="num"><b>${{fmt(r[5])}}</b></td><td class="num">${{fmt(r[7])}}</td></tr>`).join('');
  document.getElementById('cardsWrap').innerHTML=rows.map(r=>`<div class="ccard" style="border-left:4px solid ${{CORES[CATS[r[2]]]}}"><div class="ccard-head"><div><div class="nm">${{r[0]}}</div><div class="cj">${{r[1]||'—'}}</div></div><span class="chev">▾</span></div><div class="ccard-body" hidden><div class="lin"><span class="k">Tipo</span><span class="val">${{tag(r[2])}}</span></div><div class="lin"><span class="k">Empenhado</span><span class="val emp">${{fmt(r[3])}}</span></div><div class="lin"><span class="k">Liquidado</span><span class="val liq">${{fmt(r[4])}}</span></div><div class="lin"><span class="k">Pago</span><span class="val pago">${{fmt(r[5])}}</span></div><div class="lin"><span class="k">Falta pagar (aprox.)</span><span class="val ${{r[7]>0?'falta':'zero'}}">${{fmt(r[7])}}</span></div></div></div>`).join('');
  const sp=rows.reduce((s,r)=>s+r[5],0), sl=rows.reduce((s,r)=>s+r[4],0), sf=rows.reduce((s,r)=>s+r[7],0);
  document.getElementById('contador').innerHTML=`<b>${{rows.length}}</b> credor(es) · liquidado ${{fmt(sl)}} · pago ${{fmt(sp)}} · falta pagar ${{fmt(sf)}}`;
}}
function renderAll(){{renderResumo();render();}}

// seletor de ano
const selAno=document.getElementById('ano');
ANOS.forEach(a=>{{const o=document.createElement('option');o.value=a;o.textContent=a;selAno.appendChild(o);}});
selAno.value=ano;
selAno.onchange=()=>{{ano=selAno.value;busca='';document.getElementById('busca').value='';renderAll();}};

// acordeão dos mini-cards (celular)
document.getElementById('cardsWrap').addEventListener('click',e=>{{
  const head=e.target.closest('.ccard-head'); if(!head)return;
  const card=head.parentElement, body=card.querySelector('.ccard-body');
  const open=card.classList.toggle('open'); body.hidden=!open;
}});

// telas de boas-vindas + troca de versão
let modo='desktop';
function aplicaModo(m){{modo=m;document.body.classList.toggle('modo-mobile',m==='mobile');
  document.getElementById('switchLink').textContent=(m==='mobile')?'💻 Ver versão computador':'📱 Ver versão celular';
  filtro='TODOS';
  document.querySelectorAll('.chip').forEach(x=>{{const t=x.textContent==='TODOS';x.classList.toggle('active',t);x.style.background=t?'#1f2933':'#fff';x.style.color=t?'#fff':'#1f2933';x.style.borderColor=t?'transparent':'#d0d7de';}});
  render();}}
document.getElementById('switchLink').onclick=()=>aplicaModo(modo==='mobile'?'desktop':'mobile');
document.getElementById('btnCiente').onclick=()=>{{document.getElementById('ovStep1').hidden=true;document.getElementById('ovStep2').hidden=false;}};
document.getElementById('btnCel').onclick=()=>{{aplicaModo('mobile');document.getElementById('ov').style.display='none';}};
document.getElementById('btnPc').onclick=()=>{{aplicaModo('desktop');document.getElementById('ov').style.display='none';}};

// chips de tipo
const chips=['TODOS'].concat(CATS);
const box=document.getElementById('chips');
chips.forEach(c=>{{const el=document.createElement('span');el.className='chip'+(c==='TODOS'?' active':'');el.textContent=c;
  if(c==='TODOS'){{el.style.background='#1f2933';el.style.color='#fff';el.style.borderColor='transparent';}}
  el.onclick=()=>{{filtro=c;document.querySelectorAll('.chip').forEach(x=>{{x.classList.remove('active');if(x.textContent!=='TODOS'){{x.style.background='#fff';x.style.color='#1f2933';}}}});el.classList.add('active');if(c!=='TODOS'){{el.style.background=CORES[c];el.style.color='#fff';}}render();}};
  box.appendChild(el);}});
document.getElementById('busca').addEventListener('input',e=>{{busca=e.target.value;render();}});
document.querySelectorAll('#tab th').forEach(th=>th.onclick=()=>{{const k=+th.dataset.k;if(sortk===k)sortdir*=-1;else{{sortk=k;sortdir=(k<3)?1:-1;}}render();}});

aplicaModo('desktop');
renderAll();
</script>
</body></html>"""
    open(SAIDA,"w",encoding="utf-8").write(page)
    tot=sum(len(v) for v in REGP.values())
    print(f"OK -> {SAIDA}  ({os.path.getsize(SAIDA)/1048576:.1f} MB · anos {', '.join(anos)} · {tot} registros)")

if __name__=="__main__":
    main()
