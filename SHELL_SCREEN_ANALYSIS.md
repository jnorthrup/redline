# Shell Output Screen Analysis

## Problem Statement
Need to protect against large shell output dumps while enabling LLM learning of screened output patterns.

## Key Considerations

### Protection Mechanisms
1. Screen Buffer
- Fixed-size circular buffer (e.g. 1000 lines)
- Scrollback limit
- Line length truncation
- ANSI escape code filtering

2. Output Chunking
- Stream output in manageable chunks
- Allow LLM to request "more" of truncated output
- Maintain position markers for continuation

### Learning Challenges

1. Context Loss
- Important information may be truncated
- Need to teach LLM to recognize truncation patterns
- Develop strategies for requesting relevant portions

2. Pattern Recognition
- LLM must learn to identify key output sections
- Develop heuristics for important vs noise
- Build understanding of command output structures

3. Progressive Trust
- Start with heavily restricted output
- Gradually increase limits based on successful handling
- Track command-specific trust levels

## Implementation Strategy

### 1. Screen Buffer Implementation
```python
class ShellScreen:
    def __init__(self, max_lines=1000, max_line_length=500):
        self.buffer = []
        self.max_lines = max_lines
        self.max_line_length = max_line_length
        self.position = 0

    def write(self, text):
        lines = text.splitlines()
        for line in lines:
            if len(line) > self.max_line_length:
                line = line[:self.max_line_length] + "..."

            if len(self.buffer) >= self.max_lines:
                self.buffer.pop(0)
            self.buffer.append(line)

    def read(self, start=None, count=None):
        if start is None:
            start = max(0, len(self.buffer) - 20)  # Default to last 20 lines
        if count is None:
            count = 20

        end = min(start + count, len(self.buffer))
        return self.buffer[start:end]
```

### 2. Learning Assistance

1. Output Markers
- Add clear markers for truncation points
- Include metadata about truncated content
- Provide summary statistics

2. Command Categories
- Group similar commands
- Track typical output patterns
- Build command-specific handling rules

3. Context Preservation
- Store important sections (e.g. errors)
- Maintain indexes for key content
- Allow targeted retrieval

### 3. Trust System

1. Command Trust Levels
```python
class CommandTrust:
    def __init__(self):
        self.trust_levels = {}

    def get_trust(self, command):
        if command not in self.trust_levels:
            return {
                "level": 0,  # 0-10 scale
                "successful_runs": 0,
                "output_sizes": [],
                "error_count": 0
            }
        return self.trust_levels[command]

    def update_trust(self, command, success, output_size):
        trust = self.get_trust(command)
        trust["successful_runs"] += 1 if success else 0
        trust["error_count"] += 0 if success else 1
        trust["output_sizes"].append(output_size)

        # Adjust trust level based on history
        if success:
            trust["level"] = min(10, trust["level"] + 1)
        else:
            trust["level"] = max(0, trust["level"] - 1)

        self.trust_levels[command] = trust
```

2. Progressive Limits
- Base initial limits on command category
- Increase limits with successful handling
- Reduce limits after errors

3. Output Quotas
- Track output volume over time
- Implement rate limiting
- Allow bursts for trusted commands

## LLM Training Approach

1. Initial Phase
- Start with simple, predictable commands
- Focus on understanding truncation markers
- Practice requesting specific sections

2. Pattern Learning
- Introduce varied command outputs
- Teach scanning for important content
- Build output structure models

3. Advanced Handling
- Work with large output streams
- Manage multiple command contexts
- Handle error conditions

## Implementation Phases

1. Basic Protection
- Implement screen buffer
- Add simple truncation
- Basic trust tracking

2. Enhanced Learning
- Add context markers
- Implement pattern tracking
- Build command categories

3. Advanced Features
- Dynamic trust adjustment
- Intelligent chunking
- Pattern-based filtering

## Success Metrics

1. Protection
- No memory overflows
- Controlled output sizes
- Error prevention

2. Learning
- Command pattern recognition
- Effective navigation of truncated output
- Appropriate use of "more" requests

3. Efficiency
- Minimal unnecessary truncation
- Fast pattern matching
- Optimal trust levels

## Next Steps

1. Implement basic screen buffer
2. Add trust tracking system
3. Develop initial LLM training approach
4. Test with common command patterns
5. Refine based on learning metrics
