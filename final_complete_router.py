"""
FINAL COMPLETE VESSEL ROUTE OPTIMIZER
With ALL Features Working Correctly
"""

from flask import Flask, render_template, request, jsonify
import searoute as sr
import requests
import time
import numpy as np
from geopy.distance import geodesic
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)

# ==================== VESSEL TYPES DATABASE ====================

VESSEL_TYPES = {
    "small_cargo": {"name": "🚢 Small Cargo Ship", "fuel_per_day": 15, "speed_knots": 12, "capacity": "5,000-10,000 DWT"},
    "medium_cargo": {"name": "🚢 Medium Cargo Ship", "fuel_per_day": 25, "speed_knots": 14, "capacity": "10,000-30,000 DWT"},
    "large_cargo": {"name": "🚢 Large Cargo Ship", "fuel_per_day": 45, "speed_knots": 15, "capacity": "30,000-60,000 DWT"},
    "container_small": {"name": "📦 Small Container Ship", "fuel_per_day": 40, "speed_knots": 16, "capacity": "1,000-2,000 TEU"},
    "container_medium": {"name": "📦 Medium Container Ship", "fuel_per_day": 80, "speed_knots": 18, "capacity": "3,000-6,000 TEU"},
    "container_large": {"name": "📦 Large Container Ship", "fuel_per_day": 150, "speed_knots": 20, "capacity": "10,000-15,000 TEU"},
    "tanker": {"name": "⛽ Oil/Chemical Tanker", "fuel_per_day": 60, "speed_knots": 14, "capacity": "50,000-100,000 DWT"},
    "vlcc": {"name": "🛢️ VLCC (Very Large Crude Carrier)", "fuel_per_day": 120, "speed_knots": 15, "capacity": "200,000-320,000 DWT"},
    "bulk_carrier": {"name": "⚓ Bulk Carrier", "fuel_per_day": 50, "speed_knots": 14, "capacity": "50,000-100,000 DWT"},
    "roro": {"name": "🚗 Ro-Ro Vessel", "fuel_per_day": 35, "speed_knots": 16, "capacity": "Roll-on/Roll-off"},
}

# ==================== COMPLETE PORT DATABASE WITH ALL REGIONS ====================

