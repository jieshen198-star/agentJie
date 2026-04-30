from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .tasks import ProjectSpec, Task


class BaseAgent(ABC):
    def __init__(self, name: str, role: str, expertise: str):
        self.name = name
        self.role = role
        self.expertise = expertise

    @abstractmethod
    def act(self, subject: Any, context: dict[str, Any]) -> Any:
        ...


class MockAgent(BaseAgent):
    def act(self, subject: Any, context: dict[str, Any]) -> Any:
        if self.role == "planner" and isinstance(subject, ProjectSpec):
            return self._plan_project(subject)
        if self.role == "developer" and isinstance(subject, Task):
            return self._develop_task(subject, context)
        if self.role == "reviewer" and isinstance(subject, Task):
            return self._review_task(subject, context)
        raise ValueError(f"MockAgent cannot handle subject type {type(subject)}")

    def _plan_project(self, spec: ProjectSpec) -> list[Task]:
        tasks: list[Task] = []
        for index, feature in enumerate(spec.features, start=1):
            task = Task(
                id=f"T{index}",
                title=f"实现：{feature}",
                description=f"为项目 '{spec.name}' 实现以下功能：{feature}",
                assignee="developer",
                filename=self._feature_to_file(feature),
            )
            tasks.append(task)
        return tasks

    def _develop_task(self, task: Task, context: dict[str, Any]) -> str:
        code_block = f"# {task.title}\n# 描述：{task.description}\n\n"
        if "README" in task.filename.upper() or task.filename.endswith(".md"):
            code_block += f"# {task.title}\n\n" + task.description + "\n"
        else:
            module_name = task.filename.replace(".py", "")
            code_block += f"def {module_name.replace('-', '_')}_main():\n    '''{task.description}'''\n    print(\"{task.title} 已执行\")\n\n\nif __name__ == '__main__':\n    {module_name.replace('-', '_')}_main()\n"
        return f"FILE: {task.filename}\n{code_block}"

    def _review_task(self, task: Task, context: dict[str, Any]) -> str:
        if "print(" in task.output or "def " in task.output:
            return "通过：代码结构合理，符合任务描述。"
        return "修订建议：请补充实际功能实现与文件注释。"

    def _feature_to_file(self, feature: str) -> str:
        normalized = feature.lower().replace(" ", "_").replace("/", "_")
        if any(ext in normalized for ext in ["file", "readme", "doc"]):
            return f"{normalized}.md"
        return f"{normalized}.py"
