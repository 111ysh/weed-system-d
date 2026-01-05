import os
import sys
import numpy as np
import cv2
import pandas as pd
from datetime import datetime
import json

def log_message(log_file, message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    print(log_entry.strip())
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)

def validate_image_files(dataset_path, log_file):
    log_message(log_file, "开始校验图像文件...")
    
    v1_images_path = os.path.join(dataset_path, "v1", "images")
    v2_images_path = os.path.join(dataset_path, "v2", "images")
    v3_path = os.path.join(dataset_path, "v3")
    
    validation_results = {
        "v1_images": {"total": 0, "valid": 0, "invalid": 0, "errors": []},
        "v2_images": {"total": 0, "valid": 0, "invalid": 0, "errors": []},
        "v3_files": {"total": 0, "valid": 0, "invalid": 0, "errors": []}
    }
    
    for version, path, key in [("v1", v1_images_path, "v1_images"), 
                                ("v2", v2_images_path, "v2_images")]:
        if not os.path.exists(path):
            log_message(log_file, f"警告: {version} 图像目录不存在: {path}", "WARNING")
            continue
        
        files = [f for f in os.listdir(path) if f.endswith('.png')]
        validation_results[key]["total"] = len(files)
        log_message(log_file, f"{version} 图像文件总数: {len(files)}")
        
        for img_file in files:
            img_path = os.path.join(path, img_file)
            try:
                img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
                if img is None:
                    validation_results[key]["invalid"] += 1
                    validation_results[key]["errors"].append(f"{img_file}: 无法读取")
                    log_message(log_file, f"错误: {img_file} 无法读取", "ERROR")
                else:
                    validation_results[key]["valid"] += 1
            except Exception as e:
                validation_results[key]["invalid"] += 1
                validation_results[key]["errors"].append(f"{img_file}: {str(e)}")
                log_message(log_file, f"错误: {img_file} - {str(e)}", "ERROR")
    
    if os.path.exists(v3_path):
        files = [f for f in os.listdir(v3_path) if f.endswith('.npy')]
        validation_results["v3_files"]["total"] = len(files)
        log_message(log_file, f"v3 融合文件总数: {len(files)}")
        
        for npy_file in files:
            npy_path = os.path.join(v3_path, npy_file)
            try:
                data = np.load(npy_path)
                if data.ndim != 3 or data.shape[2] != 6:
                    validation_results["v3_files"]["invalid"] += 1
                    validation_results["v3_files"]["errors"].append(f"{npy_file}: 通道数错误，应为6通道")
                    log_message(log_file, f"错误: {npy_file} 通道数错误，应为6通道，实际为{data.shape[2]}通道", "ERROR")
                else:
                    validation_results["v3_files"]["valid"] += 1
            except Exception as e:
                validation_results["v3_files"]["invalid"] += 1
                validation_results["v3_files"]["errors"].append(f"{npy_file}: {str(e)}")
                log_message(log_file, f"错误: {npy_file} - {str(e)}", "ERROR")
    else:
        log_message(log_file, "警告: v3 目录不存在", "WARNING")
    
    return validation_results

