import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from core.databricks_client import execute_query
from core.theme import inject_theme, page_header, kpi_card


# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt(n):
    return f"{int(n):,}" if pd.notna(n) else "0"

def pct(n, d):
    return f"{(n / max(d, 1) * 100):.1f}%"


# ── Filtros de Safra ──────────────────────────────────────────────────────────
page_header("Onboarding", "Aquisição, ativação e velocidade de jornada", "Onboarding")

with st.container():
    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns([2, 2, 3, 2])

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

    today = date.today()

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
            cols_date = st.columns(2)
            dt_ini = cols_date[0].date_input("De", value=today - timedelta(days=30), label_visibility="collapsed")
            dt_fim = cols_date[1].date_input("Até", value=today, label_visibility="collapsed")

    with f4:
        st.caption(f"📅 {dt_ini.strftime('%d/%m/%Y')} → {dt_fim.strftime('%d/%m/%Y')}")
        st.caption(f"Base: **{base_safra}**")

    st.markdown("</div>", unsafe_allow_html=True)

# coluna de data conforme base da safra
DATE_COL_USER = "core_registration_date"
DATE_COL_DEP  = "dt_finalized"
date_col = DATE_COL_USER if base_safra == "Cadastro" else DATE_COL_DEP


# ── Queries ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_kpis(ini: str, fim: str, base: str):
    # cohort_table/col define quem entra na safra
    if base == "Cadastro":
        cohort_sql = f"""
          SELECT DISTINCT user_ext_id
          FROM workspace.default.v_users_summary
          WHERE core_registration_date BETWEEN '{ini}' AND '{fim} 23:59:59'"""
    else:
        cohort_sql = f"""
          SELECT DISTINCT user_ext_id
          FROM workspace.default.v_deposits_summary
          WHERE dt_finalized BETWEEN '{ini}' AND '{fim} 23:59:59'"""

    q = f"""
    WITH cohort AS ({cohort_sql}),
    cad AS (
      SELECT COUNT(DISTINCT u.user_ext_id) AS total
      FROM workspace.default.v_users_summary u
      INNER JOIN cohort c ON u.user_ext_id = c.user_ext_id
    ),
    ftd AS (
      SELECT COUNT(DISTINCT d.user_ext_id) AS total
      FROM workspace.default.v_deposits_summary d
      INNER JOIN cohort c ON d.user_ext_id = c.user_ext_id
    ),
    kyc AS (
      SELECT COUNT(DISTINCT u.user_ext_id) AS total
      FROM workspace.default.v_users_summary u
      INNER JOIN cohort c ON u.user_ext_id = c.user_ext_id
      WHERE u.core_kyc_status IN ('approved','APPROVED','Approved','verified','VERIFIED')
    ),
    fts AS (
      SELECT COUNT(DISTINCT s.user_ext_id) AS total
      FROM workspace.default.v_sports_bets s
      INNER JOIN cohort c ON s.user_ext_id = c.user_ext_id
    ),
    churn_ftd AS (
      SELECT COUNT(DISTINCT c.user_ext_id) AS sem_deposito
      FROM cohort c
      LEFT JOIN workspace.default.v_deposits_summary d ON c.user_ext_id = d.user_ext_id
      WHERE d.user_ext_id IS NULL
    ),
    churn_fts AS (
      SELECT COUNT(DISTINCT d.user_ext_id) AS sem_sports
      FROM workspace.default.v_deposits_summary d
      INNER JOIN cohort c ON d.user_ext_id = c.user_ext_id
      LEFT JOIN workspace.default.v_sports_bets s ON d.user_ext_id = s.user_ext_id
      WHERE s.user_ext_id IS NULL
    )
    SELECT cad.total AS cadastros, ftd.total AS ftds, kyc.total AS kyc,
           fts.total AS fts, churn_ftd.sem_deposito AS churn_ftd_n,
           churn_fts.sem_sports AS churn_fts_n
    FROM cad, ftd, kyc, fts, churn_ftd, churn_fts
    """
    return execute_query(q)


