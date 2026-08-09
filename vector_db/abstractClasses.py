from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

# dataclasses for indexing and querying the documents...
@dataclass
class VectorItem:
    """Data Transformation Object for vectore db input and querying"""
    id: str
    embedding: Optional[List[float]] = field(default_factory=list) 
    document: Optional[str] = None 
    metadata: Dict[str, Any] = field(default_factory=dict)

# abstract class for the vector db class  
class  VectorDBAbstract(ABC): 

    @abstractmethod
    async def add(self, documents: List[VectorItem]): 
        pass

    @abstractmethod
    async def query(self, document: VectorItem, top_n: int) -> List[VectorItem]: 
        pass 
