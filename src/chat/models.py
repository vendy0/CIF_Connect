from dataclasses import dataclass, field
from typing import Optional, Union
from datetime import datetime, date, time

# =============================================================================
# 1. MODÈLES DE DONNÉES
# =============================================================================


@dataclass
class Message:
    id: Union[int, str]
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
    pending: bool = False # <-- Indique si le message est en attente
    temp_id: Optional[str] = None # <-- ID temporaire pour le retrouver
