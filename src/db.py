from dotenv import load_dotenv
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import os

def get_engine():
    load_dotenv()
    db_server = os.getenv("DB_SERVER")
    db_name   = os.getenv("DB_NAME")

    connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={db_server};"
    f"DATABASE={db_name};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;")

    encoded_connection_string = quote_plus(connection_string)
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={encoded_connection_string}")
    return engine


