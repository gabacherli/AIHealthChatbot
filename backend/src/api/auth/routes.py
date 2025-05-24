"""
Authentication routes.
This module contains the routes for authentication.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from ...services.auth_service import get_user_by_credentials

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login route.

    Returns:
        A JSON response with the access token and user role.
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = get_user_by_credentials(username, password)
    if not user:
        return jsonify({"msg": "Invalid credentials"}), 401

    access_token = create_access_token(
        identity=username,
        additional_claims={"role": user["role"], "user_id": user["id"]}
    )

    return jsonify({
        "token": access_token,
        "role": user["role"],
        "user_id": user["id"],
        "username": user["username"],
        "full_name": user.get("full_name", user["username"])
    })
