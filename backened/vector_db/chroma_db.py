import logging
from typing import List
from chromadb import AsyncHttpClient
from vector_db.constants import VECTOR_DB_COLLECTION, VECTOR_DB_HOST, VECTOR_DB_PORT
from vector_db.abstractClasses import VectorDBAbstract, VectorItem

# quadrant imports 
from qdrant_client import AsyncQdrantClient, models


logger = logging.getLogger(__name__)

# Concrete croma db class
class CromadbVectorDB(VectorDBAbstract): 
    _instance = None 

    @classmethod
    async def getVectorDb(cls) -> VectorDBAbstract: 
        if cls._instance is None:
            client = await AsyncHttpClient(host=VECTOR_DB_HOST, port=int(VECTOR_DB_PORT)) 
            collection_instance = await client.get_or_create_collection(name=VECTOR_DB_COLLECTION)
            cls._instance = cls()
            cls._instance.client = client
            cls._instance.collection = collection_instance 

        return cls._instance


    async def add(self, documents: List[VectorItem]): 
        ids, embeddings, documents_, metadata_ = list(), list(), list(), list()

        for document in documents: 
            ids.append(document.id)
            embeddings.append(document.embedding)
            documents_.append(document.document)
            metadata_.append(document.metadata)
        try:
            await self.collection.add(documents=documents_, ids=ids, metadatas=metadata_, embeddings=embeddings)    
        except Exception as e: 
            logger.exception(e)
            raise Exception("Something happened while trying to add to the collection")

    async def query(self, document: VectorItem, top_n: int) -> List[VectorItem]: 
        query = dict() 

        if document.embedding:
            query["query_embeddings"] =  [document.embedding]
        else:
            raise Exception("Need embeddings for semantic search...")

        if document.metadata:
            query["where"] = document.metadata
        
        res = await self.collection.query(**query, n_results=top_n)

        result = []
        documents =  res["documents"][0] if res["documents"] else []
        ids = res["ids"][0] if res["ids"] else []
        metadata = res["metadatas"][0] if res["metadatas"] else []

        for i in range(len(ids)):
            input_ = {} 

            if len(ids) > 0:
                input_["id"] = ids[i]

            if len(documents) > 0:
                input_["document"] = documents[i]
            else:
                input_["document"] = None

            if len(metadata) > 0:
                input_["metadata"] = metadata[i]
            else: 
                input_["metadata"] = dict()

            result.append(VectorItem(**input_))
        return result

# Concrete Quandrant db class
# this is required as the cromadb does not support hybrid search for the local setup.
class QuadrantVectorDB(VectorDBAbstract): 
    _instance = None 

    @classmethod
    async def getVectorDb(cls) -> VectorDBAbstract: 
        if cls._instance is None:
            client = AsyncQdrantClient(host=VECTOR_DB_HOST, port=int(VECTOR_DB_PORT)) 
            collection_exists = await client.collection_exists(collection_name=VECTOR_DB_COLLECTION)
            if not collection_exists:
                await client.create_collection(
                        collection_name=VECTOR_DB_COLLECTION,
                        vectors_config={
                            "dense": models.VectorParams(
                                size=384,
                                distance=models.Distance.COSINE,
                            ),
                            "multi": models.VectorParams(
                                size=96,
                                distance=models.Distance.COSINE,
                                multivector_config=models.MultiVectorConfig(
                                    comparator=models.MultiVectorComparator.MAX_SIM,
                                ),
                                hnsw_config=models.HnswConfigDiff(m=0)  #  Disable HNSW for reranking
                            ),
                        },
                        sparse_vectors_config={
                            "sparse": models.SparseVectorParams(modifier=models.Modifier.IDF)
                        }
                    )
            cls._instance = cls()
            cls._instance.client = client
            cls._instance.dense_embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
            cls._instance.sparse_embedding_model = "qdrant/bm25"
            cls._instance.late_interaction_embedding_model = "answerdotai/answerai-colbert-small-v1"

        return cls._instance


    async def add(self, documents: List[VectorItem]): 
        points = [
                    models.PointStruct(
                            id=document.id,
                            vector={
                                "dense": document.embedding,
                                "sparse": models.Document(text=document.document, model=self.sparse_embedding_model),
                                "multi": models.Document(text=document.document, model=self.late_interaction_embedding_model),
                            },
                            payload={"text": document.document, **document.metadata}
                        )
                        for document in documents
                ]

        try:
            await self.client.upsert(collection_name=VECTOR_DB_COLLECTION, points=points)    
        except Exception as e: 
            logger.exception(e)
            raise Exception("Something happened while trying to add to the collection")

    async def query(self, document: VectorItem, top_n: int) -> List[VectorItem]: 

        prefetch = [
            models.Prefetch(
                query=document.embedding,
                using="dense",
                filter = models.Filter(
                                      must=[models.FieldCondition(key="user_id", match=models.MatchValue(value=document.metadata.get("user_id")))]
                                    ),
                limit=top_n,
            ),
            models.Prefetch(
                query=models.Document(text=document.document, model=self.sparse_embedding_model),
                using="sparse",
                filter = models.Filter(
                      must=[models.FieldCondition(key="user_id", match=models.MatchValue(value=document.metadata.get("user_id")))]
                    ),
                limit=top_n,
            ),
        ]
        
        res = await self.client.query_points(
                    VECTOR_DB_COLLECTION,
                    prefetch=prefetch,
                    query=models.Document(text=document.document, model=self.late_interaction_embedding_model),
                    using="multi",
                    with_payload=True,
                    limit=top_n,   
                )

        res = res.points
        result = []
        
        for point in res:
            input_ = {}
            payload= point.payload

            input_["id"] = point.id
            input_["document"] = payload.get("text")

            del payload["text"]
            input_["metadata"] = payload
            
            result.append(VectorItem(**input_))
        return result
