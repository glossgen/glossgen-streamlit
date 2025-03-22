from sqlalchemy import inspect, text
import pandas as pd

from glossgen.utils.utils import process_response, process_sample_data_column, glossary_dict_to_df

class SchemaExtractor:
    def __init__(self, engine):
        self.engine = engine
        self.connection = self.engine.connect()
        self.inspector = inspect(self.engine)

        self.schema_info = self.extract_schema()

    def extract_schema(self):
        schema_info = {}
        for table_name in self.inspector.get_table_names():
            columns = self.inspector.get_columns(table_name)
            schema_info[table_name] = {
                'columns': columns,
                'dtypes': {column['name']: column['type'] for column in columns},
                'primary_key': self.inspector.get_pk_constraint(table_name),
                'foreign_keys': self.inspector.get_foreign_keys(table_name),
                'indexes': self.inspector.get_indexes(table_name)
            }
        return schema_info

    def get_top_n_dataframe(self, table, n=5):
        try:
            if self.engine.dialect.name == 'mssql':
                return pd.read_sql(
                    f"SELECT TOP {n} * FROM {table}", self.connection)
            else:
                return pd.read_sql(
                    f"SELECT * FROM {table} LIMIT {n}", self.connection)
        except Exception as e:
            return pd.DataFrame(data=[["Error"]])

    def get_top_n_dataframe_for_all_tables(self, n=5):
        all_tables_top_n_data = {}
        for table, _ in self.schema_info.items():
            all_tables_top_n_data[table] = self.get_top_n_dataframe(table, n)
        return all_tables_top_n_data


    def get_null_percentage(self, table):
        '''
        Returns the percentage of null values for each column in the specified table.
        '''
        column_stats = {}
        details = self.schema_info.get(table, {})
        
        try:
            with self.engine.connect() as conn:
                # Get total row count
                count_query = text(f"SELECT COUNT(*) FROM {table}")
                total_rows = conn.execute(count_query).scalar()
                
                if total_rows == 0:
                    return {}
                
                # Calculate null percentage for each column
                for column in details.get('columns', []):
                    try:
                        null_query = text(f"SELECT COUNT(*) FROM {table} WHERE {column['name']} IS NULL")
                        null_count = conn.execute(null_query).scalar()
                        null_percentage = (null_count / total_rows) * 100 if total_rows > 0 else 0
                        column_stats[f"{column['name']}"] = null_percentage
                    except Exception as e:
                        print(f"Error calculating null percentage for column {column['name']}: {str(e)}")
                        column_stats[f"{column['name']}"] = None
                        
        except Exception as e:
            print(f"Error calculating column stats for table {table}: {str(e)}")
            return {}
            
        return column_stats

    def get_uniqueness_percentage(self, table):
        '''
        Returns the percentage of unique values for each column in the specified table.
        '''
        column_stats = {}
        details = self.schema_info.get(table, {})
        
        try:
            with self.engine.connect() as conn:
                # Get total row count
                count_query = text(f"SELECT COUNT(*) FROM {table}")
                total_rows = conn.execute(count_query).scalar()
                
                if total_rows == 0:
                    return {}
                    
                # Calculate uniqueness percentage for each column
                for column in details.get('columns', []):
                    try:
                        unique_query = text(f"SELECT COUNT(DISTINCT {column['name']}) FROM {table}")
                        unique_count = conn.execute(unique_query).scalar()
                        unique_percentage = (unique_count / total_rows) * 100 if total_rows > 0 else 0
                        column_stats[f"{column['name']}"] = unique_percentage
                    except Exception as e:
                        print(f"Error calculating uniqueness for column {column['name']}: {str(e)}")
                        column_stats[f"{column['name']}"] = None
                        
        except Exception as e:
            print(f"Error calculating uniqueness stats for table {table}: {str(e)}")
            return {}
            
        return column_stats

    def get_null_percentage_for_all_tables(self):
        '''
        Returns the count, mean, min, and max for each numeric column in all tables in the database.
        '''
        schema_info = self.extract_schema()
        table_stats = {}
        for table in schema_info.keys():
            table_stats[table] = self.get_column_null_stats(table)
        return table_stats

    def get_uniqueness_percentage_for_all_tables(self):
        '''
        Returns the percentage of unique values for each column in all tables in the database.
        '''
        schema_info = self.extract_schema()
        table_stats = {}
        for table in schema_info.keys():
            table_stats[table] = self.get_column_uniqueness_stats(table)
        return table_stats

    def get_sample_data_query(self, table, n=5):
        '''
        Returns a query to get a sample of n rows from a specified table in the database.
        '''
        if self.engine.dialect.name == 'sqlite':
            sample_data_query = f"SELECT * FROM {table} ORDER BY RANDOM() LIMIT {n}"
        elif self.engine.dialect.name == 'mysql':
            sample_data_query = f"SELECT * FROM {table} ORDER BY RAND() LIMIT {n}"
        elif self.engine.dialect.name == 'postgresql':
            sample_data_query = f"SELECT * FROM {table} ORDER BY RANDOM() LIMIT {n}"
        elif self.engine.dialect.name == 'mssql':
            sample_data_query = f"SELECT TOP {n} * FROM {table} ORDER BY NEWID()"
        return sample_data_query

    def get_sample_data(self, table, n=5):
        '''
        Returns a sample of n rows from a specified table in the database.
        '''
        try:
            query = self.get_sample_data_query(table, n)
            df = pd.read_sql(query, self.connection)
            return df.to_dict(orient='list')
        except Exception as e:
            print(e)
            return "Error"

    def get_sample_data_for_all_tables(self, n=5):
        '''
        Returns a sample of n rows from all tables in the database.
        '''
        schema_info = self.extract_schema()
        all_sample_data = {}
        for table, details in schema_info.items():
            all_sample_data[table] = self.get_sample_data(table, n)
        return all_sample_data

    def get_table_stats(self):
        '''
        Returns the count of rows in each table in the database.
        '''
        schema_info = self.extract_schema()
        table_stats = {}
        for table, details in schema_info.items():
            table_stats[table] = self.connection.execute(text(
                f"SELECT COUNT(*) FROM {table}"
            )).fetchone()[0]
        return table_stats

    def generate_schema_table_for_table(self, table):
        '''
        Generates a schema table in JSON format for a specific table based on the outputs of the get_** functions.
        Each row corresponds to each column of the original table.
        '''
        schema_info = self.schema_info.get(table, {})
        schema_table = []
        sample_data = self.get_sample_data(table)
        for column in schema_info.get('columns', []):
            column_info = {
                'column_name': column['name'],
                'data_type': str(column['type']),
                'sample_data': sample_data.get(f"{column['name']}", None),
                'description': None,
                'comments': None
            }
            schema_table.append(column_info)

        df_primary_key_inferred = self.infer_primary_key(table)
        df_schema_table = glossary_dict_to_df(schema_table)
        df_schema_table = df_schema_table.merge(df_primary_key_inferred, on='column_name', how='left')
        column_order = ['column_name', 'data_type', 'is_primary_key', 'sample_data', 'description', 'comments', 'uniqueness_percentage', 'null_percentage', 'primary_key_confidence_score']
        df_schema_table = df_schema_table[column_order]

        return df_schema_table

    def generate_schema_table_for_all_tables(self):
        '''
        Generates a schema table in JSON format for all tables based on the outputs of the get_** functions.
        Each row corresponds to each column of the original table.
        '''
        schema_info = self.extract_schema()
        all_schema_tables = {}
        for table in schema_info.keys():
            all_schema_tables[table] = self.generate_schema_table_for_table(
                table)
        return all_schema_tables


    def infer_primary_key(self, table_name):
        """
        Infers the primary key of a table by analyzing the actual data.
        This is useful when primary key information is not available in the schema metadata.
        
        The function checks each column for uniqueness and non-null values, which are
        characteristics of primary keys.
        
        Args:
            table_name: Name of the table to analyze
            
        Returns:
            Dictionary with potential primary key columns and their confidence scores
        """
        try:
            # Get all columns for the table
            columns = [col['name'] for col in self.schema_info.get(table_name, {}).get('columns', [])]
            if not columns:
                return {"error": f"No columns found for table {table_name}"}
            
            results = {}
            
            with self.engine.connect() as conn:
                # Get total row count
                count_query = text(f"SELECT COUNT(*) FROM {table_name}")
                total_rows = conn.execute(count_query).scalar()
                
                if total_rows == 0:
                    return {"error": f"Table {table_name} has no data"}
                
                # Check each column for uniqueness and null values
                for column in columns:
                    try:
                        column_results = {}
                        
                        # Check for null values
                        null_query = text(f"SELECT COUNT(*) FROM {table_name} WHERE {column} IS NULL")
                        null_count = conn.execute(null_query).scalar()
                        column_results["null_percentage"] = (null_count / total_rows) * 100
                        
                        # Check for uniqueness
                        unique_query = text(f"SELECT COUNT(DISTINCT {column}) FROM {table_name}")
                        unique_count = conn.execute(unique_query).scalar()
                        column_results["uniqueness_percentage"] = (unique_count / total_rows) * 100
                        
                        # Calculate confidence score (higher is better)
                        # A good primary key has 0% nulls and 100% uniqueness
                        null_factor = 1 - (column_results["null_percentage"] / 100)
                        unique_factor = column_results["uniqueness_percentage"] / 100
                        column_results["primary_key_confidence_score"] = null_factor * unique_factor * 100
                        
                        results[column] = column_results
                    except Exception as e:
                        # Skip columns that cannot be read
                        print(f"Skipping column {column} due to error: {str(e)}")
            
            # Sort results by confidence score
            sorted_results = {k: v for k, v in sorted(
                results.items(), 
                key=lambda item: item[1]["primary_key_confidence_score"], 
                reverse=True
            )}
            
            # Add a "best_candidate" field with the column having highest confidence
            if sorted_results:
                best_candidate = next(iter(sorted_results))
                # Create a DataFrame with columns for each metric
                
                # Prepare data for DataFrame
                df_data = []
                for column, metrics in sorted_results.items():
                    df_data.append({
                        'column_name': column,
                        'null_percentage': metrics['null_percentage'],
                        'uniqueness_percentage': metrics['uniqueness_percentage'],
                        'primary_key_confidence_score': metrics['primary_key_confidence_score'],
                        'is_primary_key': column == best_candidate
                    })
                
                # Create and return the DataFrame
                result_df = pd.DataFrame(df_data)
                return result_df
            else:
                return {"error": "Could not infer primary key"}
                
        except Exception as e:
            return {"error": f"Error inferring primary key: {str(e)}"}
        
    def infer_primary_key_for_all_tables(self):
        '''
        Infers the primary key for all tables in the database.
        '''
        schema_info = self.extract_schema()
        primary_key_stats = {}  
        for table in schema_info.keys():
            primary_key_stats[table] = self.infer_primary_key(table)
        return primary_key_stats

    ## Relationship Inference ##

    def get_potential_foreign_keys(self, table1, table2):
        '''
        Identifies potential foreign key relationships between two tables based on column names,
        data types, and sample data.
        '''
        potential_fks = []
        table1_cols = self.schema_info[table1]['columns']
        table2_cols = self.schema_info[table2]['columns']

        # Get sample data
        table1_sample = self.get_top_n_dataframe(table1, 100)
        table2_sample = self.get_top_n_dataframe(table2, 100)

        for col1 in table1_cols:
            for col2 in table2_cols:
                score = 0
                col1_name = col1['name']
                col2_name = col2['name']

                # Check data type compatibility
                if str(col1['type']) == str(col2['type']):
                    score += 0.3

                # Check column name similarity
                if col1_name.lower() == col2_name.lower():
                    score += 0.3
                elif col1_name.lower() in col2_name.lower() or col2_name.lower() in col1_name.lower():
                    score += 0.2

                # Check value overlap in sample data
                if col1_name in table1_sample and col2_name in table2_sample:
                    set1 = set(table1_sample[col1_name].dropna().astype(str))
                    set2 = set(table2_sample[col2_name].dropna().astype(str))
                    if len(set1) > 0 and len(set2) > 0:
                        overlap = len(set1.intersection(set2)) / min(len(set1), len(set2))
                        score += overlap * 0.4
                score *= 100
                if score > 30:  # Only include if reasonable confidence
                    potential_fks.append({
                        'table1': table1,
                        'column1': col1_name,
                        'table2': table2,
                        'column2': col2_name,
                        'confidence': score
                    })

        return sorted(potential_fks, key=lambda x: x['confidence'], reverse=True)

    def assert_relationship(self, table1, table2, column1, column2):
        '''
        Validates a potential foreign key relationship between two tables using SQL joins
        and returns a confidence score.
        '''
        try:
            with self.engine.connect() as conn:
                # Check for null values
                null_query = text(f"""
                    SELECT 
                        (SELECT COUNT(*) FROM {table1} WHERE {column1} IS NULL) as nulls1,
                        (SELECT COUNT(*) FROM {table2} WHERE {column2} IS NULL) as nulls2,
                        (SELECT COUNT(*) FROM {table1}) as total1,
                        (SELECT COUNT(*) FROM {table2}) as total2
                """)
                null_results = conn.execute(null_query).fetchone()
                null_score = 1 - ((null_results[0] + null_results[1]) / (null_results[2] + null_results[3]))

                # Check join coverage
                join_query = text(f"""
                    SELECT 
                        COUNT(DISTINCT t1.{column1}) as matched,
                        (SELECT COUNT(DISTINCT {column1}) FROM {table1}) as total
                    FROM {table1} t1
                    INNER JOIN {table2} t2 ON t1.{column1} = t2.{column2}
                """)
                join_results = conn.execute(join_query).fetchone()
                coverage_score = join_results[0] / join_results[1] if join_results[1] > 0 else 0

                # Calculate final confidence score
                confidence_score = (null_score * 0.3) + (coverage_score * 0.7)
                confidence_score *= 100
                return confidence_score

        except Exception as e:
            print(f"Error asserting relationship: {str(e)}")
            return 0

    def get_relationship_matrix_for_two_tables(self, table1, table2, potential_fks=None):
        '''
        Returns a relationship matrix for two tables with confidence scores for potential foreign keys.
        '''
        if potential_fks is None:
            potential_fks = self.get_potential_foreign_keys(table1, table2)

        relationships = []
        for fk in potential_fks:
            confidence = self.assert_relationship(
                fk['table1'], fk['table2'],
                fk['column1'], fk['column2']
            )
            if confidence > 0.1:  # Only include relationships with meaningful confidence
                relationships.append({
                    'table1': fk['table1'],
                    'column1': fk['column1'],
                    'table2': fk['table2'],
                    'column2': fk['column2'],
                    'confidence': confidence
                })

        return pd.DataFrame(relationships)

    def get_relationship_matrix(self, tables):
        '''
        Returns a relationship matrix for a list of tables.
        '''
        all_relationships = []
        
        # Evaluate relationships between each pair of tables
        for i, table1 in enumerate(tables):
            for table2 in tables[i+1:]:  # Avoid duplicate combinations
                potential_fks = self.get_potential_foreign_keys(table1, table2)
                relationships = self.get_relationship_matrix_for_two_tables(
                    table1, table2, potential_fks
                )
                if not relationships.empty:
                    all_relationships.append(relationships)

        # Combine all relationships into a single DataFrame
        if all_relationships:
            return pd.concat(all_relationships, ignore_index=True)
        return pd.DataFrame()
    
    def visualize_relationships(self, relationship_matrix):
        '''
        Visualizes table relationships using streamlit_agraph.
        Args:
            relationship_matrix: DataFrame containing relationship data with columns:
                table1, column1, table2, column2, confidence
        Returns:
            agraph visualization component
        '''
        from streamlit_agraph import agraph, Node, Edge, Config

        # Create nodes and edges lists
        nodes = []
        edges = []
        added_nodes = set()

        if not relationship_matrix.empty:
            # Add nodes for each unique table
            for table in set(relationship_matrix['table1'].unique()) | set(relationship_matrix['table2'].unique()):
                if table not in added_nodes:
                    nodes.append(Node(
                        id=table,
                        label=table,
                        size=25,
                        shape="circularImage",
                        image="../agents/icon_table.png",
                        
                    ))
                    added_nodes.add(table)

            # Add edges for relationships
            for _, row in relationship_matrix.iterrows():
                edge_label = f"{row['column1']} → {row['column2']}"
                edges.append(Edge(
                    source=row['table1'],
                    target=row['table2'],
                    label=edge_label
                ))

            # Configure the graph
            config = Config(
                width=800,
                height=600,
                directed=True,
                physics=True,
                hierarchical=False,
                nodeHighlightBehavior=True,
                # highlightColor="#F7A7A6",
                collapsible=True
            )

            return agraph(nodes=nodes, edges=edges, config=config)
        
        return None

    def visualize_relationships_networkx(self, relationship_matrix):
        '''
        Visualizes table relationships using networkx.
        Args:
            relationship_matrix: DataFrame containing relationship data with columns:
                table1, column1, table2, column2, confidence
        Returns:
            matplotlib figure
        '''
        import networkx as nx
        import matplotlib.pyplot as plt

        # Create a directed graph
        G = nx.DiGraph()

        if not relationship_matrix.empty:
            # Add nodes for each unique table
            tables = set(relationship_matrix['table1'].unique()) | set(relationship_matrix['table2'].unique())
            G.add_nodes_from(tables)

            # Add edges with labels
            for _, row in relationship_matrix.iterrows():
                G.add_edge(
                    row['table1'], 
                    row['table2'], 
                    label=f"{row['column1']} → {row['column2']}"
                )

            # Create the figure
            fig, ax = plt.subplots(figsize=(5, 4))
            
            # Calculate layout
            pos = nx.spring_layout(G)
            
            # Draw nodes
            nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                                 node_size=1000, ax=ax)
            
            # Draw edges
            nx.draw_networkx_edges(G, pos, edge_color='gray', 
                                 arrows=True, ax=ax)
            
            # Add node labels
            nx.draw_networkx_labels(G, pos, font_size=6)
            
            # Add edge labels
            edge_labels = nx.get_edge_attributes(G, 'label')
            nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=5)
            
            plt.title("Database Table Relationships", fontsize=6)
            plt.axis('off')
            plt.show()
            return fig
            
        return None

    def visualize_relationships_plotly(self, relationship_matrix):
        '''
        Visualizes table relationships using plotly.
        Args:
            relationship_matrix: DataFrame containing relationship data with columns:
                table1, column1, table2, column2, confidence
        Returns:
            plotly figure
        '''
        import networkx as nx
        import plotly.graph_objects as go

        # Create a directed graph
        G = nx.MultiDiGraph()  # Changed to MultiDiGraph to support multiple edges

        if not relationship_matrix.empty:
            # Add nodes for each unique table
            tables = set(relationship_matrix['table1'].unique()) | set(relationship_matrix['table2'].unique())
            G.add_nodes_from(tables)

            # Add edges with labels
            edge_labels = {}
            for _, row in relationship_matrix.iterrows():
                # Add edge with a unique key for each relationship
                G.add_edge(row['table1'], row['table2'])
                # Store all relationships between the same tables
                key = (row['table1'], row['table2'])
                if key not in edge_labels:
                    edge_labels[key] = []
                edge_labels[key].append(f"{row['column1']} → {row['column2']}")

            # Calculate layout
            pos = nx.spring_layout(G)

            # Create edge trace
            edge_x = []
            edge_y = []
            edge_text = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
                # Join all relationships between these tables with newlines
                relationships = '\n'.join(edge_labels[(edge[0], edge[1])])
                edge_text.extend([relationships, relationships, None])

            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=0.5, color='#888'),
                hoverinfo='text',
                mode='lines',
                textposition='middle center'
            )

            # Create node trace
            node_x = []
            node_y = []
            node_text = []
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(node)

            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=node_text,
                textposition="bottom center",
                marker=dict(
                    showscale=False,
                    color='lightblue',
                    size=30,
                    line_width=2
                )
            )

            # Create separate trace for edge labels
            edge_label_x = []
            edge_label_y = []
            edge_label_text = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                # Calculate midpoint for label
                mid_x = (x0 + x1) / 2
                mid_y = (y0 + y1) / 2
                edge_label_x.append(mid_x)
                edge_label_y.append(mid_y)
                # Join all relationships with newlines
                relationships = ', \n'.join(edge_labels[(edge[0], edge[1])])
                edge_label_text.append(relationships)

            edge_label_trace = go.Scatter(
                x=edge_label_x,
                y=edge_label_y,
                mode='text',
                text=edge_label_text,
                textposition='middle center',
                hoverinfo='none'
            )

            # Create figure with all traces
            fig = go.Figure(data=[edge_trace, node_trace, edge_label_trace],
                          layout=go.Layout(
                              title='Database Table Relationships',
                              autosize=True,
                              showlegend=False,
                              hovermode='closest',
                              margin=dict(b=20,l=5,r=5,t=40),
                              xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                              yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                          ))

            return fig

        return None
