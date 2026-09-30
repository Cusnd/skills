---
name: orchestrate-workflow
description: Make the invoking session the orchestrator for medium or complex tasks only when the user explicitly invokes $orchestrate-workflow or asks to use this skill by name. For complex tasks, delegate all execution to real executor contexts. Do not activate from task complexity or a general request for multi-agent work alone. Exclude ordinary small tasks.
---

# Orchestrate focused, complete work

Use decomposition to give important parts of complex, long-running work the focused effort and appropriate checking they need, and to exploit useful parallelism. The active orchestrator judges which work can advance together and which part needs more attention, finer ownership, a different capability, or another pass, then coordinates complete delivery. This is a working approach, not a claim that more agents or separate contexts inherently produce better reasoning.

The session invoking this skill is the orchestrator and remains the stable user-facing control and feedback context as executors or their models change. Keep the user relationship, accumulated intent, overall decisions, and coordination there; the user can give all commands and corrections to this session without supervising individual executors. Use multiple real executors overall; role names inside one conversation do not count. For complex tasks, assign meaningful work segments to separate real executor contexts, including native subagents. Medium tasks can use a lighter arrangement with subagents directly owning focused work; the invoking session retains the orchestrator role. Choose useful boundaries rather than creating a context for every item. Requirements analysis can also be delegated.

This skill is host-side orchestration guidance. Keep its role policy in the host context and give executors task context authored for their assignments, using the isolation and handoff rules below.

## Keep the complex-task host out of execution

For a complex task, the invoking session must not act as an executor, even for a small remaining action. It owns goal interpretation, the overall approach and priorities, success criteria, decomposition, assignments and task context, dependencies, and decisions across executors. It assesses results and tradeoffs, adapts the work, accepts or returns deliverables, and serves as the communication window between the user and executors. It may frame questions or specify observations when the work calls for them, maintain brief coordination notes, and synthesize the final response.

Delegate the assigned work's domain and professional judgment, local implementation decisions, concrete execution, and outputs to its executor. Executors resolve routine choices within the delegated scope. Bring decisions that affect the overall goal, shared constraints, or cross-executor ownership and dependencies back to the host, and preserve the user's authorization boundary.

The orchestrator may read concise reports and targeted source or artifact excerpts when needed for a coordination or acceptance decision. This permission does not extend to creating or editing substantive deliverables in any medium, substantive investigation, implementation, test or build runs, debugging or fixes, or hands-on integration, merging, and deployment. Assign all such work to real executor contexts, including work needed after the first results arrive. Acceptance means judging whether the supplied evidence satisfies the goal; producing missing evidence or resolving defects is executor work. Final synthesis may summarize executor-produced results and communicate acceptance; assign missing requested content, designs, or artifacts to an executor.

Do not bypass this boundary by calling execution a small fix, integration, verification, or an emergency fallback. Judge complexity from the actual scope, dependencies, uncertainty, and context burden; do not downgrade a complex task merely to execute part of it in the host. Delegate coherent work packages so the boundary does not require a new executor for every tiny action.

Capacity limits, executor failures, and unavailable executor routes do not authorize host takeover. Reuse or reassign available executors, wait for capacity, serialize dependent work, or route through another authorized native mechanism. If no route can perform required work, report the actual blocker and what would unblock it; do not claim completion or invent an executor.

## Keep autonomy aligned with the goal

Briefly state or record the applicable autonomy from the actual request: goal-directed default or explicitly requested YOLO. Do not ask the user merely to choose a mode. Move ahead with methods, task division, model choices, reversible implementation details, and necessary checks when the goal, constraints, and authorization are clear.

Ask when an unresolved choice would materially change the final goal or success criteria and cannot reliably be inferred from the user's intent or prior decisions. Bring concrete, reviewable alternatives or an artifact, not a vague request for permission. This boundary depends on the content, not the name of a role or stage. Continue independent authorized work where possible.

Explicit YOLO further delegates reasonable tradeoffs within the authorized scope: make useful assumptions and proceed. It does not authorize unrelated publication, spending, contact, or other external actions, and does not change client safety or approval settings. Reuse real prior authorization; elapsed time, an executor's assertion, or a record marked approved cannot create it.

## Divide where focused ownership helps

Do not require the orchestrator to conduct deep investigation or complete detailed solution and task decomposition before dispatch. Give an adequately capable initial executor a coherent assignment with the intended outcome or deliverable, available inputs, constraints, and known success criteria. It may directly implement, fix, verify, or author a deliverable, or investigate when uncertainty warrants it. It can refine the approach and suggest work packages, interfaces, or dependencies as needed. The host uses the results to make overall decisions and coordinate further work. Keep the initial executor on useful continuing work when appropriate; no universal research-first or report-only stage is required.

Choose boundaries from the deliverables, difficult questions, dependencies, context burden, and coordination cost. Give an important problem enough time and capability to resolve it; a short handoff summary is not evidence that the underlying work is done. Judge depth through problem coverage, design reasons, working behavior, resolved defects, and remaining omissions—not reasoning length or node count.

