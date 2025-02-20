import asyncio
import json
import logging
from quart import Quart, jsonify, request, send_file,send_from_directory
from dataclasses import dataclass, asdict
from services.search_orchestrator_service import SearchOrchestratorService
from services.index_service import IndexService
from models.user_query import UserQuery
from models.search_config import SearchConfig

logging.basicConfig(level=logging.INFO)
logging.getLogger('quart.serving').setLevel(logging.WARNING)



class SampleSearchSystemApp:
    def __init__(self):
        self.app = Quart(__name__,static_folder="static",static_url_path="/")
        
        self.search_orchestrator_service = SearchOrchestratorService()
        self.index_service = IndexService()

    def register_routes(self):
        @self.app.route('/api/categories')  # New route for categories
        async def categories():
            return #TODO

        @self.app.route('/api/search', methods=['POST'])
        async def search():
            #commenting out try/catch for debugging
            #TODO add back try/catch
            #try:
            logging.info("Received search request")

            # Parse the JSON data into a UserQuery object
            data = await request.get_json()
            user_query = UserQuery(**data)
            if user_query.search_config is not None and isinstance(user_query.search_config, dict):
                user_query.search_config = SearchConfig.from_dict(user_query.search_config)


            #testing
            logging.info("user_query.search_config.fields_to_match: %s", user_query.search_config.fields_to_match)
            logging.info("query: %s", json.dumps(asdict(user_query)))

            logging.info("Sending request to search service")
            search_results = await self.search_orchestrator_service.search(user_query)  # Await the async call
            logging.info("Search request completed")
            return jsonify(search_results), 200
            # except Exception as e:
            #     logging.error("Error processing search request: %s", str(e))
            #     return jsonify({'error': str(e)}), 500

        @self.app.route('/api/reindex', methods=['POST'])
        async def reindex():
            try:
                logging.info("Received reindex request")
                asyncio.create_task(self.index_service.reindex())  # Async execution
                logging.info("Reindex started")
                return jsonify({'success': True}), 200
            except Exception as e:
                logging.error("Error processing reindex request: %s", str(e))
                return jsonify({'error': str(e)}), 500
            
        @self.app.route('/api/update_embeddings', methods=['POST'])
        async def update_embeddings():
            try:
                logging.info("Received update_embeddings request")
                asyncio.create_task(self.index_service.udpate_embeddings_all())  # Async execution
                logging.info("update_embeddings started")
                return jsonify({'success': True}), 200
            except Exception as e:
                logging.error("Error processing update_embeddings request: %s", str(e))
                return jsonify({'error': str(e)}), 500

        @self.app.route('/')
        async def index():
            return await send_from_directory(self.app.static_folder, "index.html")
        


    def run(self):
        self.app.run(debug=True)

async def main():
    app = SampleSearchSystemApp()
    app.register_routes()
    await app.app.run_task()  # Use Quart's async run

if __name__ == '__main__':
    asyncio.run(main(), debug=True)
