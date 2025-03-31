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

from http import HTTPStatus
import json
import logging
import sqlalchemy
from sqlalchemy.orm import Session
from app.main.model.llm import LLMTableSQL
from db.config import connect_with_connector
from app.main.model.apiresponse import ApiResponse


engine = connect_with_connector()


def get_llms():
    """Returns all LLMs.
    Returns:
      A list of LLM objects.
    """
    try:
        session = Session(engine)
        llms = session.query(LLMTableSQL).all()
        llms_list = [llm.to_dict() for llm in llms]
        session.close()
        return llms_list

    except sqlalchemy.exc.OperationalError as e:
        logging.error(f"Error getting llms: {e}")
        response = ApiResponse(
            data={"error": {"type": type(e).__name__, "message": str(e)}},
            message="Error in fetching conversation settings.",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        return response.to_response()


def create_llm(
    name, display_name, provider, model_name, version, params, is_active=True
):
    """Creates a new llm object.
    Args:
        name: LLM name
        display_name: LLM display name
        provider: LLM provider
        model_name: LLM model name
        version: LLM version
        params: LLM fine tuning parameters
        is_active: LLM is active
    Returns:
        Newly created LLM object or error object.
    """
    try:
        llm = LLMTableSQL(
            name, display_name, provider, model_name, version, params, is_active
        )
        session = Session(engine, expire_on_commit=False)
        session.add(llm)
        session.commit()
        session.close()

        logging.info(f"LLM added: {name}")
        return llm.to_dict()

    except sqlalchemy.exc.SQLAlchemyError as e:
        logging.error(f"Error adding LLM: {e}")
        response = ApiResponse(
            data={"error": {"type": type(e).__name__, "message": str(e)}},
            message="Database error occurred",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,  # Or another appropriate status code
        )
        return response.to_response()


def update_llm(name, is_active):
    """Updates llm object.
    Args:
        name: LLM name (identifier)
        display_name: LLM display name
        provider: LLM provider
        model_name: LLM model name
        version: LLM version
        params: LLM fine tuning parameters
        is_active: LLM is active
    Returns:
        Response object.
    """
    try:
        session = Session(engine, expire_on_commit=False)
        llm = session.query(LLMTableSQL).filter_by(name=name).first()

        if not llm:
            logging.warning(f"No LLM record found with name: {name}.")
            response = ApiResponse(
                data={
                    "error": {
                        "type": "NoRowsUpdated",
                        "message": "No LLM record found with the given name.",
                    }
                },
                message="Error",
                status_code=HTTPStatus.NOT_FOUND,
            )
            return response.to_response()

        llm.is_active = is_active

        session.commit()
        session.close()

        logging.info(f"LLM updated successfully: {name}")
        response = ApiResponse(
            message="LLM updated successfully", status_code=HTTPStatus.OK
        )
        return response.to_response()

    except Exception as e:
        logging.error(f"Error updating LLM: {e}")
        response = ApiResponse(
            data={"error": {"type": type(e).__name__, "message": str(e)}},
            message="Database error occurred",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,  # Or another appropriate status code
        )
        return response.to_response()


def delete_llm(name):
    """Updates llm object.
    Args:
        name: LLM name (identifier)
    Returns:
        Response object.
    """
    try:
        session = Session(engine, expire_on_commit=False)
        llm = session.query(LLMTableSQL).filter_by(name=name).first()
        if not llm:
            logging.warning(f"No LLM record found with name: {name}.")
            response = ApiResponse(
                data={
                    "error": {
                        "type": "NoRowsUpdated",
                        "message": "No LLM record found with the given name.",
                    }
                },
                message="Error",
                status_code=HTTPStatus.NOT_FOUND,
            )
            return response.to_response()

        session.delete(llm)
        session.commit()
        session.close()
        logging.info(f"LLM deleted: {name}")
        response = ApiResponse(
            message="LLM deleted successfully", status_code=HTTPStatus.OK
        )
        return response.to_response()

    except Exception as e:
        logging.error(f"Error deleting LLM: {e}")
        response = ApiResponse(
            data={"error": {"type": type(e).__name__, "message": str(e)}},
            message="Database error occurred",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,  # Or another appropriate status code
        )
        return response.to_response()


def is_llm_active(name):
    """Get admin status of LLM
    Args:
        name: LLM name
    Returns:
        boolean, if the llm is active or not
    """
    try:
        session = Session(engine)
        llm = session.query(LLMTableSQL).filter_by(name=name).first()
        session.close()
        if llm:
            return llm.to_dict().get("is_active")
        return {"error": "LLM Not Found."}

    except sqlalchemy.exc.OperationalError as e:
        logging.error(f"Error fetching details of llm: {e}")
        response = ApiResponse(
            data={"error": {"type": type(e).__name__, "message": str(e)}},
            message="Error fetching details of llm ",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        return response.to_response()
