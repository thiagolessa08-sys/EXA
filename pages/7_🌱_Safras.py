import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime, timedelta, date

from core.databricks_client import execute_query
from core.theme import inject_theme
from core.template_loader import load_template

inject_theme()


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


_EMBED_OVERRIDES = """
<style id="exa-streamlit-embed">
  html, body { min-height: 0 !important; height: auto !important; background: transparent !important; }
  .app { grid-template-columns: 1fr !important; min-height: 0 !important; height: auto !important; }
  .sidebar { display: none !important; }
  .topbar { display: none !important; }
  .page { padding-top: 12px !important; padding-bottom: 12px !important; min-height: 0 !important; }
</style>
</head>"""


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown("**Filtros**")

    today = date.today()
    janela = st.selectbox(
        "Janela de cadastro",
        ["Últimos 30 dias", "Últimos 60 dias", "Últimos 90 dias", "Data aberta"],
        index=1,
        key="safra_janela",
    )
    if janela == "Data aberta":
        dt_ini = st.date_input("De", value=today - timedelta(days=60), key="safra_de")
        dt_fim = st.date_input("Até", value=today, key="safra_ate")
    else:
        dias = {"Últimos 30 dias": 30, "Últimos 60 dias": 60, "Últimos 90 dias": 90}[janela]
        dt_ini = today - timedelta(days=dias)
        dt_fim = today

ini_str = str(dt_ini)
fim_str = str(dt_fim)


# ── Query ─────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_safras(ini: str, fim: str) -> pd.DataFrame:
    """Funil diário de safra: cadastro -> FTD (D0/D0-D1/D0-D3/D0-D7) -> STD em 7 dias -> KYC.
    Retorna contagens BRUTAS (não percentuais) para permitir reagregação
    correta por semana/mês em pandas (soma de numeradores, não média de %)."""
    q = f"""
    WITH deposits_ranked AS (
        SELECT
            d.user_ext_id, d.deposit_amount, d.dt_finalized,
            ROW_NUMBER() OVER (PARTITION BY d.user_ext_id ORDER BY d.dt_finalized ASC) AS rn
        FROM workspace.default.v_deposits_summary d
    ),
    ftd AS (
        SELECT user_ext_id, deposit_amount AS valor_ftd, dt_finalized AS dt_ftd
        FROM deposits_ranked WHERE rn = 1
    ),
    std AS (
        SELECT user_ext_id, dt_finalized AS dt_std
        FROM deposits_ranked WHERE rn = 2
    ),
    base AS (
        SELECT
            u.user_ext_id,
            CAST(u.core_registration_date AS DATE) AS dia_safra,
            u.core_kyc_status AS kyc_status,
            f.valor_ftd, f.dt_ftd, s.dt_std,
            CASE WHEN f.dt_ftd IS NOT NULL
                 THEN DATEDIFF(f.dt_ftd, u.core_registration_date) ELSE NULL END AS dias_ate_ftd,
            CASE WHEN f.dt_ftd IS NOT NULL AND s.dt_std IS NOT NULL
                 THEN DATEDIFF(s.dt_std, f.dt_ftd) ELSE NULL END AS dias_ftd_ate_std
        FROM workspace.default.v_users_summary u
        LEFT JOIN ftd f ON u.user_ext_id = f.user_ext_id
        LEFT JOIN std s ON u.user_ext_id = s.user_ext_id
        WHERE u.core_registration_date BETWEEN '{ini}' AND '{fim} 23:59:59'
    ),
    flags AS (
        SELECT *,
            CASE WHEN dt_ftd IS NOT NULL THEN 1 ELSE 0 END AS tem_ftd,
            CASE WHEN dias_ate_ftd = 0            THEN 1 ELSE 0 END AS is_d0,
            CASE WHEN dias_ate_ftd BETWEEN 0 AND 1 THEN 1 ELSE 0 END AS is_d0_d1,
            CASE WHEN dias_ate_ftd BETWEEN 0 AND 3 THEN 1 ELSE 0 END AS is_d0_d3,
            CASE WHEN dias_ate_ftd BETWEEN 0 AND 7 THEN 1 ELSE 0 END AS is_d0_d7,
            CASE WHEN dias_ftd_ate_std BETWEEN 0 AND 7 THEN 1 ELSE 0 END AS is_std_7d,
            CASE WHEN kyc_status IN ('approved','APPROVED','Approved','verified','VERIFIED')
                 THEN 1 ELSE 0 END AS is_kyc
        FROM base
    )
    SELECT
        dia_safra,
        COUNT(*)                                                  AS cadastros,
        SUM(tem_ftd)                                               AS ftds_total,
        SUM(is_d0)                                                 AS d0_qtd,
        SUM(is_d0_d1)                                              AS d0_d1_qtd,
        SUM(is_d0_d3)                                              AS d0_d3_qtd,
        SUM(is_d0_d7)                                              AS d0_d7_qtd,
        SUM(CASE WHEN is_d0_d7 = 1 THEN valor_ftd ELSE 0 END)      AS soma_ticket_d0_d7,
        SUM(is_d0_d7)                                              AS cnt_ticket_d0_d7,
        SUM(is_std_7d)                                             AS std_7d_qtd,
        SUM(CASE WHEN tem_ftd = 1 AND is_kyc = 1 THEN 1 ELSE 0 END) AS kyc_ftd_qtd
    FROM flags
    GROUP BY dia_safra
    ORDER BY dia_safra DESC
    """
    df = execute_query(q)
    if not df.empty:
        df["dia_safra"] = pd.to_datetime(df["dia_safra"])
    return df


