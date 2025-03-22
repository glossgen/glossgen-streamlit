from typing import Dict, Optional, Any
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import SQLAlchemyError

from glossgen.state.session_state import SessionState
from glossgen.config.app_config import AppConfig
from glossgen.tools.sql import SchemaExtractor

class DatabaseService:
    """Service for handling database connections and operations"""
    
    def __init__(self):
        self.config = AppConfig()
        self.engine: Optional[Engine] = None
        self.schema_extractor: Optional[SchemaExtractor] = None

    def connect(self, db_type: str, **connection_params) -> bool:
        """
        Establish database connection based on type and parameters
        Returns True if connection successful, False otherwise
        """
        try:
            self.engine = self._create_engine(db_type, **connection_params)
            self._test_connection()
            self.schema_extractor = SchemaExtractor(self.engine)

            SessionState.update_db_connection(True, self.engine, self.get_database_name())
            SessionState.set_extractor(self.schema_extractor)

            return True
        except Exception as e:
            st.error(f"Connection failed: {str(e)}")
            SessionState.update_db_connection(False)
            return False
    
    def _create_engine(self, db_type: str, **params) -> Engine:
        """Create SQLAlchemy engine based on database type"""
        if db_type == "SQLite":
            db_path = params.get('db_path', self.config.DEFAULT_SQLITE_PATH)
            return create_engine(f'sqlite:///{db_path}', echo=False)
        
        # Build connection string for other database types
        user = params.get('user', '')
        password = params.get('password', '')
        host = params.get('host', self.config.DEFAULT_HOST)
        port = params.get('port', self.config.get_db_port(db_type))
        database = params.get('database', '')
        
        if db_type == "PostgreSQL":
            return create_engine(
                f'postgresql://{user}:{password}@{host}:{port}/{database}'
            )
        elif db_type == "MySQL":
            return create_engine(
                f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'
            )
        elif db_type == "SQL Server":
            return create_engine(
                f'mssql+pymssql://{user}:{password}@{host}:{port}/{database}'
            )
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def _test_connection(self) -> None:
        """Test database connection by executing a simple query"""
        if not self.engine:
            raise ValueError("No database engine available")
        
        with self.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    
    def save_dataframe(self, df: 'pd.DataFrame', table_name: str, if_exists: str = 'replace') -> None:
        """Save pandas DataFrame to database"""
        if not self.engine:
            raise ValueError("No database engine available")
        
        df.to_sql(table_name, self.engine, if_exists=if_exists, index=False)
    
    def execute_query(self, query: str) -> Any:
        """Execute a SQL query and return results"""
        if not self.engine:
            raise ValueError("No database engine available")
        
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            return result.fetchall()
    
    def get_database_name(self) -> str:
        """Get the name of the connected database"""
        if not self.engine:
            return ""
        return self.engine.url.database.split('/')[-1].strip('.db') 