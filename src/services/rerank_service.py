from models.search_result import SearchResult
from models.query_understanding import QueryUnderstanding

class RerankService:
    def __init__(self):
        pass

    async def rank_results(self, search_result, query_understanding):  # pylint: disable=W0613
        return search_result