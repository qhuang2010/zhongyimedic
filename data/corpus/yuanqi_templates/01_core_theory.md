# 元气脉法 - 核心理论导入模板

使用本模板将授课资料中的核心理论整理为结构化条目。

---

## 使用说明

1. 复制下方模板
2. 填写各字段内容
3. 保存为 `theory_XXX.yaml` 格式

---

## 模板

```yaml
# 理论条目唯一ID（格式：YQ_THEORY_序号）
theory_id: "YQ_THEORY_001"

# 理论类别
# 选项：元气本体论 / 脉象诊断论 / 辨证论 / 治则论 / 方药论
category: "元气本体论"

# 理论标题
title: ""

# 理论内容（核心观点）
content: |
  在此填写理论的详细内容...
  可以多行书写...

# 关键概念列表
key_concepts:
  - concept_name: "概念1"
    definition: "定义..."
    clinical_significance: "临床意义..."
  
  - concept_name: "概念2"
    definition: "定义..."
    clinical_significance: "临床意义..."

# 与传统理论的关系/区别
relation_to_classical:
  similar_to: ""           # 与哪些传统理论相似
  different_from: ""       # 与哪些传统理论不同
  innovation_points: ""    # 创新之处

# 临床应用要点
clinical_applications:
  - ""
  - ""

# 资料来源
source:
  lecture_name: ""         # 课程名称
  chapter: ""              # 章节
  page_or_time: ""         # 页码或视频时间点

# 相关理论条目ID（用于构建知识图谱）
related_theories: []

# 备注
notes: ""
```

---

## 示例

```yaml
theory_id: "YQ_THEORY_001"
category: "元气本体论"
title: "元气的概念与临床识别"

content: |
  元气是人体生命活动的根本动力，藏于肾，布于三焦...
  在脉诊中，元气的充盛与否可通过沉取脉象的力度判断...

key_concepts:
  - concept_name: "元气"
    definition: "先天之精所化生的生命原动力"
    clinical_significance: "元气充足则脉象沉取有力有神"
  
  - concept_name: "元气虚损"
    definition: "元气不足的病理状态"
    clinical_significance: "表现为脉象沉取无力或无根"

relation_to_classical:
  similar_to: "《难经》元气论"
  different_from: "火神派单纯强调阳虚"
  innovation_points: "强调元气的整体观，而非单一阴阳"

clinical_applications:
  - "通过脉诊判断元气盛衰"
  - "指导扶正固本治疗"

source:
  lecture_name: "元气脉法基础课程"
  chapter: "第一讲"
  page_or_time: ""

related_theories: []
notes: ""
```
