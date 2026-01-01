"""
中医脉象九宫格数据准备模块主入口
提供数据验证、转换和预处理的命令行工具
"""

import argparse
import sys
import os
from pathlib import Path
from .validator import DataValidator
from .converter import DataConverter
from .preprocessor import DataPreprocessor
from ..utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='中医脉象九宫格数据准备工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 验证数据
  python -m src.data_preparation validate data/raw --report validation_report.json
  
  # 转换数据格式
  python -m src.data_preparation convert data/raw data/processed --format manifest
  
  # 预处理数据集
  python -m src.data_preparation preprocess data/raw data/processed --augment --augment_factor 3
  
  # 可视化标注
  python -m src.data_preparation visualize data/raw data/visualized
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 验证命令
    validate_parser = subparsers.add_parser('validate', help='验证数据格式')
    validate_parser.add_argument('input_dir', help='输入数据目录')
    validate_parser.add_argument('--report', help='验证报告输出路径')
    
    # 转换命令
    convert_parser = subparsers.add_parser('convert', help='转换数据格式')
    convert_parser.add_argument('input_dir', help='输入数据目录')
    convert_parser.add_argument('output_dir', help='输出数据目录')
    convert_parser.add_argument('--format', choices=['manifest', 'training'], 
                               default='manifest', help='输出格式')
    convert_parser.add_argument('--split', action='store_true', help='分割数据集')
    convert_parser.add_argument('--train_ratio', type=float, default=0.7, help='训练集比例')
    convert_parser.add_argument('--val_ratio', type=float, default=0.15, help='验证集比例')
    
    # 预处理命令
    preprocess_parser = subparsers.add_parser('preprocess', help='预处理数据')
    preprocess_parser.add_argument('input_dir', help='输入数据目录')
    preprocess_parser.add_argument('output_dir', help='输出数据目录')
    preprocess_parser.add_argument('--augment', action='store_true', help='应用数据增强')
    preprocess_parser.add_argument('--augment_factor', type=int, default=3, help='数据增强倍数')
    
    # 可视化命令
    visualize_parser = subparsers.add_parser('visualize', help='可视化标注')
    visualize_parser.add_argument('input_dir', help='输入数据目录')
    visualize_parser.add_argument('output_dir', help='输出可视化目录')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'validate':
            validator = DataValidator()
            success = validator.validate_directory(args.input_dir, args.report)
            if success:
                logger.info("数据验证完成")
            else:
                logger.error("数据验证失败")
                sys.exit(1)
        
        elif args.command == 'convert':
            converter = DataConverter()
            if args.format == 'manifest':
                success = converter.create_training_manifest(args.input_dir, args.output_dir)
            else:
                success = converter.convert_to_training_format(args.input_dir, args.output_dir)
            
            if args.split:
                success = converter.split_dataset(args.output_dir, args.train_ratio, args.val_ratio) and success
            
            if success:
                logger.info("数据转换完成")
            else:
                logger.error("数据转换失败")
                sys.exit(1)
        
        elif args.command == 'preprocess':
            preprocessor = DataPreprocessor()
            success = preprocessor.preprocess_dataset(
                args.input_dir, args.output_dir, 
                args.augment, args.augment_factor
            )
            if success:
                logger.info("数据预处理完成")
            else:
                logger.error("数据预处理失败")
                sys.exit(1)
        
        elif args.command == 'visualize':
            converter = DataConverter()
            success = converter.visualize_annotations(args.input_dir, args.output_dir)
            if success:
                logger.info("可视化完成")
            else:
                logger.error("可视化失败")
                sys.exit(1)
    
    except Exception as e:
        logger.error(f"执行命令失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()