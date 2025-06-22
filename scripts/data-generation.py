import os
import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

class HealthcareDataGenerator:
    def __init__(self, output_dir="../data", num_records=1000, save_as_sql=False):
        self.output_dir = output_dir
        self.num_records = num_records
        self.save_as_sql = save_as_sql
        self.fake = Faker()
        os.makedirs(self.output_dir, exist_ok=True)
        self.sql_statements = []

    def generate_and_save_all(self):
        self._generate_providers()
        self._generate_hospitals()
        self._generate_departments()
        self._generate_sites()
        self._generate_patients()
        self._generate_provider_assignments()
        self._generate_shifts()
        self._generate_encounters()
        self._generate_performance_targets()
        self._generate_provider_metrics()
        self._generate_hospital_admins()
        self._generate_audit_logs()
        self._generate_diagnosis_codes()
        self._generate_shift_types()
        self._generate_site_departments()
        self._generate_hospital_contacts()
        self._generate_provider_specialties()
        self._generate_provider_feedback()
        self._generate_provider_leaves()
        self._generate_document_uploads()

        if self.save_as_sql:
            with open(os.path.join(self.output_dir, "data_dump.sql"), "w") as f:
                f.writelines(self.sql_statements)

    def _save_or_append_csv(self, df, filename, table_name):
        filepath = os.path.join(self.output_dir, filename)
        if os.path.exists(filepath):
            df_existing = pd.read_csv(filepath)
            df_combined = pd.concat([df_existing, df], ignore_index=True)
        else:
            df_combined = df

        df_combined.to_csv(filepath, index=False)

        if self.save_as_sql:
            self.sql_statements.append(f"-- {table_name}\n")
            for _, row in df.iterrows():
                values = ', '.join([f"'{str(x).replace('\'', '\'\'')}'" if pd.notnull(x) else "NULL" for x in row])
                self.sql_statements.append(f"INSERT INTO {table_name} VALUES ({values});\n")
            self.sql_statements.append("\n")

    # Methods for generating data for each table
    def _generate_providers(self):
        df = pd.DataFrame([{
            "provider_id": i,
            "npi": self.fake.unique.numerify(text="##########"),
            "first_name": self.fake.first_name(),
            "last_name": self.fake.last_name(),
            "specialty": self.fake.job(),
            "email": self.fake.email(),
            "phone": self.fake.phone_number(),
            "hire_date": self.fake.date_this_decade(),
            "status": random.choice(["Active", "On Leave", "Terminated"]),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        } for i in range(1, self.num_records + 1)])
        self._save_or_append_csv(df, "providers.csv", "providers")

    def _generate_hospitals(self):
        df = pd.DataFrame([{
            "hospital_id": i,
            "name": self.fake.company() + " Hospital",
            "address": self.fake.address().replace("\n", ", "),
            "city": self.fake.city(),
            "state": self.fake.state_abbr(),
            "zip_code": self.fake.zipcode(),
            "hospital_type": random.choice(["Acute Care", "Trauma Center", "Community"]),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        } for i in range(1, self.num_records // 2 + 1)])
        self._save_or_append_csv(df, "hospitals.csv", "hospitals")

    def _generate_departments(self):
        df = pd.DataFrame([{
            "department_id": i,
            "hospital_id": random.randint(1, self.num_records // 2),
            "name": random.choice(["Emergency", "Pediatrics", "ICU", "Cardiology"]),
            "department_code": self.fake.bothify(text="DEPT-##??"),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        } for i in range(1, self.num_records + 1)])
        self._save_or_append_csv(df, "departments.csv", "departments")

    def _generate_sites(self):
        df = pd.DataFrame([{
            "site_id": i,
            "hospital_id": random.randint(1, self.num_records // 2),
            "name": self.fake.city() + " Site",
            "level_of_service": random.choice(["Level 1 Trauma", "Level 2 Trauma", "Community"]),
            "location_desc": self.fake.catch_phrase(),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        } for i in range(1, self.num_records + 1)])
        self._save_or_append_csv(df, "sites.csv", "sites")

    def _generate_patients(self):
        df = pd.DataFrame([{
            "patient_id": i,
            "first_name": self.fake.first_name(),
            "last_name": self.fake.last_name(),
            "dob": self.fake.date_of_birth(minimum_age=1, maximum_age=99),
            "gender": random.choice(["Male", "Female", "Other"]),
            "contact_phone": self.fake.phone_number(),
            "insurance_provider": self.fake.company(),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        } for i in range(1, self.num_records + 1)])
        self._save_or_append_csv(df, "patients.csv", "patients")

    def _generate_provider_assignments(self):
        df = pd.DataFrame([{
            "assignment_id": i,
            "provider_id": random.randint(1, self.num_records),
            "department_id": random.randint(1, self.num_records),
            "start_date": self.fake.date_this_year(),
            "end_date": self.fake.date_between(start_date="+1d", end_date="+30d"),
            "status": random.choice(["Active", "Ended"]),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        } for i in range(1, self.num_records + 1)])
        self._save_or_append_csv(df, "provider_assignments.csv", "provider_assignments")

    def _generate_shifts(self):
        df = pd.DataFrame([{
            "shift_id": i,
            "provider_id": random.randint(1, self.num_records),
            "hospital_id": random.randint(1, self.num_records // 2),
            "department_id": random.randint(1, self.num_records),
            "shift_start": datetime.now(),
            "shift_end": datetime.now() + timedelta(hours=8),
            "shift_type": random.choice(["Day", "Night", "Swing"]),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        } for i in range(1, self.num_records + 1)])
        self._save_or_append_csv(df, "shifts.csv", "shifts")

    def _generate_encounters(self):
        df = pd.DataFrame([{
            "encounter_id": i,
            "patient_id": random.randint(1, self.num_records),
            "provider_id": random.randint(1, self.num_records),
            "hospital_id": random.randint(1, self.num_records // 2),
            "department_id": random.randint(1, self.num_records),
            "site_id": random.randint(1, self.num_records),
            "encounter_date": self.fake.date_time_this_year(),
            "chief_complaint": self.fake.sentence(),
            "diagnosis_code": self.fake.lexify(text="D????"),
            "discharge_disposition": random.choice(["Home", "Admitted", "Transferred"]),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        } for i in range(1, self.num_records + 1)])
        self._save_or_append_csv(df, "encounters.csv", "encounters")

    def _generate_performance_targets(self):
        df = pd.DataFrame([{
            "target_id": i,
            "department_id": random.randint(1, self.num_records),
            "metric_name": random.choice(["Wait Time", "Patient Satisfaction", "Length of Stay"]),
            "target_value": round(random.uniform(70.0, 100.0), 2),
            "unit": "%",
            "period_start": self.fake.date_this_year(),
            "period_end": self.fake.date_between(start_date="+30d", end_date="+60d"),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        } for i in range(1, self.num_records)])
        self._save_or_append_csv(df, "performance_targets.csv", "performance_targets")

    def _generate_provider_metrics(self):
        df = pd.DataFrame([{
            "metric_id": i,
            "provider_id": random.randint(1, self.num_records),
            "metric_name": random.choice(["Patients Seen", "Avg LOS", "Consults"]),
            "metric_value": round(random.uniform(1.0, 100.0), 2),
            "unit": random.choice(["%", "min", "cases"]),
            "report_date": self.fake.date_this_year(),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        } for i in range(1, self.num_records)])
        self._save_or_append_csv(df, "provider_metrics.csv", "provider_metrics")

    def _generate_hospital_admins(self):
        df = pd.DataFrame([{
            "admin_id": i,
            "user_name": self.fake.user_name(),
            "email": self.fake.email(),
            "hospital_id": random.randint(1, self.num_records // 2),
            "role": random.choice(["Director", "Admin", "Manager"]),
            "is_active": random.choice([True, False]),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        } for i in range(1, self.num_records)])
        self._save_or_append_csv(df, "hospital_admins.csv", "hospital_admins")

    def _generate_audit_logs(self):
        df = pd.DataFrame([{
            "log_id": i,
            "user_id": random.randint(1, self.num_records),
            "action": random.choice(["CREATE", "UPDATE", "DELETE"]),
            "entity_type": random.choice(["provider", "encounter", "department"]),
            "entity_id": random.randint(1, self.num_records),
            "timestamp": datetime.now(),
            "details": self.fake.sentence()
        } for i in range(1, self.num_records)])
        self._save_or_append_csv(df, "audit_logs.csv", "audit_logs")

    def _generate_diagnosis_codes(self):
        df = pd.DataFrame([{
            "code": self.fake.unique.lexify(text="D????"),
            "description": self.fake.sentence(),
            "icd_version": random.choice(["ICD-9", "ICD-10"])
        } for _ in range(1, self.num_records)])
        self._save_or_append_csv(df, "diagnosis_codes.csv", "diagnosis_codes")

    def _generate_shift_types(self):
        df = pd.DataFrame([{
            "type_id": i,
            "name": name,
            "description": self.fake.sentence()
        } for i, name in enumerate(["Day", "Night", "Swing"], start=1)])
        self._save_or_append_csv(df, "shift_types.csv", "shift_types")

    def _generate_site_departments(self):
        df = pd.DataFrame([{
            "id": i,
            "site_id": random.randint(1, self.num_records),
            "department_id": random.randint(1, self.num_records),
            "created_at": datetime.now()
        } for i in range(1, self.num_records)])
        self._save_or_append_csv(df, "site_departments.csv", "site_departments")

    def _generate_hospital_contacts(self):
        df = pd.DataFrame([{
            "contact_id": i,
            "hospital_id": random.randint(1, self.num_records // 2),
            "name": self.fake.name(),
            "role": self.fake.job(),
            "email": self.fake.email(),
            "phone": self.fake.phone_number()
        } for i in range(1, self.num_records)])
        self._save_or_append_csv(df, "hospital_contacts.csv", "hospital_contacts")

    def _generate_provider_specialties(self):
        df = pd.DataFrame([{
            "specialty_id": i,
            "provider_id": random.randint(1, self.num_records),
            "specialty_name": self.fake.job()
        } for i in range(1, self.num_records)])
        self._save_or_append_csv(df, "provider_specialties.csv", "provider_specialties")

    def _generate_provider_feedback(self):
        df = pd.DataFrame([{
            "feedback_id": i,
            "provider_id": random.randint(1, self.num_records),
            "encounter_id": random.randint(1, self.num_records),
            "rating": random.randint(1, 5),
            "comment": self.fake.sentence(),
            "submitted_at": datetime.now()
        } for i in range(1, self.num_records)])
        self._save_or_append_csv(df, "provider_feedback.csv", "provider_feedback")

    def _generate_provider_leaves(self):
        df = pd.DataFrame([{
            "leave_id": i,
            "provider_id": random.randint(1, self.num_records),
            "start_date": self.fake.date_this_year(),
            "end_date": self.fake.date_between(start_date="+1d", end_date="+30d"),
            "reason": self.fake.sentence(),
            "approved_by": random.randint(1, self.num_records // 2),
            "created_at": datetime.now()
        } for i in range(1, self.num_records)])
        self._save_or_append_csv(df, "provider_leaves.csv", "provider_leaves")

    def _generate_document_uploads(self):
        df = pd.DataFrame([{
            "doc_id": i,
            "provider_id": random.randint(1, self.num_records),
            "file_name": self.fake.file_name(extension='pdf'),
            "file_type": "application/pdf",
            "uploaded_at": datetime.now(),
            "uploaded_by": random.randint(1, self.num_records // 2)
        } for i in range(1, self.num_records)])
        self._save_or_append_csv(df, "document_uploads.csv", "document_uploads")

gen = HealthcareDataGenerator(num_records=1000, save_as_sql=False)
gen.generate_and_save_all()