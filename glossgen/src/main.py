import streamlit as st
import json
import pandas as pd

from glossgen.config.app_config import AppConfig
from glossgen.state.session_state import SessionState
from glossgen.services.database import DatabaseService
from glossgen.ui.components.sidebar import Sidebar
from glossgen.ui.components.database_tab import DatabaseTab
from glossgen.ui.components.glossary_tab import GlossaryTab
from glossgen.ui.components.relationships_tab import RelationshipsTab
from glossgen.ui.components.table_description_tab import TableDescriptionTab
from glossgen.ui.components.export_tab import ExportTab
from glossgen.ui.components.instructions_tab import InstructionsTab

def main():
    """Main application entry point"""
    # Initialize configuration
    config = AppConfig()
    
    # Configure page
    st.set_page_config(
        page_title=config.PAGE_TITLE,
        page_icon=config.PAGE_ICON,
        layout=config.PAGE_LAYOUT
    )
    
    # Initialize session state
    SessionState.initialize()
    
    # Initialize services
    db_service = DatabaseService()
    
    # Render sidebar
    sidebar = Sidebar(db_service)
    sidebar.render()
    

    # Create main content tabs
    tab_database, tab_glossary, tab_relationships, tab_descriptions, tab_export, tab_instructions = st.tabs([
        "Database", "Glossary", "Table Relationships", "Table Descriptions", "Export", "Instructions"
    ])
    
    # Render main content
    with tab_database:
        DatabaseTab().render()
    
    with tab_glossary:
        GlossaryTab().render()
    
    with tab_relationships:
        RelationshipsTab().render()
        
    with tab_descriptions:
        TableDescriptionTab().render()
        
    with tab_export:
        ExportTab().render()
        
    with tab_instructions:
        InstructionsTab().render()

def _handle_csv_upload(db_service: DatabaseService, file_path: str) -> None:
    """Handle CSV file upload and database storage"""
    try:
        df = pd.read_csv(file_path)
        st.success("CSV file loaded successfully!")
        st.write(df.head(10))
        
        # Save to database
        db_service.save_dataframe(df, "uploaded_data")
        st.success(f"Data saved to database successfully!")
        
    except Exception as e:
        st.error(f"Error processing CSV file: {str(e)}")

if __name__ == "__main__":
    main()

