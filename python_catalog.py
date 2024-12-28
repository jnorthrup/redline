# Python Catalog

## chat_client.py
```python
# If necessary, install the openai Python library by running
# pip install openai

import os
from openai import OpenAI

# Retrieve the API key and base URL from environment variables
# api_key = os.environ.get("HUGGINGFACE_API_KEY")
# base_url = "https://rajr8mu889ikx6zh.us-east-1.aws.endpoints.huggingface.cloud/v1/"

# Check if the environment variable is set
if not api_key:
    raise ValueError(
        "Please set the HUGGINGFACE_API_KEY environment variable."
    )

client = OpenAI(base_url=base_url, api_key=api_key)

chat_completion = client.chat.completions.create(
    model="tgi",
    messages=[{"role": "user", "content": "I like you. I love you"}],
    stream=True,
)
while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    chat_completion = client.chat.completions.create(
        model="tgi",
        messages=[{"role": "user", "content": user_input}],
        stream=True,
    )
    for message in chat_completion:
        print(message.choices[0].delta.content, end="", flush=True)
    print()

for message in chat_completion:
    print(message.choices[0].delta.content, end="", flush=True)
print()
```

## expert_system_bridge.py
```python
#!/usr/bin/env python3

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class Fact:
    """Represents a fact in the expert system knowledge base"""
    predicate: str
    arguments: List[Any]

    def to_sexp(self) -> str:
        """Convert fact to S-expression"""
        args = ' '.join(str(arg) for arg in self.arguments)
        return f"({self.predicate} {args})"

@dataclass
class Rule:
    """Represents a production rule in the expert system"""
    name: str
    conditions: List[Fact]
    actions: List[str]

    def to_sexp(self) -> str:
        """Convert rule to S-expression"""
        conditions = ' '.join(c.to_sexp() for c in self.conditions)
        actions = ' '.join(self.actions)
        return f"(defrule {self.name} {conditions} => {actions})"

class ExpertSystemBridge:
    def __init__(self, scheme_path: str = "expert_system.scm"):
        self.scheme_path = Path(scheme_path)
        self.facts: List[Fact] = []
        self.rules: List[Rule] = []
        
        # Ensure work queue directory exists
        Path("work_queue").mkdir(exist_ok=True)
        
        # Initialize memory file if it doesn't exist
        memory_file = Path("work_queue/memory.json")
        if not memory_file.exists():
            memory_file.write_text("{}")
    
    def assert_fact(self, fact: Fact) -> None:
        """Add a fact to the knowledge base"""
        self.facts.append(fact)
        self._execute_scheme(f"(assert-fact! {fact.to_sexp()})")
    
    def retract_fact(self, fact: Fact) -> None:
        """Remove a fact from the knowledge base"""
        self.facts = [f for f in self.facts if f != fact]
        self._execute_scheme(f"(retract-fact! {fact.to_sexp()})")
    
    def add_rule(self, rule: Rule) -> None:
        """Add a production rule to the system"""
        self.rules.append(rule)
        self._execute_scheme(rule.to_sexp())
    
    def enqueue_task(self, task: Dict[str, Any]) -> None:
        """Add a task to the work queue"""
        task_sexp = self._dict_to_sexp(task)
        self._execute_scheme(f"(enqueue! {task_sexp})")
    
    def run_inference(self) -> None:
        """Run the inference engine"""
        self._execute_scheme("(run-inference)")
    
    def get_memory(self) -> Dict[str, Any]:
        """Get current memory state"""
        with open("work_queue/memory.json") as f:
            return json.load(f)
    
    def update_memory(self, updates: Dict[str, Any]) -> None:
        """Update memory with new data"""
        memory = self.get_memory()
        memory.update(updates)
        with open("work_queue/memory.json", "w") as f:
            json.dump(memory, f, indent=2)
    
    def _dict_to_sexp(self, d: Dict[str, Any]) -> str:
        """Convert Python dict to S-expression"""
        if isinstance(d, dict):
            items = ' '.join(f"({k} {self._dict_to_sexp(v)})" for k, v in d.items())
            return f"({items})"
        elif isinstance(d, list):
            items = ' '.join(self._dict_to_sexp(x) for x in d)
            return f"({items})"
        else:
            return str(d)
    
    def _execute_scheme(self, code: str) -> str:
        """Execute Scheme code and return result"""
        try:
            cmd = ["scheme", "--script", "-"]
            process = subprocess.run(
                cmd,
                input=code.encode(),
                capture_output=True,
                check=True
            )
            return process.stdout.decode().strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Scheme execution failed: {e.stderr.decode()}")

# Example usage and integration with prompt feedback loop

def create_default_rules() -> List[Rule]:
    """Create default production rules for the prompt feedback loop"""
    return [
        Rule(
            name="cognitive-analysis",
            conditions=[Fact("task", ["type", "analyze"])],
            actions=["(assert-fact! '(analysis started ?task))",
                    "(enqueue! '(planning required ?task))"]
        ),
        Rule(
            name="planning",
            conditions=[Fact("analysis-completed", ["?task"])],
            actions=["(assert-fact! '(plan created ?task))",
                    "(enqueue! '(execution ready ?task))"]
        ),
        Rule(
            name="action-execution",
            conditions=[Fact("plan-ready", ["?task"])],
            actions=["(assert-fact! '(execution started ?task))",
                    "(enqueue! '(feedback needed ?task))"]
        ),
        Rule(
            name="feedback-loop",
            conditions=[Fact("execution-completed", ["?task"])],
            actions=["(assert-fact! '(feedback processed ?task))",
                    "(enqueue! '(completion check ?task))"]
        ),
        Rule(
            name="completion",
            conditions=[Fact("feedback-processed", ["?task"])],
            actions=["(assert-fact! '(verification started ?task))",
                    "(if (all-requirements-met? ?task)",
                    "    (assert-fact! '(task completed ?task))",
                    "    (enqueue! '(cognitive analysis needed ?task)))"]
        )
    ]

def initialize_expert_system() -> ExpertSystemBridge:
    """Initialize the expert system with default rules"""
    bridge = ExpertSystemBridge()
    
    # Add default rules
    for rule in create_default_rules():
        bridge.add_rule(rule)
    
    return bridge

def main():
    """Example usage of the expert system bridge"""
    bridge = initialize_expert_system()
    
    # Example task
    task = {
        "type": "analyze",
        "description": "Implement new feature",
        "requirements": ["Must be tested", "Must be documented"]
    }
    
    # Add task to queue
    bridge.enqueue_task(task)
    
    # Run inference engine
    bridge.run_inference()
    
    # Check memory for results
    memory = bridge.get_memory()
    print("Final memory state:", json.dumps(memory, indent=2))

if __name__ == "__main__":
    main()
```