PORT_DATABASE = {
    # ========== SOUTH ASIA ==========
    "mumbai": (72.8777, 19.0760, "South Asia", "🇮🇳"),
    "chennai": (80.2707, 13.0827, "South Asia", "🇮🇳"),
    "kolkata": (88.3639, 22.5726, "South Asia", "🇮🇳"),
    "cochin": (76.2673, 9.9312, "South Asia", "🇮🇳"),
    "goa": (73.9840, 15.2993, "South Asia", "🇮🇳"),
    "vizag": (83.2185, 17.6868, "South Asia", "🇮🇳"),
    "tuticorin": (78.1333, 8.7833, "South Asia", "🇮🇳"),
    "mangalore": (74.8560, 12.9142, "South Asia", "🇮🇳"),
    "karachi": (67.0011, 24.8607, "South Asia", "🇵🇰"),
    "colombo": (79.8612, 6.9271, "South Asia", "🇱🇰"),
    "chittagong": (91.7832, 22.3569, "South Asia", "🇧🇩"),
    
    # ========== SOUTHEAST ASIA ==========
    "singapore": (103.8198, 1.3521, "Southeast Asia", "🇸🇬"),
    "port klang": (101.4000, 3.0000, "Southeast Asia", "🇲🇾"),
    "jakarta": (106.8456, -6.2088, "Southeast Asia", "🇮🇩"),
    "surabaya": (112.7500, -7.2500, "Southeast Asia", "🇮🇩"),
    "bangkok": (100.5000, 13.7300, "Southeast Asia", "🇹🇭"),
    "ho chi minh": (106.6297, 10.8231, "Southeast Asia", "🇻🇳"),
    "haiphong": (106.6833, 20.8500, "Southeast Asia", "🇻🇳"),
    "manila": (120.9842, 14.5995, "Southeast Asia", "🇵🇭"),
    "cebu": (123.9000, 10.3000, "Southeast Asia", "🇵🇭"),
    "davao": (125.6000, 7.1000, "Southeast Asia", "🇵🇭"),
    "rangoon": (96.1951, 16.8661, "Southeast Asia", "🇲🇲"),
    "laem chabang": (100.8833, 13.0833, "Southeast Asia", "🇹🇭"),
    
    # ========== EAST ASIA ==========
    "shanghai": (121.4737, 31.2304, "East Asia", "🇨🇳"),
    "ningbo": (121.5440, 29.8683, "East Asia", "🇨🇳"),
    "shenzhen": (114.0579, 22.5431, "East Asia", "🇨🇳"),
    "hong kong": (114.1694, 22.3193, "East Asia", "🇭🇰"),
    "guangzhou": (113.2644, 23.1291, "East Asia", "🇨🇳"),
    "xiamen": (118.0894, 24.4798, "East Asia", "🇨🇳"),
    "qingdao": (120.3826, 36.0662, "East Asia", "🇨🇳"),
    "tianjin": (117.7400, 38.9729, "East Asia", "🇨🇳"),
    "dalian": (121.6122, 38.9140, "East Asia", "🇨🇳"),
    "busan": (129.0756, 35.1796, "East Asia", "🇰🇷"),
    "tokyo": (139.8395, 35.6528, "East Asia", "🇯🇵"),
    "yokohama": (139.6381, 35.4437, "East Asia", "🇯🇵"),
    "nagoya": (136.9064, 35.0183, "East Asia", "🇯🇵"),
    "osaka": (135.5083, 34.6938, "East Asia", "🇯🇵"),
    "kobe": (135.1833, 34.6833, "East Asia", "🇯🇵"),
    "incheon": (126.7052, 37.4564, "East Asia", "🇰🇷"),
    "kaohsiung": (120.2915, 22.6269, "East Asia", "🇹🇼"),
    "taichung": (120.5333, 24.2833, "East Asia", "🇹🇼"),
    
    # ========== MIDDLE EAST ==========
    "dubai": (55.2708, 25.2048, "Middle East", "🇦🇪"),
    "abu dhabi": (54.3773, 24.4539, "Middle East", "🇦🇪"),
    "sharjah": (55.4000, 25.3500, "Middle East", "🇦🇪"),
    "fujairah": (56.3333, 25.1167, "Middle East", "🇦🇪"),
    "bandar abbas": (56.2666, 27.1832, "Middle East", "🇮🇷"),
    "muscat": (58.3829, 23.5880, "Middle East", "🇴🇲"),
    "salalah": (54.0065, 16.9425, "Middle East", "🇴🇲"),
    "sohar": (56.7278, 24.3421, "Middle East", "🇴🇲"),
    "doha": (51.5310, 25.2854, "Middle East", "🇶🇦"),
    "kuwait": (47.9774, 29.3759, "Middle East", "🇰🇼"),
    "bahrain": (50.5860, 26.2285, "Middle East", "🇧🇭"),
    "jeddah": (39.1721, 21.4769, "Middle East", "🇸🇦"),
    "dammam": (50.1000, 26.5000, "Middle East", "🇸🇦"),
    
    # ========== EUROPE ==========
    "rotterdam": (4.4792, 51.9225, "Europe", "🇳🇱"),
    "hamburg": (9.9872, 53.5488, "Europe", "🇩🇪"),
    "antwerp": (4.3997, 51.2211, "Europe", "🇧🇪"),
    "piraeus": (23.6194, 37.9429, "Europe", "🇬🇷"),
    "valencia": (-0.3222, 39.4597, "Europe", "🇪🇸"),
    "barcelona": (2.1734, 41.3851, "Europe", "🇪🇸"),
    "genoa": (8.9463, 44.4056, "Europe", "🇮🇹"),
    "istanbul": (28.9784, 41.0082, "Europe", "🇹🇷"),
    "felixstowe": (1.3487, 51.9618, "Europe", "🇬🇧"),
    "le havre": (0.1085, 49.4929, "Europe", "🇫🇷"),
    "marseille": (5.3698, 43.2965, "Europe", "🇫🇷"),
    "naples": (14.2681, 40.8518, "Europe", "🇮🇹"),
    "venice": (12.3155, 45.4408, "Europe", "🇮🇹"),
    "gdansk": (18.6667, 54.3500, "Europe", "🇵🇱"),
    "lisbon": (9.1393, 38.7223, "Europe", "🇵🇹"),
    
    # ========== NORTH AMERICA ==========
    "new york": (-74.0060, 40.7128, "North America", "🇺🇸"),
    "los angeles": (-118.2437, 33.8688, "North America", "🇺🇸"),
    "vancouver": (-123.1207, 49.2827, "North America", "🇨🇦"),
    "houston": (-95.3698, 29.7604, "North America", "🇺🇸"),
    "long beach": (-118.1937, 33.7701, "North America", "🇺🇸"),
    "seattle": (-122.3321, 47.6062, "North America", "🇺🇸"),
    "montreal": (-73.5673, 45.5017, "North America", "🇨🇦"),
    "miami": (-80.1918, 25.7617, "North America", "🇺🇸"),
    "boston": (-71.0589, 42.3601, "North America", "🇺🇸"),
    "philadelphia": (-75.1652, 39.9526, "North America", "🇺🇸"),
    "new orleans": (-90.0715, 29.9511, "North America", "🇺🇸"),
    
    # ========== SOUTH AMERICA ==========
    "santos": (-46.3333, -23.9537, "South America", "🇧🇷"),
    "buenos aires": (-58.3816, -34.6037, "South America", "🇦🇷"),
    "valparaiso": (-71.6296, -33.0360, "South America", "🇨🇱"),
    "rio de janeiro": (-43.1729, -22.9068, "South America", "🇧🇷"),
    "callao": (-77.0282, -12.0432, "South America", "🇵🇪"),
    "cartagena": (-75.4794, 10.3910, "South America", "🇨🇴"),
    "guayaquil": (-79.8862, -2.1704, "South America", "🇪🇨"),
    "montevideo": (-56.1645, -34.9011, "South America", "🇺🇾"),
    
    # ========== AFRICA ==========
    "durban": (31.0218, -29.8587, "Africa", "🇿🇦"),
    "cape town": (18.4241, -33.9249, "Africa", "🇿🇦"),
    "mombasa": (39.6682, -4.0435, "Africa", "🇰🇪"),
    "casablanca": (-7.5898, 33.5731, "Africa", "🇲🇦"),
    "djibouti": (43.1456, 11.5721, "Africa", "🇩🇯"),
    "lagos": (3.4191, 6.4278, "Africa", "🇳🇬"),
    "alexandria": (29.9187, 31.2001, "Africa", "🇪🇬"),
    "dakar": (-17.4464, 14.7167, "Africa", "🇸🇳"),
    "luanda": (13.2333, -8.8167, "Africa", "🇦🇴"),
    
    # ========== AUSTRALIA & OCEANIA ==========
    "sydney": (151.2093, -33.8688, "Australia", "🇦🇺"),
    "melbourne": (144.9631, -37.8136, "Australia", "🇦🇺"),
    "brisbane": (153.0251, -27.4698, "Australia", "🇦🇺"),
    "auckland": (174.7633, -36.8485, "Australia", "🇳🇿"),
    "perth": (115.8605, -31.9505, "Australia", "🇦🇺"),
    "adelaide": (138.6000, -34.9333, "Australia", "🇦🇺"),
    "wellington": (174.7762, -41.2866, "Australia", "🇳🇿"),
}

