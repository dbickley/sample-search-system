from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any

@dataclass
class Facets:
    facets: Dict[str, List[str]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
