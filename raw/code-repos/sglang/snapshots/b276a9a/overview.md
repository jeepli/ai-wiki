---
repo: sglang
commit: b276a9acee8a02159a9a8d839da8a7b4dd898b58
source_version: b276a9a
document: overview.md
status: source-backed
---

# Overview

SGLang is tracked here as an inference-engine source snapshot for structured
generation, OpenAI-compatible serving, SGLang Runtime (SRT), scheduling,
radix/prefix cache, model execution, disaggregation, and the companion
`sgl-kernel` package. Source: `sglang` commit
`b276a9acee8a02159a9a8d839da8a7b4dd898b58`; declared role in `code-repos.yml`;
package metadata in `external-repos/sglang/python/pyproject.toml`.

## Directory Map

- `python/sglang/__init__.py` is the public package surface. It exports frontend
  language APIs such as `function`, `gen`, `select`, role helpers, media helpers,
  runtime backends, and lazy runtime engine APIs
  (`sglang@b276a9a:python/sglang/__init__.py`).
- `python/sglang/lang/` implements the frontend language layer, including
  `api.py`, `ir.py`, `interpreter.py`, `choices.py`, and backend adapters for
  OpenAI, Anthropic, LiteLLM, VertexAI, Crusoe, and runtime endpoints.
- `python/sglang/srt/` is the SGLang Runtime. High-signal areas include
  `entrypoints/`, `managers/`, `model_executor/`, `mem_cache/`, `layers/`,
  `constrained/`, `function_call/`, `disaggregation/`, `speculative/`,
  `lora/`, and `configs/`.
- `sgl-kernel/` is the companion kernel package with `csrc/`, `include/`,
  Python package files under `sgl-kernel/python/sgl_kernel`, benchmarks, and
  tests (`sglang@b276a9a:sgl-kernel/csrc/`,
  `sglang@b276a9a:sgl-kernel/include/sgl_kernel_ops.h`).
- `rust/sglang-grpc/` provides the Rust extension target used by the Python
  package (`sglang@b276a9a:python/pyproject.toml`).
- `benchmark/`, `test/`, `docs/`, `examples/`, and `scripts/` provide
  performance, validation, usage, and maintenance surfaces.

## Main Subsystems

- Frontend language: public APIs in `sglang.lang.api` expose structured program
  building and backend routing.
- SRT server: `python/sglang/srt/entrypoints/http_server.py` implements HTTP APIs
  for the inference engine via FastAPI and imports OpenAI, Anthropic, and Ollama
  serving adapters.
- Runtime managers: `python/sglang/srt/managers/scheduler.py#Scheduler`,
  `schedule_batch.py#ScheduleBatch`, tokenizer/detokenizer managers, and IO
  structs coordinate request lifecycle.
- Cache/model execution: `python/sglang/srt/mem_cache/radix_cache.py#RadixCache`,
  memory pools, and `python/sglang/srt/model_executor/model_runner.py#ModelRunner`
  are key inspection points.
- Native kernels: `sgl-kernel/csrc/` and `sgl-kernel/include/` cover attention,
  GEMM, quantization, allreduce, memory, Mamba, CPU, Metal, ROCm/MUSA, and
  extension bindings.
