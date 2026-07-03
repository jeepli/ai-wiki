---
repo: vllm
commit: 8357226f4f1b92aa2139ebc482ca71012f02016b
source_version: 8357226
document: api-surface.md
status: source-backed
---

# Api Surface

Source snapshot: `vllm` commit
`8357226f4f1b92aa2139ebc482ca71012f02016b`.

## Python Package Surface

`vllm/__init__.py` lazily exports the main public API:

- `LLM`
- `EngineArgs`, `AsyncEngineArgs`
- `LLMEngine`, `AsyncLLMEngine`
- `SamplingParams`, `PoolingParams`
- prompt types: `PromptType`, `TextPrompt`, `TokensPrompt`
- output types: `RequestOutput`, `CompletionOutput`, pooling/embedding/
  classification/scoring outputs
- `ModelRegistry`
- `initialize_ray_cluster`

Citation: `vllm@8357226:vllm/__init__.py`.

## CLI and Server Entrypoints

- Console script: `vllm = vllm.entrypoints.cli.main:main`
  (`vllm@8357226:pyproject.toml`).
- Offline inference: `vllm/entrypoints/llm.py#LLM`.
- OpenAI-compatible server: `vllm/entrypoints/openai/api_server.py`.
- API app construction: `build_app(...)`.
- Engine-client construction: `build_async_engine_client(...)` and
  `build_async_engine_client_from_engine_args(...)`.

## Runtime Extension Points

- LoRA resolver plugins are declared through `project.entry-points."vllm.general_plugins"`
  in `pyproject.toml`.
- Attention backends live under `vllm/v1/attention/backends/`; this includes
  files for FlashAttention, FlashInfer, Triton, ROCm/AITER, CPU, FlexAttention,
  and specialized attention variants.
- KV transfer/offload connectors are referenced by `Scheduler` via
  `KVConnectorFactory` and related V1 connector types
  (`vllm@8357226:vllm/v1/core/sched/scheduler.py`).
- Metrics/logging plugins are loaded by the V1 async engine through
  `load_stat_logger_plugin_factories`
  (`vllm@8357226:vllm/v1/engine/async_llm.py#AsyncLLM`).

## Internal APIs to Treat Carefully

`EngineCore`, `Scheduler`, `KVCacheManager`, and `GPUModelRunner` are the right
symbols for code exploration, but they are internal runtime components rather
than stable user APIs:

- `vllm/v1/engine/core.py#EngineCore`
- `vllm/v1/core/sched/scheduler.py#Scheduler`
- `vllm/v1/core/kv_cache_manager.py#KVCacheManager`
- `vllm/v1/worker/gpu_model_runner.py#GPUModelRunner`
