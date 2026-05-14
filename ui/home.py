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

    def new_accession(self):
            study_name = self.combobox.get()
            if study_name:
                conn = get_db_connection(db_path)
                study = conn.execute("SELECT study_id FROM studies WHERE study_name = ?", (study_name,)).fetchone()
                conn.close()
                if study:
                    #self.master.show_frame(NewAccessionFrame, study_id=study['study_id'], study_name=study_name)
                    print(f"Study ID: {study['study_id']}, Study Name: {study_name}")
            else:
                print("Please select a study before creating a new accession.")

    def create_widgets(self):
        self.label = ctk.CTkLabel(self, text="Home")
        self.label.pack(pady=12, padx=10)

        self.combobox = ctk.CTkComboBox(self, values=self.combobox_options, command=self.combobox_callback)
        self.combobox.pack(pady=12, padx=10)

        self.new_accession_button = ctk.CTkButton(self, text="New Accession", command=self.new_accession)
        self.new_accession_button.pack(pady=16, padx=10)

    
        