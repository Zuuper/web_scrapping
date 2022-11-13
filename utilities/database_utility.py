import sqlalchemy
from pymysql import Connection
from sqlalchemy import MetaData, Table, Column, Integer, String
from sqlalchemy.engine import Engine

USER = 'root'
PASSWORD = ''
HOST = '127.0.0.1'
PORT = 3306
DATABASE = 'db_scraping'
CONNECTION_URL = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DATABASE}?charset=utf8mb4"


def setup_sql_engine() -> Engine:
    engine = sqlalchemy.create_engine(CONNECTION_URL, echo=True)
    return engine


def sql_create_table(table_name, engine: Engine):
    pass
    # if not engine.dialect.has_table(engine, table_name):  # If table don't exist, Create.
    #     metadata = MetaData(engine)
    #     # Create a table with the appropriate Columns
    #     Table(table_name, metadata,
    #           Column('id', Integer, primary_key=True, nullable=False),
    #           Column('name', String), Column('Country', String),
    #           Column('Brand', String), Column('Price', Float),
    #           # Implement the creation
    #           metadata.create_all()


