# --------------------------------------------------------------------------------
# ------------------ Base stage - used to build the application ------------------
# --------------------------------------------------------------------------------
# define an alias for the specific python version used in this file.
FROM docker.io/python:3.12.7-slim-bookworm AS python

# python
ENV PYTHONUNBUFFERED=1 \
  # prevents python creating .pyc files
  PYTHONDONTWRITEBYTECODE=1 \
  \
  # pip
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  \
  # poetry
  # https://python-poetry.org/docs/configuration/#using-environment-variables
  # make poetry install to this location
  POETRY_VERSION=1.8.3 \
  POETRY_HOME="/opt/poetry" \
  # make poetry create the virtual environment in the project's root
  # it gets named `.venv`
  POETRY_VIRTUALENVS_IN_PROJECT=true \
  # do not ask any interactive question
  POETRY_NO_INTERACTION=1 \
  \
  # paths
  # this is where our requirements + virtual environment will live
  PYSETUP_PATH="/opt/pysetup" \
  VENV_PATH="/opt/pysetup/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# --------------------------------------------------------------------------------
# --------- Build stage - to build deps + create our virtual environment ---------
# --------------------------------------------------------------------------------
FROM python AS python-build-stage

ARG BUILD_ENVIRONMENT=local

# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
  # deps for installing poetry
  curl \
  # dependencies for building Python packages
  build-essential \
  # psycopg dependencies
  libpq-dev

# Install Poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN --mount=type=cache,target=/root/.cache \
    curl -sSL https://install.python-poetry.org | python3 -

# NOTE: "We want to cache our requirements and only reinstall them when
# pyproject.toml or poetry.lock files change. Otherwise builds will be slow."
# (https://stackoverflow.com/questions/53835198/integrating-python-poetry-with-docker)
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN --mount=type=cache,target=/root/.cache \
    poetry install --sync --with=ui

# --------------------------------------------------------------------------------
# --------------- Run stage - used during development / testing ------------------
# --------------------------------------------------------------------------------
# Python 'run' stage
FROM python AS python-run-stage

ARG BUILD_ENVIRONMENT=prod
ARG APP_HOME=/ui

ENV BUILD_ENV=${BUILD_ENVIRONMENT}

# devcontainer dependencies and utils
RUN apt-get update && apt-get install --no-install-recommends -y \
  sudo git bash-completion nano ssh

# Create devcontainer user and add it to sudoers
RUN groupadd --gid 1000 dev-user \
  && useradd --uid 1000 --gid dev-user --shell /bin/bash --create-home dev-user \
  && echo dev-user ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/dev-user \
  && chmod 0440 /etc/sudoers.d/dev-user

# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
  # psycopg dependencies
  libpq-dev  \
  wait-for-it \
  # Translations dependencies
  gettext \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# copy in our built poetry + venv
WORKDIR $PYSETUP_PATH
COPY --from=python-build-stage $POETRY_HOME $POETRY_HOME
COPY --from=python-build-stage $PYSETUP_PATH $PYSETUP_PATH

# quicker install as runtime deps are already installed
RUN --mount=type=cache,target=/root/.cache \
    poetry install --sync --with=ui

COPY ./compose/production/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

WORKDIR ${APP_HOME}

# copy application code to WORKDIR
COPY ./ui ${APP_HOME}

CMD [ "/start" ]
