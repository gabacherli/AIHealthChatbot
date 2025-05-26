"""
Audit Service for HIPAA compliance and security tracking.
This module handles audit logging for all sensitive operations in the system.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import request
from ..models.database import db, AuditLog, User


class AuditService:
    """Service for managing audit logs and compliance tracking."""

    def log_action(
        self,
        action: str,
        resource_type: str,
        user_id: Optional[int] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
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
            The created audit log entry
        """
        try:
            # Get request context if available
            if not ip_address and request:
                ip_address = request.remote_addr

            if not user_agent and request:
                user_agent = request.headers.get('User-Agent', '')[:500]  # Limit length

            # Create audit log entry
            audit_log = AuditLog(
                action=action,
                resource_type=resource_type,
                user_id=user_id,
                resource_id=resource_id,
                details=details,
                ip_address=ip_address,
                user_agent=user_agent
            )

            db.session.add(audit_log)
            db.session.commit()

            return audit_log

        except Exception as e:
            # Don't let audit logging failures break the main operation
            db.session.rollback()
            return None

    def log_document_access(
        self,
        user_id: int,
        document_id: str,
        document_name: str,
        access_type: str = 'view',
        patient_id: Optional[int] = None
    ) -> AuditLog:
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
    ) -> AuditLog:
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
    ) -> AuditLog:
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

    def get_user_audit_logs(
        self,
        user_id: int,
        days: int = 30,
        action_filter: Optional[str] = None,
        resource_type_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Get audit logs for a specific user.

        Args:
            user_id: ID of the user
            days: Number of days to look back
            action_filter: Optional action filter
            resource_type_filter: Optional resource type filter

        Returns:
            List of audit log dictionaries
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        query = AuditLog.query.filter(
            AuditLog.user_id == user_id,
            AuditLog.timestamp >= start_date
        )

        if action_filter:
            query = query.filter(AuditLog.action.ilike(f'%{action_filter}%'))

        if resource_type_filter:
            query = query.filter(AuditLog.resource_type == resource_type_filter)

        logs = query.order_by(AuditLog.timestamp.desc()).limit(1000).all()
        return [log.to_dict() for log in logs]

    def get_document_audit_logs(
        self,
        document_id: str,
        days: int = 30
    ) -> List[Dict]:
        """
        Get audit logs for a specific document.

        Args:
            document_id: ID of the document
            days: Number of days to look back

        Returns:
            List of audit log dictionaries
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        logs = AuditLog.query.filter(
            AuditLog.resource_type == 'document',
            AuditLog.resource_id == document_id,
            AuditLog.timestamp >= start_date
        ).order_by(AuditLog.timestamp.desc()).all()

        return [log.to_dict() for log in logs]

    def get_patient_access_logs(
        self,
        patient_id: int,
        days: int = 30
    ) -> List[Dict]:
        """
        Get all access logs for a patient's data.

        Args:
            patient_id: ID of the patient
            days: Number of days to look back

        Returns:
            List of audit log dictionaries
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        # Get logs where patient_id is in details or user_id is the patient
        logs = AuditLog.query.filter(
            AuditLog.timestamp >= start_date
        ).filter(
            db.or_(
                AuditLog.user_id == patient_id,
                AuditLog.details.contains(f'"patient_id": {patient_id}')
            )
        ).order_by(AuditLog.timestamp.desc()).limit(1000).all()

        return [log.to_dict() for log in logs]

    def get_professional_access_logs(
        self,
        professional_id: int,
        days: int = 30
    ) -> List[Dict]:
        """
        Get all access logs for a professional's actions.

        Args:
            professional_id: ID of the professional
            days: Number of days to look back

        Returns:
            List of audit log dictionaries
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        logs = AuditLog.query.filter(
            AuditLog.user_id == professional_id,
            AuditLog.timestamp >= start_date
        ).order_by(AuditLog.timestamp.desc()).limit(1000).all()

        return [log.to_dict() for log in logs]

    def get_system_audit_summary(self, days: int = 7) -> Dict:
        """
        Get a summary of system audit activity.

        Args:
            days: Number of days to look back

        Returns:
            Dictionary with audit summary statistics
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        # Get total counts by action type
        action_counts = db.session.query(
            AuditLog.action,
            db.func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= start_date
        ).group_by(AuditLog.action).all()

        # Get total counts by resource type
        resource_counts = db.session.query(
            AuditLog.resource_type,
            db.func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= start_date
        ).group_by(AuditLog.resource_type).all()

        # Get unique users
        unique_users = db.session.query(
            db.func.count(db.distinct(AuditLog.user_id))
        ).filter(
            AuditLog.timestamp >= start_date
        ).scalar()

        # Get total log count
        total_logs = AuditLog.query.filter(
            AuditLog.timestamp >= start_date
        ).count()

        return {
            'period_days': days,
            'start_date': start_date.isoformat(),
            'total_logs': total_logs,
            'unique_users': unique_users,
            'action_counts': {action: count for action, count in action_counts},
            'resource_counts': {resource: count for resource, count in resource_counts}
        }

    def cleanup_old_logs(self, days_to_keep: int = 365) -> int:
        """
        Clean up old audit logs (for storage management).

        Args:
            days_to_keep: Number of days of logs to keep

        Returns:
            Number of logs deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        deleted_count = AuditLog.query.filter(
            AuditLog.timestamp < cutoff_date
        ).delete()

        db.session.commit()
        return deleted_count


# Create a singleton instance for easy import
audit_service = AuditService()
