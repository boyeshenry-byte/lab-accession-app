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
        self.label = ctk.CTkLabel(self, text=f"New Accession for {self.study_name}")
        self.label.pack(pady=12, padx=10)