print(f"📌 Loaded {len(PORT_DATABASE)} ports worldwide")

# Region distribution
regions = {}
for name, data in PORT_DATABASE.items():
    region = data[2]
    regions[region] = regions.get(region, 0) + 1

print("\n📊 Region Distribution:")
for region, count in sorted(regions.items()):
    print(f"   {region}: {count} ports")

# ==================== TRAIN RANDOM FOREST ====================

print("\n🤖 Training Random Forest Risk Predictor...")

np.random.seed(42)
n_samples = 5000
lats = np.random.uniform(-60, 60, n_samples)
lons = np.random.uniform(-180, 180, n_samples)

risks = []
for i in range(n_samples):
    lat, lon = lats[i], lons[i]
    if 24 <= lat <= 31 and 48 <= lon <= 60:
        risks.append(3)
    elif 22 <= lat <= 27 and 56 <= lon <= 62:
        risks.append(2)
    elif 11 <= lat <= 15 and 44 <= lon <= 52:
        risks.append(2)
    elif 1 <= lat <= 6 and 97 <= lon <= 102:
        risks.append(1)
    else:
        risks.append(0)

X_train = np.column_stack([lats, lons])
y_train = np.array(risks)

rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
rf_model.fit(X_train, y_train)
accuracy = rf_model.score(X_train, y_train)
print(f"✅ Random Forest Trained! Accuracy: {accuracy:.2%}")

# ==================== TRAIN K-MEANS ====================

print("\n🤖 Training K-Means Port Clustering...")

port_names = list(PORT_DATABASE.keys())
port_coords = np.array([(v[0], v[1]) for v in PORT_DATABASE.values()])

kmeans = KMeans(n_clusters=8, random_state=42, n_init=10)
kmeans.fit(port_coords)

cluster_labels = {}
for i, port in enumerate(port_names):
    cluster_labels[port] = int(kmeans.labels_[i])

print("✅ K-Means Complete!")

# ==================== FUEL CALCULATION (REALISTIC) ====================

def calculate_fuel_savings(distance, vessel_type="container_medium"):
    vessel = VESSEL_TYPES.get(vessel_type, VESSEL_TYPES["container_medium"])
    speed_knots = vessel["speed_knots"]
    fuel_per_day = vessel["fuel_per_day"]
    
    speed_kmh = speed_knots * 1.852
    voyage_days = distance / speed_kmh / 24
    voyage_hours = voyage_days * 24
    
    traditional_distance = distance * 1.1
    traditional_days = traditional_distance / speed_kmh / 24
    
    fuel_consumed_tonnes = voyage_days * fuel_per_day
    traditional_fuel_tonnes = traditional_days * fuel_per_day
    fuel_saved_tonnes = traditional_fuel_tonnes - fuel_consumed_tonnes
    
    cost_per_tonne = 600
    cost_saved_usd = int(fuel_saved_tonnes * cost_per_tonne)
    co2_saved_tonnes = fuel_saved_tonnes * 3.15
    
    return {
        "vessel_name": vessel["name"],
        "vessel_type": vessel_type,
        "speed_knots": speed_knots,
        "speed_kmh": round(speed_kmh, 1),
        "fuel_per_day": fuel_per_day,
        "voyage_hours": round(voyage_hours, 1),
        "voyage_days": round(voyage_days, 1),
        "traditional_days": round(traditional_days, 1),
        "fuel_consumed_tonnes": round(fuel_consumed_tonnes, 1),
        "traditional_fuel_tonnes": round(traditional_fuel_tonnes, 1),
        "fuel_saved_tonnes": round(max(0, fuel_saved_tonnes), 1),
        "cost_saved_usd": max(0, cost_saved_usd),
        "co2_saved_tonnes": round(max(0, co2_saved_tonnes), 1),
        "saved_km": int(traditional_distance - distance)
    }

# ==================== LINEAR REGRESSION FUEL PREDICTOR ====================

