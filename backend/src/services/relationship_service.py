"""
Patient-Professional Relationship Management Service.
This module handles the business logic for managing relationships between patients and healthcare professionals.
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date
from sqlalchemy import and_, or_
from ..models.database import db, User, PatientProfessionalRelationship, AuditLog
from .audit_service import AuditService


class RelationshipService:
    """Service for managing patient-professional relationships."""

    def __init__(self):
        """Initialize the relationship service."""
        self.audit_service = AuditService()

    def create_relationship(
        self,
        patient_id: int,
        professional_id: int,
        relationship_type: str = 'primary_care',
        relationship_status: str = 'active',
        created_by_id: Optional[int] = None,
        notes: Optional[str] = None,
        permissions: Optional[Dict] = None
    ) -> Tuple[bool, str, Optional[PatientProfessionalRelationship]]:
        """
        Create a new patient-professional relationship.

        Args:
            patient_id: ID of the patient
            professional_id: ID of the healthcare professional
            relationship_type: Type of relationship (primary_care, specialist, etc.)
            relationship_status: Status of relationship (active, pending, etc.)
            created_by_id: ID of user creating the relationship
            notes: Optional notes about the relationship
            permissions: Optional permissions dictionary

        Returns:
            Tuple of (success, message, relationship)
        """
        try:
            # Validate users exist and have correct roles
            patient = User.query.filter_by(id=patient_id, role='patient').first()
            professional = User.query.filter_by(id=professional_id, role='professional').first()

            if not patient:
                return False, "Patient not found", None

            if not professional:
                return False, "Healthcare professional not found", None

            if patient_id == professional_id:
                return False, "Patient and professional cannot be the same person", None

            # Check if relationship already exists
            existing = PatientProfessionalRelationship.query.filter_by(
                patient_id=patient_id,
                professional_id=professional_id
            ).first()

            if existing:
                return False, "Relationship already exists", None

            # Create new relationship
            relationship = PatientProfessionalRelationship(
                patient_id=patient_id,
                professional_id=professional_id,
                relationship_type=relationship_type,
                relationship_status=relationship_status,
                created_by_id=created_by_id
            )

            if notes:
                relationship.notes = notes

            # Set permissions if provided
            if permissions:
                relationship.can_view_documents = permissions.get('can_view_documents', True)
                relationship.can_add_notes = permissions.get('can_add_notes', True)
                relationship.can_request_tests = permissions.get('can_request_tests', False)

            db.session.add(relationship)
            db.session.commit()

            # Log the action
            self.audit_service.log_action(
                action='relationship_created',
                resource_type='relationship',
                resource_id=str(relationship.id),
                user_id=created_by_id,
                details={
                    'patient_id': patient_id,
                    'professional_id': professional_id,
                    'relationship_type': relationship_type,
                    'relationship_status': relationship_status
                }
            )

            return True, "Relationship created successfully", relationship

        except Exception as e:
            db.session.rollback()
            return False, f"Error creating relationship: {str(e)}", None

    def get_patient_professionals(self, patient_id: int, status: Optional[str] = None) -> List[Dict]:
        """
        Get all healthcare professionals for a patient.

        Args:
            patient_id: ID of the patient
            status: Optional status filter

        Returns:
            List of professional relationships
        """
        query = PatientProfessionalRelationship.query.filter_by(patient_id=patient_id)

        if status:
            query = query.filter_by(relationship_status=status)

        relationships = query.all()
        return [rel.to_dict(include_users=True) for rel in relationships]

    def get_professional_patients(self, professional_id: int, status: Optional[str] = None) -> List[Dict]:
        """
        Get all patients for a healthcare professional.

        Args:
            professional_id: ID of the healthcare professional
            status: Optional status filter

        Returns:
            List of patient relationships
        """
        query = PatientProfessionalRelationship.query.filter_by(professional_id=professional_id)

        if status:
            query = query.filter_by(relationship_status=status)

        relationships = query.all()
        return [rel.to_dict(include_users=True) for rel in relationships]

    def update_relationship(
        self,
        relationship_id: int,
        updated_by_id: int,
        **kwargs
    ) -> Tuple[bool, str, Optional[PatientProfessionalRelationship]]:
        """
        Update an existing relationship.

        Args:
            relationship_id: ID of the relationship to update
            updated_by_id: ID of user making the update
            **kwargs: Fields to update

        Returns:
            Tuple of (success, message, relationship)
        """
        try:
            relationship = PatientProfessionalRelationship.query.get(relationship_id)
            if not relationship:
                return False, "Relationship not found", None

            # Store original values for audit
            original_values = relationship.to_dict(include_users=False)

            # Update allowed fields
            allowed_fields = [
                'relationship_status', 'relationship_type', 'notes',
                'can_view_documents', 'can_add_notes', 'can_request_tests',
                'start_date', 'end_date'
            ]

            updated_fields = {}
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(relationship, field):
                    setattr(relationship, field, value)
                    updated_fields[field] = value

            if updated_fields:
                relationship.updated_at = datetime.utcnow()
                db.session.commit()

                # Log the action
                self.audit_service.log_action(
                    action='relationship_updated',
                    resource_type='relationship',
                    resource_id=str(relationship_id),
                    user_id=updated_by_id,
                    details={
                        'updated_fields': updated_fields,
                        'original_values': {k: original_values.get(k) for k in updated_fields.keys()}
                    }
                )

                return True, "Relationship updated successfully", relationship
            else:
                return False, "No valid fields to update", relationship

        except Exception as e:
            db.session.rollback()
            return False, f"Error updating relationship: {str(e)}", None

    def delete_relationship(
        self,
        relationship_id: int,
        deleted_by_id: int,
        reason: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Delete (deactivate) a relationship.

        Args:
            relationship_id: ID of the relationship to delete
            deleted_by_id: ID of user deleting the relationship
            reason: Optional reason for deletion

        Returns:
            Tuple of (success, message)
        """
        try:
            relationship = PatientProfessionalRelationship.query.get(relationship_id)
            if not relationship:
                return False, "Relationship not found"

            # Store relationship data for audit
            relationship_data = relationship.to_dict(include_users=True)

            # Instead of hard delete, mark as terminated
            relationship.relationship_status = 'terminated'
            relationship.end_date = date.today()
            relationship.updated_at = datetime.utcnow()

            if reason:
                relationship.notes = f"{relationship.notes or ''}\n\nTerminated: {reason}".strip()

            db.session.commit()

            # Log the action
            self.audit_service.log_action(
                action='relationship_terminated',
                resource_type='relationship',
                resource_id=str(relationship_id),
                user_id=deleted_by_id,
                details={
                    'relationship_data': relationship_data,
                    'termination_reason': reason
                }
            )

            return True, "Relationship terminated successfully"

        except Exception as e:
            db.session.rollback()
            return False, f"Error terminating relationship: {str(e)}"

    def check_access_permission(
        self,
        patient_id: int,
        professional_id: int,
        permission_type: str = 'can_view_documents'
    ) -> bool:
        """
        Check if a professional has specific permission for a patient.

        Args:
            patient_id: ID of the patient
            professional_id: ID of the professional
            permission_type: Type of permission to check

        Returns:
            True if permission granted, False otherwise
        """
        relationship = PatientProfessionalRelationship.query.filter_by(
            patient_id=patient_id,
            professional_id=professional_id,
            relationship_status='active'
        ).first()

        if not relationship:
            return False

        return getattr(relationship, permission_type, False)

    def get_shared_patients(self, professional_id: int) -> List[int]:
        """
        Get list of patient IDs that a professional has access to.

        Args:
            professional_id: ID of the professional

        Returns:
            List of patient IDs
        """
        relationships = PatientProfessionalRelationship.query.filter_by(
            professional_id=professional_id,
            relationship_status='active',
            can_view_documents=True
        ).all()

        return [rel.patient_id for rel in relationships]

    def get_relationship_by_id(self, relationship_id: int) -> Optional[Dict]:
        """
        Get a relationship by ID.

        Args:
            relationship_id: ID of the relationship

        Returns:
            Relationship dictionary or None
        """
        relationship = PatientProfessionalRelationship.query.get(relationship_id)
        return relationship.to_dict(include_users=True) if relationship else None

    def search_professionals(
        self,
        query: str,
        specialty: Optional[str] = None,
        organization: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for healthcare professionals.

        Args:
            query: Search query (name, username, etc.)
            specialty: Optional specialty filter
            organization: Optional organization filter

        Returns:
            List of matching professionals
        """
        search_query = User.query.filter_by(role='professional', is_active=True)

        if query:
            search_query = search_query.filter(
                or_(
                    User.username.ilike(f'%{query}%'),
                    User.first_name.ilike(f'%{query}%'),
                    User.last_name.ilike(f'%{query}%'),
                    User.email.ilike(f'%{query}%')
                )
            )

        if specialty:
            search_query = search_query.filter(User.specialty.ilike(f'%{specialty}%'))

        if organization:
            search_query = search_query.filter(User.organization.ilike(f'%{organization}%'))

        professionals = search_query.limit(20).all()
        return [prof.to_dict() for prof in professionals]
