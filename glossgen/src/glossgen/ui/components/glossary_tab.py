import streamlit as st
import pandas as pd
from datetime import datetime
import json
import io
from typing import Dict, Any

from glossgen.config.app_config import AppConfig
from glossgen.state.session_state import SessionState
from glossgen.services.database import DatabaseService
from glossgen.chains.glossary_chain import GlossaryChain
from glossgen.utils.utils import process_response
# Create column configuration
column_config = {
            'column_name': st.column_config.TextColumn(
                'Column Name',
                help='Name of the column',
                width='small',
            ),
            'data_type': st.column_config.TextColumn(
                'Data Type',
                help='Data type for the column',
                width='small',
            ),
            'description': st.column_config.TextColumn(
                'Description',
                help='Enter a description for the column',
                width='medium',
                max_chars=1000
            ),
            'sample_data': st.column_config.ListColumn(
                'Sample Data',
                help='Sample data for the column',
                width='medium'
            ),
            'comments': st.column_config.TextColumn(
                'Comments',
                help='Enter any additional comments for the column',
                width='medium',
                max_chars=1000
            ),
            'is_primary_key': st.column_config.CheckboxColumn(
                'Is Primary Key',
                help='Check if the column is a primary key',
                default=False
            ),
            'uniqueness_percentage': st.column_config.NumberColumn(
                'Uniqueness Percentage',
                help='Uniqueness percentage for the column',
                min_value=0,
                max_value=100,
                format='%.0f%%',
                width='small'
            ),
            'null_percentage': st.column_config.NumberColumn(
                'Null Percentage',
                help='Null percentage for the column',
                min_value=0,
                max_value=100,
                format='%.0f%%',
                width='small'
            ),
            'primary_key_confidence_score': st.column_config.NumberColumn(
                'Primary Key Confidence Score',
                help='Primary key confidence score based on null percentage and uniqueness percentage',
                min_value=0,
                max_value=100,
                format='%.0f%%',
                width='small'
            ),
        }
        

class GlossaryTab:
    """Manages the glossary tab UI components"""
    
    def __init__(self):
        self.config = AppConfig()
        self.disabled_columns = [
            'column_name', 'sample_data', 'uniqueness_percentage',
            'null_percentage', 'primary_key_confidence_score'
        ]
    
    def render(self) -> None:
        """Render the glossary tab content"""
        if not st.session_state['db_connected']:
            st.error("Please connect to a database first.")
            return
        
        if not st.session_state['glossary_dicts']:
            with st.spinner("Generating data glossaries..."):
                glossary_dicts = st.session_state['extractor'].generate_schema_table_for_all_tables()
                SessionState.update_glossary_data(glossary_dicts)
        
        self._render_table_selector()
        self._render_glossary_editor()
        self._render_export_section()
    
    def _render_table_selector(self) -> None:
        """Render the table selection dropdown"""
        st.selectbox(
            "Select a Table",
            st.session_state['tables'],
            key='selected_glossary_table'
        )
    
    def _render_glossary_editor(self) -> None:
        """Render the glossary editor interface"""
        if 'selected_glossary_table' not in st.session_state:
            return
        
        table = st.session_state['selected_glossary_table']
        glossary_df = st.session_state['glossary_dicts'][table]
        
        
        # Create an empty container for the editor
        glossary_container = st.empty()
        
        # Display the editor
        edited_df = glossary_container.data_editor(
            glossary_df,
            disabled=self.disabled_columns,
            column_config=column_config
        )
        
        # Update button for AI-generated descriptions
        if st.button("Add or update descriptions with AI"):
            self._update_descriptions_with_ai(table, glossary_container, column_config)
    
    def _update_descriptions_with_ai(self, table: str, container: st.empty, column_config: Dict) -> None:
        """Update descriptions using AI for the selected table"""
        st.write("Started generating data glossary descriptions!")
        
        with st.spinner(f"AI generating description for table: {table}"):
            glossary_dict = st.session_state['extractor'].generate_schema_table_for_table(table)
            glossary_chain = GlossaryChain()
            response = glossary_chain.invoke(glossary_dict)
            st.write(response)
            res_json = self._process_response(response)
            df_res = pd.DataFrame(res_json)[['column_name', 'description']]
            
            if "description" not in st.session_state['glossary_dicts'][table].columns:
                st.session_state['glossary_dicts'][table] = st.session_state['glossary_dicts'][table].merge(
                    df_res, on='column_name', how='left'
                )
            else:
                st.session_state['glossary_dicts'][table]['description'] = df_res['description']
            
            # Update the displayed dataframe
            container.data_editor(
                st.session_state['glossary_dicts'][table],
                disabled=self.disabled_columns,
                column_config=column_config
            )
        
        st.write("Glossary descriptions generated by AI.")
    
    def _render_export_section(self) -> None:
        """Render the export options section"""
        st.subheader("Export Glossary")
        
        # Get database name and create default filename
        db_name = st.session_state['db_name']
        timestamp = datetime.now().strftime(self.config.TIMESTAMP_FORMAT)
        default_filename = f"data_glossary_{db_name}_{timestamp}"
        
        # File format selection
        file_format = st.selectbox(
            "Select file format",
            self.config.EXPORT_FORMATS
        )
        
        # Prepare combined dataframe
        all_glossaries = []
        for table, df in st.session_state['glossary_dicts'].items():
            df = df.copy()
            df['table_name'] = table
            all_glossaries.append(df)
        combined_df = pd.concat(all_glossaries, ignore_index=True)
        
        # Export based on selected format
        if file_format == "csv":
            self._export_csv(combined_df, default_filename)
        elif file_format == "json":
            self._export_json(combined_df, default_filename)
        elif file_format == "xlsx":
            self._export_excel(default_filename)
    
    def _export_csv(self, df: pd.DataFrame, filename: str) -> None:
        """Export glossary as CSV"""
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=f"{filename}.csv",
            mime="text/csv"
        )
    
    def _export_json(self, df: pd.DataFrame, filename: str) -> None:
        """Export glossary as JSON"""
        json_dict = {}
        for table_name, group_df in df.groupby('table_name'):
            group_df = group_df.drop('table_name', axis=1)
            json_dict[table_name] = group_df.to_dict(orient='records')
        
        json_data = json.dumps(json_dict, indent=2)
        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name=f"{filename}.json",
            mime="application/json"
        )
    
    def _export_excel(self, filename: str) -> None:
        """Export glossary as Excel"""
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
            for table, df in st.session_state['glossary_dicts'].items():
                df.to_excel(writer, index=False, sheet_name=table)
        
        st.download_button(
            label="Download Excel",
            data=excel_buffer.getvalue(),
            file_name=f"{filename}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    @staticmethod
    def _process_response(response: Any) -> Dict:
        """Process the AI response for glossary generation"""
        return process_response(response)