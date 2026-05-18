import customtkinter as ctk
from database.db import get_db_connection, db_path
import sqlite3
from ui.add_study_dialog import AddStudyDialog
from CTkMessagebox import CTkMessagebox

class EditAccessionFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, accession_id):
        super().__init__(master)
        self.pack(pady=20, padx=60, fill="both", expand=True)
        self.accession_id = accession_id
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.create_widgets()

    def load_accession_details(self):
        conn = get_db_connection(db_path)
        with conn:
            accession = conn.execute("""
                SELECT a.*, p.first_name, p.last_name, p.iml_number, p.ccf_number, 
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
        
        self.title_label = ctk.CTkLabel(self, text=f"Edit Accession #{self.accession_id}", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=12)

        self.freezer_id_label = ctk.CTkLabel(self, text="Freezer ID:")
        self.freezer_id_label.grid(row=1, column=0, pady=8, padx=10, sticky="e")
        self.freezer_id_entry = ctk.CTkEntry(self, width=200)
        self.freezer_id_entry.grid(row=1, column=1, pady=8, padx=10, sticky="w")
        self.freezer_id_entry.insert(0, accession['freezer_id'] if accession['freezer_id'] else "")

        self.tech_label = ctk.CTkLabel(self, text="Technician:")
        self.tech_label.grid(row=2, column=0, pady=8, padx=10, sticky="e")
        self.tech_entry = ctk.CTkEntry(self, width=200)
        self.tech_entry.grid(row=2, column=1, pady=8, padx=10, sticky="w")
        self.tech_entry.insert(0, accession['tech_initials'] if accession['tech_initials'] else "")

        self.disease_type_label = ctk.CTkLabel(self, text="Disease Type:")
        self.disease_type_label.grid(row=3, column=0, pady=8, padx=10, sticky="e")
        self.disease_type_entry = ctk.CTkEntry(self, width=200)
        self.disease_type_entry.grid(row=3, column=1, pady=8, padx=10, sticky="w")
        self.disease_type_entry.insert(0, accession['disease_type'] if accession['disease_type'] else "")

        self.timepoint_label = ctk.CTkLabel(self, text="Timepoint:")
        self.timepoint_label.grid(row=4, column=0, pady=8, padx=10, sticky="e")
        self.timepoint_entry = ctk.CTkEntry(self, width=200)
        self.timepoint_entry.grid(row=4, column=1, pady=8, padx=10, sticky="w")
        self.timepoint_entry.insert(0, accession['timepoint'] if accession['timepoint'] else "")

        self.notes_label = ctk.CTkLabel(self, text="Notes:")
        self.notes_label.grid(row=5, column=0, pady=8, padx=10, sticky="ne")
        self.notes_text = ctk.CTkTextbox(self, width=400, height=200)
        self.notes_text.grid(row=5, column=1, pady=8, padx=10, sticky="w")
        self.notes_text.insert("0.0", accession['notes'] if accession['notes'] else "")

        # Add a Save button to save changes
        self.save_button = ctk.CTkButton(self, text="Save Changes", command=self.save_changes)
        self.save_button.grid(row=100, column=0, columnspan=2, pady=20)

        self.back_button = ctk.CTkButton(self, text="Back", command=self.go_back)
        self.back_button.grid(row=0, column=2, pady=8, padx=10)

    def save_changes(self):
        from ui.home import HomeFrame
        freezer_id = self.freezer_id_entry.get().strip() or None
        tech_initials = self.tech_entry.get().strip()
        disease_type = self.disease_type_entry.get().strip() or None
        timepoint = self.timepoint_entry.get().strip() or None
        notes = self.notes_text.get("0.0", "end").strip() or None

        tech_id = None
        if tech_initials:
            conn = get_db_connection(db_path)
            tech = conn.execute("SELECT tech_id FROM techs WHERE tech_initials = ?", (tech_initials,)).fetchone()
            conn.close()
            if tech:
                tech_id = tech['tech_id']

        conn = get_db_connection(db_path)
        with conn:
            conn.execute("""
                UPDATE accessions
                SET freezer_id = ?, tech_id = ?, disease_type = ?, timepoint = ?, notes = ?
                WHERE accession_id = ?
            """, (freezer_id, tech_id, disease_type, timepoint, notes, self.accession_id))
        conn.close()

        CTkMessagebox(title="Success", message="Accession updated successfully.", icon="check")
        self.master.master.show_frame(HomeFrame)

    def open_edit(self, accession_id):
        from ui.edit_accession import EditAccessionFrame
        self.master.master.master.show_frame(EditAccessionFrame, accession_id=accession_id)

    def go_back(self):
        from ui.search_accession import SearchAccessionFrame
        self.get_app().show_frame(SearchAccessionFrame)