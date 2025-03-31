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
import os
import logging
import sqlalchemy
import random
import string
from sqlalchemy.orm import Session
from app.main.model.user import UserSQL
from db.config import connect_with_connector
from app.main.model.apiresponse import ApiResponse
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests


engine = connect_with_connector()


def generate_random_username_suffix(length=4):
    """Generate a random string of fixed length.
    Args:
        length: length of the output random string

    Returns:
        Random string

    """

    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))


def get_users():
    """Returns all users.
    Returns:
      A list of user objects.
    """
    try:
        session = Session(engine)
        users = session.query(UserSQL).all()
        users_list = [user.to_dict() for user in users]
        session.close()
        return users_list

    except Exception as e:
        logging.error(f"Error getting users: {e}")
        response = ApiResponse(
            data={"error": {"type": type(e).__name__, "message": str(e)}},
            message="Error fetching users.",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        return response.to_response()


def create_user(user_email):
    """Create new user.
    Returns:
      User info
    """
    try:
        
        base_username = user_email.split("@")[0]
        username = base_username

        session = Session(engine, expire_on_commit=False)
        while session.query(UserSQL).filter_by(username=username).first() is not None:
            random_suffix = generate_random_username_suffix()
            username = f"{base_username}_{random_suffix}"

        user = UserSQL(
            email=user_email,
            tenant_id=os.environ.get("TENANT_ID"),
            username=username
        )

        session.add(user)
        session.commit()
        session.close()

        logging.info(f"User added: {user_email}")
        return user.to_dict()

    except Exception as e:
        logging.error(f"Error adding user: {e}")
        response = ApiResponse(
            data={"error": {"type": type(e).__name__, "message": str(e)}},
            message="Database error occurred. User could not be registered",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        return response.to_response()


def get_user_data(username):
    """Get details of 1 user.
    Args:
        username: username
    Returns:
        boolean, if the user is admin or not
    """
    try:
        session = Session(engine)
        user = session.query(UserSQL).filter_by(username=username).first()
        session.close()
        if user:
            return user.to_dict()

        response = ApiResponse(
            data={"error": {"message": "User Not Found."}},
            message="User Not Found.",
            status_code=HTTPStatus.NOT_FOUND,
        )
        return response.to_response()

    except Exception as e:
        logging.error(f"Error fetching details of user: {e}")
        response = ApiResponse(
            data={"error": {"type": type(e).__name__, "message": str(e)}},
            message="Error fetching details of user",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        return response.to_response()


def get_user_data_email(user_email):
    """Get details of user using the email.
    Args:
        user_email: email id of user
    Returns:
        user info, if user is found, otherwise error
    """
    try:
        session = Session(engine)
        user = session.query(UserSQL).filter_by(email=user_email).first()
        session.close()
        if user:
            return user.to_dict()
        return create_user(user_email)


    except Exception as e:
        logging.error(f"Error fetching details of user: {e}")
        response = ApiResponse(
            data={"error": {"type": type(e).__name__, "message": str(e)}},
            message="Error fetching details of user",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        return response.to_response()


def validate_user_token(token):
    """ validate user token.
    Args:
        token: user token
    Returns:
        user info corresponding to the token, if user is found, otherwise error
    """
    try:
        CLIENT_ID = os.environ.get("CLIENT_ID")
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), CLIENT_ID)

        user_email = idinfo['email']
        user_id = idinfo['sub']

        logging.info(f"Email extracted from token - {user_email}")
        user_info = get_user_data_email(user_email)

        return user_info

    except Exception as e:
        logging.error(f"Token validation error: {e}")

        response = ApiResponse(
            data={"error": {"type": type(e).__name__, "message": str(e)}},
            message="Token validation error",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        return response.to_response()