import customtkinter as ctk
from database.db import get_db_connection, db_path

class HomeFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.combobox_options = self.load_studies()
        self.pack(pady=20, padx=60, fill="both", expand=True)
        self.create_widgets()

    def load_studies(self):
        conn = get_db_connection(db_path)
        studies = conn.execute("SELECT study_name FROM studies").fetchall()
        conn.close()
        return [study['study_name'] for study in studies]

    def combobox_callback(self, choice):
        print(f"Selected: {choice}")

    def create_widgets(self):
        self.label = ctk.CTkLabel(self, text="Home")
        self.label.pack(pady=12, padx=10)

        self.combobox = ctk.CTkComboBox(self, values=self.combobox_options, command=self.combobox_callback)
        self.combobox.pack(pady=12, padx=10)