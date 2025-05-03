import cv2
import torch
import numpy as np
import time
from pathlib import Path

class ObjectDetector:
    def __init__(self, weights="models/yolov5s.pt", conf_threshold=0.45, iou_threshold=0.45):
        # Load YOLOv5 model
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=weights)
        
        # Set model parameters
        self.model.conf = conf_threshold # Confidence threshold
        self.model.iou = iou_threshold # NMS IoU threshold
        self.model.classes = None # Filter by class, i.e. = [0, 15, 16] for COCO person
        self.model.multi_label = False # NMS multiple labels per box
        self.model.max_det = 20 # Maximum detections per image
        
        # Use CUDA if available
        self.model.to('cuda' if torch.cuda.is_available() else 'cpu')
        self.device = next(self.model.parameters()).device
        
        # Class names
        self.class_names = self.model.names
        
        # Define colors for each class
        np.random.seed(42) # for reproducibility
        self.colors = {i: tuple(map(int, np.random.randint(0, 255, size=3))) for i in range(len(self.class_names))}
        
        # Performance tracking
        self.frame_count = 0
        self.start_time = time.time()
        self.fps = 0
        
        print(f"YOLOv5 initialized on {self.device}")
        
    def process_frame(self, frame):
        # Create a copy for drawing
        output_frame = frame.copy()
        # Increment frame counter for FPS calculation
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 1:
            self.fps = self.frame_count / elapsed_time
            self.frame_count = 0
            self.start_time = time.time()
            
        # Draw FPS on frame
        cv2.putText(output_frame, f"FPS: {self.fps:.1f}",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)   
        # Perform inference
        results = self.model(frame)
        # Extract detections
        predictions = results.pandas().xyxy[0]
        # Draw bounding boxes and labels
        for _, detection in predictions.iterrows():
            # Extract information
            x1, y1, x2, y2 = int(detection['xmin']), int(detection['ymin']), int(detection['xmax']), int(detection['ymax'])
            conf = float(detection['confidence'])
            class_id = int(detection['class'])
            class_name = detection['name']
            
            # Get color for this class
            color = self.colors[class_id]
            
            # Draw bounding box
            cv2.rectangle(output_frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label background
            text = f"{class_name} {conf:.2f}"
            text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(output_frame, (x1, y1 - text_size[1] - 10), (x1 + text_size[0] + 10, y1), color, -1)
            
            # Draw text
            cv2.putText(output_frame, text, (x1 + 5, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                       
        # Draw model info
        cv2.putText(output_frame, f"Model: YOLOv5 | Objects: {len(predictions)}",
                   (10, output_frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                   
        return output_frame