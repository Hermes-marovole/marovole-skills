# LLM Leaderboard Source Registry

Use this reference when building a public LLM ranking, composite leaderboard, model comparison index, or model-selection report. It captures authoritative leaderboard sources discovered during research for 翡冷翠's “LLM Reality Rank / 大模型真实使用价值榜”.

## P0: first-version must include

| Source | URL | Category | Use in composite ranking | Notes |
|---|---|---|---|---|
| LMArena / Chatbot Arena | https://lmarena.ai/leaderboard/ | General preference | General UX, dialogue, writing/user preference | High public recognition; subjective Elo, style-sensitive. |
| Artificial Analysis LLM Leaderboard | https://artificialanalysis.ai/leaderboards/models | General + practicality | Intelligence, price, speed, latency, context, API availability | Core source for “real usage value” practicality multiplier. |
| LiveBench | https://livebench.ai/ | General, reasoning, coding | Objective ability, freshness, anti-contamination | Good high-weight objective source. |
| OpenCompass LLM Leaderboard | https://rank.opencompass.org.cn/leaderboard-llm-v2 | General + Chinese | Chinese-friendly comprehensive evaluation | Useful to offset western benchmark bias. |
| Hugging Face Open LLM Leaderboard | https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard | Open-weight LLMs | Open/open-weight model subrank | Do not overweight; open leaderboard history includes contamination/gaming concerns. |
| Stanford HELM / HELM Lite | https://crfm.stanford.edu/helm/ and https://crfm.stanford.edu/helm/lite/latest/ | Academic holistic evaluation | Robustness, calibration, fairness, safety, efficiency | High academic credibility; slower updates. |
| SWE-bench | https://www.swebench.com/ | Coding | AI Coding / agentic software engineering | Prefer SWE-bench Verified. |
| Aider Leaderboards | https://aider.chat/docs/leaderboards/ | Coding | Code editing, practical AI coding, cost-aware coding | Strong fit for AI Coding personal brand; high weight for coding subrank. |
| LiveCodeBench | https://livecodebench.github.io/leaderboard.html | Coding | Algorithmic/code generation ability | More current than HumanEval/MBPP. |
| SuperCLUE | https://superclueai.com/ | Chinese | Chinese capability subrank | Must-have for Chinese LLM evaluation. |
| C-Eval | https://cevalbenchmark.com/static/leaderboard.html | Chinese | Chinese knowledge/exam-style capability | Site may have certificate issues; use mirror/raw data if needed. |
| CMMLU | https://github.com/haonan-li/CMMLU | Chinese | Chinese multi-task language understanding | Distinguish third-party data vs vendor-reported scores. |
| MMMU | https://mmmu-benchmark.github.io/ | Multimodal | Vision-language reasoning | High-weight multimodal source. |
| MathVista | https://mathvista.github.io/ | Multimodal reasoning | Visual math reasoning | Good multimodal submetric. |
| GAIA | https://gaia-benchmark-leaderboard.hf.space/ | Agent | Research assistant / tool-using agent tasks | High-weight for Agent subrank. |
| Berkeley Function Calling / Gorilla | https://gorilla.cs.berkeley.edu/leaderboard.html | Tool use | Function calling/API/tool-use ability | Core Agent practicality signal. |
| OpenRouter Rankings | https://openrouter.ai/rankings | Adoption/practicality | Usage/adoption/ecosystem signal | Not an ability score; use as popularity/adoption multiplier only. |

## P1: useful in first version, but lower weight or subrank-only

| Source | URL | Category | Use | Notes |
|---|---|---|---|---|
| Vellum LLM Leaderboard | https://www.vellum.ai/llm-leaderboard | App/developer view | Application-builder reference | Auxiliary source. |
| Scale SWE-bench Leaderboard | https://scale.com/leaderboard/swe-bench | Coding | SWE-bench productized tracker | Handle redirects. |
| BigCodeBench | https://bigcode-bench.github.io/ | Coding | Complex code tasks | More modern than HumanEval. |
| EvalPlus | https://evalplus.github.io/leaderboard.html | Coding | HumanEval+/MBPP+ | Keep lower weight; traditional code benchmarks are aging. |
| Humanity’s Last Exam | https://scale.com/research/humanitys-last-exam | Hard reasoning | Expert-level knowledge/reasoning | Useful for frontier-model differentiation. |
| ARC-AGI / ARC Prize | https://arcprize.org/leaderboard and https://agi.safe.ai/ | Abstract reasoning | AGI/reasoning signal | Low total-rank weight; not everyday utility. |
| BAAI Open Chinese LLM Leaderboard | https://huggingface.co/spaces/BAAI/open_cn_llm_leaderboard | Chinese open models | Chinese open-weight subrank | Good supplement for domestic/open models. |
| Open Multilingual LLM Leaderboard | https://huggingface.co/spaces/PetruZetta/open_multilingual_llm_leaderboard | Multilingual | Multilingual capability | Useful for global audience; lower than Chinese-specific sources for Chinese rank. |
| OpenCompass Open VLM Leaderboard | https://huggingface.co/spaces/opencompass/open_vlm_leaderboard | Multimodal open VLMs | Open VLM subrank | Use in multimodal subrank. |
| OCRBench / MultimodalOCR | https://github.com/Yuliang-Liu/MultimodalOCR | OCR/document understanding | Practical document/screenshot/PDF utility | Strong real-use signal despite being narrower. |
| WebArena | https://webarena.dev/ | Web agent | Browser/task-completion agent | Agent subrank only. |
| OSWorld | https://os-world.github.io/ | Computer-use agent | Real computer environment tasks | Good for computer-use agents. |
| MTEB | https://huggingface.co/spaces/mteb/leaderboard and https://mteb-leaderboard.hf.space/ | Embeddings/RAG | Embedding/RAG component ranking | Not a generative LLM score; separate component rank. |

