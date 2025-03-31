# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
from google.cloud import storage


# # Example usage
# bucket_name = "your-bucket-name"
# user_email = "user@example.com"
# conversation_id = "12345"
# file_name = "my-file"


def get_file_from_gcs(
    conversation_id,
    file_name="message",
    bucket_name="navi-store",
    user_email="user@example.com",
):
    """Retrieves a file from a GCS path.

    Args:
        conversation_id: Unique identifier for the conversation.
        file_name: Name of the file to be written. It will either be message or llm-settings.
        bucket_name: Name of the GCS bucket.
        user_email: Email address of the user.

    Returns:
        The contents of the a file as a Python dictionary, or None if the file is not found.
    """

    blob_name = f"{user_email}/{conversation_id}/{file_name}.json"

    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        if not blob.exists():
            logging.error(f"File not found: gs://{bucket_name}/{blob_name}")
            return {}
        file_content_string = blob.download_as_string()
        file_content_dict = json.loads(file_content_string)
        return file_content_dict

    except Exception as e:
        logging.error(f"An error occurred while reading {blob_name} file from GCS: {e}")
        return {"error": "Failed to get file from GCS"}, 400


# # Example usage
# bucket_name = "your-bucket-name"
# user_email = "user@example.com"
# conversation_id = "12345"
# file_name = "my-file"
# json_data = {"message": "Hello from the JSON file!"}


def write_file_to_gcs(
    conversation_id,
    data,
    file_name="message",
    bucket_name="navi-store",
    user_email="user@example.com",
):
    """Writes a file to a GCS path.

    Args:
        conversation_id: Unique identifier for the conversation.
        data: The data to be written in the file.
        file_name: Name of the file to be written. It will either be message or llm-settings.
        bucket_name: Name of the GCS bucket.
        user_email: Email address of the user.

    Returns:
        A tuple of operation response and response code.
    """

    # TODO: Fixed for testing. Change later
    blob_name = f"{user_email}/{conversation_id}/{file_name}.json"

    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(json.dumps(data), content_type="application/json")
        logging.info(f"JSON data uploaded to: gs://{bucket_name}/{blob_name}")
        return {
            "message": f"JSON data uploaded to: gs://{bucket_name}/{blob_name}"
        }, 200

    except Exception as e:
        logging.error(f"An error occurred while writing {blob_name} file to GCS: {e}")
        return {
            "error": f"An error occurred while writing {blob_name} file to GCS"
        }, 400


# # Example usage:
# bucket_name = "your-bucket-name"
# user_email = "user@example.com"
# prefix = f"{user_email}/"  # Construct the path


def list_folders_in_gcs(
    bucket_name="navi-store", prefix="user@example.com/", delimiter="/"
):
    """Lists all folders (prefixes) in a GCS bucket under a given path.

    Args:
        bucket_name: Name of the GCS bucket.
        prefix: Path prefix to search for folders.
    """
    storage_client = storage.Client()  # Uses default credentials
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix, delimiter=delimiter)
    # running to consume blobs object, else prefixes can not be iterated
    for blob in blobs:
        _ = blob.name
    folders = []
    if delimiter:
        for prefix in blobs.prefixes:
            # prefix = user_email/conversation_id/
            folders.append(prefix.split("/")[1])
    # print("List of conversation folders in GCS - ", folders)
    return folders
