from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List
from models.search_result_row import SearchResultRow
from models.query_understanding import QueryUnderstanding
from models.facets import Facets

@dataclass
class SearchResult:
    number_of_results: int
    search_result_rows: List[SearchResultRow] = field(default_factory=list)
    facets: Optional[Facets] = None
    query_understanding: Optional[QueryUnderstanding] = None
    es_query: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
