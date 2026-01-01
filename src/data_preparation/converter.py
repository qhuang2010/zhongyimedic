"""
中医脉象九宫格数据转换工具
将标注数据转换为DeepSeek-OCR训练格式
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Any, Tuple
import yaml
from PIL import Image, ImageDraw, ImageFont
from ..utils.logger import get_logger
from ..utils.config import get_config

logger = get_logger(__name__)


class DataConverter:
    """数据转换器类"""
    
    def __init__(self, config: Dict = None):
        """
        初始化转换器
        
        Args:
            config: 配置字典，如果为None则使用默认配置
        """
        self.config = config or get_config()
        self.image_size = self.config['data']['image_size']
        self.grid_size = self.config['data']['grid_size']
        
    def convert_single_file(self, annotation_path: str, image_dir: str, output_dir: str) -> bool:
        """
        转换单个标注文件
        
        Args:
            annotation_path: 标注文件路径
            image_dir: 原始图像目录
            output_dir: 输出目录
            
        Returns:
            是否成功转换
        """
        try:
            # 读取标注文件
            with open(annotation_path, 'r', encoding='utf-8') as f:
                annotation_data = json.load(f)
            
            # 获取图像文件名和路径
            image_filename = annotation_data['image_info']['file_name']
            image_path = os.path.join(image_dir, image_filename)
            
            if not os.path.exists(image_path):
                logger.error(f"图像文件不存在: {image_path}")
                return False
            
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 复制图像文件
            output_image_path = os.path.join(output_dir, image_filename)
            shutil.copy2(image_path, output_image_path)
            
            # 转换标注格式
            converted_annotations = self._convert_annotations(annotation_data['annotations'])
            
            # 保存转换后的标注
            output_annotation_path = os.path.join(output_dir, f"{Path(image_filename).stem}.json")
            with open(output_annotation_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "image_path": image_filename,
                    "annotations": converted_annotations,
                    "metadata": annotation_data.get('metadata', {})
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"成功转换: {annotation_path} -> {output_annotation_path}")
            return True
            
        except Exception as e:
            logger.error(f"转换失败 {annotation_path}: {str(e)}")
            return False
    
    def _convert_annotations(self, annotations: List[Dict]) -> List[Dict]:
        """
        转换标注格式
        
        Args:
            annotations: 原始标注列表
            
        Returns:
            转换后的标注列表
        """
        converted = []
        
        for ann in annotations:
            converted_ann = {
                "grid_id": ann["grid_id"],
                "position": ann["position"],
                "text": ann["text"],
                "bbox": ann["bbox"],
                "attributes": ann["attributes"]
            }
            converted.append(converted_ann)
        
        return converted
    
    def create_training_manifest(self, data_dir: str, output_path: str) -> bool:
        """
        创建训练清单文件
        
        Args:
            data_dir: 数据目录
            output_path: 输出清单文件路径
            
        Returns:
            是否成功创建
        """
        try:
            manifest_data = []
            
            # 查找所有JSON文件
            json_files = list(Path(data_dir).glob("*.json"))
            
            for json_file in json_files:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 检查对应的图像文件是否存在
                image_path = os.path.join(data_dir, data["image_path"])
                if os.path.exists(image_path):
                    manifest_data.append({
                        "image_path": data["image_path"],
                        "annotation_path": json_file.name,
                        "metadata": data.get("metadata", {})
                    })
                else:
                    logger.warning(f"图像文件不存在，跳过: {image_path}")
            
            # 保存清单文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(manifest_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"训练清单已创建: {output_path} ({len(manifest_data)} 条记录)")
            return True
            
        except Exception as e:
            logger.error(f"创建训练清单失败: {str(e)}")
            return False
    
    def visualize_annotations(self, image_path: str, annotation_path: str, output_path: str = None) -> bool:
        """
        可视化标注结果
        
        Args:
            image_path: 图像文件路径
            annotation_path: 标注文件路径
            output_path: 输出图像路径，如果为None则显示图像
            
        Returns:
            是否成功
        """
        try:
            # 读取图像
            image = Image.open(image_path)
            draw = ImageDraw.Draw(image)
            
            # 读取标注
            with open(annotation_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            annotations = data.get("annotations", [])
            
            # 绘制标注框和文本
            for ann in annotations:
                bbox = ann["bbox"]
                x, y, w, h = bbox
                
                # 绘制矩形框
                draw.rectangle([x, y, x + w, y + h], outline="red", width=2)
                
                # 绘制文本
                text = f"{ann['grid_id']}: {ann['position']}"
                draw.text((x, y - 20), text, fill="red")
                
                # 绘制详细文本（换行显示）
                detail_text = ann["text"]
                lines = self._wrap_text(detail_text, max_width=20)
                for i, line in enumerate(lines):
                    draw.text((x, y + h + 5 + i * 15), line, fill="blue")
            
            if output_path:
                image.save(output_path)
                logger.info(f"可视化结果已保存: {output_path}")
            else:
                image.show()
            
            return True
            
        except Exception as e:
            logger.error(f"可视化失败: {str(e)}")
            return False
    
    def _wrap_text(self, text: str, max_width: int = 20) -> List[str]:
        """
        文本换行处理
        
        Args:
            text: 原始文本
            max_width: 最大宽度（字符数）
            
        Returns:
            换行后的文本列表
        """
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + word) <= max_width:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines if lines else [text]
    
    def split_dataset(self, data_dir: str, output_dir: str, train_ratio: float = 0.8, val_ratio: float = 0.1) -> bool:
        """
        分割数据集为训练集、验证集和测试集
        
        Args:
            data_dir: 数据目录
            output_dir: 输出目录
            train_ratio: 训练集比例
            val_ratio: 验证集比例
            
        Returns:
            是否成功
        """
        try:
            # 获取所有数据文件
            json_files = list(Path(data_dir).glob("*.json"))
            total_files = len(json_files)
            
            if total_files == 0:
                logger.error("没有找到数据文件")
                return False
            
            # 计算分割数量
            train_count = int(total_files * train_ratio)
            val_count = int(total_files * val_ratio)
            test_count = total_files - train_count - val_count
            
            # 随机打乱文件列表
            import random
            random.shuffle(json_files)
            
            # 分割数据
            train_files = json_files[:train_count]
            val_files = json_files[train_count:train_count + val_count]
            test_files = json_files[train_count + val_count:]
            
            # 创建输出目录
            for split in ['train', 'val', 'test']:
                os.makedirs(os.path.join(output_dir, split), exist_ok=True)
            
            # 复制文件到对应目录
            self._copy_files(train_files, data_dir, os.path.join(output_dir, 'train'))
            self._copy_files(val_files, data_dir, os.path.join(output_dir, 'val'))
            self._copy_files(test_files, data_dir, os.path.join(output_dir, 'test'))
            
            # 创建分割清单
            split_info = {
                "train": len(train_files),
                "val": len(val_files),
                "test": len(test_files),
                "total": total_files,
                "ratios": {
                    "train": train_ratio,
                    "val": val_ratio,
                    "test": 1 - train_ratio - val_ratio
                }
            }
            
            with open(os.path.join(output_dir, 'split_info.json'), 'w', encoding='utf-8') as f:
                json.dump(split_info, f, ensure_ascii=False, indent=2)
            
            logger.info(f"数据集分割完成: 训练集{len(train_files)}, 验证集{len(val_files)}, 测试集{len(test_files)}")
            return True
            
        except Exception as e:
            logger.error(f"数据集分割失败: {str(e)}")
            return False
    
    def _copy_files(self, file_list: List[Path], source_dir: str, target_dir: str):
        """
        复制文件列表到目标目录
        
        Args:
            file_list: 文件列表
            source_dir: 源目录
            target_dir: 目标目录
        """
        for json_file in file_list:
            # 复制JSON文件
            shutil.copy2(json_file, target_dir)
            
            # 读取JSON获取图像文件名
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 复制对应的图像文件
            image_filename = data["image_path"]
            image_path = os.path.join(source_dir, image_filename)
            if os.path.exists(image_path):
                shutil.copy2(image_path, target_dir)


def main():
    """主函数，用于命令行调用"""
    import argparse
    
    parser = argparse.ArgumentParser(description='转换中医脉象九宫格数据')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 转换命令
    convert_parser = subparsers.add_parser('convert', help='转换标注文件')
    convert_parser.add_argument('annotation', help='标注文件路径')
    convert_parser.add_argument('image_dir', help='图像目录')
    convert_parser.add_argument('output_dir', help='输出目录')
    
    # 创建清单命令
    manifest_parser = subparsers.add_parser('manifest', help='创建训练清单')
    manifest_parser.add_argument('data_dir', help='数据目录')
    manifest_parser.add_argument('output_path', help='输出清单文件路径')
    
    # 可视化命令
    viz_parser = subparsers.add_parser('visualize', help='可视化标注')
    viz_parser.add_argument('image_path', help='图像文件路径')
    viz_parser.add_argument('annotation_path', help='标注文件路径')
    viz_parser.add_argument('--output', help='输出图像路径')
    
    # 分割数据集命令
    split_parser = subparsers.add_parser('split', help='分割数据集')
    split_parser.add_argument('data_dir', help='数据目录')
    split_parser.add_argument('output_dir', help='输出目录')
    split_parser.add_argument('--train_ratio', type=float, default=0.8, help='训练集比例')
    split_parser.add_argument('--val_ratio', type=float, default=0.1, help='验证集比例')
    
    args = parser.parse_args()
    
    converter = DataConverter()
    
    if args.command == 'convert':
        success = converter.convert_single_file(args.annotation, args.image_dir, args.output_dir)
        print(f"转换{'成功' if success else '失败'}")
    elif args.command == 'manifest':
        success = converter.create_training_manifest(args.data_dir, args.output_path)
        print(f"清单创建{'成功' if success else '失败'}")
    elif args.command == 'visualize':
        success = converter.visualize_annotations(args.image_path, args.annotation_path, args.output)
        print(f"可视化{'成功' if success else '失败'}")
    elif args.command == 'split':
        success = converter.split_dataset(args.data_dir, args.output_dir, args.train_ratio, args.val_ratio)
        print(f"数据集分割{'成功' if success else '失败'}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()