
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings

class VectorHuggingFaceEmbeddingModel:
    _instance = None 

    @classmethod
    def getVectorEmbedder(cls) -> Embeddings:
        if cls._instance is None:
            cls._instance = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        return cls._instance