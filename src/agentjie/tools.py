from __future__ import annotations

from pathlib import Path
from typing import Any

from .tasks import ProjectSpec, Task, TaskStatus


class Tool:
    name: str

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class TaskPlannerTool(Tool):
    name = "TaskPlanner"

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        spec: ProjectSpec = payload["project_spec"]
        tasks: list[Task] = []
        for index, feature in enumerate(spec.features, start=1):
            tasks.append(
                Task(
                    id=f"T{index}",
                    title=f"实现：{feature}",
                    description=f"为项目 '{spec.name}' 实现以下功能：{feature}",
                    assignee="developer",
                    filename=self._feature_to_file(feature),
                )
            )
        return {"tasks": tasks}

    def _feature_to_file(self, feature: str) -> str:
        normalized = feature.lower().replace(" ", "_").replace("/", "_")
        if any(ext in normalized for ext in ["file", "readme", "doc"]):
            return f"{normalized}.md"
        return f"{normalized}.py"


class DeveloperTool(Tool):
    name = "Developer"

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        tasks: list[Task] = payload["tasks"]
        for task in tasks:
            task.output = self._generate_code(task)
        return {"tasks": tasks}

    def _generate_code(self, task: Task) -> str:
        content = f"# {task.title}\n# 描述：{task.description}\n\n"
        if task.filename.endswith(".md"):
            content += f"# {task.title}\n\n{task.description}\n"
        else:
            name = task.filename.replace(".py", "").replace("-", "_")
            content += (
                f"def {name}_main():\n"
                f"    '''{task.description}'''\n"
                f"    print(\"{task.title} 已执行\")\n\n"
                f"if __name__ == '__main__':\n"
                f"    {name}_main()\n"
            )
        return f"FILE: {task.filename}\n{content}"


class ReviewerTool(Tool):
    name = "Reviewer"

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        tasks: list[Task] = payload["tasks"]
        for task in tasks:
            review = self._review_output(task.output)
            task.review_notes = review
            task.status = TaskStatus.DONE if "通过" in review or "approve" in review.lower() else TaskStatus.BLOCKED
        return {"tasks": tasks}

    def _review_output(self, output: str) -> str:
        if "def " in output or "print(" in output:
            return "通过：代码结构合理，符合任务描述。"
        return "修订建议：请补充实际功能实现与文件注释。"


class FileSystemTool(Tool):
    name = "FileSystem"

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        tasks: list[Task] = payload["tasks"]
        written: list[str] = []
        for task in tasks:
            filename = self._extract_filename(task.output) or task.filename or f"{task.id}.txt"
            content = self._extract_content(task.output) or task.output
            target = self.output_dir / filename
            target.write_text(content, encoding="utf-8")
            written.append(str(target))
        return {"written_files": written}

    def _extract_filename(self, output: str) -> str | None:
        for line in output.splitlines():
            if line.startswith("FILE:"):
                return line.split("FILE:", 1)[1].strip()
        return None

    def _extract_content(self, output: str) -> str:
        lines = output.splitlines()
        if lines and lines[0].startswith("FILE:"):
            return "\n".join(lines[1:]).lstrip("\n")
        return output
