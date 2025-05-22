"""
Chat routes.
This module contains the routes for chat functionality.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from ...services.chat_service import get_answer_with_context

chat_bp = Blueprint("chat", __name__, url_prefix="/chat")

@chat_bp.route("", methods=["POST"])
@jwt_required()
def chat():
    """
    Chat route.

    Returns:
        A JSON response with the answer to the question.
    """
    claims = get_jwt()
    role = claims.get("role", "patient")
    data = request.get_json()
    question = data.get("question", "")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        # Get user ID from JWT claims
        user_id = claims.get("sub", "anonymous")

        # Get answer with context and sources
        result = get_answer_with_context(question, role, user_id)

        # Check if result is a tuple (answer, sources)
        if isinstance(result, tuple) and len(result) == 2:
            answer, sources = result
            return jsonify({
                "answer": answer,
                "sources": sources
            })
        else:
            # Backward compatibility
            return jsonify({
                "answer": result,
                "sources": []
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
