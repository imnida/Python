# Agent Sort Skill

This skill provides sorting capabilities for agent data and collections.

## Overview

The agent sort skill enables agents to:
- Sort collections of data
- Apply custom sort criteria
- Handle complex nested structures
- Perform stable and unstable sorts

## Usage

```yaml
skill: agent-sort
version: 1.0.0
```

## Capabilities

### Basic Sorting
- Sort arrays by value
- Sort objects by key
- Sort by multiple criteria

### Advanced Sorting
- Custom comparators
- Nested field sorting
- Type-aware sorting

### Performance
- O(n log n) complexity
- Memory efficient
- Streaming support

## Configuration

```yaml
sort:
  algorithm: timsort
  stable: true
  direction: ascending
```

## Examples

### Basic Sort
```python
agent.sort(data, key='name')
agent.sort(data, key='date', reverse=True)
```

### Multi-key Sort
```python
agent.sort(data, keys=['priority', 'name'])
```
