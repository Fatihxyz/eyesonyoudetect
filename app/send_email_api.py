import os
import requests
from fastapi import APIRouter, Body, HTTPException
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

SENDINBLUE_API_KEY = os.getenv("SENDINBLUE_API_KEY")
SENDINBLUE_URL = "https://api.brevo.com/v3/smtp/email"

@router.post("/api/kirim-email")
async def kirim_email(
    email: str = Body(...),
    label: str = Body(...),
    info: str = Body(...),
    hasil_akhir: str = Body(...)
):
    if not SENDINBLUE_API_KEY:
        raise HTTPException(status_code=500, detail="API Key belum dikonfigurasi.")

    # Keterangan tambahan berdasarkan label hasil prediksi
    if label.lower() == "cataract":
        tips = """
        <strong>⚠️ Indikasi Katarak Terdeteksi.</strong><br>
        Disarankan segera berkonsultasi dengan dokter mata untuk pemeriksaan dan penanganan lebih lanjut.
        <br><br>
        <strong>Tips Menjaga Kesehatan Mata:</strong>
        <ul>
          <li>Gunakan kacamata hitam saat di luar ruangan untuk menghindari paparan sinar UV.</li>
          <li>Hindari merokok karena meningkatkan risiko katarak.</li>
          <li>Konsumsi makanan kaya antioksidan seperti sayuran hijau dan buah-buahan.</li>
          <li>Rutin periksa mata minimal setahun sekali, terutama jika berusia di atas 50 tahun.</li>
        </ul>
        """
    elif label.lower() == "normal":
        tips = """
        <strong>✅ Tidak ditemukan indikasi katarak.</strong><br>
        Tetap disarankan untuk melakukan pemeriksaan mata rutin, terutama bagi usia di atas 40 tahun.
        <br><br>
        <strong>Tips Menjaga Kesehatan Mata:</strong>
        <ul>
          <li>Hindari penggunaan gadget terlalu lama tanpa istirahat.</li>
          <li>Jaga pola makan seimbang dan konsumsi vitamin A.</li>
          <li>Periksa mata secara berkala, minimal satu tahun sekali.</li>
          <li>Gunakan pelindung mata saat bekerja di tempat berdebu atau silau.</li>
        </ul>
        """
    elif label.lower() == "not_eye":
        tips = """
        <strong>❌ Gambar tidak dikenali sebagai mata.</strong><br>
        Silakan unggah ulang gambar dengan posisi mata yang jelas, terang, dan fokus.
        """
    else:
        tips = "Hasil prediksi tidak dapat diproses."

    payload = {
        "sender": {
            "name": "Eyes On You",
            "email": "fatihnusantara80@gmail.com"
        },
        "to": [{"email": email}],
        "subject": "Hasil Deteksi Mata Anda - EyesOnYou",
        "htmlContent": f"""
            <h3>Hasil Deteksi:</h3>
            <p><strong>{label.upper()}</strong></p>
            <p>{info}</p>
            <hr>
            <h4>🧠 Diagnosa Akhir:</h4>
            <p>{hasil_akhir}</p>
            <hr>
            <p>{tips}</p>
            <br>
            <p style=\"color:gray; font-size:13px;\">
            Email ini dikirim otomatis oleh sistem deteksi katarak berbasis AI dari <strong>EyesOnYou</strong>.<br>
            Untuk hasil akurat, silakan tetap konsultasikan ke dokter mata.
            </p>
        """
    }

    headers = {
        "api-key": SENDINBLUE_API_KEY,
        "Content-Type": "application/json",
        "accept": "application/json"
    }

    response = requests.post(SENDINBLUE_URL, json=payload, headers=headers)

    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return {"message": "Email berhasil dikirim"}
