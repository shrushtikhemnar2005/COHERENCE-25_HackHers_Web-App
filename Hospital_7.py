import tkinter as tk
from tkinter import ttk, messagebox
import requests
import folium
import webbrowser
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import os
from PIL import Image, ImageTk
import threading

class HospitalExpertSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("MediLocator - Hospital Finder")
        self.root.geometry("900x650")
        self.root.configure(bg="#f2f7ff")
        self.root.resizable(True, True)
        
        # Set app icon (you would need to add your own icon file)
        try:
            self.root.iconbitmap("hospital_icon.ico")
        except:
            pass
            
        # Initialize user location
        self.user_latitude = None
        self.user_longitude = None
        self.geolocator = Nominatim(user_agent="medilocator_app")
        
        # Create custom style
        self.create_styles()
        
        # Create main layout
        self.create_header()
        self.create_content()
        self.create_footer()
    
    def create_styles(self):
        # Configure custom styles
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configure button style
        style.configure("TButton", 
                        font=("Helvetica", 11), 
                        background="#3498db", 
                        foreground="#ffffff",
                        padding=5)
        
        # Configure notebook style
        style.configure("TNotebook", 
                        background="#f2f7ff",
                        tabmargins=[2, 5, 2, 0])
        
        style.configure("TNotebook.Tab", 
                        font=("Helvetica", 11),
                        padding=[10, 5],
                        background="#d6e4f0",
                        foreground="#333333")
        
        style.map("TNotebook.Tab",
                  background=[("selected", "#3498db")],
                  foreground=[("selected", "#ffffff")])
        
        # Configure frame style
        style.configure("TFrame", background="#f2f7ff")
        
        # Configure label style
        style.configure("TLabel", 
                        font=("Helvetica", 11),
                        background="#f2f7ff")
        
        # Custom styles
        style.configure("Header.TLabel", 
                        font=("Helvetica", 16, "bold"),
                        foreground="#2c3e50",
                        background="#f2f7ff")
        
        style.configure("Subheader.TLabel", 
                        font=("Helvetica", 12),
                        foreground="#34495e",
                        background="#f2f7ff")
        
        style.configure("Footer.TLabel", 
                        font=("Helvetica", 9),
                        foreground="#7f8c8d",
                        background="#f2f7ff")
        
        style.configure("Search.TButton", 
                        font=("Helvetica", 11, "bold"),
                        background="#2ecc71",
                        padding=6)
    
    def create_header(self):
        # Create header frame
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # App logo/title
        header_label = ttk.Label(header_frame, 
                                text="MediLocator",
                                style="Header.TLabel")
        header_label.pack(side=tk.LEFT)
        
        # App description
        desc_label = ttk.Label(header_frame,
                              text="Find nearby hospitals and medical facilities",
                              style="Subheader.TLabel")
        desc_label.pack(side=tk.LEFT, padx=10)
    
    def create_content(self):
        # Create main content notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create tabs
        self.search_tab = ttk.Frame(self.notebook)
        self.info_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.search_tab, text="Find Hospitals")
        self.notebook.add(self.info_tab, text="Medical Information")
        
        # Set up the search tab
        self.setup_search_tab()
        
        # Set up the info tab
        self.setup_info_tab()
    
    def setup_search_tab(self):
        # Create search controls frame
        control_frame = ttk.Frame(self.search_tab)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Location entry
        location_label = ttk.Label(control_frame, 
                                  text="Your Location:",
                                  style="TLabel")
        location_label.grid(row=0, column=0, padx=5, pady=10, sticky=tk.W)
        
        self.location_entry = ttk.Entry(control_frame, width=40, font=("Helvetica", 11))
        self.location_entry.grid(row=0, column=1, padx=5, pady=10)
        self.location_entry.insert(0, "Enter city or address")
        self.location_entry.bind("<FocusIn>", self.clear_placeholder)
        
        # Radius selection
        radius_label = ttk.Label(control_frame, 
                                text="Search Radius:",
                                style="TLabel")
        radius_label.grid(row=0, column=2, padx=5, pady=10, sticky=tk.W)
        
        self.radius_var = tk.StringVar(value="5")
        radius_combo = ttk.Combobox(control_frame, 
                                   textvariable=self.radius_var,
                                   values=["1", "2", "5", "10", "20"], 
                                   width=5)
        radius_combo.grid(row=0, column=3, padx=5, pady=10, sticky=tk.W)
        
        radius_unit = ttk.Label(control_frame, 
                               text="km",
                               style="TLabel")
        radius_unit.grid(row=0, column=4, padx=0, pady=10, sticky=tk.W)
        
        # Buttons frame
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=1, column=0, columnspan=5, pady=5)
        
        # Search button
        search_btn = ttk.Button(button_frame, 
                               text="Search Hospitals",
                               command=self.search_hospitals,
                               style="Search.TButton")
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Use current location button
        current_loc_btn = ttk.Button(button_frame,
                                    text="Use Current Location",
                                    command=self.use_current_location)
        current_loc_btn.pack(side=tk.LEFT, padx=5)
        
        # Create results frame
        self.results_frame = ttk.Frame(self.search_tab)
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Map placeholder
        self.map_frame = ttk.LabelFrame(self.results_frame, text="Hospital Map")
        self.map_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.map_label = ttk.Label(self.map_frame, 
                                  text="Enter your location and click 'Search Hospitals' to view nearby facilities",
                                  anchor=tk.CENTER)
        self.map_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=50)
        
        # Status bar
        self.status_frame = ttk.Frame(self.search_tab)
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = ttk.Label(self.status_frame, 
                                     text="Ready to search",
                                     anchor=tk.W)
        self.status_label.pack(fill=tk.X)
    
    def setup_info_tab(self):
        # Information content
        info_content = ttk.Frame(self.info_tab)
        info_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Emergency information
        emergency_frame = ttk.LabelFrame(info_content, text="Emergency Information")
        emergency_frame.pack(fill=tk.X, padx=5, pady=10)
        
        emergency_info = (
            "Emergency Hotlines:\n"
            "• Medical Emergency: 911 (US) / 112 (EU)\n"
            "• Poison Control: 1-800-222-1222\n\n"
            "What to do in a medical emergency:\n"
            "1. Stay calm and assess the situation\n"
            "2. Call emergency services\n"
            "3. Follow dispatcher instructions\n"
            "4. Do not move injured persons unless necessary"
        )
        
        emergency_label = ttk.Label(emergency_frame, 
                                  text=emergency_info,
                                  justify=tk.LEFT,
                                  wraplength=800)
        emergency_label.pack(fill=tk.X, padx=10, pady=10)
        
        # Common symptoms frame
        symptoms_frame = ttk.LabelFrame(info_content, text="When to Seek Medical Help")
        symptoms_frame.pack(fill=tk.X, padx=5, pady=10)
        
        symptoms_info = (
            "Seek immediate medical attention for:\n"
            "• Difficulty breathing or shortness of breath\n"
            "• Chest or upper abdominal pain or pressure\n"
            "• Fainting, sudden dizziness, weakness\n"
            "• Changes in vision\n"
            "• Confusion or changes in mental status\n"
            "• Any sudden or severe pain\n"
            "• Uncontrolled bleeding\n"
            "• Severe or persistent vomiting or diarrhea\n"
            "• Coughing or vomiting blood\n"
            "• Suicidal or homicidal feelings"
        )
        
        symptoms_label = ttk.Label(symptoms_frame, 
                                 text=symptoms_info,
                                 justify=tk.LEFT,
                                 wraplength=800)
        symptoms_label.pack(fill=tk.X, padx=10, pady=10)
        
        # First aid tips
        firstaid_frame = ttk.LabelFrame(info_content, text="Basic First Aid Tips")
        firstaid_frame.pack(fill=tk.X, padx=5, pady=10)
        
        firstaid_info = (
            "• For cuts and scrapes: Clean with soap and water, apply antibiotic ointment, cover with sterile bandage\n"
            "• For burns: Cool with cold running water for 10-15 minutes, cover with clean dry cloth\n"
            "• For sprains: Rest, apply ice, compress with bandage, elevate (RICE method)\n"
            "• For choking: Perform the Heimlich maneuver\n"
            "• For heart attack: Chew aspirin if not allergic, perform CPR if needed\n\n"
            "Note: This information is not a substitute for professional medical advice"
        )
        
        firstaid_label = ttk.Label(firstaid_frame, 
                                 text=firstaid_info,
                                 justify=tk.LEFT,
                                 wraplength=800)
        firstaid_label.pack(fill=tk.X, padx=10, pady=10)
    
    def create_footer(self):
        # Create footer frame
        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Footer text
        footer_label = ttk.Label(footer_frame, 
                               text="MediLocator v1.0 - For educational purposes only. Not for actual medical emergencies.",
                               style="Footer.TLabel")
        footer_label.pack(side=tk.LEFT)
    
    def clear_placeholder(self, event):
        if self.location_entry.get() == "Enter city or address":
            self.location_entry.delete(0, tk.END)
    
    def search_hospitals(self):
        location = self.location_entry.get().strip()
        if not location or location == "Enter city or address":
            messagebox.showinfo("Input Required", "Please enter your location.")
            return
        
        self.status_label.config(text=f"Searching for hospitals near {location}...")
        self.root.update()
        
        # Use a thread to avoid freezing the UI during search
        search_thread = threading.Thread(target=self.perform_search, args=(location,))
        search_thread.daemon = True
        search_thread.start()
    
    def perform_search(self, location):
        # Geocode the location to get latitude and longitude
        try:
            location_info = self.geolocator.geocode(location)
            if location_info:
                self.user_latitude = location_info.latitude
                self.user_longitude = location_info.longitude
                self.root.after(0, lambda: self.status_label.config(
                    text=f"Found location: {location_info.address[:60]}..."
                    if len(location_info.address) > 60 else f"Found location: {location_info.address}"))
            else:
                self.root.after(0, lambda: self.status_label.config(text="Location not found. Please try again."))
                self.root.after(0, lambda: messagebox.showinfo("Location Error", "Location not found. Please try a different location."))
                return
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text=f"Error: {str(e)}"))
            self.root.after(0, lambda: messagebox.showinfo("Location Error", f"Error finding location: {str(e)}"))
            return
        
        # Get radius in meters (convert from km)
        radius = int(float(self.radius_var.get()) * 1000)
        
        # Fetch hospital data
        self.root.after(0, lambda: self.status_label.config(text="Fetching hospital data..."))
        hospitals = self.get_real_time_hospitals(self.user_latitude, self.user_longitude, radius)
        
        # Update the map
        if hospitals:
            self.root.after(0, lambda: self.status_label.config(text=f"Found {len(hospitals)} hospitals near {location}"))
            self.root.after(0, lambda: self.update_map(hospitals))
        else:
            self.root.after(0, lambda: self.status_label.config(text=f"No hospitals found in {location} within {self.radius_var.get()} km radius"))
            self.root.after(0, lambda: self.map_label.config(text=f"No hospitals found. Try increasing your search radius."))
    
    def get_real_time_hospitals(self, latitude, longitude, radius=5000):
        """
        Fetch real-time hospital data using Overpass API (OpenStreetMap).
        """
        overpass_url = "https://overpass-api.de/api/interpreter"
        query = f"""
        [out:json];
        (
          node["amenity"="hospital"](around:{radius},{latitude},{longitude});
          way["amenity"="hospital"](around:{radius},{latitude},{longitude});
          relation["amenity"="hospital"](around:{radius},{latitude},{longitude});
          node["amenity"="clinic"](around:{radius},{latitude},{longitude});
          way["amenity"="clinic"](around:{radius},{latitude},{longitude});
          relation["amenity"="clinic"](around:{radius},{latitude},{longitude});
          node["healthcare"="hospital"](around:{radius},{latitude},{longitude});
          way["healthcare"="hospital"](around:{radius},{latitude},{longitude});
          relation["healthcare"="hospital"](around:{radius},{latitude},{longitude});
        );
        out center;
        """
        try:
            response = requests.get(overpass_url, params={"data": query})
            response.raise_for_status()
            data = response.json()
            return data.get("elements", [])
        except requests.RequestException as e:
            self.root.after(0, lambda: messagebox.showinfo("API Error", f"Error fetching hospital data: {str(e)}"))
            return []
    
    def update_map(self, hospitals):
        """
        Update the map with hospital locations and information.
        """
        if not hospitals:
            self.map_label.config(text="No hospitals found to display on the map.")
            return
        
        # Create a folium map centered at the user's location
        map_center = [self.user_latitude, self.user_longitude]
        hospital_map = folium.Map(location=map_center, zoom_start=13)
        
        # Add a marker for the user's location
        folium.Marker(
            map_center,
            tooltip="Your Location",
            popup="Your Location",
            icon=folium.Icon(color="blue", icon="user", prefix="fa")
        ).add_to(hospital_map)
        
        # Process and sort hospitals by distance
        hospital_with_distances = []
        for hospital in hospitals:
            lat = hospital.get("lat") or hospital.get("center", {}).get("lat")
            lon = hospital.get("lon") or hospital.get("center", {}).get("lon")
            name = hospital.get("tags", {}).get("name", "Unknown Hospital")
            
            if lat and lon:
                # Calculate the distance from the user's location
                hospital_coords = (lat, lon)
                user_coords = (self.user_latitude, self.user_longitude)
                distance = geodesic(user_coords, hospital_coords).km
                
                # Get facility type and details
                facility_type = hospital.get("tags", {}).get("amenity") or hospital.get("tags", {}).get("healthcare", "hospital")
                phone = hospital.get("tags", {}).get("phone") or "Not available"
                healthcare = hospital.get("tags", {}).get("healthcare:speciality") or "General"
                emergency = "Yes" if hospital.get("tags", {}).get("emergency") == "yes" else "Unknown"
                
                # Get address components
                address = hospital.get("tags", {}).get("addr:full", "")
                if not address:
                    street = hospital.get("tags", {}).get("addr:street", "")
                    housenumber = hospital.get("tags", {}).get("addr:housenumber", "")
                    city = hospital.get("tags", {}).get("addr:city", "")
                    address = f"{housenumber} {street}, {city}".strip()
                    if not address:
                        address = "Address not available"
                
                hospital_with_distances.append({
                    "hospital": hospital,
                    "distance": distance,
                    "lat": lat,
                    "lon": lon,
                    "name": name,
                    "address": address,
                    "type": facility_type,
                    "phone": phone,
                    "healthcare": healthcare,
                    "emergency": emergency
                })
        
        # Sort by distance
        hospital_with_distances.sort(key=lambda x: x["distance"])
        
        # Get only the closest hospitals to avoid overloading the map
        closest_hospitals = hospital_with_distances[:15]
        
        # Add markers for hospitals
        for idx, hospital_info in enumerate(closest_hospitals):
            lat = hospital_info["lat"]
            lon = hospital_info["lon"]
            name = hospital_info["name"]
            distance = hospital_info["distance"]
            address = hospital_info["address"]
            facility_type = hospital_info["type"]
            phone = hospital_info["phone"]
            healthcare = hospital_info["healthcare"]
            emergency = hospital_info["emergency"]
            
            # Determine icon color based on the type of facility
            icon_color = "red"
            if facility_type == "clinic":
                icon_color = "green"
                
            # Create a detailed popup
            popup_html = f"""
            <div style="width: 250px;">
                <h4 style="margin-bottom: 5px;">{name}</h4>
                <div style="font-size: 12px; color: #888;">
                    {facility_type.capitalize()}
                </div>
                <div style="margin-top: 8px;">
                    <b>Distance:</b> {distance:.2f} km<br>
                    <b>Address:</b> {address}<br>
                    <b>Phone:</b> {phone}<br>
                    <b>Speciality:</b> {healthcare}<br>
                    <b>Emergency:</b> {emergency}
                </div>
            </div>
            """
            
            # Add marker with information
            folium.Marker(
                [lat, lon],
                tooltip=f"{idx+1}. {name} ({distance:.2f} km)",
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=icon_color, icon="plus", prefix="fa")
            ).add_to(hospital_map)
            
            # Add a circle around the hospital to indicate its proximity
            folium.Circle(
                [lat, lon],
                radius=100,  # 100 meter radius circle
                color=icon_color,
                fill=True,
                fill_opacity=0.2
            ).add_to(hospital_map)
        
        # Save the map to an HTML file and open it in a browser
        map_file = os.path.join(os.path.expanduser("~"), "medilocator_map.html")
        hospital_map.save(map_file)
        webbrowser.open('file://' + map_file)
        
        # Update map label
        self.map_label.config(text=f"Map opened in browser showing {len(closest_hospitals)} nearest hospitals and clinics")
    
    def use_current_location(self):
        """
        Get the user's current location via IP geolocation.
        """
        self.status_label.config(text="Getting your current location...")
        self.root.update()
        
        # Use a thread to avoid freezing the UI
        location_thread = threading.Thread(target=self.fetch_current_location)
        location_thread.daemon = True
        location_thread.start()
    
    def fetch_current_location(self):
        try:
            # Use ipinfo.io to get approximate location based on IP
            response = requests.get('https://ipinfo.io/json')
            data = response.json()
            
            if 'loc' in data:
                # Format is "latitude,longitude"
                lat, lon = data['loc'].split(',')
                self.user_latitude = float(lat)
                self.user_longitude = float(lon)
                
                # Get readable location name
                location_name = f"{data.get('city', '')}, {data.get('region', '')}, {data.get('country', '')}"
                location_name = location_name.strip(', ')
                
                self.root.after(0, lambda: self.location_entry.delete(0, tk.END))
                self.root.after(0, lambda: self.location_entry.insert(0, location_name))
                self.root.after(0, lambda: self.status_label.config(text=f"Using location: {location_name}"))
                self.root.after(0, lambda: self.search_hospitals())
            else:
                raise ValueError("Location information not found")
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text="Could not determine your location"))
            self.root.after(0, lambda: messagebox.showinfo("Location Error", 
                            "Could not determine your location. Please enter it manually."))


def main():
    root = tk.Tk()
    app = HospitalExpertSystem(root)
    root.mainloop()


if __name__ == "__main__":
    main()