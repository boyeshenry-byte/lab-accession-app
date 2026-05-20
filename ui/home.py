import customtkinter as ctk
from database.db import get_db_connection, db_path
from version import __version__

class HomeFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(pady=20, padx=60, fill="both", expand=True)
        self.create_widgets()

    def new_accession(self):
            from ui.new_accession import NewAccessionFrame
            self.master.show_frame(NewAccessionFrame)

    def create_widgets(self):
        self.label = ctk.CTkLabel(self, text="Home")
        self.label.pack(pady=12, padx=10)
        self.version_label = ctk.CTkLabel(self, text=f"v{__version__}", font=ctk.CTkFont(size=10), text_color="gray")
        self.version_label.pack(side="bottom", anchor="e", pady=10, padx=10)
        
        self.new_accession_button = ctk.CTkButton(self, text="New Accession", command=self.new_accession)
        self.new_accession_button.pack(pady=16, padx=10)

        self.patient_search_button = ctk.CTkButton(self, text="Search/Edit Accessions", command=self.search_accessions)
        self.patient_search_button.pack(pady=16, padx=10)

        self.view_accession_button = ctk.CTkButton(self, text="View Accession Details", command=self.view_accession)
        self.view_accession_button.pack(pady=16, padx=10)

    def search_accessions(self):
        from ui.search_accession import SearchAccessionFrame
        self.master.show_frame(SearchAccessionFrame)

    def view_accession(self):
        from ui.view import ViewAccessionFrame
        self.master.show_frame(ViewAccessionFrame)