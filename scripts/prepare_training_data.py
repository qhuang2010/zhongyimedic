"""
Training Data Preparation for Yuanqi Pulse Method AI
元气脉法AI训练数据准备

Converts imported knowledge base data into training format for:
1. Knowledge injection (RAG)
2. Fine-tuning (LoRA/QLoRA)
3. Prompt-based learning

Output Formats:
- JSONL for fine-tuning
- Embeddings for RAG
"""

import os
import sys
import json
import yaml
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_imported_data(import_dir: str) -> Dict[str, List[Dict]]:
    """
    加载所有已导入的数据
    Load all imported data
    """
    data = {
        "theories": [],
        "cases": []
    }
    
    for filename in os.listdir(import_dir):
        if not filename.endswith('.json'):
            continue
        
        filepath = os.path.join(import_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            items = json.load(f)
        
        if 'theories' in filename:
            data["theories"].extend(items)
        elif 'general' in filename:  # Case data
            data["cases"].extend(items)
    
    return data


def generate_theory_prompts(theories: List[Dict]) -> List[Dict[str, str]]:
    """
    将理论转换为问答对（用于微调）
    Convert theories to Q&A pairs for fine-tuning
    """
    prompts = []
    
    for theory in theories:
        title = theory.get("title", "")
        content = theory.get("content", "")
        
        if not title or not content:
            continue
        
        # 生成问答对
        qa = {
            "instruction": f"请详细解释元气脉法中关于【{title}】的理论。",
            "input": "",
            "output": content.strip()
        }
        prompts.append(qa)
        
        # 生成简答版本
        if len(content) > 200:
            summary = content[:200] + "..."
            qa_short = {
                "instruction": f"简述元气脉法【{title}】的核心要点。",
                "input": "",
                "output": summary
            }
            prompts.append(qa_short)
    
    return prompts


def generate_case_prompts(cases: List[Dict]) -> List[Dict[str, str]]:
    """
    将病例转换为诊断推理对（用于微调）
    Convert cases to diagnostic reasoning pairs
    """
    prompts = []
    
    for case in cases:
        title = case.get("title", "")
        content = case.get("content", "")
        
        if not content:
            continue
        
        # 尝试提取结构化信息
        # 生成诊断问答
        qa = {
            "instruction": "根据以下病例信息，请按照元气脉法进行辨证分析和处方建议。",
            "input": f"病例：{title}\n\n临床资料：{content[:500]}...",
            "output": f"## 元气脉法辨证分析\n\n{content}"
        }
        prompts.append(qa)
    
    return prompts


def generate_cot_prompts(cases: List[Dict]) -> List[Dict[str, str]]:
    """
    生成思维链推理数据（Chain-of-Thought格式）
    Generate Chain-of-Thought reasoning data
    """
    cot_prompts = []
    
    for case in cases:
        title = case.get("title", "")
        content = case.get("content", "")
        
        if not content or len(content) < 100:
            continue
        
        # 构建CoT格式
        cot = {
            "instruction": "请使用元气脉法的思维方式，逐步分析以下病例，给出诊断和治疗方案。",
            "input": f"病例信息：{title}",
            "output": f"""让我按照元气脉法的思维步骤来分析这个病例：

**第一步：脉象分析**
首先，我需要评估患者的元气状态。根据元气脉法的"察根"原则，重点关注沉取层次的脉象。

**第二步：元气状态判断**
根据脉象特征判断元气是充盛、虚损还是外浮。

**第三步：辨证论治**
{content}

**第四步：治疗方案**
根据元气状态确定治则，选择相应的方剂。

以上是元气脉法的诊断思路和治疗建议。"""
        }
        cot_prompts.append(cot)
    
    return cot_prompts


def generate_conversation_data(theories: List[Dict], cases: List[Dict]) -> List[Dict]:
    """
    生成对话格式数据（适用于ChatML格式微调）
    Generate conversation format data for ChatML fine-tuning
    """
    conversations = []
    
    # 理论问答对话
    for theory in theories[:50]:  # 限制数量
        title = theory.get("title", "")
        content = theory.get("content", "")
        
        if not title or not content:
            continue
        
        conv = {
            "messages": [
                {"role": "system", "content": "你是一位精通元气脉法的中医师，请根据元气脉法的理论体系回答问题。"},
                {"role": "user", "content": f"请解释{title}"},
                {"role": "assistant", "content": content.strip()}
            ]
        }
        conversations.append(conv)
    
    # 病例分析对话
    for case in cases[:30]:
        title = case.get("title", "")
        content = case.get("content", "")
        
        if not content:
            continue
        
        conv = {
            "messages": [
                {"role": "system", "content": "你是一位精通元气脉法的中医师。请使用元气脉法的诊断思路分析病例，重点关注脉象的浮中沉三层特征和元气状态评估。"},
                {"role": "user", "content": f"请分析这个病例：{title}"},
                {"role": "assistant", "content": content.strip()}
            ]
        }
        conversations.append(conv)
    
    return conversations


def prepare_training_data(
    import_dir: str,
    output_dir: str
) -> Dict[str, Any]:
    """
    准备完整的训练数据集
    Prepare complete training dataset
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # 加载数据
    print("📂 加载已导入数据...")
    data = load_imported_data(import_dir)
    
    print(f"   理论条目: {len(data['theories'])}")
    print(f"   病例条目: {len(data['cases'])}")
    
    stats = {
        "source_theories": len(data['theories']),
        "source_cases": len(data['cases']),
        "generated_prompts": {}
    }
    
    # 1. 生成Alpaca格式数据（用于通用微调）
    print("\n🔄 生成Alpaca格式训练数据...")
    theory_prompts = generate_theory_prompts(data['theories'])
    case_prompts = generate_case_prompts(data['cases'])
    all_prompts = theory_prompts + case_prompts
    
    alpaca_file = os.path.join(output_dir, "alpaca_yuanqi.json")
    with open(alpaca_file, 'w', encoding='utf-8') as f:
        json.dump(all_prompts, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ Alpaca格式: {len(all_prompts)} 条 -> {alpaca_file}")
    stats["generated_prompts"]["alpaca"] = len(all_prompts)
    
    # 2. 生成CoT格式数据
    print("\n🔄 生成思维链格式数据...")
    cot_prompts = generate_cot_prompts(data['cases'])
    
    cot_file = os.path.join(output_dir, "cot_yuanqi.json")
    with open(cot_file, 'w', encoding='utf-8') as f:
        json.dump(cot_prompts, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ CoT格式: {len(cot_prompts)} 条 -> {cot_file}")
    stats["generated_prompts"]["cot"] = len(cot_prompts)
    
    # 3. 生成对话格式数据（ChatML）
    print("\n🔄 生成对话格式数据...")
    conversations = generate_conversation_data(data['theories'], data['cases'])
    
    conv_file = os.path.join(output_dir, "conversations_yuanqi.json")
    with open(conv_file, 'w', encoding='utf-8') as f:
        json.dump(conversations, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ 对话格式: {len(conversations)} 条 -> {conv_file}")
    stats["generated_prompts"]["conversations"] = len(conversations)
    
    # 4. 生成JSONL格式（通用格式）
    print("\n🔄 生成JSONL格式...")
    jsonl_file = os.path.join(output_dir, "train_yuanqi.jsonl")
    with open(jsonl_file, 'w', encoding='utf-8') as f:
        for item in all_prompts:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"   ✅ JSONL格式: {len(all_prompts)} 行 -> {jsonl_file}")
    
    # 统计信息
    stats_file = os.path.join(output_dir, "training_stats.json")
    stats["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    return stats


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="准备元气脉法AI训练数据")
    parser.add_argument(
        "--input", "-i",
        default="data/corpus/yuanqi_imported",
        help="已导入数据目录"
    )
    parser.add_argument(
        "--output", "-o",
        default="data/training",
        help="训练数据输出目录"
    )
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("元气脉法AI训练数据准备")
    print("=" * 50)
    
    stats = prepare_training_data(args.input, args.output)
    
    print("\n" + "=" * 50)
    print("📊 生成完成!")
    print(f"   原始理论: {stats['source_theories']} 条")
    print(f"   原始病例: {stats['source_cases']} 条")
    print(f"   Alpaca格式: {stats['generated_prompts']['alpaca']} 条")
    print(f"   CoT格式: {stats['generated_prompts']['cot']} 条")
    print(f"   对话格式: {stats['generated_prompts']['conversations']} 条")
    print("=" * 50)


if __name__ == "__main__":
    main()
