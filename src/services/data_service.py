import json
import os
from dataclasses import dataclass, asdict
from typing import Type, TypeVar, Generic


# Data classes included here for simplification
@dataclass
class UserContext:
    username: str = ""
    preferences: dict = None

    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {}


@dataclass
class SessionContext:
    session_id: str = ""
    is_active: bool = False
    last_access: str = ""


@dataclass
class SearchRatings:
    id: str = ""
    rating: bool = False
    date: str = ""


# Generic type for data models
T = TypeVar("T")
class DataService(Generic[T]):
    def __init__(self, file_path: str, data_type: Type[T]):
        self.file_path = file_path
        self.data_type = data_type
        self.data = self.load_data()

    def load_data(self) -> T:
        """Load data from JSON file or return default instance."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r",encoding="utf-8") as f:
                    raw_data = json.load(f)
                    return self.data_type(**raw_data)
            except (json.JSONDecodeError, TypeError):
                print(f"Error reading {self.file_path}. Using default values.")
        return self.data_type()

    def save_data(self):
        """Save current data to JSON file."""
        with open(self.file_path, "w",encoding="utf-8") as f:
            json.dump(asdict(self.data), f, indent=4)

    def update(self, **kwargs):
        """Update data fields dynamically and save."""
        for key, value in kwargs.items():
            if hasattr(self.data, key):
                setattr(self.data, key, value)
        self.save_data()
