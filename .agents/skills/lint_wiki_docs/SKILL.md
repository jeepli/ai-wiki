---
name: lint-wiki-docs
description: Use when auditing or linting this personal AI learning wiki for broken links, orphan pages, root-layout issues, page format drift, sparse citations, weak source coverage, concept gaps, contradictions, outdated claims, prior report regressions, or raw sources not reflected in wiki pages.
---

# Lint Wiki Docs

## Overview

Audit the personal AI learning wiki and write findings to a timestamped report under `reports/`.

Default behavior is report-only: do not edit `wiki/`, `raw/`, `wiki/index.md`, or `wiki/log.md` unless the user explicitly asks to fix findings after the audit.

## Hard Constraints

- Never modify `raw/`.
- Do not modify wiki pages during audit mode.
- Treat `wiki/index.md` and `wiki/log.md` as the only allowed root-level wiki markdown files.
- Write every audit result to `reports/{{yyyy-mm-dd-hh-mm-ss}}.md`.
- Use a findings table with severity, category, location, finding, and suggested fix.
- Inspect recent existing reports before starting a new audit.
- Do not write "No findings" unless every in-scope category and prior-report regression check was completed.
- If any category is skipped, call the report a partial audit and list skipped categories in coverage notes.
- Ask the user when source interpretation, categorization, or fix ownership is ambiguous.

## Expected Wiki Shape

- `raw/paper/`: paper PDFs and other paper-like source documents.
- `wiki/index.md`: table of contents for all wiki pages.
- `wiki/log.md`: append-only ingest and maintenance log.
- `wiki/papers/`: papers, long-form articles, course notes, and source summaries.
- `wiki/concepts/`: reusable AI, ML, LLM, optimization, and systems concepts.
- `wiki/models/`: model families, architectures, training recipes, and capabilities.
- `wiki/systems/`: inference, training, data, evaluation, kernel, and infrastructure systems.
- `wiki/math/`: mathematical foundations and derivations.
- `code-repos.yml`: tracked manifest for explorable local code repositories.
- `external-repos/`: ignored local code repository clones used for focused code exploration, not wiki ingest.

Other scoped directories are acceptable only when the content clearly does not fit the default layout.

## Audit Scope

Audit these areas when the user asks to lint or audit the wiki:

- **Root layout**: no content page lives directly under `wiki/`; root markdown is limited to `index.md` and `log.md`.
- **Page format**: maintained pages have title, summary, sources, last updated, separator, useful headings, and related pages.
- **Broken links**: every `[[wiki-link]]` resolves to an existing `wiki/**/*.md` page, including aliases and heading suffixes.
- **Orphan pages**: pages with no inbound links, excluding `wiki/index.md` and `wiki/log.md`.
- **Index coverage**: `wiki/index.md` lists maintained pages with useful one-line descriptions.
- **Log coverage**: `wiki/log.md` reflects recent wiki changes when page history is available.
- **Citation coverage**: factual paragraphs, key numbers, results, comparisons, definitions, diagrams, and limitations cite a source.
- **Citation quality**: citations identify the source clearly enough; ambiguous repeated basenames should use source paths.
- **Source support**: cited sources actually support the wiki claim; unknown or tentative source statements must not become definitive wiki claims.
- **Raw coverage**: important documents under `raw/`, including paper PDFs under `raw/paper/`, are reflected in wiki pages or called out as uningested.
- **Code-derived support**: code-derived facts cite repository name, path, symbol or file, and commit/version when available.
- **Code repository manifest**: `code-repos.yml` entries use ignored `external-repos/...` paths and do not imply bulk wiki coverage.
- **Concept gaps**: recurring or central AI concepts lack reusable pages under `wiki/concepts/`, `wiki/systems/`, `wiki/models/`, or `wiki/math/`.
- **Contradictions and outdated claims**: pages conflict with each other, newer sources, or newer raw snapshots.
- **Prior-report regression**: recent findings remain open until current files and sources prove they were fixed, false positives, or out of scope.

## Source Handling

