from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
)
import os
from typing import Dict, Any, Optional

from glossgen.utils.ai_utils import get_llm_client
from glossgen.utils.utils import process_response
from glossgen.state.session_state import SessionState

example_schema_data = """[
{{
"name":"show_id",
"type":"TEXT",
"num_stats":null,
"text_stats":8807,
"sample_data":[
"s2844",
"s2056",
"s8387",
"s1214",
"s7971"
]
}},
{{
"name":"type",
"type":"TEXT",
"num_stats":null,
"text_stats":2,
"sample_data":[
"Movie",
"Movie",
"Movie",
"TV Show",
"Movie"
]
}},
{{
"name":"title",
"type":"TEXT",
"num_stats":null,
"text_stats":8807,
"sample_data":[
"Aurora",
"Freaks – You're One of Us",
"The Last Hangover",
"Paradise PD",
"Secrets of Althorp - The Spencers"
]
}},
{{
"name":"director",
"type":"TEXT",
"num_stats":null,
"text_stats":4528,
"sample_data":[
"Cristi Puiu",
"Felix Binder",
"Rodrigo Van Der Put",
null,
"Kasia Uscinska"
]
}}
]"""

example_glossary_data = """[
    {{
        "column_name": "show_id",
        "description": "A unique identifier for each show in the dataset. It is likely a string that starts with 's' followed by a number, indicating a sequential or random ID."
    }},
    {{
        "column_name": "type",
        "description": "Indicates the type of the show, such as 'Movie' or 'TV Show'. This helps categorize the content into different formats."
    }},
    {{
        "column_name": "title",
        "description": "The title of the show. This is the name by which the show is known and can be used for display or search purposes."
    }}]"""

glossary_system_template_str = """
You are a helpful data engineer assistant.
Your task is to generate a data glossary table based on the input schema data extracted from a table.
You should also infer the meaning of each column. Be as detailed as possible, but
don't make up any information that's not from the context.
Return the glossary table in JSON format.

## Example
# Input Schema Table:
""" + example_schema_data + """
# Output Data Glossary Table in JSON format:
""" + example_glossary_data + """

## Database Information:
- The database type is SQL.
- The schema of the relevant table(s) is as follows:
  {schema_data}
"""

class GlossaryChain(object):
    def __init__(self):
        """Initialize the GlossaryChain"""
        glossary_system_prompt = SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=["schema_data"], template=glossary_system_template_str
            )
        )

        messages = [glossary_system_prompt]

        self.glossary_prompt_template = ChatPromptTemplate(
            input_variables=["schema_data"],
            messages=messages,
        )
        
        # LLM will be initialized when needed
        self.llm = None
    
    def _initialize_llm(self):
        """Initialize the LLM based on current session state"""
        ai_settings = SessionState.get_ai_settings()
        
        self.llm = get_llm_client(
            provider=ai_settings['provider'] or "OpenAI",
            api_key=ai_settings['api_key'],
            model=ai_settings['model'] or "gpt-3.5-turbo",
            endpoint=ai_settings['endpoint'],
            temperature=0.2
        )
    
    def invoke(self, input: dict) -> dict:
        """
        Generate a glossary for the given schema data
        
        Args:
            input: Dictionary containing schema_data
            
        Returns:
            Dictionary containing the generated glossary
        """
        # Initialize LLM if not already done
        if not self.llm:
            self._initialize_llm()
        
        # Invoke the LLM with the prompt
        response = self.llm.invoke(self.glossary_prompt_template.format(schema_data=input))
        
        # Process and return the response
        try:
            return process_response(response)
        except:
            # If JSON parsing fails, return the raw content
            return {"error": response.content}


table_description_template_str = """You are a helpful assistant that generates clear and concise descriptions of database tables based on their glossary information and relationships.

Given the table name, glossary data, and relationship data below, please generate a brief but informative description of what this table appears to represent and store.

Table Name: {table_name}

Glossary Data:
{glossary_data}

Table Relationships:
{relationship_data}

Focus on:
1. The core purpose/entity this table represents
2. Key fields and their significance 
3. Any patterns visible in the sample data
4. Relationships to other tables (based on the relationship data)

Respond with a clear 2-3 sentence description that a database user would find helpful for understanding this table's purpose and contents.

Response should be direct prose, not JSON formatted."""


class TableDescriptionChain(object):
    def __init__(self):
        """Initialize the TableDescriptionChain"""
        description_system_prompt = SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=["table_name", "glossary_data", "relationship_data"], 
                template=table_description_template_str
            )
        )

        messages = [description_system_prompt]

        self.description_prompt_template = ChatPromptTemplate(
            input_variables=["table_name", "glossary_data", "relationship_data"],
            messages=messages,
        )
        
        # LLM will be initialized when needed
        self.llm = None
    
    def _initialize_llm(self):
        """Initialize the LLM based on current session state"""
        ai_settings = SessionState.get_ai_settings()
        
        self.llm = get_llm_client(
            provider=ai_settings['provider'] or "OpenAI",
            api_key=ai_settings['api_key'],
            model=ai_settings['model'] or "gpt-3.5-turbo",
            endpoint=ai_settings['endpoint'],
            temperature=0.2
        )
    
    def invoke(self, table_name: str, glossary_data: dict, relationship_data: dict) -> str:
        """
        Generate a table description based on the provided metadata
        
        Args:
            table_metadata: Dictionary containing:
                - table_name: Name of the table
                - columns: List of column details
                - relationships: Dictionary of incoming and outgoing relationships
        
        Returns:
            LLM response containing the generated description
        """
        # Initialize LLM if not already done
        if not self.llm:
            self._initialize_llm()
        
        
        # Invoke the LLM with the prompt
        response = self.llm.invoke(
            self.description_prompt_template.format(
                table_name=table_name,
                glossary_data=glossary_data,
                relationship_data=relationship_data
            )
        )
        
        return response.content
