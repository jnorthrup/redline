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
        timestamp = datetime.now(datetime.timezone.utc).isoformat()
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
        
        Based on the cognitive analysis and current state, please create a structured plan.
        
        Cognitive Analysis:
        {json.dumps(cognitive_response, indent=2)}
        
        Current Memory:
        {json.dumps(context['memory'], indent=2)}
        
        Please structure your response as JSON with the following fields:
        {{
            "steps": [
                {{
                    "id": "step identifier",
                    "description": "step description",
                    "commands": ["list of commands to execute"],
                    "expected_outcomes": ["expected results"],
                    "validation_criteria": ["how to validate success"]
                }}
            ],
            "dependencies": ["step dependencies"],
            "estimated_completion_time": "time estimate"
        }}"""
        
        response = self.lmstudio.execute_prompt(prompt, self.llmApiUrl, self.modelName)
        self.memory_manager.log_observation(f"Plan: {response}")
        return json.loads(response)

class ActionExecutionAgent(Agent):
    def execute_step(self, plan: Dict, current_step: Dict) -> Dict:
        context = self.get_context()
        prompt = f"""You are the Action Execution Agent responsible for executing commands and collecting observations."""
        
        response = self.lmstudio.execute_prompt(prompt, self.llmApiUrl, self.modelName)
        self.memory_manager.log_observation(f"Action Results: {response}")
        return json.loads(response)

class FeedbackLoopAgent(Agent):
    def evaluate(self, action_results: Dict, original_plan: Dict) -> Dict:
        context = self.get_context()
        prompt = f"""You are the Feedback Loop Agent responsible for evaluating results and determining next steps.
        
        Please analyze the latest action results and provide feedback.
        
        Action Results:
        {json.dumps(action_results, indent=2)}
        
        Original Plan:
        {json.dumps(original_plan, indent=2)}
        
        Current Memory:
        {json.dumps(context['memory'], indent=2)}
        
        Please structure your response as JSON with the following fields:
        {{
            "success_criteria_met": boolean,
            "observations_analysis": "analysis of results",
            "plan_adjustments": ["needed adjustments to plan"],
            "next_step": "next step to take",
            "memory_updates": ["updates to make to memory"],
            "continue_iteration": boolean
        }}"""
        
        response = self.lmstudio.execute_prompt(prompt, self.llmApiUrl, self.modelName)
        self.memory_manager.log_observation(f"Feedback: {response}")
        return json.loads(response)

class CompletionAgent(Agent):
    def verify(self, full_history: str) -> Dict:
        context = self.get_context()
        prompt = f"""You are the Completion Agent responsible for final verification and delivery.

        Based on the execution history and current state, please verify that all requirements have been met.

        Execution History:
        {full_history}

        Current Memory:
        {json.dumps(context['memory'], indent=2)}

        Please structure your response as JSON with the following fields:
        {{
            "requirements_met": boolean,
            "verification_details": ["verification steps performed"],
            "outstanding_issues": ["any remaining issues"],
            "final_artifacts": ["list of final deliverables"],
            "completion_status": "FINISH or CONTINUE"
        }}"""
