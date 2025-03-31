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
from app.main.model.message import Message
from app.main.service.conversation_service import (
    post_conversation_settings,
    get_conversation_settings,
    update_conversation_title,
    update_conversation_settings,
    get_conversation
)
from app.main.util.utils import (
    get_file_from_gcs,
    list_folders_in_gcs,
    write_file_to_gcs,
)
from app.main.model.llm import LLMBase, LLMFactory, GeminiLLM, CodestralLLM
from app.main.model.apiresponse import ApiResponse
from app.main.service.llm_service import is_llm_active


def create_message(role: str, message: str):
    """Creates a new message object.
    Args:
        role: Role of the message creator. Value will be either user or system.
        message: Message sent by entity represented by role.
                Prompt in case of user, response in case of system.
    Returns:
        Newly created message object.
    """
    message = Message(role, message)
    return message


def get_messages_for_conversation(conversation_id):
    """Returns messages corresponding to a particular conversation.
    Args:
      conversation_id: Conversation Id
    Returns:
      A list of messages.
    """
    conversation_messages = get_file_from_gcs(
        conversation_id=conversation_id, file_name="message"
    )
    if conversation_messages == {}:
        # return empty context when first message is sent
        return []
    return conversation_messages


def get_chat_response(context: list, prompt: str, llm_params: dict) -> str:
    """Sends prompt to LLM.
    Args:
        context: List of messages to be sent as context
        prompt: Prompt sent by user
        llm_params: Dictionary of LLM parameters to be passed
    Returns:
        Text extracted from LLM response.
    """
    factory = LLMFactory()
    llm = LLMBase(factory.create_llm(llm_params["model_name"], llm_params["api_key"]))
    response = llm.send_response(prompt)
    return response


def get_context_from_bucket(conversation_id):
    """Gets complete context of a conversation using id from GCS.
    Args:
        id: Conversation Id
    Returns:
        Entire context of conversation as a dictionary.
    """
    context = get_messages_for_conversation(conversation_id)
    return context


def generate_title(user_propmt):
    # By default, gemini will be used to generate the prompt
    llm_model = GeminiLLM()
    admin_prompt = """Generate a conversation title for the given prompt. This prompt is
                    suppose to be the first message sent by a user to a chat bot. 
                    Follow these guidelines,
                    1. Title should be less than 7 words
                    2. Do not use any punctuation marks in the response 
                    3. If the prompt does not have enough context then respond with - Untitled Chat
                    4. Always format your response as follows - Title: <generated title> 
                    where <generated_title> should be your response.
                    """
    non_streaming_response = llm_model.generate_response(
        [], admin_prompt + "\n Prompt: " + user_propmt, {"temp": 0.1, "max_tokens": 15}, False
    )
    for response in non_streaming_response:
        if response["result"] == "success":
            raw_title = response["data"][0]["message"]
            logging.info("-------------RAW TITLE: ", raw_title)
            formatted_title = (
                raw_title.split(": ")[1]
                .replace("\n", "")
                .replace("\r", "")
                .replace("\t", "")
                .strip()
            )
            logging.info(
                "SUCCESS - Title generation.\nConversation Title: ", formatted_title
            )
            return formatted_title
        else:
            logging.error("FAILED - Title generation.")
            return "Untitled Chat"
    
def update_title(conversation_id, conversation_title):
    update_conversation = update_conversation_title(conversation_id, conversation_title)
    logging.info("Updated conversation title in DB - ", update_conversation)
    updated_title = {
        "title": conversation_title 
    }
    _ = update_conversation_settings(conversation_id, updated_title)
    logging.info("Updated conversation title in GCS - ", conversation_id)


def post_message(conversation_id: str, message_request_body: dict, stream=True):
    """Send prompt to LLM and store response.
    Args:
        id: Conversation Id
        message_request_body: Dictionary containing role -> user and message -> prompt
    Returns:
        Dict response received from LLM containing role -> system and message -> response text.
    """
    conversations = list_folders_in_gcs()
    current_conversation = None
    # Check if the conversation id already exists
    for conversation in conversations:
        if conversation_id == conversation:
            existing_conversation = get_conversation(conversation_id)
            if isinstance(existing_conversation, dict) and existing_conversation["title"] == "Untitled Chat":
                conversation_title = generate_title(message_request_body["message"])
                # update title in DB and GCS (llm-settings.json)
                update_title(conversation_id, conversation_title)
            current_conversation = conversation
            break
    if not current_conversation:
        conversation_title = generate_title(message_request_body["message"])
        current_conversation = post_conversation_settings(
            conversation_id, title=conversation_title
        )

    try:
        prompt = message_request_body["message"]
        context = get_context_from_bucket(conversation_id)
        llm_settings = get_conversation_settings(conversation_id)
        llm_name = llm_settings["llm_name"]
        llm_params = llm_settings["llm_params"]

        # Check if the particular llm is active
        if not is_llm_active(llm_name):
            response_data = {
                "role": "system",
                "message": "This LLM has been disabled, please switch to some other LLM.",
            }
            yield (json.dumps(response_data) + "\n").encode("utf-8")

        else:
            if llm_name == "Gemini":
                llm_model = GeminiLLM()
            elif llm_name == "Codestral":
                llm_model = CodestralLLM()
            else:
                # setting default as Gemini
                llm_model = GeminiLLM()

            if stream:
                streaming_response_generator = llm_model.generate_response(
                    context, prompt, llm_params, True
                )
                complete_response = ""
                for streaming_response in streaming_response_generator:
                    streaming_response_data = streaming_response["data"][0]
                    complete_response += streaming_response_data["message"]
                    yield (json.dumps(streaming_response_data) + "\n").encode("utf-8")

                context.append(message_request_body)
                context.append({"role": "system", "message": complete_response})
                write_file_to_gcs(
                    conversation_id=conversation_id, data=context, file_name="message"
                )

            else:
                non_streaming_response = llm_model.generate_response(
                    context, prompt, llm_params, False
                )
                for resp in non_streaming_response:
                    response_data = resp["data"][0]
                    context.append(message_request_body)
                    context.append(response_data)
                    write_file_to_gcs(
                        conversation_id=conversation_id,
                        data=context,
                        file_name="message",
                    )
                    yield (json.dumps(response_data) + "\n").encode("utf-8")

    except Exception as e:
        logging.error(f"Error in post message - {e}")
        response = ApiResponse(
            data={"error": {"type": type(e).__name__, "message": str(e)}},
            message="Database error occurred",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        return response.to_response()
