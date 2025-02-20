from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List
@dataclass
class UserContext:
    user_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)