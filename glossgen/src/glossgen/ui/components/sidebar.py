import json
import streamlit as st
import os
from typing import Tuple, Dict, Any, Optional

from glossgen.config.app_config import AppConfig
from glossgen.state.session_state import SessionState
from glossgen.services.database import DatabaseService
from glossgen.chains.glossary_chain import GlossaryChain
from glossgen.chains.glossary_chain import TableDescriptionChain
from glossgen.utils.utils import process_response
from glossgen.utils.ai_utils import test_ai_connection
import pandas as pd

class Sidebar:
    """Manages the sidebar UI components"""
    
    def __init__(self, db_service: DatabaseService):
        self.config = AppConfig()
        self.db_service = db_service
    
    def render(self) -> Tuple[str, str]:
        """Render all sidebar components and return selected data source and file path if applicable"""
        with st.sidebar:
            self._render_about()
            self._render_ai_settings()
            # self._render_data_source()
            self._render_database_connection()
            return self._render_generate_documentation()

    def _render_about(self) -> None:
        """Render the about section"""
        with st.expander("About GlossGen"):
            st.link_button("GlossGen Homepage", "https://glossgen.github.io/", use_container_width=True)

            st.markdown("""
            # GlossGen
            
            A tool for exploring and documenting databases using AI.
            
            - Connect to various database types
            - Generate data glossaries
            - Visualize table relationships
            - Create comprehensive documentation
            """)
    
    def _render_ai_settings(self) -> None:
        """Render AI settings section"""
        with st.expander("AI Settings"):
            # AI provider selection
            provider = st.selectbox(
                "Provider", 
                options=self.config.AI_PROVIDERS,
                index=self.config.AI_PROVIDERS.index(
                    st.session_state.get('generative_ai_provider', self.config.DEFAULT_AI_PROVIDER)
                )
            )
            
            if provider not in self.config.IMPLETMENTED_AI_PROVIDERS:
                st.error(f"Only {self.config.IMPLETMENTED_AI_PROVIDERS} are supported at the moment.")
                return

            # API key input with environment variable hint
            env_key_name = self.config.ENV_API_KEYS.get(provider, "")
            api_key_help = f"If empty, using environment variable: {env_key_name}" if env_key_name else ""
            
            api_key = st.text_input(
                "API Key",
                type="password",
                value=st.session_state.get('generative_ai_api_key', ""),
                help=api_key_help
            )
            
            # Custom endpoint for OpenAI Compatible
            endpoint = ""
            if provider == "OpenAI Compatible":
                endpoint = st.text_input(
                    "API Endpoint",
                    value=st.session_state.get('generative_ai_endpoint', ""),
                    help="Full URL to the API endpoint (e.g., https://your-server.com/v1)"
                )
            else:
                endpoint = self.config.DEFAULT_ENDPOINTS.get(provider, "")
            
            # Model selection based on provider
            available_models = self.config.get_models_for_provider(provider)
            
            if provider == "OpenAI Compatible":
                model = st.text_input(
                    "Model",
                    value="",
                    help="Model name (e.g., gpt-4o-mini)"
                )
            else:
                model = st.selectbox(
                    "Model",
                    options=available_models,
                    index=0 if not st.session_state.get('generative_ai_model') else 
                        available_models.index(st.session_state.get('generative_ai_model')) 
                        if st.session_state.get('generative_ai_model') in available_models else 0
                )
            
            # Test connection button

            if st.button("Save & Test Connection"):
                with st.spinner("Testing connection..."):
                    success, message = test_ai_connection(
                        provider=provider,
                        api_key=api_key,
                        model=model,
                        endpoint=endpoint
                    )
                    SessionState.update_ai_settings(provider, api_key, model, endpoint)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
            
        
    
    def _render_data_source(self) -> Tuple[str, str]:
        """Render data source selection section"""
        st.expander("Select Data Source")
        data_source = st.radio(
            "How would you like to load data?",
            ["Upload CSV", "Connect to Database"]
        )
        
        file_path = ""
        if data_source == "Upload CSV":
            file_path = self._render_csv_upload()
        else:
            self._render_database_connection()
        
        return data_source, file_path
    
    def _render_csv_upload(self) -> str:
        """Render CSV upload section"""
        st.subheader("Upload a CSV File")
        uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
        
        if uploaded_file:
            return uploaded_file.name
        return ""
    
    def _render_database_connection(self) -> None:
        """Render database connection section"""
        with st.expander("Database Connection Settings", expanded=True):
            
            db_type = st.selectbox(
                "Select Database Type",
                options=self.config.SUPPORTED_DB_TYPES
            )
            
            # Connection parameters based on database type
            if db_type == "SQLite":
                db_path = st.text_input(
                    "Database File Path",
                    value=self.config.DEFAULT_SQLITE_PATH
                )
                params = {'db_path': db_path}
            else:
                if db_type == "MySQL":
                    host = st.text_input("Host", value=self.config.DEFAULT_MYSQL_HOST)
                    port = st.text_input("Port", value=self.config.DEFAULT_MYSQL_PORT)
                    database = st.text_input("Database Name", value=self.config.DEFAULT_MYSQL_DATABASE)
                    user = st.text_input("Username", value=self.config.DEFAULT_MYSQL_USERNAME)
                    password = st.text_input("Password", type="password", value=self.config.DEFAULT_MYSQL_PASSWORD)
                else:
                    host = st.text_input("Host", value=self.config.DEFAULT_HOST)
                    port = st.text_input("Port", value=self.config.get_db_port(db_type))
                    database = st.text_input("Database Name")
                    user = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                
                params = {
                    'host': host,
                    'port': port,
                    'database': database,
                    'user': user,
                    'password': password
                }
            
            if st.button("Connect"):
                self.db_service.connect(db_type, **params) 

    def _render_generate_documentation(self) -> None:
        """Render the generate documentation section""" 
        # Add Generate Documentation button
        st.markdown("---")
        if st.button("Generate Documentation with AI", disabled=not st.session_state['db_connected']):
            if not st.session_state['db_connected']:
                st.error("Please connect to a database first.")
                return

            with st.spinner("Generating glossary entries..."):
                # Generate glossaries for all tables
                glossary_chain = GlossaryChain()
                for table in st.session_state['tables']:
                    # Generate schema table
                    glossary_dict = st.session_state['extractor'].generate_schema_table_for_table(table)
                    
                    # Get column descriptions using GlossaryChain
                    response = glossary_chain.invoke(glossary_dict)
                    res_json = response
                    df_res = pd.DataFrame(res_json)[['column_name', 'description']]
                    
                    # Update glossary_dicts with descriptions
                    if table not in st.session_state['glossary_dicts']:
                        st.session_state['glossary_dicts'][table] = pd.DataFrame()  # Create an empty DataFrame
                    
                    if "description" not in st.session_state['glossary_dicts'][table].columns:
                        st.session_state['glossary_dicts'][table] = st.session_state['glossary_dicts'][table].merge(
                            df_res, on='column_name', how='left'
                        )
                    else:
                        st.session_state['glossary_dicts'][table]['description'] = df_res['description']
                        
                st.success("Glossary entries generated!")

            with st.spinner("Generating table descriptions..."):
                # Generate descriptions for all tables
                description_chain = TableDescriptionChain()
                relationship_matrix = st.session_state['relationship_matrix'].to_json()
                
                for table in st.session_state['tables']:
                    glossary_data = st.session_state['glossary_dicts'][table]
                    description = description_chain.invoke(
                        table,
                        glossary_data,
                        relationship_matrix
                    )
                    st.session_state['table_descriptions'][table] = description
                st.success("Table descriptions generated!")