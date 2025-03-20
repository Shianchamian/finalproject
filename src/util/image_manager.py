import cv2
import numpy as np
import sys

try:
    # Try importing the lightweight TFLite runtime first
    from tflite_runtime.interpreter import Interpreter
    # print("Using tflite-runtime")
except ImportError:
    try:
        # If tflite-runtime is not available, fallback to full TensorFlow
        from tensorflow.lite.python.interpreter import Interpreter
        # print("Using full TensorFlow")
    except ImportError:
        raise ImportError("Neither tflite-runtime nor TensorFlow is installed. Please install one.")


class ImageManager():
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_face_model()
        self.init_detect_model()

    def init_face_model(self):
        self.face_model = Interpreter(model_path="models/mobilefacenet.tflite")
        self.face_model.allocate_tensors()
        self.input_details = self.face_model.get_input_details()
        self.output_details = self.face_model.get_output_details()

    def init_detect_model(self):
        self.detect_model = Interpreter(model_path="models/face_detection.tflite")
        self.detect_model.allocate_tensors()
        self.detect_input_details = self.detect_model.get_input_details()
        self.detect_output_details = self.detect_model.get_output_details()

    def extract_features(self, image):
        """Extract facial feature vector using MobileFaceNet."""
        # Resize the image to match the input size of the model (112x112)
        img = cv2.resize(image, (112, 112))
    
        # Normalize pixel values to the range [-1, 1]
        img = img.astype(np.float32) / 127.5 - 1

        # img = np.expand_dims(img, axis=0)

         # If the model expects a batch size of 2, duplicate the image
        if self.input_details[0]['shape'][0] == 2:
            img = np.tile(img, (2, 1, 1, 1))  # Shape: (2, 112, 112, 3)

        self.face_model.set_tensor(self.input_details[0]['index'], img)
        self.face_model.invoke()
        features = self.face_model.get_tensor(self.output_details[0]['index'])

        return features.flatten()

    def detect_faces(self, frame, threshold=0.6):

        img_resized = cv2.resize(frame, (128,128))
        img_resized = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)

        input_data = (np.expand_dims(img_resized, axis=0).astype(np.float32) - 127.5) / 127.5

        self.detect_model.set_tensor(self.detect_input_details[0]['index'], input_data)
        self.detect_model.invoke()

        boxes = self.detect_model.get_tensor(self.detect_output_details[0]['index'])[0]
        scores = self.detect_model.get_tensor(self.detect_output_details[1]['index'])[0]

        h, w, _ = frame.shape
        faces = []

        for i, score in enumerate(scores):
            if score >= threshold:
                box = boxes[i]
                x_center, y_center, box_width, box_height = box[:4]

                xmin = int((x_center - box_width / 2) * w)
                ymin = int((y_center - box_height / 2) * h)
                xmax = int((x_center + box_width / 2) * w)
                ymax = int((y_center + box_height / 2) * h)

                keypoints = []
                for j in range(4, 16, 2):
                    kp_x = int(box[j] * w) 
                    kp_y = int(box[j + 1] * h)
                    keypoints.append((kp_x, kp_y))

                faces.append((xmin, ymin, xmax, ymax))

        return faces
