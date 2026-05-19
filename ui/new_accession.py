import customtkinter as ctk
from database.db import get_db_connection, db_path
from datetime import datetime, date
import sqlite3
from CTkMessagebox import CTkMessagebox
from ui.add_study_dialog import AddStudyDialog

class NewAccessionFrame(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(pady=20, padx=60, fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        for i in range(6):
            self.columnconfigure(i, weight=1)
        
        self.title_label = ctk.CTkLabel(self, text=f"New Accession")
        self.title_label.grid(row=0, column=0, columnspan=2, pady=12, padx=10, sticky="ew")

        self.search_label = ctk.CTkLabel(self, text="Search (MRN, Patient Name or IML #)")
        self.search_label.grid(row=1, column=0, columnspan=2, pady=8, padx=10, sticky="e")

        self.search_entry = ctk.CTkEntry(self, width=200)
        self.search_entry.grid(row=1, column=2, pady=8, padx=10, sticky="w")
        self.search_entry.bind("<Return>", lambda event: self.search_patient())

        self.search_button = ctk.CTkButton(self, text="Search", command=self.search_patient)
        self.search_button.grid(row=2, column=1, columnspan=2, pady=8)

        self.add_patient_button = ctk.CTkButton(self, text="Add Patient", command=self.show_add_patient_form)
        self.add_patient_button.grid(row=2, column=3, pady=8)

        self.back_button = ctk.CTkButton(self, text="Back", command=self.back_to_home)
        self.back_button.grid(row=0, column=5, columnspan=2, pady=8)

        self.studies = self.load_studies()
        self.study_label = ctk.CTkLabel(self, text="Select Study")
        self.study_label.grid(row=1, column=3, pady=8, padx=10, sticky="e")
        self.study_optionmenu = ctk.CTkComboBox(self, values=self.studies, command=self.on_study_selected)
        self.study_optionmenu.grid(row=1, column=4, pady=8, padx=10, sticky="w")

        self.results_frame = ctk.CTkFrame(self, height=150, width=400)
        self.results_frame.grid(row=3, column=0, columnspan=4, pady=12, padx=10, sticky="ew")

        self.accession_frame = ctk.CTkFrame(self)
        self.accession_frame.grid(row=6, column=0, columnspan=6, pady=12, padx=10, sticky="ew")
        self.accession_frame.columnconfigure(0, weight=1)
        self.accession_frame.columnconfigure(1, weight=1)

    def search_patient(self):
        search_term = self.search_entry.get().strip()
        if not search_term:
            CTkMessagebox(title="Error", message="Search by MRN, IML number, or patient name.", icon="cancel")
            return

        terms = search_term.split()
        conditions = []
        params = []

        for term in terms:
            conditions.append("iml_number LIKE ?")
            conditions.append("ccf_number LIKE ?")
            conditions.append("uh_id LIKE ?")
            conditions.append("first_name LIKE ?")
            conditions.append("last_name LIKE ?")
            params.extend([f"%{term}%",]*5)

        if len(terms) > 1:
            conditions.append("(first_name || ' ' || last_name) LIKE ?")
            params.append(f"%{search_term}%")
        
        conn = get_db_connection(db_path)
        query = f"SELECT * FROM patients WHERE {' OR '.join(conditions)}"
        patient = conn.execute(query, params).fetchall()
        conn.close()

        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if patient:
            for p in patient:
                label_text = f"{p['first_name']} {p['last_name']} | IML: {p['iml_number']} | CCF: {p['ccf_number']}"
                btn = ctk.CTkButton(self.results_frame, text=label_text, command=lambda pt=p: self.select_patient(pt))
                btn.pack(pady=4, padx=4, fill="x")
        else:
            no_results_label = ctk.CTkLabel(self.results_frame, text="No patients found.")
            no_results_label.pack(pady=4, padx=4)

    def load_studies(self):
        conn = get_db_connection(db_path)
        studies = conn.execute("SELECT study_name FROM studies").fetchall()
        conn.close()
        return ["Unknown/Pending"] + [study['study_name'] for study in studies] + ["Add New Study"]

    def select_patient(self, patient):
        self.selected_patient = patient
        for widget in self.accession_frame.winfo_children():
            widget.destroy()
        label_text = f"{patient['first_name']} {patient['last_name']} | IML: \
            {patient['iml_number']} | CCF: {patient['ccf_number']}"
        self.selected_patient_label = ctk.CTkLabel(self.accession_frame, text=label_text, wraplength=600, anchor="w")
        self.selected_patient_label.grid(row=0, column=0, columnspan=6, pady=8, padx=10, sticky="ew")

        # Auto-fill the current date in the accession date field
        self.date_label = ctk.CTkLabel(self.accession_frame, text="Date")
        self.date_label.grid(row=1, column=0, pady=8, padx=10, sticky="e")
        self.date_value = ctk.CTkLabel(self.accession_frame, text=date.today().strftime("%Y-%m-%d"))
        self.date_value.grid(row=1, column=1, pady=8, padx=10, sticky="w")

        # Timepoint
        self.timepoint_label = ctk.CTkLabel(self.accession_frame, text="Timepoint")
        self.timepoint_label.grid(row=2, column=0, pady=8, padx=10, sticky="e")
        self.timepoint_entry = ctk.CTkEntry(self.accession_frame, width=200)
        self.timepoint_entry.grid(row=2, column=1, pady=8, padx=10, sticky="w")

        # Disease Type
        self.disease_label = ctk.CTkLabel(self.accession_frame, text="Disease Type")
        self.disease_label.grid(row=3, column=0, pady=8, padx=10, sticky="e")
        self.disease_entry = ctk.CTkEntry(self.accession_frame, width=200)
        self.disease_entry.grid(row=3, column=1, pady=8, padx=10, sticky="w")

        # Tech Initials
        self.tech_label = ctk.CTkLabel(self.accession_frame, text="Tech Initials")
        self.tech_label.grid(row=4, column=0, pady=8, padx=10, sticky="e")
        self.tech_dropdown = ctk.CTkComboBox(self.accession_frame, values=self.load_techs(),\
                                                command=self.on_tech_selected, width=200)
        self.tech_dropdown.grid(row=4, column=1, pady=8, padx=10, sticky="w")

        # Freezer ID
        self.freezer_label = ctk.CTkLabel(self.accession_frame, text="Freezer ID")
        self.freezer_label.grid(row=5, column=0, pady=8, padx=10, sticky="e")
        self.freezer_entry = ctk.CTkEntry(self.accession_frame, width=200)
        self.freezer_entry.grid(row=5, column=1, pady=8, padx=10, sticky="w")

        # Tube Type
        self.tube_rows = []
        self.tube_label = ctk.CTkLabel(self.accession_frame, text="Tubes")
        self.tube_label.grid(row=6, column=0, pady=8, padx=10, sticky="e")
        self.add_tube_button = ctk.CTkButton(self.accession_frame, text="Add Tube", command=self.add_tube_row)
        self.add_tube_button.grid(row=6, column=1, pady=8, padx=10, sticky="w")

        self.save_button = ctk.CTkButton(self.accession_frame, text="Save Accession", command=self.save_accession)
        self.save_button.grid(row=100, column=0, columnspan=4, pady=16, padx=10)

    def load_techs(self):
        conn = get_db_connection(db_path)
        techs = conn.execute("SELECT tech_initials FROM techs").fetchall()
        conn.close()
        return [tech['tech_initials'] for tech in techs] + ["Other"]
    
    def on_tech_selected(self, choice):
        if choice == "Other":
            self.tech_other_entry = ctk.CTkEntry(self.accession_frame, width=200, placeholder_text="Enter initials")
            self.tech_other_entry.grid(row=4, column=2, pady=8, padx=10, sticky="w")
            self.tech_other_entry.bind("<Return>", self.add_new_tech)
            self.tech_other_entry.bind("<FocusOut>", self.add_new_tech)
        else:
            if hasattr(self, 'tech_other_entry'):
                self.tech_other_entry.destroy()
        

    def add_new_tech(self, event=None):
        new_initials = self.tech_other_entry.get().strip().upper()
        if not new_initials:
            return
        conn = get_db_connection(db_path)
        with conn:
            conn.execute("INSERT OR IGNORE INTO techs (tech_initials) VALUES (?)", (new_initials,))
        conn.close()
        updated_techs = self.load_techs()
        self.tech_dropdown.configure(values=updated_techs)
        self.tech_dropdown.set(new_initials)
        self.tech_other_entry.destroy()

    def load_tubes(self):
        conn = get_db_connection(db_path)
        tubes = conn.execute("SELECT tube_type_name FROM tube_types").fetchall()
        conn.close()
        tube_names = [tube['tube_type_name'] for tube in tubes]
        if "Other" in tube_names:
            tube_names.remove("Other")
        return tube_names + ["Other"]

   
    def on_tube_selected(self, choice, row):
        row_idx = row - 7
        tube_dropdown, quantity_entry, other_entry = self.tube_rows[row_idx]
        
        if other_entry:
            other_entry.destroy()
            
        if choice == "Other":
            new_other = ctk.CTkEntry(self.accession_frame, width=200, placeholder_text="Enter tube type")
            new_other.grid(row=row, column=3, pady=8, padx=10, sticky="w")
            new_other.bind("<Return>", self.add_new_tube)
            new_other.bind("<FocusOut>", self.add_new_tube)
            self.tube_rows[row_idx] = (tube_dropdown, quantity_entry, new_other)
        else:
            self.tube_rows[row_idx] = (tube_dropdown, quantity_entry, None)

    def add_new_tube(self, event=None):
        new_tube = self.tube_other_entry.get().strip()
        if not new_tube:
            return
        conn = get_db_connection(db_path)
        with conn:
            conn.execute("INSERT OR IGNORE INTO tube_types (tube_type_name) VALUES (?)", (new_tube,))
        conn.close()
        updated_tubes = self.load_tubes()
        self.tube_dropdown.configure(values=updated_tubes)
        self.tube_dropdown.set(new_tube)
        self.tube_other_entry.destroy()

    def add_tube_row(self):
        row_index = len(self.tube_rows) + 7
        tube_dropdown = ctk.CTkComboBox(self.accession_frame, values=self.load_tubes(),
                                    command=lambda choice, r=row_index: self.on_tube_selected(choice, r), width=150)
        tube_dropdown.grid(row=row_index, column=1, pady=8, padx=10, sticky="w")
        quantity_entry = ctk.CTkEntry(self.accession_frame, width=100, placeholder_text="Quantity")
        quantity_entry.grid(row=row_index, column=2, pady=8, padx=10, sticky="w")
        self.tube_rows.append((tube_dropdown, quantity_entry, None))

    def save_accession(self):
        if not self.tech_dropdown.get() or self.tech_dropdown.get() == "Other":
            CTkMessagebox(title="Error", message="Tech initials required.", icon="cancel")
            return
        if not self.tube_rows:
            CTkMessagebox(title="Error", message="At least one tube is required.", icon="cancel")
            return

        study_name = self.study_optionmenu.get()
        study_id = None

        if study_name != "Unknown/Pending":
            conn = get_db_connection(db_path)
            study = conn.execute("SELECT study_id FROM studies WHERE study_name = ?", (study_name,)).fetchone()
            conn.close()
            if study:
                study_id = study['study_id']

        patient_id = self.selected_patient['patient_id']
        conn = get_db_connection(db_path)
        with conn:
            enrollment = conn.execute(
                "SELECT enrollment_id FROM enrollments WHERE patient_id = ? AND study_id = ?",
                (patient_id, study_id)
            ).fetchone()
            
            if not enrollment:
                conn.execute(
                    "INSERT INTO enrollments (patient_id, study_id, enrollment_date) VALUES (?, ?, ?)",
                    (patient_id, study_id, date.today().strftime("%Y-%m-%d"))
                )
                enrollment_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            else:
                enrollment_id = enrollment['enrollment_id']
            
            # Look up tech_id
            tech_initials = self.tech_dropdown.get()
            tech = conn.execute("SELECT tech_id FROM techs WHERE tech_initials = ?", (tech_initials,)).fetchone()
            tech_id = tech['tech_id'] if tech else None

            # Insert accession
            conn.execute(
                """INSERT INTO accessions 
                (enrollment_id, accession_date, timepoint, disease_type, freezer_id, tech_id, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    enrollment_id,
                    date.today().strftime("%Y-%m-%d"),
                    self.timepoint_entry.get().strip() or None,
                    self.disease_entry.get().strip() or None,
                    self.freezer_entry.get().strip() or None,
                    tech_id,
                    None
                )
            )
            accession_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

            # Insert tubes
            for tube_dropdown, quantity_entry, other_entry in self.tube_rows:
                tube_name = tube_dropdown.get()
                quantity = quantity_entry.get().strip()
                if tube_name and quantity and tube_name != "Other":
                    tube = conn.execute("SELECT tube_type_id FROM tube_types WHERE tube_type_name = ?", (tube_name,)).fetchone()
                    if tube:
                        conn.execute(
                            "INSERT INTO tube_accessions (accession_id, tube_type_id, quantity) VALUES (?, ?, ?)",
                            (accession_id, tube['tube_type_id'], int(quantity))
                        )

        CTkMessagebox(title="Success", message="Accession saved successfully.", icon="check")
        
        # Refresh the form for the next accession
        self.focus_set()
        for widget in self.accession_frame.winfo_children():
            widget.destroy()
        self.tube_rows = []

    def show_add_patient_form(self):
        for widget in self.accession_frame.winfo_children():
            widget.destroy()
        
        # First Name
        self.new_first_name_label = ctk.CTkLabel(self.accession_frame, text="First Name", wraplength=600, anchor="w")
        self.new_first_name_label.grid(row=0, column=0, columnspan=6, pady=8, padx=10, sticky="ew")
        self.new_first_name_entry = ctk.CTkEntry(self.accession_frame, width=200, placeholder_text="First Name")
        self.new_first_name_entry.grid(row=0, column=1, pady=8, padx=10, sticky="w")

        # Last Name
        self.new_last_name_label = ctk.CTkLabel(self.accession_frame, text="Last Name", wraplength=600, anchor="w")
        self.new_last_name_label.grid(row=1, column=0, columnspan=6, pady=8, padx=10, sticky="ew")
        self.new_last_name_entry = ctk.CTkEntry(self.accession_frame, width=200, placeholder_text="Last Name")
        self.new_last_name_entry.grid(row=1, column=1, pady=8, padx=10, sticky="w")

        # IML Number
        self.new_iml_num_label = ctk.CTkLabel(self.accession_frame, text="IML Number", wraplength=600, anchor="w")
        self.new_iml_num_label.grid(row=2, column=0, columnspan=6, pady=8, padx=10, sticky="ew")
        self.new_iml_num_entry = ctk.CTkEntry(self.accession_frame, width=200, placeholder_text="IML Number")
        self.new_iml_num_entry.grid(row=2, column=1, pady=8, padx=10, sticky="w")

        # CCF Number
        self.new_ccf_num_label = ctk.CTkLabel(self.accession_frame, text="CCF Number", wraplength=600, anchor="w")
        self.new_ccf_num_label.grid(row=3, column=0, columnspan=6, pady=8, padx=10, sticky="ew")
        self.new_ccf_num_entry = ctk.CTkEntry(self.accession_frame, width=200, placeholder_text="CCF Number")
        self.new_ccf_num_entry.grid(row=3, column=1, pady=8, padx=10, sticky="w")

        # UH ID
        self.new_uh_id_label = ctk.CTkLabel(self.accession_frame, text="UH ID", wraplength=600, anchor="w")
        self.new_uh_id_label.grid(row=4, column=0, columnspan=6, pady=8, padx=10, sticky="ew")
        self.new_uh_id_entry = ctk.CTkEntry(self.accession_frame, width=200, placeholder_text="UH ID")
        self.new_uh_id_entry.grid(row=4, column=1, pady=8, padx=10, sticky="w")

        # Date of Birth
        self.new_dob_label = ctk.CTkLabel(self.accession_frame, text="Date of Birth (YYYY-MM-DD)", wraplength=600, anchor="w")
        self.new_dob_label.grid(row=5, column=0, columnspan=6, pady=8, padx=10, sticky="ew")
        self.new_dob_entry = ctk.CTkEntry(self.accession_frame, width=200, placeholder_text="Date of Birth (YYYY-MM-DD)")
        self.new_dob_entry.grid(row=5   , column=1, pady=8, padx=10, sticky="w")

        # Study
        self.new_study_label = ctk.CTkLabel(self.accession_frame, text="Study (if known)")
        self.new_study_label.grid(row=6, column=0, pady=8, padx=10, sticky="e")
        self.new_study_optionmenu = ctk.CTkComboBox(self.accession_frame, values=self.load_studies())
        self.new_study_optionmenu.grid(row=6, column=1, pady=8, padx=10, sticky="w")

        self.save_patient_button = ctk.CTkButton(self.accession_frame, text="Save Patient", command=self.save_new_patient)
        self.save_patient_button.grid(row=100, column=0, columnspan=4, pady=16, padx=10)

    def save_new_patient(self):
        first_name = self.new_first_name_entry.get().strip()
        last_name = self.new_last_name_entry.get().strip()
        iml_number = self.new_iml_num_entry.get().strip().upper()
        ccf_number = self.new_ccf_num_entry.get().strip()
        uh_id = self.new_uh_id_entry.get().strip()
        dob_str = self.new_dob_entry.get().strip()
        study_name = self.new_study_optionmenu.get()

        if not first_name or not last_name or not iml_number:
            CTkMessagebox(title="Error", message="First, last name, and IML number are required.", icon="cancel")
            return

        dob = None
        if dob_str:
            try:
                dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
            except ValueError:
                CTkMessagebox(title="Error", message="Invalid date format. Use YYYY-MM-DD.", icon="cancel")
                return

        study_id = None
        if study_name != "Unknown/Pending":
            conn = get_db_connection(db_path)
            study = conn.execute("SELECT study_id FROM studies WHERE study_name = ?", (study_name,)).fetchone()
            conn.close()
            if study:
                study_id = study['study_id']

        conn = get_db_connection(db_path)
        with conn:
            try:
                conn.execute(
                    "INSERT INTO patients (first_name, last_name, iml_number, ccf_number, uh_id, date_of_birth) \
                    VALUES (?, ?, ?, ?, ?, ?)",
                    (first_name, last_name, iml_number, ccf_number, uh_id, dob_str if dob else None)
                )
            except sqlite3.IntegrityError:
                CTkMessagebox(title="Error", 
                              message="IML Number must be unique. A patient with this IML number already exists.", 
                              icon="cancel")
                return
            patient_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

            if study_id:
                conn.execute(
                    "INSERT INTO enrollments (patient_id, study_id, enrollment_date) VALUES (?, ?, ?)",
                    (patient_id, study_id, date.today().strftime("%Y-%m-%d"))
                )
        conn = get_db_connection(db_path)
        new_patient = conn.execute(
            "SELECT * FROM patients WHERE patient_id = ?", (patient_id,)
        ).fetchone()
        conn.close()
        self.after(50, lambda: self.select_patient(new_patient)) 
        CTkMessagebox(title="Success", message=f"Patient {first_name} {last_name} added successfully.", icon="check")

    def on_study_selected(self, choice):
        if choice == "Add New Study":
            AddStudyDialog(self, on_save=self.on_new_study_saved)

    def on_new_study_saved(self, study_name):
        self.studies = self.load_studies()
        self.study_optionmenu.configure(values=self.studies)
        self.study_optionmenu.set(study_name)

    def get_app(self):
        widget = self
        while widget is not None:
            if hasattr(widget, 'show_frame'):
                return widget
            widget = widget.master
        return None

    def back_to_home(self):
        from ui.home import HomeFrame
        self.get_app().show_frame(HomeFrame)