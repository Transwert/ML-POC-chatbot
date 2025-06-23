from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import sqlite3
import os
import pandas as pd
from dotenv import load_dotenv
import uvicorn

from ai_service import AIService
# Load .env variables
load_dotenv()
DB_PATH = os.getenv("DB_PATH", "./data/hospital_data.db")
SQL_DUMP_PATH = os.getenv("SQL_DUMP_PATH", "./data/data_dump.sql")
DATA_FOLDER = os.getenv("DATA_FOLDER", "./data")
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("BE_PORT", 8000))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

app = FastAPI()

# ----------- Sample Initialization ------------
def initialize_sample_db(force_initialize: bool = False):
    db_empty = not os.path.exists(DB_PATH) or os.path.getsize(DB_PATH) == 0

    if not (force_initialize or db_empty):
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE providers (
            provider_id INTEGER PRIMARY KEY,
            npi TEXT,
            first_name TEXT,
            last_name TEXT,
            specialty TEXT,
            email TEXT,
            phone TEXT,
            hire_date TEXT,
            status TEXT,
            created_at TEXT,
            updated_at TEXT
        );

        CREATE TABLE hospitals (
            hospital_id INTEGER PRIMARY KEY,
            name TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            zip_code TEXT,
            hospital_type TEXT,
            created_at TEXT,
            updated_at TEXT
        );

        CREATE TABLE departments (
            department_id INTEGER PRIMARY KEY,
            hospital_id INTEGER,
            name TEXT,
            department_code TEXT,
            created_at TEXT,
            updated_at TEXT
        );

        CREATE TABLE sites (
            site_id INTEGER PRIMARY KEY,
            hospital_id INTEGER,
            name TEXT,
            level_of_service TEXT,
            location_desc TEXT,
            created_at TEXT,
            updated_at TEXT
        );

        CREATE TABLE patients (
            patient_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            dob TEXT,
            gender TEXT,
            contact_phone TEXT,
            insurance_provider TEXT,
            created_at TEXT,
            updated_at TEXT
        );

        CREATE TABLE provider_assignments (
            assignment_id INTEGER PRIMARY KEY,
            provider_id INTEGER,
            department_id INTEGER,
            start_date TEXT,
            end_date TEXT,
            status TEXT,
            created_at TEXT,
            updated_at TEXT
        );

        CREATE TABLE shifts (
            shift_id INTEGER PRIMARY KEY,
            provider_id INTEGER,
            hospital_id INTEGER,
            department_id INTEGER,
            shift_start TEXT,
            shift_end TEXT,
            shift_type TEXT,
            created_at TEXT,
            updated_at TEXT
        );

        CREATE TABLE encounters (
            encounter_id INTEGER PRIMARY KEY,
            patient_id INTEGER,
            provider_id INTEGER,
            hospital_id INTEGER,
            department_id INTEGER,
            site_id INTEGER,
            encounter_date TEXT,
            chief_complaint TEXT,
            diagnosis_code TEXT,
            discharge_disposition TEXT,
            created_at TEXT,
            updated_at TEXT
        );

        CREATE TABLE performance_targets (
            target_id INTEGER PRIMARY KEY,
            department_id INTEGER,
            metric_name TEXT,
            target_value REAL,
            unit TEXT,
            period_start TEXT,
            period_end TEXT,
            created_at TEXT,
            updated_at TEXT
        );

        CREATE TABLE provider_metrics (
            metric_id INTEGER PRIMARY KEY,
            provider_id INTEGER,
            metric_name TEXT,
            metric_value REAL,
            unit TEXT,
            report_date TEXT,
            created_at TEXT,
            updated_at TEXT
        );

        CREATE TABLE hospital_admins (
            admin_id INTEGER PRIMARY KEY,
            user_name TEXT,
            email TEXT,
            hospital_id INTEGER,
            role TEXT,
            is_active INTEGER,
            created_at TEXT,
            updated_at TEXT
        );

        CREATE TABLE audit_logs (
            log_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            action TEXT,
            entity_type TEXT,
            entity_id INTEGER,
            timestamp TEXT,
            details TEXT
        );

        CREATE TABLE diagnosis_codes (
            code TEXT PRIMARY KEY,
            description TEXT,
            icd_version TEXT
        );

        CREATE TABLE shift_types (
            type_id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT
        );

        CREATE TABLE site_departments (
            id INTEGER PRIMARY KEY,
            site_id INTEGER,
            department_id INTEGER,
            created_at TEXT
        );

        CREATE TABLE hospital_contacts (
            contact_id INTEGER PRIMARY KEY,
            hospital_id INTEGER,
            name TEXT,
            role TEXT,
            email TEXT,
            phone TEXT
        );

        CREATE TABLE provider_specialties (
            specialty_id INTEGER PRIMARY KEY,
            provider_id INTEGER,
            specialty_name TEXT
        );

        CREATE TABLE provider_feedback (
            feedback_id INTEGER PRIMARY KEY,
            provider_id INTEGER,
            encounter_id INTEGER,
            rating INTEGER,
            comment TEXT,
            submitted_at TEXT
        );

        CREATE TABLE provider_leaves (
            leave_id INTEGER PRIMARY KEY,
            provider_id INTEGER,
            start_date TEXT,
            end_date TEXT,
            reason TEXT,
            approved_by INTEGER,
            created_at TEXT
        );

        CREATE TABLE document_uploads (
            doc_id INTEGER PRIMARY KEY,
            provider_id INTEGER,
            file_name TEXT,
            file_type TEXT,
            uploaded_at TEXT,
            uploaded_by INTEGER
        );
    ''')

    conn.commit()
    conn.close()

    load_data_dump()

# ------------- Load SQL Data ------------------
def load_data_dump():
    if os.path.exists(SQL_DUMP_PATH):
        with open(SQL_DUMP_PATH, "r") as file:
            sql = file.read()
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.executescript(sql)
                conn.commit()
                conn.close()
            except sqlite3.Error as e:
                print("Error loading data dump:", e)

# ------------- Request Model ------------------
class SQLQuery(BaseModel):
    query: str
    force_initialize: bool = False

class NL2SQL_data(BaseModel):
    userInput: str

# ------------- Main Endpoints ------------------
@app.post("/execute")
async def execute_sql(sql_query: SQLQuery):
    initialize_sample_db(force_initialize=sql_query.force_initialize)
    query = sql_query.query

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("BEGIN")
        result = cursor.execute(query)

        if query.strip().lower().startswith("select"):
            columns = [description[0] for description in result.description]
            rows = result.fetchall()
            conn.commit()
            conn.close()
            return {"columns": columns, "rows": rows}
        else:
            conn.commit()
            conn.close()
            return {"status": "success", "message": "Query executed successfully."}

    except sqlite3.Error as e:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/initialize")
async def initialize(force: bool = True):
    initialize_sample_db(force_initialize=force)
    return {"status": "initialized", "forced": force}

ai_service =  AIService()
@app.post("/NL2SQL")
async def naturalLanguageToSqlQuery (data: NL2SQL_data):
    try:
        output = ai_service.generate_sql_query(natural_language_prompt=data.userInput)
        return output
    except Exception as e:
        print("Error: problem in generating data from query!")
        return e
    
@app.post("/intent_classify")
async def intentClassify (data: NL2SQL_data):
    try:
        output = ai_service.detect_intent(user_input=data.userInput)
        return output
    except Exception as e:
        return e

# ------------- Main Entry ----------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host=API_HOST, port=API_PORT, reload=DEBUG)
