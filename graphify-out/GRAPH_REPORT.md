# Graph Report - mcp-local-llm  (2026-10-16)

## Corpus Check
- Corpus is ~2,366 words - fits in a single context window. You may not need a graph.

## Summary
- 42 nodes · 50 edges · 8 communities (5 shown, 3 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.85)
- Token cost: 1,250 input · 480 output

## Community Hubs (Navigation)
- Hardware & Inference Engine
- Ollama Client & Async Generation
- Configuration & Environment Setup
- MCP Server Tools & File Analysis
- Health Check & Status Telemetry
- Hybrid Intelligence Architecture
- Source Package Metadata
- Test Suite & Diagnostics

## God Nodes (most connected - your core abstractions)
1. `OllamaClient` - 7 edges
2. `ask_local_llm()` - 3 edges
3. `analyze_file_locally()` - 3 edges
4. `check_local_llm_status()` - 3 edges
5. `Antigravity Local LLM MCP Bridge` - 3 edges
6. `run_diagnostics()` - 2 edges
7. `Ollama Inference Engine` - 2 edges
8. `Antigravity Local LLM MCP Bridge package.` - 1 edges
9. `Check Ollama service status, version, and list installed models.` - 1 edges
10. `Send a prompt to Ollama and return the generated text response.` - 1 edges

## Surprising Connections (you probably didn't know these)
- `run_diagnostics()` --calls--> `OllamaClient`  [EXTRACTED]
  tests/test_connection.py → src/client.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **MCP Bridge Execution Triad** — architecture_plan_local_llm_mcp_bridge, src_server, architecture_plan_ollama_engine [EXTRACTED 0.95]

## Communities (8 total, 3 thin omitted)

### Community 0 - "Hardware & Inference Engine"
Cohesion: 0.22
Nodes (8): NVIDIA GeForce RTX 5060 GPU, Ollama Inference Engine, httpx, json, mcp_server_fastmcp, mcp_server_mcpserver, Antigravity & Claude Client Integration, typing

### Community 1 - "Ollama Client & Async Generation"
Cohesion: 0.29
Nodes (5): asyncio, OllamaClient, Send a prompt to Ollama and return the generated text response., sys, run_diagnostics()

### Community 2 - "Configuration & Environment Setup"
Cohesion: 0.29
Nodes (6): dataclasses, dotenv, os, pathlib, Python MCP & HTTPX Dependencies, Settings

### Community 3 - "MCP Server Tools & File Analysis"
Cohesion: 0.29
Nodes (7): analyze_file_locally(), ask_local_llm(), check_local_llm_status(), Check Ollama service availability, version, default model, and list of…, Send a computational, summarization, or code drafting prompt to the local LLM.…, Read a local file directly on this machine and analyze it with the local LLM…, tool

### Community 5 - "Hybrid Intelligence Architecture"
Cohesion: 0.67
Nodes (3): Hybrid Intelligence Workflow, Antigravity Local LLM MCP Bridge, Zero Quota Offloading

## Knowledge Gaps
- **5 isolated node(s):** `Settings`, `Hybrid Intelligence Workflow`, `NVIDIA GeForce RTX 5060 GPU`, `Antigravity & Claude Client Integration`, `Python MCP & HTTPX Dependencies`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 25 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `OllamaClient` connect `Ollama Client & Async Generation` to `Hardware & Inference Engine`, `Health Check & Status Telemetry`?**
  _High betweenness centrality (0.271) - this node is a cross-community bridge._
- **Why does `Antigravity Local LLM MCP Bridge` connect `Hybrid Intelligence Architecture` to `Hardware & Inference Engine`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._
- **Why does `ask_local_llm()` connect `MCP Server Tools & File Analysis` to `Hardware & Inference Engine`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **What connects `Settings`, `Hybrid Intelligence Workflow`, `NVIDIA GeForce RTX 5060 GPU` to the rest of the system?**
  _5 weakly-connected nodes found - possible documentation gaps or missing edges._