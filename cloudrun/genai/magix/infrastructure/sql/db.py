import os
from typing import List
from dotenv import load_dotenv
from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy
import sys
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, JSON, UUID, DateTime, Boolean, func


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

def connect():
    # initialize Connector object
    connector = Connector()

    return connector

def run_ddl_script(connector: Connector):

    # initialize SQLAlchemy connection pool with Connector
    engine = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=lambda: connector.connect(
            os.getenv("instance_connection_name"),
            "pg8000",
            user=os.getenv("db_user"),
            password=os.getenv("db_password"),
            db=os.getenv("db_name")
        ),
    )

    Base.metadata.create_all(bind=engine)



if __name__ == "__main__":
    load_dotenv()
    connector = connect()
    run_ddl_script(connector)