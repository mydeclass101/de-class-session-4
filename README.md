# Session 4 · Python สำหรับ Data Engineer

เรียน Python ตั้งแต่เริ่มต้น แล้วใช้ Python เก็บข้อมูลลง **Lakehouse (RustFS + Apache Iceberg)** ของเราเอง

- บทที่ 1–5 : พื้นฐาน Python ด้วยตัวอย่างในชีวิตประจำวัน (ร้านกาแฟ รายจ่าย วันเกิด)
- บทที่ 6 : ดึงข้อมูลจาก API และจัดการตารางด้วย pandas
- บทที่ 7 : RustFS + Iceberg: สร้าง/แก้/ย้อนเวลาตารางด้วย SQL
- บทที่ 8 : ลงมือทำ pipeline เล็ก ๆ : ไฟล์ CSV + API → bronze → silver → gold

เขียนโค้ดใน **VS Code** (notebook `.ipynb`) บนเครื่องตัวเอง ส่วน Docker รันแค่ RustFS กับ API จำลอง

## 1. สิ่งที่ต้องติดตั้ง (ครั้งเดียว)

| โปรแกรม | หมายเหตุ |
|---|---|
| [Python 3.12](https://www.python.org/downloads/) (3.11–3.13 ได้) | **Windows: ติ๊ก "Add python.exe to PATH"** ตอนติดตั้ง |
| [VS Code](https://code.visualstudio.com/) | |
| VS Code extension **Python** และ **Jupyter** (ของ Microsoft) | กด `Ctrl+Shift+X` แล้วค้นชื่อ |
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | ใช้มาตั้งแต่ session 2 แล้ว |
| git | |

## 2. เตรียม repo (ทำก่อนวันเรียน ~10 นาที)

```bash
git clone git@github.com:mydeclass101/de-class-session-4.git
cd de-class-session-4
code .                       # เปิดโฟลเดอร์นี้ใน VS Code (หรือ File > Open Folder)
```

ใน VS Code เปิด Terminal (`` Ctrl+` ``) แล้วพิมพ์ทีละบรรทัด

**Windows**

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env
docker compose up -d
```

**macOS / Linux**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
docker compose up -d
```

- `.venv` = กล่อง Python ของ repo นี้โดยเฉพาะ library ที่ติดตั้งจะอยู่ในนี้ ไม่ปนกับเครื่อง
- `.env` = ค่าตั้งค่าและรหัสผ่าน (ไม่ขึ้น git)
- `docker compose up -d` = เปิด RustFS และ API จำลอง · เช็กด้วย `docker compose ps` ต้องเห็น `de4-rustfs` เป็น `healthy`

> ⚠️ ถ้ายังเปิด stack ของ session 2 (RustFS port 9000/9001) อยู่ ให้ปิดก่อน: ไปที่โฟลเดอร์ session 2 แล้ว `docker compose stop`

## 3. เปิด notebook และเลือก kernel

1. เปิด `lessons/00_setup_check.ipynb`
2. มุมขวาบนกด **Select Kernel** → **Python Environments** → เลือก **.venv**
3. กด **Shift + Enter** ทีละ cell ทุก cell ต้องขึ้น ✅ (ถ้า VS Code ถามให้ติดตั้ง `ipykernel` กด Install)

ผ่านครบ = พร้อมเรียน

| หน้าเว็บ | URL |
|---|---|
| RustFS (ดูไฟล์ใน bucket) | http://localhost:9001 · user `student` / `classroom` |
| เอกสาร API จำลอง | http://localhost:8000/docs |

ครั้งต่อไป: เปิด Docker Desktop → `docker compose up -d` → เปิด VS Code

## 4. เนื้อหา

| บท | notebook | หัวข้อ |
|---|---|---|
| 0 | `00_setup_check` | เช็กเครื่อง |
| 1 | `01_python_basics` | print, ตัวแปร, ชนิดข้อมูล, f-string, list, dict, if, for, while |
| 2 | `02_functions` | function, return, ค่า default, keyword argument, type hint, `*args`/`**kwargs`, decorator (`@`) |
| 3 | `03_modules_objects_files` | import, object/method, สร้าง object จาก class, `with`, อ่านเขียนไฟล์, JSON |
| 4 | `04_dates_and_times` | date, datetime, timedelta, แปลงข้อความ ↔ วันที่, ช่วงเวลา 1 วัน, timezone |
| 5 | `05_errors_and_settings` | อ่าน error, try/except, raise, ลองใหม่, logging, `.env` |
| 6 | `06_api_and_pandas` | requests, API key, หลายหน้า, pandas: read_csv, กรอง, groupby, merge |
| 7 | `07_rustfs_and_iceberg` | boto3, Iceberg catalog ใน RustFS, bronze/silver/gold, INSERT/UPDATE/DELETE/MERGE, snapshot |
| 8 | `08_mini_pipeline` | ไฟล์ + API → bronze → silver (incremental) → gold (full load), รันซ้ำได้ |

สัญลักษณ์: 🧪 = ลองเอง · 💡 = จำไว้ใช้บ่อย · ⚠️ = ผิดบ่อย · ❌ = cell ที่ตั้งใจให้ error (ฝึกอ่าน error)

## 5. โครงสร้าง repo

```
lessons/            บทเรียน 0–8 + lakehouse.py (function ช่วยต่อ RustFS/Iceberg)
homework/           การบ้าน (มีตรวจคำตอบอัตโนมัติ)
data/marketplace/   ไฟล์ CSV ยอดขายจาก marketplace
docker/shop-api/    API จำลอง (ไม่ต้องแก้)
work/               ที่ทำงานของเรา (git ไม่สนใจ)
CHEATSHEET.md       สรุป Python หน้าเดียว
```

**อย่าแก้ไฟล์บทเรียนตรง ๆ** ถ้าจะจดโน้ต/ลองเพิ่ม ให้คัดลอกเป็น `lessons/my_<ชื่อ>.ipynb` (git ไม่สนใจไฟล์ `my_*`)
เวลาผู้สอนอัปเดตบทเรียนจะ `git pull` ได้โดยไม่ชน

## 6. การบ้าน

1. คัดลอก `homework/homework.ipynb` ไปเป็น `lessons/my_homework.ipynb`
2. ทำ 9 ข้อ รัน cell **ตรวจคำตอบ** ให้ขึ้น ✅ ทุกข้อ (ข้อ 8 ต้องเปิด Docker)
3. ส่งไฟล์ + ตัวเลขข้อ 7 ตามช่องทางที่ผู้สอนแจ้ง

## 7. เริ่มใหม่ทั้งหมด

```bash
docker compose down -v      # ลบ bucket และตารางทั้งหมดใน RustFS
docker compose up -d
```

## 8. แก้ปัญหาที่พบบ่อย

| อาการ | วิธีแก้ |
|---|---|
| `python` ไม่รู้จักคำสั่ง (Windows) | ติดตั้ง Python ใหม่แล้วติ๊ก "Add python.exe to PATH" หรือใช้ `py` แทน `python` |
| `pip` ขึ้น `UnicodeDecodeError` / `cp874` | อย่าเพิ่มภาษาไทยในไฟล์ `requirements.txt` |
| ไม่เห็น `.venv` ตอนเลือก kernel | `Ctrl+Shift+P` → **Python: Select Interpreter** → เลือก `.venv` แล้วลองเลือก kernel ใหม่ หรือปิดเปิด VS Code |
| `ModuleNotFoundError` | เลือก kernel ผิด (ต้องเป็น `.venv`) หรือยังไม่ได้ `pip install -r requirements.txt` |
| `ModuleNotFoundError: lakehouse` | notebook ต้องอยู่ในโฟลเดอร์ `lessons/` (ข้าง `lakehouse.py`) |
| `ConnectionError` / `Connection refused` | ยังไม่ได้ `docker compose up -d` หรือ Docker Desktop ยังไม่เปิด |
| `port is already allocated` | ปิด stack ของ session 2 หรือแก้ port ใน `.env` (`RUSTFS_PORT`, `SHOP_API_PORT`) และ URL ให้ตรงกัน แล้ว `docker compose up -d` |
| API ตอบ 429 / 503 | **ตั้งใจ** ให้เป็นแบบนั้น บทที่ 6 สอนวิธีรับมือ |
| บทที่ 7 ครั้งแรกช้า / error เรื่องดาวน์โหลด extension | DuckDB ดาวน์โหลดส่วนเสริม `httpfs`, `iceberg` ครั้งแรก ต้องต่ออินเทอร์เน็ต |
| มีโฟลเดอร์ `lessons/data` ว่าง ๆ โผล่มา | DuckDB สร้างเองตอน `CREATE TABLE ... AS SELECT` ลบได้ ไม่มีผลอะไร (ข้อมูลจริงอยู่ใน RustFS) |
| `Invalid unicode (byte sequence mismatch)` | ตาราง Iceberg + กรองด้วยข้อความภาษาไทย ใช้ข้อความภาษาอังกฤษหรือกรองด้วย id แทน (บทที่ 7) |
