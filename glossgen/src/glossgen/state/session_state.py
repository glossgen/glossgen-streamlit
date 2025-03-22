import streamlit as st
from typing import Dict, Any, Optional
from sqlalchemy.engine.base import Engine
import pandas as pd
from glossgen.config.app_config import AppConfig
class SessionState:
    """Manages the application's session state"""
    
    @staticmethod
    def initialize() -> None:
        """Initialize session state variables"""
        if 'db_connected' not in st.session_state:
            st.session_state['db_connected'] = False
        
        if 'engine' not in st.session_state:
            st.session_state['engine'] = None
        
        if 'extractor' not in st.session_state:
            st.session_state['extractor'] = None
        
        if 'tables' not in st.session_state:
            st.session_state['tables'] = []
        
        if 'glossary_dicts' not in st.session_state:
            st.session_state['glossary_dicts'] = {}
        
        if 'relationship_matrix' not in st.session_state:
            st.session_state['relationship_matrix'] = pd.DataFrame()  
        
        if 'generative_ai_provider' not in st.session_state:
            st.session_state['generative_ai_provider'] = AppConfig.DEFAULT_AI_PROVIDER
        
        if 'generative_ai_api_key' not in st.session_state:
            st.session_state['generative_ai_api_key'] = ""
        
        if 'generative_ai_model' not in st.session_state:
            st.session_state['generative_ai_model'] = AppConfig.DEFAULT_MODEL
            
        if 'generative_ai_endpoint' not in st.session_state:
            st.session_state['generative_ai_endpoint'] = ""
        
        if 'db_name' not in st.session_state:
            st.session_state['db_name'] = ""
        
        if 'table_descriptions' not in st.session_state:
            st.session_state['table_descriptions'] = {}
    
    @staticmethod
    def update_db_connection(is_connected: bool, engine: Optional[Engine] = None, db_name: str = "") -> None:
        """Update database connection state"""
        st.session_state['db_connected'] = is_connected
        st.session_state['engine'] = engine
        st.session_state['relationship_matrix'] = pd.DataFrame()
        st.session_state['db_name'] = db_name
        if not is_connected:
            st.session_state['tables'] = []
            st.session_state['glossary_dicts'] = {}
            st.session_state['extractor'] = None
    
    @staticmethod
    def set_extractor(extractor: Any) -> None:
        """Set the schema extractor instance"""
        st.session_state['extractor'] = extractor
        if extractor:
            st.session_state['tables'] = extractor.schema_info.keys()
    
    @staticmethod
    def update_glossary_data(glossary_dicts: Dict) -> None:
        """Update glossary data in session state"""
        st.session_state['glossary_dicts'] = glossary_dicts
    
    @staticmethod
    def update_relationship_data(relationship_matrix: Any) -> None:
        """Update relationship matrix in session state"""
        st.session_state['relationship_matrix'] = relationship_matrix
    
    @staticmethod
    def update_ai_settings(provider: str, api_key: str, model: str, endpoint: str = "") -> None:
        """Update AI settings in session state"""
        st.session_state['generative_ai_provider'] = provider
        st.session_state['generative_ai_api_key'] = api_key
        st.session_state['generative_ai_model'] = model
        st.session_state['generative_ai_endpoint'] = endpoint
    
    @staticmethod
    def get_ai_settings() -> Dict[str, str]:
        """Get current AI settings from session state"""
        return {
            'provider': st.session_state.get('generative_ai_provider', ""),
            'api_key': st.session_state.get('generative_ai_api_key', ""),
            'model': st.session_state.get('generative_ai_model', ""),
            'endpoint': st.session_state.get('generative_ai_endpoint', "")
        }