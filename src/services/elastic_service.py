from elasticsearch import Elasticsearch
import logging
from models.search_result import SearchResult
from models.search_result_row import SearchResultRow
from settings import ES_HOST, ES_PORT, ES_INDEX, ES_AUTH

class ElasticService:
    def __init__(self):
        self.es = Elasticsearch(hosts=[f'http://{ES_HOST}:{ES_PORT}'], basic_auth=(ES_AUTH['username'],ES_AUTH['password']), request_timeout=600)
        self.index_name = ES_INDEX

    async def get_terms_for_field(self, field_name, size=100):
        try:
            agg = {
                "terms": {
                    "field": field_name,
                    "size": size
                }
            }
            response = self.es.search(index=self.index_name, aggregations={field_name: agg}, size=0)
            terms = [bucket["key"] for bucket in response["aggregations"][field_name]["buckets"]]
            return terms
        except Exception as e: # pylint: disable=W0703
            logging.error("Error getting terms for field %s: %s", field_name, e)  # Lazy formatting
            return []

    async def search(self, query: str):
            logging.info("Query: %s", query)  # Lazy formatting
            es_response = self.es.search(index=self.index_name, body=query)
            logging.info("Query success: hits: %s", es_response["hits"]["total"]["value"])  # Lazy formatting
            search_result = self.convert_es_response_to_search_result(query['from'], es_response)
            return search_result

    def convert_es_response_to_search_result(self, start_index, es_response):
        hits = es_response['hits']['hits']
        total_hits = es_response['hits']['total']['value'] 

        counter = start_index
        search_result_rows = []
        for hit in hits:
            search_result_row = SearchResultRow(
                product_id=hit['_id'],
                title=hit['_source']['name'],
                main_category=hit['_source']['main_category'],
                sub_category=hit['_source']['sub_category'],
                image_url=hit['_source']['image'],
                product_url=hit['_source']['link'],
                ratings=hit['_source']['ratings'],
                no_of_ratings=hit['_source']['no_of_ratings'],
                discount_price=hit['_source']['discount_price'],
                actual_price=hit['_source']['actual_price'],
                orginal_rank=counter,
                score=hit['_score']
            )
            counter += 1


            search_result_rows.append(search_result_row)
        
        search_result = SearchResult(number_of_results=total_hits, search_result_rows=search_result_rows)  # Important change

        return search_result