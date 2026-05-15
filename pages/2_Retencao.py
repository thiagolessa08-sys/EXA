import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from core.databricks_client import execute_query
from core.theme import inject_theme, page_header

st.set_page_config(page_title="Retenção", page_icon="🔄", layout="wide")
inject_theme()


def cell_class(val):
    if val is None: return "cell-null", "—"
    if val >= 99:   return "cell-100", f"{val:.0f}%"
    if val >= 85:   return "cell-85",  f"{val:.0f}%"
    if val >= 45:   return "cell-45",  f"{val:.0f}%"
    if val >= 30:   return "cell-30",  f"{val:.0f}%"
    if val >= 15:   return "cell-15",  f"{val:.0f}%"
    return "cell-low", f"{val:.0f}%"


# ── Header ────────────────────────────────────────────────────────────────────
page_header("Retenção", "Cohorts, recorrência e sobrevivência de usuários", "Retenção")

# ── Filtros ───────────────────────────────────────────────────────────────────
with st.container():
    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    f1, f1b, f2, f3, f4, f5, f6 = st.columns([2, 2, 2, 2, 2, 2, 2])

    today = date.today()

    with f1:
        safra_tipo = st.selectbox("Granularidade", ["Ano", "Mês", "Data aberta"], label_visibility="visible")

    with f1b:
        if safra_tipo == "Ano":
            anos = list(range(today.year, today.year - 5, -1))
            ano_sel = st.selectbox("Ano", anos, label_visibility="visible")
            dt_ini = date(ano_sel, 1, 1)
            dt_fim = date(ano_sel, 12, 31) if ano_sel < today.year else today
        elif safra_tipo == "Mês":
            meses = pd.date_range(end=today, periods=18, freq="MS").strftime("%Y-%m").tolist()[::-1]
            mes_sel = st.selectbox("Mês", meses, label_visibility="visible",
                                   format_func=lambda x: datetime.strptime(x, "%Y-%m").strftime("%b/%y"))
            dt_ini = datetime.strptime(mes_sel, "%Y-%m").date()
            dt_fim = (dt_ini.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        else:
            dt_ini = st.date_input("De", value=today - timedelta(days=30), label_visibility="visible")
            dt_fim = st.date_input("Até", value=today, label_visibility="visible")

    with f2:
        visao = st.selectbox("Visão", ["Semanal", "Quinzenal", "Mensal"], label_visibility="visible")

    with f3:
        canal_opt = st.selectbox("Canal", ["Total", "Afiliados", "Orgânico", "Mobile"], label_visibility="visible")

    with f4:
        produto_opt = st.selectbox("Produto", ["Total", "Casino", "Sports"], label_visibility="visible")

    with f5:
        base_ret = st.selectbox("Base", ["Cadastro", "1º Depósito"], label_visibility="visible")

    with f6:
        max_weeks = st.selectbox("Semanas", [4, 6, 8, 12], label_visibility="visible", index=1)

    st.markdown("</div>", unsafe_allow_html=True)

ini_str = str(dt_ini)
fim_str = str(dt_fim)

# filtro canal
canal_filter = ""
if canal_opt == "Afiliados":
    canal_filter = "AND u.core_affiliate_id IS NOT NULL AND u.core_affiliate_id > 0"
elif canal_opt == "Orgânico":
    canal_filter = "AND (u.core_affiliate_id IS NULL OR u.core_affiliate_id = 0)"
elif canal_opt == "Mobile":
    canal_filter = "AND u.platform = 'mobile'"

# filtro produto para atividade
if produto_opt == "Casino":
    activity_sql = f"SELECT user_ext_id, DATE_TRUNC('WEEK', dt) AS aw, SUM(bet_amount) AS stake FROM workspace.default.v_casino_bets GROUP BY 1,2"
elif produto_opt == "Sports":
    activity_sql = f"SELECT user_ext_id, DATE_TRUNC('WEEK', dt_update) AS aw, SUM(sport_last_bet_amount) AS stake FROM workspace.default.v_sports_bets GROUP BY 1,2"
else:
    activity_sql = f"""
    SELECT user_ext_id, DATE_TRUNC('WEEK', dt) AS aw, SUM(bet_amount) AS stake
    FROM workspace.default.v_casino_bets GROUP BY 1,2
    UNION ALL
    SELECT user_ext_id, DATE_TRUNC('WEEK', dt_update) AS aw, SUM(sport_last_bet_amount) AS stake
    FROM workspace.default.v_sports_bets GROUP BY 1,2"""

# granularidade do cohort — Ano sempre usa MONTH para ver os 12 meses
trunc_map = {"Semanal": "WEEK", "Quinzenal": "WEEK", "Mensal": "MONTH"}
cohort_trunc = "MONTH" if safra_tipo == "Ano" else trunc_map[visao]

if base_ret == "Cadastro":
    cohort_date = "u.core_registration_date"
else:
    cohort_date = "u.core_registration_date"  # fallback; idealmente seria primeira data de depósito


# ── Queries ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_cohort_matrix(ini: str, fim: str, trunc: str, act_sql: str, canal_f: str, n_weeks: int):
    q = f"""
    WITH cohort_users AS (
      SELECT u.user_ext_id,
             DATE_TRUNC('{trunc}', u.core_registration_date) AS cohort_week
      FROM workspace.default.v_users_summary u
      WHERE u.core_registration_date BETWEEN '{ini}' AND '{fim} 23:59:59'
        {canal_f}
    ),
    activity AS (
      SELECT user_ext_id, aw, SUM(stake) AS stake_sum
      FROM ({act_sql}) t
      GROUP BY 1, 2
    ),
    cohort_size AS (
      SELECT cohort_week, COUNT(DISTINCT user_ext_id) AS n_users
      FROM cohort_users GROUP BY 1
    ),
    joined AS (
      SELECT c.cohort_week,
             DATEDIFF(WEEK, c.cohort_week, a.aw) AS week_num,
             COUNT(DISTINCT a.user_ext_id)         AS retained,
             SUM(a.stake_sum)                       AS stake_ret
      FROM cohort_users c
      JOIN activity a ON c.user_ext_id = a.user_ext_id
      WHERE DATEDIFF(WEEK, c.cohort_week, a.aw) BETWEEN 0 AND {n_weeks}
      GROUP BY 1, 2
    )
    SELECT j.cohort_week, j.week_num, j.retained, j.stake_ret,
           s.n_users AS cohort_size,
           ROUND(j.retained * 100.0 / s.n_users, 1) AS retention_pct
    FROM joined j
    JOIN cohort_size s ON j.cohort_week = s.cohort_week
    ORDER BY 1, 2
    """
    return execute_query(q)


@st.cache_data(ttl=300, show_spinner=False)
def load_kpis_ret(ini: str, fim: str, act_sql: str, canal_f: str):
    q = f"""
    WITH cohort_users AS (
      SELECT u.user_ext_id,
             DATE_TRUNC('WEEK', u.core_registration_date) AS cohort_week
      FROM workspace.default.v_users_summary u
      WHERE u.core_registration_date BETWEEN '{ini}' AND '{fim} 23:59:59'
        {canal_f}
    ),
    activity AS (
      SELECT user_ext_id, aw, SUM(stake_sum) AS stake_sum
      FROM (SELECT user_ext_id, aw, SUM(stake) AS stake_sum FROM ({act_sql}) t GROUP BY 1,2) x
      GROUP BY 1, 2
    ),
    w0 AS (SELECT COUNT(DISTINCT user_ext_id) AS n FROM cohort_users),
    w1 AS (
      SELECT COUNT(DISTINCT c.user_ext_id) AS n, SUM(a.stake_sum) AS stake
      FROM cohort_users c JOIN activity a ON c.user_ext_id = a.user_ext_id
      WHERE DATEDIFF(WEEK, c.cohort_week, a.aw) = 1
    ),
    w4 AS (
      SELECT COUNT(DISTINCT c.user_ext_id) AS n
      FROM cohort_users c JOIN activity a ON c.user_ext_id = a.user_ext_id
      WHERE DATEDIFF(WEEK, c.cohort_week, a.aw) = 4
    ),
    w8 AS (
      SELECT COUNT(DISTINCT c.user_ext_id) AS n
      FROM cohort_users c JOIN activity a ON c.user_ext_id = a.user_ext_id
      WHERE DATEDIFF(WEEK, c.cohort_week, a.aw) = 8
    ),
    wins AS (
      SELECT SUM(win_amount) AS total_win
      FROM workspace.default.v_casino_wins w
      JOIN cohort_users c ON w.user_ext_id = c.user_ext_id
      WHERE DATEDIFF(WEEK, c.cohort_week, DATE_TRUNC('WEEK', w.dt)) >= 1
    )
    SELECT
      w0.n AS n_w0,
      w1.n AS n_w1, ROUND(w1.n * 100.0 / NULLIF(w0.n,0), 1) AS ret_w1,
      w4.n AS n_w4, ROUND(w4.n * 100.0 / NULLIF(w0.n,0), 1) AS ret_w4,
      w8.n AS n_w8, ROUND(w8.n * 100.0 / NULLIF(w0.n,0), 1) AS ret_w8,
      w1.stake AS stake_ret,
      wins.total_win AS total_win
    FROM w0, w1, w4, w8, wins
    """
    return execute_query(q)


# ── KPIs ──────────────────────────────────────────────────────────────────────
with st.spinner("Carregando indicadores..."):
    try:
        kpi = load_kpis_ret(ini_str, fim_str, activity_sql, canal_filter).iloc[0]
        ret_w1 = float(kpi["ret_w1"] or 0)
        ret_w4 = float(kpi["ret_w4"] or 0)
        ret_w8 = float(kpi["ret_w8"] or 0)
        n_w0   = int(kpi["n_w0"]   or 0)
        n_w1   = int(kpi["n_w1"]   or 0)
        stake  = float(kpi["stake_ret"] or 0)
        win    = float(kpi["total_win"]  or 0)
        ngr    = stake - win

        def fmt_money(v):
            if v >= 1_000_000: return f"R${v/1_000_000:.1f}M"
            if v >= 1_000:     return f"R${v/1_000:.0f}K"
            return f"R${v:.0f}"

        c1,c2,c3,c4,c5,c6 = st.columns(6)
        cards = [
            (c1, "RETENÇÃO W1",    f"{ret_w1:.1f}%", "depósito W1",      ret_w1 > 0),
            (c2, "RETENÇÃO W4",    f"{ret_w4:.1f}%", "depósito W4",      ret_w4 > 0),
            (c3, "RETENÇÃO W8",    f"{ret_w8:.1f}%", "jan W1",           ret_w8 > 0),
            (c4, "USUÁRIOS ATIVOS",f"{n_w1:,}",       "recorrentes W1",  True),
            (c5, "STAKE RETIDO",   fmt_money(stake),  "vs. mês ant.",     True),
            (c6, "RECEITA RETIDA", fmt_money(abs(ngr)),"NGR retenção",   True),
        ]
        for col, label, value, sub, up in cards:
            with col:
                delta_cls = "kpi-delta-up" if up else "kpi-delta-down"
                arrow = "▲" if up else "▼"
                st.markdown(f"""<div class="kpi-card">
                  <div class="kpi-label">{label}</div>
                  <div class="kpi-value">{value}</div>
                  <div class="{delta_cls}">{arrow} {sub}</div>
                </div>""", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erro nos KPIs: {e}")

st.markdown("<br>", unsafe_allow_html=True)

# ── Cohort Matrix ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">COHORT DE RETENÇÃO POR USUÁRIOS (%)</div>', unsafe_allow_html=True)

try:
    df_raw = load_cohort_matrix(ini_str, fim_str, cohort_trunc, activity_sql, canal_filter, max_weeks)

    if not df_raw.empty:
        df_raw["cohort_week"]   = pd.to_datetime(df_raw["cohort_week"])
        df_raw["retention_pct"] = pd.to_numeric(df_raw["retention_pct"], errors="coerce")
        df_raw["week_num"]      = pd.to_numeric(df_raw["week_num"],      errors="coerce")
        df_raw["cohort_size"]   = pd.to_numeric(df_raw["cohort_size"],   errors="coerce")
        cohorts = sorted(df_raw["cohort_week"].unique())

        # Pivotear
        pivot = df_raw.pivot_table(
            index="cohort_week", columns="week_num",
            values="retention_pct", aggfunc="first"
        )
        sizes = df_raw[df_raw["week_num"] == 0].set_index("cohort_week")["cohort_size"]

        weeks = list(range(0, max_weeks + 1))
        week_labels = [f"W{w}" for w in weeks]

        # Rótulo da linha
        def cohort_label(dt):
            mes = dt.strftime("%b").capitalize()
            if safra_tipo == "Ano" or cohort_trunc == "MONTH":
                return f"{mes}/{dt.strftime('%y')}"
            week_of_month = (dt.day - 1) // 14 + 1
            return f"{mes} W{week_of_month}"

        # Montar HTML da tabela
        header = "<tr><th>Cohort</th>" + "".join(f"<th>{w}</th>" for w in week_labels) + "</tr>"
        rows_html = ""
        for cohort in cohorts:
            label = cohort_label(cohort)
            row = f"<tr><td>{label}</td>"
            for w in weeks:
                val = pivot.loc[cohort, w] if cohort in pivot.index and w in pivot.columns else None
                cls, txt = cell_class(val)
                if cls == "cell-null":
                    row += f'<td><span class="cell-null">—</span></td>'
                else:
                    row += f'<td><span class="{cls}">{txt}</span></td>'
            row += "</tr>"
            rows_html += row

        legend = """
        <div style="text-align:center;margin-top:8px;font-size:11px;color:#596460;">
          Retenção:
          <span style="background:#1e4030;color:white;padding:2px 8px;border-radius:4px;margin:0 3px">100%</span>
          <span style="background:#3a7d52;color:white;padding:2px 8px;border-radius:4px;margin:0 3px">≥85%</span>
          <span style="background:#a7d4b8;color:#162b20;padding:2px 8px;border-radius:4px;margin:0 3px">≥45%</span>
          <span style="background:#c8e8d4;color:#162b20;padding:2px 8px;border-radius:4px;margin:0 3px">≥30%</span>
          <span style="background:#dff0e6;color:#596460;padding:2px 8px;border-radius:4px;margin:0 3px">≥15%</span>
          <span style="background:#f0f0ec;color:#8a9490;padding:2px 8px;border-radius:4px;margin:0 3px">&lt;15%</span>
        </div>"""

        st.markdown(
            f'<div style="background:white;border-radius:22px;padding:20px;border:1px solid #e2e8e4;overflow-x:auto;box-shadow:0 1px 3px rgba(0,0,0,.07)">'
            f'<table class="cohort-table"><thead>{header}</thead><tbody>{rows_html}</tbody></table>'
            f'{legend}</div>',
            unsafe_allow_html=True
        )
    else:
        st.info("Sem dados de cohort para o período selecionado.")

except Exception as e:
    st.error(f"Erro no cohort: {e}")

st.markdown("<br>", unsafe_allow_html=True)

# ── Curva de Retenção Média ───────────────────────────────────────────────────
col_curve, col_detail = st.columns([1, 1], gap="large")

with col_curve:
    st.markdown('<div class="section-title">CURVA DE RETENÇÃO MÉDIA</div>', unsafe_allow_html=True)
    try:
        if not df_raw.empty:
            df_raw["retention_pct"] = pd.to_numeric(df_raw["retention_pct"], errors="coerce")
            df_raw["week_num"]      = pd.to_numeric(df_raw["week_num"],      errors="coerce")
            avg_curve = df_raw.groupby("week_num")["retention_pct"].mean().reset_index()
            avg_curve = avg_curve[avg_curve["week_num"] <= max_weeks]

            fig_curve = go.Figure()
            fig_curve.add_trace(go.Scatter(
                x=[f"W{int(w)}" for w in avg_curve["week_num"]],
                y=avg_curve["retention_pct"].round(1),
                mode="lines+markers",
                name="Usuários %",
                line=dict(color="#3a7d52", width=3),
                marker=dict(size=9, color="#3a7d52"),
                fill="tozeroy", fillcolor="rgba(58,125,82,0.08)",
            ))
            fig_curve.update_layout(
                height=300, margin=dict(l=0, r=10, t=10, b=10),
                plot_bgcolor="#f7f6f2", paper_bgcolor="#f7f6f2",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#e2e8e4",
                           ticksuffix="%", range=[0, 110]),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                hovermode="x unified",
            )
            st.plotly_chart(fig_curve, use_container_width=True)
    except Exception as e:
        st.error(f"Erro na curva: {e}")

with col_detail:
    st.markdown('<div class="section-title">TABELA DE COHORTS</div>', unsafe_allow_html=True)
    try:
        if not df_raw.empty:
            tbl = df_raw[df_raw["week_num"] <= 6].copy()
            tbl["cohort_week"] = pd.to_datetime(tbl["cohort_week"])
            tbl["Cohort"] = tbl["cohort_week"].apply(cohort_label)

            detail = tbl.pivot_table(
                index="Cohort", columns="week_num",
                values="retained", aggfunc="first"
            ).reset_index()

            # Adiciona tamanho do cohort (W0)
            size_map = dict(zip(
                [cohort_label(c) for c in cohorts],
                [int(sizes.get(c, 0)) for c in cohorts]
            ))
            detail.insert(1, "Usuários W0", detail["Cohort"].map(size_map))

            detail.columns = ["COHORT", "USUÁRIOS W0"] + [f"W{int(c)}" for c in detail.columns[2:]]
            detail = detail.drop(columns=["W0"], errors="ignore")

            st.dataframe(detail, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Erro na tabela: {e}")
