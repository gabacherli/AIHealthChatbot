"""
Patient-Professional Relationship Management Service.
This module handles the business logic for managing relationships between patients and healthcare professionals.
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date
from ..database.repositories.user_repository import UserRepository
from ..database.repositories.relationship_repository import RelationshipRepository
from .audit_service import AuditService


class RelationshipService:
    """Service for managing patient-professional relationships."""

    def __init__(self):
        """Initialize the relationship service."""
        self.audit_service = AuditService()
        self.user_repo = UserRepository()
        self.relationship_repo = RelationshipRepository()

    def create_relationship(
        self,
        patient_id: int,
        professional_id: int,
        relationship_type: str = 'primary_care',
        relationship_status: str = 'active',
        created_by_id: Optional[int] = None,
        notes: Optional[str] = None,
        permissions: Optional[Dict] = None
    ) -> Tuple[bool, str, Optional[Dict]]:
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
            patient = self.user_repo.get_by_id(patient_id)
            professional = self.user_repo.get_by_id(professional_id)

            if not patient or patient.get('role') != 'patient':
                return False, "Patient not found", None

            if not professional or professional.get('role') != 'professional':
                return False, "Healthcare professional not found", None

            if patient_id == professional_id:
                return False, "Patient and professional cannot be the same person", None

            # Create new relationship using repository
            relationship_id = self.relationship_repo.create_relationship(
                patient_id=patient_id,
                professional_id=professional_id,
                relationship_type=relationship_type,
                status=relationship_status,
                created_by_id=created_by_id,
                notes=notes,
                permissions=permissions
            )

            if not relationship_id:
                return False, "Failed to create relationship", None

            # Get the created relationship
            relationship = self.relationship_repo.get_by_id(relationship_id)

            # Log the action
            self.audit_service.log_action(
                action='relationship_created',
                resource_type='relationship',
                resource_id=str(relationship_id),
                user_id=created_by_id,
                details={
                    'patient_id': patient_id,
                    'professional_id': professional_id,
                    'relationship_type': relationship_type,
                    'relationship_status': relationship_status
                }
            )

            return True, "Relationship created successfully", relationship

        except ValueError as e:
            return False, str(e), None
        except Exception as e:
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
        return self.relationship_repo.get_patient_relationships(patient_id, status)

    def get_professional_patients(self, professional_id: int, status: Optional[str] = None) -> List[Dict]:
        """
        Get all patients for a healthcare professional.

        Args:
            professional_id: ID of the healthcare professional
            status: Optional status filter

        Returns:
            List of patient relationships
        """
        return self.relationship_repo.get_professional_relationships(professional_id, status)

    def update_relationship(
        self,
        relationship_id: int,
        updated_by_id: int,
        **kwargs
    ) -> Tuple[bool, str, Optional[Dict]]:
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
            relationship = self.relationship_repo.get_by_id(relationship_id)
            if not relationship:
                return False, "Relationship not found", None

            # Store original values for audit
            original_values = relationship.copy()

            # Update allowed fields
            allowed_fields = [
                'status', 'relationship_type', 'notes',
                'can_view_documents', 'can_add_notes', 'can_request_tests',
                'start_date', 'end_date'
            ]

            updated_fields = {}
            for field, value in kwargs.items():
                if field in allowed_fields:
                    updated_fields[field] = value

            if updated_fields:
                # Add updated timestamp
                updated_fields['updated_at'] = datetime.now()

                success = self.relationship_repo.update_by_id(relationship_id, updated_fields)

                if success:
                    # Get updated relationship
                    updated_relationship = self.relationship_repo.get_by_id(relationship_id)

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

                    return True, "Relationship updated successfully", updated_relationship
                else:
                    return False, "Failed to update relationship", None
            else:
                return False, "No valid fields to update", relationship

        except Exception as e:
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
            relationship = self.relationship_repo.get_by_id(relationship_id)
            if not relationship:
                return False, "Relationship not found"

            # Store relationship data for audit
            relationship_data = relationship.copy()

            # Instead of hard delete, mark as terminated
            update_data = {
                'status': 'terminated',
                'end_date': date.today(),
                'updated_at': datetime.now()
            }

            if reason:
                current_notes = relationship.get('notes', '') or ''
                update_data['notes'] = f"{current_notes}\n\nTerminated: {reason}".strip()

            success = self.relationship_repo.update_by_id(relationship_id, update_data)

            if success:
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
            else:
                return False, "Failed to terminate relationship"

        except Exception as e:
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
        # Map permission types to repository method names
        permission_map = {
            'can_view_documents': 'view_documents',
            'can_add_notes': 'add_notes',
            'can_request_tests': 'request_tests'
        }

        mapped_permission = permission_map.get(permission_type, permission_type.replace('can_', ''))
        return self.relationship_repo.check_access_permission(patient_id, professional_id, mapped_permission)

    def get_shared_patients(self, professional_id: int) -> List[int]:
        """
        Get list of patient IDs that a professional has access to.

        Args:
            professional_id: ID of the professional

        Returns:
            List of patient IDs
        """
        relationships = self.relationship_repo.get_professional_relationships(professional_id, 'active')
        return [rel.get('patient_id') for rel in relationships if rel.get('can_view_documents', False)]

    def get_relationship_by_id(self, relationship_id: int) -> Optional[Dict]:
        """
        Get a relationship by ID.

        Args:
            relationship_id: ID of the relationship

        Returns:
            Relationship dictionary or None
        """
        return self.relationship_repo.get_by_id(relationship_id)

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
        return self.user_repo.search_users(query, role='professional')
