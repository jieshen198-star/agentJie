from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .tasks import ProjectSpec
from .tools import FileSystemTool, ReviewerTool, TaskPlannerTool, DeveloperTool, Tool


@dataclass
class LangGraphNode:
    id: str
    action: Callable[[dict[str, Any], dict[str, Tool]], dict[str, Any]]
    dependencies: list[str] = field(default_factory=list)

    def run(self, context: dict[str, Any], tools: dict[str, Tool]) -> dict[str, Any]:
        return self.action(context, tools)


class LangGraphEngine:
    def __init__(self, nodes: list[LangGraphNode], tools: list[Tool]):
        self.nodes = nodes
        self.tools = {tool.name: tool for tool in tools}

    def run(self, initial_context: dict[str, Any]) -> dict[str, Any]:
        context = dict(initial_context)
        for node in self.nodes:
            result = node.run(context, self.tools)
            context.update(result)
        return context


class LangGraphCoordinator:
    def __init__(self, project_spec: ProjectSpec):
        self.project_spec = project_spec
        self.tools = [
            TaskPlannerTool(),
            DeveloperTool(),
            ReviewerTool(),
            FileSystemTool(output_dir=project_spec.output_dir),
        ]
        self.nodes = self._build_graph()

    def _build_graph(self) -> list[LangGraphNode]:
        return [
            LangGraphNode(
                id="plan",
                action=self._plan_node,
            ),
            LangGraphNode(
                id="develop",
                action=self._develop_node,
                dependencies=["plan"],
            ),
            LangGraphNode(
                id="review",
                action=self._review_node,
                dependencies=["develop"],
            ),
            LangGraphNode(
                id="persist",
                action=self._persist_node,
                dependencies=["review"],
            ),
        ]

    def _plan_node(self, context: dict[str, Any], tools: dict[str, Tool]) -> dict[str, Any]:
        return tools["TaskPlanner"].execute({"project_spec": self.project_spec})

    def _develop_node(self, context: dict[str, Any], tools: dict[str, Tool]) -> dict[str, Any]:
        return tools["Developer"].execute({"tasks": context["tasks"]})

    def _review_node(self, context: dict[str, Any], tools: dict[str, Tool]) -> dict[str, Any]:
        return tools["Reviewer"].execute({"tasks": context["tasks"]})

    def _persist_node(self, context: dict[str, Any], tools: dict[str, Tool]) -> dict[str, Any]:
        return tools["FileSystem"].execute({"tasks": context["tasks"]})

    def execute(self) -> dict[str, Any]:
        initial_context: dict[str, Any] = {"project_spec": self.project_spec}
        return LangGraphEngine(nodes=self.nodes, tools=self.tools).run(initial_context)
