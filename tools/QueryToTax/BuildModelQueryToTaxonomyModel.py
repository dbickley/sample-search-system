import logging
import json
from elasticsearch import Elasticsearch
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline
import joblib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class QueryToTaxonomyModel:
    def __init__(self):
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer()),
            ('classifier', LogisticRegression(max_iter=1000))
        ])

    def train(self, data):
        """Trains the model on the provided data."""
        titles = data['name'].astype(str)
        categories = data['main_category'].astype(str)

        X_train, X_test, y_train, y_test = train_test_split(titles, categories, test_size=0.2, random_state=42)

        self.pipeline.fit(X_train, y_train)

        y_pred = self.pipeline.predict(X_test)
        print(classification_report(y_test, y_pred))

    def predict(self, query):
        """Predicts the main category for a given query."""
        prediction = self.pipeline.predict([query])[0]
        return prediction

    def save_model(self, filepath):
        joblib.dump(self.pipeline, filepath)

    def load_model(self, filepath):
        self.pipeline = joblib.load(filepath)

def train_model_in_batches(es, index_name, scroll_size=1000, scroll_timeout='1m'):
    """Trains the model in batches using the Scroll API."""

    model = QueryToTaxonomyModel()
    all_data = pd.DataFrame()

    try:
        # 1. Initialize Scroll
        search_response = es.search(index=index_name, body={"query": {"match_all": {}}}, scroll=scroll_timeout, size=scroll_size)
        scroll_id = search_response['_scroll_id']

        while True:
            hits = search_response['hits']['hits']
            if not hits:  # No more data
                break

            batch_data = pd.DataFrame([hit['_source'] for hit in hits])
            all_data = pd.concat([all_data, batch_data], ignore_index=True)

            # 2. Get next batch using Scroll ID
            search_response = es.scroll(scroll_id=scroll_id, scroll=scroll_timeout)
            scroll_id = search_response['_scroll_id']  # Update scroll ID

    except Exception as e:
        logging.error(f"An error occurred during scrolling: {e}")
        return None

    if all_data.empty:
        logging.error("No data retrieved from Elasticsearch. Cannot train the model.")
        return None

    logging.info("Starting model training on accumulated data.")
    model.train(all_data)
    return model

# Example usage:
try:
    es = Elasticsearch(hosts=[f'http://localhost:9200'], basic_auth=('elastic','password'), request_timeout=600)
    if not es.ping():
        raise ConnectionError("Failed to connect to Elasticsearch")

    trained_model = train_model_in_batches(es, "products")

    if trained_model:
        try:
            trained_model.save_model("src/ml_models/query_to_taxonomy_model.pkl")
            logging.info("Model training and saving complete.")
        except Exception as e:
            logging.exception("Error saving model:")  # Log the full traceback
            logging.error(f"Model saving failed: {e}")
    else:
        logging.error("Model training failed.")

except Exception as e:
    logging.error(f"An error occurred: {e}")

finally:
    if 'es' in locals():
        es.close()