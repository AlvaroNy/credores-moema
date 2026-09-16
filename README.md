# Credores — Prefeitura de Moema/MG

Dashboard interativo das **despesas por credor** da Prefeitura Municipal de
Moema/MG, extraídas do
[Portal da Transparência](https://webapp1-moema.cidade360.cloud/pronimtb/index.asp?acao=3&item=10)
(plataforma TransparênciaBR / Cidade360).

Mostra quem recebeu da prefeitura e quanto, com ranking dos maiores credores,
busca, filtros e gráficos.

🔗 **Online:** https://alvarony.github.io/credores-moema/

---

## O que o painel mostra

- **KPIs:** nº de credores, total empenhado, liquidado e pago, e a concentração
  (quanto os 10 maiores representam do total).
- **Top 15 maiores credores** (gráfico de barras) e **gasto por tipo de credor**
  (rosca).
- **Tabela completa** de todos os credores, com busca por nome/CNPJ, ordenação e
  filtro por tipo.
- Classificação automática (heurística pelo nome) em três tipos:
  - **Fornecedor** — empresas/pessoas que prestaram serviço ou venderam
  - **Ente público/Repasse** — Município, Câmara, SAAE, fundações, fundos etc.
  - **Encargos/Tributos** — INSS, FGTS, impostos, contribuições

  Isso separa o gasto real com fornecedores dos repasses internos e encargos.

Colunas de valor: **Empenhado** (comprometido) · **Liquidado** (despesa
efetivada) · **Pago** (efetivamente pago).

Tudo em **um único `index.html`** self-contained (Plotly embutido), abre em
qualquer navegador.

## Escopo dos dados

- Fonte: Portal da Transparência de Moema → **Despesas › Credores**.
- Anos carregados: **2025** (1.055 credores) e **2026** (Consolidada = Prefeitura +
  Câmara + SAAE), período 01/01 a 31/12 de cada ano. Há um **seletor de ano** no
  topo que troca todo o painel.
- Dá para puxar outros anos (2021–2026) e por entidade separada — cada ano vira um
  arquivo `credores_moema_<ano>.json` e aparece automaticamente no seletor.

## Como atualizar / gerar outro ano

Requer Python 3 + Playwright (ver [Requisitos](#requisitos)).

```bash
# Extrai os credores de um ano -> credores_moema_<ano>.json
python extrair_credores_moema.py 2026        # ano (default 2026), Consolidada
python extrair_credores_moema.py 2025        # outro ano
python extrair_credores_moema.py 2026 0      # ano + unidade (0=Prefeitura,1=Camara,2=SAAE,-1=Consolidada)

# Regenera o dashboard (carrega TODOS os credores_moema_*.json) -> index.html
python gerar_painel_credores_moema.py
```

O gerador junta todos os anos presentes na pasta e monta o seletor sozinho.
Depois é só commitar `index.html` (e os `.json`); o GitHub Pages republica sozinho.

## Requisitos

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

## Estrutura

| Arquivo | O quê |
|---|---|
| `index.html` | O dashboard (gerado; é o que o Pages publica) |
| `credores_moema_2026.json` | Dados extraídos (por credor) |
| `extrair_credores_moema.py` | Extrator Playwright |
| `gerar_painel_credores_moema.py` | Gera o `index.html` |
| `plotly.min.js` | Gráficos (embutido no HTML na geração) |

## Nota técnica

Como no painel de funcionários, o relatório só é devolvido numa **navegação real**
(form submit dentro da sessão ASP) — por isso a extração usa Playwright. A
paginação é feita por uma URL que carrega todos os filtros
(`&visao=1&ano=..&mesinicial=AAAA0101&mesfinal=AAAA1231&unidadegestora=..&numpag=N`),
100 credores por página.

Colunas do relatório (índice da célula): `0` Nome · `1` CNPJ/CPF ·
`2` Empenhado · `3` Em Liquidação · `4` Liquidado · `5` Pago · `6` Anulado.

---

*Dados públicos, extraídos do Portal da Transparência de Moema/MG.
Projeto de uso pessoal para consulta facilitada.*
