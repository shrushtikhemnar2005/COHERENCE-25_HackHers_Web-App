import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
import requests
import webbrowser
import folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
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
        
        # Initialize specialty var for hospital tab
        self.specialty_var = tk.StringVar(value="General Medicine")
        
        # Create main frames
        self.create_notebook()
        
    def load_icons(self):
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
        self.hospitals_frame = ttk.Frame(self.notebook)  # Add hospitals frame
        self.emergency_frame = ttk.Frame(self.notebook)
        
        # Add frames to notebook
        self.notebook.add(self.home_frame, text="Home")
        self.notebook.add(self.diagnosis_frame, text="Symptom Checker")
        self.notebook.add(self.hospitals_frame, text="Find Hospitals")  # Add hospitals tab
        self.notebook.add(self.emergency_frame, text="Emergency")
        
        # Set up each tab
        self.setup_home_tab()
        self.setup_diagnosis_tab()
        self.setup_hospitals_tab()  # Set up hospitals tab
        self.setup_emergency_tab()
        
    def setup_home_tab(self):
        # Welcome message and system overview
        welcome_frame = tk.Frame(self.home_frame, bg="#f0f0f0")
        welcome_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_label = tk.Label(welcome_frame, text="Hospital Expert System", font=("Arial", 24, "bold"), bg="#f0f0f0")
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
        desc_label = tk.Label(welcome_frame, text=desc_text, font=("Arial", 12), justify=tk.LEFT, bg="#f0f0f0")
        desc_label.pack(pady=10, anchor="w")
        
        # Quick access buttons
        button_frame = tk.Frame(welcome_frame, bg="#f0f0f0")
        button_frame.pack(pady=20)
        
        # Symptom checker button
        symptom_btn = tk.Button(button_frame, text="Check Symptoms",command=lambda: self.notebook.select(1),font=("Arial", 12), bg="#4CAF50", fg="white",padx=10, pady=5)
        symptom_btn.grid(row=0, column=0, padx=10)
        
        # Find hospitals button
        hospitals_btn = tk.Button(button_frame, text="Find Hospitals", command=lambda: self.notebook.select(2), 
                               font=("Arial", 12), bg="#2196F3", fg="white", padx=10, pady=5)
        hospitals_btn.grid(row=0, column=1, padx=10)
                
        # Emergency button
        emergency_btn = tk.Button(button_frame, text="Emergency", command=lambda: self.notebook.select(3),font=("Arial", 12), bg="#F44336", fg="white",padx=10, pady=5)
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
        
        tips_label = tk.Label(tips_frame, text=tips_text, font=("Arial", 11), justify=tk.LEFT, bg="#f0f0f0")
        tips_label.pack(pady=10, padx=10, anchor="w")
        
        # COVID-19 information (as an example of current health alerts)
        covid_frame = tk.LabelFrame(welcome_frame, text="Health Alerts", font=("Arial", 12, "bold"), bg="#FFF3CD")
        covid_frame.pack(fill=tk.X, pady=10)
        
        covid_text = """
        Stay updated with the latest health advisories from the Ministry of Health and Family Welfare.
        Follow local health guidelines and take necessary precautions during disease outbreaks.
        """
        
        covid_label = tk.Label(covid_frame, text=covid_text, font=("Arial", 11),justify=tk.LEFT, bg="#FFF3CD")
        covid_label.pack(pady=10, padx=10, anchor="w")
        
    def setup_diagnosis_tab(self):
        # Create frames
        left_frame = tk.Frame(self.diagnosis_frame, bg="#f0f0f0")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        right_frame = tk.Frame(self.diagnosis_frame, bg="#f0f0f0")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Symptom selection section
        symptom_frame = tk.LabelFrame(left_frame, text="Select Symptoms", font=("Arial", 12, "bold"), bg="#f0f0f0")
        symptom_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create variables to store symptom selections
        self.symptom_vars = {}
        
        # Create checkbuttons for each symptom
        for i, symptom in enumerate(self.symptoms_database.keys()):
            var = tk.BooleanVar()
            self.symptom_vars[symptom] = var
            cb = tk.Checkbutton(symptom_frame, text=symptom, variable=var, font=("Arial", 11), bg="#f0f0f0")
            cb.grid(row=i, column=0, sticky="w", padx=10, pady=5)
        
        # Additional symptoms entry
        tk.Label(symptom_frame, text="Additional symptoms:", 
               font=("Arial", 11), bg="#f0f0f0").grid(row=len(self.symptoms_database)+1, column=0, sticky="w", padx=10, pady=5)
        
        self.additional_symptoms = tk.Text(symptom_frame, height=3, width=30, font=("Arial", 11))
        self.additional_symptoms.grid(row=len(self.symptoms_database)+2, column=0, sticky="w", padx=10, pady=5)
        
        # Button to check diagnosis
        check_btn = tk.Button(symptom_frame, text="Check Diagnosis", command=self.check_diagnosis,font=("Arial", 12), bg="#2196F3", fg="white",padx=10, pady=5)
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
        
    def setup_hospitals_tab(self):
        # Create main frame
        main_frame = tk.Frame(self.hospitals_frame, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Search controls frame
        search_frame = tk.LabelFrame(main_frame, text="Find Hospitals", font=("Arial", 12, "bold"), bg="#f0f0f0")
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Location entry
        tk.Label(search_frame, text="Your Location:", font=("Arial", 11), bg="#f0f0f0").grid(
            row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.location_var = tk.StringVar()
        self.location_entry = tk.Entry(search_frame, textvariable=self.location_var, width=30, font=("Arial", 11))
        self.location_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Use current location button
        current_loc_btn = tk.Button(search_frame, text="Use Current Location", command=self.get_current_location,
                                  font=("Arial", 10), bg="#607D8B", fg="white")
        current_loc_btn.grid(row=0, column=2, padx=10, pady=5)
        
        # Search radius
        tk.Label(search_frame, text="Radius (km):", font=("Arial", 11), bg="#f0f0f0").grid(
            row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.radius_var = tk.StringVar(value="5")
        radius_combo = ttk.Combobox(search_frame, textvariable=self.radius_var, 
                                  values=["1", "2", "5", "10", "20", "50"], width=5)
        radius_combo.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # Specialty filter
        tk.Label(search_frame, text="Specialty:", font=("Arial", 11), bg="#f0f0f0").grid(
            row=2, column=0, sticky="w", padx=10, pady=5)
        
        specialty_combo = ttk.Combobox(search_frame, textvariable=self.specialty_var, 
                                     values=self.specialties, width=20)
        specialty_combo.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        # Search button
        search_btn = tk.Button(search_frame, text="Find Hospitals", command=self.find_hospitals,
                             font=("Arial", 11), bg="#2196F3", fg="white", padx=10, pady=5)
        search_btn.grid(row=3, column=1, padx=10, pady=10)
        
        # Results frame
        results_frame = tk.LabelFrame(main_frame, text="Nearby Hospitals", font=("Arial", 12, "bold"), bg="#f0f0f0")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a map placeholder
        self.map_placeholder = tk.Label(results_frame, text="Enter your location and click 'Find Hospitals' to see results", 
                                      font=("Arial", 12), bg="#f0f0f0", height=15)
        self.map_placeholder.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a frame for hospital listings
        self.hospital_list_frame = tk.Frame(results_frame, bg="#f0f0f0")
        self.hospital_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create scrollable area for hospital listings
        self.hospital_canvas = tk.Canvas(self.hospital_list_frame, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(self.hospital_list_frame, orient="vertical", command=self.hospital_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.hospital_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.hospital_canvas.configure(scrollregion=self.hospital_canvas.bbox("all"))
        )
        
        self.hospital_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.hospital_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.hospital_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
                
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
    
    def get_current_location(self):
        """
        Get the user's current location via IP geolocation API.
        """
        try:
            # Here we're using a public IP geolocation API
            response = requests.get('https://ipinfo.io/json')
            if response.status_code == 200:
                data = response.json()
                if 'loc' in data:
                    # Format is "latitude,longitude"
                    coords = data['loc'].split(',')
                    self.user_latitude = float(coords[0])
                    self.user_longitude = float(coords[1])
                    
                    # Set location in entry box
                    location_name = f"{data.get('city', '')}, {data.get('region', '')}, {data.get('country', '')}"
                    self.location_var.set(location_name)
                    
                    messagebox.showinfo("Location Found", f"Using your current location: {location_name}")
                else:
                    messagebox.showerror("Error", "Could not determine your location.")
            else:
                messagebox.showerror("Error", "Could not reach location service.")
        except Exception as e:
            messagebox.showerror("Error", f"Error getting location: {str(e)}")
    
    def find_hospitals(self):
        """
        Find hospitals near the specified location.
        """
        location = self.location_var.get().strip()
        if not location:
            messagebox.showinfo("Input Required", "Please enter your location.")
            return
        
        # Try to geocode the location
        try:
            geolocator = Nominatim(user_agent="hospital_expert_system")
            loc = geolocator.geocode(location)
            
            if loc:
                self.user_latitude = loc.latitude
                self.user_longitude = loc.longitude
                
                # Clear previous hospital listings
                for widget in self.scrollable_frame.winfo_children():
                    widget.destroy()
                
                # Show loading message
                self.map_placeholder.config(text="Searching for hospitals...")
                self.root.update()
                
                # Get radius and specialty
                radius = int(float(self.radius_var.get()) * 1000)  # Convert to meters
                specialty = self.specialty_var.get()
                
                # Fetch hospitals
                hospitals = self.get_nearby_hospitals(radius, specialty)
                
                if hospitals:
                    # Update map
                    self.generate_hospital_map(hospitals)
                    
                    # Update hospital listings
                    self.update_hospital_listings(hospitals)
                    
                    # Update map placeholder
                    self.map_placeholder.config(text=f"Found {len(hospitals)} hospitals near {location}. Map opened in browser.")
                else:
                    self.map_placeholder.config(text=f"No hospitals found near {location}. Try increasing your search radius.")
            else:
                messagebox.showinfo("Location Not Found", "Could not find the specified location. Please try again.")
        except Exception as e:
            messagebox.showerror("Error", f"Error finding hospitals: {str(e)}")
    
    def get_nearby_hospitals(self, radius=5000, specialty=None):
        """
        Fetch nearby hospitals using Overpass API (OpenStreetMap data).
        """
        if not self.user_latitude or not self.user_longitude:
            return []
        
        # Construct Overpass API query
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        # Base query for hospitals and clinics
        query = f"""
        [out:json];
        (
          node["amenity"="hospital"](around:{radius},{self.user_latitude},{self.user_longitude});
          way["amenity"="hospital"](around:{radius},{self.user_latitude},{self.user_longitude});
          relation["amenity"="hospital"](around:{radius},{self.user_latitude},{self.user_longitude});
          node["amenity"="clinic"](around:{radius},{self.user_latitude},{self.user_longitude});
          way["amenity"="clinic"](around:{radius},{self.user_latitude},{self.user_longitude});
          relation["amenity"="clinic"](around:{radius},{self.user_latitude},{self.user_longitude});
        );
        out center;
        """
        
        try:
            # Send request to Overpass API
            response = requests.get(overpass_url, params={"data": query})
            response.raise_for_status()  # Raise exception for HTTP errors
            
            data = response.json()
            hospitals = data.get("elements", [])
            
            # Process hospital data
            processed_hospitals = []
            for hospital in hospitals:
                # Get coordinates (handling both node and way/relation with center)
                lat = hospital.get("lat") or hospital.get("center", {}).get("lat")
                lon = hospital.get("lon") or hospital.get("center", {}).get("lon")
                
                if lat and lon:
                    # Get facility name
                    name = hospital.get("tags", {}).get("name", "Unknown Hospital")
                    
                    # Calculate distance
                    hospital_coords = (lat, lon)
                    user_coords = (self.user_latitude, self.user_longitude)
                    distance = geodesic(user_coords, hospital_coords).kilometers
                    
                    # Get address information
                    address_parts = []
                    tags = hospital.get("tags", {})
                    
                    # Try full address first
                    if "addr:full" in tags:
                        address_parts.append(tags["addr:full"])
                    else:
                        # Otherwise build from components
                        addr_components = [
                            tags.get("addr:housenumber", ""),
                            tags.get("addr:street", ""),
                            tags.get("addr:suburb", ""),
                            tags.get("addr:city", ""),
                            tags.get("addr:postcode", "")
                        ]
                        address_parts = [part for part in addr_components if part]
                    
                    address = ", ".join(address_parts) if address_parts else "Address unavailable"
                    
                    # Get other details
                    phone = tags.get("phone", tags.get("contact:phone", "Not available"))
                    website = tags.get("website", tags.get("contact:website", ""))
                    emergency = "Yes" if tags.get("emergency") == "yes" else "No" if tags.get("emergency") == "no" else "Unknown"
                    
                    # Get healthcare specialties
                    hospital_specialties = []
                    if "healthcare:speciality" in tags:
                        specs = tags["healthcare:speciality"].split(";")
                        hospital_specialties.extend(specs)
                    
                    # Add facility type as a specialty
                    facility_type = tags.get("amenity", "").capitalize()
                    if facility_type:
                        hospital_specialties.append(facility_type)
                    
                    # Add to list if it matches the specialty filter or if no filter is applied
                    if not specialty or specialty == "General Medicine" or specialty.lower() in " ".join(hospital_specialties).lower():
                        processed_hospitals.append({
                            "name": name,
                            "lat": lat,
                            "lon": lon,
                            "distance": distance,
                            "address": address,
                            "phone": phone,
                            "website": website,
                            "emergency": emergency,
                            "specialties": hospital_specialties,
                            "type": facility_type
                        })
            
            # Sort by distance
            processed_hospitals.sort(key=lambda h: h["distance"])
            return processed_hospitals
            
        except Exception as e:
            print(f"Error fetching hospitals: {e}")
            return []
    
    def generate_hospital_map(self, hospitals):
        """
        Generate an interactive map with hospital locations and save to HTML file.
        """
        # Create a map centered at the user's location
        m = folium.Map(location=[self.user_latitude, self.user_longitude], zoom_start=13)
        
        # Add marker for user's location
        folium.Marker(
            [self.user_latitude, self.user_longitude],
            popup="Your Location",
            tooltip="Your Location",
            icon=folium.Icon(color="blue", icon="home", prefix="fa")
        ).add_to(m)
        
        # Create a marker cluster for hospitals
        marker_cluster = MarkerCluster().add_to(m)
        
        # Add markers for hospitals
        for hospital in hospitals:
            # Determine icon color based on hospital type
            color = "red" if hospital["type"] == "Hospital" else "green"
            if hospital["emergency"] == "Yes":
                color = "darkred"
            
            # Create popup with hospital information
            popup_html = f"""
            <div style="width:250px">
                <h4>{hospital['name']}</h4>
                <b>Distance:</b> {hospital['distance']:.2f} km<br>
                <b>Address:</b> {hospital['address']}<br>
                <b>Phone:</b> {hospital['phone']}<br>
                <b>Emergency:</b> {hospital['emergency']}<br>
                <b>Specialties:</b> {', '.join(hospital['specialties']) if hospital['specialties'] else 'General'}<br>
                {f'<a href="{hospital["website"]}" target="_blank">Visit Website</a>' if hospital["website"] else ''}
            </div>
            """
            
            folium.Marker(
                [hospital['lat'], hospital['lon']],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=hospital['name'],
                icon=folium.Icon(color=color, icon="plus", prefix="fa")
            ).add_to(marker_cluster)
        
        # Draw a circle representing the search radius
        folium.Circle(
            location=[self.user_latitude, self.user_longitude],
            radius=float(self.radius_var.get()) * 1000,  # Convert to meters
            color='blue',
            fill=True,
            fill_opacity=0.1
        ).add_to(m)
        
        # Save map to HTML file
        map_filename = "hospital_map.html"
        m.save(map_filename)
        
        # Open map in default browser
        webbrowser.open('file://' + os.path.realpath(map_filename))
    
    def update_hospital_listings(self, hospitals):
        """
        Update the hospital listings in the scrollable frame.
        """
        # Clear previous listings
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Create a listing for each hospital
        for i, hospital in enumerate(hospitals):
            # Create a frame for this hospital
            hospital_frame = tk.Frame(self.scrollable_frame, bg="#f5f5f5", bd=1, relief=tk.RIDGE)
            hospital_frame.pack(fill=tk.X, padx=5, pady=5, expand=True)
            
            # Hospital name
            name_label = tk.Label(hospital_frame, text=hospital['name'], font=("Arial", 12, "bold"), bg="#f5f5f5")
            name_label.pack(anchor="w", padx=10, pady=(10, 5))
            
            # Hospital type and emergency status
            type_text = f"{hospital['type']} • "
            type_text += "Emergency Services Available" if hospital['emergency'] == "Yes" else "No Emergency Services"
            
            type_label = tk.Label(hospital_frame, text=type_text, font=("Arial", 10), bg="#f5f5f5", fg="#555555")
            type_label.pack(anchor="w", padx=10)
            
            # Distance
            distance_label = tk.Label(hospital_frame, text=f"Distance: {hospital['distance']:.2f} km", font=("Arial", 10), bg="#f5f5f5")
            distance_label.pack(anchor="w", padx=10, pady=2)
            
            # Address
            address_label = tk.Label(hospital_frame, text=f"Address: {hospital['address']}", font=("Arial", 10), bg="#f5f5f5", wraplength=400, justify=tk.LEFT)
            address_label.pack(anchor="w", padx=10, pady=2)
            
            # Phone
            phone_label = tk.Label(hospital_frame, text=f"Phone: {hospital['phone']}", font=("Arial", 10), bg="#f5f5f5")
            phone_label.pack(anchor="w", padx=10, pady=2)
            
            # Specialties
            specialties_text = f"Specialties: {', '.join(hospital['specialties']) if hospital['specialties'] else 'General'}"
            specialties_label = tk.Label(hospital_frame, text=specialties_text, font=("Arial", 10), bg="#f5f5f5", wraplength=400, justify=tk.LEFT)
            specialties_label.pack(anchor="w", padx=10, pady=2)
            
            # Website button if available
            if hospital['website']:
                website_btn = tk.Button(hospital_frame, text="Visit Website", 
                                    command=lambda url=hospital['website']: webbrowser.open(url),
                                    font=("Arial", 9), bg="#2196F3", fg="white")
                website_btn.pack(anchor="w", padx=10, pady=(5, 10))
    
    def check_diagnosis(self):
        """
        Process selected symptoms and suggest possible diagnoses.
        """
        # Get selected symptoms
        selected_symptoms = [symptom for symptom, var in self.symptom_vars.items() if var.get()]
        
        # Get additional symptoms
        additional = self.additional_symptoms.get("1.0", tk.END).strip()
        if additional:
            selected_symptoms.append(additional)
        
        # Check if any symptoms are selected
        if not selected_symptoms:
            messagebox.showinfo("No Symptoms", "Please select at least one symptom.")
            return
        
        # Process selected symptoms to find possible diagnoses
        possible_diagnoses = {}
        
        for symptom in selected_symptoms:
            if symptom in self.symptoms_database:
                for diagnosis in self.symptoms_database[symptom]:
                    if diagnosis in possible_diagnoses:
                        possible_diagnoses[diagnosis] += 1
                    else:
                        possible_diagnoses[diagnosis] = 1
        
        # Sort diagnoses by frequency
        sorted_diagnoses = sorted(possible_diagnoses.items(), key=lambda x: x[1], reverse=True)
        
        # Generate diagnosis results
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        
        self.results_text.insert(tk.END, "Based on your symptoms:\n\n")
        for symptom in selected_symptoms:
            self.results_text.insert(tk.END, f"• {symptom}\n")
        
        self.results_text.insert(tk.END, "\nPossible conditions could include:\n\n")
        
        if sorted_diagnoses:
            for diagnosis, count in sorted_diagnoses:
                relevance = (count / len(selected_symptoms)) * 100
                self.results_text.insert(tk.END, f"• {diagnosis} (Relevance: {relevance:.1f}%)\n")
        else:
            self.results_text.insert(tk.END, "No specific diagnoses found for the selected symptoms.\n")
        
        #self.results_text.insert(tk.END, "\nDISCLAIMER: This is not a medical diagnosis. Please consult a healthcare professional for proper evaluation.")
        #self.results_text.config(state=tk.DISABLED)
        
        # Generate recommendations
        self.generate_recommendations(sorted_diagnoses, selected_symptoms)
    
    def generate_recommendations(self, diagnoses, symptoms):
        """
        Generate recommendations based on diagnoses and symptoms.
        """
        self.recommendation_text.config(state=tk.NORMAL)
        self.recommendation_text.delete("1.0", tk.END)
        
        # General recommendations based on symptoms
        self.recommendation_text.insert(tk.END, "Recommendations:\n\n")
        
        # Fever recommendations
        if "Fever" in symptoms:
            self.recommendation_text.insert(tk.END, "• Stay hydrated and get plenty of rest\n")
            self.recommendation_text.insert(tk.END, "• Take acetaminophen or ibuprofen to reduce fever if needed\n")
        
        # Cough recommendations
        if "Cough" in symptoms:
            self.recommendation_text.insert(tk.END, "• Stay hydrated and use a humidifier if available\n")
            self.recommendation_text.insert(tk.END, "• Use honey and warm water to soothe throat (adults only)\n")
        
        # Headache recommendations
        if "Headache" in symptoms:
            self.recommendation_text.insert(tk.END, "• Rest in a quiet, dark room\n")
            self.recommendation_text.insert(tk.END, "• Apply a cold or warm compress to your head\n")
        
        # Add specialty recommendations based on diagnoses
        required_specialists = set()
        
        for diagnosis, _ in diagnoses:
            if diagnosis in ["Heart Attack", "Angina"]:
                required_specialists.add("Cardiology")
            elif diagnosis in ["COVID-19", "Pneumonia", "Bronchitis"]:
                required_specialists.add("Pulmonology")
            elif diagnosis in ["Arthritis", "Gout"]:
                required_specialists.add("Rheumatology")
            elif diagnosis in ["Migraine", "Sinusitis"]:
                required_specialists.add("Neurology")
        
        # Add specialist recommendations
        if required_specialists:
            self.recommendation_text.insert(tk.END, "\nConsider consulting these specialists:\n")
            for specialist in required_specialists:
                self.recommendation_text.insert(tk.END, f"• {specialist}\n")
        
        # Add general advice
        self.recommendation_text.insert(tk.END, "\nImportant Note: These are general recommendations. Please consult a healthcare professional for accurate diagnosis and treatment.")
        
        self.recommendation_text.config(state=tk.DISABLED)

    def update_symptom_list(self, specialty):
        """
        Update the symptom list based on selected specialty.
        """
        # This is a placeholder for future functionality
        # Could filter or highlight symptoms relevant to the selected specialty
        pass

    def log_activity(self, action):
        """
        Log user activity for analysis.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {action}\n"
        
        # Create logs directory if it doesn't exist
        if not os.path.exists("logs"):
            os.makedirs("logs")
        
        # Append to log file
        with open("logs/activity_log.txt", "a") as log_file:
            log_file.write(log_entry)
    
    def show_about(self):
        """
        Display information about the system.
        """
        about_text = """
        Hospital Expert System v1.0
        
        This application is designed to help users check symptoms, 
        find nearby hospitals, and access emergency information.
        
        Disclaimer: This system is for informational purposes only and 
        does not provide medical advice or diagnoses. Always consult a 
        qualified healthcare professional for medical concerns.
        
        Created by: [Your Name]
        """
        
        messagebox.showinfo("About", about_text)

def main():
    root = tk.Tk()
    app = HospitalExpertSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()