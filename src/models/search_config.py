from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List

@dataclass
class SearchConfig:
    fields_to_match: List[str] = field(default_factory=lambda: ["name", "main_category", "sub_category"])
    keyword: Dict[str, Any] = field(default_factory=lambda: {
        "boost": 1.0,
        "match_types": {
            "phrase": 2.0,
            "phrase_prefix": 1.0,
            "fuzzy": 1.0,
            "best_fields": 1.0,
        },
        "predicted_category_boost": 1.2
    })
    vector: Dict[str, Any] = field(default_factory=lambda: {
        "k": 10,
        "num_candidates": 1000,
        "boost": 2,
        "enabled": True
    })
    combined_query_boost: float = 1.1
    facets: Dict[str, Any] = field(default_factory=lambda: {
        "main_category": {"boost": 1.0},
        "sub_category": {"boost": 1.0}
    })
    categories: Dict[str, Any] = field(default_factory=lambda: {
        "main_category": {"boost": 1.0},
        "sub_category": {"boost": 1.0}
    })
    fuzziness: Dict[str, Any] = field(default_factory=lambda: {"default": "AUTO"})

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchConfig":
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
