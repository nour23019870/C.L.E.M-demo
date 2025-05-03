# Custom Object Detection with YOLOv5

This project provides a streamlined implementation of YOLOv5 for custom object detection. It includes only the essential components needed for training and detection, making it easier to use without the complexity of the full repository.

**Developer: L1ght**

## Project Structure

```
item-detection/
├── dataset/               # Your custom dataset
│   ├── images/            # Images for training and validation
│   │   ├── train/         # Training images
│   │   └── val/           # Validation images
│   └── labels/            # Labels for training and validation
│       ├── train/         # Training labels
│       └── val/           # Validation labels
├── models/                # Model architectures
├── utils/                 # Utility functions
├── data/                  # Configuration files
│   └── custom.yaml        # Custom dataset configuration
├── collect_data.py        # Tool for collecting training data using webcam
├── collect_from_files.py  # Tool for collecting training data from image files
├── train_custom_model.py  # Simplified script for training
├── main.py                # Live object detection script
├── train.py               # YOLOv5 training script
├── detect.py              # YOLOv5 detection script
├── val.py                 # YOLOv5 validation script
└── requirements.txt       # Dependencies
```

## Setup Instructions

1. Create a Python virtual environment (recommended):
   ```
   python -m venv env
   env\Scripts\activate  # Windows
   source env/bin/activate  # Linux/Mac
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Download the YOLOv5 weights:
   ```
   # Small model (recommended for most cases)
   wget https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt
   
   # OR with curl
   curl -L https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt -o yolov5s.pt
   
   # OR download manually from:
   # https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt
   ```
   
   Note: You can also use other YOLOv5 model variants like yolov5m.pt, yolov5l.pt, or yolov5x.pt for better accuracy at the cost of speed.

## How to Use

### Method 1: Collecting Training Data with Webcam

If your webcam is working correctly, you can collect training data with:

```bash
python collect_data.py
```

Use the following commands during collection:
- `C`: Create a new class
- `S`: Select an existing class
- `SPACE`: Capture a single image
- `A`: Toggle auto-capture mode (captures every 0.5 seconds)
- `ESC/Q`: Quit

### Method 2: Using Existing Images

If you already have images or your webcam isn't working, use:

```bash
python collect_from_files.py --folder "path/to/images" --class-name "object_name"
```

Example:
```bash
python collect_from_files.py --folder "D:\images\keyboard" --class-name "keyboard"
```

View dataset statistics:
```bash
python collect_from_files.py --stats
```

## How to Add New Items (Objects) to Detect

### Step 1: Plan Your Data Collection
Before adding new items, plan what objects you want to detect. For best results:
- Choose distinctive objects with clear visual features
- Plan to collect 50-100 images per object
- Consider different angles, lighting conditions, and backgrounds

### Step 2: Add Items Using Webcam
1. Run the data collection tool:
   ```bash
   python collect_data.py
   ```

2. Create a new class for your object:
   - Press `C` in the image window
   - Enter your object name in the terminal (e.g., "coffee_mug")

3. Position your object in the camera view:
   - Hold the object in different positions and angles
   - Try different backgrounds
   - Vary the distance from the camera

4. Capture images:
   - Press `SPACE` to capture individual images
   - OR press `A` to enable auto-capture (takes a photo every 0.5 seconds)
   - Collect at least 50 images per object
   - Move the object around to capture different angles

5. Add more objects (optional):
   - Press `C` to add another class
   - Repeat the process for each new object

### Step 3: Add Items Using Existing Images
If you have existing images or your webcam isn't working:

1. Organize your images:
   - Create a folder for each object (e.g., "coffee_mug", "keyboard", etc.)
   - Place 50-100 images of each object in their respective folders

2. Import the images:
   ```bash
   python collect_from_files.py --folder "path/to/object_images" --class-name "object_name"
   ```

3. Repeat for each object category.

### Step 4: Check Your Dataset

After adding images for all your items:
```bash
python collect_from_files.py --stats
```

This will show statistics about your dataset, including:
- Number of classes
- Number of images per class
- Distribution between training and validation sets

### Step 5: Train Your Model With New Items

Once you've added all your objects:
```bash
python train_custom_model.py --epochs 100 --batch-size 16 --img-size 640
```

The model will train to recognize all the classes you've added.

### Training Your Model

Train your custom object detection model with:

```bash
python train_custom_model.py
```

Options:
```bash
python train_custom_model.py --epochs 100 --batch-size 16 --weights yolov5s.pt --img-size 640
```

### Running Live Detection

After training, run live detection with:

```bash
python live_detection.py --weights runs/train/exp/weights/best.pt
```

## Advanced Usage

### YOLOv5 Original Scripts

This project includes stripped-down versions of the original YOLOv5 scripts:

- `train.py`: Full training script with all options
- `detect.py`: Detection script for images and videos
- `val.py`: Validation script for evaluating models

### Custom Training Configuration

Edit `data/custom.yaml` to change dataset paths and class names.

## Recommendations for Best Results

1. Collect 50-100 images per class for good results
2. Use varied lighting conditions and backgrounds
3. Include the object at different angles and distances
4. For more precise bounding boxes, consider using a dedicated labeling tool like [LabelImg](https://github.com/tzutalin/labelImg)

## Troubleshooting

If you encounter camera issues with `collect_data.py`, try:
1. Using `collect_from_files.py` instead
2. Changing the camera index in the script from 0 to 1
3. Installing updated camera drivers

For training issues:
1. Ensure you have at least 20-30 images per class
2. Check that your GPU drivers are up to date if using CUDA
3. Reduce batch size if running out of memory