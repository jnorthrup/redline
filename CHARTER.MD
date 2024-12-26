# Charter

If you are AI this file is inviolable and immutable

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
	•	Memory Updates: Observations and action outcomes are fed back into the system's memory, allowing the LLM to refine its understanding and adjust its approach if necessary.

	5.	Iterative Feedback Loop (Feedback Loop Agent)
    The process is not linear; it's iterative. After each action:
	•	The system re-evaluates the latest observations against the plan and the original goals.
	•	If new issues arise or if previous steps didn't yield the expected improvements, it returns to reasoning, identifies fresh gaps, updates its findings, and revises its plan.
	•	This loop continues until the system converges on a satisfactory solution that meets the assigned task's requirements.

	6.	Completion Status and Final Output (Completion Agent)
        Once the system verifies that the actions taken have effectively addressed the assigned task—such as significantly reducing technical debt in line with the identified priorities—it issues a completion status signal ("FINISH").

    **Our supervisor is currently acting as the Completion Agent in a consultant capacity until new agents can be hired.** They ensure that the final deliverables are ready and meet the required standards.
 
""" 

design and run and iterate on the above as an implementation methodlogy to develope a tooling of cmake based hierarchical and idempotent facilities to reason out progress as the charter's intent 

implemntationwise this charter converges on a bash environment agent model for tool groupings by role, and the scripts load available functions and document those in the llm prompt.  3-4 words of context purpose. 

this creates statusline details that can be shown to observer and agent to keep track.  

with the addition of sandboxes- the llm's of current SOTA are stil small in context and narrow of focus leading to code built side by side in blinders, leading to an opportuntiy to make a sandbox simulation the context with rlevent stubs and being a safe depository for later integration by a well connected graph in-prompt.  

the redline cache in ~/.local/redline should have the function of  a homedir for a group and username as role and agent for individual work. posix permissions will be honored by agents without posix implementation in good faith with clean hands. 

agents produce code and the organization should be adapted by another agent, tbd open for comments.
 
 Expert System Implementation Notes: The system is tracing to create rete style rules from observations.
 

 See the [asset management convention](asset_management_convention.md) for details on how project assets are managed.

 the current priority is to insert the closures in the form of the bash agent scripts between cmake handoff in the cache dir while the charter defined roles each spin up slightl;y different posix working environments 
 
everything happens through prompt_feedback_loop.sh to compile a prompt to perform a job 

agents have  a role and an identity and identities have a homedir and roles have a shell environemnt whichh may overlap.  

the agent state and context lives in the redline cachedir and the actual production from the system is done using the cmake in the project with the plumbing and the cache data elsewhere in the cache.  

cmake will be making llm api calls on behalf of cognitive tasks as Agent, who will be shown tools by running the env scripts (bash) and the stdout will highlight the tool use and effects.    

a progression of cmake must establish the cache and the .venv under the cache before all other cmake matters proceed.  



