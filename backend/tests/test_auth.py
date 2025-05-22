"""
Authentication tests.
This module contains tests for authentication.
"""
import json

def test_login_success(client):
    """
    Test successful login.
    
    Args:
        client: The test client.
    """
    response = client.post(
        "/api/auth/login",
        data=json.dumps({
            "username": "gabriel",
            "password": "gabriel123"
        }),
        content_type="application/json"
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "token" in data
    assert data["role"] == "patient"

def test_login_failure(client):
    """
    Test failed login.
    
    Args:
        client: The test client.
    """
    response = client.post(
        "/api/auth/login",
        data=json.dumps({
            "username": "invalid",
            "password": "invalid"
        }),
        content_type="application/json"
    )
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "msg" in data
