"""
Audit Log repository with SQLAlchemy Core.
This module provides ORM-like patterns for audit log operations.
"""

import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_, func, desc
from ..core.repository import BaseRepository
from ..core.tables import audit_logs, users

logger = logging.getLogger(__name__)

class AuditRepository(BaseRepository):
    """
    Audit repository providing ORM-like patterns for audit log operations.
    Extends BaseRepository with audit-specific methods.
    """
    
    def __init__(self):
        """Initialize the audit repository."""
        super().__init__(audit_logs)
    
    def log_action(self, user_id: Optional[int], action: str, resource_type: str,
                   resource_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None,
                   ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Optional[int]:
        """
        Log an audit action.
        
        Args:
            user_id: ID of the user performing the action
            action: Action being performed
            resource_type: Type of resource being acted upon
            resource_id: ID of the specific resource
            details: Additional details about the action
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Audit log ID if successful, None otherwise
        """
        audit_data = {
            'user_id': user_id,
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'timestamp': datetime.utcnow()
        }
        
        # Handle details as JSON
        if details:
            audit_data['details'] = details
        
        return self.create(audit_data)
    
    def get_user_logs(self, user_id: int, days: int = 30, 
                     action_filter: Optional[str] = None,
                     resource_type_filter: Optional[str] = None,
                     limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get audit logs for a specific user.
        
        Args:
            user_id: User ID
            days: Number of days to look back
            action_filter: Optional action filter
            resource_type_filter: Optional resource type filter
            limit: Optional limit on results
            
        Returns:
            List of audit log dictionaries
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        criteria = {
            'user_id': user_id
        }
        
        try:
            stmt = select(self.table).where(
                and_(
                    self.table.c.user_id == user_id,
                    self.table.c.timestamp >= start_date
                )
            )
            
            if action_filter:
                stmt = stmt.where(self.table.c.action.ilike(f'%{action_filter}%'))
            
            if resource_type_filter:
                stmt = stmt.where(self.table.c.resource_type == resource_type_filter)
            
            stmt = stmt.order_by(desc(self.table.c.timestamp))
            
            if limit:
                stmt = stmt.limit(limit)
            
            with self.engine.connection() as conn:
                result = conn.execute(stmt)
                return [self._row_to_dict(row) for row in result.fetchall()]
                
        except Exception as e:
            logger.error(f"Error getting user audit logs: {e}")
            return []
    
    def get_resource_logs(self, resource_type: str, resource_id: str,
                         days: int = 30, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get audit logs for a specific resource.
        
        Args:
            resource_type: Type of resource
            resource_id: Resource ID
            days: Number of days to look back
            limit: Optional limit on results
            
        Returns:
            List of audit log dictionaries with user details
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        try:
            # Join with users table to get user details
            stmt = select(
                self.table,
                users.c.username.label('username'),
                users.c.first_name.label('user_first_name'),
                users.c.last_name.label('user_last_name')
            ).select_from(
                self.table.outerjoin(users, self.table.c.user_id == users.c.id)
            ).where(
                and_(
                    self.table.c.resource_type == resource_type,
                    self.table.c.resource_id == resource_id,
                    self.table.c.timestamp >= start_date
                )
            ).order_by(desc(self.table.c.timestamp))
            
            if limit:
                stmt = stmt.limit(limit)
            
            with self.engine.connection() as conn:
                result = conn.execute(stmt)
                logs = []
                
                for row in result.fetchall():
                    log_dict = self._row_to_dict(row)
                    
                    # Add user details if available
                    if row.username:
                        log_dict['user'] = {
                            'username': row.username,
                            'first_name': row.user_first_name,
                            'last_name': row.user_last_name,
                            'full_name': f"{row.user_first_name or ''} {row.user_last_name or ''}".strip()
                        }
                    
                    logs.append(log_dict)
                
                return logs
                
        except Exception as e:
            logger.error(f"Error getting resource audit logs: {e}")
            return []
    
    def get_recent_logs(self, hours: int = 24, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent audit logs across all users.
        
        Args:
            hours: Number of hours to look back
            limit: Maximum number of logs to return
            
        Returns:
            List of audit log dictionaries with user details
        """
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        try:
            # Join with users table to get user details
            stmt = select(
                self.table,
                users.c.username.label('username'),
                users.c.first_name.label('user_first_name'),
                users.c.last_name.label('user_last_name')
            ).select_from(
                self.table.outerjoin(users, self.table.c.user_id == users.c.id)
            ).where(
                self.table.c.timestamp >= start_time
            ).order_by(desc(self.table.c.timestamp)).limit(limit)
            
            with self.engine.connection() as conn:
                result = conn.execute(stmt)
                logs = []
                
                for row in result.fetchall():
                    log_dict = self._row_to_dict(row)
                    
                    # Add user details if available
                    if row.username:
                        log_dict['user'] = {
                            'username': row.username,
                            'first_name': row.user_first_name,
                            'last_name': row.user_last_name,
                            'full_name': f"{row.user_first_name or ''} {row.user_last_name or ''}".strip()
                        }
                    
                    logs.append(log_dict)
                
                return logs
                
        except Exception as e:
            logger.error(f"Error getting recent audit logs: {e}")
            return []
    
    def get_audit_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get audit statistics for the specified period.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with audit statistics
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        try:
            with self.engine.connection() as conn:
                # Total logs
                total_stmt = select(func.count()).select_from(self.table).where(
                    self.table.c.timestamp >= start_date
                )
                total_logs = conn.execute(total_stmt).scalar()
                
                # Action counts
                action_stmt = select(
                    self.table.c.action,
                    func.count().label('count')
                ).where(
                    self.table.c.timestamp >= start_date
                ).group_by(self.table.c.action).order_by(desc(func.count()))
                
                action_counts = {}
                for row in conn.execute(action_stmt):
                    action_counts[row.action] = row.count
                
                # Resource type counts
                resource_stmt = select(
                    self.table.c.resource_type,
                    func.count().label('count')
                ).where(
                    self.table.c.timestamp >= start_date
                ).group_by(self.table.c.resource_type).order_by(desc(func.count()))
                
                resource_counts = {}
                for row in conn.execute(resource_stmt):
                    resource_counts[row.resource_type] = row.count
                
                # Unique users
                unique_users_stmt = select(
                    func.count(func.distinct(self.table.c.user_id))
                ).where(
                    self.table.c.timestamp >= start_date
                )
                unique_users = conn.execute(unique_users_stmt).scalar()
                
                return {
                    'period_days': days,
                    'start_date': start_date.isoformat(),
                    'total_logs': total_logs,
                    'unique_users': unique_users,
                    'action_counts': action_counts,
                    'resource_counts': resource_counts
                }
                
        except Exception as e:
            logger.error(f"Error getting audit statistics: {e}")
            return {}
    
    def search_logs(self, search_term: str, days: int = 30, 
                   limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search audit logs by action, resource type, or details.
        
        Args:
            search_term: Search term
            days: Number of days to search
            limit: Maximum number of results
            
        Returns:
            List of matching audit log dictionaries
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        search_pattern = f"%{search_term}%"
        
        try:
            stmt = select(
                self.table,
                users.c.username.label('username'),
                users.c.first_name.label('user_first_name'),
                users.c.last_name.label('user_last_name')
            ).select_from(
                self.table.outerjoin(users, self.table.c.user_id == users.c.id)
            ).where(
                and_(
                    self.table.c.timestamp >= start_date,
                    or_(
                        self.table.c.action.ilike(search_pattern),
                        self.table.c.resource_type.ilike(search_pattern),
                        self.table.c.resource_id.ilike(search_pattern),
                        self.table.c.details.ilike(search_pattern)
                    )
                )
            ).order_by(desc(self.table.c.timestamp)).limit(limit)
            
            with self.engine.connection() as conn:
                result = conn.execute(stmt)
                logs = []
                
                for row in result.fetchall():
                    log_dict = self._row_to_dict(row)
                    
                    # Add user details if available
                    if row.username:
                        log_dict['user'] = {
                            'username': row.username,
                            'first_name': row.user_first_name,
                            'last_name': row.user_last_name,
                            'full_name': f"{row.user_first_name or ''} {row.user_last_name or ''}".strip()
                        }
                    
                    logs.append(log_dict)
                
                return logs
                
        except Exception as e:
            logger.error(f"Error searching audit logs: {e}")
            return []

# Global audit repository instance
audit_repository = AuditRepository()

__all__ = ['AuditRepository', 'audit_repository']
