from __future__ import annotations

import json
import os
from typing import Iterable

from .agent import BaseAgent
from .project import ProjectWriter
from .tasks import ProjectSpec, Task, TaskStatus


class MultiAgentCoordinator:
    def __init__(self, agents: Iterable[BaseAgent], project_spec: ProjectSpec):
        self.agents = list(agents)
        self.project_spec = project_spec
        self.tasks: list[Task] = []
        self.logger: list[str] = []

    def find_agent(self, role: str) -> BaseAgent:
        for agent in self.agents:
            if agent.role == role:
                return agent
        raise ValueError(f"未找到角色为 '{role}' 的代理")

    def plan(self) -> list[Task]:
        self.logger.append("[Coordinator] 开始项目规划")
        planner = self.find_agent("planner")
        result = planner.act(self.project_spec, self._build_context())
        if isinstance(result, list):
            self.tasks = result
        else:
            self.tasks = self._parse_planner_text(result)
        self.logger.append(f"[Coordinator] 规划完成，生成 {len(self.tasks)} 个任务")
        return self.tasks

    def execute(self) -> list[Task]:
        if not self.tasks:
            self.plan()
        developer = self.find_agent("developer")
        reviewer = self.find_agent("reviewer")
        for task in self.tasks:
            self.logger.append(f"[Coordinator] 执行任务 {task.id} -> {task.title}")
            task.status = TaskStatus.IN_PROGRESS
            task.output = developer.act(task, self._build_context())
            task.status = TaskStatus.REVIEW
            review_result = reviewer.act(task, self._build_context())
            task.review_notes = review_result
            if "通过" in review_result or "approve" in review_result.lower():
                task.status = TaskStatus.DONE
                self.logger.append(f"[Coordinator] 任务 {task.id} 审查通过")
            else:
                task.status = TaskStatus.BLOCKED
                self.logger.append(f"[Coordinator] 任务 {task.id} 需要修订：{review_result}")
        return self.tasks

    def deliver(self) -> list[str]:
        writer = ProjectWriter(self.project_spec.output_dir)
        self.logger.append(f"[Coordinator] 写入结果到 {self.project_spec.output_dir}")
        written_files: list[str] = []
        for task in self.tasks:
            if task.output:
                file_name = writer.write_task_output(task)
                written_files.append(file_name)
                self.logger.append(f"[Coordinator] 已写入 {file_name}")
        return written_files

    def _build_context(self) -> dict[str, str]:
        return {
            "project_name": self.project_spec.name,
            "project_description": self.project_spec.description,
            "task_count": str(len(self.tasks)),
        }

    def _parse_planner_text(self, text: str) -> list[Task]:
        try:
            data = json.loads(text)
            tasks: list[Task] = []
            for item in data:
                task = Task(
                    id=item["id"],
                    title=item["title"],
                    description=item["description"],
                    assignee=item.get("assignee", "developer"),
                    filename=item.get("filename", f"task_{item['id']}.py"),
                )
                tasks.append(task)
            return tasks
        except Exception as exc:
            raise ValueError("无法解析规划器输出为任务列表") from exc
