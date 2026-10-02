"""เครื่องมือช่วยคุยกับ Lakehouse ของเรา (RustFS + Iceberg)

บทที่ 7 สอนทีละขั้นว่าข้างในทำอะไร ไฟล์นี้แค่รวบขั้นตอนเหล่านั้นไว้เป็น function ให้เรียกใช้สั้น ๆ

    from lakehouse import storage, make_table_bucket, connect_lakehouse

    s3 = storage()                      # คุยกับ RustFS แบบ S3 (bucket / ไฟล์)
    make_table_bucket("lakehouse")      # เตรียม bucket ให้เก็บตาราง Iceberg ได้ (ทำครั้งเดียว)
    lake = connect_lakehouse()          # DuckDB ที่มองเห็นตาราง Iceberg ทั้งหมดเป็น lake.<namespace>.<table>
"""
import hashlib
import os

import boto3
import duckdb
import requests
from botocore.auth import S3SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials
from dotenv import load_dotenv

load_dotenv()          # อ่านค่าจากไฟล์ .env (ถ้ามี)

ENDPOINT = os.getenv("RUSTFS_ENDPOINT", "http://127.0.0.1:9000")
ACCESS_KEY = os.getenv("RUSTFS_ACCESS_KEY", "student")
SECRET_KEY = os.getenv("RUSTFS_SECRET_KEY", "classroom")
REGION = "us-east-1"


def storage():
    """boto3 client สำหรับ RustFS (ใช้คำสั่งเดียวกับ AWS S3)"""
    return boto3.client(
        "s3",
        endpoint_url=ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=REGION,
    )


def make_bucket(bucket: str) -> None:
    """สร้าง bucket ถ้ายังไม่มี (รันซ้ำได้)"""
    s3 = storage()
    existing = [b["Name"] for b in s3.list_buckets()["Buckets"]]
    if bucket not in existing:
        s3.create_bucket(Bucket=bucket)


def make_table_bucket(bucket: str = "lakehouse") -> None:
    """สร้าง bucket แล้วเปิดให้เป็น "table bucket" (ที่เก็บตาราง Iceberg) รันซ้ำได้

    RustFS เปิดด้วยการส่ง PUT ไปที่ {ENDPOINT}/iceberg/v1/buckets/{bucket}
    พร้อมลายเซ็นแบบเดียวกับ S3 (เหมือนกดปุ่ม Enable table bucket ในหน้าเว็บ)
    """
    make_bucket(bucket)
    url = f"{ENDPOINT}/iceberg/v1/buckets/{bucket}"
    request = AWSRequest(method="PUT", url=url, data=b"",
                         headers={"x-amz-content-sha256": hashlib.sha256(b"").hexdigest()})
    S3SigV4Auth(Credentials(ACCESS_KEY, SECRET_KEY), "s3", REGION).add_auth(request)
    response = requests.put(url, headers=dict(request.headers), data=b"", timeout=30)
    response.raise_for_status()


def connect_lakehouse(bucket: str = "lakehouse") -> duckdb.DuckDBPyConnection:
    """เปิด DuckDB แล้วต่อเข้ากับ Iceberg catalog ของ RustFS ตั้งชื่อว่า lake

    หลังจากนี้ใช้ SQL กับตาราง Iceberg ได้เลย เช่น  lake.sql("SELECT * FROM lake.bronze.orders")
    """
    host = ENDPOINT.split("://", 1)[1]
    lake = duckdb.connect()
    lake.sql("INSTALL httpfs; LOAD httpfs; INSTALL iceberg; LOAD iceberg;")
    # 1) กุญแจสำหรับอ่าน/เขียนไฟล์ใน RustFS
    lake.sql(f"""
        CREATE OR REPLACE SECRET rustfs (
            TYPE s3, PROVIDER config,
            KEY_ID '{ACCESS_KEY}', SECRET '{SECRET_KEY}', REGION '{REGION}',
            ENDPOINT '{host}', URL_STYLE 'path', USE_SSL false
        )""")
    # 2) ต่อเข้ากับ Iceberg REST catalog ที่อยู่ใน RustFS (ค่าตั้งค่าตามที่ RustFS แนะนำ คัดลอกไปใช้ได้เลย)
    lake.sql(f"""
        ATTACH '{bucket}' AS lake (
            TYPE iceberg,
            ENDPOINT '{ENDPOINT}/iceberg',
            AUTHORIZATION_TYPE 'sigv4', SECRET 'rustfs',
            SIGV4_REGION '{REGION}', SIGV4_SERVICE 's3',
            ACCESS_DELEGATION_MODE 'none',
            STAGE_CREATE_TABLES false,
            SKIP_CREATE_TABLE_METADATA_UPDATES true,
            DISABLE_MULTI_TABLE_COMMIT true,
            REMOVE_FILES_ON_DELETE false,
            PURGE_REQUESTED false,
            SUPPORT_NESTED_NAMESPACES false
        )""")
    return lake


def show_tables(lake: duckdb.DuckDBPyConnection):
    """ตาราง Iceberg ทั้งหมดใน lakehouse"""
    return lake.sql("""
        SELECT table_schema AS namespace, table_name
        FROM information_schema.tables
        WHERE table_catalog = 'lake'
        ORDER BY 1, 2""")
