# 元气脉法 - 脉象模式导入模板

使用本模板将授课资料中的脉象识别规则整理为结构化条目。

---

## 模板

```yaml
# 脉象模式唯一ID
pulse_pattern_id: "YQ_PULSE_001"

# 脉象名称（元气脉法特有命名）
pattern_name: ""

# 脉象特征描述
characteristics:
  # 九宫格各位置特征
  left_cun:
    fu: ""      # 浮取
    zhong: ""   # 中取
    chen: ""    # 沉取
  left_guan:
    fu: ""
    zhong: ""
    chen: ""
  left_chi:
    fu: ""
    zhong: ""
    chen: ""
  right_cun:
    fu: ""
    zhong: ""
    chen: ""
  right_guan:
    fu: ""
    zhong: ""
    chen: ""
  right_chi:
    fu: ""
    zhong: ""
    chen: ""
    
  # 总体特征描述
  overall_description: ""
  
  # 关键识别点（用于AI学习）
  key_features:
    - ""
    - ""

# 元气脉法视角下的诊断意义
diagnostic_meaning:
  yuanqi_state: ""        # 元气状态判断
  pathomechanism: ""      # 病机分析
  organ_affected: []      # 涉及脏腑

# 与其他脉象的鉴别要点
differentiation:
  - compare_with: ""
    key_difference: ""

# 治疗方向
treatment_direction:
  principle: ""           # 治则
  methods: []             # 具体治法

# 常见配合的症状体征
associated_symptoms: []

# 资料来源
source:
  lecture_name: ""
  chapter: ""

# 备注
notes: ""
```

---

## 示例

```yaml
pulse_pattern_id: "YQ_PULSE_001"
pattern_name: "元气根虚脉"

characteristics:
  left_cun:
    fu: "可触及"
    zhong: "有力"
    chen: "无力或空"
  left_guan:
    fu: "正常"
    zhong: "中等"
    chen: "弱"
  left_chi:
    fu: "微弱"
    zhong: "弱"
    chen: "空虚无根"
  right_cun:
    fu: "正常"
    zhong: "中等"
    chen: "弱"
  right_guan:
    fu: "正常"
    zhong: "中等"
    chen: "弱"
  right_chi:
    fu: "微弱"
    zhong: "弱"
    chen: "空虚无根"
    
  overall_description: "浮中取可，沉取无力，尤以两尺沉取空虚为著"
  
  key_features:
    - "尺部沉取无根"
    - "浮中尚可、沉取空"
    - "重按欲绝"

diagnostic_meaning:
  yuanqi_state: "元气虚损，下元不固"
  pathomechanism: "先天真阳亏虚，命门火衰"
  organ_affected: ["肾", "命门"]

differentiation:
  - compare_with: "普通虚脉"
    key_difference: "虚脉全部无力，元气根虚脉浮中尚可、独沉取无根"
  - compare_with: "芤脉"
    key_difference: "芤脉中空如葱管，元气根虚脉是沉取无根但不空"

treatment_direction:
  principle: "培补元气，固护根本"
  methods: ["温补肾阳", "填精益髓", "引火归元"]

associated_symptoms:
  - "腰膝酸软"
  - "畏寒肢冷"
  - "精神萎靡"
  - "夜尿频多"

source:
  lecture_name: "元气脉法核心课程"
  chapter: "脉象识别篇"

notes: "此为元气脉法最核心的脉象识别要点"
```
