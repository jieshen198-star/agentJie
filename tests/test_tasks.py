from agentjie.tasks import ProjectSpec, Task, TaskStatus


def test_task_model():
    spec = ProjectSpec(
        name="测试项目",
        description="演示测试",
        features=["功能1", "功能2"],
    )
    assert spec.name == "测试项目"
    task = Task(
        id="T1",
        title="功能1",
        description="实现功能1",
        assignee="developer",
    )
    assert task.status == TaskStatus.TODO
    assert task.assignee == "developer"
