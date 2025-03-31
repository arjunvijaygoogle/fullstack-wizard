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

from flask import request, jsonify, Response
from http import HTTPStatus
from flask_cors import cross_origin
import logging
from app.main import bp
from app.main.service.conversation_service import (
    get_user_conversations,
    create_conversation_id,
    get_conversation_settings,
    post_conversation_settings,
    update_conversation_settings,
    get_conversation,
)
from app.main.service.message_service import (
    get_messages_for_conversation,
    post_message,
)
from app.main.util.utils import get_file_from_gcs
from app.main.model.apiresponse import ApiResponse


@bp.route("/conversations", methods=["POST", "GET"])
def get_user_conversations_route():
    """Get user Conversations controller
    Returns:
        All conversations of the user
    """
    if request.method == "GET":
        user_email = request.args.get("userEmail")
        if not user_email:
            response = ApiResponse(
                HTTPStatus.BAD_REQUEST, message="User email is required"
            )
            return response.to_response()
        conversation_id = request.args.get("id")
        if not conversation_id:
            offset = request.args.get("offset", default=0, type=int)
            limit = request.args.get("limit", type=int)
            print(f"Received offset: {offset}, limit: {limit}")
            user_conversations = get_user_conversations(user_email, offset, limit)
        else:
            user_conversations = get_conversation(conversation_id)
        return jsonify(user_conversations)
    else:
        #AVTODO it seems useless
        id = create_conversation_id()
        return id


@bp.route(
    "/conversations/<string:conversation_id>/settings", methods=["POST", "GET", "PATCH"]
)
def conversation_settings(conversation_id):
    """Conversation setting controller
    Args:
        conversation_id - Conversation ID
    Returns:
        Newly created conversation id.
    """

    if request.method == "GET":
        all_messages = get_conversation_settings(conversation_id)
        return all_messages
    elif request.method == "PATCH":
        data = request.get_json()
        if data:
            return update_conversation_settings(conversation_id, data)
        else:
            response = ApiResponse(HTTPStatus.BAD_REQUEST, message="Missing argument")
            return response.to_response()

    elif request.method == "POST":
        data = request.get_json()
        if data and "llm_name" in data and "llm_params" in data and "userEmail" in data:
            llm_name = data["llm_name"]
            llm_params = data["llm_params"]
            user_email = data["userEmail"]
            return post_conversation_settings(
                conversation_id, user_email, llm_name, llm_params
            )
        else:
            response = ApiResponse(HTTPStatus.BAD_REQUEST, message="Missing argument")
            return response.to_response()


@bp.route("/conversations/<string:conversation_id>/messages", methods=["POST", "GET"])
@cross_origin()
def get_conversation_messages_route(conversation_id):
    """Conversation message controller
    Args:
        conversation_id - Conversation ID
    Returns:
        Response from LLM
    """
    if request.method == "GET":
        all_messages = get_messages_for_conversation(conversation_id)
        return all_messages
    elif request.method == "POST":
        data = request.get_json()
        if data is not None and "role" in data and "message" in data:
            logging.debug("CONVERSATION ID: ", conversation_id)
            return Response(
                post_message(conversation_id, data), mimetype="application/json"
            )
        else:
            response = ApiResponse(HTTPStatus.BAD_REQUEST, message="Missing argument")
            return response.to_response()
