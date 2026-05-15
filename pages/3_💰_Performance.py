import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from core.databricks_client import execute_query
from core.theme import inject_theme, page_header, kpi_card

st.set_page_config(page_title="Performance", page_icon="💰", layout="wide")
inject_theme()


def fmt_money(v):
    v = float(v or 0)
    if abs(v) >= 1_000_000: return f"R${v/1_000_000:.1f}M"
    if abs(v) >= 1_000:     return f"R${v/1_000:.0f}K"
    return f"R${v:.0f}"

def fmt_num(v):
    return f"{int(v or 0):,}"


# ── Header ────────────────────────────────────────────────────────────────────
page_header("Performance", "Volume de apostas, monetização e comportamento", "Performance")

# ── Filtros ───────────────────────────────────────────────────────────────────
with st.container():
    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    f1, f2, f3, f4, f5 = st.columns([2, 2, 2, 2, 2])
    today = date.today()

    with f1:
        safra_tipo = st.selectbox("Período", ["Ano", "Mês", "Data aberta"], label_visibility="visible")

    with f2:
        if safra_tipo == "Ano":
            anos = list(range(today.year, today.year - 5, -1))
            ano_sel = st.selectbox("Ano", anos, label_visibility="visible")
            dt_ini = date(ano_sel, 1, 1)
            dt_fim = date(ano_sel, 12, 31) if ano_sel < today.year else today
        elif safra_tipo == "Mês":
            meses = pd.date_range(end=today, periods=24, freq="MS").strftime("%Y-%m").tolist()[::-1]
            mes_sel = st.selectbox("Mês", meses, label_visibility="visible",
                                   format_func=lambda x: datetime.strptime(x, "%Y-%m").strftime("%b/%y"))
            dt_ini = datetime.strptime(mes_sel, "%Y-%m").date()
            dt_fim = (dt_ini.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        else:
            dt_ini = st.date_input("De", value=today - timedelta(days=30), label_visibility="visible")
            dt_fim = st.date_input("Até", value=today, label_visibility="visible")

    with f3:
        canal_opt = st.selectbox("Canal", ["Total", "Afiliados", "Orgânico", "Mobile"], label_visibility="visible")

    with f4:
        produto_opt = st.selectbox("Produto", ["Total", "Casino", "Sports"], label_visibility="visible")

    with f5:
        granular = st.selectbox("Granularidade", ["Mensal", "Semanal", "Diária"], label_visibility="visible")

    st.markdown("</div>", unsafe_allow_html=True)

ini_str = str(dt_ini)
fim_str = str(dt_fim)
trunc   = {"Mensal": "MONTH", "Semanal": "WEEK", "Diária": "DAY"}[granular]
fmt_lbl = {"Mensal": "%b/%y",  "Semanal": "%d/%m",  "Diária": "%d/%m"}[granular]

canal_join = "LEFT JOIN workspace.default.v_users_summary u ON cb.user_ext_id = u.user_ext_id"
canal_where = ""
if canal_opt == "Afiliados":
    canal_where = "AND u.core_affiliate_id IS NOT NULL AND u.core_affiliate_id > 0"
elif canal_opt == "Orgânico":
    canal_where = "AND (u.core_affiliate_id IS NULL OR u.core_affiliate_id = 0)"
elif canal_opt == "Mobile":
    canal_where = "AND u.platform = 'mobile'"


# ── Queries ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_kpis(ini, fim, produto, canal_w):
    casino_stake = "0" if produto == "Sports" else "COALESCE(cb.bet_amount, 0)"
    casino_wins  = "0" if produto == "Sports" else "COALESCE(cw.win_amount, 0)"
    casino_bonus = "0" if produto == "Sports" else "COALESCE(cb.bet_amount_bonus, 0)"
    sport_stake  = "0" if produto == "Casino" else "COALESCE(sb.sport_last_bet_amount, 0)"

    q = f"""
    WITH base AS (
      SELECT
        cb.user_ext_id,
        {casino_stake} AS c_stake,
        {casino_wins}  AS c_win,
        {casino_bonus} AS c_bonus,
        {sport_stake}  AS s_stake
      FROM workspace.default.v_casino_bets cb
      LEFT JOIN workspace.default.v_casino_wins cw
        ON cb.bet_id = cw.bet_id
      LEFT JOIN workspace.default.v_sports_bets sb
        ON cb.user_ext_id = sb.user_ext_id
        AND DATE_TRUNC('DAY', cb.dt) = DATE_TRUNC('DAY', sb.dt_update)
      {canal_join}
      WHERE cb.dt BETWEEN '{ini}' AND '{fim} 23:59:59'
      {canal_w}
    ),
    totals AS (
      SELECT
        SUM(c_stake + s_stake)               AS stake_total,
        SUM(c_stake + s_stake - c_win)       AS ggr,
        SUM(c_stake + s_stake - c_win - c_bonus) AS ngr,
        COUNT(*)                             AS n_apostas,
        COUNT(DISTINCT user_ext_id)          AS n_users
      FROM base
    )
    SELECT *, ROUND(stake_total / NULLIF(n_users, 0), 2) AS stake_por_usuario
    FROM totals
    """
    return execute_query(q)


@st.cache_data(ttl=300, show_spinner=False)
def load_evolucao(ini, fim, trunc, produto, canal_w):
    if produto == "Sports":
        stake_expr = "SUM(sb.sport_last_bet_amount)"
        from_table = "workspace.default.v_sports_bets sb"
        date_col   = "sb.dt_update"
        join_user  = "LEFT JOIN workspace.default.v_users_summary u ON sb.user_ext_id = u.user_ext_id"
        win_expr   = "0"
    elif produto == "Casino":
        stake_expr = "SUM(cb.bet_amount)"
        from_table = "workspace.default.v_casino_bets cb"
        date_col   = "cb.dt"
        join_user  = "LEFT JOIN workspace.default.v_users_summary u ON cb.user_ext_id = u.user_ext_id"
        win_expr   = "SUM(COALESCE(cw.win_amount,0))"
    else:
        stake_expr = "SUM(cb.bet_amount) + SUM(COALESCE(sb.sport_last_bet_amount,0))"
        from_table = "workspace.default.v_casino_bets cb LEFT JOIN workspace.default.v_sports_bets sb ON cb.user_ext_id = sb.user_ext_id AND DATE_TRUNC('DAY', cb.dt) = DATE_TRUNC('DAY', sb.dt_update)"
        date_col   = "cb.dt"
        join_user  = "LEFT JOIN workspace.default.v_users_summary u ON cb.user_ext_id = u.user_ext_id"
        win_expr   = "SUM(COALESCE(cw.win_amount,0))"

    q = f"""
    SELECT
      DATE_TRUNC('{trunc}', {date_col})       AS periodo,
      {stake_expr}                             AS stake,
      {win_expr}                               AS wins,
      COUNT(DISTINCT cb.user_ext_id)           AS usuarios
    FROM {from_table}
    {'LEFT JOIN workspace.default.v_casino_wins cw ON cb.bet_id = cw.bet_id' if produto != 'Sports' else ''}
    {join_user}
    WHERE {date_col} BETWEEN '{ini}' AND '{fim} 23:59:59'
    {canal_w}
    GROUP BY 1 ORDER BY 1
    """ if produto != "Sports" else f"""
    SELECT
      DATE_TRUNC('{trunc}', sb.dt_update)      AS periodo,
      SUM(sb.sport_last_bet_amount)             AS stake,
      0                                         AS wins,
      COUNT(DISTINCT sb.user_ext_id)            AS usuarios
    FROM workspace.default.v_sports_bets sb
    {join_user}
    WHERE sb.dt_update BETWEEN '{ini}' AND '{fim} 23:59:59'
    {canal_w}
    GROUP BY 1 ORDER BY 1
    """
    return execute_query(q)


@st.cache_data(ttl=300, show_spinner=False)
def load_distribuicao(ini, fim, canal_w):
    q = f"""
    WITH user_stake AS (
      SELECT cb.user_ext_id, SUM(cb.bet_amount) AS total_stake
      FROM workspace.default.v_casino_bets cb
      LEFT JOIN workspace.default.v_users_summary u ON cb.user_ext_id = u.user_ext_id
      WHERE cb.dt BETWEEN '{ini}' AND '{fim} 23:59:59'
      {canal_w}
      GROUP BY 1
    )
    SELECT
      CASE
        WHEN total_stake < 50    THEN 'R$0-50'
        WHEN total_stake < 200   THEN 'R$50-200'
        WHEN total_stake < 500   THEN 'R$200-500'
        WHEN total_stake < 1000  THEN 'R$500-1k'
        WHEN total_stake < 2000  THEN 'R$1k-2k'
        WHEN total_stake < 5000  THEN 'R$2k-5k'
        ELSE 'R$5k+'
      END AS faixa,
      COUNT(*) AS usuarios
    FROM user_stake
    GROUP BY 1
    ORDER BY MIN(total_stake)
    """
    return execute_query(q)


@st.cache_data(ttl=300, show_spinner=False)
def load_top_jogos(ini, fim, canal_w):
    q = f"""
    SELECT
      cb.game_name,
      cb.game_provider,
      cb.game_cateogry                     AS categoria,
      COUNT(*)                              AS apostas,
      COUNT(DISTINCT cb.user_ext_id)        AS usuarios,
      ROUND(SUM(cb.bet_amount), 2)          AS stake,
      ROUND(SUM(COALESCE(cw.win_amount,0)),2) AS wins,
      ROUND(SUM(cb.bet_amount) - SUM(COALESCE(cw.win_amount,0)), 2) AS ggr
    FROM workspace.default.v_casino_bets cb
    LEFT JOIN workspace.default.v_casino_wins cw ON cb.bet_id = cw.bet_id
    LEFT JOIN workspace.default.v_users_summary u  ON cb.user_ext_id = u.user_ext_id
    WHERE cb.dt BETWEEN '{ini}' AND '{fim} 23:59:59'
    {canal_w}
    GROUP BY 1,2,3
    ORDER BY stake DESC
    LIMIT 15
    """
    return execute_query(q)


@st.cache_data(ttl=300, show_spinner=False)
def load_top_providers(ini, fim, canal_w):
    q = f"""
    SELECT
      cb.game_provider,
      COUNT(DISTINCT cb.user_ext_id)          AS usuarios,
      ROUND(SUM(cb.bet_amount), 2)            AS stake,
      ROUND(SUM(COALESCE(cw.win_amount,0)),2) AS wins,
      ROUND(SUM(cb.bet_amount) - SUM(COALESCE(cw.win_amount,0)), 2) AS ggr
    FROM workspace.default.v_casino_bets cb
    LEFT JOIN workspace.default.v_casino_wins cw ON cb.bet_id = cw.bet_id
    LEFT JOIN workspace.default.v_users_summary u  ON cb.user_ext_id = u.user_ext_id
    WHERE cb.dt BETWEEN '{ini}' AND '{fim} 23:59:59'
    {canal_w}
    GROUP BY 1
    ORDER BY stake DESC
    LIMIT 10
    """
    return execute_query(q)


# ── KPIs ──────────────────────────────────────────────────────────────────────
with st.spinner("Carregando..."):
    try:
        kpi = load_kpis(ini_str, fim_str, produto_opt, canal_where).iloc[0]
        stake   = float(kpi["stake_total"] or 0)
        ggr     = float(kpi["ggr"]         or 0)
        ngr     = float(kpi["ngr"]         or 0)
        apostas = int(kpi["n_apostas"]     or 0)
        users   = int(kpi["n_users"]       or 0)
        spu     = float(kpi["stake_por_usuario"] or 0)

        c1,c2,c3,c4,c5,c6 = st.columns(6)
        kpis = [
            (c1, "STAKE TOTAL",     fmt_money(stake),    "volume apostado",  "trending-up", "up"),
            (c2, "GGR",             fmt_money(ggr),      "receita bruta",    "bar-chart",   "up"),
            (c3, "NGR",             fmt_money(ngr),      "receita líquida",  "dollar",      "up" if ngr >= 0 else "down"),
            (c4, "APOSTAS",         fmt_num(apostas),    "total de rodadas",  "hash",        "up"),
            (c5, "USUÁRIOS APOST.", fmt_num(users),      "jogadores únicos",  "users",       "up"),
            (c6, "STAKE / USUÁRIO", fmt_money(spu),      "ticket médio",      "divide",      "up" if spu >= 0 else "down"),
        ]
        for col, label, value, sub, icon, sub_type in kpis:
            with col:
                st.markdown(kpi_card(label, value, sub, icon, sub_type=sub_type), unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erro nos KPIs: {e}")
        stake = ggr = ngr = apostas = users = spu = 0

st.markdown("<br>", unsafe_allow_html=True)

# ── Evolução + Distribuição ───────────────────────────────────────────────────
col_evol, col_dist = st.columns([3, 2], gap="large")

with col_evol:
    st.markdown('<div class="section-title">EVOLUÇÃO — STAKE & GGR</div>', unsafe_allow_html=True)
    try:
        evol = load_evolucao(ini_str, fim_str, trunc, produto_opt, canal_where)
        evol["periodo"] = pd.to_datetime(evol["periodo"])
        evol["label"]   = evol["periodo"].dt.strftime(fmt_lbl)
        evol["stake"]   = pd.to_numeric(evol["stake"], errors="coerce")
        evol["wins"]    = pd.to_numeric(evol["wins"],  errors="coerce")
        evol["ggr"]     = evol["stake"] - evol["wins"]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=evol["label"], y=evol["stake"],
            name="Stake", marker_color="rgba(37,99,235,0.18)",
        ))
        fig.add_trace(go.Scatter(
            x=evol["label"], y=evol["ggr"],
            name="GGR", mode="lines+markers",
            line=dict(color="#2563EB", width=2), marker=dict(size=7),
        ))
        fig.add_trace(go.Scatter(
            x=evol["label"], y=pd.to_numeric(evol["usuarios"], errors="coerce"),
            name="Usuários", mode="lines+markers",
            line=dict(color="#60A5FA", width=2, dash="dot"), marker=dict(size=6),
            yaxis="y2",
        ))
        fig.update_layout(
            height=300, margin=dict(l=0, r=40, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#DBEAFE"),
            yaxis2=dict(overlaying="y", side="right", showgrid=False, title="Usuários"),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Erro na evolução: {e}")

with col_dist:
    st.markdown('<div class="section-title">DISTRIBUIÇÃO DE STAKE POR USUÁRIO</div>', unsafe_allow_html=True)
    try:
        dist = load_distribuicao(ini_str, fim_str, canal_where)
        dist["usuarios"] = pd.to_numeric(dist["usuarios"], errors="coerce")
        ordem = ["R$0-50","R$50-200","R$200-500","R$500-1k","R$1k-2k","R$2k-5k","R$5k+"]
        dist["faixa"] = pd.Categorical(dist["faixa"], categories=ordem, ordered=True)
        dist = dist.sort_values("faixa")

        n = len(dist)
        cores = [f"rgba(37,99,235,{1 - i*0.10})" for i in range(n)]

        fig_dist = go.Figure(go.Bar(
            x=dist["faixa"], y=dist["usuarios"],
            marker_color=cores,
            text=dist["usuarios"].astype(int).astype(str),
            textposition="outside",
        ))
        fig_dist.update_layout(
            height=300, margin=dict(l=0, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#DBEAFE"),
            showlegend=False,
        )
        st.plotly_chart(fig_dist, use_container_width=True)
    except Exception as e:
        st.error(f"Erro na distribuição: {e}")

st.markdown("<br>", unsafe_allow_html=True)

# ── Top Jogos + Top Providers ─────────────────────────────────────────────────
col_jogos, col_prov = st.columns([3, 2], gap="large")

with col_jogos:
    st.markdown('<div class="section-title">TOP 15 JOGOS — CASINO</div>', unsafe_allow_html=True)
    try:
        jogos = load_top_jogos(ini_str, fim_str, canal_where)
        if not jogos.empty:
            jogos["stake"] = pd.to_numeric(jogos["stake"], errors="coerce").apply(fmt_money)
            jogos["ggr"]   = pd.to_numeric(jogos["ggr"],   errors="coerce").apply(fmt_money)
            jogos = jogos.rename(columns={
                "game_name": "Jogo", "game_provider": "Provider",
                "categoria": "Categoria", "apostas": "Apostas",
                "usuarios": "Usuários", "stake": "Stake", "ggr": "GGR",
            })
            st.dataframe(jogos[["Jogo","Provider","Categoria","Apostas","Usuários","Stake","GGR"]],
                         use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Erro nos jogos: {e}")

with col_prov:
    st.markdown('<div class="section-title">TOP PROVIDERS</div>', unsafe_allow_html=True)
    try:
        prov = load_top_providers(ini_str, fim_str, canal_where)
        if not prov.empty:
            prov["stake"] = pd.to_numeric(prov["stake"], errors="coerce")
            prov["ggr"]   = pd.to_numeric(prov["ggr"],   errors="coerce")
            total_stake   = prov["stake"].sum()
            prov["share"] = (prov["stake"] / total_stake * 100).round(1).astype(str) + "%"
            prov["stake_fmt"] = prov["stake"].apply(fmt_money)
            prov["ggr_fmt"]   = prov["ggr"].apply(fmt_money)

            fig_prov = go.Figure(go.Bar(
                y=prov["game_provider"][::-1],
                x=prov["stake"][::-1],
                orientation="h",
                marker_color="#2563EB",
                text=prov["stake_fmt"][::-1],
                textposition="inside",
                insidetextanchor="start",
                textfont=dict(color="white", size=11),
            ))
            fig_prov.update_layout(
                height=340, margin=dict(l=0, r=10, t=10, b=10),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                yaxis=dict(showgrid=False, tickfont=dict(size=12)),
                showlegend=False,
            )
            st.plotly_chart(fig_prov, use_container_width=True)
    except Exception as e:
        st.error(f"Erro nos providers: {e}")
