#!/usr/bin/env python3
"""
Ross-Tech VCDS Fault Codes Android App

A Kivy-based mobile application for searching fault codes offline.
"""

import os
import sqlite3
import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import platform

class FaultCodeApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_path = self.get_database_path()
        self.check_database()
    
    def get_database_path(self):
        """Get the correct database path for the platform."""
        if platform == 'android':
            # On Android, use the app's data directory
            from android.storage import primary_external_storage_path
            app_dir = os.path.join(primary_external_storage_path(), 'FaultCodesApp')
            if not os.path.exists(app_dir):
                os.makedirs(app_dir)
            return os.path.join(app_dir, 'fault_codes.db')
        else:
            # On desktop, use current directory
            return 'fault_codes.db'
    
    def check_database(self):
        """Check if database exists and has data."""
        if not os.path.exists(self.db_path):
            self.show_popup("Database Not Found", 
                          "The fault codes database was not found.\n\nPlease copy 'fault_codes.db' to the app directory.")
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM fault_codes")
            count = cursor.fetchone()[0]
            conn.close()
            
            if count == 0:
                self.show_popup("Empty Database", 
                              "The fault codes database is empty.\n\nPlease ensure the database contains fault codes.")
                return False
            
            return True
        except sqlite3.Error as e:
            self.show_popup("Database Error", f"Error accessing database: {e}")
            return False
    
    def show_popup(self, title, message):
        """Show a popup message."""
        popup = Popup(title=title,
                     content=Label(text=message, text_size=(dp(300), None)),
                     size_hint=(0.8, 0.4))
        popup.open()
    
    def build(self):
        """Build the app interface."""
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Title
        title = Label(text='Ross-Tech VCDS Fault Codes', 
                     size_hint_y=None, height=dp(50),
                     font_size=dp(20), bold=True)
        main_layout.add_widget(title)
        
        # Search section
        search_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        self.search_input = TextInput(hint_text='Enter fault code (e.g., 00532)',
                                    multiline=False,
                                    size_hint_x=0.7)
        self.search_input.bind(on_text_validate=self.search_fault_code)
        
        search_btn = Button(text='Search', size_hint_x=0.3)
        search_btn.bind(on_press=self.search_fault_code)
        
        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_btn)
        main_layout.add_widget(search_layout)
        
        # Results section
        self.results_scroll = ScrollView()
        self.results_label = Label(text='Enter a fault code to search',
                                 text_size=(Window.width - dp(20), None),
                                 halign='left',
                                 valign='top',
                                 markup=True)
        self.results_scroll.add_widget(self.results_label)
        main_layout.add_widget(self.results_scroll)
        
        # Status bar
        self.status_label = Label(text='Ready - Enter a fault code to search',
                                size_hint_y=None, height=dp(30),
                                font_size=dp(12))
        main_layout.add_widget(self.status_label)
        
        return main_layout
    
    def search_fault_code(self, instance):
        """Search for a fault code."""
        search_text = self.search_input.text.strip()
        
        if not search_text:
            self.status_label.text = "Please enter a fault code"
            return
        
        # Validate input (should be 1-5 digits)
        if not re.match(r'^\d{1,5}$', search_text):
            self.status_label.text = "Please enter a valid fault code (1-5 digits)"
            return
        
        # Pad with zeros to 5 digits if needed
        fault_code = search_text.zfill(5)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Search for exact match first
            cursor.execute('''
                SELECT code, title, full_content, symptoms, causes, solutions, special_notes, technical_info 
                FROM fault_codes WHERE code = ?
            ''', (fault_code,))
            result = cursor.fetchone()
            
            # If no exact match, search for partial matches
            if not result:
                cursor.execute('''
                    SELECT code, title, full_content, symptoms, causes, solutions, special_notes, technical_info 
                    FROM fault_codes WHERE code LIKE ?
                ''', (f"%{fault_code}%",))
                results = cursor.fetchall()
                
                if results:
                    self.display_multiple_results(results, search_text)
                else:
                    self.display_no_results(search_text)
            else:
                self.display_single_result(result)
            
            conn.close()
            
        except sqlite3.Error as e:
            self.status_label.text = "Database error occurred"
            self.show_popup("Database Error", f"Error searching database: {e}")
    
    def display_single_result(self, result):
        """Display a single fault code result."""
        code, title, full_content, symptoms, causes, solutions, special_notes, technical_info = result
        
        text = f"[color=2E86AB][b]Fault Code: {code}[/b][/color]\n"
        
        if title:
            text += f"[color=2E86AB][b]{title}[/b][/color]\n\n"
        else:
            text += "\n"
        
        # Full Content (if available and different from individual sections)
        if full_content and len(full_content) > 100:
            text += f"[color=A23B72][b]Complete Information:[/b][/color]\n"
            # Truncate very long content for mobile display
            display_content = full_content[:1500] + "..." if len(full_content) > 1500 else full_content
            text += f"{display_content}\n\n"
        
        # Symptoms
        if symptoms:
            text += f"[color=A23B72][b]Possible Symptoms:[/b][/color]\n"
            text += f"{symptoms}\n\n"
        
        # Causes
        if causes:
            text += f"[color=A23B72][b]Possible Causes:[/b][/color]\n"
            text += f"{causes}\n\n"
        
        # Solutions
        if solutions:
            text += f"[color=A23B72][b]Possible Solutions:[/b][/color]\n"
            text += f"{solutions}\n\n"
        
        # Special Notes
        if special_notes:
            text += f"[color=A23B72][b]Special Notes:[/b][/color]\n"
            text += f"{special_notes}\n\n"
        
        # Technical Information
        if technical_info:
            text += f"[color=A23B72][b]Technical Information:[/b][/color]\n"
            text += f"{technical_info}\n"
        
        self.results_label.text = text
        self.status_label.text = f"Found fault code: {code}"
    
    def display_multiple_results(self, results, search_text):
        """Display multiple fault code results."""
        text = f"[color=A23B72][b]Multiple results found for '{search_text}':[/b][/color]\n\n"
        
        for i, (code, title, full_content, symptoms, causes, solutions, special_notes, technical_info) in enumerate(results, 1):
            text += f"[color=2E86AB][b]{i}. Fault Code: {code}[/b][/color]\n"
            if title:
                text += f"   [color=2E86AB][b]{title}[/b][/color]\n"
            
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
                text += f"   Available: {', '.join(info_preview)}\n"
            
            text += "\n"
        
        self.results_label.text = text
        self.status_label.text = f"Found {len(results)} results for '{search_text}'"
    
    def display_no_results(self, search_text):
        """Display no results message."""
        text = f"[color=E17055][b]No results found for fault code '{search_text}'[/b][/color]\n\n"
        text += "Please check the fault code and try again.\n"
        text += "Fault codes are typically 5-digit numbers (e.g., 00532).\n"
        
        self.results_label.text = text
        self.status_label.text = f"No results found for '{search_text}'"

if __name__ == '__main__':
    FaultCodeApp().run()
