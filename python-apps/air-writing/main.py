import cv2
import mediapipe as mp
import numpy as np
from collections import deque

mp_hands = mp.solutions.hands

# Webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Drawing state
points = []
strokes = []
colors = {'red': (0, 0, 255), 'green': (0, 255, 0), 'blue': (255, 0, 0), 'black': (0, 0, 0)}
current_color = colors['red']
smoothing_queue = deque(maxlen=5)

# Zones
TOOL_ZONES = {
    'undo': (250, 20, 350, 80),
    'clear': (360, 20, 460, 80),
}
COLOR_ZONES = {
    'red': (50, 650, 150, 720),
    'green': (160, 650, 260, 720),
    'blue': (270, 650, 370, 720),
    'black': (380, 650, 480, 720),
}

def erase_by_thumb(thumb_pos):
    tx, ty = thumb_pos
    radius = 25
    new_strokes = []
    for stroke, color in strokes:
        new_stroke = [pt for pt in stroke if np.linalg.norm(np.array(pt) - np.array((tx, ty))) > radius]
        if len(new_stroke) > 1:
            new_strokes.append((new_stroke, color))
    return new_strokes

with mp_hands.Hands(min_detection_confidence=0.85, min_tracking_confidence=0.5, max_num_hands=1) as hands:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        canvas = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        frame_h, frame_w, _ = canvas.shape

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            lm = hand.landmark
            x8, y8 = int(lm[8].x * frame_w), int(lm[8].y * frame_h)   # Index tip
            x4, y4 = int(lm[4].x * frame_w), int(lm[4].y * frame_h)   # Thumb tip
            x6, y6 = int(lm[6].x * frame_w), int(lm[6].y * frame_h)   # Index base

            smoothing_queue.append((x8, y8))
            sx, sy = np.mean(smoothing_queue, axis=0).astype(int)

            # --- Toolbar buttons (top) ---
            for name, (x1, y1, x2, y2) in TOOL_ZONES.items():
                cv2.rectangle(canvas, (x1, y1), (x2, y2), (50, 50, 50), -1)
                cv2.putText(canvas, name, (x1 + 10, y1 + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
                if x1 <= sx <= x2 and y1 <= sy <= y2:
                    if name == 'undo' and strokes:
                        strokes.pop()
                        points.clear()
                    elif name == 'clear':
                        strokes.clear()
                        points.clear()

            # --- Color Picker (bottom) ---
            for color, (x1, y1, x2, y2) in COLOR_ZONES.items():
                cv2.rectangle(canvas, (x1, y1), (x2, y2), colors[color], -1)
                cv2.putText(canvas, color, (x1 + 5, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
                if x1 <= sx <= x2 and y1 <= sy <= y2:
                    current_color = colors[color]

            # --- Draw ---
            if y8 < y6:
                points.append((sx, sy))
            else:
                if len(points) > 1:
                    strokes.append((points.copy(), current_color))
                points.clear()

            # --- Erase with thumb ---
            if y4 < y6 - 40:
                strokes = erase_by_thumb((x4, y4))
                cv2.circle(canvas, (x4, y4), 25, (0, 255, 255), 3)

        # Draw strokes
        for stroke, color in strokes:
            for i in range(1, len(stroke)):
                cv2.line(canvas, stroke[i-1], stroke[i], color, 5)

        for i in range(1, len(points)):
            cv2.line(canvas, points[i-1], points[i], current_color, 5)

        cv2.putText(canvas, f"Color: {list(colors.keys())[list(colors.values()).index(current_color)]}",
                    (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow("Air Writing", canvas)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
