import numpy as np
from tensorflow.keras.models import load_model
from .utils import preprocess_image

# Load model dengan try-except
try:
    model = load_model("model/cataract_model.h5")  # pastikan path benar
except Exception as e:
    print("❌ Gagal load model cataract_model.h5:")
    print(e)
    model = None

class_names = ['cataract', 'normal', 'not_eye']

def predict_image(path: str):
    if model is None:
        return {"label": "error", "info": "Model belum tersedia atau gagal dimuat."}

    image = preprocess_image(path)
    image = np.expand_dims(image, axis=0)
    prediction = model.predict(image)
    label = class_names[np.argmax(prediction)]

    info = ""
    if label == "cataract":
        info = "Hasil menunjukkan indikasi katarak. Segera konsultasi dengan dokter mata."
    elif label == "not_eye":
        info = "Gambar tidak dikenali sebagai mata. Silakan upload ulang gambar mata."

    return {"label": label, "info": info}
