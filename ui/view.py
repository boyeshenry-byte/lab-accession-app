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
        
        self.details_frame = ctk.CTkFrame(self.outer_frame)
        self.details_frame.grid(row=1, column=0, pady=12, padx=12, sticky="nsew")
        self.details_frame.columnconfigure(0, weight=0)
        self.details_frame.columnconfigure(1, weight=1)
        self.details_frame.rowconfigure(0, weight=1)
        
        self.bottom_frame = ctk.CTkFrame(self.outer_frame)
        self.bottom_frame.grid(row=2, column=0, pady=12, padx=12, sticky="ew")

        self.back_button = ctk.CTkButton(self.bottom_frame, text="Back to Home", command=self.back_to_home)
        self.back_button.grid(row=0, column=6, columnspan=2, pady=8)

        self.export_button = ctk.CTkButton(self.bottom_frame, text="Export to Excel", command=self.export_to_excel)
        self.export_button.grid(row=0, column=4, columnspan=2, pady=8)

        self.filter_frame = ctk.CTkScrollableFrame(self.details_frame, width=300)
        self.filter_frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        self.filter_frame.grid_remove()  # Start with filters hidden

        self.filter_title = ctk.CTkLabel(self.filter_frame, text="Filter")
        self.filter_title.grid(column=0, row=0)

        self.name_search_label = ctk.CTkLabel(self.filter_frame, text="Patient Name")
        self.name_search_label.grid(column=0, row=1)
        self.name_filter_entry = ctk.CTkEntry(self.filter_frame)
        self.name_filter_entry.grid(column=1, row=1)

        self.tech_filter_label = ctk.CTkLabel(self.filter_frame, text="Tech Initals")
        self.tech_filter_label.grid(column=0, row=3)
        self.tech_filter_dropdown = ctk.CTkComboBox(self.filter_frame, values=["All"] + self.load_techs())
        self.tech_filter_dropdown.grid(column=1, row=3)

        self.mrn_filter_label = ctk.CTkLabel(self.filter_frame, text="Patient MRN")
        self.mrn_filter_label.grid(column=0, row=4)
        self.mrn_filter_entry = ctk.CTkEntry(self.filter_frame)
        self.mrn_filter_entry.grid(column=1, row=4)

        self.study_filter_label = ctk.CTkLabel(self.filter_frame, text="Study")
        self.study_filter_label.grid(column=0, row=5)
        self.study_filter_dropdown = ctk.CTkComboBox(self.filter_frame, values=["All"] + self.load_studies())
        self.study_filter_dropdown.grid(column=1, row=5)

        self.timepoint_filter_label = ctk.CTkLabel(self.filter_frame, text="Timepoint")
        self.timepoint_filter_label.grid(column=0, row=6)
        self.timepoint_filter_entry = ctk.CTkEntry(self.filter_frame)
        self.timepoint_filter_entry.grid(column=1, row=6)

        self.disease_filter_label = ctk.CTkLabel(self.filter_frame, text="Disease")
        self.disease_filter_label.grid(column=0, row=7)
        self.disease_filter_entry = ctk.CTkEntry(self.filter_frame)
        self.disease_filter_entry.grid(column=1, row=7)

        self.freezer_filter_label = ctk.CTkLabel(self.filter_frame, text="Freezer ID")
        self.freezer_filter_label.grid(column=0, row=8)
        self.freezer_filter_entry = ctk.CTkEntry(self.filter_frame)
        self.freezer_filter_entry.grid(column=1, row=8)

        self.accession_filter_label = ctk.CTkLabel(self.filter_frame, text="Accession Date")
        self.accession_filter_label.grid(column=0, row=9, columnspan=2)
        self.accession_from_label = ctk.CTkLabel(self.filter_frame, text="From")
        self.accession_from_label.grid(column=0, row=10)
        self.accession_to_label = ctk.CTkLabel(self.filter_frame, text="To")
        self.accession_to_label.grid(column=1, row=10)
        self.accession_from_entry = ctk.CTkEntry(self.filter_frame)
        self.accession_from_entry.grid(column=0, row=11)
        self.accession_to_entry = ctk.CTkEntry(self.filter_frame)
        self.accession_to_entry.grid(column=1, row=11)

        self.apply_filter_button = ctk.CTkButton(self.filter_frame, text="Filter", command=self.filter_results)
        self.apply_filter_button.grid(column=0, row=100)

        self.reset_filter_button = ctk.CTkButton(self.filter_frame, text="Reset", command=self.reset_filter)
        self.reset_filter_button.grid(column=1, row=100)

        self.data_frame = ctk.CTkFrame(self.details_frame)
        self.data_frame.grid(row=0, column=1, sticky="nsew", padx=12, pady=12)
        self.data_frame.columnconfigure(0, weight=1)
        self.data_frame.rowconfigure(0, weight=1)
        self.data_frame.rowconfigure(1, weight=0)

        self.treeview = ttk.Treeview(self.data_frame, 
                                     columns=("Freezer ID", "Last Name", "First Name", "DOB", "MRN", "Study",
                                              "Accession Date", "Timepoint", "Disease",
                                              "Tubes", "Tech Initals", "Notes"), show="headings")
        self.treeview.heading("Freezer ID", text="Freezer ID")
        self.treeview.heading("Last Name", text="Last Name")
        self.treeview.heading("First Name", text="First Name")
        self.treeview.heading("DOB", text="DOB")
        self.treeview.heading("MRN", text="MRN")
        self.treeview.heading("Study", text="Study")
        self.treeview.heading("Accession Date", text="Accession Date")
        self.treeview.heading("Timepoint", text="Timepoint")
        self.treeview.heading("Disease", text="Disease")
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
        search_name = self.name_filter_entry.get().strip()
        mrn_filter = self.mrn_filter_entry.get().strip()
        tech_filter = self.tech_filter_dropdown.get().strip()
        study_filter = self.study_filter_dropdown.get().strip()
        timepoint_filter  = self.timepoint_filter_entry.get().strip()
        disease_filter = self.disease_filter_entry.get().strip()
        freezer_filter = self.freezer_filter_entry.get().strip()
        from_date = self.accession_from_entry.get().strip()
        to_date = self.accession_to_entry.get().strip()
        
        conditions = []
        params = []

        if search_name:
            conditions.append("(p.first_name || ' ' || p.last_name) LIKE ?")
            params.append(f"%{search_name}%")

        if tech_filter and tech_filter != "All":
            conditions.append("t.tech_initials = ?")
            params.append(tech_filter)

        if study_filter and study_filter != "All":
            conditions.append("s.study_name = ?")
            params.append(study_filter)

        if timepoint_filter:
            conditions.append("a.timepoint = ?")
            params.append(timepoint_filter)

        if disease_filter:
            conditions.append("a.disease_type = ?")
            params.append(disease_filter)

        if freezer_filter:
            conditions.append("e.freezer_id = ?")
            params.append(freezer_filter)

        if mrn_filter:
            conditions.append("p.ccf_number = ?")
            params.append(mrn_filter)

        if from_date or to_date:
            if from_date and not to_date:
                conditions.append("a.accession_date >= ?")
                params.append(from_date)
            if to_date and not from_date:
                conditions.append("a.accession_date <= ?")
                params.append(to_date)
            if from_date and to_date:
                conditions.append("a.accession_date BETWEEN ? AND ?")
                params.extend([from_date, to_date])

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        conn = get_db_connection(db_path)
        query = f"""
            SELECT  e.freezer_id, p.last_name, p.first_name, p.date_of_birth, p.ccf_number, s.study_name,
                    a.accession_date, a.timepoint, a.disease_type, tubes.tubes, t.tech_initials, a.notes
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
            {where_clause}
        """
        results = conn.execute(query, params).fetchall()
        conn.close()
        for row in self.treeview.get_children():
            self.treeview.delete(row)

        for result in results:
            self.treeview.insert("", "end", values=tuple(result))

    def export_to_excel(self):
        #vals = []
        #for row in self.treeview.get_children():
         #   vals.append(self.treeview.item(row, "values"))

        #openpyxl.Workbook()
        #openpyxl.workbook.active
        
        #openpyxl.worksheet.append("")\
        pass

    def load_accession_details(self):
        conn = get_db_connection(db_path)
        with conn:
            accession_details = conn.execute("""                           
            SELECT  e.freezer_id, p.last_name, p.first_name, p.date_of_birth, p.ccf_number, s.study_name,
                    a.accession_date, a.timepoint, a.disease_type, tubes.tubes, t.tech_initials, a.notes
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

    def load_techs(self):
        conn = get_db_connection(db_path)
        with conn:
            techs = conn.execute("SELECT tech_initials FROM techs").fetchall()
        conn.close()
        return [tech['tech_initials'] for tech in techs]
    
    def load_studies(self):
        conn = get_db_connection(db_path)
        with conn:
            studies = conn.execute("SELECT study_name FROM studies").fetchall()
        conn.close()
        return [study['study_name'] for study in studies]
    
    def reset_filter(self):
        entries=[self.name_filter_entry, self.accession_from_entry, self.accession_to_entry, 
                 self.timepoint_filter_entry, self.mrn_filter_entry, self.freezer_filter_entry, self.disease_filter_entry]
        dropdowns=[self.tech_filter_dropdown, self.study_filter_dropdown]
        
        for entry in entries:
            entry.delete(0, "end")
        for dropdown in dropdowns:
            dropdown.set("All")
        
        for row in self.treeview.get_children():
            self.treeview.delete(row)
        
        self.load_accession_details()