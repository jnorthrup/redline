#!/usr/bin/env python3

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import subprocess

@dataclass
class ToolDescription:
    name: str
    purpose: str
    usage: str
    context: str

@dataclass
class ChapterFragment:
    role: str
    content: str
    relevance: float

@dataclass
class ContextBubble:
    private_memory: Dict
    shared_memory: Dict
    tool_context: List[ToolDescription]
    charter_fragments: List[ChapterFragment]

class PromptInitializer:
    def __init__(self, redline_home: str = "~/.local/redline"):
        self.redline_home = os.path.expanduser(redline_home)
        self.charter_path = "CHARTER.MD"
        self.role_mappings = {
            "cognitive": ["Initial Reasoning", "Thinking Model", "Generate Explanations"],
            "planning": ["Planning Phase", "Multi-Step Plan", "solution steps"],
            "action_execution": ["Action Execution", "Command Invocation", "Observation Collection"],
            "feedback_loop": ["Iterative Feedback Loop", "re-evaluates", "observations"],
            "completion": ["Completion Status", "Final Output", "verification"]
        }

    def extract_charter_fragments(self, role: str) -> List[ChapterFragment]:
        """Extract relevant charter fragments for a specific role"""
        with open(self.charter_path) as f:
            charter_content = f.read()

        fragments = []
        keywords = self.role_mappings.get(role, [])
        
        # Split charter into sections
        sections = charter_content.split('\n\n')
        
        for section in sections:
            relevance = sum(1 for kw in keywords if kw.lower() in section.lower())
            if relevance > 0:
                fragments.append(ChapterFragment(
                    role=role,
                    content=section.strip(),
                    relevance=relevance / len(keywords)
                ))
        
        return sorted(fragments, key=lambda x: x.relevance, reverse=True)

    def discover_tools(self, role: str) -> List[ToolDescription]:
        """Discover and describe tools available for the role"""
        tools_dir = Path(self.redline_home) / role / "tools"
        tools = []

        if tools_dir.exists():
            for tool_file in tools_dir.glob("*.sh"):
                # Extract tool documentation from script
                with open(tool_file) as f:
                    content = f.read()
                    # Parse tool description from script comments
                    desc = self._parse_tool_description(content)
                    if desc:
                        tools.append(desc)

        return tools

    def _parse_tool_description(self, script_content: str) -> Optional[ToolDescription]:
        """Parse tool description from script comments"""
        lines = script_content.split('\n')
        desc = {}
        current_section = None

        for line in lines:
            if line.startswith('# Tool:'):
                desc['name'] = line.replace('# Tool:', '').strip()
            elif line.startswith('# Purpose:'):
                desc['purpose'] = line.replace('# Purpose:', '').strip()
            elif line.startswith('# Usage:'):
                desc['usage'] = line.replace('# Usage:', '').strip()
            elif line.startswith('# Context:'):
                desc['context'] = line.replace('# Context:', '').strip()

        if all(k in desc for k in ['name', 'purpose', 'usage', 'context']):
            return ToolDescription(**desc)
        return None

    def setup_context_bubble(self, role: str) -> ContextBubble:
        """Set up a context bubble for the role"""
        role_dir = Path(self.redline_home) / role
        
        # Initialize memory structures
        private_memory = self._load_memory(role_dir / "private_memory.json")
        shared_memory = self._load_memory(role_dir / "shared_memory.json")
        
        # Get tools and charter fragments
        tools = self.discover_tools(role)
        fragments = self.extract_charter_fragments(role)
        
        return ContextBubble(
            private_memory=private_memory,
            shared_memory=shared_memory,
            tool_context=tools,
            charter_fragments=fragments
        )

    def _load_memory(self, memory_file: Path) -> Dict:
        """Load memory from file or initialize if not exists"""
        if memory_file.exists():
            with open(memory_file) as f:
                return json.load(f)
        return {}

    def generate_prompt_template(self, role: str, context: ContextBubble) -> str:
        """Generate role-specific prompt template"""
        template = f"""You are the {role.title()} Agent with the following charter responsibilities:

{self._format_charter_fragments(context.charter_fragments)}

Available Tools:
{self._format_tools(context.tool_context)}

Memory Access:
- Private Memory: {len(context.private_memory)} entries
- Shared Memory: {len(context.shared_memory)} entries

Your role is to {self._get_role_description(role)}.

When processing a task, consider:
1. Your specific charter responsibilities
2. Available tools and their contexts
3. Relevant memory access
4. Integration with other agents

Please format your responses as JSON with the following structure:
{{
    "understanding": "Your interpretation of the task",
    "plan": "Your approach to handling it",
    "tool_usage": ["Tools you plan to use"],
    "memory_requirements": ["Memory access needed"],
    "expected_outcome": "What you aim to achieve"
}}"""
        return template

    def _format_charter_fragments(self, fragments: List[ChapterFragment]) -> str:
        """Format charter fragments for prompt"""
        return "\n".join(f"- {f.content}" for f in fragments)

    def _format_tools(self, tools: List[ToolDescription]) -> str:
        """Format tool descriptions for prompt"""
        return "\n".join(f"- {t.name}: {t.purpose} (Context: {t.context})" for t in tools)

    def _get_role_description(self, role: str) -> str:
        """Get specific role description"""
        descriptions = {
            "cognitive": "analyze and understand tasks, identify gaps, and derive key findings",
            "planning": "create detailed execution plans and prepare tool integrations",
            "action_execution": "execute commands and collect observations",
            "feedback_loop": "evaluate results and determine next steps",
            "completion": "verify task completion and ensure quality"
        }
        return descriptions.get(role, "perform your assigned responsibilities")

    def initialize_role(self, role: str) -> Dict:
        """Initialize a role with its context and prompt template"""
        # Set up context bubble
        context = self.setup_context_bubble(role)
        
        # Generate prompt template
        template = self.generate_prompt_template(role, context)
        
        # Create role directory structure
        role_dir = Path(self.redline_home) / role
        role_dir.mkdir(parents=True, exist_ok=True)
        
        # Save prompt template
        template_file = role_dir / "prompt_template.txt"
        template_file.write_text(template)
        
        return {
            "role": role,
            "context_bubble": context,
            "template": template,
            "role_dir": str(role_dir)
        }

def main():
    """Initialize all agent roles"""
    initializer = PromptInitializer()
    roles = ["cognitive", "planning", "action_execution", "feedback_loop", "completion"]
    
    for role in roles:
        print(f"\nInitializing {role} agent...")
        result = initializer.initialize_role(role)
        print(f"Role directory: {result['role_dir']}")
        print(f"Template created: {result['role_dir']}/prompt_template.txt")
        print(f"Context bubble size: {len(result['context_bubble'].tool_context)} tools")

if __name__ == "__main__":
    main()