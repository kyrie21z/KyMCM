---
contract_type: solution
problem_id: Q1
version: v1
status: draft
---

# Solution Contract Q1 v1

Approval records the current Problem Contract version and direct dependency Solution Contract versions in authoritative state. A new version invalidates this problem and all DAG successors; successors must renew stale dependency snapshots.

## Required Predecessor Outputs

List approved outputs required from dependency problems.

## Assumptions

State assumptions that affect the mathematical solution.

## Variables, Objectives, and Constraints

Define the mathematical specification precisely.

## Model and Algorithm

Specify the selected model and solution method.

## Input and Output Interface

Define formal inputs, outputs, and units.

## Machine-Checkable Validation Criteria

List executable checks, expected values or tolerances, and required evidence files. The report must include `problem`, `problem_contract_version`, `solution_contract_version`, `dependency_solution_versions`, `status`, and non-empty `checks` with `id`, `status`, and workspace-local `evidence`.

## Decisions Required From the User

Use `None` when no decision is pending.
