from fastapi import APIRouter, Body

router = APIRouter()

@router.post("/api/analisa-gejala")
async def analisa_gejala(
    label: str = Body(...),
    gejala: list[str] = Body(...)
):
    skor = 0

    if label == "cataract":
        skor += 3
    elif label == "not_eye":
        skor -= 5

    if "blurred" in gejala:
        skor += 1
    if "glare" in gejala:
        skor += 1
    if "halos" in gejala:
        skor += 1
    if "over50" in gejala:
        skor += 1

    if skor < 0:
        hasil = "Gambar tidak valid atau tidak terindikasi sebagai mata."
    elif skor <= 1:
        hasil = "Mata terdeteksi normal, tidak terindikasi katarak."
    elif skor == 2:
        hasil = "Tidak terindikasi katarak, namun disarankan pemeriksaan rutin."
    elif skor <= 4:
        hasil = "Sangat mungkin gejala awal katarak. Disarankan konsultasi ke dokter mata."
    else:
        hasil = "Terindikasi katarak. Sangat disarankan untuk konsultasi ke dokter mata."

    return {
        "skor": skor,
        "hasil_akhir": hasil
    }
