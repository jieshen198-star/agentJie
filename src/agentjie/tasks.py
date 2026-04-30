from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class TaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    REVIEW = "REVIEW"
    DONE = "DONE"
    BLOCKED = "BLOCKED"


@dataclass
class Task:
    id: str
    title: str
    description: str
    assignee: str
    status: TaskStatus = TaskStatus.TODO
    output: str = ""
    review_notes: str = ""
    filename: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ProjectSpec:
    name: str
    description: str
    features: List[str]
    output_dir: str = "generated"