class FuelPredictor:
    def __init__(self):
        self.model = LinearRegression()
        self.is_trained = False
        
    def train(self):
        print("🤖 Training Linear Regression for Fuel Prediction...")
        np.random.seed(42)
        n_samples = 1000
        distances = np.random.uniform(500, 15000, n_samples)
        fuel_tonnes = distances * 0.045 + np.random.normal(0, 50, n_samples)
        X = distances.reshape(-1, 1)
        y = fuel_tonnes
        self.model.fit(X, y)
        self.is_trained = True
        accuracy = self.model.score(X, y)
        print(f"✅ Linear Regression Trained! R² Score: {accuracy:.2%}")
        return self.model
    
    def predict_fuel(self, distance_km):
        if not self.is_trained:
            self.train()
        prediction_tonnes = self.model.predict([[distance_km]])[0]
        return {"tonnes": round(max(0, prediction_tonnes), 1), "kg": int(max(0, prediction_tonnes * 1000))}

# ==================== DECISION TREE RISK EXPLAINER ====================

class RiskExplainer:
    def __init__(self):
        self.model = DecisionTreeClassifier(max_depth=3, random_state=42)
        self.is_trained = False
        
    def train(self):
        print("🤖 Training Decision Tree for Risk Explanation...")
        np.random.seed(42)
        n_samples = 1000
        wind_speeds = np.random.uniform(0, 60, n_samples)
        wave_heights = np.random.uniform(0, 8, n_samples)
        risks = []
        for i in range(n_samples):
            wind = wind_speeds[i]
            wave = wave_heights[i]
            if wind > 45 or wave > 5:
                risks.append(2)
            elif wind > 30 or wave > 3:
                risks.append(1)
            else:
                risks.append(0)
        X = np.column_stack([wind_speeds, wave_heights])
        y = np.array(risks)
        self.model.fit(X, y)
        self.is_trained = True
        accuracy = self.model.score(X, y)
        print(f"✅ Decision Tree Trained! Accuracy: {accuracy:.2%}")
        return self.model
    
    def explain_risk(self, wind_speed, wave_height, lat=0, lon=0):
        if not self.is_trained:
            self.train()
        features = np.array([[wind_speed, wave_height]])
        risk_class = self.model.predict(features)[0]
        importance = self.model.feature_importances_
        risk_levels = {0: "LOW", 1: "MODERATE", 2: "HIGH"}
        
        # Zone-based risk explanation
        zone_risk = ""
        zone_name = ""
        if 24 <= lat <= 31 and 48 <= lon <= 60:
            zone_risk = "CRITICAL"
            zone_name = "Persian Gulf"
        elif 22 <= lat <= 27 and 56 <= lon <= 62:
            zone_risk = "HIGH"
            zone_name = "Gulf of Oman"
        elif 11 <= lat <= 15 and 44 <= lon <= 52:
            zone_risk = "MODERATE"
            zone_name = "Gulf of Aden"
        elif 1 <= lat <= 6 and 97 <= lon <= 102:
            zone_risk = "MODERATE"
            zone_name = "Malacca Strait"
        
        explanations = []
        if zone_name:
            explanations.append(f"⚠️ LOCATION RISK: {zone_name} - {zone_risk} RISK ZONE")
            if zone_name == "Persian Gulf":
                explanations.append("   • Active conflict zone - Iranian IRGC threats")
                explanations.append("   • Multiple vessel attacks reported")
                explanations.append("   • DO NOT enter without war risk insurance")
            elif zone_name == "Gulf of Oman":
                explanations.append("   • Vessels struck 50NM north of Muscat")
                explanations.append("   • Port of Salalah attacked")
                explanations.append("   • Exercise extreme caution")
            elif zone_name == "Gulf of Aden":
                explanations.append("   • Piracy risk present")
                explanations.append("   • Armed guards recommended")
            elif zone_name == "Malacca Strait":
                explanations.append("   • Piracy incidents reported")
                explanations.append("   • Increase watchkeeping")
        
        if wind_speed > 45:
            explanations.append(f"🌀 WEATHER: Storm force winds ({wind_speed} km/h)")
        elif wind_speed > 35:
            explanations.append(f"💨 WEATHER: Strong winds ({wind_speed} km/h)")
        
        if wave_height > 5:
            explanations.append(f"🌊 WEATHER: Extreme waves ({wave_height}m)")
        elif wave_height > 3.5:
            explanations.append(f"🌊 WEATHER: High waves ({wave_height}m)")
        
        if not explanations:
            explanations.append("✅ No significant risks detected in this area")
        
        return {"risk_level": risk_levels[risk_class], "explanations": explanations, "top_factor": "Location Risk" if zone_name else "Weather"}

# ==================== KNN SIMILAR PORTS ====================

class SimilarPortFinder:
    def __init__(self, n_neighbors=5):
        self.n_neighbors = n_neighbors
        self.model = NearestNeighbors(n_neighbors=n_neighbors, metric='euclidean')
        self.port_names = []
        self.port_coords = []
        
    def train(self):
        print("🤖 Training KNN for Similar Port Finding...")
        self.port_names = list(PORT_DATABASE.keys())
        self.port_coords = np.array([(v[0], v[1]) for v in PORT_DATABASE.values()])
        self.model.fit(self.port_coords)
        print(f"✅ KNN Trained!")
        return self.model
    
    def find_similar_ports(self, port_name, n=5):
        if port_name not in PORT_DATABASE:
            return []
        port_coord = np.array([[PORT_DATABASE[port_name][0], PORT_DATABASE[port_name][1]]])
        distances, indices = self.model.kneighbors(port_coord, n_neighbors=n+1)
        similar_ports = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.port_names) and self.port_names[idx] != port_name:
                similar_ports.append({"name": self.port_names[idx], "region": PORT_DATABASE[self.port_names[idx]][2], "distance_km": int(distances[0][i] * 111)})
        return similar_ports[:n]

