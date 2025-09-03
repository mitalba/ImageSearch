
from fastapi import FastAPI, UploadFile, File
from typing import List
from sentence_transformers import SentenceTransformer
from PIL import Image
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os, shutil

app = FastAPI()

CATALOG_DIR = "catalog"
os.makedirs(CATALOG_DIR, exist_ok=True)

model = SentenceTransformer("clip-ViT-B-32")

# In-memory database {filename: embedding}
catalog_db = {}


def extract_features(image_path: str) -> np.ndarray:
    """Extract CLIP embedding from an image"""
    img = Image.open(image_path).convert("RGB")
    embedding = model.encode(img, convert_to_tensor=False, normalize_embeddings=True)
    return embedding


@app.post("/add_catalog/")
async def add_catalog(files: List[UploadFile] = File(...)):

    for file in files:
        file_path = os.path.join(CATALOG_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        catalog_db[file.filename] = extract_features(file_path)

    return {"message": f"Added {len(files)} items to catalog"}


@app.post("/search/")
async def search_similar(file: UploadFile = File(...), top_k: int = 3):

    query_path = os.path.join(CATALOG_DIR, f"query_{file.filename}")
    with open(query_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    query_features = extract_features(query_path)

    if not catalog_db:
        return {"message": "Catalog is empty. Please upload items first."}

    similarities = {
        fname: float(cosine_similarity([query_features], [emb])[0][0])
        for fname, emb in catalog_db.items()
    }

    sorted_results = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:top_k]

    return {
        "query": file.filename,
        "matches": [{"item": fname, "score": score} for fname, score in sorted_results],
    }
