import streamlit as st
import pandas as pd
from typing import List

from glossgen.config.app_config import AppConfig
from glossgen.state.session_state import SessionState
from glossgen.services.database import DatabaseService

def get_relationship_matrix_column_config(table_options: List[str]):
    return {
        "table1": st.column_config.SelectboxColumn(
            "Table 1",
                    options=table_options,
                    required=True
                ),
                "column1": st.column_config.TextColumn(
                    "Column 1",
                    required=True
                ),
                "table2": st.column_config.SelectboxColumn(
                    "Table 2",
                    options=table_options,
                    required=True
                ),
                "column2": st.column_config.TextColumn(
                    "Column 2",
                    required=True
                ),
                "confidence": st.column_config.NumberColumn(
                    "Confidence",
                    min_value=0,
                    max_value=100,
                    format="%.0f%%",
                    required=True
                )
            }

class RelationshipsTab:
    """Manages the relationships tab UI components"""
    
    def __init__(self):
        self.config = AppConfig()
    
    def render(self) -> None:
        """Render the relationships tab content"""
        if not st.session_state['db_connected']:
            st.error("Please connect to a database first.")
            return
        
        selected_tables = self._render_table_selector()
        if selected_tables:
            self._render_relationship_analysis(selected_tables)
    
    def _render_table_selector(self) -> List[str]:
        """Render the table selection interface"""
        return st.multiselect(
            "Select tables to analyze relationships",
            options=st.session_state['tables'],
            default=st.session_state['tables'],
            help="Select multiple tables to analyze their relationships. By default, all tables are selected."
        )
    
    def _render_relationship_analysis(self, selected_tables: List[str]) -> None:
        """Render the relationship analysis interface"""
        # if st.session_state["relationship_matrix"].empty:
        
        if len(selected_tables) > 1:
            with st.spinner("Analyzing table relationships..."):
                relationship_matrix = st.session_state['extractor'].get_relationship_matrix(
                    selected_tables
                )
                SessionState.update_relationship_data(relationship_matrix)
        else:
            st.info("Please select at least two tables to analyze relationships.")
            return
        
        st.header("Table Relationships")
        st.write("The following relationships were detected between the selected tables:")
        
        # Create relationship editor
        edited_rel_matrix = st.data_editor(
            st.session_state['relationship_matrix'],
            num_rows="dynamic",
            column_config=get_relationship_matrix_column_config(st.session_state['tables'])
        )
        
        # Update button
        if st.button("Update Relationships"):
            SessionState.update_relationship_data(edited_rel_matrix)
            st.success("Relationships updated successfully!")
        

        # Visualize relationships
        if not st.session_state['relationship_matrix'].empty:
            st.subheader("Relationship Visualization")
            st.write("Use the camera icon to download the visualization as a PNG image.")
            fig = st.session_state['extractor'].visualize_relationships_plotly(
                st.session_state['relationship_matrix']
            )
            st.plotly_chart(fig, use_container_width=False)

        # Download section
        self._download_rel_matrix()
        
    def _download_rel_matrix(self):
        st.subheader("Download Relationship Table.")
        col1, col2 = st.columns(2)
        
        with col1:
            csv = st.session_state['relationship_matrix'].to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name="table_relationships.csv",
                mime="text/csv"
            )
                
        with col2:
            json_str = st.session_state['relationship_matrix'].to_json(orient="records")
            st.download_button(
                label="Download as JSON", 
                data=json_str,
                file_name="table_relationships.json",
                mime="application/json"
            )
    
    def _filter_relationships(self, relationship_matrix: pd.DataFrame, min_confidence: float) -> pd.DataFrame:
        """Filter relationships based on confidence score"""
        return relationship_matrix[relationship_matrix['confidence'] >= min_confidence]