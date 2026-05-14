import customtkinter as ctk
from database.db import get_db_connection, db_path

class NewAccessionFrame(ctk.CTkFrame):
    def __init__(self, master, study_id, study_name):
        super().__init__(master)
        self.study_id = study_id
        self.study_name = study_name
        self.pack(pady=20, padx=60, fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        
        self.title_label = ctk.CTkLabel(self, text=f"New Accession - {self.study_name}")
        self.title_label.grid(row=0, column=0, columnspan=2, pady=12, padx=10, sticky="ew")

        self.search_label = ctk.CTkLabel(self, text="Search Patient (MRN or IML #)")
        self.search_label.grid(row=1, column=0, pady=8, padx=10, sticky="e")

        self.search_entry = ctk.CTkEntry(self, width=200)
        self.search_entry.grid(row=1, column=1, pady=8, padx=10, sticky="w")
        self.search_entry.bind("<Return>", lambda event: self.search_patient())

        self.search_button = ctk.CTkButton(self, text="Search", command=self.search_patient)
        self.search_button.grid(row=2, column=0, columnspan=2, pady=8)

        self.back_button = ctk.CTkButton(self, text="Back", command=self.back_to_home)
        self.back_button.grid(row=3, column=0, columnspan=2, pady=8)

    def back_to_home(self):
        from ui.home import HomeFrame
        self.master.show_frame(HomeFrame)

    def search_patient(self):
        search_term = self.search_entry.get().strip()
        if not search_term:
            print("Please enter an MRN or IML number to search.")
            return
        conn = get_db_connection(db_path)
        patient = conn.execute("SELECT * FROM patients WHERE iml_number LIKE ? OR ccf_number LIKE ?", (f"%{search_term}%", f"%{search_term}%")).fetchone()
        conn.close()

        if patient:
            print(f"Patient found: {patient['first_name']} {patient['last_name']} (IML: {patient['iml_number']}, CCF: {patient['ccf_number']})")
        else:
            print("No patient found with that MRN or IML number.")