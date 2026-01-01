# 中医脉象九宫格系统 - 数据库设计文档

## 1. 设计理念：关系型骨架 + JSONB 血肉 (Skeleton + Flesh)

为了满足传统业务查询（如按姓名查找、按日期统计）的高效性，同时兼顾 AI 训练数据（非结构化、多维度）的灵活性，本系统采用 PostgreSQL 的混合存储模式。

- **关系型骨架 (Relational Skeleton)**: 将最常用的查询字段（如 `patient_id`, `name`, `visit_date`, `complaint`）提取为标准 SQL 列，支持 B-Tree 索引，确保查询速度。
- **JSONB 血肉 (JSONB Flesh)**: 将完整的病历详情、九宫格脉象数据、以及未来可能扩展的字段（如舌象、音频特征）存储在 `JSONB` 类型的列中。这允许我们直接存储前端传来的复杂对象，并利用 GIN 索引进行全文检索或深层字段查询。

## 2. 实体关系图 (ER Diagram)

### `patients` (患者表)

| 字段名 | 类型 | 说明 | 索引 |
| :--- | :--- | :--- | :--- |
| `id` | SERIAL (PK) | 患者唯一标识 | PK |
| `name` | VARCHAR | 姓名 | B-Tree |
| `gender` | VARCHAR | 性别 | |
| `age` | INTEGER | 年龄 | |
| `info` | JSONB | **[血肉]** 扩展信息（家族史、既往史、生活习惯等） | GIN |
| `created_at` | TIMESTAMP | 创建时间 | |
| `updated_at` | TIMESTAMP | 更新时间 | |

### `medical_records` (诊疗记录表)

| 字段名 | 类型 | 说明 | 索引 |
| :--- | :--- | :--- | :--- |
| `id` | SERIAL (PK) | 记录唯一标识 | PK |
| `patient_id` | INTEGER (FK) | 关联患者ID | FK |
| `visit_date` | TIMESTAMP | 就诊日期 | B-Tree |
| `complaint` | TEXT | **[骨架]** 主诉 (用于快速检索) | |
| `diagnosis` | TEXT | **[骨架]** 诊断 (用于统计分析) | |
| `data` | JSONB | **[血肉]** 完整临床数据 (含九宫格、用药、备注、原始输入) | GIN |
| `created_at` | TIMESTAMP | 创建时间 | |
| `updated_at` | TIMESTAMP | 更新时间 | |

## 3. JSONB 数据结构示例

### `medical_records.data`

```json
{
  "medical_record": {
    "complaint": "失眠多梦，伴有头晕一周",
    "prescription": "酸枣仁汤加减...",
    "note": "患者自述工作压力大，舌红少苔"
  },
  "pulse_grid": {
    "cun-fu": "浮",
    "guan-fu": "弦",
    "chi-fu": "弱",
    "cun-zhong": "...",
    "..."
  },
  "raw_input": {
    "patient_info": { ... },
    "medical_record": { ... },
    "pulse_grid": { ... }
  },
  "ai_metadata": {
    "ocr_confidence": 0.98,
    "model_version": "v1.0"
  }
}
```

## 4. AI 训练支持

这种设计对 AI 训练非常友好：

1.  **数据导出**: 可以直接 `SELECT data FROM medical_records` 导出为 JSONL 格式，直接用于大模型微调 (Fine-tuning)。
2.  **特征提取**: 如果未来需要新的特征（比如“脉象弦细”的病人统计），无需修改表结构，只需查询 JSONB：
    ```sql
    SELECT count(*) FROM medical_records 
    WHERE data->'pulse_grid'->>'guan-fu' LIKE '%弦%';
    ```
3.  **多模态扩展**: `data` 字段可以轻松扩展以包含图像路径、音频嵌入向量等，而不会破坏现有的 SQL 查询逻辑。

## 5. 性能优化

- 在 `medical_records.data` 上创建了 **GIN 索引** (`ix_medical_records_data_gin`)，使得对 JSON 内部字段的查询速度接近于关系型列。
- 常用字段保留在骨架中，避免了每次查询都需要解析 JSON 的开销。