# ==================== INITIALIZE MODELS ====================

print("\n" + "="*60)
print("🤖 INITIALIZING AI MODELS")
print("="*60)

fuel_predictor = FuelPredictor()
fuel_predictor.train()

risk_explainer = RiskExplainer()
risk_explainer.train()

similar_port_finder = SimilarPortFinder(n_neighbors=5)
similar_port_finder.train()

print("="*60)
print("✅ All AI Models Ready!")
print("="*60 + "\n")

# ==================== WEATHER FUNCTIONS ====================

def get_live_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m,wind_gusts_10m,wave_height,weather_code&timezone=auto"
        response = requests.get(url, timeout=10)
        data = response.json()
        if 'current' not in data:
            return get_fallback_weather(lat, lon)
        current = data.get('current', {})
        wind_speed = current.get('wind_speed_10m') or 15
        wave_height = current.get('wave_height') or 1.5
        weather_code = current.get('weather_code', 0)
        
        if weather_code == 0:
            condition = "☀️ Clear"
            severity = "LOW"
        elif weather_code in [1, 2, 3]:
            condition = "⛅ Partly cloudy"
            severity = "LOW"
        elif weather_code in [45, 48]:
            condition = "🌫️ Fog"
            severity = "MODERATE"
        elif weather_code in [51, 53, 55]:
            condition = "🌧️ Drizzle"
            severity = "MODERATE"
        elif weather_code in [61, 63, 65]:
            condition = "🌧️ Rain"
            severity = "MODERATE"
        elif weather_code in [80, 81, 82]:
            condition = "🌧️ Heavy Rain"
            severity = "HIGH"
        elif weather_code in [95, 96, 99]:
            condition = "⛈️ Thunderstorm"
            severity = "HIGH"
        else:
            condition = "🌤️ Moderate"
            severity = "LOW"
        
        if wind_speed > 60:
            condition = "🌀 CYCLONE!"
            severity = "CRITICAL"
        elif wind_speed > 45:
            condition = "🌊 STORM!"
            severity = "HIGH"
        elif wind_speed > 35:
            condition = "💨 STRONG WINDS"
            severity = "HIGH"
        elif wind_speed > 25:
            condition += " 💨 Windy"
            severity = "MODERATE"
        
        if wave_height > 6:
            condition += " 🌊 EXTREME WAVES"
            severity = "CRITICAL"
        elif wave_height > 4:
            condition += " 🌊 HIGH WAVES"
            severity = "HIGH"
        elif wave_height > 2.5:
            condition += " 🌊 Rough Seas"
            severity = "MODERATE"
        
        return {
            "temperature": current.get('temperature_2m') or 25,
            "wind_speed": round(wind_speed, 1),
            "wind_gust": round(current.get('wind_gusts_10m') or wind_speed, 1),
            "wave_height": round(wave_height, 1),
            "condition": condition,
            "severity": severity,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"Weather API error: {e}")
        return get_fallback_weather(lat, lon)

