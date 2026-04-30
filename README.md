# agentJie

agentJie 是一个用于多 agent 协同开发的自动化系统框架。它提供任务拆分、代码编写、审查与交付的协作流程，支持本地模拟以及可扩展的 LLM 代理。

## 特性

- 多角色协作：规划者、开发者、审查者
- 自动任务拆分与分配
- 代码输出管理与文件写入
- 可扩展 LLM 代理接口
- CLI 运行支持

## 安装

```bash
python -m pip install -U pip
python -m pip install .
```

可选安装 OpenAI 支持：

```bash
python -m pip install .[openai]
```

## 快速开始

```bash
agentjie demo
```

或者：

```bash
python -m agentjie.demo
```

## 目录结构

- `src/agentjie/` 核心包
- `examples/` 示例脚本
- `tests/` 单元测试

## 使用说明

创建一个多 agent 协同流程：

```bash
agentjie run --goal "构建一个多 agent 协同开发系统" --output-dir generated
```

如果你想启用图工作流与工具调用，可以使用 LangGraph 模式：

```bash
agentjie run --goal "构建一个多 agent 协同开发系统" --output-dir generated --use-langgraph
```

系统将使用默认模拟代理执行规划、开发与审查，并将结果写入 `generated/`。在 LangGraph 模式下，流程通过节点图和工具调用来执行任务。
