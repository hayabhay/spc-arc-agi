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
## Docker - Local Development

To run the Streamlit app in a Docker container, you can use the included `Dockerfile`:

```bash
docker compose -f docker-compose.local.yml up
```

The above paradigm is meant for development purposes.

```bash
docker compose -f docker-compose.production.yml build
```

## Deployment

These are instructions for deploying the container on Google Cloud Run.
You can also use more bare-metal solutions like Kubernetes etc. and/or other cloud providers.

### Google Cloud Run


#### Google SDK Setup

0.1. This assumes you have a Google Cloud account and have the `gcloud` CLI installed.
If not, you can follow the instructions [here](https://cloud.google.com/sdk/docs/install).
If you do, update it to the latest version:

```bash
gcloud components update
```

You may have to authenticate with your Google Cloud account:

```bash
gcloud auth login
```

0.2. Create a new google cloud project either from the GUI or using the CLI:

```bash
gcloud projects create my-project
```

0.3. Set the project as the default project:

```bash
gcloud config set project my-project
```

Note: If you have multiple projects, you can switch between them using the above command. Be weary of the project you are currently using to avoid accidental pushes to the wrong project.


#### Google Project Setup

1.1. Enable the Cloud Run API (you can do this from the GUI as well) - this is needed to to deploy the container.

```bash
gcloud services enable run.googleapis.com
```

1.2. Enable the Artifact Registry API - this is needed to push the container to the Google Artifact Registry.

```bash
gcloud services enable artifactregistry.googleapis.com
```

Note: You can also use Google Cloud Build to build and push the container to the registry. This is a more automated way of doing things. You can find more information [here](https://cloud.google.com/cloud-build/docs/quickstart-docker).


1.3 Set up secrets manager - this is needed to store secrets like API keys etc.

- Enable the Secret Manager API:
```bash
gcloud services enable secretmanager.googleapis.com
```

- Create a secrets file
```bash
gcloud secrets create <secret-id> --replication-policy="automatic"
```

- Add the `.env` to the secrets
```bash
gcloud secrets versions add <secret-id> --data-file=.env
```

NOTE: The service account that runs the Cloud Run service needs to have the `Secret Manager Secret Accessor` role to access the secrets. This can be done on the GCP Console in the IAM & Admin section or using the CLI

```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member=serviceAccount:YOUR_SERVICE_ACCOUNT_EMAIL \
    --role=roles/secretmanager.secretAccessor
```

#### Build & Push Container

2.0 Create an artifact registry repository.

After enabling artifact registry, [you can create a repository using the GUI or the CLI](https://cloud.google.com/artifact-registry/docs/docker/store-docker-container-images).

You can also check if this is enabled & list the repositories:

```bash
gcloud artifacts repositories list
```

2.1. Build & tag the container image

```bash
docker build --tag us-west1-docker.pkg.dev/<my-project>/<repo>/myapp-prod .
```


2.2. Push the container image to the Google Artifact Registry:

```bash
docker push us-west1-docker.pkg.dev/<my-project>/<repo>/myapp-prod
```

#### Deploy Container

3.1. Deploy the container to Google Cloud Run:

```bash
gcloud run deploy my-fastapi-app \
    --image gcr.io/my-fastapi-project/myapp-prod \
    --platform managed \
    --region <region> \
    --allow-unauthenticated \
    --update-secrets=<secret-id>:latest
```

Note: Secrets can be accessed from within the app or can be injected in as environment variables to the container. The latter is recommended and the created-secret `.env` [file can be mounted using an `--update-secrets` flag](https://cloud.google.com/run/docs/configuring/services/secrets#gcloud).

Configurations like region, autoscaling, instance size etc. can be set as needed. You can find more information [here](https://cloud.google.com/sdk/gcloud/reference/run/deploy).

3.2. Once the deployment is complete, you will get a URL where the container is deployed. You can access the FastAPI app from this URL.

3.3. You can also set up a custom domain for the Cloud Run service. You can find more information [here](https://cloud.google.com/run/docs/mapping-custom-domains).

#### Cleanup

4.1. To delete the Cloud Run service:

```bash
gcloud run services delete my-fastapi-app
```

4.2. To delete the container image from the Google Artifact Registry:

```bash
gcloud container images delete us-west1-docker.pkg.dev/<my-project>/<repo_name>/myapp-prod
```

4.3. To delete the Google Cloud project:

```bash
gcloud projects delete my-project
```
