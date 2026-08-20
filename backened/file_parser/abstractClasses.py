from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from abc import ABC, abstractmethod
from typing import AsyncGenerator

# Abstract pdf parser
class FileParser(ABC):
    @abstractmethod
    async def extract_docs(self) -> AsyncGenerator[Document, None]: 
        pass 