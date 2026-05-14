import yaml
import functools
from pathlib import Path

CATALOG_PATH = Path(__file__).parent.parent / "catalog" / "data_catalog.yaml"
RULES_PATH = Path(__file__).parent.parent / "catalog" / "business_rules.yaml"


@functools.lru_cache(maxsize=1)
def load_catalog() -> dict:
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@functools.lru_cache(maxsize=1)
def load_rules() -> dict:
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def reload_catalog():
    load_catalog.cache_clear()
    load_rules.cache_clear()


def build_catalog_context() -> str:
    catalog = load_catalog()
    lines = ["## Tabelas disponíveis no Databricks\n"]

    for table_name, table_info in catalog.get("tables", {}).items():
        full_name = f"{table_info.get('catalog', 'workspace')}.{table_info.get('schema', 'default')}.{table_name}"
        lines.append(f"### {full_name}")
        lines.append(f"Descrição: {table_info.get('description', '')}")

        indexes = table_info.get("indexes", [])
        if indexes:
            lines.append(f"Índices (colunas para filtrar com melhor performance): {', '.join(indexes)}")

        columns = table_info.get("columns", {})
        if columns:
            lines.append("Colunas conhecidas:")
            for col_name, col_info in columns.items():
                lines.append(f"  - {col_name} ({col_info.get('type', 'unknown')}): {col_info.get('description', '')}")
        lines.append("")

    return "\n".join(lines)


def build_rules_context() -> str:
    rules_data = load_rules()
    rules = rules_data.get("rules", [])
    if not rules:
        return ""

    lines = ["## Regras de negócio obrigatórias\n"]
    for rule in rules:
        lines.append(f"- **{rule.get('name', '')}**: {rule.get('rule', '').strip()}")

    return "\n".join(lines)
