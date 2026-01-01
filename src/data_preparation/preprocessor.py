"""
中医脉象九宫格数据预处理工具
包括数据增强、归一化、格式转换等功能
"""

import os
import json
import random
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import cv2
from ..utils.logger import get_logger
from ..utils.config import get_config

logger = get_logger(__name__)


class DataPreprocessor:
    """数据预处理器类"""
    
    def __init__(self, config: Dict = None):
        """
        初始化预处理器
        
        Args:
            config: 配置字典，如果为None则使用默认配置
        """
        self.config = config or get_config()
        self.image_size = self.config['data']['image_size']
        self.grid_size = self.config['data']['grid_size']
        
        # 数据增强参数
        self.augmentation_params = self.config.get('augmentation', {
            'rotation_range': 10,
            'brightness_range': 0.2,
            'contrast_range': 0.2,
            'blur_probability': 0.3,
            'noise_probability': 0.2
        })
    
    def preprocess_image(self, image_path: str, output_path: str = None, 
                        apply_augmentation: bool = False) -> Optional[np.ndarray]:
        """
        预处理单个图像
        
        Args:
            image_path: 输入图像路径
            output_path: 输出图像路径，如果为None则不保存
            apply_augmentation: 是否应用数据增强
            
        Returns:
            预处理后的图像数组，如果失败返回None
        """
        try:
            # 读取图像
            image = Image.open(image_path).convert('RGB')
            
            # 调整图像大小
            image = image.resize((self.image_size, self.image_size), Image.Resampling.LANCZOS)
            
            # 应用数据增强
            if apply_augmentation:
                image = self._apply_augmentation(image)
            
            # 转换为numpy数组并归一化
            image_array = np.array(image).astype(np.float32) / 255.0
            
            # 保存处理后的图像
            if output_path:
                # 转换回0-255范围并保存
                save_image = Image.fromarray((image_array * 255).astype(np.uint8))
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                save_image.save(output_path, quality=95)
                logger.debug(f"图像已保存: {output_path}")
            
            return image_array
            
        except Exception as e:
            logger.error(f"图像预处理失败 {image_path}: {str(e)}")
            return None
    
    def _apply_augmentation(self, image: Image.Image) -> Image.Image:
        """
        应用数据增强
        
        Args:
            image: 输入图像
            
        Returns:
            增强后的图像
        """
        # 随机旋转
        if random.random() < 0.5:
            angle = random.uniform(-self.augmentation_params['rotation_range'], 
                                 self.augmentation_params['rotation_range'])
            image = image.rotate(angle, expand=False, fillcolor=(255, 255, 255))
        
        # 随机调整亮度
        if random.random() < 0.5:
            brightness_factor = random.uniform(1 - self.augmentation_params['brightness_range'], 
                                             1 + self.augmentation_params['brightness_range'])
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(brightness_factor)
        
        # 随机调整对比度
        if random.random() < 0.5:
            contrast_factor = random.uniform(1 - self.augmentation_params['contrast_range'], 
                                           1 + self.augmentation_params['contrast_range'])
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast_factor)
        
        # 随机模糊
        if random.random() < self.augmentation_params['blur_probability']:
            blur_radius = random.uniform(0.5, 1.5)
            image = image.filter(ImageFilter.GaussianBlur(blur_radius))
        
        # 随机添加噪声
        if random.random() < self.augmentation_params['noise_probability']:
            image = self._add_noise(image)
        
        return image
    
    def _add_noise(self, image: Image.Image) -> Image.Image:
        """
        添加随机噪声
        
        Args:
            image: 输入图像
            
        Returns:
            添加噪声后的图像
        """
        img_array = np.array(image)
        noise = np.random.normal(0, 5, img_array.shape).astype(np.uint8)
        noisy_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        return Image.fromarray(noisy_array)
    
    def extract_grid_regions(self, image_path: str, annotations: List[Dict]) -> Dict[int, np.ndarray]:
        """
        从图像中提取九宫格区域
        
        Args:
            image_path: 图像路径
            annotations: 标注信息列表
            
        Returns:
            grid_id到区域图像的映射
        """
        try:
            # 读取图像
            image = Image.open(image_path).convert('RGB')
            image_array = np.array(image)
            
            grid_regions = {}
            
            for ann in annotations:
                grid_id = ann['grid_id']
                bbox = ann['bbox']
                x, y, w, h = [int(v) for v in bbox]
                
                # 提取区域
                region = image_array[y:y+h, x:x+w]
                grid_regions[grid_id] = region
            
            return grid_regions
            
        except Exception as e:
            logger.error(f"提取九宫格区域失败 {image_path}: {str(e)}")
            return {}
    
    def create_grid_overlay(self, image_path: str, output_path: str = None) -> bool:
        """
        创建九宫格覆盖层，用于可视化
        
        Args:
            image_path: 输入图像路径
            output_path: 输出图像路径
            
        Returns:
            是否成功
        """
        try:
            # 读取图像
            image = Image.open(image_path).convert('RGB')
            draw = ImageDraw.Draw(image)
            
            width, height = image.size
            
            # 计算九宫格线
            third_w = width // 3
            third_h = height // 3
            
            # 绘制垂直线
            for i in range(1, 3):
                x = i * third_w
                draw.line([(x, 0), (x, height)], fill="red", width=2)
            
            # 绘制水平线
            for i in range(1, 3):
                y = i * third_h
                draw.line([(0, y), (width, y)], fill="red", width=2)
            
            # 添加网格编号
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            for i in range(3):
                for j in range(3):
                    grid_id = i * 3 + j + 1
                    x = j * third_w + 10
                    y = i * third_h + 10
                    draw.text((x, y), str(grid_id), fill="red", font=font)
            
            if output_path:
                image.save(output_path, quality=95)
                logger.info(f"九宫格覆盖层已保存: {output_path}")
            else:
                image.show()
            
            return True
            
        except Exception as e:
            logger.error(f"创建九宫格覆盖层失败: {str(e)}")
            return False
    
    def normalize_text(self, text: str) -> str:
        """
        标准化文本内容
        
        Args:
            text: 原始文本
            
        Returns:
            标准化后的文本
        """
        # 去除多余空格
        text = ' '.join(text.split())
        
        # 转换为标准标点符号
        text = text.replace('，', ',').replace('。', '.').replace('；', ';')
        
        # 去除特殊字符
        text = ''.join(c for c in text if c.isprintable() or c in '，。；、')
        
        return text.strip()
    
    def preprocess_dataset(self, input_dir: str, output_dir: str, 
                          apply_augmentation: bool = False, 
                          augmentation_factor: int = 3) -> bool:
        """
        预处理整个数据集
        
        Args:
            input_dir: 输入数据目录
            output_dir: 输出数据目录
            apply_augmentation: 是否应用数据增强
            augmentation_factor: 数据增强倍数
            
        Returns:
            是否成功
        """
        try:
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 查找所有JSON文件
            json_files = list(Path(input_dir).glob("*.json"))
            
            if not json_files:
                logger.error(f"在 {input_dir} 中未找到数据文件")
                return False
            
            processed_count = 0
            
            for json_file in json_files:
                try:
                    # 读取标注文件
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    image_filename = data["image_path"]
                    image_path = os.path.join(input_dir, image_filename)
                    
                    if not os.path.exists(image_path):
                        logger.warning(f"图像文件不存在，跳过: {image_path}")
                        continue
                    
                    # 基础处理
                    base_output_path = os.path.join(output_dir, image_filename)
                    self.preprocess_image(image_path, base_output_path, apply_augmentation=False)
                    
                    # 保存处理后的标注
                    output_json_path = os.path.join(output_dir, json_file.name)
                    with open(output_json_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    processed_count += 1
                    
                    # 数据增强
                    if apply_augmentation:
                        for i in range(augmentation_factor):
                            aug_image_filename = f"{Path(image_filename).stem}_aug{i+1}{Path(image_filename).suffix}"
                            aug_output_path = os.path.join(output_dir, aug_image_filename)
                            
                            # 应用增强
                            self.preprocess_image(image_path, aug_output_path, apply_augmentation=True)
                            
                            # 保存增强后的标注（复制原始标注）
                            aug_json_filename = f"{Path(json_file.name).stem}_aug{i+1}.json"
                            aug_json_path = os.path.join(output_dir, aug_json_filename)
                            
                            aug_data = data.copy()
                            aug_data["image_path"] = aug_image_filename
                            aug_data["metadata"]["augmented"] = True
                            aug_data["metadata"]["augmentation_id"] = i + 1
                            
                            with open(aug_json_path, 'w', encoding='utf-8') as f:
                                json.dump(aug_data, f, ensure_ascii=False, indent=2)
                            
                            processed_count += 1
                    
                except Exception as e:
                    logger.error(f"处理文件失败 {json_file}: {str(e)}")
                    continue
            
            logger.info(f"数据集预处理完成: {processed_count} 个文件")
            return True
            
        except Exception as e:
            logger.error(f"数据集预处理失败: {str(e)}")
            return False


def main():
    """主函数，用于命令行调用"""
    import argparse
    
    parser = argparse.ArgumentParser(description='预处理中医脉象九宫格数据')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 预处理单个图像
    preprocess_parser = subparsers.add_parser('preprocess', help='预处理单个图像')
    preprocess_parser.add_argument('image_path', help='输入图像路径')
    preprocess_parser.add_argument('output_path', help='输出图像路径')
    preprocess_parser.add_argument('--augment', action='store_true', help='应用数据增强')
    
    # 创建九宫格覆盖层
    grid_parser = subparsers.add_parser('grid', help='创建九宫格覆盖层')
    grid_parser.add_argument('image_path', help='输入图像路径')
    grid_parser.add_argument('--output', help='输出图像路径')
    
    # 预处理数据集
    dataset_parser = subparsers.add_parser('dataset', help='预处理整个数据集')
    dataset_parser.add_argument('input_dir', help='输入数据目录')
    dataset_parser.add_argument('output_dir', help='输出数据目录')
    dataset_parser.add_argument('--augment', action='store_true', help='应用数据增强')
    dataset_parser.add_argument('--augment_factor', type=int, default=3, help='数据增强倍数')
    
    args = parser.parse_args()
    
    preprocessor = DataPreprocessor()
    
    if args.command == 'preprocess':
        result = preprocessor.preprocess_image(args.image_path, args.output_path, args.augment)
        print(f"预处理{'成功' if result is not None else '失败'}")
    elif args.command == 'grid':
        success = preprocessor.create_grid_overlay(args.image_path, args.output)
        print(f"九宫格覆盖层创建{'成功' if success else '失败'}")
    elif args.command == 'dataset':
        success = preprocessor.preprocess_dataset(args.input_dir, args.output_dir, 
                                                args.augment, args.augment_factor)
        print(f"数据集预处理{'成功' if success else '失败'}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()