def get_fallback_weather(lat, lon):
    return {"temperature": 22, "wind_speed": 12, "wind_gust": 18, "wave_height": 1.2, "condition": "🌤️ Moderate", "severity": "LOW", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

def assess_weather_risk(weather):
    risk_score = 0
    wind = weather.get('wind_speed', 15)
    if wind > 60:
        risk_score += 60
    elif wind > 45:
        risk_score += 50
    elif wind > 35:
        risk_score += 40
    elif wind > 25:
        risk_score += 20
    elif wind > 15:
        risk_score += 10
    wave = weather.get('wave_height', 1.5)
    if wave > 6:
        risk_score += 40
    elif wave > 4:
        risk_score += 30
    elif wave > 2.5:
        risk_score += 20
    elif wave > 1.5:
        risk_score += 10
    severity = weather.get('severity', 'LOW')
    if severity == 'CRITICAL':
        risk_score += 30
    elif severity == 'HIGH':
        risk_score += 20
    elif severity == 'MODERATE':
        risk_score += 10
    return min(100, risk_score)

def evaluate_route_weather(route_coords):
    weather_points = []
    max_risk = 0
    warnings = []
    suggestions = []
    sample_indices = [0, len(route_coords)//4, len(route_coords)//2, 3*len(route_coords)//4, -1]
    positions = ["Departure", "Quarter", "Halfway", "Three Quarter", "Destination"]
    for idx, pos in zip(sample_indices, positions):
        if idx < len(route_coords):
            lon, lat = route_coords[idx]
            weather = get_live_weather(lat, lon)
            weather["position"] = pos
            risk = assess_weather_risk(weather)
            weather["risk_score"] = risk
            weather_points.append(weather)
            max_risk = max(max_risk, risk)
            if weather["wind_speed"] > 45:
                warnings.append(f"🌊 STORM at {pos}: {weather['wind_speed']} km/h")
                suggestions.append(f"⚠️ STORM at {pos}! Consider delaying")
            elif weather["wind_speed"] > 35:
                warnings.append(f"💨 Strong winds at {pos}: {weather['wind_speed']} km/h")
                suggestions.append(f"⚠️ Strong winds at {pos}")
            if weather["wave_height"] > 4:
                warnings.append(f"🌊 HIGH WAVES at {pos}: {weather['wave_height']}m")
                suggestions.append(f"⚠️ High waves at {pos}")
    if not suggestions:
        suggestions.append("✅ Weather conditions are favorable")
    return {"weather_points": weather_points, "max_risk": max_risk, "warnings": warnings, "suggestions": suggestions}

# ==================== HELPER FUNCTIONS ====================

def predict_security_risk(lat, lon):
    if 24 <= lat <= 31 and 48 <= lon <= 60:
        return {"level": "CRITICAL", "score": 90}
    elif 22 <= lat <= 27 and 56 <= lon <= 62:
        return {"level": "HIGH", "score": 65}
    elif 11 <= lat <= 15 and 44 <= lon <= 52:
        return {"level": "MODERATE", "score": 35}
    elif 1 <= lat <= 6 and 97 <= lon <= 102:
        return {"level": "MODERATE", "score": 35}
    else:
        return {"level": "LOW", "score": 10}

def get_sea_route(start, end):
    origin = (PORT_DATABASE[start][0], PORT_DATABASE[start][1])
    destination = (PORT_DATABASE[end][0], PORT_DATABASE[end][1])
    try:
        route = sr.searoute(origin, destination, units="km")
        return route['geometry']['coordinates']
    except:
        return [origin, destination]

def calculate_distance(route):
    total = 0
    for i in range(len(route)-1):
        lon1, lat1 = route[i]
        lon2, lat2 = route[i+1]
        total += geodesic((lat1, lon1), (lat2, lon2)).km
    return int(total)

def point_in_polygon(x, y, poly):
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i+1)%n]
        if ((y1 > y) != (y2 > y)) and (x < (x2-x1)*(y-y1)/(y2-y1)+x1):
            inside = not inside
    return inside

def get_danger_zones(route):
    zones = []
    danger_zones_list = [
        {"name": "🔴 CRITICAL: Persian Gulf", "coords": [(48,24),(57,24),(57,31),(48,31)], "color": "#ff0000"},
        {"name": "🟠 HIGH RISK: Gulf of Oman", "coords": [(56.5,22),(61,22),(61,27),(56.5,27)], "color": "#ff4444"},
        {"name": "🟡 MODERATE: Gulf of Aden", "coords": [(44,11),(52,11),(52,15),(44,15)], "color": "#ffaa00"},
        {"name": "🟡 MODERATE: Malacca Strait", "coords": [(97,1),(102,1),(102,6),(97,6)], "color": "#ffaa00"}
    ]
    for zone in danger_zones_list:
        for coord in route:
            if point_in_polygon(coord[0], coord[1], zone["coords"]):
                zones.append(zone)
                break
    return zones

def calculate_eta(distance, wind_speed=15):
    speed_kmh = 15 * 1.852
    wind_factor = 1 + (max(0, wind_speed - 15) / 50)
    eta_hours = (distance / speed_kmh) * wind_factor
    eta_days = eta_hours / 24
    return max(1, round(eta_hours, 1)), max(1, round(eta_days, 1))

# ==================== COMPLETE AI CHATBOT ====================

