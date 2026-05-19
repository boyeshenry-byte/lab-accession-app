import customtkinter as ctk
from database.db import get_db_connection, db_path
from ui.new_accession import NewAccessionFrame

class HomeFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(pady=20, padx=60, fill="both", expand=True)
        self.create_widgets()

    def new_accession(self):
            self.master.show_frame(NewAccessionFrame)

    def create_widgets(self):
        self.label = ctk.CTkLabel(self, text="Home")
        self.label.pack(pady=12, padx=10)

        self.new_accession_button = ctk.CTkButton(self, text="New Accession", command=self.new_accession)
        self.new_accession_button.pack(pady=16, padx=10)

        self.patient_search_button = ctk.CTkButton(self, text="Search/Edit Accessions", command=self.search_accessions)
        self.patient_search_button.pack(pady=16, padx=10)

    def search_accessions(self):
        from ui.search_accession import SearchAccessionFrame
        self.master.show_frame(SearchAccessionFrame)