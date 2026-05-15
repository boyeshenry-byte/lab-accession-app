import customtkinter as ctk
from database.db import get_db_connection, db_path
from datetime import datetime, date

class NewAccessionFrame(ctk.CTkFrame):
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

        self.back_button = ctk.CTkButton(self, text="Back", command=self.back_to_home)
        self.back_button.grid(row=0, column=5, columnspan=2, pady=8)

        self.studies = self.load_studies()
        self.study_label = ctk.CTkLabel(self, text="Select Study")
        self.study_label.grid(row=1, column=3, pady=8, padx=10, sticky="e")
        self.study_optionmenu = ctk.CTkOptionMenu(self, values=self.studies)
        self.study_optionmenu.grid(row=1, column=4, pady=8, padx=10, sticky="w")

        self.results_frame = ctk.CTkFrame(self, height=150, width=400)
        self.results_frame.grid(row=3, column=0, columnspan=4, pady=12, padx=10, sticky="ew")

        self.accession_frame = ctk.CTkFrame(self)
        self.accession_frame.grid(row=6, column=0, columnspan=6, pady=12, padx=10, sticky="ew")
        self.accession_frame.columnconfigure(0, weight=1)
        self.accession_frame.columnconfigure(1, weight=1)

    def back_to_home(self):
        from ui.home import HomeFrame
        self.master.show_frame(HomeFrame)

    def search_patient(self):
        search_term = self.search_entry.get().strip()
        if not search_term:
            print("Search by MRN, IML number, or patient name.")
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
        return ["Unknown/Pending"] + [study['study_name'] for study in studies]

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
        self.tech_entry = ctk.CTkEntry(self.accession_frame, width=200)
        self.tech_entry.grid(row=4, column=1, pady=8, padx=10, sticky="w")

        # Freezer ID
        self.freezer_label = ctk.CTkLabel(self.accession_frame, text="Freezer ID")
        self.freezer_label.grid(row=5, column=0, pady=8, padx=10, sticky="e")
        self.freezer_entry = ctk.CTkEntry(self.accession_frame, width=200)
        self.freezer_entry.grid(row=5, column=1, pady=8, padx=10, sticky="w")

