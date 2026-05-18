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

def fmt_pct(n, d=1) -> str:
    return f"{float(n or 0):.{d}f}".replace(".", ",")


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

    safra_tipo = st.selectbox("Granularidade", ["Ano", "Mês", "Data aberta"])

    if safra_tipo == "Ano":
        anos = list(range(today.year, today.year - 5, -1))
        ano_sel = st.selectbox("Ano", anos)
        dt_ini = date(ano_sel, 1, 1)
        dt_fim = date(ano_sel, 12, 31) if ano_sel < today.year else today
    elif safra_tipo == "Mês":
        meses = pd.date_range(end=today, periods=18, freq="MS").strftime("%Y-%m").tolist()[::-1]
        mes_sel = st.selectbox("Mês", meses,
                               format_func=lambda x: datetime.strptime(x, "%Y-%m").strftime("%b/%y"))
        dt_ini = datetime.strptime(mes_sel, "%Y-%m").date()
        dt_fim = (dt_ini.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    else:
        dt_ini = st.date_input("De", value=today - timedelta(days=30))
        dt_fim = st.date_input("Até", value=today)

    visao = st.selectbox("Visão", ["Semanal", "Quinzenal", "Mensal"])
    canal_opt = st.selectbox("Canal", ["Total", "Afiliados", "Orgânico", "Mobile"])
    produto_opt = st.selectbox("Produto", ["Total", "Casino", "Sports"])
    base_ret = st.selectbox("Base", ["Cadastro", "1º Depósito"])
    max_weeks = st.selectbox("Semanas", [4, 6, 8, 12], index=1)


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

# atividade por produto
if produto_opt == "Casino":
    activity_sql = "SELECT user_ext_id, DATE_TRUNC('WEEK', dt) AS aw, SUM(bet_amount) AS stake FROM workspace.default.v_casino_bets GROUP BY 1,2"
elif produto_opt == "Sports":
    activity_sql = "SELECT user_ext_id, DATE_TRUNC('WEEK', dt_update) AS aw, SUM(sport_last_bet_amount) AS stake FROM workspace.default.v_sports_bets GROUP BY 1,2"
else:
    activity_sql = """
    SELECT user_ext_id, DATE_TRUNC('WEEK', dt) AS aw, SUM(bet_amount) AS stake
    FROM workspace.default.v_casino_bets GROUP BY 1,2
    UNION ALL
    SELECT user_ext_id, DATE_TRUNC('WEEK', dt_update) AS aw, SUM(sport_last_bet_amount) AS stake
    FROM workspace.default.v_sports_bets GROUP BY 1,2"""

trunc_map = {"Semanal": "WEEK", "Quinzenal": "WEEK", "Mensal": "MONTH"}
cohort_trunc = "MONTH" if safra_tipo == "Ano" else trunc_map[visao]


# ── Queries ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_cohort_matrix(ini, fim, trunc, act_sql, canal_f, n_weeks):
    q = f"""
    WITH cohort_users AS (
      SELECT u.user_ext_id,
             DATE_TRUNC('{trunc}', u.core_registration_date) AS cohort_week
      FROM workspace.default.v_users_summary u
      WHERE u.core_registration_date BETWEEN '{ini}' AND '{fim} 23:59:59'
        {canal_f}
    ),
    activity AS (
      SELECT user_ext_id, aw, SUM(stake) AS stake_sum FROM ({act_sql}) t GROUP BY 1,2
    ),
    cohort_size AS (
      SELECT cohort_week, COUNT(DISTINCT user_ext_id) AS n_users
      FROM cohort_users GROUP BY 1
    ),
    joined AS (
      SELECT c.cohort_week,
             DATEDIFF(WEEK, c.cohort_week, a.aw) AS week_num,
             COUNT(DISTINCT a.user_ext_id) AS retained
      FROM cohort_users c
      JOIN activity a ON c.user_ext_id = a.user_ext_id
      WHERE DATEDIFF(WEEK, c.cohort_week, a.aw) BETWEEN 0 AND {n_weeks}
      GROUP BY 1, 2
    )
    SELECT j.cohort_week, j.week_num, j.retained,
           s.n_users AS cohort_size,
           ROUND(j.retained * 100.0 / s.n_users, 1) AS retention_pct
    FROM joined j JOIN cohort_size s ON j.cohort_week = s.cohort_week
    ORDER BY 1, 2
    """
    return execute_query(q)


@st.cache_data(ttl=300, show_spinner=False)
def load_kpis_ret(ini, fim, act_sql, canal_f):
    q = f"""
    WITH cohort_users AS (
      SELECT u.user_ext_id,
             DATE_TRUNC('WEEK', u.core_registration_date) AS cohort_week
      FROM workspace.default.v_users_summary u
      WHERE u.core_registration_date BETWEEN '{ini}' AND '{fim} 23:59:59'
        {canal_f}
    ),
    activity AS (
      SELECT user_ext_id, aw, SUM(stake) AS stake_sum FROM ({act_sql}) t GROUP BY 1,2
    ),
    w0 AS (SELECT COUNT(DISTINCT user_ext_id) AS n FROM cohort_users),
    w1 AS (
      SELECT COUNT(DISTINCT c.user_ext_id) AS n, SUM(a.stake_sum) AS stake
      FROM cohort_users c JOIN activity a ON c.user_ext_id = a.user_ext_id
      WHERE DATEDIFF(WEEK, c.cohort_week, a.aw) = 1
    ),
    w4 AS (
      SELECT COUNT(DISTINCT c.user_ext_id) AS n FROM cohort_users c JOIN activity a ON c.user_ext_id = a.user_ext_id
      WHERE DATEDIFF(WEEK, c.cohort_week, a.aw) = 4
    ),
    w8 AS (
      SELECT COUNT(DISTINCT c.user_ext_id) AS n FROM cohort_users c JOIN activity a ON c.user_ext_id = a.user_ext_id
      WHERE DATEDIFF(WEEK, c.cohort_week, a.aw) = 8
    ),
    wins AS (
      SELECT SUM(win_amount) AS total_win
      FROM workspace.default.v_casino_wins w
      JOIN cohort_users c ON w.user_ext_id = c.user_ext_id
      WHERE DATEDIFF(WEEK, c.cohort_week, DATE_TRUNC('WEEK', w.dt)) >= 1
    )
    SELECT w0.n AS n_w0,
           w1.n AS n_w1, ROUND(w1.n * 100.0 / NULLIF(w0.n,0), 1) AS ret_w1,
           w4.n AS n_w4, ROUND(w4.n * 100.0 / NULLIF(w0.n,0), 1) AS ret_w4,
           w8.n AS n_w8, ROUND(w8.n * 100.0 / NULLIF(w0.n,0), 1) AS ret_w8,
           w1.stake AS stake_ret, wins.total_win AS total_win
    FROM w0, w1, w4, w8, wins
    """
    return execute_query(q)


def cohort_label(dt) -> str:
    mes = dt.strftime("%b").capitalize()
    if safra_tipo == "Ano" or cohort_trunc == "MONTH":
        return f"{mes}/{dt.strftime('%y')}"
    week_of_month = (dt.day - 1) // 14 + 1
    return f"{mes} W{week_of_month}"


# ── Montar payload ────────────────────────────────────────────────────────────
def build_payload() -> dict:
    # KPIs
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
    except Exception:
        ret_w1 = ret_w4 = ret_w8 = 0.0
        n_w0 = n_w1 = 0
        stake = win = ngr = 0.0

    kpis = [
        {"key": "w1",  "label": "Retenção W1",     "value": fmt_pct(ret_w1), "unit": "%", "sub": "semana 1",       "delta": {"dir": "up" if ret_w1 > 0 else "flat", "v": ""}, "spark": [], "color": "#2540ea"},
        {"key": "w4",  "label": "Retenção W4",     "value": fmt_pct(ret_w4), "unit": "%", "sub": "semana 4",       "delta": {"dir": "up" if ret_w4 > 0 else "flat", "v": ""}, "spark": [], "color": "#2540ea"},
        {"key": "w8",  "label": "Retenção W8",     "value": fmt_pct(ret_w8), "unit": "%", "sub": "semana 8",       "delta": {"dir": "up" if ret_w8 > 0 else "flat", "v": ""}, "spark": [], "color": "#2540ea"},
        {"key": "act", "label": "Usuários ativos", "value": fmt_int(n_w1),                "sub": "recorrentes W1", "delta": {"dir": "up", "v": ""}, "spark": [], "color": "#1f9d57"},
        {"key": "stk", "label": "Stake retido",    "value": fmt_money(stake),             "sub": "no período",     "delta": {"dir": "up", "v": ""}, "spark": [], "color": "#2540ea"},
        {"key": "rec", "label": "Receita retida",  "value": fmt_money(abs(ngr)),          "sub": "NGR retenção",   "delta": {"dir": "up", "v": ""}, "spark": [], "color": "#2540ea"},
    ]

    # Cohort matrix
    cohort_header = [f"W{w}" for w in range(0, max_weeks + 1)]
    cohort_rows = []
    users_rows = []
    avg_curve_points = [100.0]
    avg_curve_labels = ["W0"]

    try:
        df = load_cohort_matrix(ini_str, fim_str, cohort_trunc, activity_sql, canal_filter, max_weeks)
        if not df.empty:
            df["cohort_week"]   = pd.to_datetime(df["cohort_week"])
            df["retention_pct"] = pd.to_numeric(df["retention_pct"], errors="coerce")
            df["week_num"]      = pd.to_numeric(df["week_num"], errors="coerce")
            df["cohort_size"]   = pd.to_numeric(df["cohort_size"], errors="coerce")
            df["retained"]      = pd.to_numeric(df["retained"], errors="coerce")

            pivot_pct = df.pivot_table(index="cohort_week", columns="week_num",
                                       values="retention_pct", aggfunc="first")
            pivot_abs = df.pivot_table(index="cohort_week", columns="week_num",
                                       values="retained", aggfunc="first")
            sizes = df[df["week_num"] == 0].set_index("cohort_week")["cohort_size"]

            for ck in sorted(df["cohort_week"].unique()):
                label = cohort_label(pd.Timestamp(ck).to_pydatetime())
                row_pct = []
                row_abs = []
                for w in range(0, max_weeks + 1):
                    v_pct = pivot_pct.loc[ck, w] if (ck in pivot_pct.index and w in pivot_pct.columns) else None
                    v_abs = pivot_abs.loc[ck, w] if (ck in pivot_abs.index and w in pivot_abs.columns) else None
                    row_pct.append(None if pd.isna(v_pct) else round(float(v_pct), 1))
                    row_abs.append(None if pd.isna(v_abs) else int(v_abs))
                cohort_rows.append({"label": label, "row": row_pct})
                users_rows.append({"label": label, "values": [int(sizes.get(ck, 0))] + row_abs[1:]})

            # curva média
            avg = df.groupby("week_num")["retention_pct"].mean().reset_index().sort_values("week_num")
            avg = avg[avg["week_num"] <= max_weeks]
            pts = [100.0] + [round(float(v), 1) for v in avg[avg["week_num"] > 0]["retention_pct"].tolist()]
            lbls = ["W0"] + [f"W{int(w)}" for w in avg[avg["week_num"] > 0]["week_num"].tolist()]
            avg_curve_points = pts
            avg_curve_labels = lbls
    except Exception:
        pass

    periodo_label = {
        "Ano": str(dt_ini.year),
        "Mês": dt_ini.strftime("%b/%y"),
    }.get(safra_tipo, f"{dt_ini.strftime('%d/%m')}–{dt_fim.strftime('%d/%m/%y')}")

    return {
        "filters": {
            "granularidade": safra_tipo,
            "base":          base_ret,
            "periodo":       periodo_label,
            "data_inicio":   dt_ini.strftime("%d/%m/%Y"),
            "data_fim":      dt_fim.strftime("%d/%m/%Y"),
            "atualizado":    datetime.now().strftime("%d/%m/%Y · %H:%M"),
        },
        "header": {
            "eyebrow":      "Painel · Engajamento",
            "title":        "Retenção",
            "lede":         "Cohorts, recorrência e sobrevivência de usuários — coortes semanais a partir do registro.",
            "base_analise": base_ret,
            "comparativo":  "Período anterior",
        },
        "user": {"name": "Analytics", "role": "EXA", "initials": "EX"},
        "nav": [
            {"key": "onboarding",  "label": "Onboarding",  "icon": "funnel"},
            {"key": "retencao",    "label": "Retenção",    "icon": "retention", "active": True},
            {"key": "performance", "label": "Performance", "icon": "perf"},
            {"key": "chat",        "label": "Chat",        "icon": "chat"},
        ],
        "kpis": kpis,
        "cohortHeader": cohort_header,
        "cohort": cohort_rows or [{"label": "—", "row": [None] * (max_weeks + 1)}],
        "curve": {
            "title":    "Curva de Retenção Média",
            "subtitle": f"Sobrevivência média dos cohorts · W0 → W{max_weeks}",
            "points":   avg_curve_points,
            "labels":   avg_curve_labels,
        },
        "usersTable": {
            "title":    "Tabela de Cohorts",
            "subtitle": "Volumes absolutos de usuários por semana",
            "cols":     ["Usuários W0"] + [f"W{w}" for w in range(1, max_weeks + 1)],
            "rows":     users_rows or [{"label": "—", "values": [0] * (max_weeks + 1)}],
        },
    }


# ── Render ────────────────────────────────────────────────────────────────────
with st.spinner("Carregando dashboard..."):
    payload = build_payload()

try:
    template = load_template("dashboard_retencao.html")
    html = template.replace("__EXA_DATA_JSON__", json.dumps(payload, ensure_ascii=False), 1)
    html = html.replace("</head>", _EMBED_OVERRIDES)
    components.html(html, height=800, scrolling=True)
except Exception as exc:
    st.error(f"Erro ao montar dashboard: {exc}")
    st.json(payload)