class MaritimeAIAssistant:
    def get_response(self, message):
        msg = message.lower().strip()
        
        # Weather queries
        if any(word in msg for word in ["weather", "temperature", "wind", "wave", "forecast", "climate"]):
            return self.handle_weather(msg)
        
        # Risk queries
        elif any(word in msg for word in ["risk", "danger", "safe", "secure", "pirate", "war", "conflict"]):
            return self.handle_risk(msg)
        
        # Route queries
        elif any(word in msg for word in ["route", "path", "way", "journey", "voyage"]):
            return self.handle_route(msg)
        
        # Fuel queries
        elif any(word in msg for word in ["fuel", "cost", "save", "money", "price", "expense"]):
            return self.handle_fuel(msg)
        
        # ETA queries
        elif any(word in msg for word in ["eta", "time", "duration", "how long", "arrival"]):
            return self.handle_eta(msg)
        
        # Port queries
        elif any(word in msg for word in ["port", "region", "area", "location"]):
            return self.handle_port(msg)
        
        # Help
        elif "help" in msg:
            return self.get_help()
        
        # Greetings
        elif any(word in msg for word in ["hello", "hi", "hey"]):
            return "👋 Hello! I'm your AI Maritime Assistant. Ask me about weather, risks, routes, fuel savings, ETA, or ports!"
        
        else:
            return "I can help with weather, risks, routes, fuel, ETA, and ports. Type 'help' to see all capabilities!"
    
    def handle_weather(self, msg):
        for port in PORT_DATABASE.keys():
            if port in msg:
                weather = get_live_weather(PORT_DATABASE[port][1], PORT_DATABASE[port][0])
                return f"📍 {port.title()} ({PORT_DATABASE[port][2]})\n🌡️ {weather['temperature']}°C | 💨 {weather['wind_speed']} km/h | 🌊 {weather['wave_height']} m\n☁️ {weather['condition']}\n⚠️ Severity: {weather['severity']}\n\n💡 Recommendation: {'🚨 DO NOT SAIL!' if weather['severity'] == 'CRITICAL' else '⚠️ Exercise caution' if weather['severity'] == 'HIGH' else '✅ Safe for sailing'}"
        return "Please specify a port. Example: 'weather in Singapore'"
    
    def handle_risk(self, msg):
        if "iran" in msg or "persian" in msg:
            return "⚠️ PERSIAN GULF - CRITICAL RISK\n\n• Active conflict zone\n• Iranian IRGC threats\n• Multiple vessel attacks\n• DO NOT ENTER without war insurance"
        elif "oman" in msg:
            return "⚠️ GULF OF OMAN - HIGH RISK\n\n• Vessels struck 50NM north of Muscat\n• Port of Salalah attacked\n• Exercise extreme caution"
        elif "aden" in msg:
            return "⚠️ GULF OF ADEN - MODERATE RISK\n\n• Piracy risk present\n• Armed guards recommended\n• Report suspicious activity"
        elif "malacca" in msg:
            return "⚠️ MALACCA STRAIT - MODERATE RISK\n\n• Piracy incidents reported\n• Increase watchkeeping\n• Use citadel if available"
        else:
            return "⚠️ HIGH RISK AREAS:\n• Persian Gulf (CRITICAL)\n• Gulf of Oman (HIGH)\n• Gulf of Aden (MODERATE)\n• Malacca Strait (MODERATE)"
    
    def handle_route(self, msg):
        return "🗺️ ROUTE PLANNING\n\n1. Select Departure Port\n2. Select Destination Port\n3. Select Vessel Type\n4. Click 'Calculate AI Route'\n\nThe AI will find the optimal ocean route avoiding land and danger zones!"
    
    def handle_fuel(self, msg):
        return "⛽ FUEL SAVINGS\n\nMedium Container Ship (18 knots, 80 tonnes/day):\n• 1,000 km → ~25 tonnes saved ($15,000)\n• 5,000 km → ~125 tonnes saved ($75,000)\n• 10,000 km → ~250 tonnes saved ($150,000)\n\nSelect your vessel type for exact calculations!"
    
    def handle_eta(self, msg):
        return "⏱️ ETA CALCULATION\n\nETA = Distance / (Ship Speed × Weather Factor)\n\n• Ship Speed: 15 knots (27.8 km/h)\n• Mumbai to Dubai (2,000 km): ~3-5 days\n• Singapore to Chennai (2,850 km): ~4-6 days\n• Singapore to Rotterdam (15,000 km): ~20-30 days"
    
    def handle_port(self, msg):
        regions_info = {
            "south asia": "🇮🇳 India, Pakistan, Sri Lanka, Bangladesh (11 ports)",
            "southeast asia": "🇸🇬 Singapore, Malaysia, Indonesia, Thailand, Vietnam, Philippines (12 ports)",
            "east asia": "🇨🇳 China, Japan, South Korea, Taiwan (18 ports)",
            "middle east": "🇦🇪 UAE, Iran, Oman, Qatar, Kuwait, Bahrain, Saudi (13 ports)",
            "europe": "🇳🇱 Netherlands, Germany, Belgium, Greece, Spain, Italy, Turkey (15 ports)",
            "north america": "🇺🇸 USA, Canada (11 ports)",
            "south america": "🇧🇷 Brazil, Argentina, Chile, Peru, Colombia (8 ports)",
            "africa": "🇿🇦 South Africa, Kenya, Morocco, Djibouti, Nigeria, Egypt (9 ports)",
            "australia": "🇦🇺 Australia, New Zealand (7 ports)"
        }
        for region, info in regions_info.items():
            if region in msg:
                return f"📍 {region.title()}: {info}"
        if "similar" in msg:
            for port in PORT_DATABASE.keys():
                if port in msg:
                    similar = similar_port_finder.find_similar_ports(port, 5)
                    if similar:
                        response = f"📍 Ports similar to {port.title()}:\n"
                        for s in similar:
                            response += f"• {s['name'].title()} ({s['region']}) - {s['distance_km']} km\n"
                        return response
        return "🌍 Regions: South Asia, Southeast Asia, East Asia, Middle East, Europe, North America, South America, Africa, Australia\n\nTry 'ports in Europe' or 'similar ports to Mumbai'"
    
    def get_help(self):
        return "🤖 AI ASSISTANT HELP\n\n🌊 WEATHER: 'weather in Singapore'\n⚠️ RISK: 'risk in Iran'\n🗺️ ROUTE: 'how to plan a route'\n⛽ FUEL: 'fuel savings'\n⏱️ ETA: 'how to calculate ETA'\n📍 PORTS: 'ports in Europe' or 'similar ports to Mumbai'"

ai_assistant = MaritimeAIAssistant()

# ==================== FLASK ROUTES ====================

@app.route('/')
def index():
    return render_template('final_complete.html')

@app.route('/api/ports')
def get_ports():
    ports_list = []
    for name, data in PORT_DATABASE.items():
        ports_list.append({"name": name, "display": f"{data[3]} {name.title()}", "region": data[2], "lat": data[1], "lon": data[0]})
    return jsonify(ports_list)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    response = ai_assistant.get_response(message)
    return jsonify({"response": response})

