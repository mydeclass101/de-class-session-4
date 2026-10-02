# Python Cheatsheet · Session 4

## พื้นฐาน (บทที่ 1)

```python
price = 55                      # int      name = "มานี"      # str
sugar = 0.5                     # float    is_iced = True     # bool     note = None
int("55"), float("1.5"), str(99)                   # แปลงชนิด
f"{name} จ่าย {price:,} บาท"                        # f-string

shopping = ["ไข่", "นม"]        # list
shopping[0], shopping[-1], len(shopping), "นม" in shopping, shopping.append("กาแฟ")

friend = {"name": "มานี", "age": 24}               # dict
friend["name"], friend.get("email", "-"), friend.items()

if money >= 200: ...
elif money >= 55: ...
else: ...

for item in shopping: ...
for i, item in enumerate(shopping, start=1): ...
while True:
    ...
    if done: break

cheap = [p for p in prices if p < 40]              # list comprehension
```

## Function (บทที่ 2)

```python
def calculate_bill(price: float, qty: int, discount: float = 0) -> float:
    """คำอธิบาย"""
    return price * qty * (1 - discount)

calculate_bill(55, 2)                              # ตามลำดับ
calculate_bill(price=55, qty=2, discount=0.1)      # keyword argument
def f(*args, **kwargs): ...                        # รับกี่ตัวก็ได้ / kwargs เป็น dict
calculate_bill(**{"price": 55, "qty": 2})          # แตก dict เป็น argument
cook_for_family(boil_egg, 3)                       # ส่ง function (ไม่มีวงเล็บ)

@timer                                             # decorator = func = timer(func)
def make_coffee(): ...
```

## import / object / ไฟล์ (บทที่ 3)

```python
import math; from datetime import date; import pandas as pd
datetime(2026, 9, 25)          # สร้าง object จาก class
obj.attribute, obj.method()
with open(path, encoding="utf-8") as f: text = f.read()
Path("../data").glob("*.csv"), Path(p).read_text(encoding="utf-8")
json.dumps(d, ensure_ascii=False), json.loads(text)
```

## วันที่ (บทที่ 4)

```python
date(2026, 9, 25) + timedelta(days=1)
date.fromisoformat("2026-09-25"), d.isoformat(), dt.strftime("%d/%m/%Y")
start = datetime.fromisoformat(day); end = start + timedelta(days=1)    # 1 วัน: start <= t < end
t.astimezone(ZoneInfo("Asia/Bangkok")).date()                           # UTC -> วันที่ไทย
```

## Error / ค่าตั้งค่า (บทที่ 5)

```python
try: ...
except ValueError as problem: ...
finally: ...
raise ValueError("บอกว่าผิดอะไร")
log = logging.getLogger("ชื่อ"); log.info(...); log.warning(...)
load_dotenv(); os.getenv("SHOP_API_KEY")
```

## API / pandas (บทที่ 6)

```python
resp = requests.get(url, params={"date": d}, headers={"X-API-Key": key}, timeout=10)
resp.status_code, resp.json(), resp.raise_for_status()

df = pd.DataFrame(list_of_dicts)          pd.read_csv(path)          pd.concat([a, b])
df[["a", "b"]]      df[df["qty"] > 0]      df["total"] = df["qty"] * df["price"]
df.groupby("day", as_index=False).agg(total=("amount", "sum"))
a.merge(b, on="day", how="left")          df.to_parquet(path)
```

## RustFS + Iceberg (บทที่ 7–8)

```python
from lakehouse import storage, make_bucket, make_table_bucket, connect_lakehouse, show_tables

s3 = storage()
s3.upload_file(local, bucket, key)   s3.list_objects_v2(Bucket=b, Prefix=p)   s3.get_object(Bucket=b, Key=k)
s3.copy_object(...) + s3.delete_object(...)                       # = ย้ายไฟล์

make_table_bucket("lakehouse")
lake = connect_lakehouse()
lake.sql("CREATE SCHEMA IF NOT EXISTS lake.bronze")
lake.sql("CREATE TABLE lake.bronze.t AS SELECT * FROM my_df")    # my_df = ตัวแปร DataFrame
lake.sql("INSERT INTO lake.bronze.t BY NAME SELECT * FROM my_df")
lake.sql("SELECT ...").df()                                       # ผลเป็น DataFrame
```

```sql
MERGE INTO lake.silver.t AS old USING new_rows AS new ON old.id = new.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

BEGIN TRANSACTION; DELETE FROM lake.gold.t; INSERT INTO lake.gold.t SELECT ...; COMMIT;   -- full load

SELECT * FROM iceberg_snapshots(lake.silver.t);                  -- ประวัติ
SELECT * FROM lake.silver.t AT (VERSION => 1234567890);          -- ย้อนเวลา
```

| ชั้น | เก็บอะไร | โหลดแบบ |
|---|---|---|
| bronze | ของดิบ + `source_file`, `loaded_at` | เพิ่มต่อท้าย |
| silver | แปลงชนิด ตัดซ้ำ ทำเครื่องหมายแถวเสีย | incremental + MERGE |
| gold | ตัวเลขสรุปพร้อมใช้ | full load (DELETE + INSERT) |
