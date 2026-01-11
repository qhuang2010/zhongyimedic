"""
Document Importer for Yuanqi Pulse Method Knowledge Base
元气脉法知识库文档导入工具

Supports:
- DOCX (Word documents)
- MD (Markdown files)
- PDF (PDF documents)

Usage:
    python scripts/import_documents.py --input /path/to/file.docx --type theory
    python scripts/import_documents.py --input /path/to/folder --batch
"""

import os
import sys
import json
import yaml
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
import re

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read_docx(file_path: str) -> str:
    """
    读取DOCX文件内容
    Read DOCX file content
    """
    try:
        from docx import Document
        doc = Document(file_path)
        
        content = []
        for para in doc.paragraphs:
            if para.text.strip():
                content.append(para.text)
        
        return "\n\n".join(content)
    except ImportError:
        print("请安装 python-docx: pip install python-docx")
        return ""
    except Exception as e:
        print(f"读取DOCX失败: {e}")
        return ""


def read_markdown(file_path: str) -> str:
    """
    读取Markdown文件内容
    Read Markdown file content
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取Markdown失败: {e}")
        return ""


def read_pdf(file_path: str) -> str:
    """
    读取PDF文件内容
    Read PDF file content
    """
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        
        content = []
        for page in doc:
            content.append(page.get_text())
        
        doc.close()
        return "\n\n".join(content)
    except ImportError:
        print("请安装 PyMuPDF: pip install pymupdf")
        return ""
    except Exception as e:
        print(f"读取PDF失败: {e}")
        return ""


def read_document(file_path: str) -> str:
    """
    自动识别并读取文档
    Auto-detect and read document
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.docx':
        return read_docx(file_path)
    elif ext in ['.md', '.markdown']:
        return read_markdown(file_path)
    elif ext == '.pdf':
        return read_pdf(file_path)
    else:
        print(f"不支持的文件格式: {ext}")
        return ""


def extract_sections(content: str) -> List[Dict[str, str]]:
    """
    从文档内容提取章节
    Extract sections from document content
    """
    sections = []
    
    # 尝试按标题分割（支持# 标题 或 一、二、三 格式）
    # Pattern for markdown headers or Chinese numbered sections
    patterns = [
        r'^#{1,3}\s+(.+)$',           # Markdown headers
        r'^[一二三四五六七八九十]+[、.]\s*(.+)$',  # Chinese numbered
        r'^\d+[、.]\s*(.+)$',          # Arabic numbered
    ]
    
    lines = content.split('\n')
    current_section = {"title": "概述", "content": []}
    
    for line in lines:
        is_header = False
        for pattern in patterns:
            match = re.match(pattern, line.strip())
            if match:
                # Save previous section
                if current_section["content"]:
                    sections.append({
                        "title": current_section["title"],
                        "content": "\n".join(current_section["content"]).strip()
                    })
                # Start new section
                current_section = {"title": match.group(1).strip(), "content": []}
                is_header = True
                break
        
        if not is_header and line.strip():
            current_section["content"].append(line)
    
    # Save last section
    if current_section["content"]:
        sections.append({
            "title": current_section["title"],
            "content": "\n".join(current_section["content"]).strip()
        })
    
    return sections if sections else [{"title": "全文", "content": content}]


def convert_to_theory(
    content: str, 
    source_file: str,
    category: str = "元气脉法理论"
) -> List[Dict[str, Any]]:
    """
    将文档内容转换为理论条目
    Convert document content to theory entries
    """
    sections = extract_sections(content)
    theories = []
    
    for i, section in enumerate(sections, 1):
        theory_id = f"YQ_THEORY_AUTO_{datetime.now().strftime('%Y%m%d')}_{i:03d}"
        
        theory = {
            "theory_id": theory_id,
            "category": category,
            "title": section["title"],
            "content": section["content"],
            "key_concepts": [],  # 需要后续标注
            "source": {
                "file": os.path.basename(source_file),
                "import_date": datetime.now().strftime("%Y-%m-%d"),
                "auto_imported": True
            },
            "needs_review": True  # 标记需要人工审核
        }
        theories.append(theory)
    
    return theories


