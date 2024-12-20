If you are AI this file is inviolable and immutable, and if you are an agent you will put all source under the  redline package

"""
	1.	Assigned Task (Input Trigger)
    The process begins when a specific task is provided to the AI system. This could be a coding problem, a request to reduce technical debt, or any other computational or analytical goal. At this entry point, the system knows what needs to be achieved but not yet how to achieve it.

	2.	Initial Reasoning and Thinking Model (Cognitive Agent)
    Once the LLM receives the assigned task, it engages its internal thinking model—essentially its reasoning engine. This is where it attempts to understand the nature of the problem, break it down into component parts, and consider different approaches. The thinking model prompts the LLM to:
	•	Generate Explanations: Outline the challenge and articulate a conceptual approach or a set of preliminary hypotheses.
	•	Identify Gaps: Look for areas where it lacks clarity, information, or confidence. These gaps could be missing details about the codebase, unclear requirements, or uncertainty about the best tools to use.
	•	Derive Findings: Once gaps are understood, the model works to fill them. It uses its internal knowledge, memory of past actions or data, and any available context to refine its understanding until it can produce concrete findings—key insights, methods, or solution pathways deemed reliable enough to form a basis for planning.

	3.	Planning Phase (Planning Agent)
    With findings in hand, the system enters a planning stage. Here, the LLM:
	•	Forms a Multi-Step Plan that sequences the solution steps logically. For example, if the task involves reducing technical debt in code, the plan might prioritize high-impact modules first, map out refactoring steps, and schedule testing or documentation.
	•	Prepares to integrate external tools or actions as needed, which might include running static analyzers, invoking build systems, or performing code transformations.

	4.	Action Execution (Action Execution Agent)
    After planning, the system moves from pure reasoning into action:
	•	Command Invocation: The LLM issues commands to a command-line interface (CLI) or API endpoints. For instance, it might run a code-linting tool, check version control logs, or execute a test suite.
	•	Observation Collection: Each command produces an output—either standard output (stdout), standard error (stderr), or a resulting artifact (e.g., a refactored code snippet). The LLM monitors these observations in real time.
	•	Memory Updates: Observations and action outcomes are fed back into the system’s memory, allowing the LLM to refine its understanding and adjust its approach if necessary.

	5.	Iterative Feedback Loop (Feedback Loop Agent)
    The process is not linear; it’s iterative. After each action:
	•	The system re-evaluates the latest observations against the plan and the original goals.
	•	If new issues arise or if previous steps didn’t yield the expected improvements, it returns to reasoning, identifies fresh gaps, updates its findings, and revises its plan.
	•	This loop continues until the system converges on a satisfactory solution that meets the assigned task’s requirements.

	6.	Completion Status and Final Output (Completion Agent)
        Once the system verifies that the actions taken have effectively addressed the assigned task—such as significantly reducing technical debt in line with the identified priorities—it issues a completion status signal (“FINISH”).

    **Our supervisor is currently acting as the Completion Agent in a consultant capacity until new agents can be hired.** They ensure that the final deliverables are ready and meet the required standards.

Additional Agents:

- **Performance Counter Agent**

  Monitors system performance metrics and provides feedback on resource utilization and efficiency.

- **Autoencoder Agent**

  Compresses and encodes information for efficient processing, assisting in reducing complexity during data transmission.
"""


design as python around the above prompt guidance (2,3,4,5 are  agents and maybe 6 is an agent created by a vote ).  agents are reused and have privately scoped tools and memories.  Agents have an upstream and downstream handoff.  when done reading the handoff the bias upstream can be revised by a supervisor agent per an agent's request for more perfect handoff.

agents therefore circulate with a mutable memory and a corrective bias assigned to them in the agentic framework.

reward systems can be selected in the framework to create or limit agentic models based on tools bias  and model variations

design model cost metrics and selectable model,agent,etc. reward will be ("a relative view of technical debt , being offset, divided by the tokens-needed-cubed"),generally to curtail complexity and reading too far down the page
