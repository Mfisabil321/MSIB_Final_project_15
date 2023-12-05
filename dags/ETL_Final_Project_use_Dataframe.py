from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import pandas as pd
import fastavro
import json
from sqlalchemy import create_engine

# Define the DAG
dag = DAG(
    dag_id="extract_and_load_data_to_postgres",
    start_date=datetime(2023, 1, 1),
    schedule_interval="@daily",
    catchup=False
)

# Fungsi untuk memuat data ke PostgreSQL
def load_data_to_postgres(table_name, dataframe, conn_params):
    connection_string = f"postgresql://{conn_params['user']}:{conn_params['password']}@{conn_params['host']}:{conn_params['port']}/{conn_params['database']}"
    engine = create_engine(connection_string)
    
    try:
        dataframe.to_sql(table_name, engine, if_exists='replace', index=False)
    finally:
        engine.dispose()

# Fungsi untuk membuat tabel di PostgreSQL
def create_table_in_postgres(table_name, table_schema, conn_params):
    connection_string = f"postgresql://{conn_params['user']}:{conn_params['password']}@{conn_params['host']}:{conn_params['port']}/{conn_params['database']}"
    engine = create_engine(connection_string)
    
    try:
        engine.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({table_schema})")
    finally:
        engine.dispose()

# Definisikan informasi koneksi
conn_params = {
    "host": "dataeng-warehouse-postgres",
    "port": 5432,
    "user": "user",
    "password": "password",
    "database": "data_warehouse"
}

# Fungsi ekstraksi JSON menjadi DataFrame dan langsung ke PostgreSQL
def extract_and_load_coupons_to_postgres():
    file_path = "/opt/airflow/data/coupons.json"
    with open(file_path, 'r') as file:
        data = json.load(file)
    df = pd.DataFrame(data)
    
    table_name = "coupons"
    table_schema = "id INT PRIMARY KEY, discount_percent FLOAT"  # Ganti dengan skema yang sesuai
    create_table_in_postgres(table_name, table_schema, conn_params)
    load_data_to_postgres(table_name, df, conn_params)

# Fungsi ekstraksi dari CSV menjadi DataFrame dan langsung ke PostgreSQL (tanpa menyimpan ke CSV)
def extract_and_load_customers_to_postgres():
    file_paths = [
        '/opt/airflow/data/customer_0.csv',
        '/opt/airflow/data/customer_1.csv',
        '/opt/airflow/data/customer_2.csv',
        '/opt/airflow/data/customer_3.csv',
        '/opt/airflow/data/customer_4.csv',
        '/opt/airflow/data/customer_5.csv',
        '/opt/airflow/data/customer_6.csv',
        '/opt/airflow/data/customer_7.csv',
        '/opt/airflow/data/customer_8.csv',
        '/opt/airflow/data/customer_9.csv',
    ]
    data_frames = [pd.read_csv(file) for file in file_paths]
    combined_data = pd.concat(data_frames)
    
    table_name = "customers"
    table_schema = "id INTEGER PRIMARY KEY, first_name VARCHAR(100), last_name VARCHAR(100), address VARCHAR(20), gender VARCHAR(200), zip_code VARCHAR(200)"  #skema pada table 
    create_table_in_postgres(table_name, table_schema, conn_params)
    load_data_to_postgres(table_name, combined_data, conn_params)

# Fungsi ekstraksi dari JSON login attempts
def extract_and_load_login_attempts_to_postgres():
    file_paths = [
         '/opt/airflow/data/login_attempts_0.json',
         '/opt/airflow/data/login_attempts_1.json',
         '/opt/airflow/data/login_attempts_2.json',
         '/opt/airflow/data/login_attempts_3.json',
         '/opt/airflow/data/login_attempts_4.json',
         '/opt/airflow/data/login_attempts_5.json',
         '/opt/airflow/data/login_attempts_6.json',
         '/opt/airflow/data/login_attempts_7.json',
         '/opt/airflow/data/login_attempts_8.json',
         '/opt/airflow/data/login_attempts_9.json',
    ]
    
    data_frames = []
    
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            file_data = json.load(file)
            data_frames.append(pd.DataFrame(file_data))
    
    combined_data = pd.concat(data_frames)
    
    table_name = "login_attempts_history"
    table_schema = "id INTEGER PRIMARY KEY, customer_id INTEGER, login_success BOOLEAN, attempted_at TIMESTAMP"  # Skema tabel
    create_table_in_postgres(table_name, table_schema, conn_params)
    load_data_to_postgres(table_name, combined_data, conn_params)

