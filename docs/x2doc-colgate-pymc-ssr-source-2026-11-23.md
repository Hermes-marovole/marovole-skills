# 文献对账与附录摘录：PyMC Labs × 高露洁 SSR 合成消费者研究（arXiv:2510.08338v3）

- **原始论文**：*LLMs Reproduce Human Purchase Intent via Semantic Similarity Elicitation of Likert Ratings*（[arXiv:2510.08338](https://arxiv.org/abs/2510.08338)，[HTML 全文 v3](https://arxiv.org/html/2510.08338v3)）
- **提交时间**：2025-10-09 提交 v1，2025-10-13 修订 v2，2025-10-27 修订 v3
- **作者与机构**：共 9 位作者——Benjamin F. Maier、Ulf Aslak、Luca Fiaschi、Nina Rismal、Kemble Fletcher、Christian C. Luhmann、Thomas V. Wiecki（以上 7 位隶属 PyMC Labs），以及 Robbie Dow、Kli Pappas（以上 2 位隶属 Colgate-Palmolive Company, New York, NY, USA；通讯作者为 Benjamin F. Maier 与 Kli Pappas）
- **开源代码仓**：[pymc-labs/semantic-similarity-rating](https://github.com/pymc-labs/semantic-similarity-rating)（2025-08-01 创建，Apache-2.0 协议）
- **爆款传播源帖**：X 博主 Nona（`@Nona_xai`）于 2026-11-22 14:49:34 UTC 发布的西语推文（https://x.com/Nona_xai/status/2124515636827340947）
- **整理归档**：来自翡冷翠（2026-11-23）

---

## 一、 附录 A / C / D / E 关键段落逐字摘录（供长文事实核查对账）

### 1. 数据集与调查设计（Section 3.1 & Appendix A.1）
- `"We analyze 57 consumer research surveys on personal care product concepts conducted by a leading corporation in that market using a digital consumer research platform (see App. A.1). Each survey involved 150–400 unique U.S. participants (N=9,300 in total), with core demographic markers such as age, gender, and location available for most respondents, and income and ethnicity for fewer. Surveys asked participants to evaluate a concept and rate their purchase intent on a 5pt Likert scale. Mean purchase intent is skewed towards positive values and narrowly distributed with mean 4.0 and standard deviation 0.1 across all surveys."`
- `"To a lesser extent, income level is reported, and only nine surveys contain information on consumer ethnicity."`
- `"While surveys prompt participants to score product concepts along various dimensions, we focus on the central question of purchase intent, often phrased as “Based on everything you’ve seen and heard, how likely are you to purchase the product?”. This response was scored on a 5pt Likert scale, requiring participants to select one of the integer numbers i=1,2,3,4,5."`

### 2. 评价指标与重测信度上限模拟（Section 3.3 & Appendix A.3）
- `"For every experiment, we estimate this ceiling by simulating 2,000 test–retest scenarios, splitting each survey into two equally-sized cohorts for each scenario: test and control."`
- `"Repeating this experiment m=2,000 times and taking the average over the respective correlation coefficient, we obtain correlation attainment"`

### 3. 合成消费者采样与三种提问方法（Section 3.4 & Appendix A.4 & Appendix B）
- `"Subsequently, the LLM was prompted with the question “How likely are you to purchase the product?”, and a response was sampled."`
- `"In the following analysis we use n=2 samples, which we found was sufficient to obtain stable results."`
- `"After sampling the response, we prompt the LLM to be a “Likert rating expert” and request it to map the text response it just gave, to the corresponding integer response on a 5pt Likert scale. The same LLM that generates a response is also tasked with rating it, using p_top=1 and T_LLM=0.3."`
- `"For instance, a response may read “I’d probably buy it. I like that it’s easy to use and I can take it with me. Plus, the price isn’t too bad.” Depending on how the scale is defined and who is on the receiving end of this statement, the response most likely would map to a “4” or a “5”."`
- `"When we refer to “image stimulus” in the main text, an image like this, including either both an illustration and the concept description or only a concept description was supplied to an LLM synthetic consumer. When we refer to “text stimulus,” only the text was given to the synthetic consumer. For the latter, the text was previously transcribed from the product concept image using GPT-4o."`
- `"We focused on models by Google and OpenAI; after initial experiments with different models such as “‘gemini-1.5-flash,” “gemini-2.5”, and “o3” we settled on “gemini-2.0-flash” (referred to as “Gem-2f” throughout the text) and “gpt-4o” (“GPT-4o”) for production runs as these models gave the most consistent responses across all experiment types. Experiments were run with parameters p_top=0.9 and temperature T_LLM in {0.5, 1.5} if not noted otherwise."`
- `"In this analysis, we use m=6 sets (see App. C.1)."`
- `"In this study, we exclusively use OpenAI’s “text-embedding-3-small” model. Tests with “text-embedding-3-large” left the results virtually unchanged."`
- `"Note that subtracting the minimum similarity over the reference statement set is a way to adjust for potential low variance in the similarity scores. In practice, we observe that within the space of all embeddable language, the numerical difference between extremes like “It’s very unlikely that I’d buy it.” and “It’s very likely that I’d buy it.” is numerically small, and so if we do not subtract the minimum similarity, the resulting pmf will be almost entirely flat."`

### 4. 锚点语句设计（Appendix C.1）
- `"To map free-text responses onto a 5pt Likert scale, we constructed six sets of anchor statements, five statements in each set (one for each Likert category 1 through 5). These anchors serve as semantic prototypes against which model-generated responses are compared in embedding space."`
- `"The anchors were designed to be short, generic, and domain-independent, such that they could plausibly apply to any consumer product concept. Their purpose is not to capture the nuances of any specific product, but to provide a reference gradient of intent from “purchase improbable” to “purchase probable.”"`

### 5. 有监督机器学习对比基线（Section 4.4 & Appendix D）
- `"We considered the complete set of 57 consumer concept surveys used in the main study. For each of 300 iterations, we randomly split the surveys in half. One half (28 surveys) was used for training, the other half (29 surveys) for testing."`
- `"Across 300 iterations, LightGBM achieved a correlation attainment of rho=(64.6±1.0)%, substantially below both follow-up Likert ratings (83.2±0.7%) and SSR-based elicitation with GPT-4o at T_LLM=0.5 and image stimulus (88.3±0.7%). For distributional similarity, LightGBM (K^xy=0.797±0.002) outperformed follow-up Likert ratings (0.716±0.001) but was surpassed by SSR (0.883±0.001)."`

### 6. 定性反馈与真假消费者评语对比（Appendix E）
- `"While the real surveys focused on ratings on a Likert scale, they also asked people to write free text as responses to the questions “What did/didn’t you like about the concept?” The replies to these open questions are lacking depth and only seldom provide important feedback. Typically, they are rather short like “It’s good”, or just repeat information contained in the concept like “Not much, just the steps and how it tells you what it was for.”"`
- `"For instance, one synthetic consumer wrote: “The ease of use and […] safety are appealing, but I’d want to know more about its effectiveness and any potential side effects.” Another responded: “The ease of use and the promise of no […] sensitivity are appealing. Plus, it’s from a trusted brand.”"`
- `"For a less positively received concept, GPT-4o synthetic consumers responded “It seems a bit too high-end for my needs and budget” and “[These body parts] don’t usually bother me, so I don’t think I need it” while two based on Gem-2f wrote e.g., “Seems kinda bougie for [this kind of product]” and “Sounds expensive, and I’m not sure I buy all that ‘microbiome’ talk. I’ll stick with what I know”, respectively."`
- `"Additionally, synthetic consumers seem to suffer less from a positivity bias, as demonstrated by the wider spread of mean purchase intent measured in the previous section as well as confirmed by the qualitative analysis of synthetic responses."`

### 7. 讨论与局限性（Section 5 Discussion and Conclusion 完整摘录）
- `"While promising, the method is not without limitations. SSR relies on carefully designed reference statements, and our results show that different anchor sets can lead to slightly different mappings. Averaging across sets mitigates this issue, but future work could optimize reference statements iteratively, or even generate them dynamically with LLMs to maximize alignment with human data. Note that the reference sets created herein were manually optimized for the 57 surveys subject to this study, which means it remains elusive how well they would perform for other surveys. Another limitation concerns demographics: although LLMs captured some demographic patterns (e.g., age and income) quite well, others (e.g., gender, region, ethnicity) were not consistently replicated. This suggests that while persona conditioning does influence synthetic responses, it cannot yet be treated as a reliable proxy for all subpopulations. Researchers must therefore use caution when interpreting subgroup analyses from synthetic panels."`
- `"More fundamentally, the usefulness of SSR is bounded by the knowledge domains represented in the LLM’s training data. LLMs are known to hallucinate when asked about unfamiliar topics, and SSR does not eliminate this risk. The reason our approach succeeds in oral care products, and even reflects demographic conditioning, is likely that the model has been exposed to abundant human discussions of these categories in its training corpus (e.g., online forums and consumer reviews). For domains where such background knowledge is sparse or absent, SSR will not conjure valid consumer preferences. Thus, it is important not to view synthetic surveys as universally reliable, but rather as tools whose validity depends on the alignment between training data and the survey domain."`
- `"Finally, while synthetic consumers reproduce human-like distributions and rankings, they cannot fully capture the real-world contingencies of purchasing behavior, such as budget constraints, cultural context, or marketing exposure."`
- `"In summary, by combining interpretability, statistical reliability, and qualitative richness, SSR addresses many of the challenges that have constrained the use of LLMs as synthetic survey respondents. While not a wholesale replacement for human research, SSR establishes a credible framework for augmenting and accelerating consumer insight generation."`
- `"The original manuscript was written by all authors, ChatGPT-5 was subsequently used in all sections to reformulate and condense the text."`

---

## 二、 Table 1 全量实验指标摘录（arXiv:2510.08338v3 Appendix E；注：原表列头 `SSR` 对应语义相似度评分 SSR，`Lik.` 对应文本诱发后的专家追问李克特打分 FLR，Direct 行的 `Lik.` 对应直接李克特打分 DLR）

| Elicit. | Dem. | Model | Stim. | T_LLM | Best Sigma | rho (%) SSR | rho (%) Lik. | K^xy SSR | K^xy Lik. | R^xy SSR | R^xy Lik. | C^xy SSR | C^xy Lik. | E[PI_s]±std SSR | E[PI_s]±std Lik. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Direct | Full | GPT-4o | Text | 1.5 | — | — | 88.5 | — | 0.37 | — | 0.717 | — | 0.39 | — | 2.95 ± 0.44 |
| Direct | Full | GPT-4o | Text | 0.5 | — | — | 89.6 | — | 0.36 | — | 0.720 | — | 0.38 | — | 2.96 ± 0.45 |
| Direct | Full | GPT-4o | Image | 1.5 | — | — | 78.7 | — | 0.29 | — | 0.648 | — | 0.29 | — | 2.97 ± 0.16 |
| Direct | Full | GPT-4o | Image | 0.5 | — | — | 81.7 | — | 0.26 | — | 0.661 | — | 0.26 | — | 2.96 ± 0.11 |
| Direct | Full | Gem-2f | Text | 1.5 | — | — | 68.4 | — | 0.46 | — | 0.546 | — | 0.48 | — | 3.28 ± 0.50 |
| Direct | Full | Gem-2f | Text | 0.5 | — | — | 67.5 | — | 0.45 | — | 0.541 | — | 0.47 | — | 3.28 ± 0.50 |
| Direct | Full | Gem-2f | Image | 1.5 | — | — | 82.5 | — | 0.41 | — | 0.660 | — | 0.41 | — | 3.17 ± 0.40 |
| Direct | Full | Gem-2f | Image | 0.5 | — | — | 80.2 | — | 0.39 | — | 0.640 | — | 0.40 | — | 3.17 ± 0.40 |
| Textual | Full | GPT-4o | Text | 1.5 | 4 | 85.0 | — | 0.85 | — | 0.691 | — | 0.94 | — | 3.75 ± 0.40 | — |
| Textual | Full | GPT-4o | Text | 0.5 | 4 | 83.1 | — | 0.84 | — | 0.680 | — | 0.92 | — | 3.71 ± 0.45 | — |
| Textual | Full | GPT-4o | Text | 0.5 | avg. | 82.5 | 69.2 | 0.84 | 0.64 | 0.675 | 0.562 | 0.94 | 0.70 | 3.63 ± 0.42 | 3.39 ± 0.79 |
| Textual | Full | GPT-4o | Image | 0.5 | 1 | 91.9 | — | 0.82 | — | 0.740 | — | 0.93 | — | 3.67 ± 0.36 | — |
| Textual | Full | GPT-4o | Image | 0.5 | avg. | 90.2 | 84.7 | 0.88 | 0.72 | 0.724 | 0.687 | 0.96 | 0.80 | 3.77 ± 0.31 | 3.67 ± 0.55 |
| Textual | Full | Gem-2f | Text | 1.5 | 3 | 76.3 | — | 0.81 | — | 0.611 | — | 0.92 | — | 3.56 ± 0.40 | — |
| Textual | Full | Gem-2f | Text | 0.5 | 3 | 72.7 | — | 0.81 | — | 0.581 | — | 0.91 | — | 3.56 ± 0.42 | — |
| Textual | Full | Gem-2f | Text | 0.5 | avg. | 73.0 | 73.5 | 0.80 | 0.62 | 0.583 | 0.589 | 0.91 | 0.69 | 3.52 ± 0.45 | 3.57 ± 0.86 |
| Textual | Full | Gem-2f | Image | 0.5 | 5 | 92.4 | — | 0.82 | — | 0.737 | — | 0.92 | — | 3.64 ± 0.45 | — |
| Textual | Full | Gem-2f | Image | 0.5 | avg. | 90.6 | 92.1 | 0.80 | 0.59 | 0.720 | 0.736 | 0.91 | 0.64 | 3.51 ± 0.42 | 3.33 ± 0.75 |
| Textual | None | GPT-4o | Text | 1.5 | 4 | 50.1 | — | 0.92 | — | 0.409 | — | 0.98 | — | 4.05 ± 0.12 | — |
| Textual | None | GPT-4o | Text | 0.5 | 4 | 45.3 | — | 0.91 | — | 0.390 | — | 0.97 | — | 4.09 ± 0.16 | — |
| Textual | None | GPT-4o | Text | 0.5 | avg. | 47.4 | 41.2 | 0.91 | 0.57 | 0.408 | 0.324 | 0.98 | 0.77 | 3.92 ± 0.14 | 4.61 ± 0.51 |
| Textual | None | Gem-2f | Text | 1.5 | 3 | 60.5 | — | 0.87 | — | 0.481 | — | 0.95 | — | 3.85 ± 0.24 | — |
| Textual | None | Gem-2f | Text | 0.5 | 3 | 49.5 | — | 0.87 | — | 0.411 | — | 0.95 | — | 3.90 ± 0.26 | — |
| Textual | None | Gem-2f | Text | 0.5 | avg. | 57.4 | 58.0 | 0.91 | 0.62 | 0.481 | 0.480 | 0.97 | 0.75 | 3.90 ± 0.26 | 4.26 ± 0.58 |
| Textual | None | Gem-2f | Image | 0.5 | 4 | 50.1 | — | 0.91 | — | 0.414 | — | 0.98 | — | 4.09 ± 0.07 | — |
| Textual | None | Gem-2f | Image | 0.5 | avg. | 15.5 | 64.3 | 0.91 | 0.67 | 0.143 | 0.530 | 0.98 | 0.78 | 3.94 ± 0.08 | 4.25 ± 0.34 |

*来自翡冷翠*
