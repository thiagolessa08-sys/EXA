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

SHEET_ID = "122gfwijcQ8f5iNK5aoDwGX3SQugHTiSIj9mo1AQHcOA"
SHEET_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

MESES_PT = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

# Safra so fecha de vez apos: 7 dias (janela do FTD) + 30 dias (janela do STD pos-7d)
DIAS_MATURACAO = 37

# Piso de data: ignora linhas antigas de schema velho que sobrem na planilha
DATA_FLOOR = pd.Timestamp("2026-04-01")


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
    """O Sheets (locale BR) exporta o ticket de 6 casas '22.060000' como
    '22.060.000' (ponto de milhar) -> valor real = digitos / 1_000_000."""
    s = str(v).strip()
    if s in ("", "nan", "None"):
        return 0.0
    if "," in s:
        try:
            return float(s.replace(".", "").replace(",", "."))
        except ValueError:
            return 0.0
    if s.count(".") >= 2:
        try:
            return int(s.replace(".", "")) / 1_000_000
        except ValueError:
            return 0.0
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


# ── Carga ─────────────────────────────────────────────────────────────────────
# Colunas somaveis (contagens + somas de ticket p/ media ponderada ao reagregar)
NUM_COLS = [
    "cadastros", "ftd_safra", "ftd_extra",
    "ftd_d0", "ftd_d0_d1", "ftd_d0_d3", "ftd_d0_d7",
    "std_7d", "std_pos7",
    "soma_tkt_d0", "soma_tkt_d7", "soma_tkt_safra", "soma_tkt_extra",
    "soma_tkt_std7", "soma_tkt_stdpos7",
]

CNT_COLS = ["cadastros", "ftd_safra", "ftd_extra", "ftd_d0", "ftd_d0_d1",
            "ftd_d0_d3", "ftd_d0_d7", "std_7d", "std_pos7"]

TKT_COLS = ["ticket_d0", "ticket_d7", "ticket_ftd_safra", "ticket_ftd_extra",
            "ticket_std_7d", "ticket_std_pos7"]


@st.cache_data(ttl=300, show_spinner=False)
def load_sheet() -> pd.DataFrame:
    df = pd.read_csv(SHEET_CSV)
    df.columns = [c.strip() for c in df.columns]
    df["dia_safra"] = pd.to_datetime(df["dia_safra"], errors="coerce")
    df = df.dropna(subset=["dia_safra"])
    df = df[df["dia_safra"] >= DATA_FLOOR]

    for c in CNT_COLS:
        if c not in df.columns:
            df[c] = 0
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    for c in TKT_COLS:
        if c not in df.columns:
            df[c] = 0
        df[c] = df[c].apply(parse_num)

    # somas para media ponderada na reagregacao
    df["soma_tkt_d0"]      = df["ticket_d0"]        * df["ftd_d0"]
    df["soma_tkt_d7"]      = df["ticket_d7"]        * df["ftd_d0_d7"]
    df["soma_tkt_safra"]   = df["ticket_ftd_safra"] * df["ftd_safra"]
    df["soma_tkt_extra"]   = df["ticket_ftd_extra"] * df["ftd_extra"]
    df["soma_tkt_std7"]    = df["ticket_std_7d"]    * df["std_7d"]
    df["soma_tkt_stdpos7"] = df["ticket_std_pos7"]  * df["std_pos7"]

    return df[["dia_safra"] + NUM_COLS]


df_all = load_sheet() if True else pd.DataFrame()
df_all["ym"] = df_all["dia_safra"].dt.to_period("M") if not df_all.empty else None


# ── Sidebar: mes (atalho) + data livre ────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown("**Filtros**")

    periodos = sorted(df_all["ym"].dropna().unique(), reverse=True) if not df_all.empty else []
    opcoes = [f"{MESES_PT[p.month - 1]}/{p.year}" for p in periodos] + ["Período personalizado"]

    escolha = st.selectbox("Mês da safra", opcoes, index=0, key="safra_mes")

    if escolha == "Período personalizado":
        d_min = df_all["dia_safra"].min().date() if not df_all.empty else date.today()
        d_max = df_all["dia_safra"].max().date() if not df_all.empty else date.today()
        dt_ini = st.date_input("De",  value=d_min, min_value=d_min, max_value=d_max, key="safra_de")
        dt_fim = st.date_input("Até", value=d_max, min_value=d_min, max_value=d_max, key="safra_ate")
        label_periodo = "Personalizado"
    else:
        p = periodos[opcoes.index(escolha)]
        dt_ini = p.start_time.date()
        dt_fim = min(p.end_time.date(), date.today())
        label_periodo = escolha

    if st.button("🔄 Recarregar planilha", key="safra_reload"):
        st.cache_data.clear()
        st.rerun()


