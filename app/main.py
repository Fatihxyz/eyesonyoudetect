import os
import shutil
import uuid
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.model_loader import predict_image
from app.hospital_api import get_nearby_hospitals
from app.wikipedia_api import router as wiki_router  
from app.send_email_api import router as email_router
from fastapi.staticfiles import StaticFiles
from app.gejala_analysis_api import router as gejala_router
from app.dokter_api import router as doctor_router, get_rsdk_table_parsed, get_rsud_sukoharjo_parsed


app = FastAPI()


#logo
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Menambahkan router Wikipedia API
app.include_router(wiki_router)

# Menambahkan router implementasi API email brevo
app.include_router(email_router)

#gejala user
app.include_router(gejala_router)

#jadwal dokter
app.include_router(doctor_router)

# Setup middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Setup templates untuk rendering HTML
templates = Jinja2Templates(directory="app/templates")

# Endpoint prediksi gambar mata
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    filename = f"temp_{uuid.uuid4().hex}.jpg"

    with open(filename, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        # Prediksi dengan model CNN
        result = predict_image(filename)
    except Exception as e:
        return {"error": str(e)}
    finally:
        try:
            os.remove(filename)
        except:
            pass

    return result

# Endpoint untuk mengambil data rumah sakit mata terdekat dari Overpass API (OpenStreetMap)
@app.get("/get_nearby_hospitals")
async def nearby_hospitals(lat: float, lon: float, radius: int = 5000):
    try:
        hospitals = get_nearby_hospitals(lat, lon, radius)
        if hospitals:
            return JSONResponse(content={'hospitals': hospitals}, status_code=200)
        else:
            return JSONResponse(content={'message': 'No hospitals found.'}, status_code=404)
    except Exception as e:
        return JSONResponse(content={'error': str(e)}, status_code=500)

# Endpoint halaman frontend peta lokasi klinik mata
@app.get("/map", response_class=HTMLResponse)
async def render_map(request: Request):
    return templates.TemplateResponse("map.html", {"request": request})

@app.get("/jadwal/rsud-sukoharjo", response_class=HTMLResponse)
async def rsud_sukoharjo_page(request: Request):
    return templates.TemplateResponse("jadwal_sukoharjo.html", {"request": request})

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/edukasi", response_class=HTMLResponse)
async def edukasi_page(request: Request):
    return templates.TemplateResponse("edukasi.html", {"request": request})

@app.get("/jadwal", response_class=HTMLResponse)
async def jadwal_page(request: Request):
    data_rsdk = get_rsdk_table_parsed()
    data_rsud = get_rsud_sukoharjo_parsed()
    
    print("=== RSUD Sukoharjo ===")
    if isinstance(data_rsud, list):
        print(f"Jumlah entri: {len(data_rsud)}")
        if data_rsud:
            print("Contoh entri:", data_rsud[0])
        else:
            print("⚠ Data kosong.")
    else:
        print("⚠ data_rsud bukan list:", type(data_rsud))

    
    return templates.TemplateResponse("jadwal.html", {
        "request": request,
        "data_rsdk": data_rsdk,
        "data_rsud": data_rsud
    })



@app.get("/api/statistik_katarak")
async def get_katarak_stats():
    return {
        "indonesia": {
            "penderita": "8 juta jiwa",
            "usia_rentan": "Di atas 50 tahun",
            "urutan_global": "Negara ke-2 tertinggi di Asia Tenggara"
        },
        "global": {
            "penderita": "94 juta jiwa",
            "penyebab": "Penyebab kebutaan nomor 1 di dunia",
            "data_sumber": "WHO World Report on Vision"
        }
    }


