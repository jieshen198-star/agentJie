from agentjie.agent import MockAgent
from agentjie.coordinator import MultiAgentCoordinator
from agentjie.tasks import ProjectSpec


def test_coordinator_run(tmp_path):
    spec = ProjectSpec(
        name="测试系统",
        description="测试多agent流程",
        features=["初始化文档", "核心模块"],
        output_dir=str(tmp_path / "generated"),
    )
    agents = [
        MockAgent(name="Planner", role="planner", expertise="项目规划"),
        MockAgent(name="Developer", role="developer", expertise="代码编写"),
        MockAgent(name="Reviewer", role="reviewer", expertise="审查"),
    ]
    coordinator = MultiAgentCoordinator(agents=agents, project_spec=spec)
    tasks = coordinator.plan()
    assert len(tasks) == 2
    executed = coordinator.execute()
    assert all(task.status in {"DONE", "BLOCKED"} for task in executed)
    written = coordinator.deliver()
    assert len(written) == 2
