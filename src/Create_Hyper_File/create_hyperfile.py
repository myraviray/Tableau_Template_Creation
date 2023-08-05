from tableauhyperapi import *


# Replace 'path/to/your/hyper_file.hyper' with the path where you want to create the Hyper file.
hyper_file_path = 'dfds.hyper'

try:
    # Step 1: Connect to the Hyper file
    with HyperProcess(telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU) as hyper:
        with Connection(endpoint=hyper.endpoint, database=hyper_file_path,
                        create_mode=CreateMode.CREATE_AND_REPLACE) as connection:
            # Step 2: Define logical tables and their schema using SQL statements
            create_table_sql = """
                CREATE TABLE LogicalTable1 (
                    Column1 int,
                    Column2 varchar(255),
                    Column3 varchar(255)
                );
            """

            # Step 3: Execute the SQL statement to create logical tables in the Hyper file
            connection.execute_command(create_table_sql)

            # Step 4: Commit the changes and close the Hyper file
           #S connection.commit()

    print(f"Hyper file '{hyper_file_path}' with logical tables created successfully.")

except Exception as e:
    print(f"An error occurred: {e}")
