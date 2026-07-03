---
repo: vllm
commit: 8357226f4f1b92aa2139ebc482ca71012f02016b
source_version: 8357226
document: build-and-entrypoints.md
status: source-backed
---

# Build And Entrypoints

Source snapshot: `vllm` commit
`8357226f4f1b92aa2139ebc482ca71012f02016b`.

## Package Build

`pyproject.toml` defines the package as `vllm`, requires Python
`>=3.10,<3.15`, and uses `setuptools.build_meta`. Build requirements include
`cmake>=3.26.1`, `ninja`, setuptools, setuptools-scm, setuptools-rust,
`torch == 2.11.0`, `wheel`, and `jinja2`
(`vllm@8357226:pyproject.toml`).

The package discovery rule includes `vllm*`, and native extension source lives
under `csrc/`. Rust components live under `rust/`, and dependency group files
are organized under `requirements/`.

## Primary Entrypoints

- CLI: `vllm.entrypoints.cli.main:main`.
- Offline Python: `vllm.entrypoints.llm:LLM`.
- OpenAI server: `vllm.entrypoints.openai.api_server`.
- V1 async engine: `vllm.v1.engine.async_llm:AsyncLLM`.
- V1 core engine: `vllm.v1.engine.core:EngineCore`.
- Scheduler: `vllm.v1.core.sched.scheduler:Scheduler`.
- KV cache manager: `vllm.v1.core.kv_cache_manager:KVCacheManager`.
- GPU model runner: `vllm.v1.worker.gpu_model_runner:GPUModelRunner`.

## Native/Kernels

High-signal native paths:

- `csrc/attention/` for attention-specific native types.
- `csrc/cpu/` for CPU attention and CPU kernels.
- `csrc/libtorch_stable/` for libtorch-stable bindings.
- `csrc/quantization/` and `csrc/moe/` for quantization/MoE native code.
- `csrc/torch_bindings.cpp` and backend-specific binding files for torch
  extension registration.

## Tests, Examples, Benchmarks

- V1 runtime tests: `tests/v1/`.
- Engine tests: `tests/engine/`.
- Entry point tests: `tests/entrypoints/`.
- Kernel tests: `tests/kernels/` and `tests/cuda/`.
- Examples: `examples/basic/`, `examples/deployment/`,
  `examples/disaggregated/`, `examples/tool_calling/`, and related folders.
- Benchmarks: `benchmarks/`, including attention/kernels/fused-kernel
  benchmark areas.
