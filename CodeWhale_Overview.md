# 🐋 CodeWhale – Terminal Coding Agent for DeepSeek Models

**CodeWhale** (by Hmbown) is an open source terminal coding agent designed to work with **DeepSeek V4** models (and other OpenAI-compatible providers).

## 🔍 What is it?

CodeWhale is a coding agent that runs in your terminal. It can:
- Read and edit files
- Execute shell commands
- Search the web
- Manage Git
- Coordinate sub-agents via a keyboard-driven TUI interface

## ⚙️ Key Features

| Feature | Description |
|---------|-------------|
| **Auto Mode** | `--model auto` automatically selects the model and reasoning level per turn |
| **Reasoning Streaming** | Real-time visualization of DeepSeek thinking blocks |
| **Full Tool Suite** | File operations, shell, git, web search, MCP, sub-agents |
| **1M Token Context** | Context tracking, manual or configured compaction |
| **Three Modes** | Plan (read-only), Agent (with approval), YOLO (auto-approved) |
| **OS Sandbox** | Seatbelt (macOS), Landlock (Linux), Job Objects (Windows) |
| **HTTP/SSE Runtime API** | `codewhale serve --http` for headless workflows |
| **MCP Protocol** | Connect to Model Context Protocol servers |
| **System Skills** | Composable instruction packs installable from GitHub |

## 🌐 Open Source / Open Weight Model Support

Although initially designed for **DeepSeek V4**, CodeWhale supports multiple providers via an OpenAI-compatible interface:

```bash
# Supported providers
codewhale --provider nvidia-nim      # NVIDIA NIM
codewhale --provider openrouter      # OpenRouter
codewhale --provider ollama          # Ollama (local models)
codewhale --provider sglang          # Self-hosted SGLang
codewhale --provider vllm            # Self-hosted vLLM
codewhale --provider openai          # Generic OpenAI-compatible endpoint
```

> ✅ **For local models**: You can point CodeWhale at a local Ollama or vLLM instance to use open weight models like **Qwen3-Coder**, **CodeLlama**, or **DeepSeek-Coder** locally.

## 📦 Quick Install

```bash
# Via npm (easiest)
npm install -g codewhale

# Via Cargo (Rust)
cargo install codewhale-cli --locked
cargo install codewhale-tui --locked

# Via Docker
docker run --rm -it \
  -e DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY" \
  -v "$PWD:/workspace" \
  ghcr.io/hmbown/codewhale:latest
```

## 🔧 Configuration for Local Models (Ollama example)

```bash
# Pull model via Ollama
ollama pull qwen3-coder:32b

# Launch CodeWhale with Ollama
OLLAMA_BASE_URL="http://localhost:11434/v1" \
codewhale --provider ollama --model qwen3-coder:32b
```

## 📚 Documentation

- [Full README](https://github.com/Hmbown/CodeWhale)
- [Installation Guide](https://github.com/Hmbown/CodeWhale/blob/main/docs/INSTALL.md)
- [MCP Integration](https://github.com/Hmbown/CodeWhale/blob/main/docs/MCP.md)
- [Technical Architecture](https://github.com/Hmbown/CodeWhale/blob/main/docs/ARCHITECTURE.md)
