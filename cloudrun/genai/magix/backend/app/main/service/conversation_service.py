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

import uuid
import copy
import logging
import sqlalchemy
from sqlalchemy.orm import Session
from http import HTTPStatus
from app.main.model.conversation import ConversationSQL
from app.main.util.utils import get_file_from_gcs, write_file_to_gcs
from db.config import connect_with_connector
from app.main.model.apiresponse import ApiResponse

from sqlalchemy import desc

# cursor = connect_to_db()
engine = connect_with_connector()


def create_conversation_id():
    """Creates a new conversation id.
    Args:
        NA
    Returns:
        Newly created conversation id.
    """
    new_id = str(uuid.uuid4())
    return new_id


def create_conversation(conversation_id, user_email, title, llm_name, llm_params):
    """Creates a new conversation object.
    Args:
        conversation_id: Conversation Id
        user_email: User email
        title: Conversation title
        llm_name: LLM name
        llm_params: LLM parameters
    Returns:
        Newly created conversation object.
    """
    try:
        conversation = ConversationSQL(
            id=conversation_id,
            user_email=user_email,
            title=title,
            llm_name=llm_name,
            llm_params=llm_params,
        )
        session = Session(engine, expire_on_commit=False)
        session.add(conversation)
        session.commit()
        session.close()
        logging.info(f"Conversation created: {conversation}")

        return conversation.to_dict()

    except sqlalchemy.exc.OperationalError as e:
        logging.error(f"Error creating conersation: {e}")
        response = ApiResponse(
            data={"error": {"type": type(e).__name__, "message": str(e)}},
            message="Error creating conversation",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        return response.to_response()
    
def update_conversation_title(conversation_id, title):
    """Creates a new conversation object.
    Args:
        conversation_id: Conversation Id
        title: Conversation title
    Returns:
        Updated conversation object.
    """
    try:
        session = Session(engine, expire_on_commit=False)
        conversation = session.query(ConversationSQL).filter_by(id=conversation_id).first()

        if conversation:
            conversation.title = title 
            session.commit()
            logging.info("Title updated successfully!")
        else:
            logging.info("Conversation not found.")

        session.close()
        
        return conversation.to_dict()
    
    except sqlalchemy.exc.OperationalError as e:
        logging.error(f"Error updating conversation title: {e}")
        response = ApiResponse(
            data={"error": {"type": type(e).__name__, "message": str(e)}},
            message="Error updating conversation title",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        return response.to_response()


def get_conversation(conversation_id):
    """Returns a conversation.
    Args:
        conversation_id: Conversation id
    Returns:
        A conversation object.
    """
    try:
        with Session(engine, expire_on_commit=False) as session:
            conversation = (
                session.query(ConversationSQL)
                .filter(ConversationSQL.id == conversation_id)
                .first()
            )
        return conversation.to_dict()

    except sqlalchemy.exc.OperationalError as e:
        logging.error(f"Error getting conversation info: {e}")
        response = ApiResponse(
            data={"error": {"type": type(e).__name__, "message": str(e)}},
            message="Database error occurred",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        return response.to_response()


# TODO: How to get user_email for this method? Fixing for now
def get_conversation_settings(conversation_id):
    """Returns LLM settings for a conversation id.
    Args:
        id: Conversation Id
    Returns:
        Returns a dictionary containing llm settings.
    """
    try:
        llm_settings = get_file_from_gcs(
            conversation_id=conversation_id, file_name="llm-settings"
        )
        return llm_settings
    except Exception as e:
        response = ApiResponse(
            data={"error": {"type": type(e).__name__, "message": str(e)}},
            message="Error in fetching conversation settings.",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        return response.to_response()


def update_conversation_settings(conversation_id, data):
    try:
        llm_settings = get_file_from_gcs(
            conversation_id=conversation_id, file_name="llm-settings"
        )
        if llm_settings == {}:
            return post_conversation_settings(
                conversation_id,
                llm_name=data.get("llm_name"),
                llm_params=data.get("llm_params"),
            )
        return update_conversation_settings_gcs(llm_settings, data)
    except Exception as e:
        logging.error(f"Error while updating llm settings - {e}")
        response = ApiResponse(
            HTTPStatus.NOT_FOUND,
            message=f"Error while updating llm settings - {e}",
        )
        return response.to_response()


def update_conversation_settings_gcs(current_settings, updated_settings):
    """Updates LLM settings for a conversation in GCS bucket
    Args:
        current_settings: Current llm settings retrived from GCS bucket.
        updated_settings: Updated llm settings based on PATCH request.
    Returns:
        Returns a dictionary containing llm settings.
    """
    new_settings = copy.deepcopy(current_settings)
    for key, value in updated_settings.items():
        new_settings[key] = value
    logging.info("Updated settings - ", new_settings)
    response = write_file_to_gcs(
        conversation_id=current_settings["id"],
        data=new_settings,
        file_name="llm-settings",
    )
    return response


def post_conversation_settings(
    conversation_id,
    user_email="user@example.com",
    title="Untitled Chat",
    llm_name="Gemini",
    llm_params={
        "temp": 0.1,
        "max_tokens": 1000
        },
):
    """Creates a new conversation and llm settings for the conversation.
    Args:
        id: Conversation Id
        user_email: User email
        title: Conversation title
        llm_name: LLM name
        llm_params: LLM parameters
    Returns:
        Response of llm-settings file creation in GCS.
    """
    try:
        conversation = create_conversation(
            conversation_id, user_email, title, llm_name, llm_params
        )
        response = write_file_to_gcs(
            conversation_id=conversation_id, data=conversation, file_name="llm-settings"
        )
        return response
    except Exception as e:
        logging.error(f"An error occurred while posting the conversation settings: {e}")
        return {"error": "Error in post conversation settings"}, 400


def get_user_conversations(user_email, offset, limit):
    """Returns all conversations for a specific user email.
    Args:
        user_email: User email
    Returns:
        A list of conversations for the given user.
    """
    try:
        with Session(engine, expire_on_commit=False) as session:
            conversations = (
                session.query(ConversationSQL)
                .filter(ConversationSQL.user_email == user_email)
                .order_by(desc(ConversationSQL.created_at))
                .offset(offset)
                .limit(limit)
                .all()
            )
            user_conversations = [row.to_dict() for row in conversations]
        return user_conversations

    except sqlalchemy.exc.OperationalError as e:
        logging.error(f"Error getting user conversations: {e}")
        response = ApiResponse(
            data={"error": {"type": type(e).__name__, "message": str(e)}},
            message="Database error occurred",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        return response.to_response()
