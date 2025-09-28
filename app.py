#!/usr/bin/env python3
"""
Ross-Tech VCDS Fault Codes Desktop Application

A simple Tkinter-based desktop application for searching fault codes offline.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
import os
import re
from typing import Optional, List, Dict

class FaultCodeApp:
    def __init__(self, root):
        self.root = root
        self.db_path = "fault_codes.db"
        self.setup_ui()
        self.check_database()
    
    def setup_ui(self):
        """Set up the user interface."""
        self.root.title("Ross-Tech VCDS Fault Codes Lookup")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Ross-Tech VCDS Fault Codes Lookup", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Search frame
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        # Search label and entry
        ttk.Label(search_frame, text="Fault Code:").grid(row=0, column=0, padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=('Arial', 12))
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.search_entry.bind('<Return>', self.search_fault_code)
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        
        # Search button
        self.search_button = ttk.Button(search_frame, text="Search", command=self.search_fault_code)
        self.search_button.grid(row=0, column=2)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Search Results", padding="10")
        results_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Results text widget with scrollbar
        self.results_text = scrolledtext.ScrolledText(
            results_frame, 
            wrap=tk.WORD, 
            font=('Arial', 10),
            bg='white',
            fg='black',
            state=tk.DISABLED,
            padx=10,
            pady=10
        )
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for formatting
        self.results_text.tag_configure('title', font=('Arial', 12, 'bold'), foreground='#2E86AB')
        self.results_text.tag_configure('section', font=('Arial', 11, 'bold'), foreground='#A23B72')
        self.results_text.tag_configure('content', font=('Arial', 10), foreground='#2D3436')
        self.results_text.tag_configure('not_found', font=('Arial', 12, 'bold'), foreground='#E17055')
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Enter a fault code to search")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Focus on search entry
        self.search_entry.focus()
    
    def check_database(self):
        """Check if the database exists and has data."""
        if not os.path.exists(self.db_path):
            self.status_var.set("Database not found. Please run crawler.py first.")
            self.search_button.config(state='disabled')
            messagebox.showwarning(
                "Database Not Found", 
                "The fault codes database was not found.\n\nPlease run 'crawler.py' first to build the database."
            )
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM fault_codes")
            count = cursor.fetchone()[0]
            conn.close()
            
            if count == 0:
                self.status_var.set("Database is empty. Please run crawler.py to populate it.")
                self.search_button.config(state='disabled')
                messagebox.showwarning(
                    "Empty Database", 
                    "The fault codes database is empty.\n\nPlease run 'crawler.py' to populate it with fault codes."
                )
            else:
                self.status_var.set(f"Ready - Database contains {count} fault codes")
        except sqlite3.Error as e:
            self.status_var.set("Database error. Please check the database file.")
            self.search_button.config(state='disabled')
            messagebox.showerror("Database Error", f"Error accessing database: {e}")
    
    def on_search_change(self, event):
        """Handle search entry changes for real-time validation."""
        search_text = self.search_var.get().strip()
        
        # Enable/disable search button based on input
        if search_text and re.match(r'^\d{1,5}$', search_text):
            self.search_button.config(state='normal')
        else:
            self.search_button.config(state='disabled')
    
    def search_fault_code(self, event=None):
        """Search for a fault code in the database."""
        search_text = self.search_var.get().strip()
        
        if not search_text:
            self.status_var.set("Please enter a fault code")
            return
        
        # Validate input (should be 1-5 digits)
        if not re.match(r'^\d{1,5}$', search_text):
            self.status_var.set("Please enter a valid fault code (1-5 digits)")
            return
        
        # Pad with zeros to 5 digits if needed
        fault_code = search_text.zfill(5)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Search for exact match first
            cursor.execute(
                "SELECT code, title, full_content, symptoms, causes, solutions, special_notes, technical_info FROM fault_codes WHERE code = ?",
                (fault_code,)
            )
            result = cursor.fetchone()
            
            # If no exact match, search for partial matches
            if not result:
                cursor.execute(
                    "SELECT code, title, full_content, symptoms, causes, solutions, special_notes, technical_info FROM fault_codes WHERE code LIKE ?",
                    (f"%{fault_code}%",)
                )
                results = cursor.fetchall()
                
                if results:
                    self.display_multiple_results(results, search_text)
                else:
                    self.display_no_results(search_text)
            else:
                self.display_single_result(result)
            
            conn.close()
            
        except sqlite3.Error as e:
            self.status_var.set("Database error occurred")
            messagebox.showerror("Database Error", f"Error searching database: {e}")
    
    def display_single_result(self, result):
        """Display a single fault code result."""
        code, title, full_content, symptoms, causes, solutions, special_notes, technical_info = result
        
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        # Title
        self.results_text.insert(tk.END, f"Fault Code: {code}\n", 'title')
        if title:
            self.results_text.insert(tk.END, f"{title}\n\n", 'title')
        else:
            self.results_text.insert(tk.END, "\n", 'title')
        
        # Full Content (if available and different from individual sections)
        if full_content and len(full_content) > 100:
            self.results_text.insert(tk.END, "Complete Information:\n", 'section')
            # Truncate very long content for display
            display_content = full_content[:2000] + "..." if len(full_content) > 2000 else full_content
            self.results_text.insert(tk.END, f"{display_content}\n\n", 'content')
        
        # Symptoms
        if symptoms:
            self.results_text.insert(tk.END, "Possible Symptoms:\n", 'section')
            self.results_text.insert(tk.END, f"{symptoms}\n\n", 'content')
        
        # Causes
        if causes:
            self.results_text.insert(tk.END, "Possible Causes:\n", 'section')
            self.results_text.insert(tk.END, f"{causes}\n\n", 'content')
        
        # Solutions
        if solutions:
            self.results_text.insert(tk.END, "Possible Solutions:\n", 'section')
            self.results_text.insert(tk.END, f"{solutions}\n\n", 'content')
        
        # Special Notes
        if special_notes:
            self.results_text.insert(tk.END, "Special Notes:\n", 'section')
            self.results_text.insert(tk.END, f"{special_notes}\n\n", 'content')
        
        # Technical Information
        if technical_info:
            self.results_text.insert(tk.END, "Technical Information:\n", 'section')
            self.results_text.insert(tk.END, f"{technical_info}\n", 'content')
        
        self.results_text.config(state=tk.DISABLED)
        self.status_var.set(f"Found fault code: {code}")
    
    def display_multiple_results(self, results, search_text):
        """Display multiple fault code results."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        self.results_text.insert(tk.END, f"Multiple results found for '{search_text}':\n\n", 'section')
        
        for i, (code, title, full_content, symptoms, causes, solutions, special_notes, technical_info) in enumerate(results, 1):
            self.results_text.insert(tk.END, f"{i}. Fault Code: {code}\n", 'title')
            if title:
                self.results_text.insert(tk.END, f"   {title}\n", 'title')
            
            # Show a preview of available information
            info_preview = []
            if symptoms:
                info_preview.append("Symptoms")
            if causes:
                info_preview.append("Causes")
            if solutions:
                info_preview.append("Solutions")
            if special_notes:
                info_preview.append("Special Notes")
            if technical_info:
                info_preview.append("Technical Info")
            if full_content:
                info_preview.append("Full Content")
            
            if info_preview:
                self.results_text.insert(tk.END, f"   Available: {', '.join(info_preview)}\n", 'content')
            
            self.results_text.insert(tk.END, "\n", 'content')
        
        self.results_text.config(state=tk.DISABLED)
        self.status_var.set(f"Found {len(results)} results for '{search_text}'")
    
    def display_no_results(self, search_text):
        """Display no results message."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        self.results_text.insert(tk.END, f"No results found for fault code '{search_text}'\n\n", 'not_found')
        self.results_text.insert(tk.END, "Please check the fault code and try again.\n", 'content')
        self.results_text.insert(tk.END, "Fault codes are typically 5-digit numbers (e.g., 00532).\n", 'content')
        
        self.results_text.config(state=tk.DISABLED)
        self.status_var.set(f"No results found for '{search_text}'")

def main():
    """Main function to run the application."""
    root = tk.Tk()
    app = FaultCodeApp(root)
    
    # Center the window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Application closed by user")

if __name__ == "__main__":
    main()
