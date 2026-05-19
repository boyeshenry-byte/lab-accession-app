import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from database.db import get_db_connection, db_path
from datetime import datetime
from ui.home import HomeFrame
import openpyxl
import os
import sqlite3

class ViewAccessionFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(pady=20, padx=60, fill="both", expand=True)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.filters_visible = False
        self.create_widgets()
    
    def create_widgets(self):
        self.outer_frame = ctk.CTkFrame(self)
        self.outer_frame.grid(row=0, column=0, sticky="nsew")
        self.outer_frame.columnconfigure(0, weight=1)
        self.outer_frame.rowconfigure(0, weight=0)
        self.outer_frame.rowconfigure(1, weight=1)
        self.outer_frame.rowconfigure(2, weight=0)

        self.title_frame = ctk.CTkFrame(self.outer_frame)
        self.title_frame.grid(row=0, column=0, pady=12, padx=12, sticky="ew")
        self.title_label = ctk.CTkLabel(self.title_frame, text="Accession Details", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=1, padx=12)
        self.filter_button = ctk.CTkButton(self.title_frame, text="Show Filters", command=self.toggle_filters_button)
        self.filter_button.grid(row=0, column=0, padx=12)
        
        self.details_frame = ctk.CTkFrame(self.outer_frame, fg_color="green")
        self.details_frame.grid(row=1, column=0, pady=12, padx=12, sticky="nsew")
        self.details_frame.columnconfigure(0, weight=0)
        self.details_frame.columnconfigure(1, weight=1)
        self.details_frame.rowconfigure(0, weight=1)
        
        self.bottom_frame = ctk.CTkFrame(self.outer_frame, fg_color="blue")
        self.bottom_frame.grid(row=2, column=0, pady=12, padx=12, sticky="ew")

        self.back_button = ctk.CTkButton(self.bottom_frame, text="Back to Home", command=self.back_to_home)
        self.back_button.grid(row=0, column=6, columnspan=2, pady=8)

        self.export_button = ctk.CTkButton(self.bottom_frame, text="Export to Excel", command=self.export_to_excel)
        self.export_button.grid(row=0, column=4, columnspan=2, pady=8)

        self.filter_frame = ctk.CTkScrollableFrame(self.details_frame)
        self.filter_frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.filter_frame.grid_remove()  # Start with filters hidden

        self.data_frame = ctk.CTkFrame(self.details_frame)
        self.data_frame.grid(row=0, column=1, sticky="nsew", padx=12, pady=12)
        self.data_frame.columnconfigure(0, weight=1)
        self.data_frame.rowconfigure(0, weight=1)
        self.data_frame.rowconfigure(1, weight=0)

        self.treeview = ttk.Treeview(self.data_frame, 
                                     columns=("IML number", "Last Name", "First Name", "DOB", "MRN", "Study",
                                              "Accession Date", "Timepoint", "Disease", "Freezer ID", 
                                              "Tubes", "Tech Initals", "Notes"), show="headings")
        self.treeview.heading("IML number", text="IML Number")
        self.treeview.heading("Last Name", text="Last Name")
        self.treeview.heading("First Name", text="First Name")
        self.treeview.heading("DOB", text="DOB")
        self.treeview.heading("MRN", text="MRN")
        self.treeview.heading("Study", text="Study")
        self.treeview.heading("Accession Date", text="Accession Date")
        self.treeview.heading("Timepoint", text="Timepoint")
        self.treeview.heading("Disease", text="Disease")
        self.treeview.heading("Freezer ID", text="Freezer ID")
        self.treeview.heading("Tubes", text="Tubes")
        self.treeview.heading("Tech Initals", text="Tech Initials")
        self.treeview.heading("Notes", text="Notes")
        self.treeview.grid(row=0, column=0, sticky="nsew")
        self.scrollbar_tree = ttk.Scrollbar(self.data_frame, orient="horizontal", command=self.treeview.xview)
        self.scrollbar_tree.grid(row=1, column=0, sticky="ew")
        self.treeview.configure(xscrollcommand=self.scrollbar_tree.set)

        self.load_accession_details()


    def toggle_filters_button(self):
        if self.filters_visible:
            self.filter_frame.grid_remove()
            self.filter_button.configure(text="Show Filters")
        else:
            self.filter_frame.grid()
            self.filter_button.configure(text="Hide Filters")
        self.filters_visible = not self.filters_visible

    def filter_results(self):
        # Implementation for filtering results
        pass

    def export_to_excel(self):
        # Implementation for exporting accession details and results to Excel
        pass

    def load_accession_details(self):
        conn = get_db_connection(db_path)
        with conn:
            accession_details = conn.execute("""                           
            SELECT  p.iml_number, p.last_name, p.first_name, p.date_of_birth, p.ccf_number, s.study_name,
                    a.accession_date, a.timepoint, a.disease_type, a.freezer_id, tubes.tubes, t.tech_initials, a.notes
            FROM accessions a 
            JOIN enrollments e ON a.enrollment_id = e.enrollment_id
            JOIN patients p ON e.patient_id = p.patient_id
            LEFT JOIN studies s ON e.study_id = s.study_id
            LEFT JOIN techs t ON a.tech_id = t.tech_id
            LEFT JOIN (SELECT ta.accession_id,
                            GROUP_CONCAT(tt.tube_type_name || ' x' || ta.quantity, ', ') AS tubes
                        FROM tube_accessions ta
                        JOIN tube_types tt ON ta.tube_type_id = tt.tube_type_id
                        GROUP BY ta.accession_id) tubes ON a.accession_id = tubes.accession_id
            """, ).fetchall()
            for detail in accession_details:
                self.treeview.insert("", "end", values=tuple(detail))
    def get_app(self):
        widget = self
        while widget is not None:
            if hasattr(widget, 'show_frame'):
                return widget
            widget = widget.master
        return None

    def back_to_home(self):
        from ui.home import HomeFrame
        self.get_app().show_frame(HomeFrame)