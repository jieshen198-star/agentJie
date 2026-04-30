from __future__ import annotations

from typing import Any

from .agent import BaseAgent
from .tasks import ProjectSpec, Task

try:
    import openai
except ImportError:  # pragma: no cover
    openai = None


class LLMAgent(BaseAgent):
    def __init__(self, name: str, role: str, expertise: str, api_key: str | None = None):
        super().__init__(name, role, expertise)
        if openai is None:
            raise RuntimeError("OpenAI SDK is not installed. Install agentjie[openai] to use LLMAgent.")
        if api_key:
            openai.api_key = api_key

    def act(self, subject: Any, context: dict[str, Any]) -> Any:
        prompt = self._build_prompt(subject, context)
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=900,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()

    def _build_prompt(self, subject: Any, context: dict[str, Any]) -> str:
        if self.role == "planner" and isinstance(subject, ProjectSpec):
            return (
                f"你是一个项目规划者，负责将项目描述拆成多个开发任务。\n"
                f"项目名称：{subject.name}\n"
                f"项目说明：{subject.description}\n"
                f"功能要求：{'；'.join(subject.features)}\n"
                "请输出一个 JSON 数组，其中每项包含 id、title、description、assignee 和 filename。"
            )
        if self.role == "developer" and isinstance(subject, Task):
            return (
                f"你是开发者，需要为以下任务生成代码文件。\n"
                f"任务标题：{subject.title}\n"
                f"任务说明：{subject.description}\n"
                f"请生成文本输出，开头包含 'FILE: {subject.filename}'，之后附上完整文件内容。"
            )
        if self.role == "reviewer" and isinstance(subject, Task):
            return (
                f"你是审查者，请阅读下面的任务输出并给出审核意见。\n"
                f"任务标题：{subject.title}\n"
                f"文件名：{subject.filename}\n"
                f"输出内容：\n{subject.output}\n"
                "如发现问题，请给出修改建议，否则直接回复通过。"
            )
        raise ValueError(f"LLMAgent 无法处理 subject 类型 {type(subject)}")
