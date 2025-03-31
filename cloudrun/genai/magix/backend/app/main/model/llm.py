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

import os
import json
import time
import logging
import google.generativeai as genai
import openai
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Content, Part, GenerationConfig
import httpx
import google.auth
from google.auth.transport.requests import Request
import os
from mistralai import Mistral, UserMessage
from sqlalchemy import create_engine, Column, String, Boolean, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class LLMTableSQL(Base):
    """
    LLM sql table
    """

    __tablename__ = "llm"

    name = Column(String, unique=True, nullable=False, primary_key=True)
    display_name = Column(String)
    provider = Column(String)
    model_name = Column(String)
    version = Column(String)
    params = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)

    def __init__(
        self, name, display_name, provider, model_name, version, params, is_active=True
    ):
        self.name = name
        self.display_name = display_name
        self.provider = provider
        self.model_name = model_name
        self.version = version
        self.params = params
        self.is_active = is_active

    def to_dict(self):
        return {
            "name": self.name,
            "display_name": self.display_name,
            "provider": self.provider,
            "model_name": self.model_name,
            "version": self.version,
            "params": self.params,
            "is_active": self.is_active,
        }


class LLMBase:
    def __init__(self, llm):
        self.llm = llm

    def send_response(self, prompt):
        logging.info("Generating response...")
        response = self.llm.generate_response(prompt)
        return response

    def get_model_name(self):
        return self.llm.get_model_name()


class OpenAILLM:
    def __init__(self, model_name="gpt-3.5-turbo", api_key=None):
        self.model_name = model_name
        self.api_key = api_key
        openai.api_key = api_key

    def generate_response(self, prompt):
        response = openai.ChatCompletion.create(
            model=self.model_name, messages=[{"role": "user", "content": prompt}]
        )
        return {
            "result": "success",
            "data": [
                {"role": "system", "message": response.choices[0].message.content}
            ],
        }

    def get_model_name(self):
        return self.model_name


class GeminiLLM:
    def __init__(self, model_name="gemini-1.5-pro", api_key=None):
        self.model_name = model_name
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.project_id = os.environ.get("GOOGLE_PROJECT_ID")
        self.region = os.environ.get("GOOGLE_REGION")

    def generate_response(self, context, prompt, params, stream=True):
        # genai.configure(api_key=self.api_key)
        vertexai.init(project=self.project_id, location=self.region)
        model = GenerativeModel(self.model_name)
        chat = model.start_chat(history=self.transform_context_structure(context))
        config = GenerationConfig(
            temperature=params.get("temp", 0.1),
            max_output_tokens=params.get("max_tokens", 1000)
        )
        if stream:
            genai_response = chat.send_message(prompt, stream=True, generation_config=config)
            for chunk in genai_response:
                yield {
                    "result": "success",
                    "data": [{"role": "system", "message": chunk.text}],
                }
        else:
            non_streaming_genai_response = chat.send_message(prompt, generation_config=config)
            non_streaming_response = {
                "result": "success",
                "data": [
                    {"role": "system", "message": non_streaming_genai_response.text}
                ],
            }
            yield non_streaming_response

    def get_model_name(self):
        return self.model_name

    def transform_context_structure(self, context):
        tranformed_context = []
        for con in context:
            if con["role"] == "user":
                t_c = Content(role="user", parts=[Part.from_text(con["message"])])
            else:
                t_c = Content(role="model", parts=[Part.from_text(con["message"])])
            tranformed_context.append(t_c)
        return tranformed_context

    def transform_message_structure(self, messages):
        tranformed_messages = []
        for message in messages:
            t_m = {"role": message["role"], "parts": message["message"]}
            tranformed_messages.append(t_m)

        return {"contents": tranformed_messages}