def validate_label_files(dataset_path, log_file):
    log_message(log_file, "开始校验标签文件...")
    
    v1_labels_path = os.path.join(dataset_path, "v1", "labels")
    v2_labels_path = os.path.join(dataset_path, "v2", "labels")
    
    validation_results = {
        "v1_labels": {"total": 0, "valid": 0, "invalid": 0, "errors": []},
        "v2_labels": {"total": 0, "valid": 0, "invalid": 0, "errors": []}
    }
    
    for version, path, key in [("v1", v1_labels_path, "v1_labels"), 
                                ("v2", v2_labels_path, "v2_labels")]:
        if not os.path.exists(path):
            log_message(log_file, f"警告: {version} 标签目录不存在: {path}", "WARNING")
            continue
        
        files = [f for f in os.listdir(path) if f.endswith('.txt')]
        validation_results[key]["total"] = len(files)
        log_message(log_file, f"{version} 标签文件总数: {len(files)}")
        
        for label_file in files:
            label_path = os.path.join(path, label_file)
            try:
                with open(label_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                valid_lines = 0
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        try:
                            class_id = int(parts[0])
                            x_center = float(parts[1])
                            y_center = float(parts[2])
                            width = float(parts[3])
                            height = float(parts[4])
                            
                            if not (0 <= class_id <= 5):
                                raise ValueError(f"类别ID超出范围: {class_id}")
                            if not (0 <= x_center <= 1 and 0 <= y_center <= 1):
                                raise ValueError(f"中心点坐标超出范围: ({x_center}, {y_center})")
                            if not (0 <= width <= 1 and 0 <= height <= 1):
                                raise ValueError(f"宽高超出范围: ({width}, {height})")
                            
                            valid_lines += 1
                        except ValueError as e:
                            validation_results[key]["invalid"] += 1
                            validation_results[key]["errors"].append(f"{label_file}: {str(e)}")
                            log_message(log_file, f"错误: {label_file} - {str(e)}", "ERROR")
                            break
                
                if valid_lines == len(lines) and len(lines) > 0:
                    validation_results[key]["valid"] += 1
                elif len(lines) == 0:
                    validation_results[key]["invalid"] += 1
                    validation_results[key]["errors"].append(f"{label_file}: 空文件")
                    log_message(log_file, f"警告: {label_file} 为空文件", "WARNING")
                
            except Exception as e:
                validation_results[key]["invalid"] += 1
                validation_results[key]["errors"].append(f"{label_file}: {str(e)}")
                log_message(log_file, f"错误: {label_file} - {str(e)}", "ERROR")
    
    return validation_results

def validate_split_files(dataset_path, log_file):
    log_message(log_file, "开始校验数据集划分文件...")
    
    train_file = os.path.join(dataset_path, "train.txt")
    val_file = os.path.join(dataset_path, "val.txt")
    
    validation_results = {
        "train_file": {"exists": False, "sample_count": 0, "errors": []},
        "val_file": {"exists": False, "sample_count": 0, "errors": []}
    }
    
    for file_type, file_path, key in [("训练集", train_file, "train_file"), 
                                       ("验证集", val_file, "val_file")]:
        if not os.path.exists(file_path):
            validation_results[key]["errors"].append(f"{file_type}文件不存在: {file_path}")
            log_message(log_file, f"错误: {file_type}文件不存在: {file_path}", "ERROR")
            continue
        
        validation_results[key]["exists"] = True
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            validation_results[key]["sample_count"] = len(lines)
            log_message(log_file, f"{file_type}样本数: {len(lines)}")
        except Exception as e:
            validation_results[key]["errors"].append(f"{str(e)}")
            log_message(log_file, f"错误: {file_type}文件读取失败 - {str(e)}", "ERROR")
    
    return validation_results

def validate_metadata(dataset_path, log_file):
    log_message(log_file, "开始校验元数据文件...")
    
    metadata_file = os.path.join(os.path.dirname(dataset_path), "dataset_metadata.csv")
    
    validation_results = {
        "metadata": {"exists": False, "sample_count": 0, "errors": []}
    }
    
    if not os.path.exists(metadata_file):
        validation_results["metadata"]["errors"].append(f"元数据文件不存在: {metadata_file}")
        log_message(log_file, f"错误: 元数据文件不存在: {metadata_file}", "ERROR")
        return validation_results
    
    validation_results["metadata"]["exists"] = True
    try:
        df = pd.read_csv(metadata_file)
        validation_results["metadata"]["sample_count"] = len(df)
        log_message(log_file, f"元数据样本数: {len(df)}")
        
        required_columns = ['date', 'sample_id', 'image_path_prefix', 'mask_path']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            validation_results["metadata"]["errors"].append(f"缺少必要列: {missing_columns}")
            log_message(log_file, f"错误: 元数据缺少必要列: {missing_columns}", "ERROR")
        
    except Exception as e:
        validation_results["metadata"]["errors"].append(f"{str(e)}")
        log_message(log_file, f"错误: 元数据文件读取失败 - {str(e)}", "ERROR")
    
    return validation_results

def generate_summary_report(validation_results, log_file):
    log_message(log_file, "\n" + "="*80)
    log_message(log_file, "数据质量校验总结报告")
    log_message(log_file, "="*80)
    
    total_valid = 0
    total_invalid = 0
    all_passed = True
    
    for category, results in validation_results.items():
        if isinstance(results, dict) and "valid" in results:
            total = results.get("total", results.get("sample_count", 0))
            valid = results.get("valid", 0)
            invalid = results.get("invalid", 0)
            errors = results.get("errors", [])
            
            total_valid += valid
            total_invalid += invalid
            
            if invalid > 0:
                all_passed = False
            
            log_message(log_file, f"\n{category}:")
            log_message(log_file, f"  总数: {total}, 有效: {valid}, 无效: {invalid}")
            if errors:
                log_message(log_file, f"  错误详情:")
                for error in errors[:10]:
                    log_message(log_file, f"    - {error}", "ERROR")
                if len(errors) > 10:
                    log_message(log_file, f"    ... 还有 {len(errors) - 10} 个错误", "WARNING")
    
    log_message(log_file, "\n" + "="*80)
    log_message(log_file, f"总计: 有效样本 {total_valid}, 无效样本 {total_invalid}")
    
    if all_passed and total_invalid == 0:
        log_message(log_file, "数据质量校验: 通过 ✓", "INFO")
        return True
    else:
        log_message(log_file, "数据质量校验: 失败 ✗", "ERROR")
        return False

def main():
    dataset_path = os.getenv("DATASET_PATH", "./datasets/processed")
    log_path = os.getenv("VALIDATION_LOG_PATH", "./data_validation.log")
    
    log_message(log_path, "="*80)
    log_message(log_path, "数据质量校验开始")
    log_message(log_path, f"数据集路径: {dataset_path}")
    log_message(log_path, f"日志路径: {log_path}")
    log_message(log_path, "="*80)
    
    if not os.path.exists(dataset_path):
        log_message(log_path, f"错误: 数据集路径不存在: {dataset_path}", "ERROR")
        sys.exit(1)
    
    validation_results = {}
    
    validation_results.update(validate_image_files(dataset_path, log_path))
    validation_results.update(validate_label_files(dataset_path, log_path))
    validation_results.update(validate_split_files(dataset_path, log_path))
    validation_results.update(validate_metadata(dataset_path, log_path))
    
    passed = generate_summary_report(validation_results, log_path)
    
    log_message(log_path, "="*80)
    log_message(log_path, "数据质量校验结束")
    log_message(log_path, "="*80)
    
    if passed:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()