# Air Writing

![Banner](2_title_banner.png)

## Overview

Air Writing is a computer vision application that transforms hand gestures into digital drawings. This innovative tool uses your webcam to track hand movements and allows you to draw in the air without physical touch interfaces.

## Features

- **Intuitive Air Drawing**: Draw by moving your index finger in the air
- **Multi-color Support**: Choose between red, green, blue, and black colors
- **Gesture Controls**: 
  - Raise index finger to draw
  - Lower index finger to stop drawing
  - Raise thumb to erase
- **Interactive UI**: 
  - Color selection panel
  - Undo and clear buttons
- **Smooth Drawing**: Implementation of motion smoothing for better line quality

## Requirements

- **Python 3.10** (Note: This application is specifically designed for Python 3.10 and may not work correctly with newer versions)
- OpenCV
- MediaPipe
- NumPy

## Installation

1. Clone this repository
```bash
git clone https://github.com/nour23019870/air-writing.git
cd air-writing
```

2. Install the required packages
```bash
pip install -r requirements.txt
```

Or install them manually:
```bash
pip install opencv-python mediapipe numpy
```

## Usage

1. Run the main application:
```bash
python main.py
```

2. Position yourself in front of the webcam

3. Use gestures to interact with the application:
   - Point your index finger upward to start drawing
   - Lower your index finger to stop drawing
   - Select colors from the bottom panel
   - Use the top toolbar for undo and clear functions
   - Raise your thumb to erase nearby strokes

4. Press 'Q' to quit the application

## How It Works

Air Writing uses MediaPipe's hand tracking technology to detect and track hand landmarks in real-time. The application tracks specific finger positions to determine whether the user is drawing, selecting tools, or performing other actions. A smoothing algorithm is applied to the detected positions to ensure smooth and natural drawing.

## Project Structure

```
air-writing/
│
├── main.py          # Main application code
├── README.md        # Project documentation
├── requirements.txt # Package dependencies
├── 2_title_banner.png # Project banner
└── air_writing.docx   # Additional documentation
```

## Future Enhancements

- Save drawings to images
- Multiple hand support
- Additional drawing tools (shapes, text)
- Adjustable line thickness
- More sophisticated smoothing algorithms

## License

[MIT License](https://opensource.org/licenses/MIT)

## Acknowledgments

- [MediaPipe](https://mediapipe.dev/) for hand tracking capabilities
- [OpenCV](https://opencv.org/) for computer vision functionality

---

Created: April 28, 2025