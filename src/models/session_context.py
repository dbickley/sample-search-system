from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List
@dataclass
class SessionContext:
    session_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)