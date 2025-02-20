from models.query_understanding import QueryUnderstanding
from models.session_context import SessionContext
from models.user_context import UserContext
from services.embedding_service import EmbeddingService
import asyncio
from services.query_to_taxonomy_service import QueryToTaxonomyService 
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('werkzeug').setLevel(logging.WARNING)

class QueryUnderstandingBuilder:
    def __init__(self):
        self.query_to_taxonomy_service = QueryToTaxonomyService()
        self.embedding_service = EmbeddingService()

    async def retrieve_session_context(self):
        return SessionContext()

    async def retrieve_user_context(self):
        return UserContext()

    async def infer_taxonomy(self, user_query,session_context,user_context): # pylint: disable=W0613
        return self.query_to_taxonomy_service.predict_category(user_query.query)
    
    async def infer_phrases(self, user_query,session_context,user_context):  # pylint: disable=W0613
        return ['']


    async def build(self, user_query):
        session_context = None
        user_context = None
        embedding_vector = None
        taxonomy = None
        query_expanded = None

        async with asyncio.TaskGroup() as tg:
            session_context_task = tg.create_task(self.retrieve_session_context())
            user_context_task = tg.create_task(self.retrieve_user_context())
            generate_embedding_task = tg.create_task(self.embedding_service.get_embedding(user_query.query))
            
            session_context = await session_context_task
            user_context = await user_context_task
            embedding_vector = await generate_embedding_task

        async with asyncio.TaskGroup() as tg:
            if user_query.predict_taxonomy:
                taxonomy_task = tg.create_task(self.infer_taxonomy(user_query, session_context, user_context))
                taxonomy = await taxonomy_task
                logging.info("taxonomy: %s", taxonomy)

        query_understanding = QueryUnderstanding(
            query_expanded=query_expanded,  
            taxonomy=taxonomy,  
            session_context=session_context,  
            user_context=user_context, 
            embedding_vector=embedding_vector
        )

        return query_understanding
