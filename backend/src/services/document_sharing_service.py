"""
Document Sharing Service for Patient-Professional Relationships.
This module handles document sharing permissions and access control between patients and professionals.
"""
from typing import List, Dict, Optional, Set
from ..services.relationship_service import RelationshipService
from ..services.audit_service import audit_service
from ..services.document_service import document_service
from ..models.database import User


class DocumentSharingService:
    """Service for managing document sharing between patients and professionals."""

    def __init__(self):
        """Initialize the document sharing service."""
        self.relationship_service = RelationshipService()
        self.audit_service = audit_service
        self.document_service = document_service

    def get_shared_documents_for_professional(
        self,
        professional_id: int,
        patient_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Get all documents that a professional has access to.

        Args:
            professional_id: ID of the healthcare professional
            patient_id: Optional patient ID to filter documents

        Returns:
            List of document metadata with sharing information
        """
        try:
            # Get all patients this professional has access to
            if patient_id:
                # Check if professional has access to this specific patient
                has_access = self.relationship_service.check_access_permission(
                    patient_id=patient_id,
                    professional_id=professional_id,
                    permission_type='can_view_documents'
                )
                if not has_access:
                    return []
                patient_ids = [patient_id]
            else:
                patient_ids = self.relationship_service.get_shared_patients(professional_id)

            if not patient_ids:
                return []

            # Get documents for these patients from vector database
            shared_documents = []

            for pid in patient_ids:
                # Get patient info
                patient = User.query.get(pid)
                if not patient:
                    continue

                # Get documents for this patient
                patient_docs = self.document_service.get_documents_by_user(str(pid))

                for doc in patient_docs:
                    # Add patient information and sharing metadata
                    doc_info = {
                        'document_id': doc.get('id'),
                        'filename': doc.get('source', 'Unknown'),
                        'content_type': doc.get('content_type', 'unknown'),
                        'upload_date': doc.get('upload_date'),
                        'patient_id': pid,
                        'patient_name': patient.get_full_name(),
                        'patient_username': patient.username,
                        'shared_via_relationship': True,
                        'access_permissions': {
                            'can_view': True,
                            'can_download': True,
                            'can_annotate': self.relationship_service.check_access_permission(
                                patient_id=pid,
                                professional_id=professional_id,
                                permission_type='can_add_notes'
                            )
                        }
                    }
                    shared_documents.append(doc_info)

            # Log the access
            self.audit_service.log_action(
                action='shared_documents_accessed',
                resource_type='document',
                user_id=professional_id,
                details={
                    'patient_ids': patient_ids,
                    'document_count': len(shared_documents),
                    'specific_patient_filter': patient_id
                }
            )

            return shared_documents

        except Exception as e:
            return []

    def get_patient_shared_documents(self, patient_id: int) -> List[Dict]:
        """
        Get all documents for a patient with sharing status.

        Args:
            patient_id: ID of the patient

        Returns:
            List of documents with sharing information
        """
        try:
            # Get patient's documents
            patient_docs = self.document_service.get_documents_by_user(str(patient_id))

            # Get professionals who have access to this patient
            relationships = self.relationship_service.get_patient_professionals(
                patient_id=patient_id,
                status='active'
            )

            shared_with = []
            for rel in relationships:
                if rel.get('can_view_documents', False):
                    shared_with.append({
                        'professional_id': rel['professional_id'],
                        'professional_name': rel['professional']['full_name'],
                        'relationship_type': rel['relationship_type'],
                        'permissions': {
                            'can_view_documents': rel.get('can_view_documents', False),
                            'can_add_notes': rel.get('can_add_notes', False),
                            'can_request_tests': rel.get('can_request_tests', False)
                        }
                    })

            # Add sharing information to each document
            documents_with_sharing = []
            for doc in patient_docs:
                doc_info = {
                    'document_id': doc.get('id'),
                    'filename': doc.get('source', 'Unknown'),
                    'content_type': doc.get('content_type', 'unknown'),
                    'upload_date': doc.get('upload_date'),
                    'shared_with_count': len(shared_with),
                    'shared_with_professionals': shared_with,
                    'is_shared': len(shared_with) > 0
                }
                documents_with_sharing.append(doc_info)

            return documents_with_sharing

        except Exception as e:
            return []

    def check_document_access(
        self,
        user_id: int,
        document_id: str,
        user_role: str
    ) -> Dict[str, bool]:
        """
        Check if a user has access to a specific document.

        Args:
            user_id: ID of the user requesting access
            document_id: ID of the document
            user_role: Role of the user (patient/professional)

        Returns:
            Dictionary with access permissions
        """
        try:
            # Get document metadata from document service
            doc_metadata = self.document_service.get_document_metadata(document_id)
            if not doc_metadata:
                return {'can_view': False, 'can_download': False, 'can_annotate': False}

            document_owner_id = doc_metadata.get('user_id')
            if not document_owner_id:
                return {'can_view': False, 'can_download': False, 'can_annotate': False}

            # If user is the document owner, they have full access
            if str(user_id) == str(document_owner_id):
                return {'can_view': True, 'can_download': True, 'can_annotate': True}

            # If user is a professional, check if they have access to the patient
            if user_role == 'professional':
                patient_id = int(document_owner_id)

                # Check relationship and permissions
                can_view = self.relationship_service.check_access_permission(
                    patient_id=patient_id,
                    professional_id=user_id,
                    permission_type='can_view_documents'
                )

                can_annotate = self.relationship_service.check_access_permission(
                    patient_id=patient_id,
                    professional_id=user_id,
                    permission_type='can_add_notes'
                )

                if can_view:
                    # Log the access check
                    self.audit_service.log_document_access(
                        user_id=user_id,
                        document_id=document_id,
                        document_name=doc_metadata.get('source', 'Unknown'),
                        access_type='access_check',
                        patient_id=patient_id
                    )

                return {
                    'can_view': can_view,
                    'can_download': can_view,
                    'can_annotate': can_annotate
                }

            # Patients can only access their own documents
            return {'can_view': False, 'can_download': False, 'can_annotate': False}

        except Exception as e:
            return {'can_view': False, 'can_download': False, 'can_annotate': False}

    def log_document_access(
        self,
        user_id: int,
        document_id: str,
        access_type: str,
        success: bool = True
    ):
        """
        Log document access for audit purposes.

        Args:
            user_id: ID of the user accessing the document
            document_id: ID of the document
            access_type: Type of access (view, download, upload, delete)
            success: Whether the access was successful
        """
        try:
            # Get document metadata
            doc_metadata = self.document_service.get_document_metadata(document_id)
            document_name = doc_metadata.get('source', 'Unknown') if doc_metadata else 'Unknown'
            patient_id = doc_metadata.get('user_id') if doc_metadata else None

            # Log the access
            self.audit_service.log_document_access(
                user_id=user_id,
                document_id=document_id,
                document_name=document_name,
                access_type=f"{access_type}_{'success' if success else 'failed'}",
                patient_id=int(patient_id) if patient_id else None
            )

        except Exception as e:
            pass

    def get_document_access_logs(
        self,
        document_id: str,
        days: int = 30
    ) -> List[Dict]:
        """
        Get access logs for a specific document.

        Args:
            document_id: ID of the document
            days: Number of days to look back

        Returns:
            List of access log entries
        """
        return self.audit_service.get_document_audit_logs(document_id, days)

    def get_patient_access_summary(
        self,
        patient_id: int,
        days: int = 30
    ) -> Dict:
        """
        Get a summary of who has accessed a patient's data.

        Args:
            patient_id: ID of the patient
            days: Number of days to look back

        Returns:
            Summary of access activity
        """
        try:
            # Get all access logs for this patient
            logs = self.audit_service.get_patient_access_logs(patient_id, days)

            # Analyze the logs
            professional_access = {}
            document_access = {}

            for log in logs:
                user_id = log.get('user_id')
                if user_id and user_id != patient_id:  # Exclude patient's own access
                    # Get professional info
                    professional = User.query.get(user_id)
                    if professional and professional.role == 'professional':
                        prof_name = professional.get_full_name()

                        if prof_name not in professional_access:
                            professional_access[prof_name] = {
                                'professional_id': user_id,
                                'access_count': 0,
                                'last_access': None,
                                'actions': []
                            }

                        professional_access[prof_name]['access_count'] += 1
                        professional_access[prof_name]['actions'].append(log.get('action'))

                        if not professional_access[prof_name]['last_access'] or \
                           log.get('timestamp') > professional_access[prof_name]['last_access']:
                            professional_access[prof_name]['last_access'] = log.get('timestamp')

                # Track document access
                if log.get('resource_type') == 'document':
                    doc_id = log.get('resource_id')
                    if doc_id:
                        if doc_id not in document_access:
                            document_access[doc_id] = {
                                'document_name': log.get('details', {}).get('document_name', 'Unknown'),
                                'access_count': 0,
                                'last_access': None
                            }

                        document_access[doc_id]['access_count'] += 1
                        if not document_access[doc_id]['last_access'] or \
                           log.get('timestamp') > document_access[doc_id]['last_access']:
                            document_access[doc_id]['last_access'] = log.get('timestamp')

            return {
                'patient_id': patient_id,
                'period_days': days,
                'total_access_events': len(logs),
                'professional_access': professional_access,
                'document_access': document_access,
                'unique_professionals': len(professional_access)
            }

        except Exception as e:
            return {
                'patient_id': patient_id,
                'period_days': days,
                'total_access_events': 0,
                'professional_access': {},
                'document_access': {},
                'unique_professionals': 0
            }
