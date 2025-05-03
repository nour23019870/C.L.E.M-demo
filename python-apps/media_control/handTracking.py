import cv2
import mediapipe as mp
import time
import math
import sys
import types

# Fix the protobuf builder import issue by injecting a mock builder
# into the protobuf internal namespace if it doesn't exist
try:
    from google.protobuf.internal import builder as _builder
    print("Protobuf builder module found!")
except ImportError:
    print("Missing protobuf builder module, creating mock...")
    # Create a minimal mock builder that implements just what mediapipe needs
    builder_module = types.ModuleType('google.protobuf.internal.builder')
    
    # Add the required functions that mediapipe uses
    def build_file_mock(file_descriptor):
        return None
        
    def build_message_mock(descriptor, global_dict):
        return None
        
    def build_top_mock(descriptor, module_name, global_dict):
        return None
        
    # Set the mock functions
    builder_module.BuildFile = build_file_mock
    builder_module.BuildMessageAndEnumDescriptors = build_message_mock
    builder_module.BuildTopDescriptorsAndMessages = build_top_mock
    
    # Insert the mock module into sys.modules so mediapipe can find it
    sys.modules['google.protobuf.internal.builder'] = builder_module
    
    # Also patch the google.protobuf.internal module to include our builder
    import google.protobuf.internal
    google.protobuf.internal.builder = builder_module

class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]
        self.lmList = []
        self.results = None

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):
        xList = []
        yList = []
        bbox = []
        self.lmList = []
        if self.results and self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo] if handNo < len(self.results.multi_hand_landmarks) else None
            if myHand:
                for id, lm in enumerate(myHand.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    xList.append(cx)
                    yList.append(cy)
                    self.lmList.append([id, cx, cy])
                    if draw:
                        cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
                if xList and yList:
                    bbox = (min(xList), min(yList), max(xList), max(yList))
                    if draw:
                        cv2.rectangle(img, (bbox[0]-20, bbox[1]-20), (bbox[2]+20, bbox[3]+20), (0, 255, 0), 2)
            else:
                return [], []
        return self.lmList, bbox

    def fingersUp(self):
        fingers = []
        if self.lmList:
            # Thumb
            if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0]-1][1]:
                fingers.append(1)
            else:
                fingers.append(0)

            # Fingers
            for id in range(1, 5):
                if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id]-2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)
        else:
            fingers = [0, 0, 0, 0, 0]
        return fingers

    def findDistance(self, p1, p2, img, draw=True):
        if not self.lmList or len(self.lmList) <= max(p1, p2):
            return 0, img, [0, 0, 0, 0, 0, 0]
            
        x1, y1 = self.lmList[p1][1], self.lmList[p1][2]
        x2, y2 = self.lmList[p2][1], self.lmList[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]

    # Additional methods for multi-hand support
    def findMultiHandLandmarks(self, img):
        if hasattr(self, 'results') and self.results.multi_hand_landmarks:
            return self.results.multi_hand_landmarks, self.results.multi_handedness
        return None, None
        
    def findPositionForHand(self, img, hand_landmark, draw=True):
        xList = []
        yList = []
        bbox = []
        lmList = []
        
        for id, lm in enumerate(hand_landmark.landmark):
            h, w, c = img.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            xList.append(cx)
            yList.append(cy)
            lmList.append([id, cx, cy])
            if draw:
                cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
                
        if xList and yList:
            bbox = (min(xList), min(yList), max(xList), max(yList))
            if draw:
                cv2.rectangle(img, (bbox[0]-20, bbox[1]-20), (bbox[2]+20, bbox[3]+20), (0, 255, 0), 2)
                
        return lmList, bbox
        
    def fingersUpForHand(self, lmList):
        fingers = []
        if lmList and len(lmList) > max(self.tipIds):
            # Thumb
            if lmList[self.tipIds[0]][1] > lmList[self.tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
                
            # Fingers
            for id in range(1, 5):
                if lmList[self.tipIds[id]][2] < lmList[self.tipIds[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)
        else:
            fingers = [0, 0, 0, 0, 0]
                
        return fingers
        
    def findDistanceForHand(self, p1, p2, lmList, img, draw=True):
        if not lmList or len(lmList) <= max(p1, p2):
            return 0, img, [0, 0, 0, 0, 0, 0]
            
        x1, y1 = lmList[p1][1], lmList[p1][2]
        x2, y2 = lmList[p2][1], lmList[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]

def main():
    pTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()
    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img)
        if lmList:
            print(lmList[4])
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
        cv2.imshow("Image", img)
        cv2.waitKey(1)

if __name__ == "__main__":
    main()
