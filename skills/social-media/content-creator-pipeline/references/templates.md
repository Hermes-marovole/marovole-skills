# 草稿模板参考

> 这些模板也存在于 Obsidian Vault `05-Outputs/content-creator/templates/` 中。
> 如果更新模板，两处都需更新。

## X 单条帖模板

```markdown
---
platform: x
type: single
lens: [透镜名称]
status: draft
created: YYYY-MM-DD
---

# [钩子：第一句就抓住注意力]

[正文：观点 + 具体细节支撑]

§

[可选：第二层展开或反转]

---

**配图需求**: [描述：暗色科技风/极简白底/截图等]
**建议发布时间**: [08:30 或 21:00]
**标签**: #[]

## 自检
- [ ] 有明确观点
- [ ] 有具体细节
- [ ] 不追热点
- [ ] 有个人色彩
- [ ] 触及≥2个透镜
```

## X Thread 模板

```markdown
---
platform: x
type: thread
lens: [透镜名称]
status: draft
created: YYYY-MM-DD
parts: N
---

# [Thread 标题/钩子]

## Part 1
[开场：制造好奇，承诺价值]

## Part 2
[第一个论点 + 证据]

## Part 3
[第二个论点 + 证据]

## Part 4
[第三个论点 + 证据或反转]

## Part 5
[总结 + 个人立场]

## Part 6 (可选)
[CTA：关注 @marovole]
```

## 公众号模板

```markdown
---
platform: wechat
type: deep-dive
lens: [透镜名称]
status: draft
created: YYYY-MM-DD
target_length: 1500-3000
---

# [标题：有观点的标题，不是"关于XX的思考"]

## 导语
[100字以内。制造好奇，抛出问题，或给出反直觉的开场。]

## [小标题1：现象/问题]
[内容：具体场景，不是抽象论述。用"我"作为视角。]

## [小标题2：分析/拆解]
[内容：用工程审美视角拆解。有数据/截图/对比。]

## [小标题3：判断/观点]
[内容：明确立场。好/坏/聪明/蠢。不骑墙。]

## [小标题4：延伸/跨领域]
[内容：连接到其他领域。游戏设计→产品，硬件→认知，等等。]

## 结尾
[一句话总结 + 个人立场。不鸡汤。]

---
**配图需求**: 1-3张
**发布命令**: `md2wechat publish [file] --mode ai --theme autumn-warm`
```

## 小红书模板

```markdown
---
platform: xiaohongshu
type: visual
lens: [透镜名称]
status: draft
created: YYYY-MM-DD
images: 6
---

# [emoji] [标题：口语化但有观点]

[第一段：直接说结论/推荐/不推荐。200-400字。]
[第二段：具体体验/细节。用"我"视角。]
[第三段：个人判断。好在哪/差在哪。不骑墙。]

§

**配图需求**:
1. [封面图：最吸引眼球的一张]
2-6. [内容图：细节/对比/使用场景]

**标签**: #工程审美 #[] #[]
```