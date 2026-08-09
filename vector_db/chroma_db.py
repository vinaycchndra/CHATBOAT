import logging
from typing import List
from chromadb import AsyncHttpClient
from vector_db.abstractClasses import VectorDBAbstract, VectorItem
from vector_db.constants import VECTOR_DB_COLLECTION, VECTOR_DB_HOST, VECTOR_DB_PORT

logger = logging.getLogger(__name__)

# Concrete croma db class
class CromadbVectorDB(VectorDBAbstract): 
    _instance = None 

    @classmethod
    async def getVectorDb(cls) -> VectorDBAbstract: 
        if cls._instance is None:
            client = AsyncHttpClient(host=VECTOR_DB_HOST, port=VECTOR_DB_PORT) 
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
