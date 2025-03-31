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

from flask import request
from app.main import bp
from http import HTTPStatus
from app.main.model.apiresponse import ApiResponse
from app.main.service.llm_service import (
    get_llms,
    create_llm,
    update_llm,
    delete_llm,
)


@bp.route("/llms", methods=["GET", "PATCH", "POST", "DELETE"])
def llms_route():
    if request.method == "GET":
        llms = get_llms()
        return llms
    elif request.method == "PATCH":
        data = request.get_json()
        if data and "name" in data and "is_active" in data:
            name = data["name"]
            is_active = data["is_active"]
            return update_llm(name, is_active)
        else:
            response = ApiResponse(HTTPStatus.BAD_REQUEST, message="Missing argument")
            return response.to_response()

    elif request.method == "DELETE":
        data = request.get_json()
        if data and "name" in data:
            return delete_llm(data["name"])
        else:
            response = ApiResponse(HTTPStatus.BAD_REQUEST, message="Missing argument")
            return response.to_response()
    else:
        data = request.get_json()
        if (
            data
            and "name" in data
            and "display_name" in data
            and "provider" in data
            and "model_name" in data
            and "version" in data
            and "params" in data
        ):
            name = data["name"]
            display_name = data["display_name"]
            provider = data["provider"]
            model_name = data["model_name"]
            version = data["version"]
            params = data["params"]
            return create_llm(name, display_name, provider, model_name, version, params)
        else:
            response = ApiResponse(HTTPStatus.BAD_REQUEST, message="Missing argument")
            return response.to_response()
