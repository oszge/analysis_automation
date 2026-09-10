import os
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)
def import_sales():
    data = pd.read_csv(r"C:\Users\oszge\Documents\CodeCool\python\envPython\analysis_automation\sales_data")

    insert_query = text("""
        INSERT INTO sales (
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


    with engine.begin() as connection:
        connection.execute(insert_query, sales_data)


    print("Data imported successfully.")

def load_sales():
    query = """
    SELECT
        sale_date,
        product,
        category,
        country,
        quantity,
        revenue
    FROM sales
    ORDER BY sale_date;
    """

    return pd.read_sql(query, engine)