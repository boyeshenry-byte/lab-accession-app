import customtkinter as ctk
from database.db import get_db_connection, db_path
import sqlite3
from ui.add_study_dialog import AddStudyDialog
from CTkMessagebox import CTkMessagebox

class EditAccessionFrame(ctk.CTkFrame):
    def __init__(self, master, accession_id):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.accession_id = accession_id
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.create_widgets()

    def load_accession_details(self):
        conn = get_db_connection(db_path)
        with conn:
            accession = conn.execute("""
                SELECT a.*, p.first_name, p.last_name, e.freezer_id, p.ccf_number, 
                p.uh_id, p.date_of_birth, t.tech_initials, s.study_name
                FROM accessions a
                JOIN enrollments e ON a.enrollment_id = e.enrollment_id
                JOIN patients p ON e.patient_id = p.patient_id
                LEFT JOIN techs t ON a.tech_id = t.tech_id
                LEFT JOIN studies s ON e.study_id = s.study_id
                WHERE a.accession_id = ?
            """, (self.accession_id,)).fetchone()
        conn.close()
        return accession
    
    def create_widgets(self):
        accession = self.load_accession_details()
        if not accession:
            CTkMessagebox(title="Error", message="Accession not found.", icon="cancel")
            from ui.home import HomeFrame
            self.master.show_frame(HomeFrame)
            return
        
        for i in range(4):
            self.columnconfigure(i, weight=1)
        
        self.title_label = ctk.CTkLabel(self, text=f"Edit Accession", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=12)
        self.patient_info_label = ctk.CTkLabel(self, text=f"Patient: {accession['first_name']} {accession['last_name']} (Freezer: {accession['freezer_id']}, CCF: {accession['ccf_number']})")
        self.patient_info_label.grid(row=1, column=0, columnspan=2, pady=8)

        self.freezer_id_label = ctk.CTkLabel(self, text="Freezer ID:")
        self.freezer_id_label.grid(row=2, column=0, pady=8, padx=10, sticky="e")
        self.freezer_id_entry = ctk.CTkEntry(self, width=200)
        self.freezer_id_entry.grid(row=2, column=1, pady=8, padx=10, sticky="w")
        self.freezer_id_entry.insert(0, accession['freezer_id'] if accession['freezer_id'] else "")

        self.tech_dropdown_label = ctk.CTkLabel(self, text="Technician:")
        self.tech_dropdown_label.grid(row=3, column=0, pady=8, padx=10, sticky="e")
        self.tech_dropdown = ctk.CTkComboBox(self, values=self.load_techs())
        self.tech_dropdown.grid(row=3, column=1, pady=8, padx=10, sticky="w")
        self.tech_dropdown.set(accession['tech_initials'] if accession['tech_initials'] else "Select Technician")

        self.disease_type_label = ctk.CTkLabel(self, text="Disease Type:")
        self.disease_type_label.grid(row=4, column=0, pady=8, padx=10, sticky="e")
        self.disease_type_entry = ctk.CTkEntry(self, width=200)
        self.disease_type_entry.grid(row=4, column=1, pady=8, padx=10, sticky="w")
        self.disease_type_entry.insert(0, accession['disease_type'] if accession['disease_type'] else "")

        self.timepoint_label = ctk.CTkLabel(self, text="Timepoint:")
        self.timepoint_label.grid(row=5, column=0, pady=8, padx=10, sticky="e")
        self.timepoint_entry = ctk.CTkEntry(self, width=200)
        self.timepoint_entry.grid(row=5, column=1, pady=8, padx=10, sticky="w")
        self.timepoint_entry.insert(0, accession['timepoint'] if accession['timepoint'] else "")

        self.notes_label = ctk.CTkLabel(self, text="Notes:")
        self.notes_label.grid(row=6, column=0, pady=8, padx=10, sticky="ne")
        self.notes_text = ctk.CTkTextbox(self, width=400, height=200)
        self.notes_text.grid(row=6, column=1, pady=8, padx=10, sticky="w")
        self.notes_text.insert("0.0", accession['notes'] if accession['notes'] else "")

        # Add a Save button to save changes
        self.save_button = ctk.CTkButton(self, text="Save Changes", command=self.save_changes)
        self.save_button.grid(row=100, column=0, columnspan=2, pady=20)

        self.back_button = ctk.CTkButton(self, text="Back", command=self.go_back)
        self.back_button.grid(row=0, column=2, pady=8, padx=10)

        self.enrollment_id = accession['enrollment_id']

        self.detail_rows = []
        self.add_detail_button = ctk.CTkButton(self, text="Add Detail", command=self.add_accession_detail)
        self.add_detail_button.grid(row=7, column=1, pady=8, padx=10, sticky="w")

    def save_changes(self):
        from ui.home import HomeFrame
        freezer_id = self.freezer_id_entry.get().strip() or None
        tech_initials = self.tech_dropdown.get().strip()
        disease_type = self.disease_type_entry.get().strip() or None
        timepoint = self.timepoint_entry.get().strip() or None
        notes = self.notes_text.get("0.0", "end").strip() or None
        details = [(field.get().strip(), value.get().strip()) for field, value, _ in self.detail_rows if field.get().strip() and value.get().strip()]

        tech_id = None
        if tech_initials:
            conn = get_db_connection(db_path)
            tech = conn.execute("SELECT tech_id FROM techs WHERE tech_initials = ?", (tech_initials,)).fetchone()
            conn.close()
            if tech:
                tech_id = tech['tech_id']

        if freezer_id:
            conn = get_db_connection(db_path)
            with conn:
                conn.execute("""
                        UPDATE enrollments
                        SET freezer_id = ?
                        WHERE enrollment_id = ? 
                        """, (freezer_id, self.enrollment_id))
            conn.close()

        conn = get_db_connection(db_path)
        with conn:
            conn.execute("""
                UPDATE accessions
                SET tech_id = ?, disease_type = ?, timepoint = ?, notes = ?
                WHERE accession_id = ?
            """, (tech_id, disease_type, timepoint, notes, self.accession_id))
        conn.close()

        if details:
            conn = get_db_connection(db_path)
            with conn:
                for field_name, field_value in details:
                    conn.execute("""
                        INSERT INTO accession_details (accession_id, field_name, field_value)
                        VALUES (?, ?, ?)
                    """, (self.accession_id, field_name, field_value))
            conn.close()

        CTkMessagebox(title="Success", message="Accession updated successfully.", icon="check")
        self.get_app().show_frame(HomeFrame)

    def open_edit(self, accession_id):
        from ui.edit_accession import EditAccessionFrame
        self.master.master.master.show_frame(EditAccessionFrame, accession_id=accession_id)

    def get_app(self):
        widget = self
        while widget is not None:
            if hasattr(widget, 'show_frame'):
                return widget
            widget = widget.master
        return None

    def go_back(self):
        from ui.search_accession import SearchAccessionFrame
        self.get_app().show_frame(SearchAccessionFrame)

    def load_techs(self):
        conn = get_db_connection(db_path)
        with conn:
            techs = conn.execute("SELECT tech_initials FROM techs").fetchall()
        conn.close()
        return [tech['tech_initials'] for tech in techs]
    
    def add_accession_detail(self):
        row_index = len(self.detail_rows) + 7
        field_name_entry = ctk.CTkEntry(self, placeholder_text="Field Name")
        field_name_entry.grid(row=row_index, column=1, pady=8, padx=10, sticky="w")
        field_value_entry = ctk.CTkEntry(self, width=100, placeholder_text="Value")
        field_value_entry.grid(row=row_index, column=2, pady=8, padx=10, sticky="w")
        self.detail_rows.append((field_name_entry, field_value_entry, None))