# ── Agregação ─────────────────────────────────────────────────────────────────
def aggregate(df: pd.DataFrame, granular: str) -> pd.DataFrame:
    if df.empty:
        return df
    d = df.copy()
    if granular == "semana":
        # semana domingo -> sabado
        off = (d["dia_safra"].dt.weekday + 1) % 7
        d["periodo_ini"] = d["dia_safra"] - pd.to_timedelta(off, unit="D")
        g = d.groupby("periodo_ini", as_index=False)[NUM_COLS].sum()
        g["periodo_fim"] = g["periodo_ini"] + pd.Timedelta(days=6)
        g["periodo_lbl"] = g["periodo_ini"].dt.strftime("%d/%m") + "–" + g["periodo_fim"].dt.strftime("%d/%m/%y")
        d = g
    else:  # mes
        d["periodo_ini"] = d["dia_safra"].dt.to_period("M").dt.to_timestamp()
        g = d.groupby("periodo_ini", as_index=False)[NUM_COLS].sum()
        g["periodo_fim"] = g["periodo_ini"] + pd.offsets.MonthEnd(0)
        g["periodo_lbl"] = g["periodo_ini"].apply(lambda x: f"{MESES_PT[x.month - 1]}/{x.year}")
        d = g

    hoje = pd.Timestamp(date.today())
    d["dias_desde_fim"] = (hoje - d["periodo_fim"]).dt.days
    d["status"] = d["dias_desde_fim"].apply(
        lambda x: "Completa" if x >= DIAS_MATURACAO else "Em maturação")

    # FTD Extra Safra Anteriores: FTDs no periodo de coortes anteriores
    # (a query ja entrega isso direto na coluna ftd_extra)
    d["ftd_extra_ant"] = d["ftd_extra"]

    # % sempre sobre FTD Safra (exceto conversao de cadastro)
    d["pct_conv"]     = d.apply(lambda r: safe_div(r["ftd_safra"],  r["cadastros"]), axis=1)
    d["pct_d0"]       = d.apply(lambda r: safe_div(r["ftd_d0"],     r["ftd_safra"]), axis=1)
    d["pct_d0_d1"]    = d.apply(lambda r: safe_div(r["ftd_d0_d1"],  r["ftd_safra"]), axis=1)
    d["pct_d0_d3"]    = d.apply(lambda r: safe_div(r["ftd_d0_d3"],  r["ftd_safra"]), axis=1)
    d["pct_d0_d7"]    = d.apply(lambda r: safe_div(r["ftd_d0_d7"],  r["ftd_safra"]), axis=1)
    d["pct_std_7d"]   = d.apply(lambda r: safe_div(r["std_7d"],     r["ftd_safra"]), axis=1)
    d["pct_std_pos7"] = d.apply(lambda r: safe_div(r["std_pos7"],   r["ftd_safra"]), axis=1)

    def wavg(num, den):
        return d.apply(lambda r: (r[num] / r[den]) if r[den] else 0, axis=1)

    d["tkt_d0"]       = wavg("soma_tkt_d0", "ftd_d0")
    d["tkt_d7"]       = wavg("soma_tkt_d7", "ftd_d0_d7")
    d["tkt_std7"]     = wavg("soma_tkt_std7", "std_7d")
    d["tkt_stdpos7"]  = wavg("soma_tkt_stdpos7", "std_pos7")
    d["tkt_extra_ant"] = wavg("soma_tkt_extra", "ftd_extra_ant")

    return d.sort_values("periodo_ini", ascending=False)


def rows_to_payload(d: pd.DataFrame) -> list:
    out = []
    for _, r in d.iterrows():
        out.append({
            "periodo":      r["periodo_lbl"],
            "cadastros":    fmt_int(r["cadastros"]),
            "ftd_safra":    fmt_int(r["ftd_safra"]),
            "ftd_extra":    fmt_int(r["ftd_extra_ant"]),
            "pct_conv":     fmt_pct(r["pct_conv"]),
            "pct_d0":       fmt_pct(r["pct_d0"]),
            "pct_d0_d7":    fmt_pct(r["pct_d0_d7"]),
            "tkt_d0":       fmt_brl(r["tkt_d0"]),
            "tkt_d7":       fmt_brl(r["tkt_d7"]),
            "pct_std_7d":   fmt_pct(r["pct_std_7d"]),
            "pct_std_pos7": fmt_pct(r["pct_std_pos7"]),
            "tkt_std7":     fmt_brl(r["tkt_std7"]),
            "status":       r["status"],
            "status_cor":   "warn" if r["status"] == "Em maturação" else "good",
        })
    return out


