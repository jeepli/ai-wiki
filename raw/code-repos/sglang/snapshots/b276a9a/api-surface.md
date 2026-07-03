---
repo: sglang
commit: b276a9acee8a02159a9a8d839da8a7b4dd898b58
source_version: b276a9a
document: api-surface.md
status: source-backed
---

# Api Surface

Source snapshot: `sglang` commit
`b276a9acee8a02159a9a8d839da8a7b4dd898b58`.

## Public Python APIs

`python/sglang/__init__.py` exports the main public API:

- frontend/runtime objects: `Engine`, `Runtime`, `RuntimeEndpoint`
- generation primitives: `function`, `gen`, `gen_int`, `gen_string`, `select`
- role helpers: `system`, `user`, `assistant` plus begin/end variants
- media helpers: `image`, `video`
- runtime utilities: `flush_cache`, `get_server_info`, `set_default_backend`,
  `separate_reasoning`
- scoring/choice helpers: `greedy_token_selection`,
  `token_length_normalized`, `unconditional_likelihood_normalized`
- backend wrappers: `OpenAI`, `Anthropic`, `LiteLLM`, `VertexAI`, `Crusoe`
- runtime engine/config: lazy `ServerArgs` and `Engine`

Citation: `sglang@b276a9a:python/sglang/__init__.py`.

## CLI and Server APIs

- Console script: `sglang = sglang.cli.main:main`.
- Utility script: `killall_sglang = sglang.cli.killall:main`.
- CLI subcommands: `serve`, `generate`, `version`
  (`sglang@b276a9a:python/pyproject.toml`,
  `sglang@b276a9a:python/sglang/cli/main.py`).
- SRT HTTP server: `python/sglang/srt/entrypoints/http_server.py`.
- Engine entrypoints: `python/sglang/srt/entrypoints/engine.py`,
  `http_server_engine.py`, `grpc_server.py`, and `grpc_bridge.py`.

## Runtime Internal APIs for Code Exploration

Use these symbols when answering implementation questions:

- Scheduler: `python/sglang/srt/managers/scheduler.py#Scheduler`.
- Batch container: `python/sglang/srt/managers/schedule_batch.py#ScheduleBatch`.
- Scheduling policy: `python/sglang/srt/managers/schedule_policy.py`.
- Tokenizer manager: `python/sglang/srt/managers/tokenizer_manager.py`.
- Detokenizer manager: `python/sglang/srt/managers/detokenizer_manager.py`.
- Prefix cache: `python/sglang/srt/mem_cache/radix_cache.py#RadixCache`.
- Model runner: `python/sglang/srt/model_executor/model_runner.py#ModelRunner`.
- KV cache mixin: `python/sglang/srt/model_executor/model_runner_kv_cache_mixin.py#ModelRunnerKVCacheMixin`.

## Kernel APIs

`sgl-kernel` exposes native and Python kernel surfaces. High-signal files:

- `sgl-kernel/include/sgl_kernel_ops.h`
- `sgl-kernel/include/sgl_flash_kernel_ops.h`
- `sgl-kernel/csrc/common_extension.cc`
- `sgl-kernel/csrc/flash_extension.cc`
- `sgl-kernel/csrc/flashmla_extension.cc`
- `sgl-kernel/python/sgl_kernel/`