@st.cache_data(ttl=300, show_spinner=False)
def load_evolucao(granular: str, ini: str, fim: str):
    trunc = {"Ano": "MONTH", "Mês": "MONTH", "Semana": "WEEK", "Dia": "DAY", "Data aberta": "MONTH"}[granular]
    q = f"""
    SELECT
      DATE_TRUNC('{trunc}', u.core_registration_date) AS periodo,
      COUNT(DISTINCT u.user_ext_id)                   AS cadastros,
      COUNT(DISTINCT d.user_ext_id)                   AS ftd,
      COUNT(DISTINCT CASE WHEN u.core_kyc_status IN ('approved','APPROVED','Approved')
                          THEN u.user_ext_id END)      AS kyc,
      COUNT(DISTINCT s.user_ext_id)                   AS fts
    FROM workspace.default.v_users_summary u
    LEFT JOIN workspace.default.v_deposits_summary d ON u.user_ext_id = d.user_ext_id
    LEFT JOIN workspace.default.v_sports_bets      s ON u.user_ext_id = s.user_ext_id
    WHERE u.core_registration_date BETWEEN '{ini}' AND '{fim} 23:59:59'
    GROUP BY 1 ORDER BY 1
    """
    return execute_query(q)


@st.cache_data(ttl=300, show_spinner=False)
def load_funil(ini: str, fim: str, base: str):
    if base == "Cadastro":
        where = f"u.core_registration_date BETWEEN '{ini}' AND '{fim} 23:59:59'"
    else:
        where = f"d.dt_finalized BETWEEN '{ini}' AND '{fim} 23:59:59'"
    q = f"""
    SELECT
      COUNT(DISTINCT u.user_ext_id)  AS cadastros,
      COUNT(DISTINCT d.user_ext_id)  AS ftd,
      COUNT(DISTINCT CASE WHEN u.core_kyc_status IN ('approved','APPROVED','Approved')
                          THEN u.user_ext_id END) AS kyc,
      COUNT(DISTINCT s.user_ext_id)  AS fts
    FROM workspace.default.v_users_summary u
    LEFT JOIN workspace.default.v_deposits_summary d ON u.user_ext_id = d.user_ext_id
    LEFT JOIN workspace.default.v_sports_bets      s ON u.user_ext_id = s.user_ext_id
    WHERE {where}
    """
    return execute_query(q)


@st.cache_data(ttl=300, show_spinner=False)
def load_canal(ini: str, fim: str, base: str):
    if base == "Cadastro":
        where = f"u.core_registration_date BETWEEN '{ini}' AND '{fim} 23:59:59'"
    else:
        where = f"d.dt_finalized BETWEEN '{ini}' AND '{fim} 23:59:59'"
    q = f"""
    SELECT
      CASE
        WHEN u.core_affiliate_id IS NOT NULL AND u.core_affiliate_id > 0 THEN 'Afiliados'
        WHEN u.platform = 'mobile' THEN 'Mobile Orgânico'
        ELSE 'Orgânico'
      END AS canal,
      COUNT(DISTINCT u.user_ext_id) AS cadastros,
      COUNT(DISTINCT d.user_ext_id) AS ftd,
      COUNT(DISTINCT CASE WHEN u.core_kyc_status IN ('approved','APPROVED','Approved')
                          THEN u.user_ext_id END) AS kyc
    FROM workspace.default.v_users_summary u
    LEFT JOIN workspace.default.v_deposits_summary d ON u.user_ext_id = d.user_ext_id
    WHERE {where}
    GROUP BY 1 ORDER BY 2 DESC
    LIMIT 10
    """
    return execute_query(q)


ini_str = str(dt_ini)
fim_str = str(dt_fim)

