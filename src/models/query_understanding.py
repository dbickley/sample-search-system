from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List
@dataclass
class QueryUnderstanding:
    query_expanded: Optional[str] = None # Optional fields should have a default value
    taxonomy: Optional[Dict[str, Any]] = None
    session_context: Optional[Dict[str, Any]] = None
    user_context: Optional[Dict[str, Any]] = None
    embedding_vector: Optional[List[float]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def __repr__(self):
        return (f"QueryUnderstanding("
                f"query_expanded={self.query_expanded}, "
                f"taxonomy={self.taxonomy}, "
                f"session_context={self.session_context}, "
                f"user_context={self.user_context}, "
                f"embedding_vector={self.embedding_vector})")