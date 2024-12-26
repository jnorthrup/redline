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