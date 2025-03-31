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
from app.main.service.user_service import (
    get_users,
    get_user_data,
    validate_user_token,
)


@bp.route("/users", methods=["GET"])
def all_users():
    username = request.args.get("username")
    if username:
        return get_user_data(username)
    return get_users()


@bp.route("/verify/token", methods=["GET"])
def validate_token():
    id_token = request.args.get("token")
    return validate_user_token(id_token)
