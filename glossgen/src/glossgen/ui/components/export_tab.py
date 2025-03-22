import streamlit as st
import pandas as pd
from typing import Dict, Any

from glossgen.config.app_config import AppConfig
from glossgen.state.session_state import SessionState
from glossgen.services.database import DatabaseService
from glossgen.chains.glossary_chain import TableDescriptionChain

class ExportTab:
    """Manages the export tab UI components"""
    
    def __init__(self):
        self.config = AppConfig()
    
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
        
        self._render_export_all_section()


    
    def _render_export_all_section(self) -> None:
        """Render the export all section"""
        if not st.session_state.get('tables'):
            return
            
        st.subheader("Export Documentation")
        
        # Get database name for filename
        db_name = st.session_state['db_name']
        
        # Generate markdown content
        markdown_content = self._generate_complete_documentation()
        st.download_button(
            label="Download Complete Documentation (Markdown)", 
            data=markdown_content,
            file_name=f"database_documentation_{db_name}.md",
            mime="text/markdown"
        )
        st.write("---")
        st.write(markdown_content)
        # Export as Markdown

    
    def _generate_complete_documentation(self) -> str:
        """Generate complete markdown documentation including tables list, relationships and details"""
        db_name = st.session_state['db_name']
        content = [
            f"# Database Documentation: {db_name}\n",
            "## Tables Overview\n"
        ]
        
        # Add table list with short descriptions
        for table in sorted(st.session_state['tables']):
            description = st.session_state.get('table_descriptions', {}).get(table, 'No description defined.')
            # Get first sentence for short description
            short_desc = description.split('.')[0] + '.'
            content.append(f"- **{table}**: {short_desc}\n")
            
        # Add relationships section
        content.append("\n## Table Relationships\n")
        if not st.session_state.get('relationship_matrix').empty:
            for _, row in st.session_state['relationship_matrix'].iterrows():
                content.append(
                    f"- {row['table1']}.{row['column1']} → {row['table2']}.{row['column2']} "
                    f"(Confidence: {row['confidence']}%)\n"
                )
        else:
            content.append("No relationships defined.\n")
            
        # Add detailed table documentation
        content.append("\n## Detailed Table Documentation\n")
        for table in sorted(st.session_state['tables']):
            content.append(f"\n### {table}\n")
            
            # Table description
            description = st.session_state.get('table_descriptions', {}).get(table, 'No description defined.')
            content.append(f"#### Description\n{description}\n")
            # Table glossary
            content.append("#### Glossary\n")
            glossary_df = st.session_state.get('glossary_dicts', {}).get(table)
            if isinstance(glossary_df, pd.DataFrame) and not glossary_df.empty:
                # Convert DataFrame to markdown table
                # Replace any | characters with \| to escape them
                glossary_df = glossary_df.astype(str).replace('\|', '\\|', regex=True)
                glossary_df = glossary_df.fillna('')
                markdown_table = glossary_df.to_markdown(index=False)
                content.append(markdown_table + "\n")
            else:
                content.append("No glossary entries available.\n")
        return "\n".join(content)
