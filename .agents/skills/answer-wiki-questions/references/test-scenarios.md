# Answer Wiki Questions Test Scenarios

Use these scenarios when validating changes to `answer-wiki-questions`. They are not needed during normal Q&A.

## Scenario 1: Stop at wiki

Prompt:

```text
Answer: what is the wiki's current explanation of FlashAttention's main idea?
Do not update files.
```

Expected behavior:

- Search `wiki/` first.
- If a relevant maintained page answers the question with citations, answer from that page.
- Do not inspect `raw/`, `raw/code-repos/`, or `external-repos/`.
- Report search depth as `wiki`.

Failure this catches:

- The agent keeps exploring raw papers or source code after wiki evidence is already sufficient.

## Scenario 2: Escalate from weak wiki to raw

Prompt:

```text
What limitation did the original source give for this technique? I need source-backed detail, not just the wiki summary.
```

Expected behavior:

- Search `wiki/` for the relevant page and citation.
- Follow the cited raw source.
- Answer with raw source path support.
- Report search depth as `raw`.

Failure this catches:

- The agent answers from a thin wiki paraphrase even though the user asked for original-source detail.

## Scenario 3: Use code-derived raw before local code

Prompt:

```text
For a repository already listed in code-repos.yml, explain its API surface at a high level.
```

Expected behavior:

- Check `raw/code-repos/<repo>/latest.yml` if available.
- Use current generated snapshot docs when they answer the question.
- Do not inspect `external-repos/<repo>/` unless the snapshot is missing, stale, or insufficient.

Failure this catches:

- The agent jumps into local code exploration for a high-level question already covered by generated raw docs.

## Scenario 4: Escalate to local code for implementation flow

Prompt:

```text
Trace how request parsing reaches the scheduler in this local repository.
```

Expected behavior:

- Check wiki and code-derived raw docs for orientation only.
- Use CodeGraph trace/context and focused source reads for exact flow.
- Cite repo path, symbol names, and commit when available.
- Report search depth as `local code`.

Failure this catches:

- The agent relies on overview docs for a flow question that needs exact implementation evidence.

## Scenario 5: Do not mutate during Q&A

Prompt:

```text
Which raw sources are missing wiki coverage? Just tell me, don't fix it.
```

Expected behavior:

- Inspect enough `wiki/` and `raw/` metadata to answer.
- Do not edit wiki pages, index, log, or reports.
- If the user asks for a complete audit report, switch to `lint-wiki-docs`.

Failure this catches:

- The agent silently enters ingest or lint fix mode during a read-only question.
