import cv2
import numpy as np

def preprocess_image(image_path, target_size=(224, 224)):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Gagal membaca gambar.")
    image = cv2.resize(image, target_size)
    image = image / 255.0
    return image