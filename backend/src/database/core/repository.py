"""
Base repository class providing ORM-like patterns with SQLAlchemy Core.
This module contains the base repository that other repositories inherit from.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime
from sqlalchemy import Table, select, insert, update, delete, and_, or_, func, text
from sqlalchemy.sql import Select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from .engine import db_engine

logger = logging.getLogger(__name__)

class BaseRepository:
    """
    Base repository class providing ORM-like patterns using SQLAlchemy Core.
    Provides common CRUD operations and query building methods.
    """
    
    def __init__(self, table: Table):
        """
        Initialize the repository with a table.
        
        Args:
            table: SQLAlchemy Core Table instance
        """
        self.table = table
        self.engine = db_engine
    
    def create(self, data: Dict[str, Any]) -> Optional[int]:
        """
        Create a new record.
        
        Args:
            data: Dictionary of column values
            
        Returns:
            ID of created record or None if failed
        """
        try:
            # Prepare data for insertion
            insert_data = self._prepare_insert_data(data)
            
            stmt = insert(self.table).values(**insert_data)
            
            with self.engine.transaction() as conn:
                result = conn.execute(stmt)
                record_id = result.inserted_primary_key[0]
                logger.debug(f"Created record with ID {record_id} in {self.table.name}")
                return record_id
                
        except IntegrityError as e:
            logger.error(f"Integrity error creating record in {self.table.name}: {e}")
            raise ValueError(f"Data integrity violation: {e}")
        except SQLAlchemyError as e:
            logger.error(f"Database error creating record in {self.table.name}: {e}")
            return None
    
    def find_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        Find a record by its ID.
        
        Args:
            record_id: Primary key value
            
        Returns:
            Record dictionary or None if not found
        """
        try:
            stmt = select(self.table).where(self.table.c.id == record_id)
            
            with self.engine.connection() as conn:
                result = conn.execute(stmt)
                row = result.fetchone()
                
                if row:
                    return self._row_to_dict(row)
                return None
                
        except SQLAlchemyError as e:
            logger.error(f"Database error finding record by ID in {self.table.name}: {e}")
            return None
    
    def find_one(self, **criteria) -> Optional[Dict[str, Any]]:
        """
        Find a single record by criteria.
        
        Args:
            **criteria: Column-value pairs for filtering
            
        Returns:
            Record dictionary or None if not found
        """
        try:
            stmt = select(self.table)
            stmt = self._apply_criteria(stmt, criteria)
            
            with self.engine.connection() as conn:
                result = conn.execute(stmt)
                row = result.fetchone()
                
                if row:
                    return self._row_to_dict(row)
                return None
                
        except SQLAlchemyError as e:
            logger.error(f"Database error finding record in {self.table.name}: {e}")
            return None
    
    def find_many(self, limit: Optional[int] = None, offset: Optional[int] = None, 
                  order_by: Optional[str] = None, **criteria) -> List[Dict[str, Any]]:
        """
        Find multiple records by criteria.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            order_by: Column name to order by
            **criteria: Column-value pairs for filtering
            
        Returns:
            List of record dictionaries
        """
        try:
            stmt = select(self.table)
            stmt = self._apply_criteria(stmt, criteria)
            
            if order_by and hasattr(self.table.c, order_by):
                stmt = stmt.order_by(getattr(self.table.c, order_by))
            
            if offset:
                stmt = stmt.offset(offset)
            
            if limit:
                stmt = stmt.limit(limit)
            
            with self.engine.connection() as conn:
                result = conn.execute(stmt)
                return [self._row_to_dict(row) for row in result.fetchall()]
                
        except SQLAlchemyError as e:
            logger.error(f"Database error finding records in {self.table.name}: {e}")
            return []
    
    def update_by_id(self, record_id: int, data: Dict[str, Any]) -> bool:
        """
        Update a record by its ID.
        
        Args:
            record_id: Primary key value
            data: Dictionary of column values to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare data for update
            update_data = self._prepare_update_data(data)
            
            stmt = update(self.table).where(self.table.c.id == record_id).values(**update_data)
            
            with self.engine.transaction() as conn:
                result = conn.execute(stmt)
                success = result.rowcount > 0
                
                if success:
                    logger.debug(f"Updated record with ID {record_id} in {self.table.name}")
                else:
                    logger.warning(f"No record found with ID {record_id} in {self.table.name}")
                
                return success
                
        except SQLAlchemyError as e:
            logger.error(f"Database error updating record in {self.table.name}: {e}")
            return False
    
    def delete_by_id(self, record_id: int) -> bool:
        """
        Delete a record by its ID.
        
        Args:
            record_id: Primary key value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            stmt = delete(self.table).where(self.table.c.id == record_id)
            
            with self.engine.transaction() as conn:
                result = conn.execute(stmt)
                success = result.rowcount > 0
                
                if success:
                    logger.debug(f"Deleted record with ID {record_id} from {self.table.name}")
                else:
                    logger.warning(f"No record found with ID {record_id} in {self.table.name}")
                
                return success
                
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting record from {self.table.name}: {e}")
            return False
    
    def count(self, **criteria) -> int:
        """
        Count records matching criteria.
        
        Args:
            **criteria: Column-value pairs for filtering
            
        Returns:
            Number of matching records
        """
        try:
            stmt = select(func.count()).select_from(self.table)
            stmt = self._apply_criteria(stmt, criteria)
            
            with self.engine.connection() as conn:
                result = conn.execute(stmt)
                return result.scalar() or 0
                
        except SQLAlchemyError as e:
            logger.error(f"Database error counting records in {self.table.name}: {e}")
            return 0
    
    def exists(self, **criteria) -> bool:
        """
        Check if any records exist matching criteria.
        
        Args:
            **criteria: Column-value pairs for filtering
            
        Returns:
            True if records exist, False otherwise
        """
        return self.count(**criteria) > 0
    
    def _apply_criteria(self, stmt: Select, criteria: Dict[str, Any]) -> Select:
        """Apply filtering criteria to a select statement."""
        for column_name, value in criteria.items():
            if hasattr(self.table.c, column_name):
                column = getattr(self.table.c, column_name)
                if isinstance(value, (list, tuple)):
                    stmt = stmt.where(column.in_(value))
                elif value is None:
                    stmt = stmt.where(column.is_(None))
                else:
                    stmt = stmt.where(column == value)
        return stmt
    
    def _prepare_insert_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for insertion, handling JSON fields and timestamps."""
        prepared = {}
        for key, value in data.items():
            if hasattr(self.table.c, key):
                # Handle JSON fields
                if key == 'details' and isinstance(value, (dict, list)):
                    prepared[key] = json.dumps(value)
                else:
                    prepared[key] = value
        return prepared
    
    def _prepare_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for update, handling JSON fields and timestamps."""
        prepared = self._prepare_insert_data(data)
        
        # Add updated_at timestamp if column exists
        if hasattr(self.table.c, 'updated_at'):
            prepared['updated_at'] = datetime.utcnow()
        
        return prepared
    
    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Convert a database row to a dictionary."""
        result = dict(row._mapping)
        
        # Handle JSON fields
        if 'details' in result and result['details']:
            try:
                result['details'] = json.loads(result['details'])
            except (json.JSONDecodeError, TypeError):
                pass  # Keep as string if not valid JSON
        
        return result
