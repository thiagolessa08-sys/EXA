import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime, timedelta, date

from core.theme import inject_theme
from core.template_loader import load_template

inject_theme()

# ── Fonte de dados: Google Sheet publicado (CSV) ──────────────────────────────
SHEET_ID = "122gfwijcQ8f5iNK5aoDwGX3SQugHTiSIj9mo1AQHcOA"
SHEET_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

MESES_PT = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

# Colunas de contagem que somam na agregação (dia -> semana)
NUM_COLS = ["cadastros", "ftd_safra", "ftd_remanescente",
            "ftd_d0", "ftd_d0_d1", "ftd_d0_d3", "ftd_d0_d7", "std_7d",
            "soma_ticket_d0", "soma_ticket_d7"]


# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt_int(n) -> str:
    return f"{int(n or 0):,}".replace(",", ".")

def fmt_pct(n, d=1) -> str:
    return f"{float(n or 0):.{d}f}".replace(".", ",")

def fmt_brl(n) -> str:
    v = float(n or 0)
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"

def safe_div(a, b):
    return (a / b * 100) if b else 0.0

def parse_num(v):
    """Converte valor numerico tolerando formatos BR/US e milhar com ponto."""
    s = str(v).strip()
    if s in ("", "nan", "None"):
        return 0.0
    if "," in s and "." in s:      # 1.234,56 -> 1234.56
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:                 # 27,00 -> 27.00
        s = s.replace(",", ".")
    if s.count(".") > 1:           # 27.000.000 (milhar) -> 27000000
        s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return 0.0


_EMBED_OVERRIDES = """
<style id="exa-streamlit-embed">
  html, body { min-height: 0 !important; height: auto !important; background: transparent !important; }
  .app { grid-template-columns: 1fr !important; min-height: 0 !important; height: auto !important; }
  .sidebar { display: none !important; }
  .topbar { display: none !important; }
  .page { padding-top: 12px !important; padding-bottom: 12px !important; min-height: 0 !important; }
</style>
</head>"""


# ── Carga da planilha ─────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_sheet() -> pd.DataFrame:
    df = pd.read_csv(SHEET_CSV)
    df.columns = [c.strip() for c in df.columns]
    df["dia_safra"] = pd.to_datetime(df["dia_safra"], errors="coerce")
    df = df.dropna(subset=["dia_safra"])

    count_cols = ["cadastros", "ftd_safra", "ftd_remanescente",
                  "ftd_d0", "ftd_d0_d1", "ftd_d0_d3", "ftd_d0_d7", "std_7d"]
    for c in count_cols:
        df[c] = pd.to_numeric(df.get(c, 0), errors="coerce").fillna(0)

    df["ticket_d0"] = df.get("ticket_d0", 0)
    df["ticket_d7"] = df.get("ticket_d7", 0)
    df["ticket_d0"] = df["ticket_d0"].apply(parse_num)
    df["ticket_d7"] = df["ticket_d7"].apply(parse_num)

    # Somas para media ponderada do ticket ao reagregar
    df["soma_ticket_d0"] = df["ticket_d0"] * df["ftd_d0"]
    df["soma_ticket_d7"] = df["ticket_d7"] * df["ftd_d0_d7"]

    df["ym"] = df["dia_safra"].dt.to_period("M")
    return df[["dia_safra", "ym"] + NUM_COLS]


# ── Agregação (dia / semana domingo-sábado) ──────────────────────────────────
def _week_start_sun(s: pd.Series) -> pd.Series:
    # domingo como inicio: weekday() seg=0..dom=6 -> voltar (weekday+1)%7 dias
    return s - pd.to_timedelta((s.dt.weekday + 1) % 7, unit="D")

