import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from core.sql_agent import generate_sql
from core.databricks_client import execute_query, test_connection
from core.catalog_loader import reload_catalog, build_catalog_context, build_rules_context


def _try_chart(df: pd.DataFrame):
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if len(df) > 1 and len(numeric_cols) >= 1:
        non_numeric = [c for c in df.columns if c not in numeric_cols]
        if non_numeric:
            try:
                chart_df = df.set_index(non_numeric[0])[numeric_cols[:3]]
                st.bar_chart(chart_df)
            except Exception:
                pass


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.caption("Analytics · Databricks · IA")
    st.markdown("---")

    st.subheader("Conexão")
    if st.button("Testar conexão", icon=":material/sensors:", use_container_width=True):
        with st.spinner("Testando..."):
            ok, msg = test_connection()
        if ok:
            st.success(msg)
        else:
            st.error(f"Falha: {msg}")

    st.markdown("---")

    st.subheader("Catálogo")
    if st.button("Recarregar catálogo", icon=":material/refresh:", use_container_width=True):
        reload_catalog()
        st.success("Catálogo recarregado!")

    with st.expander("Ver catálogo"):
        st.markdown(build_catalog_context())

    with st.expander("Ver regras de negócio"):
        st.markdown(build_rules_context())

    st.markdown("---")

    if st.button("Limpar conversa", icon=":material/delete:", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption("Edite os YAML para ajustar o comportamento do agente.")

# ── Estado da sessão ──────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Cabeçalho ─────────────────────────────────────────────────────────────────
st.markdown('<h1 class="page-title">Chat <em>Analytics</em></h1>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Faça perguntas em português sobre os dados. O agente gera e executa o SQL automaticamente.</p>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── Histórico do chat ─────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sql" in msg:
            with st.expander("🔍 SQL gerado"):
                st.code(msg["sql"], language="sql")
        if "dataframe" in msg:
            df = pd.DataFrame(msg["dataframe"])
            st.dataframe(df, use_container_width=True)
            _try_chart(df)
        if "error" in msg:
            st.error(msg["error"])

# ── Input do usuário ──────────────────────────────────────────────────────────
if prompt := st.chat_input("Ex: Quais as 10 marcas com mais ganhos no casino nos últimos 7 dias?"):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Gerando SQL..."):
            history = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[:-1]
            ]
            sql, err = generate_sql(prompt, history)

        if err:
            st.error(f"Erro ao gerar SQL: {err}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Não foi possível gerar a query.",
                "error": err,
            })
        else:
            with st.expander("🔍 SQL gerado", expanded=True):
                st.code(sql, language="sql")

            with st.spinner("Executando no Databricks..."):
                try:
                    df = execute_query(sql)
                    st.success(f"{len(df):,} registros retornados")
                    st.dataframe(df, use_container_width=True)
                    _try_chart(df)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Query executada com sucesso. {len(df):,} registros retornados.",
                        "sql": sql,
                        "dataframe": df.to_dict("records"),
                    })
                except Exception as e:
                    st.error(f"Erro ao executar: {e}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "Erro ao executar a query.",
                        "sql": sql,
                        "error": str(e),
                    })
