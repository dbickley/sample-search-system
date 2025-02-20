from sentence_transformers import SentenceTransformer
import re
import logging
import numpy as np 

# Configure logging (optional, but recommended)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EmbeddingService:
    def __init__(self, model_name='all-MiniLM-L6-v2'):  # Default model
        try:
            self.model = SentenceTransformer(model_name)
        except Exception as e: # pylint: disable=W0703
            logging.exception("Error initializing EmbeddingService: %s", e)
            self.model = None

    def preprocess_title(self, title):
        if not title:  
            return ""

        title = title.lower()
        title = re.sub(r'[^\w\s]', '', title)  # Remove punctuation and special characters
        return title

    async def get_embedding(self, text):
        if self.model is None:
            logging.error("Model not loaded. Cannot generate embeddings.")
            return None

        try:
            preprocessed_text = self.preprocess_title(text)

            if not preprocessed_text:  
                logging.warning("Preprocessed text is empty for input: %s", text)
                return None  # Return None if preprocessed text is empty

            embedding = self.model.encode(preprocessed_text)

            if embedding is None or not isinstance(embedding, np.ndarray) or embedding.size == 0: 
                logging.warning("Generated embedding is invalid for input: %s", text)
                return None

            # Normalize the embedding
            norm = np.linalg.norm(embedding)
            if not np.isclose(norm, 1.0):
                embedding = embedding / norm

            return embedding.tolist()
        except Exception: # pylint: disable=W0703
            logging.exception("Error generating embedding for text: %s", text)
            return None