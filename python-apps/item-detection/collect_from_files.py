import argparse
import cv2
import os
import glob
import shutil
import random
import numpy as np
from pathlib import Path
from tqdm import tqdm

class ImageFileProcessor:
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
    
    def process_folder(self, folder_path, class_name, review_images=False):
        """Process all images in a folder and add them to the dataset"""
        folder = Path(folder_path)
        
        if not folder.exists() or not folder.is_dir():
            print(f"Error: The folder {folder_path} does not exist")
            return False
            
        # Get all image files in the folder
        image_files = []
        for ext in ["*.jpg", "*.jpeg", "*.png", "*.bmp"]:
            image_files.extend(folder.glob(ext))
            image_files.extend(folder.glob(ext.upper()))
        
        if not image_files:
            print(f"Error: No image files found in {folder_path}")
            return False
            
        print(f"Found {len(image_files)} images in {folder_path}")
        print(f"Processing images for class: {class_name}")
        
        # Add the class if it doesn't exist
        class_id = self.add_class(class_name)
        
        # Process each image
        review_window_name = "Review Image" if review_images else None
        if review_images:
            cv2.namedWindow(review_window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(review_window_name, 800, 600)
            print("Reviewing images. Press:")
            print("  SPACE: Accept image")
            print("  DELETE/BACKSPACE: Skip image")
            print("  ESC: Quit review")
        
        progress_bar = tqdm(image_files)
        for img_file in progress_bar:
            progress_bar.set_description(f"Processing {img_file.name}")
            
            try:
                # Read the image
                img = cv2.imread(str(img_file))
                
                if img is None:
                    print(f"Warning: Could not read {img_file}, skipping")
                    continue
                
                # If review mode is enabled, show the image and wait for user input
                if review_images:
                    cv2.imshow(review_window_name, img)
                    key = cv2.waitKey(0) & 0xFF
                    
                    if key == 27:  # ESC
                        print("Review stopped by user")
                        break
                    elif key in [8, 127]:  # DELETE or BACKSPACE
                        print(f"Skipping {img_file.name}")
                        continue
                    # Otherwise (e.g., SPACE), continue processing
                
                # Save the image and create label
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
                
                # Save the image (convert to JPG for consistency)
                cv2.imwrite(str(image_path), img)
                
                # Create a simple label in the center (spanning 50% of the image)
                img_height, img_width = img.shape[:2]
                
                # Default center with 50% width/height
                x_center = 0.5  # Center of image
                y_center = 0.5  # Center of image
                width = 0.5  # 50% of image width
                height = 0.5  # 50% of image height
                
                # Write the label file
                with open(label_path, "w") as f:
                    f.write(f"{class_id} {x_center} {y_center} {width} {height}\n")
                    
            except Exception as e:
                print(f"Error processing {img_file.name}: {e}")
        
        if review_images:
            cv2.destroyWindow(review_window_name)
            
        return True
    
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

def main():
    print("=" * 50)
    print("YOLOv5 Dataset Creator - Import from Files")
    print("=" * 50)
    print("\nThis tool helps you import images from folders and create a YOLOv5 dataset")
    print("You can add multiple object classes by running this tool multiple times.")
    
    processor = ImageFileProcessor()
    
    # Interactive mode
    while True:
        print("\nWhat would you like to do?")
        print("1. Import images from a folder")
        print("2. Show dataset statistics")
        print("3. Quit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            # Get folder path
            print("\nEnter the folder path containing the images:")
            folder_path = input("Path: ").strip()
            
            if folder_path.startswith('"') and folder_path.endswith('"'):
                folder_path = folder_path[1:-1]  # Remove quotes if the user included them
                
            # Get class name
            print("\nEnter the class name for these images (e.g., 'car', 'person', etc.):")
            class_name = input("Class name: ").strip()
            
            if not class_name:
                print("Error: Class name cannot be empty")
                continue
                
            # Ask for review mode
            print("\nWould you like to review each image before adding it? (y/n)")
            review_mode = input("Review images? ").strip().lower()
            review_images = review_mode in ['y', 'yes']
            
            # Process the folder
            processor.process_folder(folder_path, class_name, review_images)
            
            # Print dataset statistics
            processor.print_dataset_stats()
            
        elif choice == '2':
            processor.print_dataset_stats()
            
        elif choice == '3':
            print("\nThank you for using the YOLOv5 Dataset Creator!")
            break
            
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()