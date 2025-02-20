import unittest
import json
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from src.models.query_understanding import QueryUnderstanding  # Correct import


class TestQueryUnderstanding(unittest.TestCase):

    def test_to_dict_and_json_serializable(self):
        # Create sample data (replace with realistic data for your use case)
        query_expanded = "expanded query"
        taxonomy = {"category": "electronics"}
        session_context = {"session_id": "123"}
        user_context = {"user_id": "456"}
        embedding_vector = [0.1, 0.2, 0.3]


        query_understanding = QueryUnderstanding(
            query_expanded=query_expanded,
            taxonomy=taxonomy,
            session_context=session_context,
            user_context=user_context,
            embedding_vector=embedding_vector
        )

        # Test to_dict()
        query_understanding_dict = query_understanding.to_dict()
        self.assertEqual(query_understanding_dict["query_expanded"], query_expanded)
        self.assertEqual(query_understanding_dict["taxonomy"], taxonomy)
        self.assertEqual(query_understanding_dict["session_context"], session_context)
        self.assertEqual(query_understanding_dict["user_context"], user_context)
        self.assertEqual(query_understanding_dict["embedding_vector"], embedding_vector)


        # Test JSON serialization
        try:
            json_string = json.dumps(query_understanding_dict)
            # Optionally, you can also decode it back to a dictionary and compare:
            loaded_dict = json.loads(json_string)
            self.assertEqual(loaded_dict, query_understanding_dict) # Compare the loaded dict to the original
        except TypeError as e:
            self.fail(f"JSON serialization failed: {e}")
        except Exception as e: # Catch any other exception during json.dumps()
            self.fail(f"JSON serialization failed: {e}")

    def test_empty_values(self):
         # Test with None or empty values
        query_understanding = QueryUnderstanding(
            query_expanded=None,
            taxonomy=None,
            session_context=None,
            user_context=None,
            embedding_vector=None
        )

        query_understanding_dict = query_understanding.to_dict()
        try:
            json_string = json.dumps(query_understanding_dict)
            loaded_dict = json.loads(json_string)
            self.assertEqual(loaded_dict, query_understanding_dict)
        except TypeError as e:
            self.fail(f"JSON serialization failed: {e}")
        except Exception as e: # Catch any other exception during json.dumps()
            self.fail(f"JSON serialization failed: {e}")


if __name__ == '__main__':
    unittest.main()