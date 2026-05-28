import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import io
import streamlit as st
import pandas as pd
from datetime import date

from core.databricks_client import execute_query
from core.theme import inject_theme

inject_theme()

st.title("📥 Exportar Dados")
st.markdown("---")

# ── Seção: Usuários de Maio ───────────────────────────────────────────────────
st.subheader("Usuários criados em Maio — com data de cadastro e FTD")
st.markdown(
    "Gera um Excel com todos os usuários cadastrados em Maio, "
    "a data de criação e a data/hora do primeiro depósito (FTD)."
)

# Seletor de ano (padrão: ano corrente)
ano_sel = st.selectbox("Ano", list(range(date.today().year, date.today().year - 3, -1)))
ini = f"{ano_sel}-05-01"
fim = f"{ano_sel}-05-31"

if st.button("🔄 Gerar relatório", type="primary"):
    with st.spinner("Consultando Databricks..."):
        try:
            q = f"""
            SELECT
                u.user_ext_id,
                u.core_registration_date                    AS data_criacao,
                MIN(d.dt_finalized)                         AS data_hora_ftd
            FROM workspace.default.v_users_summary u
            LEFT JOIN workspace.default.v_deposits_summary d
                   ON u.user_ext_id = d.user_ext_id
            WHERE u.core_registration_date
                  BETWEEN '{ini}' AND '{fim} 23:59:59'
            GROUP BY u.user_ext_id, u.core_registration_date
            ORDER BY u.core_registration_date
            """
            df = execute_query(q)

            if df.empty:
                st.warning(f"Nenhum usuário encontrado em Maio/{ano_sel}.")
            else:
                # Formata colunas
                df.columns = ["user_ext_id", "Data de Criação", "Data/Hora FTD"]

                st.success(f"✅ {len(df):,} usuários encontrados em Maio/{ano_sel}.".replace(",", "."))

                # Preview
                st.dataframe(df.head(100), use_container_width=True)
                if len(df) > 100:
                    st.caption(f"Exibindo as primeiras 100 linhas. O Excel conterá todos os {len(df):,} registros.".replace(",", "."))

                # Gera Excel em memória
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name=f"Maio_{ano_sel}")

                st.download_button(
                    label="⬇️ Baixar Excel",
                    data=buffer.getvalue(),
                    file_name=f"usuarios_maio_{ano_sel}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                )

        except Exception as e:
            st.error(f"Erro ao consultar Databricks: {e}")

# ── Separador ─────────────────────────────────────────────────────────────────
st.markdown("---")

# ── Seção genérica: exportar por período ──────────────────────────────────────
with st.expander("📅 Exportar por período personalizado"):
    col1, col2 = st.columns(2)
    with col1:
        dt_ini_custom = st.date_input("De", value=date(date.today().year, 5, 1), key="custom_ini")
    with col2:
        dt_fim_custom = st.date_input("Até", value=date(date.today().year, 5, 31), key="custom_fim")

    if st.button("🔄 Gerar relatório (período customizado)", key="btn_custom"):
        with st.spinner("Consultando Databricks..."):
            try:
                q2 = f"""
                SELECT
                    u.user_ext_id,
                    u.core_registration_date                    AS data_criacao,
                    MIN(d.dt_finalized)                         AS data_hora_ftd
                FROM workspace.default.v_users_summary u
                LEFT JOIN workspace.default.v_deposits_summary d
                       ON u.user_ext_id = d.user_ext_id
                WHERE u.core_registration_date
                      BETWEEN '{dt_ini_custom}' AND '{dt_fim_custom} 23:59:59'
                GROUP BY u.user_ext_id, u.core_registration_date
                ORDER BY u.core_registration_date
                """
                df2 = execute_query(q2)

                if df2.empty:
                    st.warning("Nenhum usuário encontrado no período selecionado.")
                else:
                    df2.columns = ["user_ext_id", "Data de Criação", "Data/Hora FTD"]
                    st.success(f"✅ {len(df2):,} usuários encontrados.".replace(",", "."))
                    st.dataframe(df2.head(100), use_container_width=True)

                    buffer2 = io.BytesIO()
                    with pd.ExcelWriter(buffer2, engine="openpyxl") as writer:
                        df2.to_excel(writer, index=False, sheet_name="Usuarios")

                    nome_arquivo = f"usuarios_{dt_ini_custom.strftime('%Y%m%d')}_{dt_fim_custom.strftime('%Y%m%d')}.xlsx"
                    st.download_button(
                        label="⬇️ Baixar Excel",
                        data=buffer2.getvalue(),
                        file_name=nome_arquivo,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="dl_custom",
                        type="primary",
                    )

            except Exception as e:
                st.error(f"Erro ao consultar Databricks: {e}")
