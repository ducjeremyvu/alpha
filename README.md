


there is a package with functions, gotta create env and then install the package.

``` 
# create/activate your venv first
pip install -e ".[dev]"
python -m ipykernel install --user --name edge-env --display-name "Python (edge)"

```
