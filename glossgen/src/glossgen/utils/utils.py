import json
import pandas as pd
def process_response(response):
    if isinstance(response, list):
        # Check if the list is a list of dictionaries
        if isinstance(response[0], dict):
            res_json = response
        else:
            raise ValueError("Response is not a list of dictionaries")
        
    else:
        res_json_text = response.content.replace(
            'json\n', '').replace('\n', '').strip("```")
        res_json = json.loads(res_json_text)

    # Convert all values of the list in the column "example_values" to str type
    for item in res_json:
        if 'example_values' in item:
            item['example_values'] = [str(value)
                                    for value in item['example_values']]

    return res_json

def process_sample_data_column(data_dict, column_name='sample_data'):
    # data_dict[column_name] = [str(item) for item in data_dict[column_name]]
    for item in data_dict:
        if column_name in item:
            item[column_name] = [str(value)
                                    for value in item[column_name]]
    return data_dict

def glossary_dict_to_df(glossary_dict):
    return pd.DataFrame(process_sample_data_column(glossary_dict))