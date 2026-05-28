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

    safra_tipo = st.selectbox(
        "Granularidade",
        ["Mês", "Semana", "Dia", "Ano", "Data aberta"],
        key="cluster_gran",
    )

    today = date.today()
    if safra_tipo == "Ano":
        anos = list(range(today.year, today.year - 5, -1))
        ano_sel = st.selectbox("Ano", anos, key="cluster_ano")
        dt_ini = date(ano_sel, 1, 1)
        dt_fim = date(ano_sel, 12, 31) if ano_sel < today.year else today
    elif safra_tipo == "Mês":
        meses = pd.date_range(end=today, periods=24, freq="MS").strftime("%Y-%m").tolist()[::-1]
        mes_sel = st.selectbox("Mês", meses, key="cluster_mes")
        dt_ini = datetime.strptime(mes_sel, "%Y-%m").date()
        dt_fim = (dt_ini.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    elif safra_tipo == "Semana":
        semana_ini = today - timedelta(days=today.weekday())
        data_sel = st.date_input("Semana", value=semana_ini, key="cluster_sem")
        dt_ini = data_sel - timedelta(days=data_sel.weekday())
        dt_fim = dt_ini + timedelta(days=6)
    elif safra_tipo == "Dia":
        data_sel = st.date_input("Dia", value=today, key="cluster_dia")
        dt_ini = dt_fim = data_sel
    else:
        dt_ini = st.date_input("De", value=today - timedelta(days=30), key="cluster_de")
        dt_fim = st.date_input("Até", value=today, key="cluster_ate")

ini_str = str(dt_ini)
fim_str = str(dt_fim)


# ── Queries ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_clusters(ini: str, fim: str):
    """Classifica FTDs do período em clusters e retorna resumo por cluster."""
    q = f"""
    WITH all_ranked AS (
        SELECT
            d.user_ext_id,
            d.deposit_amount,
            d.dt_finalized,
            ROW_NUMBER() OVER (PARTITION BY d.user_ext_id ORDER BY d.dt_finalized ASC) AS rn
        FROM workspace.default.v_deposits_summary d
    ),
    ftd AS (
        SELECT
            r.user_ext_id,
            r.deposit_amount AS valor_ftd,
            r.dt_finalized   AS dt_ftd
        FROM all_ranked r
        WHERE r.rn = 1
          AND r.dt_finalized BETWEEN '{ini}' AND '{fim} 23:59:59'
    ),
    classified AS (
        SELECT
            u.user_ext_id,
            f.valor_ftd,
            CASE
                WHEN f.valor_ftd < 20
                THEN 'Baixo Propenso'
                WHEN u.core_user_gender IN ('M','Masculino','MALE','male','m')
                     AND FLOOR(DATEDIFF(CURRENT_DATE, u.user_birthdate) / 365.25) BETWEEN 35 AND 54
                     AND f.valor_ftd > 60
                     AND u.core_reg_state IN ('DF','RS','PE','PR','MG','RJ')
                THEN 'Alto Propenso'
                ELSE 'Médio Propenso'
            END AS cluster
        FROM workspace.default.v_users_summary u
        INNER JOIN ftd f ON u.user_ext_id = f.user_ext_id
    )
    SELECT
        cluster,
        COUNT(*)                      AS qtd,
        ROUND(AVG(valor_ftd), 2)      AS ticket_medio,
        ROUND(MIN(valor_ftd), 2)      AS ticket_min,
        ROUND(MAX(valor_ftd), 2)      AS ticket_max
    FROM classified
    GROUP BY cluster
    ORDER BY cluster
    """
    return execute_query(q)


@st.cache_data(ttl=300, show_spinner=False)
def load_score(ini: str, fim: str):
    """Indicadores de qualidade do lote TIM."""
    q = f"""
    WITH all_ranked AS (
        SELECT
            d.user_ext_id,
            d.deposit_amount,
            d.dt_finalized,
            ROW_NUMBER() OVER (PARTITION BY d.user_ext_id ORDER BY d.dt_finalized ASC) AS rn
        FROM workspace.default.v_deposits_summary d
    ),
    ftd AS (
        SELECT r.user_ext_id, r.deposit_amount AS valor_ftd
        FROM all_ranked r
        WHERE r.rn = 1
          AND r.dt_finalized BETWEEN '{ini}' AND '{fim} 23:59:59'
    )
    SELECT
        COUNT(*)                                                                           AS total_ftds,
        ROUND(COUNT(CASE WHEN f.valor_ftd >= 30 THEN 1 END) * 100.0 / NULLIF(COUNT(*),0), 1) AS pct_ticket_30,
        ROUND(COUNT(CASE WHEN u.core_user_gender IN ('M','Masculino','MALE','male','m')
                              AND FLOOR(DATEDIFF(CURRENT_DATE, u.user_birthdate)/365.25) BETWEEN 35 AND 54
                         THEN 1 END) * 100.0 / NULLIF(COUNT(*),0), 1)                    AS pct_homem_3554,
        ROUND(COUNT(CASE WHEN u.core_reg_state IN ('DF','RS','PE','PR','MG','RJ') THEN 1 END) * 100.0 / NULLIF(COUNT(*),0), 1) AS pct_tier_alto
    FROM ftd f
    INNER JOIN workspace.default.v_users_summary u ON f.user_ext_id = u.user_ext_id
    """
    return execute_query(q)


# ── Build payload ─────────────────────────────────────────────────────────────
def build_payload(ini: str, fim: str, granular: str) -> dict:
    # --- clusters
    cluster_map = {"Baixo Propenso": {"qtd": 0, "ticket_medio": 0, "ticket_min": 0, "ticket_max": 0},
                   "Médio Propenso": {"qtd": 0, "ticket_medio": 0, "ticket_min": 0, "ticket_max": 0},
                   "Alto Propenso":  {"qtd": 0, "ticket_medio": 0, "ticket_min": 0, "ticket_max": 0}}
    try:
        df_c = load_clusters(ini, fim)
        for _, row in df_c.iterrows():
            key = row["cluster"]
            if key in cluster_map:
                cluster_map[key] = {
                    "qtd":          int(row["qtd"] or 0),
                    "ticket_medio": float(row["ticket_medio"] or 0),
                    "ticket_min":   float(row["ticket_min"] or 0),
                    "ticket_max":   float(row["ticket_max"] or 0),
                }
    except Exception as e:
        st.error(f"Falha ao carregar clusters: {e}")

    total_ftds = sum(v["qtd"] for v in cluster_map.values())

    def pct_cluster(key):
        return cluster_map[key]["qtd"] / max(total_ftds, 1) * 100

    # --- score
    score_row = {"total_ftds": total_ftds, "pct_ticket_30": 0.0, "pct_homem_3554": 0.0, "pct_tier_alto": 0.0}
    try:
        df_s = load_score(ini, fim)
        if not df_s.empty:
            r = df_s.iloc[0]
            score_row = {
                "total_ftds":    int(r["total_ftds"] or 0),
                "pct_ticket_30": float(r["pct_ticket_30"] or 0),
                "pct_homem_3554": float(r["pct_homem_3554"] or 0),
                "pct_tier_alto": float(r["pct_tier_alto"] or 0),
            }
    except Exception as e:
        st.error(f"Falha ao carregar score: {e}")

    # Score calculation
    pts_ticket = 40 if score_row["pct_ticket_30"] >= 60 else 0
    pts_perfil  = 30 if score_row["pct_homem_3554"] >= 35 else 0
    pts_estado  = 30 if score_row["pct_tier_alto"] >= 50 else 0
    score_total = pts_ticket + pts_perfil + pts_estado

    if score_total >= 90:
        score_status, score_cor = "APROVADO", "good"
    elif score_total >= 60:
        score_status, score_cor = "ATENÇÃO", "warn"
    else:
        score_status, score_cor = "RECUSAR", "bad"

    periodo_label = {
        "Ano": str(dt_ini.year),
        "Mês": dt_ini.strftime("%b/%y"),
    }.get(granular, f"{dt_ini.strftime('%d/%m')}–{dt_fim.strftime('%d/%m/%y')}")

    return {
        "filters": {
            "granularidade": granular,
            "base":          "FTD",
            "periodo":       periodo_label,
            "data_inicio":   dt_ini.strftime("%d/%m/%Y"),
            "data_fim":      dt_fim.strftime("%d/%m/%Y"),
            "atualizado":    datetime.now().strftime("%d/%m/%Y · %H:%M"),
        },
        "header": {
            "eyebrow": "Painel · Aquisição",
            "title":   "Clusters",
            "lede":    "Classificação de FTDs em Baixo, Médio e Alto Propenso — auditoria diária de lotes TIM.",
            "base_analise": "Primeiro Depósito",
            "comparativo":  "Período anterior",
        },
        "user": {"name": "Analytics", "role": "EXA", "initials": "EX"},
        "nav": [
            {"key": "onboarding",  "label": "Onboarding",  "icon": "funnel"},
            {"key": "retencao",    "label": "Retenção",    "icon": "retention"},
            {"key": "performance", "label": "Performance", "icon": "perf"},
            {"key": "clusters",    "label": "Clusters",    "icon": "cluster", "active": True},
            {"key": "chat",        "label": "Chat",        "icon": "chat"},
        ],
        "resumo": {
            "total_ftds": fmt_int(total_ftds),
        },
        "clusters": [
            {
                "key":          "baixo",
                "label":        "Baixo Propenso",
                "badge":        "CORTAR",
                "badge_cor":    "bad",
                "regra":        "FTD < R$20 · Feminino com FTD < R$20 · Estados MA/AM/PI/MS/AL/RN com FTD < R$20",
                "qtd":          fmt_int(cluster_map["Baixo Propenso"]["qtd"]),
                "pct_base":     fmt_pct(pct_cluster("Baixo Propenso")),
                "ticket_medio": fmt_brl(cluster_map["Baixo Propenso"]["ticket_medio"]),
                "ticket_min":   fmt_brl(cluster_map["Baixo Propenso"]["ticket_min"]),
                "ticket_max":   fmt_brl(cluster_map["Baixo Propenso"]["ticket_max"]),
                "descricao":    "Usuário de baixíssimo potencial de LTV que consome CAC sem retorno relevante de GGR.",
                "color":        "#d62a39",
                "color_bg":     "#fbecee",
            },
            {
                "key":          "medio",
                "label":        "Médio Propenso",
                "badge":        "MONITORAR",
                "badge_cor":    "warn",
                "regra":        "Tudo que não é Baixo nem Alto Propenso",
                "qtd":          fmt_int(cluster_map["Médio Propenso"]["qtd"]),
                "pct_base":     fmt_pct(pct_cluster("Médio Propenso")),
                "ticket_medio": fmt_brl(cluster_map["Médio Propenso"]["ticket_medio"]),
                "ticket_min":   fmt_brl(cluster_map["Médio Propenso"]["ticket_min"]),
                "ticket_max":   fmt_brl(cluster_map["Médio Propenso"]["ticket_max"]),
                "descricao":    "Usuário recorrente com LTV moderado. 14,7% da base e 77% do GGR.",
                "color":        "#c66a00",
                "color_bg":     "#fff7ed",
            },
            {
                "key":          "alto",
                "label":        "Alto Propenso",
                "badge":        "PRIORIZAR",
                "badge_cor":    "good",
                "regra":        "Masculino 35–54 anos · FTD > R$60 · Estados DF/RS/PE/PR/MG/RJ",
                "qtd":          fmt_int(cluster_map["Alto Propenso"]["qtd"]),
                "pct_base":     fmt_pct(pct_cluster("Alto Propenso")),
                "ticket_medio": fmt_brl(cluster_map["Alto Propenso"]["ticket_medio"]),
                "ticket_min":   fmt_brl(cluster_map["Alto Propenso"]["ticket_min"]),
                "ticket_max":   fmt_brl(cluster_map["Alto Propenso"]["ticket_max"]),
                "descricao":    "Whale / Potencial. Apenas 2,6% da base, mas gera 59% do GGR.",
                "color":        "#1f9d57",
                "color_bg":     "#ecf6ef",
            },
        ],
        "score": {
            "total":   score_total,
            "status":  score_status,
            "cor":     score_cor,
            "acao": {
                "APROVADO": "Lote aprovado — qualidade confirmada. CAC justificado.",
                "ATENÇÃO":  "Aceitar com ressalva. Monitorar D+7 e D+30 antes de aprovar.",
                "RECUSAR":  "Acionar TIM formalmente para revisão do targeting.",
            }[score_status],
            "indicadores": [
                {
                    "label":     "% FTDs com ticket ≥ R$30",
                    "meta":      60.0,
                    "meta_lbl":  "> 60%",
                    "historico": "~37%",
                    "real":      float(score_row["pct_ticket_30"]),
                    "real_lbl":  fmt_pct(score_row["pct_ticket_30"]) + "%",
                    "pts_max":   40,
                    "pts":       pts_ticket,
                    "atingiu":   pts_ticket > 0,
                },
                {
                    "label":     "% Homem 35–54 anos",
                    "meta":      35.0,
                    "meta_lbl":  "> 35%",
                    "historico": "~31%",
                    "real":      float(score_row["pct_homem_3554"]),
                    "real_lbl":  fmt_pct(score_row["pct_homem_3554"]) + "%",
                    "pts_max":   30,
                    "pts":       pts_perfil,
                    "atingiu":   pts_perfil > 0,
                },
                {
                    "label":     "% Estados Tier Alto (DF+RS+PE+PR+MG+RJ)",
                    "meta":      50.0,
                    "meta_lbl":  "> 50%",
                    "historico": "~45%",
                    "real":      float(score_row["pct_tier_alto"]),
                    "real_lbl":  fmt_pct(score_row["pct_tier_alto"]) + "%",
                    "pts_max":   30,
                    "pts":       pts_estado,
                    "atingiu":   pts_estado > 0,
                },
            ],
        },
    }


# ── Render ────────────────────────────────────────────────────────────────────
with st.spinner("Carregando clusters..."):
    payload = build_payload(ini_str, fim_str, safra_tipo)

template = load_template("dashboard_clusters.html")
html = template.replace("__EXA_DATA_JSON__", json.dumps(payload, ensure_ascii=False))
html = html.replace("</head>", _EMBED_OVERRIDES)
components.html(html, height=1350, scrolling=False)
