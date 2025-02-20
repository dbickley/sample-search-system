import logging
import joblib

# Configure logging (if not already done)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class QueryToTaxonomyService:  # Renamed class
    def __init__(self):
        try:
            model_path = "src/ml_models/query_to_taxonomy_model.pkl" 
            self.model = joblib.load(model_path)
            logging.info(f"Successfully loaded model from {model_path}")
        except Exception as e:
            logging.error(f"Error initializing QueryToTaxonomyService: {e}")
            self.model = None  # Set model to None if loading fails

    def predict_category(self, query):
        if self.model is None:
            logging.error("Model not loaded. Cannot make predictions.")
            return None

        try:
            prediction = self.model.predict([query])[0]
            return prediction
        except Exception as e:
            logging.error(f"Error making prediction: {e}")
            return None
