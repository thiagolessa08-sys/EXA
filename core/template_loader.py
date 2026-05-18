import streamlit as st
from pathlib import Path


@st.cache_resource
def load_template(filename: str) -> str:
    """Lê e cacheia template HTML pelo nome do arquivo. Cache por argumento evita colisão entre páginas."""
    p = Path(__file__).parent.parent / "static" / filename
    return p.read_text(encoding="utf-8")
