import cv2
import numpy as np

class ColorTracker:
    def __init__(self):
        self.color_values = {
            'red': [0, 0, 255],  # BGR value for red
            'green': [0, 255, 0],  # BGR value for green
            'blue': [255, 0, 0]  # BGR value for blue
        }
        self.camera = cv2.VideoCapture(0)

    def resize_and_blur(self, img):
        img = cv2.resize(img, (640, 480))
        img = cv2.GaussianBlur(img, (3, 3), 3)
        return img

    def get_contours(self, img, color):
        lower = np.array(self.color_values[color])
        upper = np.array(self.color_values[color])
        mask = cv2.inRange(img, lower, upper)
        return cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

    def draw_bounding_box(self, img, contours, color):
        if contours:
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, color, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        return img

    def display(self, img):
        cv2.imshow('Image', img)
        cv2.waitKey(1)

    def run(self):
        while True:
            ret, frame = self.camera.read()
            if not ret:
                break
            frame = self.resize_and_blur(frame)
            for color in self.color_values:
                contours = self.get_contours(frame, color)
                frame = self.draw_bounding_box(frame, contours, color)
            self.display(frame)

        self.camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    tracker = ColorTracker()
    tracker.run()