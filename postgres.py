from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, inspect, MetaData, select
from orm.models import *
import pandas as pd
import os
import psycopg2
import subprocess
from dotenv import load_dotenv
from logging_config import setup_logger
logger = setup_logger()
load_dotenv()

# REGULAR, GOOD OL' FASHION SQL DATABASE
SQL_HOSTNAME = os.getenv("SQL_HOSTNAME")
SQL_PORT = os.getenv("SQL_PORT")
SQL_DB_NAME = os.getenv("SQL_DB_NAME")
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")



class PostgresService:

    def __init__(self):
        # Database URL
        self.database_url = f"""{SQL_DB_NAME}://{SQL_USERNAME}:{SQL_PASSWORD}@{SQL_HOSTNAME}/winewise"""
        # Create Engine
        self.engine = create_engine(self.database_url)

        # Start Session
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        

    def insert_data_from_dataframe(self, df, engine, table: str):
        df.to_sql(table, engine, if_exists='append', index=False)

    def insert_review_from_dict(self, data, session):
        review = WineReview(**data)
        session.add(review)
        session.commit()

    def insert_vector_from_dict(self, data, session):
        vector = WineReviewVector(**data)
        session.add(vector)
        session.commit()

    def backup_database(self, backup_filepath: str):
        try:
            subprocess.run(['pg_dump', '-U', SQL_USERNAME, '-h', SQL_HOSTNAME, '-p', SQL_PORT, '-F', 'c', '-b', '-v', '-f', backup_filepath, SQL_DB_NAME])
            logger.info(f'[COMPLETE] Successfully backed up database to {backup_filepath}.')
        except Exception as e:
            logger.error(f'[ERROR] Failed to backup database: {e}')

    def restore_database(self, backup_filepath: str):
        try:
            subprocess.run(['pg_restore', '-U', SQL_USERNAME, '-h', SQL_HOSTNAME, '-p', SQL_PORT, '-d', SQL_DB_NAME, '-v', backup_filepath])
            logger.info(f'[COMPLETE] Successfully restored database from {backup_filepath}.')
        except Exception as e:
            logger.error(f'[ERROR] Failed to restore database: {e}')


    def test_query(self):
        stmt = select(WineReview).where(WineReview.country == "US")
        result = self.session.execute(stmt).all()

        print(f"[COMPLETED] Successful test query: {result}")
        return result
    
    def _show_tables(self):
        # Use inspector to get table information
        inspector = inspect(self.engine)
        tables = inspector.get_table_names()
        for table in tables:
            print(table)

    def _show_all_table_columns(self):
        # Use inspector to get table and column information
        inspector = inspect(self.engine)
        tables = inspector.get_table_names()
        for table in tables:
            print(f"Table: {table}")
            columns = inspector.get_columns(table)
            for column in columns:
                print(f"  Column: {column['name']}, Type: {column['type']}")

    def _delete_all_tables(self):
        meta = MetaData()
        meta.reflect(bind=self.engine)
        meta.drop_all(bind=self.engine)

    def _delete_table(self, table_name):
        meta = MetaData()
        meta.reflect(bind=self.engine)
        table = meta.tables.get(table_name)
        if table is not None:
            table.drop(bind=self.engine)

    def _create_all(self):
        Base.metadata.create_all(self.engine)


def main():
    logger.info("STARTING POSTGRES SERVICE")
    ps = PostgresService()

    
    print("Tables: ")
    ps._show_tables()
    print("Tables with Columns: ")
    ps._show_all_table_columns()

    ps.test_query()
    print("Deleting a specific table...")
    ps._delete_table('wine_reviews')  # Replace 'table_name' with the name of the table you want to delete
    print("Deleting all tables...")
    ps._delete_all_tables()
    print("Creating all tables...")
    ps._create_all()
    print("done")

if __name__ == "__main__":
    main()