- Include `raw/` in source coverage checks.
- Treat `raw/paper/` as the default location for paper PDF sources.
- Do not treat `external-repos/` as raw coverage input.
- Do not report an external code repository as missing from `wiki/` merely because it appears in `code-repos.yml`.
- Ignore OS artifacts such as `.DS_Store`.
- For PDFs, verify whether cited claims can be traced to extracted text, page numbers, or a clearly named PDF source.
- For code-derived claims, verify the cited repository path and symbol/file when the relevant repository is locally available.
- Prefer comparing source families by version, date, or snapshot to avoid reporting old versions as missing when newer ones supersede them.
- Do not rely only on grep for semantic checks; open the relevant wiki pages and cited sources.

## Recommended Checks

Use fast local commands where possible:

- `rg --files wiki reports raw`
- `test -f code-repos.yml && sed -n '1,220p' code-repos.yml`
- `ls -1 reports/*.md | sort | tail`
- `rg -n '\[\[[^]]+\]\]' wiki`
- `find wiki -maxdepth 1 -type f -name '*.md' ! -name index.md ! -name log.md`
- inspect `wiki/index.md` and `wiki/log.md`

For link validation, a small local script is acceptable. It must resolve:

- nested targets under `wiki/**/*.md`
- alias syntax such as `[[concepts/attention|Attention]]`
- heading suffixes such as `[[papers/flashattention#method-or-mechanism]]`

## Prior Report Regression

Before writing a new report:

1. List recent reports with `ls -1 reports/*.md | sort | tail`.
2. Read the latest report with findings. If the immediately previous report says "No findings", inspect older reports until a findings report is found or report history is exhausted.
3. Build a checkpoint list from prior findings: category, location, claim, and suggested fix.
4. Re-check each checkpoint against current wiki pages and cited sources.
5. In the new report, repeat still-open findings; move closed or excluded findings to coverage notes with evidence.

A "No findings" report must explicitly state that prior findings were rechecked and why none remain open.

## Report Format

Create `reports/{{yyyy-mm-dd-hh-mm-ss}}.md` with this structure:

```markdown
# Wiki Lint Report

**Summary**: One or two sentences summarizing the audit result.

**Generated at**: YYYY-MM-DD HH:MM:SS

**Scope**: Files or directories audited.

---

## Findings

| Severity | Category | Location | Finding | Suggested fix |
| --- | --- | --- | --- | --- |
| high | Broken links | `wiki/example.md` | `[[missing-page]]` has no target. | Create the page or update the link. |

## Coverage Notes

Notes on checks completed, prior-report regression, intentionally excluded areas, and residual risks.
```

Use severity consistently:

- `high`: broken links, contradictions, outdated claims likely to mislead, unsupported key claims, or missing core source coverage.
- `medium`: page format violations, sparse citations on important pages, likely missing concept pages, index gaps, or root-layout drift.
- `low`: weak related-page links, minor naming drift, wording consistency, or low-impact citation precision issues.

If no findings exist for a category, add a coverage note instead of inventing findings.

## Fix Mode

Only enter fix mode if the user explicitly asks to fix lint findings.

When fixing:

- Use `ingest-wiki-docs` for changes that ingest new raw facts.
- Update `wiki/index.md` and `wiki/log.md` if wiki pages change.
- Preserve the original lint report; create a follow-up note or report if needed.
- Run link validation and `git diff --check` before reporting completion.

## Failure Handling

| Condition | Action |
|---|---|
| `reports/` does not exist | Create it before writing the audit report. |
| `wiki/` does not exist or has no content pages | Write a partial audit report explaining missing wiki coverage. |
| `raw/` has sources but wiki has no matching pages | Report raw coverage findings instead of silently passing. |
| `code-repos.yml` references a missing local path | Note it as optional code exploration coverage unless the audit scope requires code availability. |
| Source extraction is unreliable | Mark related source-support checks as partial and note the risk. |
| A semantic claim cannot be verified quickly | Mark it as needs verification; do not assert it is false. |

## Do Not Do

- Do not modify `raw/` or wiki pages during audit mode.
- Do not lint `external-repos/` as if it were wiki content or raw ingest input.
- Do not report "No findings" after only running link checks.
- Do not close prior findings without current evidence.
- Do not treat missing concept pages as findings unless the concept is recurring, central, or link-worthy.
- Do not replace source-reading with grep for contradiction, outdated-claim, or source-support checks.
- Do not create noisy style findings that do not affect learning value, traceability, or navigation.

## Reporting

Final response should include:

- report path
- number of findings by severity
- most important findings
- checks run
- prior-report regression result
- intentionally excluded categories or partial-audit limits
