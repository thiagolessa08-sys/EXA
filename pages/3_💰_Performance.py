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

def fmt_money(v) -> str:
    v = float(v or 0)
    if abs(v) >= 1_000_000: return f"R${v/1_000_000:.1f}M".replace(".", ",")
    if abs(v) >= 1_000:     return f"R${v/1_000:.0f}K"
    return f"R${v:.0f}"

def fmt_money_short(v) -> str:
    v = float(v or 0)
    if abs(v) >= 1_000_000: return f"R${v/1_000_000:.1f}M".replace(".", ",")
    if abs(v) >= 1_000:     return f"R${v/1_000:.0f}K"
    return f"R${v:.0f}"


_EMBED_OVERRIDES = """
<style id="exa-streamlit-embed">
  .app { grid-template-columns: 1fr !important; }
  .sidebar { display: none !important; }
  .topbar { display: none !important; }
  .page { padding-top: 12px !important; }
  body { background: transparent !important; }
</style>
</head>"""


# ── Filtros (sidebar) ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown("**Filtros**")

    today = date.today()

    safra_tipo = st.selectbox("Período", ["Ano", "Mês", "Data aberta"])

    if safra_tipo == "Ano":
        anos = list(range(today.year, today.year - 5, -1))
        ano_sel = st.selectbox("Ano", anos)
        dt_ini = date(ano_sel, 1, 1)
        dt_fim = date(ano_sel, 12, 31) if ano_sel < today.year else today
    elif safra_tipo == "Mês":
        meses = pd.date_range(end=today, periods=24, freq="MS").strftime("%Y-%m").tolist()[::-1]
        mes_sel = st.selectbox("Mês", meses,
                               format_func=lambda x: datetime.strptime(x, "%Y-%m").strftime("%b/%y"))
        dt_ini = datetime.strptime(mes_sel, "%Y-%m").date()
        dt_fim = (dt_ini.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    else:
        dt_ini = st.date_input("De", value=today - timedelta(days=30))
        dt_fim = st.date_input("Até", value=today)

    canal_opt = st.selectbox("Canal", ["Total", "Afiliados", "Orgânico", "Mobile"])
    produto_opt = st.selectbox("Produto", ["Total", "Casino", "Sports"])
    granular = st.selectbox("Granularidade", ["Mensal", "Semanal", "Diária"])


ini_str = str(dt_ini)
fim_str = str(dt_fim)
trunc   = {"Mensal": "MONTH", "Semanal": "WEEK", "Diária": "DAY"}[granular]
fmt_lbl = {"Mensal": "%b/%y",  "Semanal": "%d/%m",  "Diária": "%d/%m"}[granular]

canal_join  = "LEFT JOIN workspace.default.v_users_summary u ON cb.user_ext_id = u.user_ext_id"
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
      SELECT cb.user_ext_id,
        {casino_stake} AS c_stake, {casino_wins} AS c_win,
        {casino_bonus} AS c_bonus, {sport_stake} AS s_stake
      FROM workspace.default.v_casino_bets cb
      LEFT JOIN workspace.default.v_casino_wins cw ON cb.bet_id = cw.bet_id
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
        COUNT(*) AS n_apostas,
        COUNT(DISTINCT user_ext_id) AS n_users
      FROM base
    )
    SELECT *, ROUND(stake_total / NULLIF(n_users, 0), 2) AS stake_por_usuario FROM totals
    """
    return execute_query(q)


@st.cache_data(ttl=300, show_spinner=False)
def load_evolucao(ini, fim, trunc, produto, canal_w):
    if produto == "Sports":
        q = f"""
        SELECT DATE_TRUNC('{trunc}', sb.dt_update) AS periodo,
               SUM(sb.sport_last_bet_amount)       AS stake,
               0                                    AS wins,
               COUNT(DISTINCT sb.user_ext_id)      AS usuarios
        FROM workspace.default.v_sports_bets sb
        LEFT JOIN workspace.default.v_users_summary u ON sb.user_ext_id = u.user_ext_id
        WHERE sb.dt_update BETWEEN '{ini}' AND '{fim} 23:59:59'
        {canal_w}
        GROUP BY 1 ORDER BY 1
        """
    elif produto == "Casino":
        q = f"""
        SELECT DATE_TRUNC('{trunc}', cb.dt) AS periodo,
               SUM(cb.bet_amount)            AS stake,
               SUM(COALESCE(cw.win_amount,0)) AS wins,
               COUNT(DISTINCT cb.user_ext_id) AS usuarios
        FROM workspace.default.v_casino_bets cb
        LEFT JOIN workspace.default.v_casino_wins cw ON cb.bet_id = cw.bet_id
        LEFT JOIN workspace.default.v_users_summary u ON cb.user_ext_id = u.user_ext_id
        WHERE cb.dt BETWEEN '{ini}' AND '{fim} 23:59:59'
        {canal_w}
        GROUP BY 1 ORDER BY 1
        """
    else:
        q = f"""
        SELECT DATE_TRUNC('{trunc}', cb.dt) AS periodo,
               SUM(cb.bet_amount) + SUM(COALESCE(sb.sport_last_bet_amount,0)) AS stake,
               SUM(COALESCE(cw.win_amount,0))   AS wins,
               COUNT(DISTINCT cb.user_ext_id)   AS usuarios
        FROM workspace.default.v_casino_bets cb
        LEFT JOIN workspace.default.v_sports_bets sb
          ON cb.user_ext_id = sb.user_ext_id
          AND DATE_TRUNC('DAY', cb.dt) = DATE_TRUNC('DAY', sb.dt_update)
        LEFT JOIN workspace.default.v_casino_wins cw ON cb.bet_id = cw.bet_id
        LEFT JOIN workspace.default.v_users_summary u ON cb.user_ext_id = u.user_ext_id
        WHERE cb.dt BETWEEN '{ini}' AND '{fim} 23:59:59'
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
    GROUP BY 1 ORDER BY MIN(total_stake)
    """
    return execute_query(q)


@st.cache_data(ttl=300, show_spinner=False)
def load_top_jogos(ini, fim, canal_w):
    q = f"""
    SELECT cb.game_name, cb.game_provider, cb.game_cateogry AS categoria,
           COUNT(*) AS apostas,
           COUNT(DISTINCT cb.user_ext_id) AS usuarios,
           ROUND(SUM(cb.bet_amount), 2) AS stake,
           ROUND(SUM(cb.bet_amount) - SUM(COALESCE(cw.win_amount,0)), 2) AS ggr
    FROM workspace.default.v_casino_bets cb
    LEFT JOIN workspace.default.v_casino_wins cw ON cb.bet_id = cw.bet_id
    LEFT JOIN workspace.default.v_users_summary u ON cb.user_ext_id = u.user_ext_id
    WHERE cb.dt BETWEEN '{ini}' AND '{fim} 23:59:59'
    {canal_w}
    GROUP BY 1,2,3 ORDER BY stake DESC LIMIT 15
    """
    return execute_query(q)


@st.cache_data(ttl=300, show_spinner=False)
def load_top_providers(ini, fim, canal_w):
    q = f"""
    SELECT cb.game_provider,
           ROUND(SUM(cb.bet_amount) - SUM(COALESCE(cw.win_amount,0)), 2) AS ggr
    FROM workspace.default.v_casino_bets cb
    LEFT JOIN workspace.default.v_casino_wins cw ON cb.bet_id = cw.bet_id
    LEFT JOIN workspace.default.v_users_summary u ON cb.user_ext_id = u.user_ext_id
    WHERE cb.dt BETWEEN '{ini}' AND '{fim} 23:59:59'
    {canal_w}
    GROUP BY 1 ORDER BY ggr DESC LIMIT 10
    """
    return execute_query(q)


# ── Montar payload ────────────────────────────────────────────────────────────
def build_payload() -> dict:
    # KPIs
    try:
        row = load_kpis(ini_str, fim_str, produto_opt, canal_where).iloc[0]
        stake_total = float(row["stake_total"] or 0)
        ggr         = float(row["ggr"]         or 0)
        ngr         = float(row["ngr"]         or 0)
        n_apostas   = int(row["n_apostas"]     or 0)
        n_users     = int(row["n_users"]       or 0)
        spu         = float(row["stake_por_usuario"] or 0)
    except Exception:
        stake_total = ggr = ngr = spu = 0.0
        n_apostas = n_users = 0

    kpis = [
        {"key": "stake",  "label": "Stake total",     "value": fmt_money_short(stake_total), "sub": "volume apostado", "delta": {"dir": "up",   "v": ""}, "spark": [], "color": "#2540ea"},
        {"key": "ggr",    "label": "GGR",             "value": fmt_money_short(ggr),         "sub": "receita bruta",   "delta": {"dir": "up",   "v": ""}, "spark": [], "color": "#2540ea"},
        {"key": "ngr",    "label": "NGR",             "value": fmt_money_short(ngr),         "sub": "receita líquida", "delta": {"dir": "up" if ngr >= 0 else "down", "v": ""}, "spark": [], "color": "#2540ea"},
        {"key": "rod",    "label": "Apostas",         "value": fmt_int(n_apostas),           "sub": "total de rodadas","delta": {"dir": "up",   "v": ""}, "spark": [], "color": "#2540ea"},
        {"key": "users",  "label": "Usuários apost.", "value": fmt_int(n_users),             "sub": "jogadores únicos","delta": {"dir": "up",   "v": ""}, "spark": [], "color": "#2540ea"},
        {"key": "stk_u",  "label": "Stake / usuário", "value": fmt_money_short(spu),         "sub": "ticket médio",    "delta": {"dir": "flat", "v": ""}, "spark": [], "color": "#6b7280"},
    ]

    # Evolução
    months, bars_stake, ggr_line, users_line = [], [], [], []
    try:
        evol = load_evolucao(ini_str, fim_str, trunc, produto_opt, canal_where)
        evol["periodo"] = pd.to_datetime(evol["periodo"])
        evol["stake"]   = pd.to_numeric(evol["stake"], errors="coerce").fillna(0)
        evol["wins"]    = pd.to_numeric(evol["wins"],  errors="coerce").fillna(0)
        evol["usuarios"]= pd.to_numeric(evol["usuarios"], errors="coerce").fillna(0)
        for _, r in evol.iterrows():
            months.append(r["periodo"].strftime(fmt_lbl))
            bars_stake.append(round(float(r["stake"]) / 1_000_000, 2))
            ggr_val = float(r["stake"]) - float(r["wins"])
            ggr_line.append(round(ggr_val / 1_000_000, 2))
            users_line.append(int(r["usuarios"]))
    except Exception:
        pass

    # Distribuição
    buckets = []
    try:
        dist = load_distribuicao(ini_str, fim_str, canal_where)
        ordem = ["R$0-50","R$50-200","R$200-500","R$500-1k","R$1k-2k","R$2k-5k","R$5k+"]
        label_map = {"R$0-50":"R$0–50","R$50-200":"R$50–200","R$200-500":"R$200–500",
                     "R$500-1k":"R$500–1k","R$1k-2k":"R$1k–2k","R$2k-5k":"R$2k–5k","R$5k+":"R$5k+"}
        dist["usuarios"] = pd.to_numeric(dist["usuarios"], errors="coerce").fillna(0)
        dist["faixa"] = pd.Categorical(dist["faixa"], categories=ordem, ordered=True)
        dist = dist.sort_values("faixa")
        for _, r in dist.iterrows():
            buckets.append({"label": label_map.get(str(r["faixa"]), str(r["faixa"])),
                            "value": int(r["usuarios"])})
    except Exception:
        pass

    # Top jogos
    games_rows = []
    try:
        jg = load_top_jogos(ini_str, fim_str, canal_where)
        for _, r in jg.iterrows():
            games_rows.append({
                "jogo": str(r.get("game_name") or "—"),
                "provider": str(r.get("game_provider") or "—"),
                "cat": str(r.get("categoria") or "—"),
                "apostas": int(r.get("apostas") or 0),
                "users":   int(r.get("usuarios") or 0),
                "stake":   fmt_money(r.get("stake")),
                "ggr":     fmt_money(r.get("ggr")),
            })
    except Exception:
        pass

    # Top providers
    prov_rows = []
    try:
        pv = load_top_providers(ini_str, fim_str, canal_where)
        pv["ggr"] = pd.to_numeric(pv["ggr"], errors="coerce").fillna(0)
        for _, r in pv.iterrows():
            ggr_v = float(r["ggr"])
            prov_rows.append({
                "name":  str(r.get("game_provider") or "—"),
                "value": round(ggr_v / 1_000_000, 3),
                "label": fmt_money(ggr_v),
            })
    except Exception:
        pass

    periodo_label = {
        "Ano": str(dt_ini.year),
        "Mês": dt_ini.strftime("%b/%y"),
    }.get(safra_tipo, f"{dt_ini.strftime('%d/%m')}–{dt_fim.strftime('%d/%m/%y')}")

    return {
        "filters": {
            "granularidade": granular,
            "base":          produto_opt,
            "periodo":       periodo_label,
            "data_inicio":   dt_ini.strftime("%d/%m/%Y"),
            "data_fim":      dt_fim.strftime("%d/%m/%Y"),
            "atualizado":    datetime.now().strftime("%d/%m/%Y · %H:%M"),
        },
        "header": {
            "eyebrow":      "Painel · Monetização",
            "title":        "Performance",
            "lede":         "Volume de apostas, monetização e comportamento — stake, GGR/NGR e top jogos no período.",
            "base_analise": produto_opt,
            "comparativo":  "Período anterior",
        },
        "user": {"name": "Analytics", "role": "EXA", "initials": "EX"},
        "nav": [
            {"key": "onboarding",  "label": "Onboarding",  "icon": "funnel"},
            {"key": "retencao",    "label": "Retenção",    "icon": "retention"},
            {"key": "performance", "label": "Performance", "icon": "perf", "active": True},
            {"key": "chat",        "label": "Chat",        "icon": "chat"},
        ],
        "kpis": kpis,
        "combo": {
            "title":    "Evolução — Stake & GGR",
            "subtitle": f"{granular} · período selecionado",
            "months":   months or ["—"],
            "stake":    bars_stake or [0],
            "ggr":      ggr_line   or [0],
            "users":    users_line or [0],
        },
        "dist": {
            "title":    "Distribuição de stake por usuário",
            "subtitle": "Por faixa de gasto",
            "buckets":  buckets or [{"label": "—", "value": 0}],
        },
        "topGames": {
            "title":    "Top 15 jogos — Casino",
            "subtitle": "Por volume apostado no período",
            "rows":     games_rows or [],
        },
        "topProviders": {
            "title":    "Top Providers",
            "subtitle": "Por GGR no período",
            "rows":     prov_rows or [],
        },
    }


# ── Render ────────────────────────────────────────────────────────────────────
with st.spinner("Carregando dashboard..."):
    payload = build_payload()

template = load_template("dashboard_performance.html")
html = template.replace("__EXA_DATA_JSON__", json.dumps(payload, ensure_ascii=False), 1)
html = html.replace("</head>", _EMBED_OVERRIDES)
components.html(html, height=800, scrolling=False)