# ── Agregação (dia / semana / mês) ───────────────────────────────────────────
NUM_COLS = ["cadastros", "ftds_total", "d0_qtd", "d0_d1_qtd", "d0_d3_qtd", "d0_d7_qtd",
            "soma_ticket_d0_d7", "cnt_ticket_d0_d7", "std_7d_qtd", "kyc_ftd_qtd"]

def aggregate(df: pd.DataFrame, granular: str) -> pd.DataFrame:
    if df.empty:
        return df
    d = df.copy()
    if granular == "dia":
        d["periodo_ini"] = d["dia_safra"]
        d["periodo_fim"] = d["dia_safra"]
        d["periodo_lbl"] = d["dia_safra"].dt.strftime("%d/%m/%y")
    elif granular == "semana":
        d["periodo_ini"] = d["dia_safra"] - pd.to_timedelta(d["dia_safra"].dt.weekday, unit="D")
        d["periodo_fim"] = d["periodo_ini"] + pd.Timedelta(days=6)
        g = d.groupby("periodo_ini", as_index=False)[NUM_COLS].sum()
        g["periodo_fim"] = g["periodo_ini"] + pd.Timedelta(days=6)
        g["periodo_lbl"] = g["periodo_ini"].dt.strftime("%d/%m") + "–" + g["periodo_fim"].dt.strftime("%d/%m/%y")
        d = g
    elif granular == "mes":
        d["periodo_ini"] = d["dia_safra"].dt.to_period("M").dt.to_timestamp()
        g = d.groupby("periodo_ini", as_index=False)[NUM_COLS].sum()
        g["periodo_fim"] = g["periodo_ini"] + pd.offsets.MonthEnd(0)
        g["periodo_lbl"] = g["periodo_ini"].dt.strftime("%b/%y")
        d = g

    if granular == "dia":
        d = d.groupby(["periodo_ini", "periodo_fim", "periodo_lbl"], as_index=False)[NUM_COLS].sum()

    hoje = pd.Timestamp(date.today())
    d["dias_desde_fim"] = (hoje - d["periodo_fim"]).dt.days
    d["status_maturacao"] = d["dias_desde_fim"].apply(lambda x: "Completa" if x >= 14 else "Em maturação")

    d["pct_d0"]    = d.apply(lambda r: safe_div(r["d0_qtd"],    r["cadastros"]), axis=1)
    d["pct_d0_d1"] = d.apply(lambda r: safe_div(r["d0_d1_qtd"], r["cadastros"]), axis=1)
    d["pct_d0_d3"] = d.apply(lambda r: safe_div(r["d0_d3_qtd"], r["cadastros"]), axis=1)
    d["pct_d0_d7"] = d.apply(lambda r: safe_div(r["d0_d7_qtd"], r["cadastros"]), axis=1)
    d["pct_std_7d"]= d.apply(lambda r: safe_div(r["std_7d_qtd"],r["ftds_total"]), axis=1)
    d["pct_kyc"]   = d.apply(lambda r: safe_div(r["kyc_ftd_qtd"], r["ftds_total"]), axis=1)
    d["ticket_medio"] = d.apply(lambda r: (r["soma_ticket_d0_d7"] / r["cnt_ticket_d0_d7"]) if r["cnt_ticket_d0_d7"] else 0, axis=1)

    return d.sort_values("periodo_ini", ascending=False)


