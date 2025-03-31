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

from sqlalchemy import Column, String, JSON, UUID, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ConversationSQL(Base):
    """
    Conversation class

    """

    __tablename__ = "conversation"
    id = Column(UUID, unique=True, primary_key=True)
    user_email = Column(String)
    title = Column(String)
    llm_name = Column(String)
    llm_params = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now())

    def __init__(self, id, user_email, title, llm_name, llm_params):
        self.id = id
        self.user_email = user_email
        self.title = title
        self.llm_name = llm_name
        self.llm_params = llm_params

    def to_dict(self) -> dict:
        """Convert to doct

        Keyword arguments:
        Return: return dict of conversation object
        """

        return {
            "id": self.id,
            "user_email": self.user_email,
            "title": self.title,
            "llm_name": self.llm_name,
            "llm_params": self.llm_params,
        }
