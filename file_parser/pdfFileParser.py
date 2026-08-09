from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from typing import List, AsyncGenerator
from .abstractClasses import FileParser

class PdfParser(FileParser): 
    def __init__(self, filePath: str): 
        self.filePath = filePath

    async def extract_docs(self) -> AsyncGenerator[Document, None]:
        loader = PyPDFLoader(self.filePath)   
        async for page in loader.alazy_load():
            yield page