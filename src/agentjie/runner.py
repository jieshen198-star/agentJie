from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from .agent import MockAgent
from .coordinator import MultiAgentCoordinator
from .langgraph import LangGraphCoordinator
from .tasks import ProjectSpec

app = typer.Typer()
console = Console()


@app.command()
def run(
    goal: str = typer.Option(
        "构建一个多agent协同开发自动化系统",
        help="要实现的项目目标",
    ),
    output_dir: str = typer.Option("generated", help="生成文件的输出目录"),
    use_langgraph: bool = typer.Option(
        False,
        help="启用 LangGraph 图工作流与工具调用",
    ),
):
    spec = ProjectSpec(
        name="agentJie Demo",
        description=goal,
        features=[
            "项目说明文档",
            "协同开发框架核心模块",
            "多代理执行与审查流程",
        ],
        output_dir=output_dir,
    )

    if use_langgraph:
        coordinator = LangGraphCoordinator(project_spec=spec)
        result = coordinator.execute()
        written = result.get("written_files", [])
    else:
        agents = [
            MockAgent(name="Planner", role="planner", expertise="项目规划"),
            MockAgent(name="Developer", role="developer", expertise="代码编写"),
            MockAgent(name="Reviewer", role="reviewer", expertise="审查与质量控制"),
        ]
        coordinator = MultiAgentCoordinator(agents=agents, project_spec=spec)
        coordinator.plan()
        coordinator.execute()
        written = coordinator.deliver()

    console.print("[bold green]任务执行完成[/bold green]")
    console.print("写入文件：")
    for path in written:
        console.print(f"  - {path}")


@app.command()
def demo(use_langgraph: bool = typer.Option(False, help="启用 LangGraph 流程")):
    """运行演示流程并生成默认输出。"""
    run(use_langgraph=use_langgraph)


if __name__ == "__main__":
    app()
