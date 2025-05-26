"""
Audit Service for HIPAA compliance and security tracking.
This module handles audit logging for all sensitive operations in the system.
"""
from typing import Dict, Optional, Any
from datetime import datetime
from flask import request
import json
from ..database.repositories.audit_repository import AuditRepository


class AuditService:
    """Service for managing audit logs and compliance tracking."""

    def __init__(self):
        """Initialize the audit service."""
        self.audit_repo = AuditRepository()

    def log_action(
        self,
        action: str,
        resource_type: str,
        user_id: Optional[int] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[int]:
        """
        Log an action for audit purposes.

        Args:
            action: The action performed (e.g., 'document_accessed', 'relationship_created')
            resource_type: Type of resource (e.g., 'document', 'relationship', 'user')
            user_id: ID of the user performing the action
            resource_id: ID of the resource being acted upon
            details: Additional details about the action
            ip_address: IP address of the request
            user_agent: User agent string

        Returns:
            The created audit log ID if successful, None otherwise
        """
        try:
            # Get request context if available
            if not ip_address and request:
                ip_address = request.remote_addr

            if not user_agent and request:
                user_agent = request.headers.get('User-Agent', '')[:500]  # Limit length

            # Prepare audit log data
            audit_data = {
                'action': action,
                'resource_type': resource_type,
                'user_id': user_id,
                'resource_id': resource_id,
                'details': json.dumps(details) if details else None,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'timestamp': datetime.now()
            }

            return self.audit_repo.create(audit_data)

        except Exception as e:
            # Don't let audit logging failures break the main operation
            return None

    def log_document_access(
        self,
        user_id: int,
        document_id: str,
        document_name: str,
        access_type: str = 'view',
        patient_id: Optional[int] = None
    ) -> Optional[int]:
        """
        Log document access for HIPAA compliance.

        Args:
            user_id: ID of the user accessing the document
            document_id: ID of the document
            document_name: Name of the document
            access_type: Type of access (view, download, upload, delete)
            patient_id: ID of the patient who owns the document

        Returns:
            The created audit log entry
        """
        return self.log_action(
            action=f'document_{access_type}',
            resource_type='document',
            user_id=user_id,
            resource_id=document_id,
            details={
                'document_name': document_name,
                'access_type': access_type,
                'patient_id': patient_id
            }
        )

    def log_relationship_access(
        self,
        user_id: int,
        relationship_id: int,
        action: str,
        patient_id: Optional[int] = None,
        professional_id: Optional[int] = None
    ) -> Optional[int]:
        """
        Log relationship-related actions.

        Args:
            user_id: ID of the user performing the action
            relationship_id: ID of the relationship
            action: Action performed (created, updated, terminated, accessed)
            patient_id: ID of the patient in the relationship
            professional_id: ID of the professional in the relationship

        Returns:
            The created audit log entry
        """
        return self.log_action(
            action=f'relationship_{action}',
            resource_type='relationship',
            user_id=user_id,
            resource_id=str(relationship_id),
            details={
                'patient_id': patient_id,
                'professional_id': professional_id,
                'action': action
            }
        )

    def log_user_action(
        self,
        user_id: int,
        action: str,
        target_user_id: Optional[int] = None,
        details: Optional[Dict] = None
    ) -> Optional[int]:
        """
        Log user-related actions.

        Args:
            user_id: ID of the user performing the action
            action: Action performed (login, logout, profile_update, etc.)
            target_user_id: ID of the target user (if different from user_id)
            details: Additional details

        Returns:
            The created audit log entry
        """
        return self.log_action(
            action=f'user_{action}',
            resource_type='user',
            user_id=user_id,
            resource_id=str(target_user_id) if target_user_id else str(user_id),
            details=details
        )


# Create a singleton instance for easy import
audit_service = AuditService()
