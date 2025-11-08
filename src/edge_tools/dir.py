from pathlib import Path
from jinja2 import Template

SQL_DIR = Path(".").resolve() / "sql"

def load_query(name: str) -> Template:
    path = SQL_DIR / name
    text = path.read_text(encoding="utf-8")
    return Template(text)



def render_query(template: Template, **params):
    sql = template.render(**params)
    return sql


def get_sql_query(name: str, **params) -> str:
    template = load_query(name)
    sql = render_query(template, **params)
    return sql