# ── Payload ───────────────────────────────────────────────────────────────────
def rows_to_payload(d: pd.DataFrame) -> list:
    out = []
    for _, r in d.iterrows():
        out.append({
            "periodo":      r["periodo_lbl"],
            "cadastros":    fmt_int(r["cadastros"]),
            "ftds_total":   fmt_int(r["ftds_total"]),
            "pct_d0":       fmt_pct(r["pct_d0"]),
            "pct_d0_d1":    fmt_pct(r["pct_d0_d1"]),
            "pct_d0_d3":    fmt_pct(r["pct_d0_d3"]),
            "pct_d0_d7":    fmt_pct(r["pct_d0_d7"]),
            "ticket_medio": fmt_brl(r["ticket_medio"]),
            "pct_std_7d":   fmt_pct(r["pct_std_7d"]),
            "pct_kyc":      fmt_pct(r["pct_kyc"]),
            "status":       r["status_maturacao"],
            "status_cor":   "warn" if r["status_maturacao"] == "Em maturação" else "good",
        })
    return out


def build_payload(ini: str, fim: str) -> dict:
    try:
        df_raw = load_safras(ini, fim)
    except Exception as e:
        st.error(f"Falha ao carregar safras: {e}")
        df_raw = pd.DataFrame(columns=["dia_safra"] + NUM_COLS)

    d_dia    = aggregate(df_raw, "dia")
    d_semana = aggregate(df_raw, "semana")
    d_mes    = aggregate(df_raw, "mes")

    # Totais do período (para KPIs e funil) — soma de brutos, nunca média de %
    tot = {c: int(df_raw[c].sum()) if not df_raw.empty else 0 for c in NUM_COLS}
    pct_d0_7_tot   = safe_div(tot["d0_d7_qtd"], tot["cadastros"])
    pct_std_tot    = safe_div(tot["std_7d_qtd"], tot["ftds_total"])
    pct_kyc_tot    = safe_div(tot["kyc_ftd_qtd"], tot["ftds_total"])
    ticket_tot     = (tot["soma_ticket_d0_d7"] / tot["cnt_ticket_d0_d7"]) if tot["cnt_ticket_d0_d7"] else 0

    funil = [
        {"label": "Cadastros",         "qtd": tot["cadastros"],  "pct_base": 100.0},
        {"label": "FTD D0",            "qtd": tot["d0_qtd"],     "pct_base": safe_div(tot["d0_qtd"], tot["cadastros"])},
        {"label": "FTD D0–D1",         "qtd": tot["d0_d1_qtd"],  "pct_base": safe_div(tot["d0_d1_qtd"], tot["cadastros"])},
        {"label": "FTD D0–D3",         "qtd": tot["d0_d3_qtd"],  "pct_base": safe_div(tot["d0_d3_qtd"], tot["cadastros"])},
        {"label": "FTD D0–D7",         "qtd": tot["d0_d7_qtd"],  "pct_base": safe_div(tot["d0_d7_qtd"], tot["cadastros"])},
        {"label": "STD em 7 dias",     "qtd": tot["std_7d_qtd"], "pct_base": pct_std_tot, "base_alt": "sobre FTDs"},
    ]
    funil_max = max(f["qtd"] for f in funil) or 1
    for f in funil:
        f["pct_barra"] = round(f["qtd"] / funil_max * 100, 1)
        f["qtd"] = fmt_int(f["qtd"])
        f["pct_base"] = fmt_pct(f["pct_base"])

    return {
        "filters": {
            "periodo":    f"{dt_ini.strftime('%d/%m')}–{dt_fim.strftime('%d/%m/%y')}",
            "data_inicio": dt_ini.strftime("%d/%m/%Y"),
            "data_fim":    dt_fim.strftime("%d/%m/%Y"),
            "atualizado":  datetime.now().strftime("%d/%m/%Y · %H:%M"),
        },
        "header": {
            "eyebrow": "Painel · Onboarding",
            "title":   "Safras",
            "lede":    "Funil diário de conversão por safra de cadastro — FTD (D0 a D7), segundo depósito (STD) em 7 dias e KYC.",
            "base_analise": "Data de Cadastro",
            "comparativo":  "Semana anterior",
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
        "resumo": {
            "cadastros":    fmt_int(tot["cadastros"]),
            "pct_d0_d7":    fmt_pct(pct_d0_7_tot) + "%",
            "ticket_medio": fmt_brl(ticket_tot),
            "pct_std_7d":   fmt_pct(pct_std_tot) + "%",
            "pct_kyc":      fmt_pct(pct_kyc_tot) + "%",
        },
        "funil": funil,
        "tabelas": {
            "dia":    rows_to_payload(d_dia),
            "semana": rows_to_payload(d_semana),
            "mes":    rows_to_payload(d_mes),
        },
    }


# ── Render ────────────────────────────────────────────────────────────────────
with st.spinner("Carregando safras..."):
    payload = build_payload(ini_str, fim_str)

template = load_template("dashboard_safras.html")
html = template.replace("__EXA_DATA_JSON__", json.dumps(payload, ensure_ascii=False))
html = html.replace("</head>", _EMBED_OVERRIDES)
components.html(html, height=1500, scrolling=False)