# Fungsi ekstraksi dari Avro order items
def extract_and_load_order_items_to_postgres():
    file_path = "/opt/airflow/data/order_item.avro"
    data = []
    
    with open(file_path, "rb") as file:
        reader = fastavro.reader(file)
        for record in reader:
            data.append(record)
    
    table_name = "order_items"
    table_schema = "id INTEGER PRIMARY KEY, order_id INTEGER, product_id INTEGER, amount INTEGER, coupon_id INTEGER"  # Skema tabel
    create_table_in_postgres(table_name, table_schema, conn_params)
    load_data_to_postgres(table_name, pd.DataFrame(data), conn_params)

# Fungsi ekstraksi dari Parquet orders
def extract_and_load_orders_to_postgres():
    file_path = "/opt/airflow/data/order.parquet"
    data = pd.read_parquet(file_path)
    
    table_name = "orders"
    table_schema = "id INTEGER PRIMARY KEY, customer_id VARCHAR(50), status TEXT, created_at TIMESTAMP"  # Skema tabel
    create_table_in_postgres(table_name, table_schema, conn_params)
    load_data_to_postgres(table_name, data, conn_params)

# Fungsi ekstraksi dari XLS/XLSX product category
def extract_and_load_product_category_to_postgres():
    file_path = "/opt/airflow/data/product_category.xls"
    data = pd.read_excel(file_path)
    
    table_name = "product_category"
    table_schema = "id INTEGER PRIMARY KEY, name VARCHAR(50)"  # Skema tabel
    create_table_in_postgres(table_name, table_schema, conn_params)
    load_data_to_postgres(table_name, data, conn_params)

# Fungsi ekstraksi dari XLS/XLSX products
def extract_and_load_products_to_postgres():
    file_path = "/opt/airflow/data/product.xls"
    data = pd.read_excel(file_path)
    
    table_name = "products"
    table_schema = "id INTEGER PRIMARY KEY, name VARCHAR(100), price FLOAT, category_id INTEGER, supplier_id INTEGER"  # Skema tabel
    create_table_in_postgres(table_name, table_schema, conn_params)
    load_data_to_postgres(table_name, data, conn_params)

# Fungsi ekstraksi dari XLS/XLSX suppliers
def extract_and_load_suppliers_to_postgres():
    file_path = "/opt/airflow/data/supplier.xls"
    data = pd.read_excel(file_path)
    
    table_name = "suppliers"
    table_schema = "id SERIAL PRIMARY KEY, name VARCHAR(100), country VARCHAR(100)"  # Skema tabel
    create_table_in_postgres(table_name, table_schema, conn_params)
    load_data_to_postgres(table_name, data, conn_params)
# ... (fungsi lainnya seperti yang di atas)

# Define the tasks ekstraksi dan load
# Define tasks untuk ekstraksi dan load data
extract_and_load_coupons_task = PythonOperator(
    task_id="extract_and_load_coupons_to_postgres",
    python_callable=extract_and_load_coupons_to_postgres,
    dag=dag,
)

extract_and_load_customers_task = PythonOperator(
    task_id="extract_and_load_customers_to_postgres",
    python_callable=extract_and_load_customers_to_postgres,
    dag=dag,
)

extract_and_load_login_attempts_task = PythonOperator(
    task_id="extract_and_load_login_attempts_to_postgres",
    python_callable=extract_and_load_login_attempts_to_postgres,
    dag=dag,
)

extract_and_load_order_items_task = PythonOperator(
    task_id="extract_and_load_order_items_to_postgres",
    python_callable=extract_and_load_order_items_to_postgres,
    dag=dag,
)

extract_and_load_orders_task = PythonOperator(
    task_id="extract_and_load_orders_to_postgres",
    python_callable=extract_and_load_orders_to_postgres,
    dag=dag,
)

extract_and_load_product_category_task = PythonOperator(
    task_id="extract_and_load_product_category_to_postgres",
    python_callable=extract_and_load_product_category_to_postgres,
    dag=dag,
)

extract_and_load_products_task = PythonOperator(
    task_id="extract_and_load_products_to_postgres",
    python_callable=extract_and_load_products_to_postgres,
    dag=dag,
)

extract_and_load_suppliers_task = PythonOperator(
    task_id="extract_and_load_suppliers_to_postgres",
    python_callable=extract_and_load_suppliers_to_postgres,
    dag=dag,
)

# Set task dependencies
extract_and_load_coupons_task >> extract_and_load_customers_task
extract_and_load_coupons_task >> extract_and_load_login_attempts_task
extract_and_load_customers_task >> extract_and_load_orders_task
extract_and_load_orders_task >> extract_and_load_order_items_task
extract_and_load_product_category_task >> extract_and_load_products_task
extract_and_load_products_task >> extract_and_load_suppliers_task
