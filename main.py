import customtkinter as ctk
from database.db import init_db, db_path
from ui.home import HomeFrame

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("IML Identifier Lab Accession")
        self.geometry("600x500")
        init_db(db_path)
        self.create_widgets()

    def create_widgets(self):
        self.home_frame = HomeFrame(self)
       

if __name__ == "__main__":
    app = App()
    app.mainloop()