# ── KPI Cards ─────────────────────────────────────────────────────────────────
with st.spinner("Carregando indicadores..."):
    try:
        kpi = load_kpis(ini_str, fim_str, base_safra).iloc[0]
        cadastros   = int(kpi["cadastros"]   or 0)
        ftds        = int(kpi["ftds"]        or 0)
        kyc         = int(kpi["kyc"]         or 0)
        fts         = int(kpi["fts"]         or 0)
        churn_ftd_n = int(kpi["churn_ftd_n"] or 0)
        churn_fts_n = int(kpi["churn_fts_n"] or 0)

        conv_ftd     = ftds / max(cadastros, 1) * 100
        conv_kyc     = kyc  / max(ftds, 1)      * 100
        conv_fts     = fts  / max(ftds, 1)      * 100
        churn_ftd_p  = churn_ftd_n / max(cadastros, 1) * 100
        churn_fts_p  = churn_fts_n / max(ftds, 1)     * 100

        # Linha 1 — indicadores de ativação
        st.markdown('<div class="section-title">INDICADORES DE ATIVAÇÃO</div>', unsafe_allow_html=True)
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        ativ = [
            (c1, "CADASTROS",       fmt(cadastros),     f"{conv_ftd:.1f}% conv. FTD",    "users",      "up"),
            (c2, "FTDS",            fmt(ftds),           f"{conv_ftd:.1f}% dos cadastros", "dollar",     "up"),
            (c3, "KYC APROVADOS",   fmt(kyc),             f"{conv_kyc:.0f}% dos FTDs",    "shield",     "up"),
            (c4, "FTS",             fmt(fts),             f"{conv_fts:.0f}% dos FTDs",    "zap",        "up"),
            (c5, "CONV. CAD → FTD", f"{conv_ftd:.1f}%",  "conversão acumulada",          "percent",    "neutral"),
            (c6, "CONV. FTD → FTS", f"{conv_fts:.1f}%",  "conversão acumulada",          "percent",    "neutral"),
        ]
        for col, label, value, sub, icon, sub_type in ativ:
            with col:
                st.markdown(kpi_card(label, value, sub, icon, sub_type=sub_type), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Linha 2 — indicadores de churn
        st.markdown('<div class="section-title-red">INDICADORES DE CHURN</div>', unsafe_allow_html=True)
        ch1, ch2, ch3, ch4 = st.columns(4)

        with ch1:
            st.markdown(kpi_card("CHURN FTD (qtd)", fmt(churn_ftd_n), "Cadastros sem 1º depósito", "trending-down", "churn", "churn"), unsafe_allow_html=True)
        with ch2:
            st.markdown(kpi_card("CHURN FTD (%)", f"{churn_ftd_p:.1f}%", f"{churn_ftd_n:,} de {cadastros:,} cadastros", "percent", "churn", "churn"), unsafe_allow_html=True)
        with ch3:
            st.markdown(kpi_card("CHURN FTS (qtd)", fmt(churn_fts_n), "FTDs sem aposta esportiva", "trending-down", "churn", "churn"), unsafe_allow_html=True)
        with ch4:
            st.markdown(kpi_card("CHURN FTS (%)", f"{churn_fts_p:.1f}%", f"{churn_fts_n:,} de {ftds:,} FTDs", "percent", "churn", "churn"), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erro ao carregar KPIs: {e}")
        cadastros = ftds = kyc = fts = churn_ftd_n = churn_fts_n = 0
        conv_ftd = conv_fts = churn_ftd_p = churn_fts_p = 0.0

st.markdown("<br>", unsafe_allow_html=True)

# ── Funil + Evolução ──────────────────────────────────────────────────────────
col_funil, col_evol = st.columns([1, 1], gap="large")

with col_funil:
    st.markdown('<div class="section-title">FUNIL DE ATIVAÇÃO</div>', unsafe_allow_html=True)
    try:
        f = load_funil(ini_str, fim_str, base_safra).iloc[0]
        cad_f = int(f["cadastros"] or 0)
        ftd_f = int(f["ftd"]       or 0)
        kyc_f = int(f["kyc"]       or 0)
        fts_f = int(f["fts"]       or 0)

        steps = [
            ("Cadastros", cad_f, 100.0,                              "#1D3186"),
            ("FTD",       ftd_f, ftd_f / max(cad_f, 1) * 100,       "#2563EB"),
            ("KYC",       kyc_f, kyc_f / max(cad_f, 1) * 100,       "#60A5FA"),
            ("FTS",       fts_f, fts_f / max(cad_f, 1) * 100,       "#93C5FD"),
        ]
        conv_labels = [
            "100%",
            f"{ftd_f/max(cad_f,1)*100:.1f}% conv.",
            f"{kyc_f/max(ftd_f,1)*100:.1f}% conv.",
            f"{fts_f/max(ftd_f,1)*100:.1f}% conv.",
        ]

        fig_funil = go.Figure()
        for i, (label, total, pct_val, cor) in enumerate(steps):
            fig_funil.add_trace(go.Bar(
                y=[label], x=[pct_val], orientation="h",
                marker_color=cor,
                text=f"  {total:,}   {conv_labels[i]}",
                textposition="inside", insidetextanchor="start",
                textfont=dict(color="white", size=12),
                showlegend=False,
            ))

        fig_funil.update_layout(
            height=240, margin=dict(l=0, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(range=[0, 115], showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, tickfont=dict(size=13)),
        )
        st.plotly_chart(fig_funil, use_container_width=True)
    except Exception as e:
        st.error(f"Erro no funil: {e}")

with col_evol:
    st.markdown('<div class="section-title">EVOLUÇÃO — CADASTROS & FTDS</div>', unsafe_allow_html=True)
    try:
        evol = load_evolucao(safra_tipo, ini_str, fim_str)
        evol["periodo"] = pd.to_datetime(evol["periodo"])
        fmt_map = {"Ano": "%b/%y", "Dia": "%d/%m", "Semana": "%d/%m", "Mês": "%b/%y", "Data aberta": "%b/%y"}
        evol["label"] = evol["periodo"].dt.strftime(fmt_map[safra_tipo])

        fig_evol = go.Figure()
        fig_evol.add_trace(go.Bar(
            x=evol["label"], y=evol["cadastros"],
            name="Cadastros", marker_color="rgba(37,99,235,0.18)",
        ))
        fig_evol.add_trace(go.Scatter(
            x=evol["label"], y=evol["ftd"],
            name="FTDs", mode="lines+markers",
            line=dict(color="#2563EB", width=2), marker=dict(size=7),
        ))
        fig_evol.update_layout(
            height=240, margin=dict(l=0, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#DBEAFE"),
        )
        st.plotly_chart(fig_evol, use_container_width=True)
    except Exception as e:
        st.error(f"Erro na evolução: {e}")

# ── Gráfico Churn ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-title-red">EVOLUÇÃO DO CHURN — FTD & FTS</div>', unsafe_allow_html=True)
try:
    evol_ch = load_evolucao(safra_tipo, ini_str, fim_str)
    evol_ch["periodo"] = pd.to_datetime(evol_ch["periodo"])
    fmt_map = {"Ano": "%b/%y", "Dia": "%d/%m", "Semana": "%d/%m", "Mês": "%b/%y", "Data aberta": "%b/%y"}
    evol_ch["label"] = evol_ch["periodo"].dt.strftime(fmt_map[safra_tipo])
    evol_ch["churn_ftd_pct"] = (1 - evol_ch["ftd"] / evol_ch["cadastros"].clip(lower=1)) * 100
    evol_ch["churn_fts_pct"] = (1 - evol_ch["fts"] / evol_ch["ftd"].clip(lower=1)) * 100

    fig_churn = go.Figure()
    fig_churn.add_trace(go.Scatter(
        x=evol_ch["label"], y=evol_ch["churn_ftd_pct"].round(1),
        name="Churn FTD (%)", mode="lines+markers",
        line=dict(color="#d4544a", width=2), marker=dict(size=7),
        fill="tozeroy", fillcolor="rgba(212,84,74,0.08)",
    ))
    fig_churn.add_trace(go.Scatter(
        x=evol_ch["label"], y=evol_ch["churn_fts_pct"].round(1),
        name="Churn FTS (%)", mode="lines+markers",
        line=dict(color="#d4982a", width=2, dash="dot"), marker=dict(size=7),
        fill="tozeroy", fillcolor="rgba(212,152,42,0.05)",
    ))
    fig_churn.update_layout(
        height=280, margin=dict(l=0, r=10, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#DBEAFE", ticksuffix="%"),
        hovermode="x unified",
    )
    st.plotly_chart(fig_churn, use_container_width=True)
except Exception as e:
    st.error(f"Erro no gráfico de churn: {e}")

st.markdown("<br>", unsafe_allow_html=True)

# ── Breakdown por Canal ───────────────────────────────────────────────────────
st.markdown('<div class="section-title">BREAKDOWN POR CANAL</div>', unsafe_allow_html=True)
try:
    canal_df = load_canal(ini_str, fim_str, base_safra)
    if not canal_df.empty:
        canal_df["conv_ftd_%"] = (canal_df["ftd"] / canal_df["cadastros"].clip(lower=1) * 100).round(1).astype(str) + "%"
        canal_df["churn_%"]    = ((1 - canal_df["ftd"] / canal_df["cadastros"].clip(lower=1)) * 100).round(1).astype(str) + "%"
        st.dataframe(
            canal_df.rename(columns={"canal": "CANAL", "cadastros": "CADASTROS", "ftd": "FTD", "kyc": "KYC",
                                     "conv_ftd_%": "CONV. FTD", "churn_%": "CHURN FTD"}
            )[["CANAL", "CADASTROS", "FTD", "KYC", "CONV. FTD", "CHURN FTD"]],
            use_container_width=True,
            hide_index=True,
        )
except Exception as e:
    st.error(f"Erro no canal: {e}")
