import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from core.databricks_client import execute_query

st.set_page_config(page_title="Onboarding", page_icon="📈", layout="wide")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .main { background-color: #f0f4f8; }
  .kpi-card {
    background: white;
    border: 1.5px solid #3b82f6;
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
  }
  .kpi-label { font-size: 11px; font-weight: 700; color: #6b7280; letter-spacing: 1px; text-transform: uppercase; }
  .kpi-value { font-size: 28px; font-weight: 800; color: #111827; margin: 6px 0 4px; }
  .kpi-delta { font-size: 12px; color: #16a34a; font-weight: 600; }
  .kpi-sub   { font-size: 11px; color: #6b7280; }
  .section-title { font-size: 13px; font-weight: 700; color: #1d4ed8; letter-spacing: 0.5px; border-left: 3px solid #1d4ed8; padding-left: 8px; margin-bottom: 12px; }
  .block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)


# ── Queries ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_kpis():
    q = """
    WITH mes_atual AS (
      SELECT
        COUNT(*) AS cadastros,
        SUM(CASE WHEN core_kyc_status IN ('approved','APPROVED','verified','VERIFIED','Approved') THEN 1 ELSE 0 END) AS kyc
      FROM workspace.default.v_users_summary
      WHERE core_registration_date >= DATE_TRUNC('month', CURRENT_DATE())
    ),
    mes_anterior AS (
      SELECT COUNT(*) AS cadastros_ant
      FROM workspace.default.v_users_summary
      WHERE core_registration_date >= DATE_TRUNC('month', DATEADD(MONTH, -1, CURRENT_DATE()))
        AND core_registration_date <  DATE_TRUNC('month', CURRENT_DATE())
    ),
    ftd AS (
      SELECT COUNT(DISTINCT user_ext_id) AS ftds
      FROM workspace.default.v_deposits_summary
      WHERE dt_finalized >= DATE_TRUNC('month', CURRENT_DATE())
    ),
    ftd_ant AS (
      SELECT COUNT(DISTINCT user_ext_id) AS ftds_ant
      FROM workspace.default.v_deposits_summary
      WHERE dt_finalized >= DATE_TRUNC('month', DATEADD(MONTH, -1, CURRENT_DATE()))
        AND dt_finalized <  DATE_TRUNC('month', CURRENT_DATE())
    ),
    fts AS (
      SELECT COUNT(DISTINCT user_ext_id) AS fts
      FROM workspace.default.v_sports_bets
      WHERE dt_update >= DATE_TRUNC('month', CURRENT_DATE())
    )
    SELECT
      a.cadastros, b.cadastros_ant,
      c.ftds, d.ftds_ant,
      a.kyc,
      e.fts
    FROM mes_atual a, mes_anterior b, ftd c, ftd_ant d, fts e
    """
    return execute_query(q)


@st.cache_data(ttl=300)
def load_evolucao():
    q = """
    SELECT
      DATE_TRUNC('month', u.core_registration_date) AS mes,
      COUNT(*)                                        AS cadastros,
      COUNT(DISTINCT d.user_ext_id)                  AS ftds
    FROM workspace.default.v_users_summary u
    LEFT JOIN workspace.default.v_deposits_summary d
      ON u.user_ext_id = d.user_ext_id
      AND DATE_TRUNC('month', d.dt_finalized) = DATE_TRUNC('month', u.core_registration_date)
    WHERE u.core_registration_date >= DATEADD(MONTH, -4, CURRENT_DATE())
    GROUP BY 1
    ORDER BY 1
    """
    return execute_query(q)


@st.cache_data(ttl=300)
def load_canal():
    q = """
    SELECT
      CASE
        WHEN core_affiliate_id IS NOT NULL AND core_affiliate_id > 0 THEN 'Afiliados'
        WHEN platform = 'mobile' THEN 'Mobile Orgânico'
        ELSE 'Orgânico'
      END AS canal,
      COUNT(*)                         AS cadastros,
      SUM(CASE WHEN core_kyc_status IN ('approved','APPROVED','Approved') THEN 1 ELSE 0 END) AS kyc
    FROM workspace.default.v_users_summary
    WHERE core_registration_date >= DATE_TRUNC('month', CURRENT_DATE())
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT 10
    """
    df = execute_query(q)
    return df


@st.cache_data(ttl=300)
def load_funil():
    q = """
    SELECT
      COUNT(DISTINCT u.user_ext_id)   AS cadastros,
      COUNT(DISTINCT d.user_ext_id)   AS ftd,
      COUNT(DISTINCT CASE WHEN u.core_kyc_status IN ('approved','APPROVED','Approved') THEN u.user_ext_id END) AS kyc,
      COUNT(DISTINCT s.user_ext_id)   AS fts
    FROM workspace.default.v_users_summary u
    LEFT JOIN workspace.default.v_deposits_summary d ON u.user_ext_id = d.user_ext_id
    LEFT JOIN workspace.default.v_sports_bets s      ON u.user_ext_id = s.user_ext_id
    WHERE u.core_registration_date >= DATE_TRUNC('month', CURRENT_DATE())
    """
    return execute_query(q)


# ── Header ────────────────────────────────────────────────────────────────────
col_title, col_ts = st.columns([4, 1])
with col_title:
    st.markdown("## Onboarding")
    st.caption("Aquisição, ativação e velocidade de jornada")
with col_ts:
    st.markdown(f"<div style='text-align:right;padding-top:18px;font-size:12px;color:#6b7280'>● Atualizado {datetime.now().strftime('%d/%m/%Y — %H:%M')}</div>", unsafe_allow_html=True)

st.markdown("---")

# ── KPI Cards ─────────────────────────────────────────────────────────────────
with st.spinner("Carregando indicadores..."):
    try:
        kpi = load_kpis().iloc[0]
        cadastros     = int(kpi["cadastros"])
        cadastros_ant = int(kpi["cadastros_ant"]) if kpi["cadastros_ant"] else 1
        ftds          = int(kpi["ftds"])
        ftds_ant      = int(kpi["ftds_ant"]) if kpi["ftds_ant"] else 1
        kyc           = int(kpi["kyc"])
        fts           = int(kpi["fts"])

        delta_cad  = ((cadastros - cadastros_ant) / max(cadastros_ant, 1)) * 100
        delta_ftd  = ((ftds - ftds_ant) / max(ftds_ant, 1)) * 100
        conv_ftd   = (ftds / max(cadastros, 1)) * 100
        conv_kyc   = (kyc  / max(ftds, 1)) * 100
        conv_fts   = (fts  / max(ftds, 1)) * 100

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        cards = [
            (c1, "CADASTROS",     f"{cadastros:,}",   f"▲ {delta_cad:.1f}% vs mês ant.", ""),
            (c2, "FTDS",          f"{ftds:,}",         f"▲ {delta_ftd:.1f}% vs mês ant.", ""),
            (c3, "KYC APROVADOS", f"{kyc:,}",          f"▲ {conv_kyc:.0f}% dos FTDs",     ""),
            (c4, "FTS",           f"{fts:,}",          f"▲ {conv_fts:.0f}% dos FTDs",     ""),
            (c5, "CONV. FTD",     f"{conv_ftd:.1f}%",  "Cadastro → FTD",                  ""),
            (c6, "CONV. FTS",     f"{conv_fts:.1f}%",  "FTD → FTS",                       ""),
        ]
        for col, label, value, delta, sub in cards:
            with col:
                st.markdown(f"""
                <div class="kpi-card">
                  <div class="kpi-label">{label}</div>
                  <div class="kpi-value">{value}</div>
                  <div class="kpi-delta">{delta}</div>
                  <div class="kpi-sub">{sub}</div>
                </div>""", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erro ao carregar KPIs: {e}")
        cadastros = ftds = kyc = fts = 0

st.markdown("<br>", unsafe_allow_html=True)

# ── Funil + Evolução ──────────────────────────────────────────────────────────
col_funil, col_evol = st.columns([1, 1], gap="large")

with col_funil:
    st.markdown('<div class="section-title">FUNIL DE ATIVAÇÃO</div>', unsafe_allow_html=True)
    try:
        f = load_funil().iloc[0]
        cad_f = int(f["cadastros"])
        ftd_f = int(f["ftd"])
        kyc_f = int(f["kyc"])
        fts_f = int(f["fts"])

        funil_data = pd.DataFrame({
            "Etapa":  ["Cadastros", "FTD", "KYC", "FTS"],
            "Total":  [cad_f, ftd_f, kyc_f, fts_f],
            "Pct":    [100, (ftd_f/max(cad_f,1))*100, (kyc_f/max(cad_f,1))*100, (fts_f/max(cad_f,1))*100],
            "Conv":   ["100%",
                       f"{(ftd_f/max(cad_f,1))*100:.1f}% conv.",
                       f"{(kyc_f/max(ftd_f,1))*100:.1f}% conv.",
                       f"{(fts_f/max(ftd_f,1))*100:.1f}% conv."],
            "Cor":    ["#1d4ed8", "#3b82f6", "#34d399", "#10b981"],
        })

        fig_funil = go.Figure()
        for _, row in funil_data.iterrows():
            fig_funil.add_trace(go.Bar(
                y=[row["Etapa"]], x=[row["Pct"]],
                orientation="h",
                marker_color=row["Cor"],
                text=f'  {row["Total"]:,}   {row["Conv"]}',
                textposition="inside",
                insidetextanchor="start",
                textfont=dict(color="white", size=12),
                showlegend=False,
                name=row["Etapa"],
            ))

        fig_funil.update_layout(
            height=260, margin=dict(l=0, r=10, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(range=[0, 115], showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, tickfont=dict(size=12)),
            barmode="overlay",
        )
        st.plotly_chart(fig_funil, use_container_width=True)
    except Exception as e:
        st.error(f"Erro no funil: {e}")

with col_evol:
    st.markdown('<div class="section-title">EVOLUÇÃO — CADASTROS & FTDS</div>', unsafe_allow_html=True)
    try:
        evol = load_evolucao()
        evol["mes_label"] = pd.to_datetime(evol["mes"]).dt.strftime("%b/%y")

        fig_evol = go.Figure()
        fig_evol.add_trace(go.Bar(
            x=evol["mes_label"], y=evol["cadastros"],
            name="Cadastros", marker_color="rgba(59,130,246,0.25)",
            yaxis="y1",
        ))
        fig_evol.add_trace(go.Scatter(
            x=evol["mes_label"], y=evol["ftds"],
            name="FTDs", mode="lines+markers",
            line=dict(color="#1d4ed8", width=2),
            marker=dict(size=7, color="#1d4ed8"),
            yaxis="y1",
        ))
        fig_evol.update_layout(
            height=260, margin=dict(l=0, r=10, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        )
        st.plotly_chart(fig_evol, use_container_width=True)
    except Exception as e:
        st.error(f"Erro na evolução: {e}")

# ── Breakdown por Canal ───────────────────────────────────────────────────────
st.markdown('<div class="section-title">BREAKDOWN POR CANAL</div>', unsafe_allow_html=True)
try:
    canal_df = load_canal()
    if not canal_df.empty:
        canal_df["ftd"] = "-"
        canal_df["conv_ftd"] = (canal_df["kyc"] / canal_df["cadastros"] * 100).round(1).astype(str) + "%"
        canal_df = canal_df.rename(columns={
            "canal": "CANAL",
            "cadastros": "CADASTROS",
            "ftd": "FTD",
            "kyc": "KYC",
            "conv_ftd": "CONV. %",
        })
        st.dataframe(
            canal_df[["CANAL", "CADASTROS", "FTD", "KYC", "CONV. %"]],
            use_container_width=True,
            hide_index=True,
        )
except Exception as e:
    st.error(f"Erro no canal: {e}")
