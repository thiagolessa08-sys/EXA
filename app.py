import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

st.set_page_config(
    page_title="EXA Analytics",
    page_icon="📊",
    layout="wide",
)

pg = st.navigation([
    st.Page("pages/1_📈_Onboarding.py",  title="Onboarding",  icon=":material/how_to_reg:", default=True),
    st.Page("pages/2_🔄_Retencao.py",    title="Retenção",    icon=":material/loop:"),
    st.Page("pages/3_💰_Performance.py", title="Performance", icon=":material/bar_chart:"),
    st.Page("pages/4_💬_Chat.py",         title="Chat",        icon=":material/forum:"),
])
pg.run()
