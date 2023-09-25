# main.py
from fastapi import FastAPI
from nlp_tasks import NLPTasks
from logging_config import setup_logger

logger = setup_logger()

# For separation of concerns, and separate logs permaybechance, hmmm?
nlp = NLPTasks()

app = FastAPI()



@app.post("/embed")
async def embed(texts: list):
    logger.info(f"Embedding endpoint hit with {len(texts)} texts")
    embeddings = await nlp.embed_text(texts)
    return {"embeddings": embeddings}

@app.post("/inference")
async def inference(query_embeddings: list, dataset_embeddings: list):
    logger.info(f'Inference endpoint hit with {len(query_embeddings)} queries, and {len(dataset_embeddings)} dataset embeddings')
    recommendations = await nlp.perform_inference(query_embeddings, dataset_embeddings)
    return {"recommendations": recommendations}