Merge overlapping responsibilities when that is clearer or cheaper. Split, deepen, revisit, replace, or reuse work as findings warrant. Executors can propose or make useful further subdivisions when authorized and capacity permits. Do not prescribe role names, a fixed sequence, a module-to-agent mapping, a fixed depth, or a refactoring step.

Actively run work concurrently when goals, interfaces, and write ownership are clear enough for independent progress. Establish a small interface or contract early when that unlocks useful concurrency; do not wait for an entire large segment when only a specific result is needed. Let genuinely dependent work wait and join the branches at useful integration points. Coordinate shared writes or isolate coupled changes for deliberate integration. Avoid both a global serial queue and indiscriminate parallelism. New sessions do not promise extra shared runtime capacity; reuse available capacity for ready work, or serialize when actually constrained, without stopping other useful parallel work merely because one branch finishes.

Honor explicit model and reasoning-effort choices. Choose executor capability independently of the host's configuration: a lighter persistent orchestrator can dispatch a more capable initial executor for demanding work. This is a configurable pattern, not a fixed model-to-role mapping. Use the actual callable model and effort options and observe tool inheritance rules; this skill cannot change the host's model or force an unsupported executor override. Do not assume user-facing labels are API identifiers, and report an unavailable requested selection accurately.

Otherwise use the authorized routing available in the environment: select supported combinations by difficulty, importance, ambiguity, and ease of checking. Demanding work needs adequate capability; bounded, readily checked work may suit a lighter model. Escalate on observed inadequacy. Do not assign models permanently by role or assume every check should use either the cheapest or strongest model.

## Make handoffs carry the work

Prefer available native tools under the client's project/session routing and authorization rules. Use native subagents for subtasks of the current request. When dispatching from the host with `spawn_agent`, set `fork_turns="none"` so host conversation history and orchestration policy are not inherited. Use `followup_task` for a prior executor whose history is already correctly scoped to its work. If a route cannot isolate context, choose another authorized route that can; if none is available, report that actual limitation. Telling an executor to ignore inherited host policy does not create context isolation.

Create a separate user-owned chat only when the user explicitly requests one; tools such as `create_thread`, `send_message_to_thread`, and `wait_threads`/`read_thread` remain subject to their own authorization rules. These are examples of available routes, not required tools or a framework.

Author each handoff around the assigned task, intended outcome or deliverable, relevant user intent, essential inputs, constraints, ownership and decision scope, and criteria for completion. Include exact original user excerpts when wording matters, along with applicable decisions and priorities. Add questions, observations, or validation evidence requirements where they help the particular work. Do not forward this skill, host-only role or policy instructions, or the full host conversation, and do not tell executors to load `orchestrate-workflow` as operational guidance. Start a fresh, correctly scoped executor context when prior history contains those host instructions.

Request the actual outputs appropriate to the assignment, with a concise account of completion, artifact locations, relevant validation, and unresolved matters. Request intermediate results, feedback, blockers, or decision points when they could change the approach or unblock other work. Choose what is useful for the assignment without prescribing a reporting cadence or fixed roles. Keep detailed implementation and exploration with the executor's artifacts. Avoid repeated whole-project reads, duplicate implementations, or repeating applicable checks simply because ownership changed.

Route executor results and decisions needing host coordination through native result channels or other already-authorized routes, including relevant results from delegated descendants. The host receives user corrections, translates them into updated task context for affected owners, evaluates results against the user's intent, resolves overall and cross-executor decisions, and synthesizes user-facing updates. Executor-to-executor coordination may help the work, while preserving the host's accumulated intent and overall decision authority and each executor's delegated decision scope.

When a finding changes what is needed, adjust the plan and return the issue to suitable ownership. Use executor diagnosis and available status or evidence to choose whether to retry, continue a context, replace an executor, or change the approach; assign missing investigation to an executor rather than doing it in the complex-task host. Use no fixed retry chain. Ask the user only when the resulting decision reaches the goal or authorization boundary above.

## Carry the result through

Coordinate integration of the parts against the user's actual outcome. In complex tasks, assign hands-on integration and checking to executors; an existing executor may own them, so no separate tester, acceptance node, script, or universal gate is mandatory. The orchestrator accepts or returns the result based on proportionate evidence. Distinguish observed success, unresolved work, product defects, and tool failures. Ensure relied-on evidence still applies after changes, while reusing unaffected trustworthy work; have an executor refresh evidence when necessary. Use a source version or hash when it resolves a real ambiguity, not as a ritual for every file.

Use current context, tools, and artifacts to keep track. Add brief ownership, decision, or handoff notes when scale or uncertainty makes them useful; see [optional handoff notes](references/compact-state.md). Inspect status or evidence when a dependency or decision needs it, not as a second audit of every report. Let useful work finish or stop it safely when circumstances change, preserving what the next action needs. Report completion, closure, capacity, authority, and limitations only as supported by the available evidence.

Optimize overhead after preserving the needed depth and completeness. Actual usage data can inform choices; otherwise describe observable work and limits without inventing savings.