class CodestralLLM:
    def __init__(self, model_name="codestral-latest", api_key=None, stream=False):
        self.model_name = model_name
        self.api_key = api_key
        self.stream = stream

    def get_credentials(self):
        credentials, project_id = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        credentials.refresh(Request())
        return credentials.token

    def build_endpoint_url(
        self,
        region: str,
        project_id: str,
        model_name: str,
        model_version: str,
        streaming: bool = False,
    ):
        base_url = f"https://{region}-aiplatform.googleapis.com/v1/"
        project_fragment = f"projects/{project_id}"
        location_fragment = f"locations/{region}"
        specifier = "streamRawPredict" if streaming else "rawPredict"
        model_fragment = f"publishers/mistralai/models/{model_name}@{model_version}"
        url = f"{base_url}{'/'.join([project_fragment, location_fragment, model_fragment])}:{specifier}"
        return url

    def extract_streamed_content(self, chunk):
        if chunk.strip() == "data: [DONE]":
            return
        try:
            # Parse the JSON chunk
            data = json.loads(chunk[5:])  # Remove the "data: " prefix
            # Extract the 'content' value
            content = data["choices"][0]["delta"]["content"]
            if content != None:
                return content

        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in chunk: {chunk}")
            return None  # Or handle the error as needed

        except KeyError:
            print(f"Error: 'content' key not found in chunk: {chunk}")
            return None  # Or handle the error as needed

    def extract_non_streamed_content(self, chunk):
        try:
            # Parse the JSON chunk
            data = json.loads(chunk)  # Remove the "data: " prefix
            # Extract the 'content' value
            content = data["choices"][0]["message"]["content"]
            if content != None:
                return content

        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in chunk: {chunk}")
            return None  # Or handle the error as needed

        except KeyError:
            print(f"Error: 'content' key not found in chunk: {chunk}")
            return None  # Or handle the error as needed

    def generate_response(self, context, prompt, params, stream=True):
        try:
            project_id = os.environ.get("GOOGLE_PROJECT_ID")
            region = os.environ.get("GOOGLE_REGION")

            # Retrieve Google Cloud credentials.
            access_token = self.get_credentials()

            model = "codestral"
            model_version = "2405"

            # Build URL
            url = self.build_endpoint_url(
                project_id=project_id,
                region=region,
                model_name=model,
                model_version=model_version,
                streaming=stream,
            )

            # Define query headers
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            }

            context = self.transform_context_structure(context=context, prompt=prompt)

            # Define POST payload
            data = {
                "model": model, 
                "messages": context, 
                "stream": stream, 
                "temperature": params.get("temp", 0.1),
                "max_tokens": params.get("max_tokens", 1000)
                }
            # Make the call with streaming
            with httpx.Client() as client:
                with client.stream(
                    "POST", url, json=data, headers=headers, timeout=None
                ) as resp:
                    for chunk in resp.iter_lines():
                        if chunk and stream == True:
                            # print(chunk, end='\n', flush=True)
                            content = self.extract_streamed_content(chunk=chunk)
                            if content is not None:
                                yield {
                                    "result": "success",
                                    "data": [
                                        {
                                            "role": "assistant",
                                            "message": content,
                                        }
                                    ],
                                }
                        if chunk and stream == False:
                            # print(chunk, end='\n', flush=True)
                            content = self.extract_non_streamed_content(chunk=chunk)
                            if content is not None:
                                non_streaming_response = {
                                    "result": "success",
                                    "data": [
                                        {
                                            "role": "assistant",
                                            "message": content,
                                        }
                                    ],
                                }
                                yield non_streaming_response
        except Exception as e:
            logging.error(f"error in generate response - {e}")

    def transform_context_structure(self, context, prompt):
        tranformed_context = []
        for con in context:
            if con["role"] == "user":
                t_c = {"role": con["role"], "content": con["message"]}
            else:
                t_c = {"role": "system", "content": con["message"]}
            tranformed_context.append(t_c)
        tranformed_context.append({"role": "user", "content": prompt})
        return tranformed_context

    def get_model_name(self):
        return self.model_name


class LLMFactory:
    @staticmethod
    def create_llm(model_name, api_key):
        if "openai" in model_name.lower():
            return OpenAILLM(model_name, api_key)
        elif "gemini" in model_name.lower():
            return GeminiLLM(model_name, api_key)
        else:
            raise ValueError(f"Unsupported model name: {model_name}")
