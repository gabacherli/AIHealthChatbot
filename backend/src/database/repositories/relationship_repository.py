"""
Patient-Professional Relationship repository with SQLAlchemy Core.
This module provides ORM-like patterns for relationship data operations.
"""

import logging
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from sqlalchemy import select, and_, or_, func, join
from ..core.repository import BaseRepository
from ..core.tables import patient_professional_relationships, users

logger = logging.getLogger(__name__)

class RelationshipRepository(BaseRepository):
    """
    Relationship repository providing ORM-like patterns for patient-professional relationships.
    Extends BaseRepository with relationship-specific methods.
    """
    
    def __init__(self):
        """Initialize the relationship repository."""
        super().__init__(patient_professional_relationships)
    
    def create_relationship(self, patient_id: int, professional_id: int, 
                          relationship_type: str = 'primary', status: str = 'active',
                          created_by_id: Optional[int] = None, notes: Optional[str] = None,
                          permissions: Optional[Dict[str, bool]] = None) -> Optional[int]:
        """
        Create a new patient-professional relationship.
        
        Args:
            patient_id: ID of the patient
            professional_id: ID of the healthcare professional
            relationship_type: Type of relationship
            status: Status of the relationship
            created_by_id: ID of user creating the relationship
            notes: Optional notes
            permissions: Optional permissions dictionary
            
        Returns:
            Relationship ID if successful, None otherwise
            
        Raises:
            ValueError: If relationship already exists or invalid data
        """
        # Validate that users are different
        if patient_id == professional_id:
            raise ValueError("Patient and professional cannot be the same user")
        
        # Check if relationship already exists
        existing = self.find_one(patient_id=patient_id, professional_id=professional_id)
        if existing:
            raise ValueError("Relationship already exists between these users")
        
        # Prepare relationship data
        relationship_data = {
            'patient_id': patient_id,
            'professional_id': professional_id,
            'relationship_type': relationship_type,
            'status': status,
            'created_by_id': created_by_id,
            'notes': notes
        }
        
        # Set permissions
        if permissions:
            relationship_data.update({
                'can_view_documents': permissions.get('can_view_documents', True),
                'can_add_notes': permissions.get('can_add_notes', True),
                'can_request_tests': permissions.get('can_request_tests', False)
            })
        else:
            # Default permissions
            relationship_data.update({
                'can_view_documents': True,
                'can_add_notes': True,
                'can_request_tests': False
            })
        
        return self.create(relationship_data)
    
    def find_by_patient_and_professional(self, patient_id: int, 
                                       professional_id: int) -> Optional[Dict[str, Any]]:
        """
        Find a relationship by patient and professional IDs.
        
        Args:
            patient_id: Patient ID
            professional_id: Professional ID
            
        Returns:
            Relationship dictionary or None if not found
        """
        return self.find_one(patient_id=patient_id, professional_id=professional_id)
    
    def get_patient_relationships(self, patient_id: int, 
                                status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all relationships for a patient with professional details.
        
        Args:
            patient_id: Patient ID
            status: Optional status filter
            
        Returns:
            List of relationships with professional details
        """
        try:
            # Join with users table to get professional details
            stmt = select(
                self.table,
                users.c.username.label('professional_username'),
                users.c.first_name.label('professional_first_name'),
                users.c.last_name.label('professional_last_name'),
                users.c.email.label('professional_email'),
                users.c.specialty.label('professional_specialty'),
                users.c.organization.label('professional_organization')
            ).select_from(
                self.table.join(users, self.table.c.professional_id == users.c.id)
            ).where(
                self.table.c.patient_id == patient_id
            )
            
            if status:
                stmt = stmt.where(self.table.c.status == status)
            
            stmt = stmt.order_by(self.table.c.relationship_type, users.c.last_name)
            
            with self.engine.connection() as conn:
                result = conn.execute(stmt)
                relationships = []
                
                for row in result.fetchall():
                    rel_dict = self._row_to_dict(row)
                    
                    # Add professional details
                    rel_dict['professional'] = {
                        'username': row.professional_username,
                        'first_name': row.professional_first_name,
                        'last_name': row.professional_last_name,
                        'email': row.professional_email,
                        'specialty': row.professional_specialty,
                        'organization': row.professional_organization,
                        'full_name': f"{row.professional_first_name or ''} {row.professional_last_name or ''}".strip()
                    }
                    
                    relationships.append(rel_dict)
                
                return relationships
                
        except Exception as e:
            logger.error(f"Error getting patient relationships: {e}")
            return []
    
    def get_professional_relationships(self, professional_id: int, 
                                     status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all relationships for a professional with patient details.
        
        Args:
            professional_id: Professional ID
            status: Optional status filter
            
        Returns:
            List of relationships with patient details
        """
        try:
            # Join with users table to get patient details
            stmt = select(
                self.table,
                users.c.username.label('patient_username'),
                users.c.first_name.label('patient_first_name'),
                users.c.last_name.label('patient_last_name'),
                users.c.email.label('patient_email')
            ).select_from(
                self.table.join(users, self.table.c.patient_id == users.c.id)
            ).where(
                self.table.c.professional_id == professional_id
            )
            
            if status:
                stmt = stmt.where(self.table.c.status == status)
            
            stmt = stmt.order_by(self.table.c.relationship_type, users.c.last_name)
            
            with self.engine.connection() as conn:
                result = conn.execute(stmt)
                relationships = []
                
                for row in result.fetchall():
                    rel_dict = self._row_to_dict(row)
                    
                    # Add patient details
                    rel_dict['patient'] = {
                        'username': row.patient_username,
                        'first_name': row.patient_first_name,
                        'last_name': row.patient_last_name,
                        'email': row.patient_email,
                        'full_name': f"{row.patient_first_name or ''} {row.patient_last_name or ''}".strip()
                    }
                    
                    relationships.append(rel_dict)
                
                return relationships
                
        except Exception as e:
            logger.error(f"Error getting professional relationships: {e}")
            return []
    
    def update_relationship_status(self, relationship_id: int, status: str) -> bool:
        """
        Update the status of a relationship.
        
        Args:
            relationship_id: Relationship ID
            status: New status
            
        Returns:
            True if successful, False otherwise
        """
        if status not in ['active', 'inactive', 'pending', 'terminated']:
            raise ValueError("Invalid status value")
        
        return self.update_by_id(relationship_id, {'status': status})
    
    def update_permissions(self, relationship_id: int, 
                          permissions: Dict[str, bool]) -> bool:
        """
        Update permissions for a relationship.
        
        Args:
            relationship_id: Relationship ID
            permissions: Dictionary of permissions
            
        Returns:
            True if successful, False otherwise
        """
        update_data = {}
        
        if 'can_view_documents' in permissions:
            update_data['can_view_documents'] = permissions['can_view_documents']
        
        if 'can_add_notes' in permissions:
            update_data['can_add_notes'] = permissions['can_add_notes']
        
        if 'can_request_tests' in permissions:
            update_data['can_request_tests'] = permissions['can_request_tests']
        
        if update_data:
            return self.update_by_id(relationship_id, update_data)
        
        return True
    
    def check_access_permission(self, patient_id: int, professional_id: int, 
                              permission_type: str) -> bool:
        """
        Check if a professional has a specific permission for a patient.
        
        Args:
            patient_id: Patient ID
            professional_id: Professional ID
            permission_type: Type of permission to check
            
        Returns:
            True if permission granted, False otherwise
        """
        relationship = self.find_one(
            patient_id=patient_id,
            professional_id=professional_id,
            status='active'
        )
        
        if not relationship:
            return False
        
        permission_map = {
            'view_documents': 'can_view_documents',
            'add_notes': 'can_add_notes',
            'request_tests': 'can_request_tests'
        }
        
        permission_field = permission_map.get(permission_type)
        if permission_field:
            return relationship.get(permission_field, False)
        
        return False
    
    def get_relationship_stats(self) -> Dict[str, Any]:
        """
        Get relationship statistics.
        
        Returns:
            Dictionary with relationship statistics
        """
        try:
            with self.engine.connection() as conn:
                # Total relationships
                total_stmt = select(func.count()).select_from(self.table)
                total_relationships = conn.execute(total_stmt).scalar()
                
                # Relationships by status
                status_stmt = select(
                    self.table.c.status,
                    func.count().label('count')
                ).group_by(self.table.c.status)
                
                status_counts = {}
                for row in conn.execute(status_stmt):
                    status_counts[row.status] = row.count
                
                # Relationships by type
                type_stmt = select(
                    self.table.c.relationship_type,
                    func.count().label('count')
                ).group_by(self.table.c.relationship_type)
                
                type_counts = {}
                for row in conn.execute(type_stmt):
                    type_counts[row.relationship_type] = row.count
                
                return {
                    'total_relationships': total_relationships,
                    'status_counts': status_counts,
                    'type_counts': type_counts
                }
                
        except Exception as e:
            logger.error(f"Error getting relationship stats: {e}")
            return {}

# Global relationship repository instance
relationship_repository = RelationshipRepository()

__all__ = ['RelationshipRepository', 'relationship_repository']
