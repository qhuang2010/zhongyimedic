# 元气脉法 - 临床病例导入模板

使用本模板录入临床病例，用于AI训练和验证。

---

## 病例录入模板

```yaml
# 病例基本信息
case_id: "CASE_001"
record_date: "2026-01-01"

# 患者信息（脱敏）
patient:
  gender: ""              # 男/女
  age: 0
  occupation: ""
  
# 主诉
chief_complaint: ""

# 现病史
present_illness: ""

# 脉象记录（九宫格）
pulse_grid:
  # 左手
  left_cun:
    fu: ""
    zhong: ""
    chen: ""
  left_guan:
    fu: ""
    zhong: ""
    chen: ""
  left_chi:
    fu: ""
    zhong: ""
    chen: ""
  # 右手
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
  # 总评
  overall: ""

# 其他四诊信息
other_diagnosis:
  inspection: ""          # 望诊
  listening: ""           # 闻诊
  inquiry: []             # 问诊要点（列表）

# 元气脉法诊断
yuanqi_diagnosis:
  yuanqi_state: ""        # 元气状态判断
  pulse_pattern: ""       # 识别的脉象模式
  syndrome: ""            # 辨证结论
  pathomechanism: ""      # 病机分析

# 治疗方案
treatment:
  principle: ""           # 治则
  formula_name: ""        # 方名
  herbs:
    - name: ""
      dosage: ""
    - name: ""
      dosage: ""
  modifications: ""       # 加减说明

# 疗效记录（如有）
outcome:
  follow_up_date: ""
  improvement: ""         # 好转/无效/加重
  pulse_change: ""        # 脉象变化
  notes: ""

# 元数据
metadata:
  recorded_by: ""
  verified_by: ""
  data_quality: ""        # 优/良/一般
```

---

## 示例病例

```yaml
case_id: "CASE_001"
record_date: "2026-01-10"

patient:
  gender: "男"
  age: 52
  occupation: "教师"
  
chief_complaint: "腰膝酸软、畏寒乏力半年"

present_illness: |
  患者半年前开始出现腰膝酸软，畏寒怕冷，尤以下肢为甚。
  伴有精神萎靡，夜尿频多（每晚3-4次），大便溏薄。
  曾服用六味地黄丸无明显效果。

pulse_grid:
  left_cun:
    fu: "可"
    zhong: "中等"
    chen: "弱"
  left_guan:
    fu: "弦"
    zhong: "中等"
    chen: "弱"
  left_chi:
    fu: "弱"
    zhong: "弱"
    chen: "空虚"
  right_cun:
    fu: "可"
    zhong: "中等"
    chen: "弱"
  right_guan:
    fu: "中等"
    zhong: "中等"
    chen: "弱"
  right_chi:
    fu: "弱"
    zhong: "弱"
    chen: "空虚"
  overall: "脉浮中可取，沉取无力，尤以两尺沉取空虚为著"

other_diagnosis:
  inspection: "面色晦暗，精神萎靡，舌淡胖边有齿痕，苔白"
  listening: "声低气怯"
  inquiry:
    - "畏寒肢冷，以下肢为甚"
    - "夜尿频多，每晚3-4次"
    - "大便溏薄，每日1-2次"
    - "腰膝酸软，久站加重"
    - "睡眠尚可，但晨起乏力"

yuanqi_diagnosis:
  yuanqi_state: "元气虚损，下元不固"
  pulse_pattern: "元气根虚脉"
  syndrome: "肾阳虚衰，命门火弱"
  pathomechanism: |
    两尺沉取空虚，示肾中元气亏虚。
    浮中尚可而沉取无根，说明病在下焦根本，而非表浅之虚。
    此为先天真阳不足，命门火衰，温煦失职。

treatment:
  principle: "温补元阳，培固根本"
  formula_name: "附子理中汤加减"
  herbs:
    - name: "制附子"
      dosage: "15g（先煎）"
    - name: "干姜"
      dosage: "10g"
    - name: "党参"
      dosage: "15g"
    - name: "白术"
      dosage: "15g"
    - name: "炙甘草"
      dosage: "6g"
    - name: "肉桂"
      dosage: "6g（后下）"
    - name: "枸杞子"
      dosage: "15g"
    - name: "杜仲"
      dosage: "15g"
  modifications: "因腰膝酸软加杜仲、枸杞补肾壮腰"

outcome:
  follow_up_date: "2026-01-24"
  improvement: "好转"
  pulse_change: "两尺沉取较前有力，但仍偏弱"
  notes: "畏寒减轻，夜尿减至每晚1-2次，精神好转"

metadata:
  recorded_by: "医师A"
  verified_by: "主任医师B"
  data_quality: "优"
```

---

## 批量导入说明

1. 将多个病例保存为 `case_XXX.yaml` 文件
2. 放入 `data/corpus/clinical_cases/` 目录
3. 运行导入脚本：`python scripts/import_cases.py`
