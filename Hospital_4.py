import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
import requests
import webbrowser
import folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from PIL import Image, ImageTk
import io
import os
import json
from datetime import datetime

# Replace with your actual API key
MAP_API_KEY = "YOUR_MAP_API_KEY"

class HospitalExpertSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Hospital and Medical Facilities Management System")
        self.root.geometry("1100x700")
        self.root.configure(bg="#f0f0f0")
        
        # Load icons and images
        self.load_icons()
        
        # Initialize user location
        self.user_latitude = None
        self.user_longitude = None
        self.geolocator = Nominatim(user_agent="hospital_expert_system")
        
        # Create database of common symptoms and potential diagnoses
        self.symptoms_database = {
            "Fever": ["Viral Infection", "Malaria", "Typhoid", "COVID-19"],
            "Cough": ["Common Cold", "Bronchitis", "Pneumonia", "COVID-19"],
            "Headache": ["Tension Headache", "Migraine", "Sinusitis"],
            "Chest Pain": ["Angina", "Heart Attack", "Muscle Strain", "GERD"],
            "Abdominal Pain": ["Appendicitis", "Gastritis", "Food Poisoning"],
            "Shortness of Breath": ["Asthma", "Pneumonia", "Heart Failure", "COVID-19"],
            "Joint Pain": ["Arthritis", "Gout", "Injury"],
            "Rash": ["Allergic Reaction", "Eczema", "Chicken Pox"],
            "Dizziness": ["Low Blood Pressure", "Anemia", "Vertigo"],
            "Fatigue": ["Anemia", "Thyroid Disorders", "Depression", "COVID-19"]
        }
        
        # Hospital specialties
        self.specialties = [
            "General Medicine", "Cardiology", "Orthopedics", "Pediatrics", 
            "Gynecology", "Neurology", "Ophthalmology", "ENT", "Dermatology",
            "Oncology", "Nephrology", "Urology", "Psychiatry"
        ]
        
        # Create main frames
        self.create_notebook()
        
        # Load sample hospital data for India
        self.load_hospital_data()
        
    def load_icons(self):
        # This would normally load from files, but for the example we'll create basic icons
        # In a real application, you'd have these files in an 'icons' directory
        
        # Create directory for temporary icons if it doesn't exist
        if not os.path.exists("temp_icons"):
            os.makedirs("temp_icons")
            
        # Generate a simple hospital icon and save it
        hospital_img = Image.new('RGBA', (64, 64), (255, 255, 255, 0))
        # This is a very basic representation - in a real app you'd use actual icon files
        self.hospital_icon = ImageTk.PhotoImage(hospital_img)
        
        # Load other icons in the same way
        self.emergency_icon = ImageTk.PhotoImage(Image.new('RGBA', (64, 64), (255, 0, 0, 128)))
        self.search_icon = ImageTk.PhotoImage(Image.new('RGBA', (20, 20), (0, 0, 255, 128)))
        self.location_icon = ImageTk.PhotoImage(Image.new('RGBA', (20, 20), (0, 255, 0, 128)))
        
    def create_notebook(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create frames for each tab
        self.home_frame = ttk.Frame(self.notebook)
        self.diagnosis_frame = ttk.Frame(self.notebook)
        self.hospitals_frame = ttk.Frame(self.notebook)
        self.emergency_frame = ttk.Frame(self.notebook)
        
        # Add frames to notebook
        self.notebook.add(self.home_frame, text="Home")
        self.notebook.add(self.diagnosis_frame, text="Symptom Checker")
        self.notebook.add(self.hospitals_frame, text="Find Hospitals")
        self.notebook.add(self.emergency_frame, text="Emergency")
        
        # Set up each tab
        self.setup_home_tab()
        self.setup_diagnosis_tab()
        self.setup_hospitals_tab()
        self.setup_emergency_tab()
        
    def setup_home_tab(self):
        # Welcome message and system overview
        welcome_frame = tk.Frame(self.home_frame, bg="#f0f0f0")
        welcome_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_label = tk.Label(welcome_frame, text="Hospital Expert System", 
                               font=("Arial", 24, "bold"), bg="#f0f0f0")
        header_label.pack(pady=20)
        
        # Description
        desc_text = """
        Welcome to the Hospital and Medical Facilities Management System.
        
        This application helps you:
        • Check symptoms and get preliminary diagnosis suggestions
        • Find hospitals near your location
        • Get emergency medical assistance
        • Access health information
        
        Please select a tab to begin.
        """
        
        desc_label = tk.Label(welcome_frame, text=desc_text, font=("Arial", 12), 
                             justify=tk.LEFT, bg="#f0f0f0")
        desc_label.pack(pady=10, anchor="w")
        
        # Quick access buttons
        button_frame = tk.Frame(welcome_frame, bg="#f0f0f0")
        button_frame.pack(pady=20)
        
        # Symptom checker button
        symptom_btn = tk.Button(button_frame, text="Check Symptoms", 
                              command=lambda: self.notebook.select(1),
                              font=("Arial", 12), bg="#4CAF50", fg="white",
                              padx=10, pady=5)
        symptom_btn.grid(row=0, column=0, padx=10)
        
        # Find hospitals button
        hospital_btn = tk.Button(button_frame, text="Find Hospitals", 
                               command=lambda: self.notebook.select(2),
                               font=("Arial", 12), bg="#2196F3", fg="white",
                               padx=10, pady=5)
        hospital_btn.grid(row=0, column=1, padx=10)
        
        # Emergency button
        emergency_btn = tk.Button(button_frame, text="Emergency", 
                                command=lambda: self.notebook.select(3),
                                font=("Arial", 12), bg="#F44336", fg="white",
                                padx=10, pady=5)
        emergency_btn.grid(row=0, column=2, padx=10)
        
        # Health tips section
        tips_frame = tk.LabelFrame(welcome_frame, text="Health Tips", 
                                  font=("Arial", 12, "bold"), bg="#f0f0f0")
        tips_frame.pack(fill=tk.X, pady=20)
        
        tips_text = """
        • Stay hydrated by drinking at least 8 glasses of water daily
        • Include fruits and vegetables in your daily diet
        • Practice regular hand washing to prevent infections
        • Exercise for at least 30 minutes daily
        • Get 7-8 hours of sleep each night
        """
        
        tips_label = tk.Label(tips_frame, text=tips_text, font=("Arial", 11), 
                             justify=tk.LEFT, bg="#f0f0f0")
        tips_label.pack(pady=10, padx=10, anchor="w")
        
        # COVID-19 information (as an example of current health alerts)
        covid_frame = tk.LabelFrame(welcome_frame, text="Health Alerts", 
                                   font=("Arial", 12, "bold"), bg="#FFF3CD")
        covid_frame.pack(fill=tk.X, pady=10)
        
        covid_text = """
        Stay updated with the latest health advisories from the Ministry of Health and Family Welfare.
        Follow local health guidelines and take necessary precautions during disease outbreaks.
        """
        
        covid_label = tk.Label(covid_frame, text=covid_text, font=("Arial", 11), 
                              justify=tk.LEFT, bg="#FFF3CD")
        covid_label.pack(pady=10, padx=10, anchor="w")
        
    def setup_diagnosis_tab(self):
        # Create frames
        left_frame = tk.Frame(self.diagnosis_frame, bg="#f0f0f0")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        right_frame = tk.Frame(self.diagnosis_frame, bg="#f0f0f0")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Symptom selection section
        symptom_frame = tk.LabelFrame(left_frame, text="Select Symptoms", 
                                     font=("Arial", 12, "bold"), bg="#f0f0f0")
        symptom_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create variables to store symptom selections
        self.symptom_vars = {}
        
        # Create checkbuttons for each symptom
        for i, symptom in enumerate(self.symptoms_database.keys()):
            var = tk.BooleanVar()
            self.symptom_vars[symptom] = var
            cb = tk.Checkbutton(symptom_frame, text=symptom, variable=var, 
                               font=("Arial", 11), bg="#f0f0f0")
            cb.grid(row=i, column=0, sticky="w", padx=10, pady=5)
        
        # Additional symptoms entry
        tk.Label(symptom_frame, text="Additional symptoms:", 
               font=("Arial", 11), bg="#f0f0f0").grid(row=len(self.symptoms_database)+1, 
                                                    column=0, sticky="w", padx=10, pady=5)
        
        self.additional_symptoms = tk.Text(symptom_frame, height=3, width=30, 
                                         font=("Arial", 11))
        self.additional_symptoms.grid(row=len(self.symptoms_database)+2, column=0, 
                                    sticky="w", padx=10, pady=5)
        
        # Button to check diagnosis
        check_btn = tk.Button(symptom_frame, text="Check Diagnosis", 
                            command=self.check_diagnosis,
                            font=("Arial", 12), bg="#2196F3", fg="white",
                            padx=10, pady=5)
        check_btn.grid(row=len(self.symptoms_database)+3, column=0, pady=10)
        
        # Results section
        results_frame = tk.LabelFrame(right_frame, text="Diagnosis Results", 
                                     font=("Arial", 12, "bold"), bg="#f0f0f0")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.results_text = tk.Text(results_frame, height=15, width=40, 
                                  font=("Arial", 11), wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.results_text.config(state=tk.DISABLED)
        
        # Recommendation section
        recommendation_frame = tk.LabelFrame(right_frame, text="Recommendations", 
                                           font=("Arial", 12, "bold"), bg="#f0f0f0")
        recommendation_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.recommendation_text = tk.Text(recommendation_frame, height=10, width=40, 
                                         font=("Arial", 11), wrap=tk.WORD)
        self.recommendation_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.recommendation_text.config(state=tk.DISABLED)
        
        # Find hospitals button
        find_hospital_btn = tk.Button(right_frame, text="Find Nearby Hospitals", 
                                    command=lambda: self.notebook.select(2),
                                    font=("Arial", 12), bg="#4CAF50", fg="white",
                                    padx=10, pady=5)
        find_hospital_btn.pack(pady=10)
        
    def setup_hospitals_tab(self):
        # Create frames
        control_frame = tk.Frame(self.hospitals_frame, bg="#f0f0f0")
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        content_frame = tk.Frame(self.hospitals_frame)
        content_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_frame = tk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_frame = tk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Location entry
        tk.Label(control_frame, text="Enter your location:", 
               font=("Arial", 11), bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        
        self.location_entry = tk.Entry(control_frame, width=30, font=("Arial", 11))
        self.location_entry.pack(side=tk.LEFT, padx=5)
        self.location_entry.insert(0, "Delhi, India")  # Default location
        
        # Specialty filter
        tk.Label(control_frame, text="Specialty:", 
               font=("Arial", 11), bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        
        self.specialty_var = tk.StringVar()
        self.specialty_var.set("All")
        
        specialty_options = ["All"] + sorted(self.specialties)
        specialty_dropdown = ttk.Combobox(control_frame, textvariable=self.specialty_var,
                                        values=specialty_options, font=("Arial", 11),
                                        width=15)
        specialty_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Search button
        search_btn = tk.Button(control_frame, text="Search", 
                             command=self.search_hospitals,
                             font=("Arial", 11), bg="#2196F3", fg="white",
                             padx=10, pady=2)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Use current location button
        current_loc_btn = tk.Button(control_frame, text="Use Current Location", 
                                  command=self.use_current_location,
                                  font=("Arial", 11), bg="#4CAF50", fg="white",
                                  padx=10, pady=2)
        current_loc_btn.pack(side=tk.LEFT, padx=5)
        
        # Hospital list
        list_frame = tk.LabelFrame(left_frame, text="Nearby Hospitals", 
                                  font=("Arial", 12, "bold"))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview for hospital list
        columns = ("Name", "Type", "Distance", "Rating")
        self.hospital_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Define headings
        for col in columns:
            self.hospital_tree.heading(col, text=col)
            if col == "Name":
                self.hospital_tree.column(col, width=150)
            else:
                self.hospital_tree.column(col, width=80, anchor=tk.CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                command=self.hospital_tree.yview)
        self.hospital_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.hospital_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind select event
        self.hospital_tree.bind("<<TreeviewSelect>>", self.on_hospital_select)
        
        # Hospital details
        details_frame = tk.LabelFrame(right_frame, text="Hospital Details", 
                                     font=("Arial", 12, "bold"))
        details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.details_text = tk.Text(details_frame, height=10, width=30, 
                                  font=("Arial", 11), wrap=tk.WORD)
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.details_text.config(state=tk.DISABLED)
        
        # Map frame
        map_frame = tk.LabelFrame(right_frame, text="Location Map", 
                                 font=("Arial", 12, "bold"))
        map_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a label for the map (in a real app, you'd embed a map here)
        self.map_label = tk.Label(map_frame, text="Map will be displayed here", 
                                font=("Arial", 11), bg="#e0e0e0")
        self.map_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Buttons for actions
        btn_frame = tk.Frame(right_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        directions_btn = tk.Button(btn_frame, text="Get Directions", 
                                 command=self.get_directions,
                                 font=("Arial", 11), bg="#2196F3", fg="white",
                                 padx=10, pady=2)
        directions_btn.pack(side=tk.LEFT, padx=5)
        
        call_btn = tk.Button(btn_frame, text="Call Hospital", 
                           command=self.call_hospital,
                           font=("Arial", 11), bg="#4CAF50", fg="white",
                           padx=10, pady=2)
        call_btn.pack(side=tk.LEFT, padx=5)
        
        book_btn = tk.Button(btn_frame, text="Book Appointment", 
                           command=self.book_appointment,
                           font=("Arial", 11), bg="#FF9800", fg="white",
                           padx=10, pady=2)
        book_btn.pack(side=tk.LEFT, padx=5)
        
    def setup_emergency_tab(self):
        # Main frame
        main_frame = tk.Frame(self.emergency_frame, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header with warning
        header_label = tk.Label(main_frame, text="EMERGENCY SERVICES", 
                               font=("Arial", 24, "bold"), fg="#F44336", bg="#f0f0f0")
        header_label.pack(pady=10)
        
        warning_label = tk.Label(main_frame, text="If you're experiencing a medical emergency, immediately call 102 or 108", 
                                font=("Arial", 14), fg="#F44336", bg="#f0f0f0")
        warning_label.pack(pady=5)
        
        # Emergency numbers
        numbers_frame = tk.LabelFrame(main_frame, text="Emergency Contact Numbers", 
                                     font=("Arial", 14, "bold"), bg="#f0f0f0")
        numbers_frame.pack(fill=tk.X, pady=15)
        
        emergency_numbers = [
            ("Ambulance", "102/108"),
            ("National Emergency Number", "112"),
            ("Police", "100"),
            ("Fire Department", "101"),
            ("Women Helpline", "1091"),
            ("Disaster Management", "108"),
            ("Poison Control", "1066")
        ]
        
        for i, (service, number) in enumerate(emergency_numbers):
            tk.Label(numbers_frame, text=service, font=("Arial", 12, "bold"), 
                   bg="#f0f0f0").grid(row=i, column=0, sticky="w", padx=20, pady=5)
            
            number_frame = tk.Frame(numbers_frame, bg="#f0f0f0")
            number_frame.grid(row=i, column=1, padx=20, pady=5)
            
            tk.Label(number_frame, text=number, font=("Arial", 12), 
                   bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
            
            #call_btn = tk.Button(number_frame, text="Call", 
                               #command=lambda n=number: self.call_emergency(n),
                               #font=("Arial", 10), bg="#F44336", fg="white",
                               #padx=5, pady=1)
            #call_btn.pack(side=tk.LEFT, padx=5)
        
        # First Aid Guidelines
        firstaid_frame = tk.LabelFrame(main_frame, text="Basic First Aid Guidelines", 
                                      font=("Arial", 14, "bold"), bg="#f0f0f0")
        firstaid_frame.pack(fill=tk.BOTH, expand=True, pady=15)
        
        # Create a notebook for first aid categories
        firstaid_notebook = ttk.Notebook(firstaid_frame)
        firstaid_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # First aid categories and instructions
        firstaid_info = {
            "Cardiac Emergency": """
            1. Call emergency services (102/108) immediately
            2. Begin CPR if the person is unresponsive and not breathing normally
            3. If available, use an AED (Automated External Defibrillator)
            4. Continue CPR until emergency services arrive
            """,
            
            "Choking": """
            1. Encourage the person to cough
            2. If coughing doesn't help, give 5 back blows
            3. If back blows don't help, give 5 abdominal thrusts (Heimlich maneuver)
            4. Alternate between 5 back blows and 5 abdominal thrusts
            5. If the person becomes unconscious, begin CPR
            """,
            
            "Bleeding": """
            1. Apply direct pressure to the wound using a clean cloth
            2. If possible, elevate the injured area above the heart
            3. Apply a bandage firmly but not too tight
            4. If blood soaks through, add more material without removing the first layer
            5. Seek medical attention
            """,
            
            "Burns": """
            1. For minor burns: Cool the burn with cold running water for 10-15 minutes
            2. Do not apply ice directly to the burn
            3. Do not apply butter, oil, or ointments
            4. Cover with a clean, non-stick bandage
            5. For severe burns: Call emergency services immediately
            """,
            
            "Fractures": """
            1. Keep the injured area immobilized
            2. Apply ice wrapped in a cloth to reduce swelling
            3. Do not attempt to realign the bone
            4. If there's an open fracture, cover the wound with a clean cloth
            5. Seek immediate medical attention
            """
        }
        
        # Create tabs for each first aid category
        for category, instructions in firstaid_info.items():
            tab = ttk.Frame(firstaid_notebook)
            firstaid_notebook.add(tab, text=category)
            
            text_widget = tk.Text(tab, wrap=tk.WORD, font=("Arial", 11), height=10)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert(tk.END, instructions)
            text_widget.config(state=tk.DISABLED)
        
        # Find nearest emergency services button
        find_emergency_btn = tk.Button(main_frame, text="Find Nearest Emergency Services", 
                                     command=self.find_emergency_services,
                                     font=("Arial", 14), bg="#F44336", fg="white",
                                     padx=10, pady=5)
        find_emergency_btn.pack(pady=15)
        
    def check_diagnosis(self):
        # Get selected symptoms
        selected_symptoms = [symptom for symptom, var in self.symptom_vars.items() if var.get()]
        
        # Get additional symptoms
        additional = self.additional_symptoms.get("1.0", tk.END).strip()
        
        if not selected_symptoms and not additional:
            messagebox.showinfo("No Symptoms", "Please select at least one symptom.")
            return
        
        # Clear previous results
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.recommendation_text.config(state=tk.NORMAL)
        self.recommendation_text.delete("1.0", tk.END)
        
        # Display selected symptoms
        self.results_text.insert(tk.END, "Selected Symptoms:\n")
        for symptom in selected_symptoms:
            self.results_text.insert(tk.END, f"- {symptom}\n")
        
        if additional:
            self.results_text.insert(tk.END, f"\nAdditional Symptoms:\n{additional}\n")
        
        # Determine possible diagnoses based on symptoms
        possible_diagnoses = {}
        for symptom in selected_symptoms:
            for diagnosis in self.symptoms_database.get(symptom, []):
                if diagnosis in possible_diagnoses:
                    possible_diagnoses[diagnosis] += 1
                else:
                    possible_diagnoses[diagnosis] = 1
        
        # Sort diagnoses by frequency
        sorted_diagnoses = sorted(possible_diagnoses.items(), key=lambda x: x[1], reverse=True)
        
        # Display possible diagnoses
        self.results_text.insert(tk.END, "\nPossible Conditions:\n")
        if sorted_diagnoses:
            for diagnosis, count in sorted_diagnoses:
                confidence = (count / len(selected_symptoms)) * 100
                self.results_text.insert(tk.END, f"- {diagnosis} (Confidence: {confidence:.0f}%)\n")
        else:
            self.results_text.insert(tk.END, "No specific conditions identified based on your symptoms.\n")
        
        # Provide recommendations
        self.results_text.insert(tk.END, "\nNOTE: This is only a preliminary assessment. Please consult a healthcare professional for accurate diagnosis and treatment.\n")
        
        self.recommendation_text.insert(tk.END, "Recommendations:\n\n")
        
        # Based on severity, provide different recommendations
        has_severe_symptoms = any(s in selected_symptoms for s in ["Chest Pain", "Shortness of Breath"])
        has_moderate_symptoms = any(s in selected_symptoms for s in ["Fever", "Abdominal Pain"])
        
        if has_severe_symptoms:
            self.recommendation_text.insert(tk.END, "URGENT: Some of your symptoms may indicate a serious condition. Seek immediate medical attention or call emergency services.\n\n")
            # Highlight text
            self.recommendation_text.tag_add("urgent", "2.0", "3.0")
            self.recommendation_text.tag_config("urgent", foreground="red", font=("Arial", 11, "bold"))
        elif has_moderate_symptoms:
            self.recommendation_text.insert(tk.END, "You should consult a healthcare professional within 24 hours.\n\n")
        else:
            self.recommendation_text.insert(tk.END, "Monitor your symptoms. If they persist for more than 3 days or worsen, consult a healthcare professional.\n\n")
        
        # Add specialty recommendation
        if "Chest Pain" in selected_symptoms:
            specialty = "Cardiology"
        elif "Headache" in selected_symptoms:
            specialty = "Neurology"
        elif "Joint Pain" in selected_symptoms:
            specialty = "Orthopedics"
        elif "Rash" in selected_symptoms:
            specialty = "Dermatology"
        else:
            specialty = "General Medicine"
        
        self.recommendation_text.insert(tk.END, f"Recommended Specialty: {specialty}\n\n")
        self.recommendation_text.insert(tk.END, "Click 'Find Nearby Hospitals' to locate healthcare facilities that offer this specialty.")
        
        # Update the specialty filter in the hospitals tab
        self.specialty_var.set(specialty)
        
        # Set text widgets to read-only
        self.results_text.config(state=tk.DISABLED)
        self.recommendation_text.config(state=tk.DISABLED)
        
    def load_hospital_data(self):
        # In a real application, this would load from an API or database
        # For this example, we'll use a static list of sample hospitals in India
        self.hospitals = [
            {
                "id": 1,
                "name": "All India Institute of Medical Sciences (AIIMS)",
                "location": "New Delhi",
                "coordinates": {"lat": 28.5672, "lng": 77.2100},
                "type": "Government",
                "specialties": ["General Medicine", "Cardiology", "Neurology", "Oncology", "Orthopedics"],
                "emergency": True,
                "contact": "+91-11-26588500",
                "rating": 4.5,
                "beds": 2200,
                "website": "https://www.aiims.edu",
                "description": "AIIMS is a premier medical institution in India offering tertiary care."
            },
            {
                "id": 2,
                "name": "Apollo Hospitals",
                "location": "Chennai",
                "coordinates": {"lat": 13.0827, "lng": 80.2707},
                "type": "Private",
                "specialties": ["Cardiology", "Orthopedics", "Nephrology", "Oncology"],
                "emergency": True,
                "contact": "+91-44-28290200",
                "rating": 4.7,
                "beds": 1000,
                "website": "https://www.apollohospitals.com",
                "description": "Apollo Hospitals is one of the leading private healthcare providers in India with state-of-the-art facilities."
            },
            {
                "id": 3,
                "name": "Fortis Hospital",
                "location": "Mumbai",
                "coordinates": {"lat": 19.0760, "lng": 72.8777},
                "type": "Private",
                "specialties": ["Cardiology", "Neurology", "Orthopedics", "Gynecology"],
                "emergency": True,
                "contact": "+91-22-43099999",
                "rating": 4.6,
                "beds": 800,
                "website": "https://www.fortishealthcare.com",
                "description": "Fortis is a multi-specialty hospital known for cardiac care and organ transplants."
            },
            {
                "id": 4,
                "name": "Lilavati Hospital",
                "location": "Mumbai",
                "coordinates": {"lat": 19.0509, "lng": 72.8290},
                "type": "Private",
                "specialties": ["Cardiology", "Nephrology", "Neurology", "Urology"],
                "emergency": True,
                "contact": "+91-22-26751000",
                "rating": 4.5,
                "beds": 350,
                "website": "https://www.lilavatihospital.com",
                "description": "Lilavati Hospital is a renowned multi-specialty hospital in Mumbai."
            },
            {
                "id": 5,
                "name": "Christian Medical College (CMC)",
                "location": "Vellore",
                "coordinates": {"lat": 12.9240, "lng": 79.1325},
                "type": "Private",
                "specialties": ["General Medicine", "Cardiology", "Neurology", "Pediatrics"],
                "emergency": True,
                "contact": "+91-416-2282010",
                "rating": 4.8,
                "beds": 2800,
                "website": "https://www.cmch-vellore.edu",
                "description": "CMC Vellore is known for its excellent medical education and healthcare services."
            },
            {
                "id": 6,
                "name": "Tata Memorial Hospital",
                "location": "Mumbai",
                "coordinates": {"lat": 19.0054, "lng": 72.8436},
                "type": "Government",
                "specialties": ["Oncology"],
                "emergency": True,
                "contact": "+91-22-24177000",
                "rating": 4.6,
                "beds": 700,
                "website": "https://tmc.gov.in",
                "description": "Tata Memorial is India's premier cancer treatment and research center."
            },
            {
                "id": 7,
                "name": "Narayana Health",
                "location": "Bangalore",
                "coordinates": {"lat": 12.9716, "lng": 77.5946},
                "type": "Private",
                "specialties": ["Cardiology", "Orthopedics", "Neurology", "Nephrology"],
                "emergency": True,
                "contact": "+91-80-22222222",
                "rating": 4.5,
                "beds": 500,
                "website": "https://www.narayanahealth.org",
                "description": "Narayana Health is known for affordable cardiac care and surgeries."
            },
            {
                "id": 8,
                "name": "NIMHANS",
                "location": "Bangalore",
                "coordinates": {"lat": 12.9431, "lng": 77.5959},
                "type": "Government",
                "specialties": ["Psychiatry", "Neurology"],
                "emergency": True,
                "contact": "+91-80-26995000",
                "rating": 4.6,
                "beds": 750,
                "website": "https://www.nimhans.ac.in",
                "description": "NIMHANS is a specialized hospital for neurological and psychiatric conditions."
            },
            {
                "id": 9,
                "name": "Medanta - The Medicity",
                "location": "Gurgaon",
                "coordinates": {"lat": 28.4367, "lng": 77.0426},
                "type": "Private",
                "specialties": ["Cardiology", "Neurology", "Gastroenterology", "Orthopedics"],
                "emergency": True,
                "contact": "+91-124-4141414",
                "rating": 4.7,
                "beds": 1250,
                "website": "https://www.medanta.org",
                "description": "Medanta is a multi-specialty hospital with advanced medical technology."
            },
            {
                "id": 10,
                "name": "Post Graduate Institute of Medical Education and Research (PGI)",
                "location": "Chandigarh",
                "coordinates": {"lat": 30.7642, "lng": 76.7760},
                "type": "Government",
                "specialties": ["General Medicine", "Cardiology", "Neurology", "Pediatrics"],
                "emergency": True,
                "contact": "+91-172-2746018",
                "rating": 4.5,
                "beds": 1900,
                "website": "https://pgimer.edu.in",
                "description": "PGI Chandigarh is a premier medical and research institute in North India."
            }
        ]
    
    def search_hospitals(self):
        # Clear previous results
        for item in self.hospital_tree.get_children():
            self.hospital_tree.delete(item)
        
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)
        self.details_text.config(state=tk.DISABLED)
        
        location = self.location_entry.get().strip()
        if not location:
            messagebox.showinfo("Input Required", "Please enter your location.")
            return
        
        # In a real application, you would use the Maps API to geocode the location
        # For this example, we'll simulate finding the coordinates
        try:
            # Use geopy to get coordinates
            location_info = self.geolocator.geocode(location)
            if location_info:
                self.user_latitude = location_info.latitude
                self.user_longitude = location_info.longitude
            else:
                # Default to Delhi coordinates if location not found
                self.user_latitude = 28.6139
                self.user_longitude = 77.2090
                messagebox.showinfo("Location Not Found", "Using default location (Delhi).")
        except Exception as e:
            # Default to Delhi coordinates on error
            self.user_latitude = 28.6139
            self.user_longitude = 77.2090
            messagebox.showinfo("Geocoding Error", f"Error finding location: {str(e)}\nUsing default location (Delhi).")
        
        # Filter by specialty if selected
        specialty = self.specialty_var.get()
        filtered_hospitals = self.hospitals
        if specialty != "All":
            filtered_hospitals = [h for h in self.hospitals if specialty in h["specialties"]]
        
        # Calculate distances (in a real app, this would use the Google Maps Distance Matrix API)
        for hospital in filtered_hospitals:
            # Simple Euclidean distance calculation for demonstration
            # In a real app, you would calculate road distance/time using Maps API
            lat_diff = hospital["coordinates"]["lat"] - self.user_latitude
            lng_diff = hospital["coordinates"]["lng"] - self.user_longitude
            distance = ((lat_diff ** 2) + (lng_diff ** 2)) ** 0.5
            
            # Convert to approximate km (very rough estimate)
            distance_km = distance * 111
            hospital["distance"] = distance_km
        
        # Sort by distance
        filtered_hospitals.sort(key=lambda x: x["distance"])
        
        # Display hospitals in treeview
        for hospital in filtered_hospitals:
            self.hospital_tree.insert("", tk.END, values=(
                hospital["name"],
                hospital["type"],
                f"{hospital['distance']:.1f} km",
                hospital["rating"]
            ), tags=(str(hospital["id"]),))
        
        # Update the map
        self.update_map(filtered_hospitals)
        
        # Display message if no hospitals found
        if not filtered_hospitals:
            messagebox.showinfo("No Results", f"No hospitals found with specialty: {specialty}")
    
    def update_map(self, hospitals):
        # In a real application, this would generate and display a map
        # For this example, we'll just update the text in the map label
        if hospitals:
            self.map_label.config(text=f"Map showing {len(hospitals)} hospitals near {self.location_entry.get()}")
            
            # In a real application, you would create a map using folium and display it
            # Here's an example of how you might do that:
            
            map_center = [self.user_latitude, self.user_longitude]
            m = folium.Map(location=map_center, zoom_start=12)
            
            # Add marker for user location
            folium.Marker(
                map_center,
                tooltip="Your Location",
                icon=folium.Icon(color="blue", icon="user", prefix="fa")
            ).add_to(m)
            
            # Add markers for hospitals
            for hospital in hospitals:
                folium.Marker(
                    [hospital["coordinates"]["lat"], hospital["coordinates"]["lng"]],
                    tooltip=hospital["name"],
                    popup=f"{hospital['name']}<br>{hospital['type']}<br>{hospital['contact']}",
                    icon=folium.Icon(color="red" if hospital["emergency"] else "green", icon="plus", prefix="fa")
                ).add_to(m)
            
            # Save map to HTML file
            map_file = "hospital_map.html"
            m.save(map_file)
            
            # Display the map in a webview or browser
            # This would depend on your platform and requirements
            
        else:
            self.map_label.config(text="No hospitals found to display on map")
    
    def on_hospital_select(self, event):
        selected_items = self.hospital_tree.selection()
        if not selected_items:
            return
        
        # Get the selected hospital's tag (ID)
        item = selected_items[0]
        item_values = self.hospital_tree.item(item, "values")
        hospital_name = item_values[0]
        
        # Find the hospital in our data
        selected_hospital = None
        for hospital in self.hospitals:
            if hospital["name"] == hospital_name:
                selected_hospital = hospital
                break
        
        if not selected_hospital:
            return
        
        # Update details text
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)
        
        self.details_text.insert(tk.END, f"{selected_hospital['name']}\n", "header")
        self.details_text.insert(tk.END, f"Location: {selected_hospital['location']}\n")
        self.details_text.insert(tk.END, f"Type: {selected_hospital['type']}\n")
        self.details_text.insert(tk.END, f"Distance: {selected_hospital['distance']:.1f} km\n")
        self.details_text.insert(tk.END, f"Rating: {selected_hospital['rating']} / 5.0\n")
        self.details_text.insert(tk.END, f"Beds: {selected_hospital['beds']}\n")
        self.details_text.insert(tk.END, f"Contact: {selected_hospital['contact']}\n")
        self.details_text.insert(tk.END, f"Emergency Services: {'Yes' if selected_hospital['emergency'] else 'No'}\n\n")
        
        self.details_text.insert(tk.END, "Specialties:\n")
        for specialty in selected_hospital["specialties"]:
            self.details_text.insert(tk.END, f"• {specialty}\n")
        
        self.details_text.insert(tk.END, f"\nDescription:\n{selected_hospital['description']}")
        
        # Apply style to header
        self.details_text.tag_configure("header", font=("Arial", 12, "bold"))
        
        self.details_text.config(state=tk.DISABLED)
    
    def use_current_location(self):
        # In a real application, this would use browser geolocation or a location API
        # For this example, we'll use a default location (Delhi)
        self.user_latitude = 28.6139
        self.user_longitude = 77.2090
        self.location_entry.delete(0, tk.END)
        self.location_entry.insert(0, "Delhi, India")
        
        messagebox.showinfo("Location Updated", "Using current location: Delhi, India\n\nIn a real application, this would use your device's GPS.")
        
        # Trigger search with new location
        self.search_hospitals()
    
    def get_directions(self):
        selected_items = self.hospital_tree.selection()
        if not selected_items:
            messagebox.showinfo("Selection Required", "Please select a hospital first.")
            return
        
        # Get the selected hospital
        item = selected_items[0]
        item_values = self.hospital_tree.item(item, "values")
        hospital_name = item_values[0]
        
        # Find the hospital in our data
        selected_hospital = None
        for hospital in self.hospitals:
            if hospital["name"] == hospital_name:
                selected_hospital = hospital
                break
        
        if not selected_hospital:
            return
        
        # In a real application, this would open Google Maps with directions
        # For this example, we'll just show a message
        messagebox.showinfo("Get Directions", 
                          f"Getting directions to {selected_hospital['name']}...\n\n"
                          f"In a real application, this would open Google Maps with directions from your location to the hospital.")
        
        # Example of how to open Google Maps in browser:
        """
        hospital_lat = selected_hospital["coordinates"]["lat"]
        hospital_lng = selected_hospital["coordinates"]["lng"]
        maps_url = f"https://www.google.com/maps/dir/?api=1&origin={self.user_latitude},{self.user_longitude}&destination={hospital_lat},{hospital_lng}"
        webbrowser.open(maps_url)
        """
    
    def call_hospital(self):
        selected_items = self.hospital_tree.selection()
        if not selected_items:
            messagebox.showinfo("Selection Required", "Please select a hospital first.")
            return
        
        # Get the selected hospital
        item = selected_items[0]
        item_values = self.hospital_tree.item(item, "values")
        hospital_name = item_values[0]
        
        # Find the hospital in our data
        selected_hospital = None
        for hospital in self.hospitals:
            if hospital["name"] == hospital_name:
                selected_hospital = hospital
                break
        
        if not selected_hospital:
            return
        
        # In a real application, this would initiate a call using the device's capabilities
        # For this example, we'll just show a message
        messagebox.showinfo("Call Hospital", 
                          f"Calling {selected_hospital['name']} at {selected_hospital['contact']}...\n\n"
                          f"In a real application, this would initiate a phone call to the hospital.")
    
    def book_appointment(self):
        selected_items = self.hospital_tree.selection()
        if not selected_items:
            messagebox.showinfo("Selection Required", "Please select a hospital first.")
            return
        
        # Get the selected hospital
        item = selected_items[0]
        item_values = self.hospital_tree.item(item, "values")
        hospital_name = item_values[0]
        
        # Find the hospital in our data
        selected_hospital = None
        for hospital in self.hospitals:
            if hospital["name"] == hospital_name:
                selected_hospital = hospital
                break
        
        if not selected_hospital:
            return
        
        # Create appointment booking window
        booking_window = tk.Toplevel(self.root)
        booking_window.title(f"Book Appointment - {selected_hospital['name']}")
        booking_window.geometry("500x400")
        booking_window.configure(bg="#f0f0f0")
        
        # Form fields
        form_frame = tk.Frame(booking_window, bg="#f0f0f0")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Hospital name
        tk.Label(form_frame, text=selected_hospital['name'], 
               font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)
        
        # Patient information
        info_frame = tk.LabelFrame(form_frame, text="Patient Information", 
                                  font=("Arial", 12, "bold"), bg="#f0f0f0")
        info_frame.pack(fill=tk.X, pady=10)
        
        # Name
        tk.Label(info_frame, text="Name:", font=("Arial", 11), 
               bg="#f0f0f0").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        name_entry = tk.Entry(info_frame, font=("Arial", 11), width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Age
        tk.Label(info_frame, text="Age:", font=("Arial", 11), 
               bg="#f0f0f0").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        age_entry = tk.Entry(info_frame, font=("Arial", 11), width=10)
        age_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Gender
        tk.Label(info_frame, text="Gender:", font=("Arial", 11), 
               bg="#f0f0f0").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        gender_var = tk.StringVar(value="Male")
        gender_options = ["Male", "Female", "Other"]
        gender_menu = ttk.Combobox(info_frame, textvariable=gender_var, 
                                 values=gender_options, font=("Arial", 11), width=10)
        gender_menu.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        # Phone
        tk.Label(info_frame, text="Phone:", font=("Arial", 11), 
               bg="#f0f0f0").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        phone_entry = tk.Entry(info_frame, font=("Arial", 11), width=30)
        phone_entry.grid(row=3, column=1, padx=10, pady=5)
        
        # Appointment details
        appointment_frame = tk.LabelFrame(form_frame, text="Appointment Details", 
                                        font=("Arial", 12, "bold"), bg="#f0f0f0")
        appointment_frame.pack(fill=tk.X, pady=10)
        
        # Department/Specialty
        tk.Label(appointment_frame, text="Specialty:", font=("Arial", 11), 
               bg="#f0f0f0").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        specialty_var = tk.StringVar()
        specialty_menu = ttk.Combobox(appointment_frame, textvariable=specialty_var, 
                                    values=selected_hospital["specialties"], font=("Arial", 11), width=20)
        specialty_menu.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        specialty_menu.current(0)
        
        # Date
        tk.Label(appointment_frame, text="Date:", font=("Arial", 11), 
               bg="#f0f0f0").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        # Get current date for default
        current_date = datetime.now().strftime("%Y-%m-%d")
        date_entry = tk.Entry(appointment_frame, font=("Arial", 11), width=15)
        date_entry.insert(0, current_date)
        date_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Time slots
        tk.Label(appointment_frame, text="Time Slot:", font=("Arial", 11), 
               bg="#f0f0f0").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        time_var = tk.StringVar()
        time_slots = ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", 
                     "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM"]
        time_menu = ttk.Combobox(appointment_frame, textvariable=time_var, 
                               values=time_slots, font=("Arial", 11), width=15)
        time_menu.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        time_menu.current(0)
        
        # Additional notes
        tk.Label(appointment_frame, text="Notes:", font=("Arial", 11), 
               bg="#f0f0f0").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        notes_text = tk.Text(appointment_frame, height=3, width=30, font=("Arial", 11))
        notes_text.grid(row=3, column=1, padx=10, pady=5)
        
        # Submit button
        submit_btn = tk.Button(form_frame, text="Book Appointment", 
                             command=lambda: self.submit_appointment(booking_window),
                             font=("Arial", 12), bg="#4CAF50", fg="white",
                             padx=10, pady=5)
        submit_btn.pack(pady=15)
    
    def submit_appointment(self, window):
        # In a real application, this would save the appointment to a database
        # For this example, we'll just show a confirmation and close the window
        messagebox.showinfo("Appointment Booked", 
                          "Your appointment has been booked successfully.\n\n"
                          "You will receive a confirmation SMS shortly.")
        window.destroy()
    
    def call_emergency(self, number):
        # In a real application, this would initiate a call
        # For this example, we'll just show a message
        messagebox.showinfo("Emergency Call", 
                          f"Calling emergency number {number}...\n\n"
                          f"In a real application, this would initiate an emergency call.")
    
    def find_emergency_services(self):
        # Switch to hospitals tab and set filter for emergency services
        self.notebook.select(2)  # Switch to hospitals tab
        self.specialty_var.set("All")  # Reset specialty filter
        self.location_entry.delete(0, tk.END)
        self.location_entry.insert(0, "Current Location")  # Set to current location
        
        # Use current location
        self.use_current_location()
        
        # Show message about filtering for emergency services
        messagebox.showinfo("Emergency Services", 
                          "Searching for hospitals with emergency services near your location.")

def main():
    root = tk.Tk()
    app = HospitalExpertSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()