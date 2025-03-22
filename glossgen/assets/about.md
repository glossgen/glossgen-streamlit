Welcome to GlossGen! This tool helps you explore, document, and understand your databases using AI.
Follow the steps below to get started.

## Contents
1. [Getting Started](#getting-started)
2. [Connecting to a Database](#connecting-to-a-database)
3. [Exploring Tables](#exploring-tables)
4. [Generating Glossaries](#generating-glossaries)
5. [Visualizing Relationships](#visualizing-relationships)
6. [Creating Table Descriptions](#creating-table-descriptions)
7. [Exporting Documentation](#exporting-documentation)
8. [AI Provider Settings](#ai-provider-settings)
9. [Troubleshooting](#troubleshooting)

## Getting Started

GlossGen is designed to help you:
- Connect to various database types (MySQL, PostgreSQL, SQLite, MS SQL Server)
- Explore table structures and data
- Generate data glossaries with AI-powered descriptions
- Visualize and understand table relationships
- Create comprehensive documentation for your database

The application is organized into tabs, each with a specific purpose:
- **Database**: Connect to databases and explore tables
- **Glossary**: View and edit AI-generated column descriptions
- **Table Relationships**: Visualize how tables are connected
- **Table Descriptions**: Generate comprehensive table documentation
- **Instructions**: This guide

To begin, you'll need to connect to a database using the sidebar.

## Connecting to a Database

1. In the sidebar, expand the **Database Connection** section
2. Select your database type (MySQL, PostgreSQL, SQLite, MS SQL Server)
3. Enter the connection details:
    - Host (default: localhost)
    - Port (auto-filled based on database type)
    - Username and Password
    - Database name
4. Click **Connect**

For SQLite databases, you can simply browse and select a .db file.

Once connected, the application will load the list of available tables.

## Exploring Tables

After connecting to a database:

1. In the **Database** tab, you'll see a list of available tables
2. Select a table to view a preview of its data
3. The preview shows the first few rows and all columns
4. You can also run custom SQL queries if needed

This gives you a quick overview of the data structure before generating documentation.

## Generating Glossaries

Glossaries provide detailed descriptions of each column in your tables:

1. In the **Database** tab, select a table
2. Click **Generate Glossary** to create AI-powered descriptions
3. The system will analyze column names, data types, and sample data
4. Switch to the **Glossary** tab to view and edit the results
5. You can manually edit any description if needed
6. Click **Update with AI** to regenerate specific descriptions

The glossary includes:
- Column descriptions
- Data type information
- Primary key identification
- Null and uniqueness percentages

You can export glossaries in various formats (CSV, JSON, Excel).

## Visualizing Relationships

Understanding table relationships is crucial for database documentation:

1. In the **Database** tab, click **Generate Relationships**
2. The system will analyze foreign key relationships and data patterns
3. Switch to the **Table Relationships** tab to view the results
4. You'll see two visualizations:
    - A heatmap matrix showing relationship strengths
    - A network graph showing connections between tables

Stronger relationships are indicated by darker colors in the matrix and thicker lines in the graph.

## Creating Table Descriptions

For comprehensive documentation of each table:

1. First, generate both glossaries and relationships
2. Go to the **Table Descriptions** tab
3. Select a table from the dropdown
4. Click **Generate Description**
5. The AI will create a detailed description including:
    - Overview of the table's purpose
    - Detailed column information
    - Relationships with other tables
    - Usage guidelines

You can regenerate descriptions if needed, and export all descriptions as a markdown document.

## Exporting Documentation

GlossGen allows you to export documentation in various formats:

- **Glossaries**: Export as CSV, JSON, or Excel from the Glossary tab
- **Relationships**: Export as CSV from the Table Relationships tab
- **Table Descriptions**: Export as Markdown from the Table Descriptions tab

The exported files include timestamps and database names for easy identification.

## AI Provider Settings

GlossGen supports multiple AI providers for generating descriptions:

1. In the sidebar, expand the **AI Settings** section
2. Select your preferred provider:
    - OpenAI (default)
    - Deepseek
    - OpenAI Compatible (for self-hosted models)
    - Claude
    - Google Gemini
3. Enter your API key or use environment variables
4. Select a model from the available options
5. For OpenAI Compatible providers, enter the API endpoint
6. Click **Test Connection** to verify your settings
7. Click **Save Settings** to store your preferences

If no API key is provided, the system will check for environment variables based on the selected provider.

## Troubleshooting

Common issues and solutions:

**Connection Problems**
- Verify your database credentials
- Check that the database server is running
- Ensure your IP has access to the database server

**AI Generation Issues**
- Verify your API key is correct
- Check your internet connection
- Ensure you have sufficient API credits
- Try a different model or provider

**Performance Considerations**
- Large tables may take longer to analyze
- Complex relationship analysis may be resource-intensive
- Consider limiting the number of tables for initial testing

**Data Privacy**
- GlossGen sends sample data to AI providers for analysis
- Only a small subset of data is used (typically 5 rows)
- No full table data is ever sent to external services
- Use OpenAI Compatible with a self-hosted model for maximum privacy

---

For more information, visit the [GlossGen GitHub repository](https://github.com/glossgen/glossgen_streamlit).
