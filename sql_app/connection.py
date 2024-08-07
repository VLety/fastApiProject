"""
https://docs.sqlalchemy.org/en/20/core/connections.html
When using an Engine with multiple Python processes, such as when using os.fork or Python multiprocessing,
it’s important that the engine is initialized per process.
See Using Connection Pools with Multiprocessing or os.fork() for details.
https://docs.sqlalchemy.org/en/20/core/pooling.html#pooling-multiprocessing
https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/quickstart/#initialize-the-extension
"""
import sys
import os
import inspect
import util
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text as sql_alc_text
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
curr_proj_file = os.path.basename(__file__)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class User(db.Model):
    __tablename__ = "users"  # Set relevant table name or pass this string if class name is equal table name
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    nick_name = db.Column(db.String(20), index=True)
    phone = db.Column(db.String(20), index=True)
    email = db.Column(db.String(254), index=True)
    birthday = db.Column(db.String(10), index=True)
    country = db.Column(db.String(64), index=True)
    city = db.Column(db.String(64), index=True)
    address = db.Column(db.String(254), index=True)
    created = db.Column(db.String(19), index=True)
    updated = db.Column(db.String(19), index=True)


def sqlite_db_connection():
    sqlite_db_path = util.get_config()["sqlite_db_path"]

    sqlite_engine = create_engine(f"sqlite:////{util.get_project_root()}{sqlite_db_path}", echo=False)
    sqlite_engine = sqlite_engine.execution_options(autocommit=True)

    util.print_divider("_")
    print(">>> SQLAlchemy: Try to connect to the SQLite database...")
    print("Database path/name:", sqlite_db_path)
    try:
        sqlite_conn = sqlite_engine.connect()
        sql_query = "select sqlite_version();"
        sql_result = sqlite_conn.execute(sql_alc_text(sql_query)).fetchall()
        print("Connected to SQLite version:", sql_result)
        print("SQLAlchemy: Successfully connected to the SQLite database >>>")
        util.print_divider("_")

        return sqlite_conn, sqlite_engine

    except SQLAlchemyError as exception_error:
        util.exception_handler(curr_proj_file, inspect.currentframe().f_code.co_name, repr(exception_error))
        print("SQLAlchemy: Connection to the SQLite database FAILED")
        util.print_divider("!")
        sys.exit()


def get_sql_alc_pandas_df(sql, conn):
    sql_alc = sql_alc_text(sql)
    data_frame = pd.read_sql(sql_alc, conn)

    return data_frame


def execute_sql_query_with_commit(db_conn, sql):

    query_result = db_conn.execute(sql_alc_text(sql))
    return query_result


def insert_dataframe_to_db_table(sqlite_engine, insert_df, table_name: str):
    util.print_divider(".")
    print("Trying to insert a DataFrame into a database table:", table_name)
    print(insert_df.head(5).to_string())

    # if_exists{‘fail’, ‘replace’, ‘append’}, default ‘fail’
    if_exists = 'append'

    # Specify the number of rows in each batch to be written at a time. By default, all rows will be written at once.
    chunk_size = 500

    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html
    result = insert_df.to_sql(name=table_name, con=sqlite_engine, if_exists=if_exists, chunksize=chunk_size,
                              index=False, index_label=None, method=None, dtype=None)
    print("Dataframe successfully inserted in to the database, row(s) count:", result)
    util.print_divider("-")
    return result


def insert_json_to_db_table(db_engine, insert_json, table_name):
    insert_df = pd.json_normalize(insert_json)
    db_insert_result = insert_dataframe_to_db_table(db_engine, insert_df, table_name)

    return db_insert_result


def get_db_records_by_one_column(sqlite_conn, column_name, column_value, table_name):
    if isinstance(column_value, str):
        sql_query = f"""
        SELECT * 
        FROM {table_name} 
        WHERE {column_name} = '{column_value}'
        ORDER BY created DESC
        """
    else:
        sql_query = f"""
        SELECT * 
        FROM {table_name} 
        WHERE {column_name} = {column_value}
        ORDER BY created DESC
        """

    records_df = get_sql_alc_pandas_df(sql_query, sqlite_conn)
    print(records_df.head(5).to_string())

    return records_df


def update_record_in_db(table_name, set_query_str, user_id):

    sqlite_conn, sqlite_engine = sqlite_db_connection()

    update_sql = f"""
    UPDATE {table_name}
    SET {set_query_str}
    WHERE id = '{user_id}';
    """
    # print(sql_alc_text(update_sql))

    with sqlite_engine.connect() as connection:
        sql_result = connection.execute(sql_alc_text(update_sql))
        result = sql_result.rowcount
        connection.commit()  # commit the transaction

    return result
