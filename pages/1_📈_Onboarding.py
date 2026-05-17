import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime, timedelta, date
from pathlib import Path
from core.databricks_client import execute_query
from core.theme import inject_theme


inject_theme()


# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt_int(n) -> str:
    return f"{int(n or 0):,}".replace(",", ".")

def fmt_pct(n, d=1) -> str:
    return f"{float(n or 0):.{d}f}".replace(".", ",")

def delta_dir(current, prev):
    if prev == 0:
        return "flat"
    return "up" if current >= prev else "down"


# ── Template HTML ─────────────────────────────────────────────────────────────
@st.cache_resource
def _read_template() -> str:
    p = Path(__file__).parent.parent / "static" / "dashboard.html"
    return p.read_text(encoding="utf-8")


# ── Filtros ───────────────────────────────────────────────────────────────────
with st.container():
    st.markdown('''<div class="exa-topbar-row">
      <span class="exa-topbar-pulse"></span>
      <span class="exa-topbar-brand">EXA &middot; Analytics</span>
      <span class="exa-topbar-sep"></span>
      <span class="exa-topbar-live-badge"><span></span>Live</span>
    </div>''', unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns([2, 2, 3, 2])
    today = date.today()

    with f1:
        safra_tipo = st.selectbox(
            "Granularidade",
            ["Ano", "Mês", "Semana", "Dia", "Data aberta"],
            label_visibility="collapsed",
        )
    with f2:
        base_safra = st.selectbox(
            "Base da safra",
            ["Cadastro", "1º Depósito"],
            label_visibility="collapsed",
        )
    with f3:
        if safra_tipo == "Ano":
            anos = list(range(today.year, today.year - 5, -1))
            ano_sel = st.selectbox("Ano", anos, label_visibility="collapsed")
            dt_ini = date(ano_sel, 1, 1)
            dt_fim = date(ano_sel, 12, 31) if ano_sel < today.year else today
        elif safra_tipo == "Mês":
            meses = pd.date_range(end=today, periods=24, freq="MS").strftime("%Y-%m").tolist()[::-1]
            mes_sel = st.selectbox("Mês", meses, label_visibility="collapsed")
            dt_ini = datetime.strptime(mes_sel, "%Y-%m").date()
            dt_fim = (dt_ini.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        elif safra_tipo == "Semana":
            semana_ini = today - timedelta(days=today.weekday())
            data_sel = st.date_input("Semana", value=semana_ini, label_visibility="collapsed")
            dt_ini = data_sel - timedelta(days=data_sel.weekday())
            dt_fim = dt_ini + timedelta(days=6)
        elif safra_tipo == "Dia":
            data_sel = st.date_input("Dia", value=today, label_visibility="collapsed")
            dt_ini = dt_fim = data_sel
        else:
            c1, c2 = st.columns(2)
            dt_ini = c1.date_input("De", value=today - timedelta(days=30), label_visibility="collapsed")
            dt_fim = c2.date_input("Até", value=today, label_visibility="collapsed")
    with f4:
        st.caption(f"📅 {dt_ini.strftime('%d/%m/%Y')} → {dt_fim.strftime('%d/%m/%Y')}")
        st.caption(f"Base: **{base_safra}**")


ini_str = str(dt_ini)
fim_str = str(dt_fim)


# ── Queries ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_kpis(ini: str, fim: str, base: str):
    if base == "Cadastro":
        cohort_sql = f"""
          SELECT DISTINCT user_ext_id FROM workspace.default.v_users_summary
          WHERE core_registration_date BETWEEN '{ini}' AND '{fim} 23:59:59'"""
    else:
        cohort_sql = f"""
          SELECT DISTINCT user_ext_id FROM workspace.default.v_deposits_summary
          WHERE dt_finalized BETWEEN '{ini}' AND '{fim} 23:59:59'"""

    q = f"""
    WITH cohort AS ({cohort_sql}),
    cad  AS (SELECT COUNT(DISTINCT u.user_ext_id) AS total FROM workspace.default.v_users_summary u     INNER JOIN cohort c ON u.user_ext_id = c.user_ext_id),
    ftd  AS (SELECT COUNT(DISTINCT d.user_ext_id) AS total FROM workspace.default.v_deposits_summary d INNER JOIN cohort c ON d.user_ext_id = c.user_ext_id),
    kyc  AS (SELECT COUNT(DISTINCT u.user_ext_id) AS total FROM workspace.default.v_users_summary u     INNER JOIN cohort c ON u.user_ext_id = c.user_ext_id WHERE u.core_kyc_status IN ('approved','APPROVED','Approved','verified','VERIFIED')),
    fts  AS (SELECT COUNT(DISTINCT s.user_ext_id) AS total FROM workspace.default.v_sports_bets s       INNER JOIN cohort c ON s.user_ext_id = c.user_ext_id)
    SELECT cad.total AS cadastros, ftd.total AS ftds, kyc.total AS kyc, fts.total AS fts
    FROM cad, ftd, kyc, fts
    """
    return execute_query(q)


@st.cache_data(ttl=300, show_spinner=False)
def load_evolucao(ini: str, fim: str):
    q = f"""
    SELECT
      DATE_TRUNC('MONTH', u.core_registration_date) AS periodo,
      COUNT(DISTINCT u.user_ext_id)  AS cadastros,
      COUNT(DISTINCT d.user_ext_id)  AS ftd
    FROM workspace.default.v_users_summary u
    LEFT JOIN workspace.default.v_deposits_summary d ON u.user_ext_id = d.user_ext_id
    WHERE u.core_registration_date BETWEEN '{ini}' AND '{fim} 23:59:59'
    GROUP BY 1 ORDER BY 1
    """
    return execute_query(q)


# ── Montar payload ────────────────────────────────────────────────────────────
def build_payload(ini: str, fim: str, base: str, granular: str) -> dict:
    try:
        row = load_kpis(ini, fim, base).iloc[0]
        cadastros = int(row["cadastros"] or 0)
        ftds      = int(row["ftds"]      or 0)
        kyc       = int(row["kyc"]       or 0)
        fts       = int(row["fts"]       or 0)
    except Exception:
        cadastros = ftds = kyc = fts = 0

    conv_cad_ftd = ftds / max(cadastros, 1)
    conv_ftd_fts = fts  / max(ftds, 1)
    churn_ftd_q  = cadastros - ftds
    churn_ftd_p  = churn_ftd_q / max(cadastros, 1)
    churn_fts_q  = ftds - fts
    churn_fts_p  = churn_fts_q / max(ftds, 1)

    # Evolução mensal para o gráfico
    months, bars, line = [], [], []
    try:
        evol = load_evolucao(ini, fim)
        evol["periodo"] = pd.to_datetime(evol["periodo"])
        for _, r in evol.iterrows():
            months.append(r["periodo"].strftime("%b/%y"))
            bars.append(int(r["cadastros"] or 0))
            line.append(int(r["ftd"] or 0))
    except Exception:
        pass

    periodo_label = {
        "Ano": str(dt_ini.year),
        "Mês": dt_ini.strftime("%b/%y"),
    }.get(granular, f"{dt_ini.strftime('%d/%m')}–{dt_fim.strftime('%d/%m/%y')}")

    return {
        "filters": {
            "granularidade": granular,
            "base":          base,
            "periodo":       periodo_label,
            "data_inicio":   dt_ini.strftime("%d/%m/%Y"),
            "data_fim":      dt_fim.strftime("%d/%m/%Y"),
            "atualizado":    datetime.now().strftime("%d/%m/%Y · %H:%M"),
        },
        "header": {
            "eyebrow":       "Painel · Aquisição",
            "title":         "Onboarding",
            "lede":          "Aquisição, ativação e velocidade de jornada — do cadastro à primeira aposta esportiva.",
            "base_analise":  base,
            "comparativo":   "Período anterior",
        },
        "user": {"name": "Analytics", "role": "EXA", "initials": "EX"},
        "nav": [
            {"key": "onboarding",  "label": "Onboarding",  "icon": "funnel",     "active": True},
            {"key": "retencao",    "label": "Retenção",     "icon": "retention"},
            {"key": "performance", "label": "Performance",  "icon": "perf"},
            {"key": "chat",        "label": "Chat",         "icon": "chat"},
        ],
        "ativacao": [
            {"key": "cadastros", "label": "Cadastros",       "value": fmt_int(cadastros),         "sub": f"{fmt_pct(conv_cad_ftd * 100)}% de conv. p/ FTD", "delta": {"dir": "up",   "v": ""},  "spark": [],  "color": "#2540ea"},
            {"key": "ftds",      "label": "FTDs",            "value": fmt_int(ftds),              "sub": f"{fmt_pct(conv_cad_ftd * 100)}% dos cadastros",   "delta": {"dir": "up",   "v": ""},  "spark": [],  "color": "#2540ea"},
            {"key": "kyc",       "label": "KYC Aprovados",   "value": fmt_int(kyc),               "sub": f"{fmt_pct(kyc / max(ftds,1) * 100)}% dos FTDs",   "delta": {"dir": "up",   "v": ""},  "spark": [],  "color": "#2540ea"},
            {"key": "fts",       "label": "FTS",             "value": fmt_int(fts),               "sub": f"{fmt_pct(conv_ftd_fts * 100)}% dos FTDs",        "delta": {"dir": "down", "v": ""},  "spark": [],  "color": "#d62a39"},
            {"key": "conv1",     "label": "Conv. CAD → FTD", "value": fmt_pct(conv_cad_ftd * 100),"unit": "%", "sub": "Conversão acumulada",                "delta": {"dir": "up",   "v": ""},  "spark": [],  "color": "#1f9d57"},
            {"key": "conv2",     "label": "Conv. FTD → FTS", "value": fmt_pct(conv_ftd_fts * 100),"unit": "%", "sub": "Conversão acumulada",                "delta": {"dir": "flat", "v": ""},  "spark": [],  "color": "#6b7280"},
        ],
        "churn": [
            {"key": "ch1", "label": "Churn FTD (QTD)", "value": fmt_int(churn_ftd_q),       "sub": "Cadastros sem 1º depósito",                                     "delta": {"dir": "up",   "v": ""}, "spark": []},
            {"key": "ch2", "label": "Churn FTD (%)",   "value": fmt_pct(churn_ftd_p * 100), "unit": "%", "sub": f"{fmt_int(churn_ftd_q)} de {fmt_int(cadastros)}", "delta": {"dir": "flat", "v": ""}, "spark": []},
            {"key": "ch3", "label": "Churn FTS (QTD)", "value": fmt_int(churn_fts_q),       "sub": "FTDs sem aposta esportiva",                                     "delta": {"dir": "up",   "v": ""}, "spark": []},
            {"key": "ch4", "label": "Churn FTS (%)",   "value": fmt_pct(churn_fts_p * 100), "unit": "%", "sub": f"{fmt_int(churn_fts_q)} de {fmt_int(ftds)}",      "delta": {"dir": "up",   "v": ""}, "spark": []},
        ],
        "funnel": {
            "title":    "Funil de Ativação",
            "subtitle": "Cadastro → KYC → Primeiro depósito → Primeira aposta esportiva",
            "stages": [
                {"name": "Cadastros",     "count": fmt_int(cadastros), "pct": 100.0,                              "conv": 100.0,                           "classN": "blue",   "from": None},
                {"name": "KYC Aprovados", "count": fmt_int(kyc),       "pct": round(kyc  / max(cadastros,1)*100,1),"conv": round(kyc  / max(cadastros,1)*100,1),"classN": "blue-2", "from": "Cadastros"},
                {"name": "FTD",           "count": fmt_int(ftds),      "pct": round(ftds / max(cadastros,1)*100,1),"conv": round(ftds / max(kyc,1)*100,1),       "classN": "blue-3", "from": "KYC"},
                {"name": "FTS",           "count": fmt_int(fts),       "pct": round(fts  / max(cadastros,1)*100,1),"conv": round(fts  / max(ftds,1)*100,1),       "classN": "blue-4", "from": "FTD"},
            ],
            "notes": [
                {"lbl": "Gargalo principal",    "prefix": "FTD → FTS", "suffix": f" ({fmt_pct(churn_fts_p*100)}% queda)", "bold": "prefix"},
                {"lbl": "Coorte de referência", "prefix": dt_ini.strftime("%d/%m") + " — ", "suffix": dt_fim.strftime("%d/%m/%Y"), "bold": "suffix"},
            ],
        },
        "chart": {
            "title":    "Evolução — Cadastros & FTDs",
            "subtitle": "Mensal",
            "months":   months or ["—"],
            "bars":     bars   or [0],
            "line":     line   or [0],
        },
    }


# ── Render ────────────────────────────────────────────────────────────────────
with st.spinner("Carregando dashboard..."):
    payload = build_payload(ini_str, fim_str, base_safra, safra_tipo)

template = _read_template()
html = template.replace("__EXA_DATA_JSON__", json.dumps(payload, ensure_ascii=False))
components.html(html, height=1480, scrolling=True)
