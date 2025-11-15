from pathlib import Path
from jinja2 import Template
import logging

logger = logging.getLogger(__name__)

SQL_DIR = Path(".").resolve() / "sql"

def load_query(name: str) -> Template:
    """Load a SQL query template from the sql directory.
    
    Args:
        name (str): The filename of the SQL query template. 
    Returns:
        Template: A Jinja2 Template object containing the SQL query.
    """
    path = SQL_DIR / name
    text = path.read_text(encoding="utf-8")
    return Template(text)



def render_query(template: Template, **params):
    """Render a SQL query template with the given parameters.
    Args:
        template (Template): A Jinja2 Template object.
        **params: Parameters to render the template with.
    Returns:
        str: The rendered SQL query.        
    """
    sql = template.render(**params)
    return sql

def check_if_sql_suffix(file_name: str) -> str:
    """
    Ensure the filename ends with '.sql'. If not, append it.
    """
    if not file_name.lower().endswith(".sql"):
        logger.debug("Filename missing .sql suffix, adding it.")
        return file_name + ".sql"

    logger.debug("Filename already has .sql suffix.")
    return file_name

def get_sql_query(file_name: str, **params) -> str:
    """Get a rendered SQL query from a template file.
    Args:
        name (str): The filename of the SQL query template.
        **params: Parameters to render the template with.
    Returns:
        str: The rendered SQL query.    
    """

    file_name = check_if_sql_suffix(file_name)

    # queries must be placed inside a 'sql' folder in the root directory
    template = load_query(file_name)
    sql = render_query(template, **params)
    return sql



if __name__=='__main__':
    pass