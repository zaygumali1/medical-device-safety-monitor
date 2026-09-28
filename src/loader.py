from sqlalchemy.exc import SQLAlchemyError
from src.logger import get_logger
from sqlalchemy import inspect



logger = get_logger(__name__)
def load_dataframe(df, table_name, connection):
    row_count = len(df)
    if df.empty:
        logger.info(f"No rows to load into stg.{table_name}")
        return row_count

    try:
        inspector=inspect(connection)
        if not inspector.has_table(table_name, schema="stg"):
            raise ValueError(f"Target table stg.{table_name} does not exist")
        df.to_sql(
            name=table_name,
            con=connection,
            schema='stg',
            if_exists='append',
            index=False

        )
    except SQLAlchemyError as e:
        logger.error(f"exception : {str(e)} while loading table {table_name}")
        raise
    logger.info(f"Loaded {row_count} rows into stg.{table_name}")
    return row_count