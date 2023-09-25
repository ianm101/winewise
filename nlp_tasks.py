# nlp_tasks.py
from torch import cuda
import asyncio
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
import faiss
import os
import pandas as pd
from dotenv import load_dotenv
import numpy as np
from typing import List
import traceback
from logging_config import setup_logger
import psycopg2
from postgres import PostgresService
import uuid
load_dotenv()

ps = PostgresService()

logger = setup_logger()

EMBED_DIM = os.getenv('EMBED_DIM')
EMBED_MODEL_ID = os.getenv("EMBED_MODEL_ID")

# VECTOR DATABASE
index = faiss.IndexFlatIP(int(EMBED_DIM))
idindex = faiss.IndexIDMap2(index)



device = f'cuda:{cuda.current_device()}' if cuda.is_available() else 'cpu'

embed_model = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL_ID,
    model_kwargs = {'device': device},
    encode_kwargs = {'device': device, 'batch_size': 32}
)

class NLPTasks:

    def __init__(self):
        self.index = index
        self.idindex = idindex
        self.embed_model = embed_model

    def save_faiss_index(self, filepath: str):
        faiss.write_index(self.idindex, filepath)
        logger.info(f'[COMPLETE] Successfully saved FAISS index to {filepath}.')

    def load_faiss_index(self, filepath: str):
        self.idindex = faiss.read_index(filepath)
        logger.info(f'[COMPLETE] Successfully loaded FAISS index from {filepath}.')


    def embed_and_store_df(self, df, batch_size = 32):
        backup_interval = len(df) // 5  # Calculate backup interval as 1/5 of DataFrame length
        for i in range(0, len(df), batch_size):
            i_end = min(len(df), i+batch_size)
            batch = df.iloc[i:i_end]
            batch = df.iloc[i:i_end].copy()  # Create a copy to avoid SettingWithCopyWarning
            # Generate UUIDs for each record in the batch
            batch['uuid'] = [str(uuid.uuid4()) for _ in range(len(batch))]
            
            # Insert data to Postgres
            # 1. Regular text reviews
            ps.insert_data_from_dataframe(batch, ps.engine, table='wine_reviews')

            
            # Vectorize descriptions
            descriptions = batch['description'].tolist()
            embeddings = self.embed_model.embed_documents(descriptions)
            np_embeddings = np.array(embeddings)
            
            embeddings_df = pd.DataFrame({
                'uuid': batch['uuid'],
                'embedding': np_embeddings
            })

            # 2. Vectorized versions
            ps.insert_data_from_dataframe(embeddings_df, ps.engine, table='wine_vectors')

            if (i + batch_size) % backup_interval < batch_size:
                print("Making intermediate backup")
                ps.backup_database("./sql_backup.sql")

        logger.info(f'[COMPLETE] Successfully added {len(df)} records.')


    def query_vdb(self, query: str, k: int = 3):
        # Convert the query to a vector
        query_vector = self.embed_model.embed_documents([query])
        query_np_vector = np.array(query_vector)

        # Search the FAISS index
        D, I = self.idindex.search(query_np_vector, k)

        print(f'D: {D}')
        # Retrieve the vectors of the nearest neighbors
        print(f'I: {I}')
        vectors = [self.idindex.reconstruct(i) for i in I[0]]

        # Combine the results
        results = [{'uuid': uuid, 'vector': vector, 'distance': distance} for uuid, vector, distance in zip(uuids, vectors, D[0])]

        return results



def main():
    print(os.getcwd())
    df = pd.read_csv('/home/ian/Documents/winewise/winemag-data-130k-v2.csv')
    df.drop('Unnamed: 0', inplace=True, axis=1)
    nlp = NLPTasks()

    upload_df = df.head(5000)
    nlp.embed_and_store_df(upload_df)
    
if __name__ == "__main__":
    main()