def convert_to_pulse_pattern(
    content: str,
    source_file: str
) -> List[Dict[str, Any]]:
    """
    将文档内容转换为脉象模式
    Convert document content to pulse patterns
    """
    sections = extract_sections(content)
    patterns = []
    
    for i, section in enumerate(sections, 1):
        pattern_id = f"YQ_PULSE_AUTO_{datetime.now().strftime('%Y%m%d')}_{i:03d}"
        
        pattern = {
            "pulse_pattern_id": pattern_id,
            "pattern_name": section["title"],
            "description": section["content"],
            "characteristics": {},  # 需要后续标注
            "key_features": [],
            "diagnostic_meaning": {},
            "source": {
                "file": os.path.basename(source_file),
                "import_date": datetime.now().strftime("%Y-%m-%d"),
                "auto_imported": True
            },
            "needs_review": True
        }
        patterns.append(pattern)
    
    return patterns


def save_imported_data(
    data: List[Dict],
    output_dir: str,
    prefix: str = "imported"
):
    """
    保存导入的数据
    Save imported data
    """
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save as YAML
    yaml_file = os.path.join(output_dir, f"{prefix}_{timestamp}.yaml")
    with open(yaml_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    
    # Also save as JSON for easier processing
    json_file = os.path.join(output_dir, f"{prefix}_{timestamp}.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return yaml_file, json_file


def import_document(
    file_path: str,
    doc_type: str = "theory",
    output_dir: str = None
) -> Dict[str, Any]:
    """
    导入单个文档
    Import a single document
    """
    print(f"\n📄 正在导入: {file_path}")
    
    # Read document
    content = read_document(file_path)
    if not content:
        return {"success": False, "error": "无法读取文档内容"}
    
    print(f"   读取成功: {len(content)} 字符")
    
    # Convert based on type
    if doc_type == "theory":
        data = convert_to_theory(content, file_path)
        prefix = "theories"
    elif doc_type == "pulse":
        data = convert_to_pulse_pattern(content, file_path)
        prefix = "pulse_patterns"
    else:
        data = convert_to_theory(content, file_path)
        prefix = "general"
    
    print(f"   提取条目: {len(data)} 条")
    
    # Save
    if output_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(base_dir, "data", "corpus", "yuanqi_imported")
    
    yaml_file, json_file = save_imported_data(data, output_dir, prefix)
    
    print(f"   ✅ 已保存: {yaml_file}")
    
    return {
        "success": True,
        "entries_count": len(data),
        "yaml_file": yaml_file,
        "json_file": json_file,
        "needs_review": True
    }


def batch_import(
    input_dir: str,
    doc_type: str = "theory",
    output_dir: str = None
) -> Dict[str, Any]:
    """
    批量导入目录中的所有文档
    Batch import all documents in a directory
    """
    results = []
    supported_extensions = ['.docx', '.md', '.markdown', '.pdf']
    
    for filename in os.listdir(input_dir):
        ext = os.path.splitext(filename)[1].lower()
        if ext in supported_extensions:
            file_path = os.path.join(input_dir, filename)
            result = import_document(file_path, doc_type, output_dir)
            result["file"] = filename
            results.append(result)
    
    success_count = sum(1 for r in results if r.get("success"))
    total_entries = sum(r.get("entries_count", 0) for r in results if r.get("success"))
    
    return {
        "files_processed": len(results),
        "success_count": success_count,
        "total_entries": total_entries,
        "results": results
    }


def main():
    parser = argparse.ArgumentParser(
        description="元气脉法知识库文档导入工具"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="输入文件路径或目录"
    )
    parser.add_argument(
        "--type", "-t",
        choices=["theory", "pulse", "case"],
        default="theory",
        help="文档类型: theory(理论), pulse(脉象), case(病例)"
    )
    parser.add_argument(
        "--output", "-o",
        help="输出目录 (默认: data/corpus/yuanqi_imported)"
    )
    parser.add_argument(
        "--batch", "-b",
        action="store_true",
        help="批量导入目录中所有文档"
    )
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("元气脉法知识库文档导入工具")
    print("=" * 50)
    
    if args.batch or os.path.isdir(args.input):
        result = batch_import(args.input, args.type, args.output)
        print(f"\n📊 导入完成:")
        print(f"   处理文件: {result['files_processed']}")
        print(f"   成功数量: {result['success_count']}")
        print(f"   总条目数: {result['total_entries']}")
    else:
        result = import_document(args.input, args.type, args.output)
        if result["success"]:
            print(f"\n✅ 导入成功: {result['entries_count']} 条")
        else:
            print(f"\n❌ 导入失败: {result.get('error')}")
    
    print("\n⚠️  提示: 自动导入的条目已标记 needs_review=True")
    print("   请人工审核后更新到知识库代码中")


if __name__ == "__main__":
    main()
