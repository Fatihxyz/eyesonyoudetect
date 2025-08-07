from fastapi import APIRouter
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from selenium.webdriver.support.ui import Select

router = APIRouter()

@router.get("/jadwal/rsdk-pwt")
def get_rsdk_table_parsed():
    try:
        response = requests.get("http://api.rsdk-pwt.com/dev/localrest/jadwaldokter")
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")
        rows = table.find_all("tr")

        headers = ["Poliklinik", "Dokter", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

        data = []
        last_poliklinik = ""

        for row in rows:
            cols = [td.get_text(strip=True) for td in row.find_all("td")]

            # Skip jika tidak ada isi
            if not cols or len(cols) < 2:
                continue

            # Deteksi: apakah baris ini baris baru (ada nama poliklinik)?
            if len(cols) == 9:
                last_poliklinik = cols[0]
                item = dict(zip(headers, cols))
            elif len(cols) == 8:
                # Tambahkan poliklinik sebelumnya
                item = dict(zip(headers, [last_poliklinik] + cols))
            else:
                continue  # baris tidak valid

            # Lengkapi kolom jika kurang
            while len(item) < len(headers):
                item[headers[len(item)]] = ""

            data.append(item)

        return data

    except Exception as e:
        return {"error": str(e)}

@router.get("/jadwal/rsud-sukoharjo")
def get_rsud_sukoharjo_parsed():
    # Setup Selenium
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get("https://rsud.sukoharjokab.go.id/v3/api/bridging/v1/iframe/jadwal_dokter")
    time.sleep(3)
    # Paksa DataTables menampilkan semua entri via JavaScript
    driver.execute_script("""
    let dropdown = document.querySelector('select[name="jadwal_dokter_length"]');
    if (dropdown) {
        dropdown.value = 100;
        dropdown.dispatchEvent(new Event('change'));
    }
    """)
    time.sleep(3)  # tunggu table reload


    # Pilih dropdown untuk menampilkan 100 entri (jika tersedia)
    try:
        select_element = Select(driver.find_element(By.NAME, 'jadwal_dokter_length'))
        select_element.select_by_value('100')  # atau 'All' jika tersedia
        time.sleep(3)  # tunggu table reload
    except:
        print("Dropdown jumlah entri tidak ditemukan. Melanjutkan dengan default.")

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    table = soup.find("table", {"id": "jadwal_dokter"})
    rows = table.find("tbody").find_all("tr")

    # === Mulai parsing per hari ===
    hari_list = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

    def parse_jadwal(jadwal_str):
        jadwal_per_hari = {hari: "" for hari in hari_list}
        for baris in jadwal_str.splitlines():
            for hari in hari_list:
                if baris.startswith(hari):
                    jadwal_per_hari[hari] = baris
        return jadwal_per_hari

    hasil = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 4:
            nama = cols[1].find("strong").text.strip()
            poli = cols[2].get_text(strip=True)
            jadwal_raw = cols[3].get_text(separator="\n").strip()
            jadwal_per_hari = parse_jadwal(jadwal_raw)

            entri = {
                "Poliklinik": poli,
                "Dokter": nama,
                **jadwal_per_hari
            }
            hasil.append(entri)

    print(f"Parsing selesai, jumlah entri total: {len(hasil)}")

    # === Logika filter: wajib ada "klinik mata", total maksimal 10 entri ===
    klinik_mata_entries = [e for e in hasil if 'klinik mata' in e['Poliklinik'].lower()]
    non_klinik_mata_entries = [e for e in hasil if 'klinik mata' not in e['Poliklinik'].lower()]

    final_result = []
    if klinik_mata_entries:
        final_result.append(klinik_mata_entries[0])  # minimal 1 entri klinik mata
        final_result += non_klinik_mata_entries[:9]  # tambahkan entri lain sampai total 10
    else:
        final_result = hasil[:10]  # fallback: tetap maksimal 10, walau tanpa klinik mata

    print(f"Total entri akhir: {len(final_result)}")
    if final_result:
        print("Contoh entri:", final_result[0])
    return final_result
