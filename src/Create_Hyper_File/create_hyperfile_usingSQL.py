import mysql.connector
from tableauhyperapi import *

# Replace 'path/to/your/hyper_file.hyper' with the path where you want to create the .hyper file.
hyper_file_path = 'path/to/your/hyper_file.hyper'

# Replace 'your_mysql_host', 'your_mysql_database', 'your_mysql_user', and 'your_mysql_password' with your MySQL credentials.
mysql_host = 'your_mysql_host'
mysql_database = 'your_mysql_database'
mysql_user = 'your_mysql_user'
mysql_password = 'your_mysql_password'

# Replace 'your_mysql_table' with the name of the table from which you want to load data.
mysql_table = 'your_mysql_table'

def create_hyper_table_from_mysql(hyper_file_path, mysql_host, mysql_database, mysql_user, mysql_password, mysql_table):
    try:
        # Step 1: Connect to the MySQL database and retrieve the data
        mysql_connection = mysql.connector.connect(
            host=mysql_host,
            database=mysql_database,
            user=mysql_user,
            password=mysql_password
        )
        mysql_cursor = mysql_connection.cursor()
        mysql_cursor.execute(f"SELECT * FROM {mysql_table}")
        mysql_data = mysql_cursor.fetchall()

        # Step 2: Define the schema of the logical table (columns and their data types)
        table_definition = TableDefinition(table_name="Customer")
        for column_name, column_type in zip(mysql_cursor.column_names, mysql_cursor.column_types):
            if column_type == 'int':
                table_definition.add_column(column_name, SqlType.int())
            elif column_type == 'float':
                table_definition.add_column(column_name, SqlType.double())
            else:
                table_definition.add_column(column_name, SqlType.text())

        # Step 3: Create a connection to the .hyper file and create the logical table
        with HyperProcess(telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU) as hyper:
            with Connection(endpoint=hyper.endpoint, database=hyper_file_path, create_mode=CreateMode.CREATE_AND_REPLACE) as connection:
                connection.catalog.create_table(table_definition)
                # Step 4: Insert the data from MySQL into the logical table
                with Inserter(connection, table_definition) as inserter:
                    inserter.add_rows(rows=mysql_data)

                # Step 5: Commit the changes and close the connection
                connection.commit()

        print(f"MySQL data loaded into the logical table in '{hyper_file_path}' successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if mysql_connection.is_connected():
            mysql_cursor.close()
            mysql_connection.close()

# Load MySQL data into the logical table in the .hyper file
create_hyper_table_from_mysql(hyper_file_path, mysql_host, mysql_database, mysql_user, mysql_password, mysql_table)
