-- 初始化数据库脚本
-- 运行方式: psql -U postgres -d tcm_pulse_db -f scripts/init_db.sql

-- 1. 创建患者表
CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    gender VARCHAR(10),
    age INTEGER,
    info JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_patients_name ON patients(name);
CREATE INDEX IF NOT EXISTS idx_patients_info_gin ON patients USING GIN (info);

-- 2. 创建诊疗记录表
CREATE TABLE IF NOT EXISTS medical_records (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    visit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    complaint TEXT, -- 骨架字段：主诉
    diagnosis TEXT, -- 骨架字段：诊断
    data JSONB NOT NULL DEFAULT '{}'::jsonb, -- 血肉字段：完整数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_records_visit_date ON medical_records(visit_date);
CREATE INDEX IF NOT EXISTS idx_records_data_gin ON medical_records USING GIN (data);

-- 3. 插入示例数据 (用于测试)
INSERT INTO patients (name, gender, age, info) 
VALUES ('张三', '男', 35, '{"occupation": "程序员", "history": "无"}');

INSERT INTO medical_records (patient_id, complaint, diagnosis, data)
VALUES (
    1, 
    '长期失眠', 
    '心脾两虚',
    '{
        "medical_record": {"complaint": "长期失眠", "prescription": "归脾汤", "note": "注意休息"},
        "pulse_grid": {"cun-fu": "细", "guan-fu": "弱"},
        "raw_input": {}
    }'
);