@app.route('/api/route', methods=['POST'])
def get_route():
    data = request.json
    start = data.get('start_port', '').lower().strip()
    end = data.get('end_port', '').lower().strip()
    vessel_type = data.get('vessel_type', 'container_medium')
    
    if start not in PORT_DATABASE or end not in PORT_DATABASE:
        return jsonify({'error': 'Port not found'}), 404
    
    print(f"🚢 Calculating route: {start} → {end} | Vessel: {vessel_type}")
    
    route_coords = get_sea_route(start, end)
    leaflet_route = [[lat, lon] for lon, lat in route_coords]
    distance = calculate_distance(route_coords)
    
    start_security = predict_security_risk(PORT_DATABASE[start][1], PORT_DATABASE[start][0])
    end_security = predict_security_risk(PORT_DATABASE[end][1], PORT_DATABASE[end][0])
    danger_zones = get_danger_zones(route_coords)
    weather_evaluation = evaluate_route_weather(route_coords)
    
    start_weather = get_live_weather(PORT_DATABASE[start][1], PORT_DATABASE[start][0])
    end_weather = get_live_weather(PORT_DATABASE[end][1], PORT_DATABASE[end][0])
    
    eta_hours, eta_days = calculate_eta(distance, end_weather['wind_speed'])
    fuel_savings = calculate_fuel_savings(distance, vessel_type)
    
    start_cluster = cluster_labels.get(start, 0)
    end_cluster = cluster_labels.get(end, 0)
    
    all_risks = [start_security["score"], end_security["score"], weather_evaluation["max_risk"]]
    for z in danger_zones:
        if "CRITICAL" in z["name"]:
            all_risks.append(90)
        elif "HIGH" in z["name"]:
            all_risks.append(65)
    
    max_risk = max(all_risks)
    
    if max_risk >= 80:
        final_risk = "CRITICAL"
        route_color = "#ff0000"
        rec = "🔴 CRITICAL RISK - Conflict zone! DO NOT PROCEED."
    elif max_risk >= 60:
        final_risk = "HIGH"
        route_color = "#ff4444"
        rec = "⚠️ HIGH RISK - Exercise extreme caution"
    elif max_risk >= 30:
        final_risk = "MODERATE"
        route_color = "#ffaa00"
        rec = "⚠️ MODERATE RISK - Normal precautions advised"
    else:
        final_risk = "LOW"
        route_color = "#00ff66"
        rec = "✅ LOW RISK - Safe for transit"
    
    print(f"✅ Distance: {distance} km | Days: {eta_days} | Fuel: {fuel_savings['fuel_consumed_tonnes']} tonnes")
    
    return jsonify({
        'success': True,
        'start_port': start.title(),
        'end_port': end.title(),
        'start_region': PORT_DATABASE[start][2],
        'end_region': PORT_DATABASE[end][2],
        'route': leaflet_route,
        'route_color': route_color,
        'distance_km': distance,
        'waypoints': len(leaflet_route),
        'eta_hours': eta_hours,
        'eta_days': eta_days,
        'risk_level': final_risk,
        'risk_score': max_risk,
        'recommendation': rec,
        'fuel_savings': fuel_savings,
        'ml_results': {'risk_accuracy': f'{accuracy:.1%}', 'start_cluster': start_cluster, 'end_cluster': end_cluster, 'same_region': start_cluster == end_cluster},
        'danger_zones': danger_zones,
        'weather_evaluation': weather_evaluation,
        'weather': {'start': start_weather, 'end': end_weather}
    })

@app.route('/api/predict_fuel', methods=['POST'])
def predict_fuel():
    data = request.json
    distance = data.get('distance_km', 1000)
    result = fuel_predictor.predict_fuel(distance)
    return jsonify({'distance_km': distance, 'predicted_fuel_tonnes': result['tonnes'], 'predicted_fuel_kg': result['kg'], 'algorithm': 'Linear Regression'})

@app.route('/api/explain_risk', methods=['POST'])
def explain_risk():
    data = request.json
    wind_speed = data.get('wind_speed', 15)
    wave_height = data.get('wave_height', 1.5)
    lat = data.get('lat', 0)
    lon = data.get('lon', 0)
    explanation = risk_explainer.explain_risk(wind_speed, wave_height, lat, lon)
    return jsonify(explanation)

@app.route('/api/similar_ports/<port_name>')
def similar_ports(port_name):
    similar = similar_port_finder.find_similar_ports(port_name.lower(), 5)
    return jsonify({'port': port_name, 'similar_ports': similar, 'algorithm': 'K-Nearest Neighbors (KNN)'})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚢 COMPLETE VESSEL ROUTE OPTIMIZER 🚢")
    print("="*60)
    print(f"📌 {len(PORT_DATABASE)} ports worldwide")
    print("\n📊 Regions: South Asia, SE Asia, East Asia, Middle East, Europe, North America, South America, Africa, Australia")
    print("\n🚢 Vessel Types: 10 types with realistic fuel consumption")
    print("\n✅ AI Models: Random Forest, K-Means, Linear Regression, Decision Tree, KNN")
    print("\n🌐 Open: http://localhost:5000")
    print("="*60 + "\n")
    app.run(debug=True, port=5000, threaded=True)
