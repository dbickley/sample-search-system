from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional
from models.search_config import SearchConfig

@dataclass
class UserQuery:
    query: str
    facets: Optional[Dict[str, Any]] = None
    main_category: Optional[str] = None
    sub_category: Optional[str] = None
    number_of_results: Optional[int] = 10
    start_index: Optional[int] = 0
    predict_taxonomy: Optional[bool] = None
    keyword_search: Optional[bool] = None
    vector_search: Optional[bool] = None
    re_rank: Optional[bool] = None
    search_stratagy_verions: Optional[str] = 'v1'
    search_config: SearchConfig = field(default_factory=SearchConfig)  # Directly use SearchConfig


    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)