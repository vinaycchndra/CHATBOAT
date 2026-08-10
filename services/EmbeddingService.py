import uuid, logging
from typing import List, Any, Dict
from file_parser.pdfFileParser import PdfParser
from vector_db.chroma_db import CromadbVectorDB
from vector_db.abstractClasses import VectorItem
from vector_db.vector_embedder import VectorHuggingFaceEmbeddingModel
from langchain_text_splitters import RecursiveCharacterTextSplitter


logger = logging.getLogger(__name__)


class VectorEmbeddingService:


    @classmethod 
    async def __embedAndAddToVectorDb(cls, textChunkList: List[str], metaDataList: List[str]): 
        vectorEmbedder = VectorHuggingFaceEmbeddingModel.getVectorEmbedder()
        vectorDb = await CromadbVectorDB.getVectorDb()
        # create vector embeddings 
        try: 
            embeddings = await vectorEmbedder.aembed_documents(textChunkList)
        except Exception as e: 
            logger.exception(e)

        # Creating vector items
        vectorItems = []
        for i in range(len(textChunkList)): 
            vectorItems.append(VectorItem(id=str(uuid.uuid4()), embedding=embeddings[i], document=textChunkList[i], metadata=metaDataList[i]))

        # Add data to the vector db
        try:
            if len(vectorItems) > 0:
                await vectorDb.add(vectorItems)
                print(f"added {len(vectorItems)} items...")
        except Exception as e: 
            logger.exception(e)

    @classmethod 
    async def createEmbeddingForFile(cls, fileType: str, filePath: str, userId: int, documentId: int): 
        """
            fileType: str -> such as application/pdf
            filePath: str -> file address 
            userId: int -> User id trying to upload the file 
            documentId: int -> Id of the uploaded file in the database
        """

        if fileType == "application/pdf": 
            file_parser_object = PdfParser(filePath=filePath)
        else: 
            raise ValueError("Unsupported file type...")

        file_parser_generator = file_parser_object.extract_docs()

        textSplitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap = 50,
            length_function = len,
            separators=["\n\n", "\n", " ", ""]
            )

        chunkTextList = []
        chunkMetaData = []

        # get the document, get updated metadata... 
        async for document in file_parser_generator:
            doc_text = document.page_content
            doc_metadata =  document.metadata

            metadata = dict() 
            text = doc_text.strip() 

            if not text: 
                continue 

            metadata["user_id"] = userId
            metadata["document_id"] = documentId
            metadata["page"] = doc_metadata.get("page_label")

            # splitting the page into the chunks...
            document.metadata = metadata
            listDocuments = textSplitter.split_documents([document])
            
            for doc in listDocuments:
                
                if doc.page_content: 
                    stripedDoc = doc.page_content.strip()
                    chunkTextList.append(stripedDoc)
                    chunkMetaData.append(doc.metadata)


            if len(chunkTextList) >= 200:
                await cls.__embedAndAddToVectorDb(chunkTextList, chunkMetaData)
                chunkTextList.clear()
                chunkMetaData.clear()

        if len(chunkTextList) > 0:
            await cls.__embedAndAddToVectorDb(chunkTextList, chunkMetaData)

    @classmethod
    async def QueryVectorDb(cls, user_id: int, text: str, top_n: int) -> List[Dict[str, Any]]: 
        """
            user_id: int -> User Id 
            text: str -> User input text 
            top_n: int -> Count of nearest match
        """

        if not text: 
            return []
        
        vectorEmbedder = VectorHuggingFaceEmbeddingModel.getVectorEmbedder()
        vectorDb = await CromadbVectorDB.getVectorDb()  

        # create embedding
        embeddings = await vectorEmbedder.aembed_documents([text])

        #create vector item object
        queryDTO = VectorItem(embedding=embeddings[0], metadata={"user_id": user_id})

        # query
        try: 
            res = await vectorDb.query(document = queryDTO, top_n = top_n)
        except Exception as e: 
            raise e 

        result = []
        for item in res: 
            result.append({"text": item.document, "id": item.id, "metadata": item.metadata})

        return result