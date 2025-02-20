import logging
from services.query_understanding_builder import QueryUnderstandingBuilder
from services.elastic_service import ElasticService
from services.rerank_service import RerankService
from services.query_builder import QueryBuilder
import numpy as np

logging.basicConfig(level=logging.INFO)
logging.getLogger('werkzeug').setLevel(logging.WARNING)

class SearchOrchestratorService:
    def __init__(self):
        self.query_understanding_builder = QueryUnderstandingBuilder()
        self.elastic_service = ElasticService()
        self.rerank_service = RerankService()
        self.query_builder = QueryBuilder()


    async def search(self, user_query):
        if(user_query.search_stratagy_verions == 'v1'):
            query_understanding = await self.query_understanding_builder.build(user_query)      
            if isinstance(query_understanding.embedding_vector, np.ndarray):  # Check if it's a NumPy array
                logging.info("Embedding vector is a NumPy array.")
            query =  self.query_builder.build_query(user_query,query_understanding)
            search_result = await self.elastic_service.search(query)
            if(user_query.re_rank):
                search_result = await self.rerank_service.rank_results(search_result, query_understanding)
            
            #for debugging
            search_result.query_understanding = query_understanding
            search_result.es_query = query

            return search_result
        else:
            raise Exception ("Invalid search strategy version")  # pylint: disable=W0719