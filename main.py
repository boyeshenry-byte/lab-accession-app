import customtkinter as ctk
from database.db import init_db, db_path
from ui.home import HomeFrame

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("IML Identifier Lab Accession")
        self.geometry("1000x800")
        init_db(db_path)
        self.current_frame = None
        self.current_study_id = None
        self.current_study_name = None
        self.show_frame(HomeFrame)
       
    def show_frame(self, frame_class, **kwargs):
        if hasattr(self, 'current_frame') and self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame_class(self, **kwargs)

if __name__ == "__main__":
    app = App()
    app.mainloop()