def aggregate(df: pd.DataFrame, granular: str) -> pd.DataFrame:
    if df.empty:
        return df
    d = df.copy()
    if granular == "dia":
        d["periodo_ini"] = d["dia_safra"]
        d["periodo_fim"] = d["dia_safra"]
        d = d.groupby(["periodo_ini", "periodo_fim"], as_index=False)[NUM_COLS].sum()
        d["periodo_lbl"] = d["periodo_ini"].dt.strftime("%d/%m/%y")
    else:  # semana (dom-sab)
        d["periodo_ini"] = _week_start_sun(d["dia_safra"])
        g = d.groupby("periodo_ini", as_index=False)[NUM_COLS].sum()
        g["periodo_fim"] = g["periodo_ini"] + pd.Timedelta(days=6)
        g["periodo_lbl"] = g["periodo_ini"].dt.strftime("%d/%m") + "–" + g["periodo_fim"].dt.strftime("%d/%m/%y")
        d = g

    hoje = pd.Timestamp(date.today())
    d["dias_desde_fim"] = (hoje - d["periodo_fim"]).dt.days
    d["status_maturacao"] = d["dias_desde_fim"].apply(lambda x: "Completa" if x >= 14 else "Em maturação")

    # Percentuais SOBRE FTD SAFRA
    d["pct_d0"]    = d.apply(lambda r: safe_div(r["ftd_d0"],    r["ftd_safra"]), axis=1)
    d["pct_d0_d1"] = d.apply(lambda r: safe_div(r["ftd_d0_d1"], r["ftd_safra"]), axis=1)
    d["pct_d0_d3"] = d.apply(lambda r: safe_div(r["ftd_d0_d3"], r["ftd_safra"]), axis=1)
    d["pct_d0_d7"] = d.apply(lambda r: safe_div(r["ftd_d0_d7"], r["ftd_safra"]), axis=1)
    d["pct_std"]   = d.apply(lambda r: safe_div(r["std_7d"],    r["ftd_safra"]), axis=1)
    d["conv_safra"] = d.apply(lambda r: safe_div(r["ftd_safra"], r["cadastros"]), axis=1)
    d["ticket_d0"] = d.apply(lambda r: (r["soma_ticket_d0"] / r["ftd_d0"]) if r["ftd_d0"] else 0, axis=1)
    d["ticket_d7"] = d.apply(lambda r: (r["soma_ticket_d7"] / r["ftd_d0_d7"]) if r["ftd_d0_d7"] else 0, axis=1)

    return d.sort_values("periodo_ini", ascending=False)


def rows_to_payload(d: pd.DataFrame) -> list:
    out = []
    for _, r in d.iterrows():
        out.append({
            "periodo":      r["periodo_lbl"],
            "cadastros":    fmt_int(r["cadastros"]),
            "ftd_safra":    fmt_int(r["ftd_safra"]),
            "ftd_reman":    fmt_int(r["ftd_remanescente"]),
            "pct_d0":       fmt_pct(r["pct_d0"]),
            "pct_d0_d1":    fmt_pct(r["pct_d0_d1"]),
            "pct_d0_d3":    fmt_pct(r["pct_d0_d3"]),
            "pct_d0_d7":    fmt_pct(r["pct_d0_d7"]),
            "ticket_d0":    fmt_brl(r["ticket_d0"]),
            "ticket_d7":    fmt_brl(r["ticket_d7"]),
            "pct_std":      fmt_pct(r["pct_std"]),
            "status":       r["status_maturacao"],
            "status_cor":   "warn" if r["status_maturacao"] == "Em maturação" else "good",
        })
    return out


