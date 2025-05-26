"""
SQLAlchemy Core database engine and connection management.
This module provides database connection pooling and transaction management.
"""

import os
import logging
from typing import Optional, Any, Dict
from contextlib import contextmanager
from sqlalchemy import create_engine, Engine, Connection, text
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
from .tables import metadata

logger = logging.getLogger(__name__)

class DatabaseEngine:
    """
    Database engine manager with connection pooling and transaction support.
    Implements singleton pattern for shared database connections.
    """

    _instance: Optional['DatabaseEngine'] = None
    _engine: Optional[Engine] = None

    def __new__(cls) -> 'DatabaseEngine':
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the database engine if not already initialized."""
        if self._engine is None:
            self._initialize_engine()

    def _initialize_engine(self) -> None:
        """Initialize the SQLAlchemy engine with connection pooling."""
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is required")

        # Engine configuration for MySQL with connection pooling
        engine_config = {
            'poolclass': QueuePool,
            'pool_size': int(os.getenv('SQLALCHEMY_CORE_POOL_SIZE', '10')),
            'max_overflow': int(os.getenv('SQLALCHEMY_CORE_MAX_OVERFLOW', '20')),
            'pool_pre_ping': True,  # Validate connections before use
            'pool_recycle': 3600,   # Recycle connections every hour
            'echo': os.getenv('SQLALCHEMY_CORE_ECHO', 'false').lower() == 'true',
        }

        # MySQL-specific configuration
        if database_url.startswith('mysql'):
            engine_config.update({
                'connect_args': {
                    'charset': 'utf8mb4',
                    'autocommit': False,
                }
            })

        try:
            self._engine = create_engine(database_url, **engine_config)
            logger.info(f"Database engine initialized successfully")

            # Test connection
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("Database connection test successful")

        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise

    @property
    def engine(self) -> Engine:
        """Get the SQLAlchemy engine instance."""
        if self._engine is None:
            self._initialize_engine()
        return self._engine

    def get_connection(self) -> Connection:
        """Get a database connection from the pool."""
        return self.engine.connect()

    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.
        Automatically commits on success or rolls back on error.

        Usage:
            with db_engine.transaction() as conn:
                conn.execute(stmt)
        """
        conn = self.get_connection()
        trans = conn.begin()
        try:
            yield conn
            trans.commit()
            logger.debug("Transaction committed successfully")
        except Exception as e:
            trans.rollback()
            logger.error(f"Transaction rolled back due to error: {e}")
            raise
        finally:
            conn.close()

    @contextmanager
    def connection(self):
        """
        Context manager for database connections without transactions.

        Usage:
            with db_engine.connection() as conn:
                result = conn.execute(stmt)
        """
        conn = self.get_connection()
        try:
            yield conn
        finally:
            conn.close()

    def execute_query(self, query, params=None) -> Any:
        """
        Execute a query and return results.

        Args:
            query: SQL query or SQLAlchemy statement
            params: Query parameters

        Returns:
            Query result
        """
        with self.connection() as conn:
            if params:
                return conn.execute(query, params)
            else:
                return conn.execute(query)

    def execute_transaction(self, queries_and_params) -> bool:
        """
        Execute multiple queries in a single transaction.

        Args:
            queries_and_params: List of (query, params) tuples

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.transaction() as conn:
                for query, params in queries_and_params:
                    if params:
                        conn.execute(query, params)
                    else:
                        conn.execute(query)
            return True
        except SQLAlchemyError as e:
            logger.error(f"Transaction failed: {e}")
            return False

    def create_tables(self) -> None:
        """Create all tables defined in metadata."""
        try:
            metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise

    def drop_tables(self) -> None:
        """Drop all tables defined in metadata."""
        try:
            metadata.drop_all(self.engine)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise

    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the database connection.

        Returns:
            Dictionary with health check results
        """
        try:
            with self.connection() as conn:
                result = conn.execute(text("SELECT 1 as health_check"))
                row = result.fetchone()

                if row and row[0] == 1:
                    return {
                        'status': 'healthy',
                        'database': 'connected',
                        'pool_size': self.engine.pool.size(),
                        'checked_out': self.engine.pool.checkedout()
                    }
                else:
                    return {'status': 'unhealthy', 'error': 'Invalid response'}

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

    def close(self) -> None:
        """Close the database engine and all connections."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            logger.info("Database engine closed")

# Global database engine instance
db_engine = DatabaseEngine()