## P2: observation / later expansion

- Terminal-Bench: https://terminal-bench.com/ — CLI/terminal agent tasks; may have TLS access issues in some tooling.
- SimpleBench: https://huggingface.co/spaces/simple-bench/simple-bench — common-sense/“simple but hard for models” tasks; HF access may be restricted.
- ZebraLogic: https://huggingface.co/spaces/allenai/ZebraLogic — logic reasoning.
- SEA-HELM: https://leaderboard.sea-lion.ai/ — Southeast Asian language evaluation.
- OpenCompass Video VLM Leaderboard: https://huggingface.co/spaces/opencompass/openvlm_video_leaderboard — video model subrank.
- Video-MME: common project entry https://video-mme.github.io/ — verify current canonical URL before relying on it.
- AlpacaEval: https://tatsu-lab.github.io/alpaca_eval/ — instruction following/preference; judge-model bias risk.
- RewardBench: https://huggingface.co/spaces/allenai/reward-bench — reward/preference model evaluation.
- WildBench: https://huggingface.co/spaces/allenai/WildBench — open-ended real-world tasks.
- τ-bench/tool-agent benchmarks — verify canonical source before adding.

## Practical project scaffold for a composite leaderboard

When the task progresses from research into building a maintainable public leaderboard, create three layers instead of jumping directly to a webpage:

1. Docs layer
   - `docs/llm-reality-rank-source-registry.md`
   - `docs/llm-reality-rank-scoring-methodology.md`
   - `docs/llm-reality-rank-model-normalization.md`
   - `docs/llm-reality-rank-scoring-pipeline-plan.md`

2. Data layer
   - `data/llm-reality-rank/sources.yaml`: machine-readable source registry with P0/P1/P2, URLs, categories, metric types, trust/risk, ingestion method.
   - `data/llm-reality-rank/models.yaml`: canonical model registry with `canonical_id`, aliases, provider, family, variant, version, modality, tool support, confidence.
   - `data/llm-reality-rank/raw_rankings.csv`: raw observed leaderboard rows; preserve original model name, source, metric, rank/score, dates, trust/risk, notes.

3. Pipeline layer
   - `scripts/llm-reality-rank/validate_data.py`: validate YAML/CSV parse and source/model cross-references.
   - `scripts/llm-reality-rank/normalize_scores.py`: convert Elo/rank/accuracy/price/speed to 0-100 normalized rows.
   - `scripts/llm-reality-rank/aggregate_scores.py`: aggregate category scores into overall/subrank outputs.
   - `outputs/llm-reality-rank/model_scores.csv` and `.md`: generated tables for article/static-site use.

This preserves traceability and lets the public article, static webpage, and future automation all use the same data spine.

### Canonical model ID pattern

Use stable IDs of the form:

```text
provider_slug/model_family-or-name@version_or_date
```

Examples:

- `openai/gpt-4o@2024-08-06`
- `anthropic/claude-3.5-sonnet@2024-10-22`
- `google/gemini-2.5-pro@unknown`
- `deepseek/deepseek-v3@2025-03-24`
- `meta/llama-3.1-405b-instruct@2024-07-23`

Rules:

- Never merge mini/full/pro/flash/opus/sonnet/base/instruct/reasoning variants.
- Use `@unknown` when the version is unclear, but lower confidence and avoid final-public scoring until verified.
- Preserve raw model names in `raw_rankings.csv` even after mapping to `canonical_id`.

### Minimal raw ranking schema

```csv
source_id,source_name,source_priority,category_primary,metric_name,metric_type,model_name_raw,canonical_id,provider,rank_raw,score_raw,score_unit,score_higher_is_better,date_published,date_observed,source_url,evaluation_independence,source_trust,contamination_risk,freshness_weight,notes
```

Validate that every `source_id` exists in `sources.yaml` and every `canonical_id` exists in `models.yaml` before calculating scores.

## Composite-ranking guidance

For a public “LLM Reality Rank”, group sources into five signal classes:

1. Capability: LMArena, LiveBench, HELM, OpenCompass, HLE.
2. Specialized ability: SWE-bench, Aider, LiveCodeBench, MMMU, SuperCLUE, GAIA.
3. Practicality: Artificial Analysis price/speed/latency/context/API availability.
4. Ecosystem/adoption: OpenRouter rankings, tool support, function calling, common dev-tool availability.
5. Confidence: source count, recency, independent-vs-vendor evaluation, contamination risk.

Avoid claiming a single “absolute intelligence” score. Prefer “综合使用价值 / real usage value”. Explain that model ranking is scenario-dependent and provide subranks: overall value, coding, Chinese, cost-efficiency, agent/tool-use, multimodal, open-weight.

## Source metadata schema

```yaml
source_id:
  name:
  url:
  organization:
  category: [general, coding, chinese, multimodal, agent, cost_speed, adoption]
  metric_type: [elo, accuracy, pass_rate, win_rate, rank, price, latency, usage]
  update_frequency:
  source_trust: high|medium|low
  contamination_risk: high|medium|low
  recommended_weight:
  notes:
```
