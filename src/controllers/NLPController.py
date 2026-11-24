from .BaseController import BaseController
from models.db_schemes import project_scheme, chunk_scheme
from stores.llm.LLMEnums import DocumentTypeEnum

class NLPController(BaseController):
    def __init__(self, vectordb_client, generation_client, embedding_client, template_parser = None):
        super().__init__()
        
        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser
        

    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()
    
    def reset_vector_db_collection(self, project: project_scheme):
        
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name = collection_name)
    
    def get_vector_db_collection_info(self, project: project_scheme):
        
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vectordb_client.get_collection_info(collection_name = collection_name)
        
        return collection_info
    
    
    def index_into_vector_db(self, project: project_scheme, chunks: list[chunk_scheme],chunk_ids: list[int], do_reset: bool = False):

        # step1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)
        
        # step2: mange items of chunks
        metadata = [c.chunk_metadata for c in chunks]
        texts = [chunk.chunk_text for chunk in chunks]

        vectors = self.embedding_client.embed_text(
            texts=texts,
            document_type=DocumentTypeEnum.DOCUMENT.value
        )

        if not vectors or len(vectors) != len(texts):
            return False
                
        # step3: create collection if not exists
        is_collection_created = self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size = self.embedding_client.embedding_size,
            do_reset = do_reset)
        
        #step4: insert into vector db
        is_inserted = self.vectordb_client.insert_many(
            collection_name = collection_name,
            texts = texts,
            vectors= vectors,
            record_ids = chunk_ids,
            metadata = metadata)
        
        return bool(is_inserted)
    
    
    def search_vector_db_collection(self, project: project_scheme, text: str, limit: int = 10):
        
        #step1: get collection name
        collection_name =  self.create_collection_name(project_id=project.project_id)
        
        # step2: get text embedding vector
        vectors = self.embedding_client.embed_text(
            texts=[text],
            document_type=DocumentTypeEnum.QUERY.value
        )

        if not vectors or not vectors[0]:
            return []

        vector = vectors[0]

        
        #step3: do semantic search
        results= self.vectordb_client.search_by_vector(
            collection_name= collection_name,
            vector= vector,
            limit = limit
        )
        
        if results is None:
            return []

        return results

    def answer_rag_question(self, project: project_scheme, query: str, limit: int = 10):
        retrieved_documents = self.search_vector_db_collection(
            project=project,
            text=query,
            limit=limit
        )

        if not retrieved_documents:
            return None, None, None

        if self.template_parser is None:
            raise RuntimeError("Template parser was not configured")

        system_prompt = self.template_parser.get("rag", "system_prompt")

        documents_prompt = "\n".join([
            self.template_parser.get("rag", "document_prompt", {
                "doc_num": idx + 1,
                "chunk_text": doc.text
            })
            for idx, doc in enumerate(retrieved_documents)
        ])

        footer_prompt = self.template_parser.get("rag", "footer_prompt", {
            "user_query": query
        })
        full_prompt = "\n\n".join([documents_prompt, footer_prompt])

        # generate_text appends its prompt to chat_history. Passing only the
        # system message prevents the user question from being sent repeatedly.
        system_message = self.generation_client.construct_prompt(
            prompt=system_prompt,
            role=self.generation_client.enums.SYSTEM.value
        )
        user_message = self.generation_client.construct_prompt(
            prompt=full_prompt,
            role=self.generation_client.enums.USER.value
        )
        chat_history = [system_message, user_message]

        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=[system_message]
        )

        return answer, full_prompt, chat_history
