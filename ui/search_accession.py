import customtkinter as ctk
from database.db import get_db_connection, db_path
import sqlite3
from ui.add_study_dialog import AddStudyDialog
from CTkMessagebox import CTkMessagebox

class SearchAccessionFrame(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(pady=20, padx=60, fill="both", expand=True)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.create_widgets()

    def load_studies(self):
        conn = get_db_connection(db_path)
        with conn:
            studies = conn.execute("SELECT study_name FROM studies").fetchall()
        conn.close()
        return [study['study_name'] for study in studies]

    def back_to_home(self):
        from ui.home import HomeFrame
        self.master.master.show_frame(HomeFrame)

    def create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.search_label = ctk.CTkLabel(self, text="Search by Patient Name or ID:")
        self.search_label.grid(row=1, column=0, pady=8, padx=10, sticky="e")
        self.search_entry = ctk.CTkEntry(self, width=200)
        self.search_entry.grid(row=1, column=1, pady=8, padx=10, sticky="w")
        self.search_entry.bind("<Return>", lambda event: self.search_patient())

        self.search_button = ctk.CTkButton(self, text="Search", command=self.search_patient)
        self.search_button.grid(row=1, column=2, columnspan=2, pady=8)

        self.tech_dropdown_label = ctk.CTkLabel(self, text="Filter by Technician:")
        self.tech_dropdown_label.grid(row=3, column=0, pady=8, padx=10, sticky="e")
        self.tech_dropdown = ctk.CTkComboBox(self, values=["All"] + self.load_techs())
        self.tech_dropdown.grid(row=3, column=1, columnspan=2, pady=8)

        self.study_dropdown_label = ctk.CTkLabel(self, text="Filter by Study:")
        self.study_dropdown_label.grid(row=4, column=0, pady=8, padx=10, sticky="e")
        self.study_dropdown = ctk.CTkComboBox(self, values=["All"] + self.load_studies())
        self.study_dropdown.grid(row=4, column=1, columnspan=2, pady=8)

        self.title_label = ctk.CTkLabel(self, text="Search Accessions", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=12)

        self.back_button = ctk.CTkButton(self, text="Back to Home", command=self.back_to_home)
        self.back_button.grid(row=0, column=6, columnspan=2, pady=8)

    def load_techs(self):
        conn = get_db_connection(db_path)
        with conn:
            techs = conn.execute("SELECT tech_initials FROM techs").fetchall()
        conn.close()
        return [tech['tech_initials'] for tech in techs]
    
    def load_studies(self):
        conn = get_db_connection(db_path)
        with conn:
            studies = conn.execute("SELECT study_name FROM studies").fetchall()
        conn.close()
        return [study['study_name'] for study in studies]
    
    def search_patient(self):
        search_term = self.search_entry.get().strip()
        tech_filter = self.tech_dropdown.get().strip()
        study_filter = self.study_dropdown.get().strip()
        
        conditions = []
        params = []

        if search_term:
            conditions.append("(p.first_name || ' ' || p.last_name LIKE ? OR p.iml_number LIKE ? OR p.ccf_number LIKE ?)")
            params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])

        if tech_filter and tech_filter != "All":
            conditions.append("t.tech_initials = ?")
            params.append(tech_filter)

        if study_filter and study_filter != "All":
            conditions.append("s.study_name = ?")
            params.append(study_filter)

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        conn = get_db_connection(db_path)
        query = f"""
            SELECT a.accession_id, p.first_name, p.last_name, p.iml_number, 
                s.study_name, a.accession_date, t.tech_initials
            FROM patients p
            JOIN enrollments e ON p.patient_id = e.patient_id
            LEFT JOIN studies s ON e.study_id = s.study_id
            JOIN accessions a ON e.enrollment_id = a.enrollment_id
            LEFT JOIN techs t ON a.tech_id = t.tech_id
            {where_clause}
        """
        results = conn.execute(query, params).fetchall()
        conn.close()
        self.display_search_results(results)
    
    def display_search_results(self, results):
        for widget in self.winfo_children():
            if int(widget.grid_info().get("row", -1)) > 4:
                widget.destroy()
        if not results:
            no_results_message = CTkMessagebox(title="No Results", message="No patients found.", icon="cancel")
            return
        for idx, result in enumerate(results):
            result_button = result_button = ctk.CTkButton(self, 
                                                          text=f"{result['first_name']} {result['last_name']} \
                                                            (IML: {result['iml_number']}) - {result['study_name'] if result['study_name'] else 'No Study'} \
                                                                - {result['accession_date']}",
                                                          command=lambda r=result: self.open_edit(r['accession_id']),
                                                            anchor="w"
)
            result_button.grid(row=5+idx, column=0, columnspan=3, pady=4, sticky='ew')

    def open_edit(self, accession_id):
        print(f"Opening accession {accession_id}")