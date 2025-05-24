"""
Document routes.
This module contains the routes for document management.
"""
import os
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt
from werkzeug.utils import secure_filename
from ...services.document_service import DocumentService
from ...config import get_config

from . import documents_bp

config = get_config()
document_service = DocumentService()

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

@documents_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_document():
    """
    Upload a document.

    Returns:
        A JSON response with the upload status.
    """
    # Debug logging
    print(f"Content-Type: {request.content_type}")
    print(f"Request files: {request.files}")
    print(f"Request form: {request.form}")
    print(f"Request data: {request.data}")
    print(f"Request json: {request.get_json(silent=True)}")

    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        # Get user info for metadata
        claims = get_jwt()
        user_id = claims.get("sub", "anonymous")
        user_role = claims.get("role", "patient")

        # Process the file
        try:
            # Create user-specific upload directory if it doesn't exist
            upload_dir = os.path.join(config.UPLOAD_FOLDER, user_id)
            os.makedirs(upload_dir, exist_ok=True)

            # Save the file
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)

            # Process and store the document
            document_id = document_service.process_and_store_document(
                file_path,
                filename,
                user_role=user_role,
                user_id=user_id
            )

            return jsonify({
                "message": "Document uploaded and processed successfully",
                "document_id": document_id,
                "filename": filename
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "File type not allowed"}), 400

@documents_bp.route("/list", methods=["GET"])
@jwt_required()
def list_documents():
    """
    List all documents for the current user.

    Returns:
        A JSON response with the list of documents.
    """
    try:
        # Get user ID
        claims = get_jwt()
        user_id = claims.get("sub", "anonymous")

        # Get documents for the user
        documents = document_service.get_documents_by_user(user_id)
        return jsonify({"documents": documents})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@documents_bp.route("/download/<filename>", methods=["GET"])
@jwt_required()
def download_document(filename):
    """
    Download a document.

    Args:
        filename: The name of the file to download.

    Returns:
        The file for download.
    """
    try:
        # Get user ID
        claims = get_jwt()
        user_id = claims.get("sub", "anonymous")

        # Secure the filename
        secure_name = secure_filename(filename)

        # User-specific upload directory (use absolute path)
        upload_dir = os.path.abspath(os.path.join(config.UPLOAD_FOLDER, user_id))
        file_path = os.path.join(upload_dir, secure_name)

        # Check if file exists before sending
        if not os.path.exists(file_path):
            return jsonify({"error": f"File not found: {file_path}"}), 404

        return send_from_directory(
            upload_dir,
            secure_name,
            as_attachment=True
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@documents_bp.route("/delete/<filename>", methods=["DELETE"])
@jwt_required()
def delete_document(filename):
    """
    Delete a document.

    Args:
        filename: The name of the file to delete.

    Returns:
        A JSON response with the deletion status.
    """
    try:
        # Get user ID for authorization
        claims = get_jwt()
        user_id = claims.get("sub", "anonymous")

        # Secure the filename
        secure_name = secure_filename(filename)

        # Delete the document
        num_deleted = document_service.delete_document(secure_name, user_id)

        if num_deleted > 0:
            return jsonify({
                "message": "Document deleted successfully",
                "chunks_deleted": num_deleted
            })
        else:
            return jsonify({
                "error": "Document not found or you do not have permission to delete it"
            }), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@documents_bp.route("/search", methods=["POST"])
@jwt_required()
def search_documents():
    """
    Search for documents.

    Returns:
        A JSON response with the search results.
    """
    data = request.get_json()
    query = data.get("query", "")

    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # Get user info for filtering
        claims = get_jwt()
        user_id = claims.get("sub", "anonymous")
        user_role = claims.get("role", "patient")

        # Get optional filters
        filters = data.get("filters", {})

        # Add user ID and role to filters if not explicitly provided
        if "user_id" not in filters:
            filters["user_id"] = user_id

        if "user_role" not in filters:
            filters["user_role"] = user_role

        # Search for documents
        results = document_service.search_documents(query, filters)

        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
