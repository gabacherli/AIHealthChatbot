"""
Chat tests.
This module contains tests for chat functionality.
"""
import json
import pytest
from unittest.mock import patch

@pytest.fixture
def auth_headers():
    """
    Create authentication headers for testing.
    
    Returns:
        Authentication headers.
    """
    return {
        "Authorization": "Bearer test-token"
    }

@patch("src.services.chat_service.get_answer_with_context")
def test_chat_success(mock_get_answer, client, auth_headers):
    """
    Test successful chat.
    
    Args:
        mock_get_answer: Mock for get_answer_with_context.
        client: The test client.
        auth_headers: Authentication headers.
    """
    mock_get_answer.return_value = "Test answer"
    
    response = client.post(
        "/api/chat/chat",
        data=json.dumps({
            "question": "Test question"
        }),
        content_type="application/json",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["answer"] == "Test answer"
    
    mock_get_answer.assert_called_once_with("Test question", "patient")

def test_chat_no_question(client, auth_headers):
    """
    Test chat with no question.
    
    Args:
        client: The test client.
        auth_headers: Authentication headers.
    """
    response = client.post(
        "/api/chat/chat",
        data=json.dumps({}),
        content_type="application/json",
        headers=auth_headers
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
