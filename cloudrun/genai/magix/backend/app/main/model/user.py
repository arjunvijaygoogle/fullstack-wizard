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

from sqlalchemy import Column, String, Boolean, UUID, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class UserSQL(Base):
    """
    Conversation class

    """

    __tablename__ = "user"
    email = Column(String)
    username = Column(String, unique=True, primary_key=True)
    is_admin = Column(Boolean, default=False)
    tenant_id = Column(UUID)
    created_at = Column(DateTime, default=func.now())

    def __init__(self, email, username, tenant_id):
        self.email = email
        self.username = username
        self.tenant_id = tenant_id

    def to_dict(self) -> dict:
        """Convert to doct

        Keyword arguments:
        Return: return dict of conversation object
        """

        return {
            "email": self.email,
            "username": self.username,
            "is_admin": self.is_admin,
            "tenant_id": self.tenant_id,
        }
