# South Park Common's Arc-Agi jabs

---

This repo houses hacky code & data towards taking a shot at improving on arc-agi benchmarks.
This repo is a stripped down version of [this template repo](https://github.com/hayabhay/fastapi-streamlit-starter/issues).

This uses -
1. [Poetry](https://python-poetry.org/) for package management (`poetry` is quite complicated when it comes to ML projects so be wary of that when this is used for ML projects)
2. `ruff` as a lightweight linter/formatter to `black`, `flake8` & `isort`.
3. `pre-commit` hooks to run `ruff` & other checks before committing.
4. `.github` workflows for CI/CD.

## Quickstart

First, clone the repo:

```bash
git clone <repo-url>
```

Install `poetry` with `pipx`:

```bash
pipx install poetry
```

Now install the dependencies:

```bash
git clone
poetry sync --with=dev,ui
```

The `--with=dev,ui` flag is used to install the development dependencies as well. This is needed to run the Streamlit app.

> Note: Streamlit is only available in dev mode which is set in the `pyproject.toml` file. This is to keep the production API container as small as possible. Feel free to change this as needed.

Now, you can run the Streamlit development UI.

```bash
cd ui
poetry run streamlit run 01_🏠_Home.py
``
