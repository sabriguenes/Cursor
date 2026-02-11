# Research Resources - LLVM/Clang Knowledge Mining & Code Review Agent

> **Curated resources for Agent Orchestration, RAG Systems, Multi-Agent Collaboration, and Code Review Patterns**

---

## 🎯 Priority 1: Agent Orchestration Patterns

These are **directly applicable** to Will Pak's requirements for the orchestration layer.

### LangGraph - Multi-Agent Systems

| Resource | Description | Link |
|----------|-------------|------|
| **Multi-Agent Supervisor** | Supervisor agent orchestrates specialized sub-agents, manages task delegation | [Notebook](https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/multi_agent/agent_supervisor.ipynb) |
| **Hierarchical Agent Teams** | Top-level supervisor delegates to sub-agents with clear task hierarchy | [Notebook](https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/multi_agent/hierarchical_agent_teams.ipynb) |
| **Multi-Agent Collaboration** | Multiple specialized agents working together on complex tasks | [Notebook](https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/multi_agent/multi-agent-collaboration.ipynb) |
| **Plan-and-Execute Agent** | Generates multi-step plan, executes sequentially, revises as needed | [Notebook](https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/plan-and-execute/plan-and-execute.ipynb) |

### AutoGen - Multi-Agent Patterns

| Resource | Description | Link |
|----------|-------------|------|
| **Group Chat (3+ agents, 1 manager)** | Task-solving via multi-agent collaboration with manager | [Notebook](https://microsoft.github.io/autogen/0.2/docs/notebooks/agentchat_groupchat) |
| **Complex Task Solving (6 agents)** | Larger group collaboration for complex problems | [Notebook](https://microsoft.github.io/autogen/0.2/docs/notebooks/agentchat_groupchat_research) |
| **Coding & Planning Agents** | Combines coding and planning agents effectively | [Notebook](https://github.com/microsoft/autogen/blob/0.2/notebook/agentchat_planning.ipynb) |
| **Custom Speaker Selection** | Custom function for speaker selection in group chats | [Notebook](https://microsoft.github.io/autogen/0.2/docs/notebooks/agentchat_groupchat_customized) |

### CrewAI + LangGraph

| Resource | Description | Link |
|----------|-------------|------|
| **CrewAI + LangGraph Integration** | Demonstrates integration between frameworks | [GitHub](https://github.com/crewAIInc/crewAI-examples/tree/main/integrations/CrewAI-LangGraph) |

---

## 🎯 Priority 2: RAG Systems (Knowledge Base)

For querying the C++ Alliance's Pinecone vector database effectively.

### LangGraph Agentic RAG

| Resource | Description | Link |
|----------|-------------|------|
| **Agentic RAG** | Agent determines best retrieval strategy before response | [Notebook](https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/rag/langgraph_agentic_rag.ipynb) |
| **Adaptive RAG** | Dynamic retrieval based on query complexity | [Notebook](https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/rag/langgraph_adaptive_rag.ipynb) |
| **Corrective RAG (CRAG)** | Evaluates/refines retrieved docs before generation | [Notebook](https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/rag/langgraph_crag.ipynb) |
| **Self-RAG** | Reflects on responses, retrieves additional info if needed | [Notebook](https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/rag/langgraph_self_rag.ipynb) |

### AutoGen RAG

| Resource | Description | Link |
|----------|-------------|------|
| **RAG Group Chat** | Group chat with Retrieval Augmented Generation | [Notebook](https://microsoft.github.io/autogen/0.2/docs/notebooks/agentchat_groupchat_RAG) |
| **Retrieval Augmented Agents** | Code generation + Q&A with retrieval | [Notebook](https://microsoft.github.io/autogen/0.2/docs/notebooks/agentchat_RetrieveChat) |
| **Qdrant-based Retrieval** | Enhanced retrieval with Qdrant vector DB | [Notebook](https://microsoft.github.io/autogen/0.2/docs/notebooks/agentchat_RetrieveChat_qdrant) |

---

## 🎯 Priority 3: Code Review & Document Analysis

Patterns applicable to PR review and code analysis.

### Code Assistants

| Resource | Description | Link |
|----------|-------------|------|
| **LangGraph Code Assistant** | Graph-based agent for code generation, error checking, iterative refinement | [Notebook](https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/code_assistant/langgraph_code_assistant.ipynb) |
| **AutoGen Code Generation & Debugging** | Automated task-solving with code gen, execution, debugging | [Notebook](https://microsoft.github.io/autogen/0.2/docs/notebooks/agentchat_auto_feedback_from_code_execution) |

### Document Analysis (Similar Pattern to PR Reviews)

| Resource | Description | Link |
|----------|-------------|------|
| **Legal Document Review Assistant** | Automates document review, highlights key clauses | [GitHub](https://github.com/firica/legalai) |
| **Agno Legal Document Analysis** | Analyzes legal docs from PDFs, vector embeddings + GPT-4o | [GitHub](https://github.com/agno-agi/agno/blob/main/cookbook/examples/agents/legal_consultant.py) |

---

## 🎯 Priority 4: Reflection & Self-Improvement

For iterative quality improvement in code reviews.

| Resource | Description | Link |
|----------|-------------|------|
| **Reflection Agent** | Agent critiques and revises its own outputs | [Notebook](https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/reflection/reflection.ipynb) |
| **Reflexion Agent** | Reflects on actions/outcomes for iterative improvement | [Notebook](https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/reflexion/reflexion.ipynb) |
| **Self Evaluation Loop Flow** | CrewAI self-assessment process | [GitHub](https://github.com/crewAIInc/crewAI-examples/tree/main/flows/self_evaluation_loop_flow) |

---

## 🎯 Priority 5: GitHub Integration & Automation

For GitHub-based workflows.

| Resource | Description | Link |
|----------|-------------|------|
| **Claude Code Auto-Close Duplicates** | Workflow for auto-closing duplicate issues (UX pattern, not detection) | [GitHub](https://github.com/anthropics/claude-code/blob/main/.github/workflows/auto-close-duplicates.yml) |
| **Claude Code Duplicate Script** | TypeScript implementation of auto-close logic | [GitHub](https://github.com/anthropics/claude-code/blob/main/scripts/auto-close-duplicates.ts) |

---

## 🎯 Priority 6: Cost Optimization & Observability

For Opus 4.5 cost management.

| Resource | Description | Link |
|----------|-------------|------|
| **Cost Calculation** | Track token usage, estimate costs | [Notebook](https://github.com/microsoft/autogen/blob/0.2/notebook/agentchat_cost_token_tracking.ipynb) |
| **AgentOps Observability** | Monitor LLM calls, tool usage, errors | [Notebook](https://github.com/microsoft/autogen/blob/0.2/notebook/agentchat_agentops.ipynb) |
| **Optimize for Code Generation** | Cost-effective optimization techniques | [Notebook](https://github.com/microsoft/autogen/blob/0.2/notebook/oai_completion.ipynb) |

---

## 🎯 Priority 7: Supply Chain / Complex Optimization

Reference architecture for multi-agent problem solving.

| Resource | Description | Link |
|----------|-------------|------|
| **OptiGuide** | Coding + Tool Use + Safeguarding + Q&A for optimization problems | [GitHub](https://github.com/microsoft/OptiGuide) |
| **OptiGuide Notebook** | Nested chats, coding agent, safeguard agent | [Notebook](https://microsoft.github.io/autogen/0.2/docs/notebooks/agentchat_nestedchat_optiguide) |

---

## 📚 Full Repository Reference

- **500+ AI Agent Projects**: https://github.com/ashishpatel26/500-AI-Agents-Projects
- **LangGraph Tutorials**: https://github.com/langchain-ai/langgraph/tree/main/docs/docs/tutorials
- **AutoGen Notebooks**: https://microsoft.github.io/autogen/0.2/docs/notebooks
- **CrewAI Examples**: https://github.com/crewAIInc/crewAI-examples
- **Agno Cookbook**: https://github.com/agno-agi/agno/tree/main/cookbook/examples/agents

---

## 🔑 Key Takeaways for Our Project

### Agent Architecture (Based on Research)

```
┌─────────────────────────────────────────────────────────────┐
│                    SUPERVISOR AGENT                         │
│              (Orchestration Layer - Your Scope)             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Planning     │  │ Data         │  │ GitHub       │      │
│  │ Agent        │  │ Agent        │  │ Agent        │      │
│  │ (Strategy)   │  │ (Retrieval)  │  │ (PRs/Issues) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Code Review  │  │ Testing      │  │ Debugging    │      │
│  │ Agent        │  │ Agent        │  │ Agent        │      │
│  │ (Analysis)   │  │ (Validation) │  │ (Fixes)      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │   MCP Server (Pinecone) │
              │   C++ Knowledge Base    │
              └─────────────────────────┘
```

### Recommended Patterns to Study First

1. **LangGraph Multi-Agent Supervisor** - Core orchestration pattern
2. **Agentic RAG** - How to query knowledge base intelligently
3. **Reflection Agent** - Self-improvement for code review quality
4. **OptiGuide** - Reference for Coding + Safeguarding pattern

---

## 📅 Research Log

| Date | Topic | Notes |
|------|-------|-------|
| 2026-02-04 | Initial resource collection | Curated from 500-AI-Agents-Projects |
| | Claude Code auto-close workflow | Useful UX pattern (grace period, user feedback) but NOT duplicate detection |
| | Dependabot | NOT relevant - only for dependency updates |

---

*Last updated: 2026-02-04*
