import pytest
import uuid
from unittest.mock import MagicMock, create_autospec
from http import HTTPStatus
from app.main.service.conversation_service import (
    create_conversation_id,
    get_user_conversations,
    create_conversation,
    get_conversation,
)
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from app import create_app  # Adjust import according to your app's structure


@pytest.fixture
def app():
    app = create_app()  # Initialize the Flask app
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_session(mocker):
    # Create a mock Session object
    mock_session = create_autospec(Session, instance=True)
    # Configure the mock Session object to behave as a context manager
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = (
        False  # Typically, __exit__ should return False
    )
    # Patch the Session import in your module
    mocker.patch(
        "app.main.service.conversation_service.Session", return_value=mock_session
    )
    return mock_session


def test_create_conversation_id():
    """Test that the create_conversation_id function generates a valid UUID."""
    new_id = create_conversation_id()
    assert isinstance(new_id, str)
    try:
        uuid.UUID(new_id)
    except ValueError:
        pytest.fail("The generated conversation ID is not a valid UUID.")


def test_create_conversation_success(mock_session, mocker):
    """Test successful creation of a conversation object and correct handling of session methods."""
    mock_conversation = MagicMock()
    mock_conversation.to_dict.return_value = {
        "id": "b8e234ee-3849-4d51-b8e8-ea768eee08e3",
        "user_email": "test@example.com",
        "title": "Untitled Chat",
        "llm_name": "Gemini",
        "llm_params": {"temp": 0.1},
    }

    # Patch the ConversationSQL to return a mock conversation object
    mock_conversation_sql = mocker.patch(
        "app.main.service.conversation_service.ConversationSQL",
        return_value=mock_conversation,
    )
    # Patch the engine so that no actual database connection is used
    mocker.patch("app.main.service.conversation_service.engine")

    # Ensure that add, commit, and close do not raise exceptions
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.close.return_value = None

    # Act
    result = create_conversation(
        "b8e234ee-3849-4d51-b8e8-ea768eee08e3",
        "test@example.com",
        "Untitled Chat",
        "Gemini",
        {"temp": 0.1},
    )

    # Assert that the response or create_conversation is as expected
    assert result == {
        "id": "b8e234ee-3849-4d51-b8e8-ea768eee08e3",
        "user_email": "test@example.com",
        "title": "Untitled Chat",
        "llm_name": "Gemini",
        "llm_params": {"temp": 0.1},
    }

    # Verify that the ConversationSQL object was created with the correct parameters
    mock_conversation_sql.assert_called_once_with(
        id="b8e234ee-3849-4d51-b8e8-ea768eee08e3",
        user_email="test@example.com",
        title="Untitled Chat",
        llm_name="Gemini",
        llm_params={"temp": 0.1},
    )

    # Verify that add, commit, and close were called on the session
    mock_session.add.assert_called_once_with(mock_conversation)
    mock_session.commit.assert_called_once()
    mock_session.close.assert_called_once()


def test_create_conversation_failure(client, mock_session, mocker):
    """Test that the create_conversation function handles OperationalError exceptions properly."""
    mock_conversation = MagicMock()
    mock_conversation.to_dict.return_value = {
        "id": "b8e234ee-3849-4d51-b8e8-ea768eee08e3",
        "user_email": "test@example.com",
        "title": "Untitled Chat",
        "llm_name": "Gemini",
        "llm_params": {"temp": 0.1},
    }

    # Patch the ConversationSQL to simulate an OperationalError during initialization
    mocker.patch(
        "app.main.model.conversation.ConversationSQL", return_value=mock_conversation
    )
    mocker.patch("app.main.service.conversation_service.engine")

    # Patch the Session methods to raise OperationalError
    mock_session.add.side_effect = OperationalError("INSERT ...", {}, "database error")
    mock_session.commit.side_effect = OperationalError(
        "INSERT ...", {}, "database error"
    )

    with client.application.app_context():
        response = create_conversation(
            "b8e234ee-3849-4d51-b8e8-ea768eee08e3",
            "test@example.com",
            "Untitled Chat",
            "Gemini",
            {"temp": 0.1},
        )

    assert isinstance(response, tuple)
    response_json, status_code = response

    if hasattr(response_json, "json"):
        response_json = response_json.json
    print(response_json)

    # Assert JSON data
    assert isinstance(response_json, dict)
    assert "message" in response_json
    assert "error" in response_json["data"]
    assert "OperationalError" in response_json["data"]["error"]["type"]

    # Assert status code (optional, depending on what you're testing)
    assert status_code == HTTPStatus.INTERNAL_SERVER_ERROR


def test_get_conversation_success(mock_session, mocker):
    """Test that get_conversation function returns the conversation data matching the input conversation id."""
    expected_conversation = {
        "id": "b8e234ee-3849-4d51-b8e8-ea768eee08e3",
        "user_email": "test@example.com",
        "title": "Untitled Chat",
        "llm_name": "Gemini",
        "llm_params": {"temp": 0.1},
    }

    mock_conversation = MagicMock()
    mock_conversation.to_dict.return_value = expected_conversation

    # Set up the mock to return these mock objects
    mock_session.query.return_value.filter.return_value.first.return_value = (
        mock_conversation
    )
    conversation = get_conversation(
        conversation_id="b8e234ee-3849-4d51-b8e8-ea768eee08e3"
    )

    # Assert that the returned data is as expected
    assert conversation == expected_conversation


def test_get_all_user_conversations(mock_session):
    """Test that get_user_conversations returns the expected user conversation data."""
    # Sample data that you expect to be returned from the database
    expected_conversations = [
        {
            "id": "b8e234ee-3849-4d51-b8e8-ea768eee08e3",
            "user_email": "test@example.com",
            "title": "Untitled Chat",
            "llm_name": "Gemini",
            "llm_params": {"temp": 0.1},
        },
        {
            "id": "a31e8b91-351b-4866-9742-b5d039f0d874",
            "user_email": "test@example.com",
            "title": "Untitled Chat",
            "llm_name": "Codestral",
            "llm_params": {"temp": 0.5},
        },
    ]

    mock_conversations = [
        MagicMock(to_dict=lambda c=conversation: c)
        for conversation in expected_conversations
    ]

    # Set up the mock to return these mock objects
    mock_session.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = (
        mock_conversations
    )
    user_conversations = get_user_conversations(user_email="test@example.com", offset=0, limit=5)

    # Assert that the returned data is as expected
    assert user_conversations == expected_conversations


def test_get_user_conversations_no_conversations(mock_session):
    """Test that get_user_conversations handles the case with no conversations correctly."""
    # Mock an empty query result
    mock_session.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = (
        []
    )
    result = get_user_conversations("test@example.com", offset=0, limit=5)
    # Assert an empty list is returned when no conversations are found
    assert result == []


def test_get_user_conversations_operational_error(client, mock_session):
    """Test handling of OperationalError in get_user_conversations."""
    # Mock an OperationalError
    mock_session.query.return_value.filter.side_effect = OperationalError(
        "SELECT ...", {}, "database error"
    )

    with client.application.app_context():
        response = get_user_conversations("test@example.com", offset=0, limit=5)

    assert isinstance(response, tuple)
    response_json, status_code = response

    if hasattr(response_json, "json"):
        response_json = response_json.json
    # print(response_json)

    # Assert JSON data
    assert isinstance(response_json, dict)
    assert "message" in response_json
    assert "error" in response_json["data"]
    assert "OperationalError" in response_json["data"]["error"]["type"]

    # Assert status code (optional, depending on what you're testing)
    assert status_code == HTTPStatus.INTERNAL_SERVER_ERROR
