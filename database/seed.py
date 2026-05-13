from datetime import datetime 
from database.db import get_db_connection, db_path

def seed_db(db_path):
    conn = get_db_connection(db_path)
    with conn:
        # Insert sample users
        conn.execute("INSERT INTO studies (study_name, irb_number) VALUES (?, ?)", ("Study A", "IRB12345")) 
        conn.execute("INSERT INTO studies (study_name, irb_number) VALUES (?, ?)", ("Study B", "IRB67890"))
        conn.execute("INSERT INTO patients (iml_number, first_name, last_name, date_of_birth, ccf_number) VALUES (?, ?, ?, ?, ?)", \
        ("IML001", "John", "Doe", "1980-01-01", "CCF001"))
        conn.execute("INSERT INTO patients (iml_number, first_name, last_name, date_of_birth, ccf_number) VALUES (?, ?, ?, ?, ?)", \
        ("IML002", "Jane", "Doe", "1980-01-01", "CCF002"))
        conn.execute("INSERT INTO enrollments (patient_id, study_id, enrollment_date) VALUES (?, ?, ?)", \
        (1, 1, datetime.now().strftime("%Y-%m-%d")))
        conn.execute("INSERT INTO enrollments (patient_id, study_id, enrollment_date) VALUES (?, ?, ?)", \
        (2, 2, datetime.now().strftime("%Y-%m-%d")))
        conn.execute("""INSERT INTO accessions (enrollment_id, accession_date, timepoint, disease_type, freezer_id,
        tech_name) VALUES (?, ?, ?, ?, ?, ?)""", \
        (1, datetime.now().strftime("%Y-%m-%d"), "Baseline", "Disease A", "Freezer 1", "Tech A"))
        conn.execute("""INSERT INTO accessions (enrollment_id, accession_date, timepoint, disease_type, freezer_id,
        tech_name) VALUES (?, ?, ?, ?, ?, ?)""", \
        (2, datetime.now().strftime("%Y-%m-%d"), "Baseline", "Disease B", "Freezer 1", "Tech B"))
        conn.execute("INSERT INTO accession_details (accession_id, field_name, field_value) VALUES (?, ?, ?)", \
        (1, "Sample Type", "Blood"))
        conn.execute("INSERT INTO accession_details (accession_id, field_name, field_value) VALUES (?, ?, ?)", \
        (2, "Sample Type", "Blood"))
        conn.execute("INSERT INTO tube_types (tube_type_name) VALUES (?)", ("EDTA",))
        conn.execute("INSERT INTO tube_types (tube_type_name) VALUES (?)", ("Heparin",))
        conn.execute("INSERT INTO tube_types (tube_type_name) VALUES (?)", ("SST",))
        conn.execute("INSERT INTO tube_types (tube_type_name) VALUES (?)", ("Streck",))
        conn.execute("INSERT INTO tube_types (tube_type_name) VALUES (?)", ("Urine",))
        conn.execute("INSERT INTO tube_types (tube_type_name) VALUES (?)", ("Other",))
        conn.execute("INSERT INTO tube_accessions (accession_id, tube_type_id, quantity) VALUES (?, ?, ?)", \
        (1, 1, 1))
    conn.close()

if __name__ == '__main__':
    seed_db(db_path)
    print("Database seeded with sample data")