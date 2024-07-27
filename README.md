# GlareDB Demo

<!-- TOC -->
* [GlareDB Demo](#glaredb-demo)
  * [Overview](#overview)
  * [Prerequisites](#prerequisites)
  * [Install](#install)
  * [Authenticate to GCP](#authenticate-to-gcp)
  * [Provision infrastructure](#provision-infrastructure)
  * [Execute demo](#execute-demo)
  * [Destroy infrastructure](#destroy-infrastructure)
<!-- TOC -->

## Overview

## Prerequisites

* [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
* [poetry](https://python-poetry.org/docs/#installation)
* [gcloud](https://cloud.google.com/sdk/docs/install)
* [terraform](https://developer.hashicorp.com/terraform/install)

## Install

```shell
npm install
poetry install
```

## Authenticate to GCP

```shell
gcloud auth login
gcloud auth application-default login 
```

## Provision infrastructure

```shell
export GCP_PROJECT=<project>
export GCP_REGION=<region>
npx cdktf deploy

# TODO: Get GlareDB to use Application Default Credentials.
#       We should not be exporting Service Account keys.
gcloud iam service-accounts keys create sa.json \
    --iam-account=glaredb-sa@${GCP_PROJECT}.iam.gserviceaccount.com

# TODO: Get GlareDB to use a separate billing project when querying bq-public-data.
#       For now we make a couple table copies.
bq query \
  --location=US \
  --use_legacy_sql=false \
  "create table ${GCP_PROJECT}.glaredb.Projects " \
  "copy \`bigquery-public-data.deps_dev_v1.Projects\`;"

bq query \
  --location=US \
  --use_legacy_sql=false \
  "create table ${GCP_PROJECT}.glaredb.PackageVersions " \
  "copy \`bigquery-public-data.deps_dev_v1.PackageVersions\`;"

# Export a table to GCS to demo a federated query between disparate data sources.
bq extract \
  --location=US \
  --destination_format=PARQUET \
  bigquery-public-data:deps_dev_v1.PackageVersionToProject \
  "gs://${GCP_PROJECT}-glaredb/PackageVersionToProject/*.parquet"
````

## Execute demo

```shell
poetry run jupyter notebook
```

Open [glaredb_demo.ipynb](glaredb_demo.ipynb).

## Destroy infrastructure

```shell
npx cdktf destroy
```
