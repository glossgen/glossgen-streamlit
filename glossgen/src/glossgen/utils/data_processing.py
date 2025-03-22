from typing import Any, Dict, List
import json
import pandas as pd

def process_ai_response(response: Any) -> Dict:
    """Process the AI response for glossary generation"""
    res_json_text = response.content.replace('json\n', '').replace('\n', '').strip("```")
    res_json = json.loads(res_json_text)
    
    # Convert example values to strings
    for item in res_json:
        if 'example_values' in item:
            item['example_values'] = [str(value) for value in item['example_values']]
    
    return res_json

def process_sample_data(df: pd.DataFrame, n_samples: int = 5) -> Dict[str, List]:
    """Process sample data for each column in a DataFrame"""
    sample_data = {}
    for column in df.columns:
        sample_data[column] = df[column].dropna().head(n_samples).tolist()
    return sample_data

def calculate_column_stats(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """Calculate statistics for each column in a DataFrame"""
    stats = {}
    for column in df.columns:
        column_stats = {
            'uniqueness_percentage': (df[column].nunique() / len(df) * 100),
            'null_percentage': (df[column].isnull().sum() / len(df) * 100)
        }
        
        # Calculate primary key confidence score
        column_stats['primary_key_confidence_score'] = (
            column_stats['uniqueness_percentage'] * 
            (100 - column_stats['null_percentage']) / 100
        )
        
        stats[column] = column_stats
    
    return stats

def merge_glossary_data(
    schema_info: Dict,
    sample_data: Dict[str, List],
    column_stats: Dict[str, Dict[str, float]]
) -> pd.DataFrame:
    """Merge schema information with sample data and statistics"""
    glossary_data = []
    
    for column_name, column_info in schema_info.items():
        entry = {
            'column_name': column_name,
            'data_type': str(column_info.get('type', '')),
            'sample_data': sample_data.get(column_name, []),
            'description': '',  # To be filled by AI
            'comments': '',  # To be filled by user
            'is_primary_key': column_info.get('primary_key', False)
        }
        
        # Add statistics if available
        if column_name in column_stats:
            entry.update(column_stats[column_name])
        
        glossary_data.append(entry)
    
    return pd.DataFrame(glossary_data)

def filter_relationships(
    relationship_matrix: pd.DataFrame,
    min_confidence: float = 0.5
) -> pd.DataFrame:
    """Filter relationships based on confidence score"""
    return relationship_matrix[relationship_matrix['confidence'] >= min_confidence] 