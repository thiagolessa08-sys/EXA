import os
import re
import anthropic
from dotenv import load_dotenv
from core.catalog_loader import build_catalog_context, build_rules_context

load_dotenv()

_client = None

SYSTEM_PROMPT = """Você é um especialista em SQL para Databricks (Apache Spark SQL).
Sua função é converter perguntas em linguagem natural em queries SQL precisas e performáticas.

{catalog}

{rules}

## Instruções
- Responda APENAS com o código SQL, sem explicações, sem markdown, sem ```sql.
- Use apenas SELECT. Nunca gere INSERT, UPDATE, DELETE, DROP, CREATE ou qualquer DDL.
- Utilize os índices indicados no catálogo para filtros WHERE, garantindo performance.
- Use a sintaxe Databricks SQL / Spark SQL (ex: DATEADD, CURRENT_DATE(), etc).
- Se a pergunta for ambígua, assuma a interpretação mais provável com base nas regras de negócio.
- Sempre referencie tabelas com o caminho completo: catalog.schema.tabela
"""


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def _build_system_prompt() -> str:
    return SYSTEM_PROMPT.format(
        catalog=build_catalog_context(),
        rules=build_rules_context(),
    )


def _extract_sql(text: str) -> str:
    text = text.strip()
    # Remove blocos markdown se o modelo incluir por engano
    text = re.sub(r"```sql\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```\s*", "", text)
    return text.strip()


def _is_safe_sql(sql: str) -> bool:
    forbidden = r"\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|MERGE|REPLACE)\b"
    return not re.search(forbidden, sql, re.IGNORECASE)


def generate_sql(question: str, history: list[dict]) -> tuple[str, str | None]:
    """
    Retorna (sql, erro).
    Se erro não for None, a geração falhou.
    """
    client = _get_client()
    system = _build_system_prompt()

    messages = []
    for msg in history[-10:]:  # últimas 10 mensagens para contexto
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system,
            messages=messages,
        )
        raw = response.content[0].text
        sql = _extract_sql(raw)

        if not _is_safe_sql(sql):
            return "", "Query bloqueada: apenas SELECT é permitido."

        return sql, None

    except Exception as e:
        return "", str(e)
