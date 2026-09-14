import os
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_engine(database_url=None):
    url = database_url or DATABASE_URL
    if not url:
        raise ValueError("DATABASE_URL is not configured.")
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    try:
        return create_engine(url, pool_pre_ping=True, connect_args={"connect_timeout": 15})
    except ValueError:
        raise ValueError("DATABASE_URL contains an invalid connection parameter, such as a non-numeric port.") from None
def import_sales():
    data = pd.read_csv(r"C:\Users\oszge\Documents\CodeCool\python\envPython\analysis_automation\sales_data_v2")

    insert_query = text("""
        INSERT INTO sales_v2 (
            sale_date,
            product,
            category,
            country,
            quantity,
            revenue
        )
        VALUES (
            :sale_date,
            :product,
            :category,
            :country,
            :quantity,
            :revenue
        );
    """)


    sales_data = data.to_dict(orient="records")


    with get_engine().begin() as connection:
        connection.execute(insert_query, sales_data)


    print("Data imported successfully.")

def load_sales(database_url=None):
    query = """
    SELECT
        sale_date,
        product,
        category,
        country,
        quantity,
        revenue,
        'EUR' AS currency
    FROM sales_v2
    ORDER BY sale_date;
    """

    engine = get_engine(database_url)
    try:
        with engine.connect() as connection:
            return pd.read_sql(text(query), connection)
    finally:
        engine.dispose()
