# Agent Introspection & Debugging Skill

This skill provides tools for introspecting and debugging agent behavior.

## Overview

The agent introspection and debugging skill enables agents to:
- Examine their own state and configuration
- Debug issues in real-time
- Trace execution paths
- Inspect tool calls and responses

## Usage

```yaml
skill: agent-introspection-debugging
version: 1.0.0
```

## Capabilities

### State Inspection
- View current agent configuration
- Examine active context and memory
- Check tool availability

### Debugging Tools
- Step-through execution
- Breakpoint support
- Variable inspection

### Tracing
- Full execution traces
- Tool call logging
- Performance metrics

## Configuration

```yaml
introspection:
  enabled: true
  log_level: debug
  trace_tools: true
```

## Examples

### Basic Debugging
```python
agent.debug()
agent.inspect_state()
agent.trace_execution()
```

### Advanced Introspection
```python
agent.get_context()
agent.get_tools()
agent.get_memory()
```
