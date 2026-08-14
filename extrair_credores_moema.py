# -*- coding: utf-8 -*-
"""
Extrai a lista de CREDORES (despesas por credor) da Prefeitura de Moema/MG
do Portal da Transparência (Cidade360), para um ano inteiro.

Usa Playwright (o relatório só sai numa navegação real, dentro da sessão ASP).
Salva em credores_moema_<ano>.json.

Uso:
    python extrair_credores_moema.py            # ano corrente (2026), Consolidada
    python extrair_credores_moema.py 2025       # outro ano
    python extrair_credores_moema.py 2026 0     # ano + unidade (0=Prefeitura, 1=Camara, 2=SAAE, -1=Consolidada)
"""
import sys, os, json, re, time
from playwright.sync_api import sync_playwright

try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://webapp1-moema.cidade360.cloud/pronimtb/"
URL  = BASE + "index.asp?acao=3&item=10"

ANO = sys.argv[1] if len(sys.argv) > 1 else "2026"
UG  = sys.argv[2] if len(sys.argv) > 2 else "-1"   # -1 = Consolidada
UG_NOME = {"-1":"CONSOLIDADA","0":"PREFEITURA","1":"CAMARA","2":"SAAE"}.get(UG, UG)
SAIDA = os.path.join(HERE, f"credores_moema_{ANO}.json")

def br_money(s):
    if not s: return 0.0
    s = re.sub(r"[^\d,.-]", "", s).replace(".", "").replace(",", ".")
    try: return float(s)
    except: return 0.0

JS_PARSE = r"""
() => {
  const tbl = Array.from(document.querySelectorAll('table'))
     .find(t => /CNPJ\/CPF/.test(t.textContent) && /Valor/.test(t.textContent));
  if (!tbl) return null;
  const out = [];
  tbl.querySelectorAll('tr').forEach(tr => {
    const td = Array.from(tr.querySelectorAll('td'));
    if (td.length < 7) return;
    const c = td.map(x => x.textContent.trim().replace(/\s+/g,' '));
    if (!/R\$/.test(c[2])) return;            // linha de dados tem valores R$
    out.push([c[0], c[1], c[2], c[3], c[4], c[5], c[6]]);
    // nome, cnpj, empenhado, emliquidacao, liquidado, pago, anulado
  });
  return out;
}
"""

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(locale="pt-BR",
              user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36")
        page = ctx.new_page(); page.set_default_timeout(60000)

        print(f"Abrindo Credores ({ANO}, {UG_NOME}) ...")
        page.goto(URL, wait_until="networkidle", timeout=60000)
        page.wait_for_selector("[name=cmbAno]", timeout=30000)

        # filtros: ano + unidade consolidada + periodo do ano inteiro
        page.evaluate(
            """(a) => { const fm=document.forms[0];
               const ca=fm.elements['cmbAno'];
               for (const o of ca.options) if (o.value.startsWith(a.ano+'|')) ca.value=o.value;
               fm.elements['cmbUnidadeGestora'].value=a.ug;
               if(fm.elements['txtDataInicial']) fm.elements['txtDataInicial'].value='01/01/'+a.ano;
               if(fm.elements['txtDataFinal'])   fm.elements['txtDataFinal'].value='31/12/'+a.ano; }""",
            {"ano": ANO, "ug": UG})
        page.evaluate("document.getElementById('confirma').click()")
        page.wait_for_load_state("networkidle", timeout=60000)
        page.wait_for_function("()=>/CNPJ\\/CPF/.test(document.body.innerText)", timeout=60000)

        pagurl = (f"{URL}&visao=1&ano={ANO}&mesinicial={ANO}0101&mesfinal={ANO}1231"
                  f"&unidadegestora={UG}&datainicial=-1&datafinal=-1&numpag=")
        todos = []
        for pag in range(1, 300):
            page.goto(pagurl + str(pag), wait_until="networkidle", timeout=60000)
            rows = page.evaluate(JS_PARSE)
            if not rows: break
            todos.extend(rows)
            if pag % 5 == 0 or len(rows) < 100:
                print(f"  pág {pag}: +{len(rows)} (total {len(todos)})")
            if len(rows) < 100: break
            time.sleep(0.25)
        browser.close()

    regs = []
    for r in todos:
        regs.append({
            "nome": r[0], "cnpj": r[1],
            "empenhado": br_money(r[2]), "em_liquidacao": br_money(r[3]),
            "liquidado": br_money(r[4]), "pago": br_money(r[5]), "anulado": br_money(r[6]),
        })
    payload = {"entidade": UG_NOME, "ano": ANO, "periodo": f"01/01/{ANO} a 31/12/{ANO}",
               "total_credores": len(regs), "registros": regs}
    with open(SAIDA, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    tot_liq = sum(r["liquidado"] for r in regs)
    tot_pago = sum(r["pago"] for r in regs)
    print(f"\nOK -> {SAIDA}")
    print(f"{len(regs)} credores · liquidado R$ {tot_liq:,.2f} · pago R$ {tot_pago:,.2f}")

if __name__ == "__main__":
    main()
