from tableauhyperapi import *

# Replace 'path/to/your/hyper_file.hyper' with the path where you want to create the .hyper file.
hyper_file_path = 'target/target_hyper_files/customer_data.hyper'
csv_file_path = 'TestData/hyper_file_data.csv'

def create_hyper_table_from_csv(hyper_file_path, csv_file_path):
    # Step 1: Define the schema of the logical table (columns and their data types)
    table_definition = TableDefinition(table_name="customer")
    customer_table = TableDefinition(
    # Since the table name is not prefixed with an explicit schema name, the table will reside in the default "public" namespace.
    table_name="Customer",
    columns=[
        TableDefinition.Column(name="customer_id", type=SqlType.text(), nullability=NOT_NULLABLE),
        TableDefinition.Column(name="customer_name", type=SqlType.text(), nullability=NOT_NULLABLE),
        TableDefinition.Column(name="loyalty_reward_points", type=SqlType.big_int(), nullability=NOT_NULLABLE),
        TableDefinition.Column(name="segment", type=SqlType.text(), nullability=NOT_NULLABLE)
    ]
)

    try:
        # Step 2: Create a connection to the .hyper file and create the logical table
        with HyperProcess(telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU) as hyper:
            with Connection(endpoint=hyper.endpoint, database=hyper_file_path, create_mode=CreateMode.CREATE_AND_REPLACE) as connection:
                connection.catalog.create_table(customer_table)

                # Step 3: Read the CSV data and insert it into the logical table
                with open(csv_file_path, 'r') as csv_file:
                    connection.execute_command(
                        f"COPY {customer_table.table_name} FROM {escape_string_literal(csv_file.name)} WITH (format csv, NULL '', delimiter ',', header)"
                    )

        print(f"CSV data loaded into the logical table in '{hyper_file_path}' successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Load CSV data into the logical table in the .hyper file
create_hyper_table_from_csv(hyper_file_path, csv_file_path)
