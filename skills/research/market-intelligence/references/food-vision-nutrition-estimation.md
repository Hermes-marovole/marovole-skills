# AI 拍照识餐：克重与热量估算的实测基线、可用路线与数据陷阱

做餐饮/营养类产品的视觉估重调研时，先读这份基线，别从零搜一遍。下面每个数字都带来源类型；**写进交付物之前回原页核一遍**（论文表格与新闻稿的转写容易串行，尤其是把 MAE 和 MAPE 混着引用）。

## 一、真实误差区间（这是谈判桌，不是排行榜）

| 方案形态 | 克重 / 热量误差 | 来源类型 |
| :--- | :--- | :--- |
| 通用 VLM 单图直出（GPT-4o / Claude / Gemini / ChatGPT-5） | 热量 MAPE **30–36%**；克重 MAE 188g（Gemini 2.5 Pro）／260g（GPT-4o）／330g（Claude 3.7） | 受控喂养称重实测（Purdue ACETADA 806 餐；Nutrients 2025） |
| 商业 App 盲测（MyFitnessPal / Lose It! / Cal AI / Appediet） | 每餐低估 **250–345 kcal**，脂肪每餐漏 **~30g** | NIH/NIDDK 代谢厨房 102 餐盲测 |
| 单图 + 食材/烹调上下文 | 热量 MAPE 降到 **24%**（仅给油盐糖信息）→ **14%**（给到份量与食材）；家常菜可到 **6.9%** | Nutrients 2025 四阶上下文递进实验 |
| 商业 App 单菜实测（Foodvisor / MyFitnessPal） | 克重 MAE 150g、热量 MAE 168 kcal；6 道混合菜 WAPE 26.6%（Foodvisor）/ 59.3%（MyFitnessPal） | Nature Comms Med 2025 表 2；悉尼大学实测 |
| LiDAR / 双摄硬件路线（SNAQ / goFOOD / SnapCalorie） | SNAQ 重量 14.0%（35.1g）、热量 MAPE 12.7%；goFOOD 体积 19% MARE、热量中位 74.9 kcal | 伯尔尼大学医院临床研究；MADiMa 数据集 |
| 论文 SOTA：离散份量分类（DietAI24） | Nutrition5k 克重 **45.1g**、热量 **68.2 kcal**；ASA24 热量 47.7 kcal | Nature Comms Med 2025 |
| 论文 SOTA：单目深度 + 尺度校准（OmniFood8K） | 中餐 8036 样本：质量 PMAE **4.5%**、热量 **8.0%**；Nutrition5k：10.2% / 14.1% | CVPR 2026，已开源 |
| 论文 SOTA：单目深度 + RGB-D 融合（DPF-Nutrition / CalBro） | Nutrition5k 质量 PMAE 10.6%、热量 14.7% | MIT 协议开源权重 + Core ML |
| 几何重建 + 餐具尺寸先验（MDMS / MFP3D） | 体积 MAPE **21%**（vs 直接问 GPT-5.2 的 34%）；MFP3D 体积 MAPE 41% | MetaFood Workshop 2026 / ICPR 2024 |

**读法**：不借助硬件、不借助上下文、纯单图端到端，**20%–35% 是当前物理下限**；想进 10%–16%，必须动下面四条路线之一。看到任何「±1%–5%」的单图产品宣传，按伪造处理（判别方法见 SKILL.md 的伪造学术背书条目）。

## 二、四条真正可落地的路线（按工程成本排序）

1. **离散份量分类 + 权威库查表（DietAI24 范式）** — 改动最小、收益最大
   - 不让模型回归连续克重，而是让它在权威库预定义的标准份量选项里做**多选题**（`1 小碗 28g` / `1 平碗 145g`），再由确定性代码查表折算营养。
   - 实测相对原生 GPT Vision：克重 MAE 89g → 45g，热量 81.8 → 68.2 kcal。
   - 短板：超大份量与纯油脂/酱汁类几乎失效（油脂类命中率接近 0），这两类必须靠显式交互或固定系数补偿。
2. **上下文与时空元数据注入（ACETADA 范式）** — 零成本、无模型改动
   - 注入「用餐时间戳推断的餐次 + 场景类型（居家/餐厅）+ 初筛食材名」，8 款主流模型平均克重 MAE 降 **~53g**、热量 MAE 降 **~76 kcal**。
   - 配合 `Scale-Hint` 指令（强制模型先点名画面里的筷子/小碗/分格盒作尺寸参照）比 CoT 更稳。
