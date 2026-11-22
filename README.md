# 🚢 AI-Powered Vessel Route Optimizer

### Intelligent Maritime Routing, Fuel Prediction & Voyage Risk Analysis

An AI-powered maritime route optimization application that helps users explore vessel routes, estimate fuel consumption, analyze voyage risks, and understand weather conditions through an interactive dashboard.

## 🌊 Project Overview

Maritime transportation plays an important role in global trade. Choosing an efficient shipping route requires considering distance, vessel speed, fuel consumption, weather conditions, and maritime risk zones.

**ShipRouteOptimizer** combines route calculation, machine learning, weather information, and interactive mapping to provide a unified maritime decision-support platform.

## ✨ Key Features

- **AI-Based Route Optimization:** Calculate maritime routes between selected ports.
- **Interactive Route Map:** Visualize shipping routes using Leaflet.
- **Multiple Vessel Selection:** Select vessel types with different speeds and fuel consumption rates.
- **Fuel Prediction:** Estimate fuel requirements using machine learning models.
- **ETA Estimation:** Calculate estimated voyage arrival time.
- **Similar Port Discovery:** Identify nearby alternative ports.
- **Weather Monitoring:** View weather conditions at departure and destination ports.
- **Weather Risk Alerts:** Highlight potentially dangerous weather conditions.
- **Maritime Risk Analysis:** Identify critical and moderate maritime risk zones.
- **AI Assistant:** Ask questions about route risks, weather, ETA, and fuel savings.
- **Voyage Summary:** View important voyage information in one dashboard.
- **Ship Animation:** Visualize vessel movement along the selected route.
- **Report Generation:** Download voyage reports.

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript |
| Mapping | Leaflet |
| Machine Learning | Scikit-learn, XGBoost |
| Routing | SeaRoute |
| Data Processing | NumPy |
| Geolocation | Geopy |
| API Integration | REST APIs, Requests |

## 🤖 Machine Learning Components

The project includes trained model artifacts for:

- Random Forest
- XGBoost
- ETA prediction
- K-Means clustering
- Feature scaling

These models support the application's prediction and analysis workflows.

## 📂 Project Structure

```text
ShipRouteOptimizer/
│
├── models/
│   ├── random_forest.pkl
│   ├── scaler.pkl
│   ├── xgboost.json
│   ├── xgboost_eta.json
│   ├── cluster_labels.pkl
│   └── kmeans.pkl
│
├── templates/
│   └── final_complete.html
│
├── final_complete_router.py
├── requirements.txt
├── README.md
├── .gitignore
└── LICENSE
```

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Navigate to the project directory

```bash
cd ShipRouteOptimizer
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the environment

Windows:

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
python final_complete_router.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

## 🎯 Project Objective

The objective is to demonstrate how Python, machine learning, maritime routing, and real-time information can be combined into a practical decision-support application for maritime transportation.

## 👩‍💻 Developer

**Keerthika P**

B.Tech – Artificial Intelligence and Data Science

Interests: Python Development | Full Stack Development | Machine Learning | Data Science

---

⭐ If you find this project interesting, consider giving this repository a star!