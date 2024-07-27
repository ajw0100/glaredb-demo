#!/usr/bin/env python
# Copyright (c) 2024 AJ Welch <awelch0100@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""GlareDB Demo GCP infrastructure."""
import os

from cdktf import App, TerraformOutput, TerraformStack
from cdktf_cdktf_provider_google_beta.google_bigquery_dataset import (
    GoogleBigqueryDataset,
)
from cdktf_cdktf_provider_google_beta.google_bigquery_dataset_iam_member import (
    GoogleBigqueryDatasetIamMember,
)
from cdktf_cdktf_provider_google_beta.google_project_iam_member import (
    GoogleProjectIamMember,
)
from cdktf_cdktf_provider_google_beta.google_service_account import GoogleServiceAccount
from cdktf_cdktf_provider_google_beta.google_storage_bucket import GoogleStorageBucket
from cdktf_cdktf_provider_google_beta.google_storage_bucket_iam_member import (
    GoogleStorageBucketIamMember,
)
from cdktf_cdktf_provider_google_beta.provider import GoogleBetaProvider
from constructs import Construct


def _service_account(scope: Construct, project: str) -> GoogleServiceAccount:
    return GoogleServiceAccount(
        scope,
        "google_project_service_account",
        project=project,
        account_id="glaredb-sa",
        description="GlareDB Service Account.",
    )


def _storage(
    scope: Construct, project: str, region: str, service_account: GoogleServiceAccount
) -> GoogleStorageBucket:
    bucket = GoogleStorageBucket(
        scope,
        "google_storage_bucket",
        project=project,
        name=f"{project}-glaredb",
        location=region,
        force_destroy=True,
        uniform_bucket_level_access=True,
    )
    GoogleStorageBucketIamMember(
        scope,
        "google_storage_bucket_iam_member",
        bucket=bucket.name,
        role="roles/storage.admin",
        member=f"serviceAccount:{service_account.email}",
    )
    return bucket


def _bigquery(
    scope: Construct, project: str, service_account: GoogleServiceAccount
) -> GoogleBigqueryDataset:
    GoogleProjectIamMember(
        scope,
        "google_bigquery_job_user_role",
        project=project,
        role="roles/bigquery.jobUser",
        member=f"serviceAccount:{service_account.email}",
    )
    GoogleProjectIamMember(
        scope,
        "google_bigquery_read_session_role",
        project=project,
        role="roles/bigquery.readSessionUser",
        member=f"serviceAccount:{service_account.email}",
    )
    dataset = GoogleBigqueryDataset(
        scope,
        "google_bigquery_dataset",
        project=project,
        # Must be US because bigquery-public-data:deps_dev_v1.PackageVersions is in US
        location="US",
        dataset_id="glaredb",
        delete_contents_on_destroy=True,
    )
    GoogleBigqueryDatasetIamMember(
        scope,
        "google_bigquery_admin_role",
        project=project,
        dataset_id=dataset.dataset_id,
        role="roles/bigquery.admin",
        member=f"serviceAccount:{service_account.email}",
    )
    return dataset


class InfrastructureStack(TerraformStack):
    """Data stack."""

    def __init__(
        self, scope: Construct, id: str, project: str, region: str
    ):  # pylint: disable=redefined-builtin
        super().__init__(scope, id)
        GoogleBetaProvider(self, "google_beta_provider", region=region, project=project)
        service_account = _service_account(self, project)
        storage_bucket = _storage(self, project, region, service_account)
        bigquery_dataset = _bigquery(self, project, service_account)
        TerraformOutput(self, "service_account", value=service_account.email)
        TerraformOutput(self, "storage_bucket", value=storage_bucket.name)
        TerraformOutput(self, "bigquery_dataset", value=bigquery_dataset.dataset_id)


def main() -> None:
    project = os.getenv("GCP_PROJECT")
    region = os.getenv("GCP_REGION")
    if project is None or region is None:
        raise ValueError("GCP project and region must be specified.")
    app = App()
    InfrastructureStack(app, "infrastructure", project=project, region=region)
    app.synth()


if __name__ == "__main__":
    main()