3. **单目深度 + 尺度校准（OmniFood8K / DPF-Nutrition）** — 中等成本，需 GPU
   - 单张 RGB → 深度图（Depth Anything V2）→ 频域对齐融合 → 回归质量与热量；关键是**全局尺度校正**，裸深度图直接积分会系统性偏大偏小。
   - 轻量版（V2-Small）单图推理约 0.25s，可进服务端但别进移动端主链路。
4. **3D 重建 + 餐具尺寸先验（MDMS / MFP3D）** — 精度不如上一条但可解释性最好
   - 用 SAM/FoodSAM 分割 + 盘碗筷的标准尺寸先验反推全局尺度；单次重建 10–30s，只适合离线批处理或用户等待页。

**选型判据**：小程序 / 移动端主链路 → 路线 1 + 2（无硬件、无额外推理时延）；有服务端 GPU 且菜品类别集中 → 加 3；做 B 端量体/营养科报告 → 4 可作交叉校验。

## 三、数据集的真值质量（决定能不能拿去微调）

| 数据集 | 真值来源 | 能不能微调克重 |
| :--- | :--- | :--- |
| Nutrition5k（Google, CVPR 2021） | 机械臂 + 电子秤逐项称重 | ✅ 可训练，西餐自助为主 |
| OmniFood8K / NutritionSynth-115K（CVPR 2026） | 生鲜食材逐项称重 + 官方成分表 | ✅ 中餐首选，165 类中餐 |
| MetaFood3D / SimpleFood45（Purdue） | 3D 扫描体积 + 电子秤 | ✅ 但类别少，适合做几何验证 |
| MM-Food-100K（众包 10 万图） | **标签由 GPT-4o 生成，非实测** | ❌ 只可训菜名/食材分类；拿它的 `portion_size` 微调 = 蒸馏另一个模型的估重偏差 |
| 各类商家上传的「AI 识别结果」CSV | 上游模型输出 | ❌ 同上 |

判据：数据卡片里看不到「电子秤 / 实测 / weighed / ground truth」字样，就当模型生成标签处理。

## 四、中式菜品落地的 Do / Don't

- ✅ 把国内膳食调查图谱（如汪之顼《回顾性膳食调查辅助估量食物图谱》：300+ 种食物、每种 5–8 个实测克重阶梯、生熟比、可食部、中式碗杯容量）抽成结构化的「份量选项表」，直接充当路线 1 的权威库——它就是中国版的 FNDDS 份量阶梯。
- ✅ 生熟比与可食部必须在后端折算，不能让模型自己算（一碗熟饭按生米算会直接翻倍，是最伤信任的错误类型）。
- ✅ 隐形烹调油按「烹法 × 油量档」显式叠加固定补偿，而不是留给模型猜——这是商业 App 集体低估 30% 的主因。
- ❌ 不要让 VLM 自由输出「约 200g」再原样入库；食材一旦命中权威库，就用查表值覆盖模型自猜值。
- ❌ 不要把 3D 重建/NeRF 放进同步请求链路（10–30s 会击穿移动端超时预算）。
- ❌ 不要用 LLM 生成标签的数据集训练克重回归。

## 五、关键来源（复用时回原页核对）

- DietAI24 — `nature.com/articles/s43856-025-01159-0`（含表 2 跨模型 MAE 对比）
- OmniFood8K — `arxiv.org/html/2604.12356`，代码 `github.com/yudongjian/OmniFood8K-food`
- DPF-Nutrition / CalBro — `huggingface.co/T0MYYY/dpf-nutrition`（MIT）
- ACETADA 上下文基准 — `arxiv.org/html/2507.07048v1`
- ChatGPT-5 四阶上下文 — `pmc.ncbi.nlm.nih.gov/articles/PMC12655113/`
- 商业 App 盲测（NIH）— `eurekalert.org/news-releases/1136415`
- Nutrition5k — `openaccess.thecvf.com/content/CVPR2021/papers/Thames_Nutrition5k_...pdf`
- 伪造评测站判别 — `calk.me/articles/photo-calorie-counting-accuracy/`（164 条文献注册表）
