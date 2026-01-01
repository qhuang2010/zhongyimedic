"""
中医脉象九宫格数据验证工具
用于验证标注文件是否符合数据格式规范
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
import jsonschema
from ..utils.logger import get_logger

logger = get_logger(__name__)

# 定义JSON Schema用于验证
ANNOTATION_SCHEMA = {
    "type": "object",
    "required": ["image_info", "annotations", "metadata"],
    "properties": {
        "image_info": {
            "type": "object",
            "required": ["file_name", "width", "height", "format"],
            "properties": {
                "file_name": {"type": "string"},
                "width": {"type": "integer", "minimum": 1},
                "height": {"type": "integer", "minimum": 1},
                "format": {"type": "string", "enum": ["jpg", "jpeg", "png", "bmp", "tiff"]},
                "created_at": {"type": "string"}
            }
        },
        "annotations": {
            "type": "array",
            "minItems": 1,
            "maxItems": 9,
            "items": {
                "type": "object",
                "required": ["grid_id", "position", "text", "bbox", "attributes"],
                "properties": {
                    "grid_id": {"type": "integer", "minimum": 1, "maximum": 9},
                    "position": {"type": "string"},
                    "text": {"type": "string"},
                    "bbox": {
                        "type": "array",
                        "minItems": 4,
                        "maxItems": 4,
                        "items": {"type": "number"}
                    },
                    "attributes": {
                        "type": "object",
                        "required": ["pulse_type", "strength", "rhythm", "confidence"],
                        "properties": {
                            "pulse_type": {"type": "string"},
                            "strength": {"type": "string", "enum": ["强", "中", "弱"]},
                            "rhythm": {"type": "string", "enum": ["齐", "不齐", "促", "结", "代"]},
                            "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                        }
                    }
                }
            }
        },
        "metadata": {
            "type": "object",
            "required": ["annotator", "annotation_date", "version"],
            "properties": {
                "annotator": {"type": "string"},
                "annotation_date": {"type": "string"},
                "version": {"type": "string"}
            }
        }
    }
}

class DataValidator:
    """数据验证器类"""
    
    def __init__(self, schema: Dict = None):
        """
        初始化验证器
        
        Args:
            schema: JSON Schema，如果为None则使用默认的ANNOTATION_SCHEMA
        """
        self.schema = schema or ANNOTATION_SCHEMA
        self.validation_errors = []
        
    def validate_data(self, data: Dict, context: str = "memory") -> Tuple[bool, List[str]]:
        """
        验证数据字典
        
        Args:
            data: 数据字典
            context: 验证上下文（如文件名），用于错误提示
            
        Returns:
            (is_valid, errors): 是否有效和错误列表
        """
        self.validation_errors = []
        
        try:
            # 使用JSON Schema验证
            try:
                jsonschema.validate(instance=data, schema=self.schema)
            except jsonschema.exceptions.ValidationError as e:
                self.validation_errors.append(f"JSON Schema验证失败: {str(e)}")
                return False, self.validation_errors
            
            # 自定义验证规则
            is_valid = self._validate_custom_rules(data, context)
            
            return is_valid, self.validation_errors
            
        except Exception as e:
            self.validation_errors.append(f"验证过程中发生错误: {str(e)}")
            return False, self.validation_errors

    def validate_file(self, file_path: str) -> Tuple[bool, List[str]]:
        """
        验证单个标注文件
        
        Args:
            file_path: 标注文件路径
            
        Returns:
            (is_valid, errors): 是否有效和错误列表
        """
        self.validation_errors = []
        
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                self.validation_errors.append(f"文件不存在: {file_path}")
                return False, self.validation_errors
            
            # 读取JSON文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return self.validate_data(data, file_path)
            
        except json.JSONDecodeError as e:
            self.validation_errors.append(f"JSON解析失败: {str(e)}")
            return False, self.validation_errors
        except Exception as e:
            self.validation_errors.append(f"验证过程中发生错误: {str(e)}")
            return False, self.validation_errors
    
    def _validate_custom_rules(self, data: Dict, file_path: str) -> bool:
        """
        验证自定义规则
        
        Args:
            data: 标注数据
            file_path: 文件路径
            
        Returns:
            是否通过验证
        """
        is_valid = True
        
        # 验证grid_id的唯一性
        grid_ids = [ann['grid_id'] for ann in data['annotations']]
        if len(grid_ids) != len(set(grid_ids)):
            self.validation_errors.append("grid_id存在重复")
            is_valid = False
        
        # 验证bbox格式
        for i, ann in enumerate(data['annotations']):
            bbox = ann['bbox']
            if len(bbox) != 4:
                self.validation_errors.append(f"第{i+1}个标注的bbox格式错误，应为4个数值")
                is_valid = False
            else:
                x, y, w, h = bbox
                if w <= 0 or h <= 0:
                    self.validation_errors.append(f"第{i+1}个标注的bbox宽度和高度必须为正数")
                    is_valid = False
        
        # 验证文本内容不为空
        for i, ann in enumerate(data['annotations']):
            if not ann['text'] or not ann['text'].strip():
                self.validation_errors.append(f"第{i+1}个标注的文本内容为空")
                is_valid = False
        
        # 验证confidence值
        for i, ann in enumerate(data['annotations']):
            confidence = ann['attributes']['confidence']
            if confidence < 0 or confidence > 1:
                self.validation_errors.append(f"第{i+1}个标注的confidence值必须在0-1之间")
                is_valid = False
        
        return is_valid
    
    def validate_directory(self, dir_path: str, recursive: bool = True) -> Dict[str, Tuple[bool, List[str]]]:
        """
        验证目录中的所有标注文件
        
        Args:
            dir_path: 目录路径
            recursive: 是否递归子目录
            
        Returns:
            文件路径到验证结果的映射
        """
        results = {}
        
        if not os.path.exists(dir_path):
            logger.error(f"目录不存在: {dir_path}")
            return results
        
        # 查找所有JSON文件
        pattern = "**/*.json" if recursive else "*.json"
        json_files = list(Path(dir_path).glob(pattern))
        
        logger.info(f"找到 {len(json_files)} 个JSON文件待验证")
        
        for file_path in json_files:
            is_valid, errors = self.validate_file(str(file_path))
            results[str(file_path)] = (is_valid, errors)
            
            if is_valid:
                logger.info(f"✓ {file_path} 验证通过")
            else:
                logger.error(f"✗ {file_path} 验证失败: {errors}")
        
        return results
    
    def generate_validation_report(self, results: Dict[str, Tuple[bool, List[str]]], output_path: str = None) -> str:
        """
        生成验证报告
        
        Args:
            results: 验证结果
            output_path: 报告输出路径，如果为None则返回字符串
            
        Returns:
            报告内容
        """
        total_files = len(results)
        valid_files = sum(1 for is_valid, _ in results.values() if is_valid)
        invalid_files = total_files - valid_files
        
        report_lines = [
            "=" * 60,
            "中医脉象九宫格数据验证报告",
            "=" * 60,
            f"验证时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"总文件数: {total_files}",
            f"通过验证: {valid_files}",
            f"验证失败: {invalid_files}",
            f"成功率: {valid_files/total_files*100:.1f}%" if total_files > 0 else "成功率: 0%",
            "=" * 60,
            ""
        ]
        
        if invalid_files > 0:
            report_lines.append("验证失败的文件:")
            report_lines.append("-" * 60)
            
            for file_path, (is_valid, errors) in results.items():
                if not is_valid:
                    report_lines.append(f"\n文件: {file_path}")
                    for error in errors:
                        report_lines.append(f"  - {error}")
        
        report_content = "\n".join(report_lines)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"验证报告已保存到: {output_path}")
        
        return report_content


def main():
    """主函数，用于命令行调用"""
    import argparse
    
    parser = argparse.ArgumentParser(description='验证中医脉象九宫格标注文件')
    parser.add_argument('path', help='要验证的文件或目录路径')
    parser.add_argument('--recursive', '-r', action='store_true', help='递归验证子目录')
    parser.add_argument('--report', help='生成验证报告到指定文件')
    
    args = parser.parse_args()
    
    validator = DataValidator()
    
    if os.path.isfile(args.path):
        # 验证单个文件
        is_valid, errors = validator.validate_file(args.path)
        
        if is_valid:
            print(f"✓ {args.path} 验证通过")
        else:
            print(f"✗ {args.path} 验证失败:")
            for error in errors:
                print(f"  - {error}")
    else:
        # 验证目录
        results = validator.validate_directory(args.path, args.recursive)
        
        if args.report:
            validator.generate_validation_report(results, args.report)
            print(f"验证报告已生成: {args.report}")
        else:
            report = validator.generate_validation_report(results)
            print(report)


if __name__ == "__main__":
    main()