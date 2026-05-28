import customtkinter as ctk
from database.db import get_db_connection, db_path
from CTkMessagebox import CTkMessagebox

class AddStudyDialog(ctk.CTkToplevel):
    def __init__(self, master, on_save):
        super().__init__(master)
        self.title("Add New Study")
        self.geometry("400x300")
        self.on_save = on_save
        self.grab_set()
        self.focus_force()
        self.study_name_var = ctk.StringVar()
        self.irb_number_var = ctk.StringVar()
        self.study_prefix_var = ctk.StringVar()
        self.create_widgets()
    
    def create_widgets(self):
        ctk.CTkLabel(self, text="Study Name:").pack(pady=(20, 5))
        ctk.CTkEntry(self, textvariable=self.study_name_var).pack(pady=5)
        
        ctk.CTkLabel(self, text="IRB Number:").pack(pady=5)
        ctk.CTkEntry(self, textvariable=self.irb_number_var).pack(pady=5)

        ctk.CTkLabel(self, text="Study Prefix").pack(pady=5)
        ctk.CTkEntry(self, textvariable=self.study_prefix_var).pack(pady=5)
        
        ctk.CTkButton(self, text="Save", command=self.save_study).pack(pady=20)
    
    def save_study(self):
        study_name = self.study_name_var.get().strip()
        irb_number = self.irb_number_var.get().strip()
        study_prefix = self.study_prefix_var.get().strip().upper()
        
        if not study_name or not irb_number or not study_prefix:
            CTkMessagebox(title="Error", message="Study name, IRB number and prefix are required.", icon="cancel")
            return
        
        conn = get_db_connection(db_path)
        with conn:
            conn.execute("INSERT INTO studies (study_name, irb_number, study_prefix) VALUES (?, ?, ?)", 
                         (study_name, irb_number, study_prefix))
        conn.close()
        
        CTkMessagebox(title="Success", message=f"Study '{study_name}' added successfully.", icon="check")
        
        self.grab_release()
        self.destroy()
        self.on_save(study_name)