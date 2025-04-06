from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt
from src.services.auth_service import USERS
from src.services.chat_service import get_answer_with_context

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = USERS.get(username)
    if not user or user["password"] != password:
        return jsonify({"msg": "Invalid credentials"}), 401

    access_token = create_access_token(identity=username, additional_claims={"role": user["role"]})
    return jsonify({"token": access_token, "role": user["role"]})

@chat_bp.route("/chat", methods=["POST"])
@jwt_required()
def chat():
    claims = get_jwt()
    role = claims.get("role", "patient")
    data = request.get_json()
    question = data.get("question", "")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        answer = get_answer_with_context(question, role)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
