---
repo: sglang
commit: b276a9acee8a02159a9a8d839da8a7b4dd898b58
source_version: b276a9a
document: build-and-entrypoints.md
status: source-backed
---

# Build And Entrypoints

Source snapshot: `sglang` commit
`b276a9acee8a02159a9a8d839da8a7b4dd898b58`.

## Python Package Build

The main Python package metadata is in `python/pyproject.toml`. It defines the
project as `sglang`, requires Python `>=3.10`, uses `setuptools.build_meta`, and
uses setuptools-rust for a Rust extension target
`sglang.srt.grpc._core` from `../rust/sglang-grpc/Cargo.toml`
(`sglang@b276a9a:python/pyproject.toml`).

The package declares large runtime dependencies for serving and kernels,
including Torch 2.11, transformers 5.12.1, FastAPI, uvicorn, uvloop,
FlashAttention 4 beta, FlashInfer Python/cubin, `sglang-kernel`, CUTLASS DSL,
xgrammar, llguidance, outlines-related dependencies, and tracing/test extras
(`sglang@b276a9a:python/pyproject.toml`).

## CLI Entrypoints

- `sglang = sglang.cli.main:main`
- `killall_sglang = sglang.cli.killall:main`
- `sglang.cli.main` dispatches `serve`, `generate`, and `version`
  (`sglang@b276a9a:python/sglang/cli/main.py`).

## Runtime Entrypoints

- Public package import: `python/sglang/__init__.py`.
- Frontend language API: `python/sglang/lang/api.py`.
- HTTP server: `python/sglang/srt/entrypoints/http_server.py`.
- Runtime engine: `python/sglang/srt/entrypoints/engine.py`.
- Scheduler process: `python/sglang/srt/managers/scheduler.py`.
- Model runner: `python/sglang/srt/model_executor/model_runner.py`.
- Prefix cache: `python/sglang/srt/mem_cache/radix_cache.py`.

## Kernel Package Entrypoints

`sgl-kernel/` is the native kernel package area:

- `sgl-kernel/csrc/` for native kernel implementations and extension bindings.
- `sgl-kernel/include/` for kernel operation headers.
- `sgl-kernel/python/sgl_kernel/` for Python package bindings.
- `sgl-kernel/benchmark/` for kernel benchmarks.
- `sgl-kernel/tests/` for kernel correctness tests.

## Tests, Benchmarks, Examples

- Runtime tests: `test/`.
- Kernel tests: `sgl-kernel/tests/`.
- Serving and model benchmarks: `benchmark/`.
- Runtime/examples: `examples/runtime/`, `examples/usage/`, `examples/monitoring`,
  `examples/profiler`, and checkpoint engine examples.
- Documentation: `docs/` and `docs_new/`.
