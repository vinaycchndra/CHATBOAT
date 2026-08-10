import asyncio
from services import EmbeddingService

async def main():
    # await EmbeddingService.VectorEmbeddingService.createEmbeddingForFile(fileType="application/pdf", filePath="./data/Medical_book.pdf", userId=1, documentId=1)
    data = await EmbeddingService.VectorEmbeddingService.QueryVectorDb(user_id=1, text = "what is this sebaceous glands ?", top_n=10)
    for data_ in data: 
        print(data_, "\n\n\n")
asyncio.run(main())
