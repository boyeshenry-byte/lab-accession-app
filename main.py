import customtkinter as ctk
from database.db import init_db, db_path

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("IML Identifier Lab Accession")
        self.geometry("600x500")
        init_db(db_path)
        self.create_widgets()

    def create_widgets(self):
        self.label = ctk.CTkLabel(self, text="Welcome to IML Identifier Lab Accession tool!")
        self.label.pack(pady=20)   

if __name__ == "__main__":
    app = App()
    app.mainloop()