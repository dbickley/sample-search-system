import logging
from elasticsearch import Elasticsearch

logging.basicConfig(level=logging.INFO)
logging.getLogger("quart.serving").setLevel(logging.WARNING)


class QueryBuilder:

    def _build_keyword_query(self, query, fields_to_match, predicted_category, keyword_search_enabled, search_config):
        if not query:
            return {"match_all": {}}

        keyword_queries = []
        if(keyword_search_enabled): 
            match_types = search_config.keyword.get("match_types", {}) 
            for match_type, boost in match_types.items():
                if match_type == "phrase":
                    keyword_queries.append({"multi_match": {"query": query, "fields": fields_to_match, "type": "phrase", "boost": boost}})
                elif match_type == "phrase_prefix":
                    keyword_queries.append({"multi_match": {"query": query, "fields": fields_to_match, "type": "phrase_prefix", "boost": boost}})
                elif match_type == "fuzzy":
                    fuzziness = search_config.fuzziness.get("default", "AUTO") 
                    keyword_queries.append({"multi_match": {"query": query, "fields": fields_to_match, "fuzziness": fuzziness, "boost": boost}})
                elif match_type == "best_fields":
                    keyword_queries.append({"multi_match": {"query": query, "fields": fields_to_match, "type": "best_fields", "boost": boost}})

        keyword_query = {"bool": {"should": keyword_queries, "minimum_should_match": 1}}

        predicted_category_boost = search_config.keyword.get("predicted_category_boost")
        if predicted_category and predicted_category_boost:
            keyword_query["bool"]["should"].append(
                {"bool": {"must": [{"match": {"main_category": predicted_category}}], "boost": predicted_category_boost}}
            )
        return keyword_query

    def _build_vector_query(self, embedding_vector, search_config):
        if not embedding_vector or not search_config.vector.get("enabled", False):
            return None

        logging.info("Vector search enabled")
        vector_query = {
            "knn": {
                "field": "name_embedding",
                "query_vector": embedding_vector, 
                "k": search_config.vector.get("k", 10),
                "num_candidates": search_config.vector.get("num_candidates", 1000)
            }
        }
        return {"bool": {"should": [vector_query], "boost": search_config.vector.get("boost", 0.8)}}

    def _build_facet_filter(self, facets, search_config):
        if not facets:
            return None

        must_clauses = []
        for field, values in facets.items():
            boost = search_config.facets.get(field, {}).get("boost", 1.0)
            if isinstance(values, list):
                must_clauses.append({"terms": {field: values, "boost": boost}})
            else:
                must_clauses.append({"term": {field: values, "boost": boost}})

        return {"bool": {"must": must_clauses}} if must_clauses else None

    def _build_category_filter(self, main_category, sub_category, search_config):
        category_queries = []
        if main_category:
            boost = search_config.categories.get("main_category", {}).get("boost", 1.0)
            category_queries.append({"match": {"main_category": main_category, "boost": boost}})
        if sub_category:
            boost = search_config.categories.get("sub_category", {}).get("boost", 1.0)
            category_queries.append({"match": {"sub_category": sub_category, "boost": boost}})

        return {"bool": {"should": category_queries, "minimum_should_match": 1}} if category_queries else None

    def build_query(self, user_query, understanding):
        search_config = user_query.search_config
        fields_to_match = search_config.fields_to_match 
        query = user_query.query
        facets = user_query.facets
        predicted_category = understanding.taxonomy
        keyword_search_enabled = user_query.keyword_search
        vector_search_enabled = user_query.vector_search
        if understanding.embedding_vector is not None and len(understanding.embedding_vector) > 0 and vector_search_enabled:
            embedding_vector = list(understanding.embedding_vector)
        else:
            embedding_vector = None
        main_category = user_query.main_category
        sub_category = user_query.sub_category

        query_body = {}

        keyword_query = self._build_keyword_query(query, fields_to_match, predicted_category, keyword_search_enabled, search_config)
        if keyword_query:
          query_body["query"] = keyword_query

        vector_query = self._build_vector_query(embedding_vector, search_config)
        if vector_query and "query" in query_body:
            query_body["query"] = {"bool": {"should": [query_body["query"], vector_query], "boost": search_config.combined_query_boost} }
        elif vector_query:
          query_body["query"] = vector_query

        filter_clauses = []

        facet_filter = self._build_facet_filter(facets, search_config)
        if facet_filter:
            filter_clauses.append(facet_filter)

        category_filter = self._build_category_filter(main_category, sub_category, search_config)
        if category_filter:
            filter_clauses.append(category_filter)
        
        if filter_clauses:
          query_body["filter"] = {"bool": {"must": filter_clauses}}

        query_body["from"] = user_query.start_index
        query_body["size"] = user_query.number_of_results

        return query_body