def build_payload(df_mes: pd.DataFrame, mes_lbl: str) -> dict:
    d_dia    = aggregate(df_mes, "dia")
    d_semana = aggregate(df_mes, "semana")

    tot = {c: int(df_mes[c].sum()) if not df_mes.empty else 0 for c in NUM_COLS}
    conv_safra   = safe_div(tot["ftd_safra"], tot["cadastros"])
    pct_std_tot  = safe_div(tot["std_7d"], tot["ftd_safra"])
    pct_d7_tot   = safe_div(tot["ftd_d0_d7"], tot["ftd_safra"])
    ticket_d0_tot = (tot["soma_ticket_d0"] / tot["ftd_d0"]) if tot["ftd_d0"] else 0
    ticket_d7_tot = (tot["soma_ticket_d7"] / tot["ftd_d0_d7"]) if tot["ftd_d0_d7"] else 0

    if df_mes.empty:
        dt_ini = dt_fim = date.today()
    else:
        dt_ini = df_mes["dia_safra"].min().date()
        dt_fim = df_mes["dia_safra"].max().date()

    # Funil (sobre o mes): Cadastros -> FTD Safra -> D0-D7 -> STD
    funil = [
        {"label": "Cadastros",       "qtd": tot["cadastros"], "pct_base": 100.0, "base_lbl": ""},
        {"label": "FTD Safra",       "qtd": tot["ftd_safra"], "pct_base": conv_safra, "base_lbl": "dos cadastros"},
        {"label": "FTD até D7",      "qtd": tot["ftd_d0_d7"], "pct_base": pct_d7_tot, "base_alt": True, "base_lbl": "do FTD Safra"},
        {"label": "STD em 7 dias",   "qtd": tot["std_7d"],    "pct_base": pct_std_tot, "base_alt": True, "base_lbl": "do FTD Safra"},
    ]
    funil_max = max((f["qtd"] for f in funil), default=1) or 1
    for f in funil:
        f["pct_barra"] = round(f["qtd"] / funil_max * 100, 1)
        f["qtd"] = fmt_int(f["qtd"])
        f["pct_base"] = fmt_pct(f["pct_base"])

    return {
        "filters": {
            "periodo":     mes_lbl,
            "data_inicio": dt_ini.strftime("%d/%m/%Y"),
            "data_fim":    dt_fim.strftime("%d/%m/%Y"),
            "atualizado":  datetime.now().strftime("%d/%m/%Y · %H:%M"),
        },
        "header": {
            "eyebrow": "Painel · Onboarding",
            "title":   "Safras",
            "lede":    "Funil da safra do mês — FTD Safra (cadastro + FTD no mesmo mês), janelas D0–D7 e 2º depósito (STD) em 7 dias. Percentuais sobre o FTD Safra.",
            "base_analise": "Data de Cadastro",
        },
        "user": {"name": "Analytics", "role": "EXA", "initials": "EX"},
        "nav": [
            {"key": "onboarding",  "label": "Onboarding",  "icon": "funnel"},
            {"key": "retencao",    "label": "Retenção",    "icon": "retention"},
            {"key": "performance", "label": "Performance", "icon": "perf"},
            {"key": "clusters",    "label": "Clusters",    "icon": "cluster"},
            {"key": "safras",      "label": "Safras",      "icon": "safra", "active": True},
            {"key": "chat",        "label": "Chat",        "icon": "chat"},
        ],
        "resumo": [
            {"lbl": "Cadastros no mês",       "val": fmt_int(tot["cadastros"])},
            {"lbl": "FTD Total Safra",        "val": fmt_int(tot["ftd_safra"]), "sub": fmt_pct(conv_safra) + "% dos cadastros", "cor": "#2540ea"},
            {"lbl": "FTD Remanescentes",      "val": fmt_int(tot["ftd_remanescente"]), "sub": "FTD fora do mês do cadastro", "cor": "#c66a00"},
            {"lbl": "STD em 7 dias pós FTD",  "val": fmt_pct(pct_std_tot) + "%", "sub": fmt_int(tot["std_7d"]) + " · base FTD Safra", "cor": "#1f9d57"},
            {"lbl": "Ticket médio · D0",      "val": fmt_brl(ticket_d0_tot), "sub": "FTD no mesmo dia"},
            {"lbl": "Ticket médio · D7",      "val": fmt_brl(ticket_d7_tot), "sub": "FTD até 7 dias"},
        ],
        "funil": funil,
        "tabelas": {
            "dia":    rows_to_payload(d_dia),
            "semana": rows_to_payload(d_semana),
        },
    }


# ── Carrega dados + Sidebar (seletor de mês) ─────────────────────────────────
erro_carga = None
try:
    df_all = load_sheet()
except Exception as e:
    erro_carga = str(e)
    df_all = pd.DataFrame(columns=["dia_safra", "ym"] + NUM_COLS)

# meses disponiveis (a query ja limita a atual + anterior)
periodos = sorted(df_all["ym"].dropna().unique(), reverse=True) if not df_all.empty else []
labels = [f"{MESES_PT[p.month - 1]}/{p.year}" for p in periodos]

with st.sidebar:
    st.markdown("---")
    st.markdown("**Filtros**")
    if labels:
        mes_sel = st.selectbox("Mês da safra", labels, index=0, key="safra_mes")
    else:
        mes_sel = None
        st.info("Sem dados na planilha.")
    if st.button("🔄 Recarregar planilha", key="safra_reload"):
        st.cache_data.clear()
        st.rerun()

if erro_carga:
    st.error(f"Falha ao ler a planilha: {erro_carga}")

if mes_sel:
    p_sel = periodos[labels.index(mes_sel)]
    df_mes = df_all[df_all["ym"] == p_sel].copy()
else:
    df_mes = df_all.iloc[0:0].copy()
    mes_sel = "—"


# ── Render ────────────────────────────────────────────────────────────────────
with st.spinner("Carregando safras..."):
    payload = build_payload(df_mes, mes_sel)

template = load_template("dashboard_safras.html")
html = template.replace("__EXA_DATA_JSON__", json.dumps(payload, ensure_ascii=False))
html = html.replace("</head>", _EMBED_OVERRIDES)
components.html(html, height=1400, scrolling=False)
