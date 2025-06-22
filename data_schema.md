
# 🏥 Vituity Sample Healthcare Database Schema

This document provides the full SQL schema for a simulated US healthcare network, including all 20+ tables used to model providers, hospitals, sites, encounters, KPIs, and admin data.

---

## 📌 Core Tables

### 🧑‍⚕️ `providers`
```sql
CREATE TABLE providers (
    provider_id SERIAL PRIMARY KEY,
    npi VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    specialty VARCHAR(100),
    email VARCHAR(150),
    phone VARCHAR(20),
    hire_date DATE,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

### 🏥 `hospitals`
```sql
CREATE TABLE hospitals (
    hospital_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    hospital_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

### 🏬 `departments`
```sql
CREATE TABLE departments (
    department_id SERIAL PRIMARY KEY,
    hospital_id INT REFERENCES hospitals(hospital_id),
    name VARCHAR(100),
    department_code VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

### 📍 `sites`
```sql
CREATE TABLE sites (
    site_id SERIAL PRIMARY KEY,
    hospital_id INT REFERENCES hospitals(hospital_id),
    name VARCHAR(100),
    level_of_service VARCHAR(50),
    location_desc TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

### 👤 `patients`
```sql
CREATE TABLE patients (
    patient_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    dob DATE,
    gender VARCHAR(20),
    contact_phone VARCHAR(20),
    insurance_provider VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

### 🔁 `provider_assignments`
```sql
CREATE TABLE provider_assignments (
    assignment_id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES providers(provider_id),
    department_id INT REFERENCES departments(department_id),
    start_date DATE,
    end_date DATE,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

### 🕑 `shifts`
```sql
CREATE TABLE shifts (
    shift_id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES providers(provider_id),
    hospital_id INT REFERENCES hospitals(hospital_id),
    department_id INT REFERENCES departments(department_id),
    shift_start TIMESTAMP,
    shift_end TIMESTAMP,
    shift_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

### 📋 `encounters`
```sql
CREATE TABLE encounters (
    encounter_id SERIAL PRIMARY KEY,
    patient_id INT,
    provider_id INT REFERENCES providers(provider_id),
    hospital_id INT REFERENCES hospitals(hospital_id),
    department_id INT REFERENCES departments(department_id),
    site_id INT REFERENCES sites(site_id),
    encounter_date TIMESTAMP,
    chief_complaint TEXT,
    diagnosis_code VARCHAR(20),
    discharge_disposition VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

### 🎯 `performance_targets`
```sql
CREATE TABLE performance_targets (
    target_id SERIAL PRIMARY KEY,
    department_id INT REFERENCES departments(department_id),
    metric_name VARCHAR(100),
    target_value NUMERIC(10, 2),
    unit VARCHAR(20),
    period_start DATE,
    period_end DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

### 📈 `provider_metrics`
```sql
CREATE TABLE provider_metrics (
    metric_id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES providers(provider_id),
    metric_name VARCHAR(100),
    metric_value NUMERIC(10, 2),
    unit VARCHAR(20),
    report_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

### 👨‍💼 `hospital_admins`
```sql
CREATE TABLE hospital_admins (
    admin_id SERIAL PRIMARY KEY,
    user_name VARCHAR(100),
    email VARCHAR(150),
    hospital_id INT REFERENCES hospitals(hospital_id),
    role VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

### 📜 `audit_logs`
```sql
CREATE TABLE audit_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INT,
    action VARCHAR(100),
    entity_type VARCHAR(50),
    entity_id INT,
    timestamp TIMESTAMP DEFAULT NOW(),
    details TEXT
);
```

---

### 💊 `diagnosis_codes`
```sql
CREATE TABLE diagnosis_codes (
    code VARCHAR(20) PRIMARY KEY,
    description TEXT,
    icd_version VARCHAR(10)
);
```

---

### 🕒 `shift_types`
```sql
CREATE TABLE shift_types (
    type_id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    description TEXT
);
```

---

### 🏪 `site_departments`
```sql
CREATE TABLE site_departments (
    id SERIAL PRIMARY KEY,
    site_id INT REFERENCES sites(site_id),
    department_id INT REFERENCES departments(department_id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### 📞 `hospital_contacts`
```sql
CREATE TABLE hospital_contacts (
    contact_id SERIAL PRIMARY KEY,
    hospital_id INT REFERENCES hospitals(hospital_id),
    name VARCHAR(100),
    role VARCHAR(100),
    email VARCHAR(150),
    phone VARCHAR(20)
);
```

---

### 📚 `provider_specialties`
```sql
CREATE TABLE provider_specialties (
    specialty_id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES providers(provider_id),
    specialty_name VARCHAR(100)
);
```

---

### 💬 `provider_feedback`
```sql
CREATE TABLE provider_feedback (
    feedback_id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES providers(provider_id),
    encounter_id INT REFERENCES encounters(encounter_id),
    rating INT,
    comment TEXT,
    submitted_at TIMESTAMP DEFAULT NOW()
);
```

---

### 🌴 `provider_leaves`
```sql
CREATE TABLE provider_leaves (
    leave_id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES providers(provider_id),
    start_date DATE,
    end_date DATE,
    reason TEXT,
    approved_by INT REFERENCES hospital_admins(admin_id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### 🗂️ `document_uploads`
```sql
CREATE TABLE document_uploads (
    doc_id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES providers(provider_id),
    file_name VARCHAR(255),
    file_type VARCHAR(50),
    uploaded_at TIMESTAMP DEFAULT NOW(),
    uploaded_by INT
);
```

---

## ✅ Notes
- Each table uses audit fields: `created_at`, `updated_at` where applicable.
- Most primary keys are `SERIAL`.
- Foreign keys use explicit `REFERENCES` constraints.
- Designed to support both transactional and analytical queries.
