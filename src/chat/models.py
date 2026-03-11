from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime, date, time


@dataclass
class Message:
    id: int
    pseudo: str
    content: str
    message_type: str
    modified: bool
    message_datetime: datetime
    message_date: date
    message_time: time
    parent_id: Optional[int] = None
    parent_content: Optional[str] = None
    parent_author: Optional[str] = None
    reactions: dict = field(default_factory=dict)