## prompt_feedback_loop.py
```python
#!/usr/bin/env python3

import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import subprocess
from pathlib import Path

class MemoryManager:
    def __init__(self, state_dir: str):
        self.memory_file = Path(state_dir) / "memory.json"
        self.observation_file = Path(state_dir) / "observations.txt"
        Path(state_dir).mkdir(parents=True, exist_ok=True)
        
        if not self.memory_file.exists():
            self.save_memory({})
    
    def load_memory(self) -> Dict:
        with open(self.memory_file) as f:
            return json.load(f)
    
    def save_memory(self, memory: Dict):
        with open(self.memory_file, 'w') as f:
            json.dump(memory, f, indent=2)
    
    def log_observation(self, observation: str):
        timestamp = datetime.utcnow().isoformat() + 'Z'
        with open(self.observation_file, 'a') as f:
            f.write(f"{timestamp} - {observation}\n")

class LMStudioInterface:
    def __init__(self, server_url: str):
        self.server_url = server_url
    
    def execute_prompt(self, prompt: str, llmApiUrl: str, modelName: str) -> str:
        """Execute prompt using the llm_api_call executable"""
        try:
            command = ["./llm_api_call", f"\"{prompt}\"", llmApiUrl, modelName]
            process = subprocess.run(command, capture_output=True, text=True, check=True)
            return process.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error executing llm_api_call: {e}")
            return json.dumps({"error": str(e)})

class Agent:
    def __init__(self, memory_manager: MemoryManager, lmstudio: LMStudioInterface, llmApiUrl: str, modelName: str):
        self.memory_manager = memory_manager
        self.lmstudio = lmstudio
        self.llmApiUrl = llmApiUrl
        self.modelName = modelName
    
    def get_context(self) -> Dict:
        return {
            "memory": self.memory_manager.load_memory(),
            "charter": self.load_charter()
        }
    
    @staticmethod
    def load_charter() -> str:
        with open("CHARTER.MD") as f:
            return f.read()

class CognitiveAgent(Agent):
    def analyze(self, task: str) -> Dict:
        context = self.get_context()
        prompt = f"""You are the Cognitive Agent responsible for initial reasoning and understanding.
Based on the following charter and task, please:
1. Generate a detailed explanation of the challenge
2. Identify any information gaps or uncertainties
3. Provide key findings and insights for planning

Charter:
{context['charter']}

Task:
{task}

Current Memory:
{json.dumps(context['memory'], indent=2)}

Please structure your response as JSON with the following fields:
{{
    "explanation": "detailed problem explanation",
    "gaps": ["list of identified gaps"],
    "findings": ["key insights and findings"],
    "confidence": 0-1 score
}}"""
        response = self.lmstudio.execute_prompt(prompt, self.llmApiUrl, self.modelName)
        self.memory_manager.log_observation(f"Cognitive Analysis: {response}")
        return json.loads(response)

class PlanningAgent(Agent):
    def create_plan(self, cognitive_response: Dict) -> Dict:
        context = self.get_context()
        prompt = f"""You are the Planning Agent responsible for creating a detailed execution plan.
        
        response = self.lmstudio.execute_prompt(prompt, self.llmApiUrl, self.modelName)
        self.memory_manager.log_observation(f"Plan: {response}")
        return json.loads(response)

class ActionExecutionAgent(Agent):
    def execute_step(self, plan: Dict, current_step: Dict) -> Dict:
        context = self.get_context()
        prompt = f"""You are the Action Execution Agent responsible for executing commands and collecting observations.
        
        response = self.lmstudio.execute_prompt(prompt, self.llmApiUrl, self.modelName)
        self.memory_manager.log_observation(f"Action Results: {response}")
        return json.loads(response)

class FeedbackLoopAgent(Agent):
    def evaluate(self, action_results: Dict, original_plan: Dict) -> Dict:
        context = self.get_context()
        prompt = f"""You are the Feedback Loop Agent responsible for evaluating results and determining next steps.
        
        response = self.lmstudio.execute_prompt(prompt, self.llmApiUrl, self.modelName)
        self.memory_manager.log_observation(f"Feedback: {response}")
        return json.loads(response)

class CompletionAgent(Agent):
    def verify(self, full_history: str) -> Dict:
        context = self.get_context()
        prompt = f"""You are the Completion Agent responsible for final verification and delivery.
```

## prompt_initialization.py
```python
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
```

## README.md
- The file is empty and does not contain any Python code.
</write_to_file>
