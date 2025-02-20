from dataclasses import dataclass, asdict
from typing import  Optional, Dict, Any

@dataclass
class SearchResultRow:
    product_id: str
    title: str
    main_category: str
    sub_category: str
    image_url: str
    product_url: str
    ratings: str  # Or float if you want to convert
    no_of_ratings: str # Or int if you want to convert
    discount_price: str
    actual_price: str
    orginal_rank: Optional[int] = None # Optional and should be int
    re_rank: Optional[int] = None # Optional and should be int
    score: Optional[float] = None # Should be float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
