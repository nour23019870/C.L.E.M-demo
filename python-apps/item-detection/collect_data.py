import cv2
import os
import time
import shutil
import random
import numpy as np
from pathlib import Path

class ItemDataCollector:
    def __init__(self):
        self.dataset_dir = Path("dataset")
        self.images_train_dir = self.dataset_dir / "images" / "train"
        self.images_val_dir = self.dataset_dir / "images" / "val"
        self.labels_train_dir = self.dataset_dir / "labels" / "train"
        self.labels_val_dir = self.dataset_dir / "labels" / "val"
        
        # Ensure directories exist
        self.images_train_dir.mkdir(exist_ok=True, parents=True)
        self.images_val_dir.mkdir(exist_ok=True, parents=True)
        self.labels_train_dir.mkdir(exist_ok=True, parents=True)
        self.labels_val_dir.mkdir(exist_ok=True, parents=True)
        
        # Counter for image filenames
        self.image_counter = 0
        
        # Training/validation split ratio
        self.validation_split = 0.2  # 20% for validation
        
        # Classes and categories
        self.classes = []
        self.class_indices = {}
        
        # Check for CUDA
        self.has_cuda = cv2.cuda.getCudaEnabledDeviceCount() > 0
        
        # Load existing class list if available
        self.load_classes()
        
    def load_classes(self):
        class_file = self.dataset_dir / "classes.txt"
        if class_file.exists():
            with open(class_file, "r") as f:
                self.classes = [line.strip() for line in f.readlines()]
                self.class_indices = {cls: i for i, cls in enumerate(self.classes)}
            print(f"Loaded {len(self.classes)} existing classes: {', '.join(self.classes)}")
    
    def save_classes(self):
        class_file = self.dataset_dir / "classes.txt"
        with open(class_file, "w") as f:
            for cls in self.classes:
                f.write(f"{cls}\n")
        
        # Also create a data.yaml file for training
        data_yaml = self.dataset_dir / "data.yaml"
        with open(data_yaml, "w") as f:
            f.write(f"path: ../dataset\n")
            f.write(f"train: images/train\n")
            f.write(f"val: images/val\n\n")
            f.write(f"nc: {len(self.classes)}\n")
            f.write(f"names: {self.classes}\n")
        
    def add_class(self, class_name):
        if class_name not in self.classes:
            self.classes.append(class_name)
            self.class_indices[class_name] = len(self.classes) - 1
            self.save_classes()
            print(f"Added new class: {class_name} (index: {self.class_indices[class_name]})")
        return self.class_indices[class_name]
    
    def collect_images(self):
        # Initialize webcam with improved approach
        print(f"Opening camera...")
        
        # Try different camera backends - prioritizing DirectShow on Windows which usually works better
        backends = [
            cv2.CAP_DSHOW,        # DirectShow (usually best on Windows)
            cv2.CAP_ANY,          # Auto-detect
            cv2.CAP_MSMF,         # Microsoft Media Foundation
            cv2.CAP_V4L2,         # Video for Linux
            cv2.CAP_GSTREAMER     # GStreamer
        ]
        
        # Add debug info for the user
        print("\nAttempting to access camera. If you're having issues, try:")
        print("1. Make sure your webcam is properly connected")
        print("2. Check if another application is using the webcam")
        print("3. Try different USB ports if the camera is external")
        print("4. Unplug and replug the camera\n")
        
        # Force disconnection of any previously opened cameras
        for i in range(5):  # Try to release cameras on indices 0-4
            temp_cam = cv2.VideoCapture(i)
            temp_cam.release()
            
        video_capture = None
        for backend in backends:
            backend_name = {
                cv2.CAP_DSHOW: "DirectShow",
                cv2.CAP_ANY: "Auto-detect",
                cv2.CAP_MSMF: "Microsoft Media Foundation",
                cv2.CAP_V4L2: "Video4Linux",
                cv2.CAP_GSTREAMER: "GStreamer"
            }.get(backend, f"Backend {backend}")
            
            print(f"\nTrying backend: {backend_name}")
            
            for camera_index in [0, 1, 2, -1]:  # Add -1 as auto-detect option
                # Release any previously opened camera for this attempt
                if video_capture is not None:
                    video_capture.release()
                    video_capture = None
                
                try:
                    print(f"  - Trying camera index {camera_index}...")
                    video_capture = cv2.VideoCapture(camera_index, backend)
                    
                    # Add a delay to give the camera time to initialize
                    time.sleep(2)
                    
                    # Check if camera opened successfully
                    if video_capture.isOpened():
                        ret, test_frame = video_capture.read()
                        if ret and test_frame is not None and test_frame.size > 0:
                            # Get camera properties
                            original_width = video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
                            original_height = video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
                            original_fps = video_capture.get(cv2.CAP_PROP_FPS)
                            
                            print(f"  ✓ SUCCESS! Camera opened with {backend_name}")
                            print(f"    Original resolution: {original_width}x{original_height}, FPS: {original_fps}")
                            
                            # Configure camera properties for higher resolution
                            video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                            video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                            
                            # Verify the new settings
                            actual_width = video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
                            actual_height = video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
                            print(f"    Configured resolution: {actual_width}x{actual_height}")
                            
                            # Successfully initialized camera
                            break
                        else:
                            print(f"  ✗ Camera opened but couldn't read frame")
                            if video_capture is not None:
                                video_capture.release()
                                video_capture = None
                    else:
                        print(f"  ✗ Could not open camera")
                except Exception as e:
                    print(f"  ✗ Error: {str(e)}")
                    if video_capture is not None:
                        video_capture.release()
                        video_capture = None
            
            if video_capture is not None and video_capture.isOpened():
                ret, test_frame = video_capture.read()
                if ret and test_frame is not None and test_frame.size > 0:
                    break
                else:
                    video_capture.release()
                    video_capture = None
        
        # Final check if camera was opened successfully
        if video_capture is None or not video_capture.isOpened():
            print("\n❌ ERROR: Could not open camera with any combination of index and backend.")
            print("   Please ensure your webcam is properly connected and not being used by another application.")
            print("   You might also need to check device drivers or try a different webcam.\n")
            return False
            
        print("\n✅ Camera initialized successfully! Proceeding with data collection...\n")
        
        # Variables for FPS calculation
        prev_time = time.time()
        frame_count = 0
        fps = 0
        
        # Capture state
        class_name = None
        capturing = False
        capture_interval = 0.5  # seconds between automatic captures
        last_capture_time = 0
        capture_mode = "manual"  # or "auto"
        
        print("\n=== YOLOv5 Object Data Collection Tool ===")
        print("First, choose or create a class name for the object")
        print("Then position the object in the camera view and start capturing")
        print("\nCommands:")
        print("  C: Create new class (enter name in terminal)")
        print("  S: Select existing class (from terminal)")
        print("  SPACE: Capture single image")
        print("  A: Toggle auto-capture mode (captures every 0.5 seconds)")
        print("  ESC/Q: Quit\n")
        print("IMPORTANT: When prompted for input, switch to the terminal window!")
        
        window_name = "Object Data Collection"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1280, 720)
        
        try:
            while True:
                # Capture frame-by-frame
                ret, frame = video_capture.read()
                
                if not ret:
                    print("Failed to grab frame")
                    break
                
                # Calculate FPS
                frame_count += 1
                current_time = time.time()
                if current_time - prev_time >= 1.0:
                    fps = frame_count / (current_time - prev_time)
                    prev_time = current_time
                    frame_count = 0
                
                # Create a copy to draw UI elements on
                display_frame = frame.copy()
                
                # Display FPS on the frame
                cv2.putText(display_frame, f"FPS: {fps:.1f}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                if self.has_cuda:
                    cv2.putText(display_frame, "CUDA Enabled", (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Display current class and instructions
                info_bg = np.zeros((200, display_frame.shape[1], 3), dtype=np.uint8)
                
                if class_name:
                    cv2.putText(info_bg, f"Selected Class: {class_name}", (10, 40), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    # Show how many images have been captured for this class
                    train_count = len(list(self.images_train_dir.glob(f"{class_name}_*.jpg")))
                    val_count = len(list(self.images_val_dir.glob(f"{class_name}_*.jpg")))
                    total_count = train_count + val_count
                    
                    cv2.putText(info_bg, f"Images: {total_count} (Train: {train_count}, Val: {val_count})", 
                               (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    
                    if capture_mode == "auto" and capturing:
                        cv2.putText(info_bg, "AUTO-CAPTURE ON", (10, 120), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                else:
                    cv2.putText(info_bg, "No class selected. Press 'C' to create or 'S' to select.", 
                               (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                    cv2.putText(info_bg, "IMPORTANT: When prompted, type your response in the terminal window!", 
                               (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Add instruction reminder at bottom
                cv2.putText(info_bg, "SPACE: Capture | A: Auto-capture | C: Create class | S: Select class | Q/ESC: Quit", 
                           (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                
                # Combine the frame and info background
                combined_frame = np.vstack([display_frame, info_bg])
                
                # Auto-capture if enabled
                if capturing and capture_mode == "auto" and current_time - last_capture_time >= capture_interval:
                    self.save_image(frame, class_name)
                    last_capture_time = current_time
                    
                    # Flash effect to indicate capture
                    flash = np.ones_like(combined_frame) * 255
                    cv2.addWeighted(combined_frame, 0.5, flash, 0.5, 0, combined_frame)
                
                # Show the frame
                cv2.imshow(window_name, combined_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                
                if key == 27 or key == ord('q'):  # ESC or Q
                    print("Exiting...")
                    break
                    
                elif key == ord('c'):  # Create new class
                    print("\n===== CREATE NEW CLASS =====")
                    print("Please type the name of the item/object in the terminal window")
                    print("(Switch to your terminal window now!)")
                    class_name = input("Enter new class name: ").strip()
                    if class_name:  # Check the class name is not empty
                        self.add_class(class_name)
                        print(f"Class '{class_name}' created! Switch back to the image window.")
                        print("Position your object in the camera view, then press SPACE to capture or A for auto-capture.")
                    else:
                        print("Class name cannot be empty.")
                    
                elif key == ord('s'):  # Select existing class
                    if not self.classes:
                        print("\nNo classes defined yet. Press 'C' to create a new class.")
                    else:
                        print("\n===== SELECT EXISTING CLASS =====")
                        print("Available classes:")
                        for i, cls in enumerate(self.classes):
                            print(f"{i}: {cls}")
                        print("(Switch to your terminal window now!)")
                        try:
                            selection = input("Enter class number (or name): ").strip()
                            # Try to convert to integer for index-based selection
                            try:
                                idx = int(selection)
                                if 0 <= idx < len(self.classes):
                                    class_name = self.classes[idx]
                                    print(f"Selected class: {class_name}")
                                else:
                                    print("Invalid selection number!")
                            except ValueError:
                                # If not a number, try exact name match
                                if selection in self.classes:
                                    class_name = selection
                                    print(f"Selected class: {class_name}")
                                else:
                                    print(f"No class named '{selection}' found.")
                            
                            print("Switch back to the image window.")
                            print("Position your object in the camera view, then press SPACE to capture or A for auto-capture.")
                        except Exception as e:
                            print(f"Error during selection: {e}")
                
                elif key == ord('a'):  # Toggle auto-capture
                    if class_name:
                        capturing = not capturing
                        capture_mode = "auto"
                        print(f"Auto-capture: {'ON' if capturing else 'OFF'}")
                    else:
                        print("Please select a class first!")
                
                elif key == 32:  # SPACE - Single capture
                    if class_name:
                        self.save_image(frame, class_name)
                        print(f"Captured image for class: {class_name}")
                    else:
                        print("Please select a class first!")
                        
        except Exception as e:
            print(f"Error during image collection: {e}")
        
        finally:
            # Release resources
            video_capture.release()
            cv2.destroyAllWindows()
            
            # Generate dataset stats
            self.print_dataset_stats()
            
            return True
    
    def save_image(self, frame, class_name):
        """Save an image and create a dummy label file for the selected class"""
        self.image_counter += 1
        filename_base = f"{class_name}_{self.image_counter:05d}"
        
        # Decide if this image goes to training or validation set
        is_validation = random.random() < self.validation_split
        
        if is_validation:
            image_path = self.images_val_dir / f"{filename_base}.jpg"
            label_path = self.labels_val_dir / f"{filename_base}.txt"
        else:
            image_path = self.images_train_dir / f"{filename_base}.jpg"
            label_path = self.labels_train_dir / f"{filename_base}.txt"
        
        # Save the image
        cv2.imwrite(str(image_path), frame)
        
        # Create a dummy label in YOLO format (assuming object is centered)
        # Format: class_id x_center y_center width height
        # All values are normalized between 0 and 1
        img_height, img_width = frame.shape[:2]
        
        # Create a simple dummy label in the center (spanning 50% of the image)
        class_id = self.class_indices[class_name]
        x_center = 0.5  # Center of image
        y_center = 0.5  # Center of image
        width = 0.5  # 50% of image width
        height = 0.5  # 50% of image height
        
        # Write the label file
        with open(label_path, "w") as f:
            f.write(f"{class_id} {x_center} {y_center} {width} {height}\n")
    
    def print_dataset_stats(self):
        """Print statistics about the collected dataset"""
        print("\n=== Dataset Statistics ===")
        print(f"Total classes: {len(self.classes)}")
        
        train_images = list(self.images_train_dir.glob("*.jpg"))
        val_images = list(self.images_val_dir.glob("*.jpg"))
        
        print(f"Training images: {len(train_images)}")
        print(f"Validation images: {len(val_images)}")
        
        # Class distribution
        print("\nClass distribution:")
        for cls in self.classes:
            train_count = len(list(self.images_train_dir.glob(f"{cls}_*.jpg")))
            val_count = len(list(self.images_val_dir.glob(f"{cls}_*.jpg")))
            print(f"  {cls}: {train_count + val_count} images (Train: {train_count}, Val: {val_count})")
        
        print("\nNote: Labels have been created with objects centered in the image.")
        print("For better results, consider using a labeling tool to precisely mark objects.")
        print("Ready for training!")


if __name__ == "__main__":
    collector = ItemDataCollector()
    collector.collect_images()