import streamlit as st
import pandas as pd
from typing import Dict, Any

from glossgen.config.app_config import AppConfig
from glossgen.state.session_state import SessionState
from glossgen.services.database import DatabaseService
from glossgen.chains.glossary_chain import TableDescriptionChain

class TableDescriptionTab:
    """Manages the table description tab UI components"""
    
    def __init__(self):
        self.config = AppConfig()
        self.description_chain = TableDescriptionChain()
    
    def render(self) -> None:
        """Render the table description tab content"""
        if not st.session_state['db_connected']:
            st.error("Please connect to a database first.")
            return
        
        if not st.session_state.get('glossary_dicts'):
            st.info("No glossary data available. Please generate glossaries from the Database tab first.")
            return
            
        if st.session_state['relationship_matrix'].empty:
            st.info("No relationship data available. Please generate relationships from the Database tab first.")
            return
        
        self._render_table_selector()
        self._render_description_generator()
        self._render_export_section()
    def _render_table_selector(self) -> None:
        """Render the table selection dropdown"""
        st.selectbox(
            "Select a Table",
            st.session_state['tables'],
            key='selected_description_table'
        )
    
    def _render_description_generator(self) -> None:
        """Render the description generation interface"""
        if 'selected_description_table' not in st.session_state:
            return
            
        table = st.session_state['selected_description_table']
        
        # Get table metadata
        glossary_data = st.session_state['glossary_dicts'][table]
        relationship_matrix = st.session_state['relationship_matrix'].to_json()
        
        # Generate or retrieve description
        if 'table_descriptions' not in st.session_state:
            st.session_state['table_descriptions'] = {}
            
        if table not in st.session_state['table_descriptions']:
            if st.button("Generate Description"):
                with st.spinner(f"Generating description for table: {table}"):
                    description = self.description_chain.invoke(
                                    table,
                                    glossary_data,
                                    relationship_matrix
                                )
                    st.session_state['table_descriptions'][table] = description
        
        # Display description if available
        if table in st.session_state['table_descriptions']:
            st.markdown("### Table Description")
            st.markdown(st.session_state['table_descriptions'][table])
            
            # Add refresh button
            if st.button("Regenerate Description"):
                with st.spinner(f"Regenerating description for table: {table}"):
                    description = self.description_chain.invoke(
                                    table,
                                    glossary_data,
                                    relationship_matrix
                                )
                    st.session_state['table_descriptions'][table] = description
                st.experimental_rerun()
    
        
    def _render_export_section(self) -> None:
        """Render the export options section"""
        if not st.session_state.get('table_descriptions'):
            return
            
        st.subheader("Export Descriptions")
        
        # Get database name for filename
        db_name = st.session_state['db_name']
        
        # Prepare markdown content
        markdown_content = self._generate_markdown_documentation()
        
        # Export as Markdown 
        st.download_button(
            label="Download Documentation (Markdown)",
            data=markdown_content,
            file_name=f"table_descriptions_{db_name}.md",
            mime="text/markdown"
        )
    
    def _generate_markdown_documentation(self) -> str:
        """Generate complete markdown documentation"""
        db_name = st.session_state['db_name']
        content = [
            f"# Database Documentation: {db_name}",
            "\n## Table Descriptions\n"
        ]
        
        # Add each table description
        for table in sorted(st.session_state['tables']):
            if table in st.session_state['table_descriptions']:
                content.append(f"### {table}")
                content.append(st.session_state['table_descriptions'][table])
                content.append("\n---\n")
        
        return "\n".join(content) 
    