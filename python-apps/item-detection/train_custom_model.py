import os
import sys
import yaml
import torch
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Train YOLOv5 on Custom Dataset")
    parser.add_argument('--epochs', type=int, default=100,
                        help='number of epochs to train for')
    parser.add_argument('--batch-size', type=int, default=16,
                        help='batch size for training')
    parser.add_argument('--weights', type=str, default='yolov5s.pt',
                        help='initial weights path or model size (yolov5s, yolov5m)')
    parser.add_argument('--img-size', type=int, default=640,
                        help='image size for training')
    parser.add_argument('--device', default='',
                        help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    args = parser.parse_args()
    
    # Check that dataset exists
    dataset_dir = Path("dataset")
    if not dataset_dir.exists():
        print(f"Error: Dataset directory not found at {dataset_dir}")
        print("Please run collect_data.py first to create your dataset")
        return
    
    # Check for classes.txt
    classes_file = dataset_dir / "classes.txt"
    if not classes_file.exists():
        print(f"Error: Classes file not found at {classes_file}")
        print("Please run collect_data.py first to create your dataset")
        return
    
    # Read class names
    with open(classes_file, "r") as f:
        class_names = [line.strip() for line in f.readlines()]
    
    # Update custom.yaml with correct class count and names
    custom_yaml = Path("data") / "custom.yaml"
    if custom_yaml.exists():
        with open(custom_yaml, "r") as f:
            yaml_data = yaml.safe_load(f)
        
        yaml_data["nc"] = len(class_names)
        yaml_data["names"] = class_names
        
        with open(custom_yaml, "w") as f:
            yaml.dump(yaml_data, f, default_flow_style=False)
    
    print(f"Training YOLOv5 model on custom dataset with {len(class_names)} classes: {', '.join(class_names)}")
    
    # Check for GPU
    has_cuda = torch.cuda.is_available()
    if has_cuda:
        print(f"CUDA GPU detected: {torch.cuda.get_device_name(0)}")
    else:
        print("No CUDA GPU detected. Training on CPU will be slow!")
        if args.device == '':
            args.device = 'cpu'
    
    # Construct the training command
    cmd = f"python train.py --img {args.img_size} --batch {args.batch_size} --epochs {args.epochs} "
    cmd += f"--data data/custom.yaml --weights {args.weights} --device {args.device}"
    
    print(f"Running training with command: {cmd}")
    os.system(cmd)
    
    print("Training complete! Your model is saved in the 'runs/train/' directory.")
    print("You can use it with live_detection.py by specifying the weights path.")

if __name__ == "__main__":
    main()