# ── Payload ───────────────────────────────────────────────────────────────────
def build_payload() -> dict:
    d = df_all[(df_all["dia_safra"].dt.date >= dt_ini) &
               (df_all["dia_safra"].dt.date <= dt_fim)] if not df_all.empty else df_all

    tot = {c: float(d[c].sum()) if not d.empty else 0 for c in NUM_COLS}

    def wtkt(soma, cnt):
        return (tot[soma] / tot[cnt]) if tot[cnt] else 0

    pct_conv     = safe_div(tot["ftd_safra"], tot["cadastros"])
    pct_std_7d   = safe_div(tot["std_7d"], tot["ftd_safra"])
    pct_std_pos7 = safe_div(tot["std_pos7"], tot["ftd_safra"])

    # FTD Extra Safra Anteriores: FTDs no periodo de coortes anteriores (coluna ftd_extra)
    ftd_extra_ant = tot["ftd_extra"]
    tkt_extra_ant = (tot["soma_tkt_extra"] / ftd_extra_ant) if ftd_extra_ant else 0

    # Linha 1: Cadastros | FTD Safra | FTD Extra Safra Anteriores | TKM FTD Safra | TKM FTD Extra
    kpis_1 = [
        {"lbl": "Cadastros no período",         "val": fmt_int(tot["cadastros"]), "sub": label_periodo},
        {"lbl": "FTD Total / Safra",            "val": fmt_int(tot["ftd_safra"]), "sub": fmt_pct(pct_conv) + "% dos cadastros", "cor": "#2540ea"},
        {"lbl": "FTD Extra Safra Anteriores",   "val": fmt_int(ftd_extra_ant),    "sub": "FTD no período de coortes anteriores", "cor": "#6b7280"},
        {"lbl": "TKM FTD Safra",                "val": fmt_brl(wtkt("soma_tkt_safra", "ftd_safra")), "sub": "ticket médio"},
        {"lbl": "TKM FTD Safra Anterior", "val": fmt_brl(tkt_extra_ant),  "sub": "ticket médio"},
    ]
    # Linha 2: STD ate 7d | STD pos 7d | TKM STD ate D7 | TKM STD pos 7d
    kpis_2 = [
        {"lbl": "STD em até 7 dias", "val": fmt_pct(pct_std_7d) + "%",   "sub": fmt_int(tot["std_7d"]) + " · sobre FTD Safra", "cor": "#1f9d57", "destaque": True},
        {"lbl": "STD pós 7 dias",    "val": fmt_pct(pct_std_pos7) + "%", "sub": fmt_int(tot["std_pos7"]) + " · 8 a 30 dias", "cor": "#c66a00"},
        {"lbl": "TKM STD até D7",    "val": fmt_brl(wtkt("soma_tkt_std7", "std_7d")), "sub": "ticket médio 2º depósito"},
        {"lbl": "TKM STD pós 7d",    "val": fmt_brl(wtkt("soma_tkt_stdpos7", "std_pos7")), "sub": "ticket médio 2º depósito"},
    ]

    funil = [
        {"label": "Cadastros",       "qtd": tot["cadastros"], "pct_base": 100.0},
        {"label": "FTD Safra",       "qtd": tot["ftd_safra"], "pct_base": pct_conv, "base_alt": "dos cadastros"},
        {"label": "FTD até D7",      "qtd": tot["ftd_d0_d7"], "pct_base": safe_div(tot["ftd_d0_d7"], tot["ftd_safra"]), "base_alt": "do FTD Safra"},
        {"label": "STD até 7 dias",  "qtd": tot["std_7d"],    "pct_base": pct_std_7d, "base_alt": "do FTD Safra"},
        {"label": "STD pós 7 dias",  "qtd": tot["std_pos7"],  "pct_base": pct_std_pos7, "base_alt": "do FTD Safra"},
    ]
    fmax = max((f["qtd"] for f in funil), default=1) or 1
    for f in funil:
        f["pct_barra"] = round(f["qtd"] / fmax * 100, 1)
        f["qtd"] = fmt_int(f["qtd"])
        f["pct_base"] = fmt_pct(f["pct_base"])

    return {
        "filters": {
            "periodo":     label_periodo,
            "data_inicio": dt_ini.strftime("%d/%m/%Y"),
            "data_fim":    dt_fim.strftime("%d/%m/%Y"),
            "atualizado":  datetime.now().strftime("%d/%m/%Y · %H:%M"),
        },
        "header": {
            "eyebrow": "Painel · Onboarding",
            "title":   "Safras",
            "lede":    "Funil de conversão por safra de cadastro — FTD (safra e extra safra), segundo depósito (STD) até 7 dias e de 8 a 30 dias.",
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
        "kpis_1": kpis_1,
        "kpis_2": kpis_2,
        "funil": funil,
        "maturacao_dias": DIAS_MATURACAO,
        "tabelas": {
            "semana": rows_to_payload(aggregate(d, "semana")),
            "mes":    rows_to_payload(aggregate(d, "mes")),
        },
    }


with st.spinner("Carregando safras..."):
    payload = build_payload()

template = load_template("dashboard_safras.html")
html = template.replace("__EXA_DATA_JSON__", json.dumps(payload, ensure_ascii=False))
html = html.replace("</head>", _EMBED_OVERRIDES)
components.html(html, height=1500, scrolling=False)
