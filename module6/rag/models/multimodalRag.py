from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class multimodalRag:
    def __init__(self, image_data_store):
        self.image_data_store = image_data_store
        self.llm = ChatOpenAI(model="gpt-4.1", temperature=0)
    

    def create_multimodal_message(self, query, retrieved_docs):
        """Create a message with both text and images for GPT-4V."""
        content = []
        
        # Add the query
        content.append({
            "type": "text",
            "text": f"Question: {query}\n\nContext:\n"
        })
        
        # Separate text and image documents
        text_docs = [doc for doc in retrieved_docs if doc.metadata.get("type") == "text"]
        image_docs = [doc for doc in retrieved_docs if doc.metadata.get("type") == "image"]
        
        # Add text context
        if text_docs:
            text_context = "\n\n".join([
                f"[Page {doc.metadata['page']}]: {doc.page_content}"
                for doc in text_docs
            ])
            content.append({
                "type": "text",
                "text": f"Text excerpts:\n{text_context}\n"
            })
        
        # Add images
        for doc in image_docs:
            image_id = doc.metadata.get("image_id")
            if image_id and image_id in self.image_data_store:
                content.append({
                    "type": "text",
                    "text": f"\n[Image from page {doc.metadata['page']}]:\n"
                })
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{self.image_data_store[image_id]}"
                    }
                })
        
        # Add instruction
        content.append({
            "type": "text",
            "text": "\n\nPlease answer the question based on the provided text and images."
        })
        
        return HumanMessage(content=content)
    
    def multimodal_pdf_rag_pipeline(self, query, context_docs):
        """Main pipeline for multimodal RAG."""
        
        # Create the chain
        prompt = ChatPromptTemplate.from_template(
            "Answer the question based on the provided context and images. "
            "Be concise and accurate.\n\nQuestion: {query}\n\nContext: {context}"
        )
        chain = prompt | self.llm | StrOutputParser()
        
        # Prepare context
        context = "\n".join([doc.page_content for doc in context_docs])
        
        # Run the chain
        response = chain.invoke({"query": query, "context": context})
        
        return response
