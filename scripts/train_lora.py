"""
LoRA Fine-tuning Script for Yuanqi Pulse Method AI
元气脉法AI微调训练脚本

Uses LoRA (Low-Rank Adaptation) for efficient fine-tuning on local hardware.
Supports both CPU and GPU training (GPU recommended).

Requirements:
    pip install transformers peft datasets accelerate bitsandbytes

Usage:
    python scripts/train_lora.py --model qwen --epochs 3
"""

import os
import sys
import json
import argparse
from datetime import datetime

def check_dependencies():
    """检查依赖"""
    missing = []
    try:
        import torch
    except ImportError:
        missing.append("torch")
    try:
        import transformers
    except ImportError:
        missing.append("transformers")
    try:
        import peft
    except ImportError:
        missing.append("peft")
    try:
        import datasets
    except ImportError:
        missing.append("datasets")
    
    if missing:
        print(f"⚠️  缺少依赖: {', '.join(missing)}")
        print(f"请运行: pip install {' '.join(missing)}")
        return False
    return True


def load_training_data(data_path: str):
    """加载训练数据"""
    from datasets import Dataset
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 转换为Dataset格式
    dataset = Dataset.from_list(data)
    return dataset


def format_prompt(example):
    """格式化为训练prompt"""
    instruction = example.get("instruction", "")
    input_text = example.get("input", "")
    output = example.get("output", "")
    
    if input_text:
        text = f"""### 指令：
{instruction}

### 输入：
{input_text}

### 回答：
{output}"""
    else:
        text = f"""### 指令：
{instruction}

### 回答：
{output}"""
    
    return {"text": text}


def train_lora(
    model_name: str = "Qwen/Qwen2.5-0.5B",
    data_path: str = "data/training/alpaca_yuanqi.json",
    output_dir: str = "models/yuanqi_lora",
    epochs: int = 3,
    batch_size: int = 2,
    learning_rate: float = 2e-4,
    use_4bit: bool = True
):
    """
    使用LoRA微调模型
    
    Args:
        model_name: 基础模型名称
        data_path: 训练数据路径
        output_dir: 输出目录
        epochs: 训练轮数
        batch_size: 批次大小
        learning_rate: 学习率
        use_4bit: 是否使用4bit量化
    """
    import torch
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        TrainingArguments,
        Trainer,
        DataCollatorForLanguageModeling
    )
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    
    print("=" * 50)
    print("元气脉法AI LoRA微调训练")
    print("=" * 50)
    
    # 检查设备
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"📱 使用设备: {device}")
    
    # 加载模型和分词器
    print(f"\n📦 加载模型: {model_name}")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # 模型加载配置
    model_kwargs = {
        "trust_remote_code": True,
        "device_map": "auto" if device != "cpu" else None,
    }
    
    if use_4bit and device == "cuda":
        from transformers import BitsAndBytesConfig
        model_kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
    
    model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)
    
    if use_4bit and device == "cuda":
        model = prepare_model_for_kbit_training(model)
    
    # LoRA配置
    print("\n🔧 配置LoRA...")
    lora_config = LoraConfig(
        r=8,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    # 加载数据
    print(f"\n📂 加载训练数据: {data_path}")
    dataset = load_training_data(data_path)
    
    # 格式化数据
    dataset = dataset.map(format_prompt)
    
    # 分词
    def tokenize(example):
        return tokenizer(
            example["text"],
            truncation=True,
            max_length=512,
            padding="max_length"
        )
    
    tokenized_dataset = dataset.map(tokenize, remove_columns=dataset.column_names)
    
    print(f"   训练样本: {len(tokenized_dataset)}")
    
    # 训练参数
    os.makedirs(output_dir, exist_ok=True)
    
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=4,
        learning_rate=learning_rate,
        warmup_steps=10,
        logging_steps=10,
        save_steps=50,
        save_total_limit=2,
        fp16=device == "cuda",
        report_to="none",
        remove_unused_columns=False
    )
    
    # 数据整理器
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )
    
    # 训练器
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator
    )
    
    # 开始训练
    print("\n🚀 开始训练...")
    print(f"   轮数: {epochs}")
    print(f"   批次大小: {batch_size}")
    print(f"   学习率: {learning_rate}")
    
    trainer.train()
    
    # 保存模型
    print(f"\n💾 保存模型到: {output_dir}")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    # 保存训练信息
    info = {
        "base_model": model_name,
        "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "epochs": epochs,
        "samples": len(tokenized_dataset),
        "device": device
    }
    with open(os.path.join(output_dir, "training_info.json"), 'w') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 训练完成!")
    return output_dir


def test_model(model_path: str, prompt: str):
    """测试训练好的模型"""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    
    print(f"\n🧪 测试模型: {model_path}")
    
    # 加载训练信息
    info_path = os.path.join(model_path, "training_info.json")
    with open(info_path, 'r') as f:
        info = json.load(f)
    
    base_model = info["base_model"]
    
    # 加载模型
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    base = AutoModelForCausalLM.from_pretrained(base_model, trust_remote_code=True)
    model = PeftModel.from_pretrained(base, model_path)
    
    # 生成
    formatted_prompt = f"""### 指令：
{prompt}

### 回答：
"""
    
    inputs = tokenizer(formatted_prompt, return_tensors="pt")
    outputs = model.generate(
        **inputs,
        max_new_tokens=256,
        temperature=0.7,
        do_sample=True
    )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"\n📝 回答:\n{response}")


def main():
    parser = argparse.ArgumentParser(description="元气脉法AI LoRA微调训练")
    parser.add_argument("--model", default="Qwen/Qwen2.5-0.5B", help="基础模型")
    parser.add_argument("--data", default="data/training/alpaca_yuanqi.json", help="训练数据")
    parser.add_argument("--output", default="models/yuanqi_lora", help="输出目录")
    parser.add_argument("--epochs", type=int, default=3, help="训练轮数")
    parser.add_argument("--batch-size", type=int, default=2, help="批次大小")
    parser.add_argument("--test", action="store_true", help="测试已训练模型")
    parser.add_argument("--prompt", default="请解释元气脉法中的脉象分析方法", help="测试prompt")
    
    args = parser.parse_args()
    
    if not check_dependencies():
        return
    
    if args.test:
        test_model(args.output, args.prompt)
    else:
        train_lora(
            model_name=args.model,
            data_path=args.data,
            output_dir=args.output,
            epochs=args.epochs,
            batch_size=args.batch_size
        )


if __name__ == "__main__":
    main()
