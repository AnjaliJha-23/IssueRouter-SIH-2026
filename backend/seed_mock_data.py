"""
seed_mock_data.py — Seeds SQLite database with 127 realistic Jharkhand Societal Innovation Clusters (SIH 2026).
Covers all 24 districts, 12 canonical domains, research-grade problem definitions,
complete University project lifecycle, industry CSR proposals, and photo evidence.
"""
import sys
import uuid
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add backend dir to python path
sys.path.insert(0, str(Path(__file__).parent))

from db.database import engine, SessionLocal, Base
from db.models import (
    Organization,
    User,
    Challenge,
    ChallengeEvidence,
    ChallengeAnalysis,
    ChallengeRelation,
    Match,
    RoutingBatch,
    RoutingInvitation,
    Project,
    Proposal,
)

random.seed(42)

# ─────────────────────────────────────────────────────────────────────────────
# 1. CANONICAL JHARKHAND DISTRICTS & GEOGRAPHICAL COORDINATES
# ─────────────────────────────────────────────────────────────────────────────
DISTRICT_COORDS = {
    "Ranchi": (23.3441, 85.3096),
    "Dhanbad": (23.7957, 86.4304),
    "East Singhbhum": (22.8046, 86.2029),
    "Bokaro": (23.6693, 86.1511),
    "Hazaribagh": (23.9930, 85.3582),
    "Deoghar": (24.4842, 86.6961),
    "Giridih": (24.1860, 86.3050),
    "Palamu": (24.0450, 84.0700),
    "Ramgarh": (23.6300, 85.5100),
    "Godda": (24.8300, 87.2100),
    "Sahibganj": (25.2500, 87.6500),
    "Pakur": (24.6300, 87.8500),
    "Jamtara": (23.9600, 86.8000),
    "Dumka": (24.2687, 87.2490),
    "Garhwa": (24.1800, 83.8100),
    "Latehar": (23.7400, 84.5000),
    "Lohardaga": (23.4400, 84.6800),
    "Gumla": (23.0400, 84.5400),
    "Simdega": (22.6100, 84.5100),
    "West Singhbhum": (22.5500, 85.8100),
    "Saraikela-Kharsawan": (22.7000, 85.9300),
    "Khunti": (23.0700, 85.2800),
    "Chatra": (24.2100, 84.8700),
    "Koderma": (24.4700, 85.5900),
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. 127 REALISTIC JHARKHAND SOCIETAL CHALLENGE SPECIFICATIONS
# ─────────────────────────────────────────────────────────────────────────────
CHALLENGE_SPECS = [
    # --- TOP 6 IMAGE-ENABLED CLUSTERS ---
    {
        "id": "CHL-2026-0001",
        "title": "Acid Mine Drainage Contamination in Damodar Tributaries",
        "district": "Dhanbad", "block": "Jharia",
        "domain": "Water Management", "dept": "Drinking Water & Sanitation Dept",
        "prio": 96, "status": "in_project", "social": 1280, "citizen": 640,
        "media_urls": ["/uploads/evidence/jh_mine_water_acid.jpg"],
        "desc": "Acidic coal mine runoff with high sulphate and heavy metal concentrations (pH 3.2-4.1) is discharging directly into Damodar river sub-catchment streams near Jharia, rendering community handpumps reddish-orange and unusable for over 18,000 residents across 14 mining-fringe bastis.",
        "ai_summary": "High-acidity mine drainage detected in Damodar feeder streams; pH levels severely degraded with heavy iron precipitate affecting community drinking sources.",
        "uni_id": "org-univ-2", # IIT ISM Dhanbad
        "ind_id": "org-ind-2", # BCCL CSR
        "project_title": "Autonomous Mine Acid Drainage Neutralization & Heavy Metal Adsorption Unit",
        "budget": 1450000, "budget_req": "₹14,50,000", "trl": "TRL-6 (Field Pilot Ready)",
        "funding_status": "Funded", "collab_status": "Partnered", "funds": 1450000,
        "partners": ["Coal India / BCCL CSR", "Tata Steel CSR"],
        "lead": "Prof. A. K. Verma (Environmental Mining Engineering)",
        "email": "verma.ak@iitism.ac.in",
        "impact": "Restores safe drinking water access for 18,000 villagers across Jharia mining belt."
    },
    {
        "id": "CHL-2026-0002",
        "title": "Human-Elephant Corridor Conflict & Seasonal Crop Depredation",
        "district": "Latehar", "block": "Chandwa",
        "domain": "Environment", "dept": "Department of Forest, Environment & Climate Change",
        "prio": 94, "status": "in_project", "social": 940, "citizen": 410,
        "media_urls": ["/uploads/evidence/jh_elephant_conflict.jpg"],
        "desc": "A herd of 22 wild Asian elephants migrating along the disrupted Betla-Chandwa ecological corridor is frequently straying into agricultural paddy fields, destroying standing crops and damaging village boundary homesteads across 9 forest-edge villages.",
        "ai_summary": "Recurring elephant herd straying causing intense crop damage along Betla corridor fringe; urgent requirement for early geofenced detection and acoustic deterrents.",
        "uni_id": "org-univ-5", # Central University of Jharkhand
        "ind_id": "org-ind-1", # Tata Steel CSR
        "project_title": "Early Warning LoRa Acoustic & Infrasound Elephant Herd Migration Tracking System",
        "budget": 1120000, "budget_req": "₹11,20,000", "trl": "TRL-6 (Field Pilot Ready)",
        "funding_status": "Funded", "collab_status": "Partnered", "funds": 1120000,
        "partners": ["Tata Steel CSR", "Jharkhand Forest Ecology Alliance"],
        "lead": "Dr. Anita Hansda (Wildlife & Environmental Sciences)",
        "email": "anita.hansda@cuj.ac.in",
        "impact": "Eliminates crop depredation and human casualties across 9 forest-edge villages in Latehar."
    },
    {
        "id": "CHL-2026-0003",
        "title": "Open-Cast Coal Pit Land Degradation & Slope Subsidence Hazard",
        "district": "Bokaro", "block": "Bermo",
        "domain": "Environment", "dept": "Department of Mines & Geology",
        "prio": 92, "status": "in_project", "social": 810, "citizen": 380,
        "media_urls": ["/uploads/evidence/jh_opencast_mine_pit.jpg"],
        "desc": "Unstabilized overburden dumps and massive abandoned open-cast mine voids along the Bermo coal seam are experiencing deep tension cracks and slope subsidence following heavy rains, threatening nearby settlement roads and primary school buildings.",
        "ai_summary": "Slope instability and subsidence tension cracks recorded at abandoned open-cast coal pit ridge; geotechnical stabilization and real-time displacement monitoring required.",
        "uni_id": "org-univ-2", # IIT ISM Dhanbad
        "ind_id": "org-ind-4", # SAIL Bokaro Steel CSR
        "project_title": "IoT Tiltmeter & InSAR Slope Displacement Early Warning System for Abandoned Mining Voids",
        "budget": 1600000, "budget_req": "₹16,00,000", "trl": "TRL-6 (Field Pilot Ready)",
        "funding_status": "Partially Funded", "collab_status": "In Discussions", "funds": 950000,
        "partners": ["SAIL Bokaro Steel CSR"],
        "lead": "Dr. R. K. Bhattacharya (Geotechnical & Rock Mechanics Lab)",
        "email": "bhattacharya.rk@iitism.ac.in",
        "impact": "Protects 6,500 residents living along the Bermo-Phusro mining subsidence perimeter."
    },
    {
        "id": "CHL-2026-0004",
        "title": "Forest Fire Early Detection in Parasnath Hills Wildlife Sanctuary",
        "district": "Giridih", "block": "Pirtand",
        "domain": "Environment", "dept": "Department of Forest, Environment & Climate Change",
        "prio": 89, "status": "in_project", "social": 720, "citizen": 310,
        "media_urls": ["/uploads/evidence/jh_forest_fire_early.jpg"],
        "desc": "Dry deciduous Sal forest tracts across the Parasnath and Madhuban hills face recurrent canopy wildfires during dry summer months, endangering rare botanical biodiversity, tribal minor forest produce gatherers, and sacred pilgrim trekking routes.",
        "ai_summary": "Recurrent canopy wildfire outbreaks detected along dry Sal tracts in Parasnath range; thermal sensing and mesh communication towers required for prompt containment.",
        "uni_id": "org-univ-5", # Central University of Jharkhand
        "ind_id": "org-ind-5", # Jindal Steel & Power CSR
        "project_title": "Autonomous Solar LoRa Thermal Canopy Mesh for Wildfire Early Detection",
        "budget": 980000, "budget_req": "₹9,80,000", "trl": "TRL-6 (Field Pilot Ready)",
        "funding_status": "Partially Funded", "collab_status": "In Discussions", "funds": 500000,
        "partners": ["Jindal Steel & Power CSR"],
        "lead": "Prof. Manoj Kumar (Centre for Environmental Sciences)",
        "email": "manoj.kumar@cuj.ac.in",
        "impact": "Reduces wildfire response dispatch time from 6 hours to under 25 minutes across Parasnath Sanctuary."
    },
    {
        "id": "CHL-2026-0005",
        "title": "Fluoride & Heavy Metal Contamination in Community Deep Borewells",
        "district": "Garhwa", "block": "Meral",
        "domain": "Water Management", "dept": "Drinking Water & Sanitation Dept",
        "prio": 91, "status": "in_project", "social": 860, "citizen": 450,
        "media_urls": ["/uploads/evidence/jh_rural_water_pump.jpg"],
        "desc": "Groundwater samples from 26 community handpumps across Meral and Bhavnathpur blocks reveal fluoride concentrations exceeding 3.8 mg/L (safe limit: 1.0 mg/L), triggering widespread dental and skeletal fluorosis among children and elderly tribal residents.",
        "ai_summary": "Hazardous fluoride levels up to 3.8 mg/L confirmed in community groundwater borewells; urgent deployment of decentralized activated alumina adsorption filters required.",
        "uni_id": "org-univ-6", # Kolhan University
        "ind_id": "org-ind-3", # CCL CSR
        "project_title": "Zero-Electricity Gravity Nano-Alumina Defluoridation Community Water Filter Units",
        "budget": 850000, "budget_req": "₹8,50,000", "trl": "TRL-7 (Production Ready)",
        "funding_status": "Funded", "collab_status": "Partnered", "funds": 850000,
        "partners": ["Central Coalfields Ltd (CCL) CSR"],
        "lead": "Dr. Sunita Murmu (Applied Chemistry & Water Technology)",
        "email": "sunita.murmu@kolhanuniversity.ac.in",
        "impact": "Supplies safe defluoridated potable water to 8,200 residents across 12 high-fluorosis habitations."
    },
    {
        "id": "CHL-2026-0006",
        "title": "Severe Bacterial Wilt & Soil Degradation in Tribal Vegetable Farmlands",
        "district": "Khunti", "block": "Torpa",
        "domain": "AgriTech", "dept": "Department of Agriculture",
        "prio": 88, "status": "in_project", "social": 690, "citizen": 340,
        "media_urls": ["/uploads/evidence/jh_crop_soil_damage.jpg"],
        "desc": "Bacterial wilt disease caused by Ralstonia solanacearum combined with severe soil acidification (pH < 4.8) has decimated 60% of standing off-season tomato, brinjal, and chili yields across 180 smallholder tribal farming plots in Torpa block.",
        "ai_summary": "Extensive bacterial wilt and severe soil acidity impacting tribal horticultural clusters; bio-control soil amendment and resistant graft protocols required.",
        "uni_id": "org-univ-4", # Birsa Agricultural University
        "ind_id": "org-ind-6", # Jharkhand Agritech Foundation
        "project_title": "Bio-fungicidal Soil Amendment & Graft Management against Bacterial Wilt in Tomato",
        "budget": 780000, "budget_req": "₹7,80,000", "trl": "TRL-6 (Field Pilot Ready)",
        "funding_status": "Funded", "collab_status": "Partnered", "funds": 780000,
        "partners": ["Jharkhand Agritech & Rural Innovation Foundation"],
        "lead": "Dr. Rajeshwar Singh (Department of Plant Pathology)",
        "email": "singh.pathology@bauranchi.ac.in",
        "impact": "Restores crop yields for 650 tribal vegetable growers and increases household farm income by 45%."
    },

    # --- HEALTHCARE & BIOTECH CLUSTERS ---
    {
        "id": "CHL-2026-0007",
        "title": "Solar Telemedicine Diagnostic Kiosks for Remote Tribal Primary Health Centres",
        "district": "Simdega", "block": "Thethaitangar",
        "domain": "HealthTech", "dept": "Department of Health, Medical Education & Family Welfare",
        "prio": 95, "status": "in_project", "social": 740, "citizen": 360,
        "desc": "Remote forest habitations in Thethaitangar have zero access to medical specialists. Patients face an 80km journey over rough terrain for basic diagnostics and maternal consultations.",
        "ai_summary": "Deficit of specialist medical access in remote tribal areas; needs off-grid solar-powered telemedicine kiosk with real-time biometric transmission.",
        "uni_id": "org-univ-1", # RIMS Ranchi
        "ind_id": "org-ind-1", # Tata Steel CSR
        "project_title": "IoT-Enabled Solar Telemedicine Kiosk with Offline Diagnostic Sync for Rural PHCs",
        "budget": 850000, "budget_req": "₹8,50,000", "trl": "TRL-6 (Field Pilot Ready)",
        "funding_status": "Funded", "collab_status": "Partnered", "funds": 850000,
        "partners": ["Tata Steel CSR"],
        "lead": "Dr. S. K. Sharma (Biomedical Engineering & Telemedicine)",
        "email": "sharma.biomed@rims.ac.in",
        "impact": "Connects 42,000 villagers to RIMS specialist doctors without 80km transit."
    },
    {
        "id": "CHL-2026-0008",
        "title": "Rapid Point-of-Care Sickle Cell & Thalassaemia Field Screening Kit",
        "district": "West Singhbhum", "block": "Chaibasa",
        "domain": "BioTech", "dept": "Department of Health, Medical Education & Family Welfare",
        "prio": 93, "status": "in_project", "social": 910, "citizen": 480,
        "desc": "High carrier prevalence of Sickle Cell Anemia (>18%) among Ho and Munda tribal populations remains undetected until severe crisis events due to the absence of rapid on-ground diagnostic tools.",
        "ai_summary": "Widespread undetected sickle-cell hemoglobinopathies in tribal belt; requires low-cost microfluidic paper strip test for ASHA workers.",
        "uni_id": "org-univ-1", # RIMS Ranchi
        "ind_id": "org-ind-1", # Tata Steel CSR
        "project_title": "Microfluidic Lateral-Flow Point-of-Care Screening Strip for Sickle-Cell Trait",
        "budget": 920000, "budget_req": "₹9,20,000", "trl": "TRL-6 (Field Pilot Ready)",
        "funding_status": "Funded", "collab_status": "Partnered", "funds": 920000,
        "partners": ["Tata Steel CSR", "Tribal Health Mission"],
        "lead": "Dr. P. K. Hembrom (Haematology & Molecular Diagnostics)",
        "email": "hembrom.haem@rims.ac.in",
        "impact": "Screens 25,000 tribal adolescents and reduces crisis-level hospitalizations by 55%."
    },
    {
        "id": "CHL-2026-0009",
        "title": "Smart Ambulance Traffic Preemption System & Green Corridor Signaling",
        "district": "Dhanbad", "block": "Bank More",
        "domain": "HealthTech", "dept": "Urban Development & Housing Department",
        "prio": 90, "status": "in_project", "social": 830, "citizen": 390,
        "desc": "Heavy coal transit traffic and narrow urban choke points between Bank More, Saraidhela, and SNMMCH Hospital delay critical care ambulances by up to 45 minutes during peak hours.",
        "ai_summary": "Severe emergency ambulance delays on arterial hospital access routes; automated V2X traffic preemption and dynamic green corridor signaling required.",
        "uni_id": "org-univ-2", # IIT ISM Dhanbad
        "ind_id": "org-ind-2", # BCCL CSR
        "project_title": "V2X Mesh & LoRa Dynamic Green Corridor Traffic Preemption for Emergency Ambulances",
        "budget": 1400000, "budget_req": "₹14,00,000", "trl": "TRL-7 (Production Ready)",
        "funding_status": "Funded", "collab_status": "Partnered", "funds": 1400000,
        "partners": ["Coal India / BCCL CSR"],
        "lead": "Prof. A. K. Verma (AI & Robotics Lab)",
        "email": "verma.ak@iitism.ac.in",
        "impact": "Reduces critical patient transit duration by 42% on SNMMCH emergency access route."
    },
    {
        "id": "CHL-2026-0010",
        "title": "Childhood Acute Malnutrition Early Detection AI Anthropometric Scanner",
        "district": "Sahibganj", "block": "Borio",
        "domain": "Public Health", "dept": "Women, Child Development & Social Security Department",
        "prio": 92, "status": "resolved", "social": 980, "citizen": 490,
        "desc": "Severe acute malnutrition (SAM) among Paharia tribal infants in hilly hamlets often goes undetected until irreversible stunting or life-threatening infections occur.",
        "ai_summary": "High incidence of undetected SAM in isolated hill habitations; mobile smartphone-based computer vision anthropometric scanner deployed for Anganwadi workers.",
        "uni_id": "org-univ-1", # RIMS Ranchi
        "ind_id": "org-ind-3", # CCL CSR
        "project_title": "Mobile Computer-Vision Nutritional Anthropometry & SAM Triage for Anganwadis",
        "budget": 650000, "budget_req": "₹6,50,000", "trl": "TRL-7 (Production Ready)",
        "funding_status": "Funded", "collab_status": "Partnered", "funds": 650000,
        "partners": ["Central Coalfields Ltd (CCL) CSR"],
        "lead": "Dr. Meenakshi Kumari (Pediatrics & Community Health)",
        "email": "meenakshi.peds@rims.ac.in",
        "impact": "Screened 4,800 children across 32 anganwadis; recovered 340 SAM cases with zero child mortality."
    },
    {
        "id": "CHL-2026-0011",
        "title": "Field Lateral-Flow Snakebite Venom Typing & Rapid Anti-Venom Protocol",
        "district": "Deoghar", "block": "Madhupur",
        "domain": "HealthTech", "dept": "Department of Health, Medical Education & Family Welfare",
        "prio": 91, "status": "in_project", "social": 620, "citizen": 290,
        "desc": "Fatalities from snakebite envenomation remain high in agricultural regions due to inability to identify snake species (Viperidae vs Elapidae), leading to delays in administering targeted polyvalent antivenom.",
        "ai_summary": "Diagnostic uncertainty in rural snakebite cases; developing a field-level lateral flow venom detection test for primary health staff.",
        "uni_id": "org-univ-8", # AIIMS Deoghar
        "ind_id": "org-ind-5", # Jindal Steel CSR
        "project_title": "Field Lateral-Flow Immunochromatographic Venom Typing Kit for Rural PHCs",
        "budget": 1100000, "budget_req": "₹11,00,000", "trl": "TRL-6 (Field Pilot Ready)",
        "funding_status": "Partially Funded", "collab_status": "In Discussions", "funds": 600000,
        "partners": ["Jindal Steel & Power CSR"],
        "lead": "Dr. Arvind Prasad (Department of Emergency Medicine)",
        "email": "arvind.em@aiimsdeoghar.edu.in",
        "impact": "Reduces rural snakebite mortality by 65% across Deoghar and Santhal Pargana districts."
    },
    {
        "id": "CHL-2026-0012",
        "title": "Occupational Silicosis Early Radiography AI Screening for Stone-Crusher Workers",
        "district": "Koderma", "block": "Domchanch",
        "domain": "Public Health", "dept": "Department of Health, Medical Education & Family Welfare",
        "prio": 94, "status": "in_project", "social": 780, "citizen": 350,
        "desc": "Over 4,500 unorganized laborers in stone-crushing and mica-scraping units suffer progressive pulmonary silicosis, which is frequently misdiagnosed as tuberculosis in rural health centers.",
        "ai_summary": "Severe occupational silicosis misdiagnosed in stone-crushing belt; deep-learning chest X-ray screening tool deployed on mobile diagnostic vans.",
        "uni_id": "org-univ-8", # AIIMS Deoghar
        "ind_id": "org-ind-1", # Tata Steel CSR
        "project_title": "Deep Learning Chest Radiograph Screening for Occupational Silicosis & Asbestosis",
        "budget": 1250000, "budget_req": "₹12,50,000", "trl": "TRL-6 (Field Pilot Ready)",
        "funding_status": "Funded", "collab_status": "Partnered", "funds": 1250000,
        "partners": ["Tata Steel CSR", "Jharkhand Workers Welfare Board"],
        "lead": "Dr. Vikas Kumar (Pulmonary & Occupational Medicine)",
        "email": "vikas.pulmo@aiimsdeoghar.edu.in",
        "impact": "Identified 620 early-stage silicosis cases in Domchanch, enabling timely disability compensation and therapeutic rehabilitation."
    },

    # --- WATER MANAGEMENT & ENVIRONMENT ---
    {
        "id": "CHL-2026-0013",
        "title": "Heavy Haul Road Structural Health Monitoring & Pothole Predictive Telemetry",
        "district": "East Singhbhum", "block": "Mango",
        "domain": "Urban Infrastructure", "dept": "Road Construction Department",
        "prio": 86, "status": "in_project", "social": 750, "citizen": 380,
        "desc": "Industrial heavy vehicles transporting steel coils and ore cause rapid pavement structural fatigue, deep craters, and fatal accidents on NH-33 connecting Mango and Jamshedpur industrial clusters.",
        "ai_summary": "Rapid road degradation on industrial corridors; vehicle-mounted sensor telemetry and asphalt vibration sensors deployed for predictive maintenance.",
        "uni_id": "org-univ-3", # NIT Jamshedpur
        "ind_id": "org-ind-1", # Tata Steel CSR
        "project_title": "AI Computer Vision & Accelerometer Telemetry for Road Structural Fatigue Prediction",
        "budget": 1350000, "budget_req": "₹13,50,000", "trl": "TRL-6 (Field Pilot Ready)",
        "funding_status": "Funded", "collab_status": "Partnered", "funds": 1350000,
        "partners": ["Tata Steel CSR"],
        "lead": "Prof. S. N. Singh (Civil Engineering & Transportation)",
        "email": "snsingh.civil@nitjsr.ac.in",
        "impact": "Identifies sub-surface asphalt cracking 6 weeks before pothole formation, reducing maintenance costs by 38%."
    },
    {
        "id": "CHL-2026-0014",
        "title": "Subarnarekha River Industrial Effluent Monitoring Sensor Network",
        "district": "Saraikela-Kharsawan", "block": "Adityapur",
        "domain": "Water Management", "dept": "Department of Forest, Environment & Climate Change",
        "prio": 93, "status": "in_project", "social": 890, "citizen": 420,
        "desc": "Unmonitored night discharge of untreated industrial effluents with toxic heavy metals into the Subarnarekha River causes massive fish mortality and contamination of downstream municipal water intakes.",
        "ai_summary": "Intermittent nocturnal industrial discharge in Subarnarekha river; deploying real-time optical and electrochemical multiparameter water quality buoys.",
        "uni_id": "org-univ-3", # NIT Jamshedpur
        "ind_id": "org-ind-1", # Tata Steel CSR
        "project_title": "Autonomous Solar LoRa Buoy Mesh for Real-Time Industrial Effluent Detection",
        "budget": 1550000, "budget_req": "₹15,50,000", "trl": "TRL-6 (Field Pilot Ready)",
        "funding_status": "Funded", "collab_status": "Partnered", "funds": 1550000,
        "partners": ["Tata Steel CSR", "Jharkhand State Pollution Control Board"],
        "lead": "Dr. Prabal Patra (Electronics & Sensor Instrumentation)",
        "email": "ppatra.ece@nitjsr.ac.in",
        "impact": "Continuously audits 18 river outfalls, eliminating unmonitored night toxic discharge."
    },

    # --- AGRICULTURE & RURAL LIVELIHOODS ---
    {
        "id": "CHL-2026-0015",
        "title": "Solar MPPT Micro Cold-Storage Optimization for Tribal Horticultural Clusters",
        "district": "Hazaribagh", "block": "Ichak",
        "domain": "AgriTech", "dept": "Department of Agriculture",
        "prio": 87, "status": "in_project", "social": 670, "citizen": 310,
        "desc": "Smallholder farmers cultivating green peas, tomatoes, and capsicum in Ichak suffer 40% post-harvest spoilage due to lack of local cold storage and frequent grid outages.",
        "ai_summary": "Extensive post-harvest horticultural loss; off-grid solar-powered thermal energy storage micro-cooler developed for farmer producer organizations.",
        "uni_id": "org-univ-3", # NIT Jamshedpur
        "ind_id": "org-ind-5", # Jindal Steel CSR
        "project_title": "Decentralized Phase-Change Solar Cold Room for Rural Vegetable Value Chains",
        "budget": 950000, "budget_req": "₹9,50,000", "trl": "TRL-6 (Field Pilot Ready)",
        "funding_status": "Partially Funded", "collab_status": "In Discussions", "funds": 550000,
        "partners": ["Jindal Steel & Power CSR"],
        "lead": "Dr. R. V. Sharma (Mechanical & Renewable Energy Systems)",
        "email": "rvsharma.me@nitjsr.ac.in",
        "impact": "Reduces horticultural spoilage from 40% to under 6% for 280 farming families in Ichak."
    },
    {
        "id": "CHL-2026-0016",
        "title": "Decentralized Climate-Resilient Ragi Millet Micro-Drip Irrigation",
        "district": "Lohardaga", "block": "Senha",
        "domain": "AgriTech", "dept": "Department of Agriculture",
        "prio": 85, "status": "in_project", "social": 580, "citizen": 270,
        "desc": "Unpredictable monsoon dry spells cause severe crop failure in upland finger millet (Madua/Ragi) fields, which provide nutritional sustenance for marginalized tribal households.",
        "ai_summary": "Drought vulnerability in upland millet crops; low-cost gravity micro-drip kits combined with drought-hardy BAU-Ragi seed lines deployed.",
        "uni_id": "org-univ-4", # Birsa Agricultural University
        "ind_id": "org-ind-6", # Agritech Foundation
        "project_title": "Gravity Micro-Drip Irrigation Kits & Stress-Tolerant Finger Millet Cultivation",
        "budget": 720000, "budget_req": "₹7,20,000", "trl": "TRL-7 (Production Ready)",
        "funding_status": "Funded", "collab_status": "Partnered", "funds": 720000,
        "partners": ["Jharkhand Agritech & Rural Innovation Foundation"],
        "lead": "Dr. B. K. Agarwal (Department of Agronomy)",
        "email": "agarwal.agronomy@bauranchi.ac.in",
        "impact": "Increases finger millet yield by 68% across 450 rainfed tribal holdings in Senha."
    },
    {
        "id": "CHL-2026-0017",
        "title": "Decentralized Lac Processing & Temperature-Regulated Purification Kiln",
        "district": "Khunti", "block": "Murhu",
        "domain": "Rural Livelihoods", "dept": "Department of Rural Development",
        "prio": 86, "status": "resolved", "social": 740, "citizen": 350,
        "desc": "Tribal lac farmers sell raw sticklac to middlemen at depressed prices because primitive processing causes charring and loss of export-grade shellac color quality.",
        "ai_summary": "Low tribal income realization from raw sticklac; developed precision temperature-controlled clean processing kiln for lac cooperatives.",
        "uni_id": "org-univ-4", # Birsa Agricultural University
        "ind_id": "org-ind-1", # Tata Steel CSR
        "project_title": "Biomass Gasifier-Assisted Precision Temperature Shellac Processing Kiln",
        "budget": 810000, "budget_req": "₹8,10,000", "trl": "TRL-7 (Production Ready)",
        "funding_status": "Funded", "collab_status": "Partnered", "funds": 810000,
        "partners": ["Tata Steel CSR", "Jharkhand State Livelihood Promotion Society"],
        "lead": "Dr. Ramesh Soren (Entomology & Forest Livelihoods)",
        "email": "soren.lac@bauranchi.ac.in",
        "impact": "Boosted raw sticklac value addition by 140% for 520 tribal women collectors in Murhu."
    },
    {
        "id": "CHL-2026-0018",
        "title": "Tussar Silk Yarn Provenance Blockchain & Digital Handloom Grading System",
        "district": "Saraikela-Kharsawan", "block": "Kharsawan",
        "domain": "Rural Livelihoods", "dept": "Department of Rural Development",
        "prio": 84, "status": "in_project", "social": 510, "citizen": 240,
        "desc": "Traditional tribal Tussar silk weavers are undercut by synthetic powerloom fabrics falsely marketed as authentic Kharsawan wild silk, destroying generational weaver livelihoods.",
        "ai_summary": "Loss of authentic Tussar market value due to synthetic counterfeits; smart optical yarn density analyzer and blockchain origin QR tags deployed.",
        "uni_id": "org-univ-6", # Kolhan University
        "ind_id": "org-ind-1", # Tata Steel CSR
        "project_title": "Digital Optical Yarn Grading & QR Blockchain Provenance for Tussar Silk Weavers",
        "budget": 680000, "budget_req": "₹6,80,000", "trl": "TRL-6 (Field Pilot Ready)",
        "funding_status": "Funded", "collab_status": "Partnered", "funds": 680000,
        "partners": ["Tata Steel CSR"],
        "lead": "Dr. Pradip Mahato (Textile Economics & Tribal Informatics)",
        "email": "pmahato@kolhanuniversity.ac.in",
        "impact": "Authenticates 1,400 artisanal silk sarees monthly, raising weaver take-home wages by 62%."
    },
    {
        "id": "CHL-2026-0019",
        "title": "Ecological Reclamation of Degraded Iron Ore Slopes in Saranda Forest",
        "district": "West Singhbhum", "block": "Noamundi",
        "domain": "Environment", "dept": "Department of Mines & Geology",
        "prio": 93, "status": "in_project", "social": 820, "citizen": 370,
        "desc": "Extensive iron-ore mining in Saranda core boundary has led to steep barren red tailings dumps that erode during monsoons, choking perennial forest streams with heavy iron silt.",
        "ai_summary": "Severe erosion of mining overburden into Saranda waterways; microbial bio-geo-textile seed blankets deployed for rapid slope stabilization.",
        "uni_id": "org-univ-6", # Kolhan University
        "ind_id": "org-ind-1", # Tata Steel CSR
        "project_title": "Native Mycorrhizal Bio-Blankets for Accelerated Revegetation of Iron Ore Dumps",
        "budget": 1200000, "budget_req": "₹12,00,000", "trl": "TRL-6 (Field Pilot Ready)",
        "funding_status": "Funded", "collab_status": "Partnered", "funds": 1200000,
        "partners": ["Tata Steel CSR"],
        "lead": "Prof. S. K. Champia (Botany & Environmental Sciences)",
        "email": "champia.botany@kolhanuniversity.ac.in",
        "impact": "Stabilized 42 hectares of steep mining slopes, reducing silt runoff into Karo River by 76%."
    },
    {
        "id": "CHL-2026-0020",
        "title": "Solar Convective Tunnel Dryer for Mahua Flower & Forest Produce",
        "district": "Simdega", "block": "Kolebira",
        "domain": "Rural Livelihoods", "dept": "Department of Rural Development",
        "prio": 83, "status": "resolved", "social": 630, "citizen": 290,
        "desc": "Primitive open-ground sun drying of collected Mahua flowers results in dust contamination, fungal mold spoilage (45% loss), and drastically lower procurement rates for tribal gatherers.",
        "ai_summary": "High post-harvest spoilage of tribal non-timber forest produce; deployed hygienic solar convective tunnel dryers across tribal cooperative societies.",
        "uni_id": "org-univ-4", # Birsa Agricultural University
        "ind_id": "org-ind-3", # CCL CSR
        "project_title": "Community Solar Convective Poly-Tunnel Dryers for Food-Grade Mahua Processing",
        "budget": 640000, "budget_req": "₹6,40,000", "trl": "TRL-7 (Production Ready)",
        "funding_status": "Funded", "collab_status": "Partnered", "funds": 640000,
        "partners": ["Central Coalfields Ltd (CCL) CSR"],
        "lead": "Dr. Hemant Kispotta (Post-Harvest Agricultural Engineering)",
        "email": "kispotta.engg@bauranchi.ac.in",
        "impact": "Eliminated fungal mold in 85 tons of Mahua, doubling market realization for 410 tribal families."
    },

    # --- EDTECH & ACCESSIBILITY ---
    {
        "id": "CHL-2026-0021",
        "title": "Offline Tribal Vernacular STEM Learning Kiosk for Off-Grid Schools",
        "district": "Dumka", "block": "Shikaripara",
        "domain": "EdTech", "dept": "School Education & Literacy Department",
        "prio": 82, "status": "in_project", "social": 540, "citizen": 260,
        "desc": "Primary schools in hilly Santhal villages have no electricity or internet connectivity. Students struggle with standard state textbooks published exclusively in Hindi without Santhali translations.",
        "ai_summary": "Severe educational barrier due to lack of connectivity and language mismatch; solar micro-server delivering interactive Santhali/Ho audio-visual STEM content.",
        "uni_id": "org-univ-5", # Central University of Jharkhand
        "ind_id": "org-ind-2", # BCCL CSR
        "project_title": "Solar Mesh Offline Vernacular STEM Learning Server for Scheduled Tribal Schools",
        "budget": 750000, "budget_req": "₹7,50,000", "trl": "TRL-6 (Field Pilot Ready)",
        "funding_status": "Funded", "collab_status": "Partnered", "funds": 750000,
        "partners": ["Coal India / BCCL CSR"],
        "lead": "Dr. Subhashree Sen (Centre for Tribal Languages & Pedagogy)",
        "email": "subhashree.sen@cuj.ac.in",
        "impact": "Improves foundational literacy and numeracy for 1,800 Santhal students across 14 off-grid schools."
    },
    {
        "id": "CHL-2026-0022",
        "title": "Wheelchair Accessibility Infrastructure Audit & Modular Ramp Deployment",
        "district": "Ranchi", "block": "Bundu",
        "domain": "Accessibility", "dept": "Department of Rural Development",
        "prio": 81, "status": "resolved", "social": 490, "citizen": 210,
        "desc": "The Block Development Administrative Complex, Primary Health Center, and Panchayat Bhawan in Bundu lack ramps, making public grievance submission impossible for disabled citizens.",
        "ai_summary": "Total lack of physical accessibility in rural government office complexes; modular rapid-install recycled composite ramps deployed with tactile braille navigation.",
        "uni_id": "org-univ-3", # NIT Jamshedpur
        "ind_id": "org-ind-4", # SAIL Bokaro CSR
        "project_title": "Modular Recycled-Polymer Accessible Ramp & Tactile Braille Civic Complex Kit",
        "budget": 520000, "budget_req": "₹5,20,000", "trl": "TRL-7 (Production Ready)",
        "funding_status": "Funded", "collab_status": "Partnered", "funds": 520000,
        "partners": ["SAIL Bokaro Steel CSR", "Jharkhand Divyangjan Commission"],
        "lead": "Prof. T. K. Roy (Architecture & Structural Accessibility)",
        "email": "tkroy.arch@nitjsr.ac.in",
        "impact": "Made 12 major public offices completely accessible to 380 disabled residents in Bundu block."
    },

    # --- URBAN INFRASTRUCTURE & SANITATION ---
    {
        "id": "CHL-2026-0023",
        "title": "Urban Underpass Flash Inundation & Automated Storm Drain Telemetry",
        "district": "Ranchi", "block": "Main Road",
        "domain": "Urban Infrastructure", "dept": "Urban Development & Housing Department",
        "prio": 89, "status": "resolved", "social": 1150, "citizen": 590,
        "desc": "Flash monsoon rains inundate Main Road and Doranda railway underpasses under 4 feet of stagnant water within 30 minutes, paralyzing traffic and stranding emergency vehicles.",
        "ai_summary": "Critical urban underpass flash waterlogging; ultrasonic water level sensors and automated high-capacity stormwater dewatering pumps installed.",
        "uni_id": "org-univ-2", # IIT ISM Dhanbad
        "ind_id": "org-ind-3", # CCL CSR
        "project_title": "Smart City IoT Ultrasonic Drain Level Telemetry & Automated Sump Dewatering",
        "budget": 1150000, "budget_req": "₹11,50,000", "trl": "TRL-7 (Production Ready)",
        "funding_status": "Funded", "collab_status": "Partnered", "funds": 1150000,
        "partners": ["Central Coalfields Ltd (CCL) CSR", "Ranchi Municipal Corporation"],
        "lead": "Dr. Pradeep Kumar (Civil & Environmental Fluid Dynamics)",
        "email": "pradeep.fluid@iitism.ac.in",
        "impact": "Zero waterlogging closures during 2025 monsoon across Ranchi Main Road corridor."
    },
    {
        "id": "CHL-2026-0024",
        "title": "Decentralized Municipal Organic Waste Bio-Composting Facility",
        "district": "Hazaribagh", "block": "Hazaribagh Town",
        "domain": "Sanitation", "dept": "Urban Development & Housing Department",
        "prio": 84, "status": "resolved", "social": 670, "citizen": 310,
        "desc": "Over 25 tons of unsegregated organic vegetable and food waste generated daily at the main market dumps into open storm drains, creating foul odors and breeding vectors for dengue and cholera.",
        "ai_summary": "Unmanaged municipal market waste choking drainage; rapid aerobic in-vessel bio-composter installed converting municipal waste into organic soil fertilizer.",
        "uni_id": "org-univ-7", # Vinoba Bhave University
        "ind_id": "org-ind-5", # Jindal Steel CSR
        "project_title": "Accelerated In-Vessel Microbial Composting for Municipal Market Waste",
        "budget": 780000, "budget_req": "₹7,80,000", "trl": "TRL-7 (Production Ready)",
        "funding_status": "Funded", "collab_status": "Partnered", "funds": 780000,
        "partners": ["Jindal Steel & Power CSR"],
        "lead": "Dr. Madhulika Gupta (Biotechnology & Waste Remediation)",
        "email": "mgupta.biotech@vbu.ac.in",
        "impact": "Diverts 18 tons of organic waste daily, generating 4.2 tons of organic fertilizer for local farmers."
    },
]

# Additional templates to populate 127 total clusters across remaining districts and domains
TEMPLATES_CATALOG = [
    # Water Management
    ("Mine Pit Water Treatment for Agriculture", "Stagnant mine water in abandoned quarry has acidic pH but high volume. Needs neutralization filtration for field irrigation.", "Water Management", "Drinking Water & Sanitation Dept", (75, 94), (120, 550)),
    ("Arsenic Leaching in Alluvial Wells", "Elevated arsenic (>0.05 mg/L) detected in deep community handpumps along river basin.", "Water Management", "Drinking Water & Sanitation Dept", (86, 96), (200, 720)),
    ("Solar Pump Predictive Telemetry Failure", "Solar drinking water pumps frequently fail due to dust on PV panels and dry run motor burnout.", "Water Management", "Drinking Water & Sanitation Dept", (68, 88), (80, 320)),
    ("Defunct Ahar-Pyne Indigenous Irrigation Channels", "Traditional stone-and-earthen water diversion canals silted up, causing agricultural drought in kharif season.", "Water Management", "Department of Agriculture", (70, 89), (90, 390)),
    ("Industrial Fluoride Effluent Contamination", "Unlined tailing runoff leaching inorganic fluorides into adjacent community drinking wells.", "Water Management", "Department of Mines & Geology", (84, 95), (140, 610)),
    ("Microbial Contamination in Municipal Piped Supply", "Damaged municipal water main intermixed with open sewage trench, causing high coliform counts in tap water.", "Water Management", "Urban Development & Housing Department", (80, 93), (160, 580)),

    # AgriTech & BioTech
    ("Tomato Yellow Leaf Curl Virus Outbreak", "Whitefly-transmitted virus causing severe leaf curling and 50% harvest drop in commercial tomato belt.", "AgriTech", "Department of Agriculture", (74, 91), (110, 480)),
    ("Soil Acidification & Trace Mineral Deficiency", "Continuous coal dust deposition and chemical fertilizer overuse has dropped topsoil pH to 4.5.", "AgriTech", "Department of Agriculture", (68, 86), (90, 350)),
    ("Paddy Blast Fungal Infection in Upland Rice", "Neck and leaf blast fungus spreading rapidly during high humidity spells in rainfed paddy fields.", "AgriTech", "Department of Agriculture", (72, 89), (130, 440)),
    ("Post-Harvest Storage Insect Infestation in Pulses", "Bruchid beetles destroying stored arhar and gram harvest within 4 weeks of harvest in village godowns.", "AgriTech", "Department of Agriculture", (65, 84), (75, 310)),
    ("Cattle Foot and Mouth Disease Outbreak", "Contagious aphthovirus spreading among indigenous cows in village cattle fairs without rapid quarantine.", "BioTech", "Department of Agriculture", (82, 94), (140, 510)),
    ("Lack of Cold Chain for Hybrid Vegetable Seeds", "High temperatures in local agro-service centers degrading germination rates of certified hybrid vegetable seeds.", "AgriTech", "Department of Agriculture", (60, 80), (60, 240)),

    # Environment & Forestry
    ("Illegal Sand Mining & Riverbank Scour", "Unregulated mechanized sand excavation eroding riverbank foundation near bridges and rural road culverts.", "Environment", "Department of Mines & Geology", (83, 94), (180, 620)),
    ("Open Burning of Coal Slurry & Biomass", "Illegal domestic processing of raw coal fines producing choking sulphur and hydrocarbon smoke clouds.", "Environment", "Department of Forest, Environment & Climate Change", (78, 92), (150, 530)),
    ("Wetland Encroachment & Bird Habitat Loss", "Rapid construction dumping silt and debris into migratory waterfowl wetlands during breeding season.", "Environment", "Department of Forest, Environment & Climate Change", (70, 87), (80, 310)),
    ("Industrial Particulate Fugitive Dust Emissions", "Sponge iron and cement units operating without electrostatic precipitator bags at night.", "Environment", "Department of Forest, Environment & Climate Change", (84, 95), (210, 780)),
    ("Unregulated Stone Quarry Noise & Vibration", "Heavy blasting inside stone quarries causing plaster cracks in village brick houses within 300m.", "Environment", "Department of Mines & Geology", (74, 89), (120, 430)),
    ("Forest Fringe Timber Smuggling & Tree Loss", "Felling of old-growth Sal and Teak trees along state forest borders without automated forest perimeter alarms.", "Environment", "Department of Forest, Environment & Climate Change", (76, 90), (95, 360)),

    # HealthTech & Public Health
    ("Primary Health Centre Staff Absenteeism", "PHC remains unattended for 4 days a week with no doctor or basic diagnostic tests available.", "HealthTech", "Department of Health, Medical Education & Family Welfare", (80, 94), (140, 590)),
    ("Vaccine Refrigerator Solar Cold-Chain Failure", "Erratic power supply at sub-centre spoiling pentavalent and hepatitis vaccines during hot weather.", "HealthTech", "Department of Health, Medical Education & Family Welfare", (85, 96), (170, 680)),
    ("High Neonatal Sepsis in Rural Deliveries", "Home childbirths in remote hamlets resulting in umbilical infections and neonatal jaundice due to lack of clean kits.", "Public Health", "Department of Health, Medical Education & Family Welfare", (88, 98), (190, 750)),
    ("Unmonitored Industrial Bio-Medical Waste", "Clinical bio-waste, used syringes, and anatomical waste found dumped on open grounds near community river.", "Public Health", "Department of Health, Medical Education & Family Welfare", (84, 95), (130, 480)),
    ("Tuberculosis Treatment Adherence Drop", "Tribal TB patients stopping DOTS antibiotics halfway due to travel cost to district dispensary.", "Public Health", "Department of Health, Medical Education & Family Welfare", (78, 92), (110, 410)),
    ("Arterial Traffic Delays for Emergency Ambulances", "Single-lane highway bottlenecks delaying emergency patient transit to district civil hospital by over an hour.", "HealthTech", "Urban Development & Housing Department", (82, 94), (160, 620)),

    # EdTech & Accessibility
    ("Dilapidated School Ceiling & Roof Leakage", "Water seeping through classroom slab during monsoon, creating electrical shock hazards and classroom closures.", "EdTech", "School Education & Literacy Department", (70, 88), (90, 370)),
    ("Inaccessible Sanitary Blocks for Disabled Girls", "Rural high school toilets have stepped thresholds and narrow doors preventing access for disabled students.", "Accessibility", "School Education & Literacy Department", (74, 91), (110, 420)),
    ("Science Laboratory Practical Equipment Deficit", "Higher secondary model school lacks microscopes, glassware, and reagent kits for state board chemistry syllabus.", "EdTech", "School Education & Literacy Department", (62, 82), (65, 270)),
    ("Lack of Tactile Paving & Audio Signals at Bus Terminal", "Visually impaired citizens face severe danger navigating chaotic bus bays and interstate ticketing counters.", "Accessibility", "Urban Development & Housing Department", (76, 89), (85, 340)),
    ("Dropout Risk in Non-Vernacular High Schools", "Tribal students face learning disengagement due to lack of bilingual Santhali-Hindi curriculum resources.", "EdTech", "School Education & Literacy Department", (68, 85), (80, 310)),
    ("Lack of Ramps in Panchayat Administrative Halls", "Disabled citizens unable to attend monthly Gram Sabha welfare eligibility hearings due to flight of stairs.", "Accessibility", "Department of Rural Development", (72, 88), (95, 380)),

    # Urban Infrastructure, Sanitation & Public Admin
    ("Chronic Road Craters on Industrial Link Corridor", "Overloaded mineral trucks causing deep tire-rutting and structural asphalt failure on main market artery.", "Urban Infrastructure", "Road Construction Department", (75, 91), (150, 580)),
    ("Overflowing Commercial Market Garbage Dumpster", "Vegetable and poultry market waste overflowing for 6 days, blocking traffic lane and causing health hazard.", "Sanitation", "Urban Development & Housing Department", (72, 88), (120, 460)),
    ("Low-Voltage Power Surges Damaging Agricultural Pumps", "Voltage dropping to 140V during peak irrigation hours, burning submersible pump windings in 30 farms.", "Urban Infrastructure", "Jharkhand Urja Vikas Nigam", (76, 92), (130, 490)),
    ("Delayed Resolution of Rural Water Grievances", "Citizens waiting 45 days for replacement of broken borewell cylinder seals due to manual paper routing.", "Public Administration", "Drinking Water & Sanitation Dept", (65, 84), (70, 280)),
    ("Open Drains Clogging & Peri-Urban Stagnation", "Uncovered municipal drain filled with single-use plastic bottles, overflowing into residential basements during rains.", "Sanitation", "Urban Development & Housing Department", (74, 90), (140, 520)),
    ("Non-Functional Streetlights on Rural Connecting Road", "Over 70% of solar streetlights defective along 5km forest stretch, leading to evening snatching risks.", "Urban Infrastructure", "Department of Rural Development", (66, 85), (85, 340)),
]

# District allocations to hit 127 total clusters distributed across all 24 districts:
DISTRICT_DISTRIBUTION = [
    ("Ranchi", 16),
    ("Dhanbad", 12),
    ("East Singhbhum", 11),
    ("Bokaro", 9),
    ("Hazaribagh", 7),
    ("Deoghar", 6),
    ("Giridih", 6),
    ("Palamu", 6),
    ("Ramgarh", 5),
    ("West Singhbhum", 5),
    ("Saraikela-Kharsawan", 5),
    ("Latehar", 5),
    ("Gumla", 4),
    ("Khunti", 4),
    ("Garhwa", 4),
    ("Sahibganj", 3),
    ("Godda", 3),
    ("Pakur", 3),
    ("Dumka", 3),
    ("Jamtara", 2),
    ("Lohardaga", 2),
    ("Simdega", 2),
    ("Chatra", 2),
    ("Koderma", 2),
]

def seed():
    print("[seed_mock_data] Creating tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("[seed_mock_data] Performing clean transaction-level wipe...")
        db.query(Proposal).delete()
        db.query(Project).delete()
        db.query(RoutingInvitation).delete()
        db.query(RoutingBatch).delete()
        db.query(Match).delete()
        db.query(ChallengeEvidence).delete()
        db.query(ChallengeAnalysis).delete()
        db.query(ChallengeRelation).delete()
        db.query(Challenge).delete()
        db.query(User).delete()
        db.query(Organization).delete()
        db.commit()

        # ── 1. SEED ORGANIZATIONS ──────────────────────────────────────────
        print("[seed_mock_data] Seeding institutional organizations...")
        orgs = [
            # Government
            Organization(id="org-gov-1", name="Jharkhand Health & Innovation Department", type="Gov", location="Ranchi", district="Ranchi", research_domains="HealthTech, Public Health, BioTech", status="ACTIVE"),
            Organization(id="org-gov-2", name="Jharkhand Drinking Water & Sanitation Department", type="Gov", location="Ranchi", district="Ranchi", research_domains="Water Management, Sanitation", status="ACTIVE"),
            Organization(id="org-gov-3", name="Jharkhand Department of Mines & Geology", type="Gov", location="Ranchi", district="Ranchi", research_domains="Environment, Mining", status="ACTIVE"),
            Organization(id="org-gov-4", name="Jharkhand Department of Agriculture", type="Gov", location="Ranchi", district="Ranchi", research_domains="AgriTech, BioTech, Rural Livelihoods", status="ACTIVE"),

            # Anchor Universities (Pre-seeded so IDs match mock challenges; seed_universities will add CSV entries)
            Organization(id="org-univ-1", name="RIMS Ranchi", type="University", location="Ranchi", district="Ranchi", research_domains="HealthTech, Public Health, BioTech", research_specializations="Clinical Medicine, Telemedicine, Epidemiology", research_output="High: 850+ clinical papers, state apex referral medical college", status="ACTIVE"),
            Organization(id="org-univ-2", name="IIT ISM Dhanbad", type="University", location="Dhanbad", district="Dhanbad", research_domains="Environment, Water Management, Urban Infrastructure", research_specializations="Mining Engineering, Geotechnical Stability, Sensor Networks", research_output="Apex: 3,500+ Scopus papers, national institute of importance", status="ACTIVE"),
            Organization(id="org-univ-3", name="NIT Jamshedpur", type="University", location="Jamshedpur", district="East Singhbhum", research_domains="Urban Infrastructure, Water Management, Accessibility", research_specializations="Civil Engineering, IoT Telemetry, Transportation Systems", research_output="High: 1,800+ papers, leading robotics & civil R&D", status="ACTIVE"),
            Organization(id="org-univ-4", name="Birsa Agricultural University", type="University", location="Ranchi", district="Ranchi", research_domains="AgriTech, BioTech, Rural Livelihoods", research_specializations="Crop Genetics, Dryland Farming, Bio-Pesticides, Lac Cultivation", research_output="High: 1,000+ research papers, ICAR center of excellence", status="ACTIVE"),
            Organization(id="org-univ-5", name="Central University of Jharkhand", type="University", location="Ranchi", district="Ranchi", research_domains="Environment, Water Management, EdTech", research_specializations="Environmental Sciences, Tribal Pedagogy, Renewable Energy", research_output="High: 1,200+ indexed publications, DST/SERB funding", status="ACTIVE"),
            Organization(id="org-univ-6", name="Kolhan University", type="University", location="Chaibasa", district="West Singhbhum", research_domains="Environment, Rural Livelihoods, Water Management", research_specializations="Mining Geology, Tribal Handicrafts, Water Defluoridation", research_output="Moderate: Regional tribal studies and geoscientific documentation", status="ACTIVE"),
            Organization(id="org-univ-7", name="Vinoba Bhave University", type="University", location="Hazaribagh", district="Hazaribagh", research_domains="Environment, Sanitation, Rural Livelihoods", research_specializations="Microbial Composting, Soil Sciences, Rural Economics", research_output="Moderate: 300+ indexed papers, waste management models", status="ACTIVE"),
            Organization(id="org-univ-8", name="AIIMS Deoghar", type="University", location="Deoghar", district="Deoghar", research_domains="HealthTech, Public Health, BioTech", research_specializations="Emergency Medicine, Occupational Silicosis, Toxicology", research_output="Apex: Institute of National Importance, clinical epidemiology", status="ACTIVE"),

            # Industry CSR Partners
            Organization(id="org-ind-1", name="Tata Steel CSR", type="Industry", location="Jamshedpur", district="East Singhbhum", research_domains="Urban Infrastructure, Water Management, HealthTech, Rural Livelihoods", status="ACTIVE"),
            Organization(id="org-ind-2", name="Coal India / BCCL CSR", type="Industry", location="Dhanbad", district="Dhanbad", research_domains="Environment, Water Management, HealthTech, EdTech", status="ACTIVE"),
            Organization(id="org-ind-3", name="Central Coalfields Ltd (CCL) CSR", type="Industry", location="Ranchi", district="Ranchi", research_domains="Water Management, Public Health, Sanitation, Environment", status="ACTIVE"),
            Organization(id="org-ind-4", name="SAIL Bokaro Steel CSR", type="Industry", location="Bokaro", district="Bokaro", research_domains="Urban Infrastructure, Accessibility, HealthTech", status="ACTIVE"),
            Organization(id="org-ind-5", name="Jindal Steel & Power CSR", type="Industry", location="Ramgarh", district="Ramgarh", research_domains="Rural Livelihoods, AgriTech, Environment", status="ACTIVE"),
            Organization(id="org-ind-6", name="Jharkhand Agritech & Rural Innovation Foundation", type="Industry", location="Ranchi", district="Ranchi", research_domains="AgriTech, BioTech, Rural Livelihoods", status="ACTIVE"),
        ]
        db.bulk_save_objects(orgs)
        db.commit()

        # ── 2. SEED CORE USERS ─────────────────────────────────────────────
        print("[seed_mock_data] Seeding authenticated system users...")
        users = [
            User(id="user-gov-1", name="Jharkhand Nodal Officer", email="gov@jharkhand.gov.in", password_hash="dummyhash", role="Gov", org_id="org-gov-1"),
            User(id="user-cit-1", name="Rahul Kumar", email="rahul@citizen.in", password_hash="dummyhash", role="Citizen", org_id=None),
            User(id="user-univ-1", name="Dr. S. K. Sharma", email="sharma@rims.ac.in", password_hash="dummyhash", role="University", org_id="org-univ-1"),
            User(id="user-univ-2", name="Prof. A. K. Verma", email="verma@iitism.ac.in", password_hash="dummyhash", role="University", org_id="org-univ-2"),
            User(id="user-univ-3", name="Prof. Anita Hansda", email="hansda@nitjsr.ac.in", password_hash="dummyhash", role="University", org_id="org-univ-3"),
            User(id="user-univ-4", name="Dr. Rajeshwar Singh", email="singh@bau.ac.in", password_hash="dummyhash", role="University", org_id="org-univ-4"),
            User(id="user-ind-1", name="Tata Steel CSR Lead", email="csr@tatasteel.com", password_hash="dummyhash", role="Industry", org_id="org-ind-1"),
            User(id="user-ind-2", name="BCCL Community Lead", email="csr@bccl.gov.in", password_hash="dummyhash", role="Industry", org_id="org-ind-2"),
        ]
        db.bulk_save_objects(users)
        db.commit()

        # ── 3. ASSEMBLE 127 REALISTIC CHALLENGES ───────────────────────────
        print("[seed_mock_data] Synthesizing 127 detailed Jharkhand societal challenge clusters...")
        now = datetime.now(timezone.utc)
        challenges = []
        specs_by_id = {s["id"]: s for s in CHALLENGE_SPECS}

        # First add the 24 handcrafted top challenge specifications
        for spec in CHALLENGE_SPECS:
            dist = spec["district"]
            base_lat, base_lng = DISTRICT_COORDS[dist]
            lat = round(base_lat + random.uniform(-0.02, 0.02), 6)
            lng = round(base_lng + random.uniform(-0.02, 0.02), 6)

            comp_count = spec["social"] + spec["citizen"]
            reach = int(comp_count * random.uniform(3.0, 5.5))
            trend = random.choices(["up", "stable", "down"], weights=[45, 45, 10])[0]

            days_ago = random.randint(1, 13)
            created_at = now - timedelta(days=days_ago, hours=random.randint(0, 23))

            # Several citizen-submitted challenges assigned to Rahul Kumar
            creator_id = "user-cit-1" if spec["id"] in ["CHL-2026-0001", "CHL-2026-0002", "CHL-2026-0005", "CHL-2026-0006", "CHL-2026-0015", "CHL-2026-0022"] else "user-cit-1"

            challenges.append(Challenge(
                id=spec["id"],
                title=f"{spec['title']} — {spec['block']}, {spec['district']}",
                official_description=spec["desc"],
                ai_generated_summary=spec["ai_summary"],
                domain=spec["domain"],
                department=spec["dept"],
                status=spec["status"],
                priority_score=spec["prio"],
                location=f"{spec['block']}, {spec['district']}",
                district=spec["district"],
                block=spec["block"],
                lat=lat,
                lng=lng,
                complaint_count=comp_count,
                source_counts={
                    "social": spec["social"],
                    "citizen": spec["citizen"],
                    "ngo": random.randint(10, 45),
                    "government": random.randint(1, 4) if spec["status"] != "pending_verification" else 0
                },
                ai_confidence=round(random.uniform(0.88, 0.98), 2),
                duplicate_risk=round(random.uniform(0.01, 0.08), 2),
                rt_reach=reach,
                trend=trend,
                verified=(spec["status"] != "pending_verification"),
                verified_by="user-gov-1" if spec["status"] != "pending_verification" else None,
                verified_at=(created_at + timedelta(hours=6)) if spec["status"] != "pending_verification" else None,
                created_by=creator_id,
                media_urls=spec.get("media_urls"),
                created_at=created_at
            ))

        # Status distribution pool for remaining 103 items
        # To hit targets: pending: ~22, verified: ~25, matches_suggested: ~16, ready_for_routing: ~14, routed: ~18, in_project: ~21, resolved: ~11
        # Handcrafted items already contributed: in_project: 18, resolved: 6 (Total 24)
        # Remaining 103 items will supply:
        remaining_status_pool = (
            ["pending_verification"] * 22 +
            ["verified"] * 25 +
            ["matches_suggested"] * 16 +
            ["ready_for_routing"] * 15 +
            ["routed"] * 18 +
            ["in_project"] * 3 +
            ["resolved"] * 4
        )
        random.shuffle(remaining_status_pool)

        # Build remaining challenges up to 127
        curr_num = 25
        tmpl_idx = 0
        for dist, target_count in DISTRICT_DISTRIBUTION:
            already_done = sum(1 for c in challenges if c.district == dist)
            needed = target_count - already_done
            for _ in range(needed):
                if curr_num > 127 or not remaining_status_pool:
                    break

                tmpl = TEMPLATES_CATALOG[tmpl_idx % len(TEMPLATES_CATALOG)]
                tmpl_idx += 1

                t_title, t_desc, t_domain, t_dept, prio_range, count_range = tmpl
                base_lat, base_lng = DISTRICT_COORDS[dist]
                lat = round(base_lat + random.uniform(-0.025, 0.025), 6)
                lng = round(base_lng + random.uniform(-0.025, 0.025), 6)

                st = remaining_status_pool.pop()
                prio = random.randint(*prio_range)
                social_cnt = random.randint(*count_range)
                cit_cnt = int(social_cnt * random.uniform(0.4, 0.7))
                tot_comp = social_cnt + cit_cnt
                reach = int(tot_comp * random.uniform(2.5, 6.0))
                trend = random.choices(["up", "stable", "down"], weights=[40, 45, 15])[0]

                days_ago = random.randint(0, 13)
                created_at = now - timedelta(days=days_ago, hours=random.randint(0, 23))
                cid = f"CHL-2026-{str(curr_num).zfill(4)}"

                # Assign photo evidence to 4 additional challenges
                media = None
                if curr_num in [28, 35, 42, 56]:
                    media = ["/uploads/evidence/ev_06b50888f03e.jpeg"] if curr_num % 2 == 0 else ["/uploads/evidence/ev_3e4f0db840da.jpeg"]

                challenges.append(Challenge(
                    id=cid,
                    title=f"{t_title} — {dist}",
                    official_description=f"{t_desc} Observed across multiple habitations in {dist} district requiring institutional technical intervention.",
                    ai_generated_summary=f"Automated distress cluster: {t_desc[:120]}...",
                    domain=t_domain,
                    department=t_dept,
                    status=st,
                    priority_score=prio,
                    location=f"{dist} Central Block, {dist}",
                    district=dist,
                    block=f"{dist} Central",
                    lat=lat,
                    lng=lng,
                    complaint_count=tot_comp,
                    source_counts={
                        "social": social_cnt,
                        "citizen": cit_cnt,
                        "ngo": random.randint(5, 25),
                        "government": 1 if st not in ["pending_verification", "verified"] else 0
                    },
                    ai_confidence=round(random.uniform(0.85, 0.97), 2),
                    duplicate_risk=round(random.uniform(0.01, 0.12), 2),
                    rt_reach=reach,
                    trend=trend,
                    verified=(st != "pending_verification"),
                    verified_by="user-gov-1" if st != "pending_verification" else None,
                    verified_at=(created_at + timedelta(hours=8)) if st != "pending_verification" else None,
                    created_by="user-cit-1",
                    media_urls=media,
                    created_at=created_at
                ))
                curr_num += 1

        db.bulk_save_objects(challenges)
        db.commit()
        print(f"[seed_mock_data] Seeded {len(challenges)} master challenges across Jharkhand.")

        # ── 4. SEED EVIDENCE RECORDS ───────────────────────────────────────
        print("[seed_mock_data] Seeding citizen & field evidence records...")
        evidence_records = []
        for ch in challenges:
            # 1. Citizen report evidence
            ev_id1 = f"ev-{ch.id.lower()}-1"
            evidence_records.append(ChallengeEvidence(
                id=ev_id1,
                challenge_id=ch.id,
                source="citizen",
                raw_text=f"Citizen Grievance #{ch.id}: {ch.official_description}",
                clean_text=ch.official_description or "",
                media_urls=ch.media_urls,
                submitted_lat=ch.lat,
                submitted_lng=ch.lng,
                created_at=ch.created_at
            ))

            # 2. Social signal evidence for high-priority challenges
            if ch.priority_score and ch.priority_score >= 80:
                ev_id2 = f"ev-{ch.id.lower()}-2"
                evidence_records.append(ChallengeEvidence(
                    id=ev_id2,
                    challenge_id=ch.id,
                    source="twitter",
                    raw_text=f"RT @JharkhandVoice: Multiple community complaints regarding {ch.title}. Critical intervention needed! #{ch.domain.replace(' ', '')} #JharkhandGrievance",
                    clean_text=f"Community reports on {ch.title}. Public infrastructure issue escalated via social listening stream.",
                    media_urls=None,
                    submitted_lat=ch.lat,
                    submitted_lng=ch.lng,
                    created_at=ch.created_at + timedelta(hours=2)
                ))

        db.bulk_save_objects(evidence_records)
        db.commit()

        # ── 5. SEED MATCHES ────────────────────────────────────────────────
        print("[seed_mock_data] Generating multi-institutional university matches...")
        matches = []
        all_unis = ["org-univ-1", "org-univ-2", "org-univ-3", "org-univ-4", "org-univ-5", "org-univ-6", "org-univ-7", "org-univ-8"]
        
        for ch in challenges:
            if ch.status in ["matches_suggested", "ready_for_routing", "routed", "in_project", "resolved"]:
                spec = specs_by_id.get(ch.id)
                assigned_uni = spec.get("uni_id") if spec else None

                # Pick 2-3 matched universities
                matched_orgs = []
                if assigned_uni:
                    matched_orgs.append(assigned_uni)
                
                # Pick 1-2 other relevant unis
                candidates = [u for u in all_unis if u not in matched_orgs]
                matched_orgs.extend(random.sample(candidates, 2))

                for i, u_id in enumerate(matched_orgs):
                    is_accepted = (ch.status in ["in_project", "resolved"] and (u_id == assigned_uni or i == 0))
                    score = random.randint(88, 98) if is_accepted else random.randint(76, 89)
                    matches.append(Match(
                        id=str(uuid.uuid4()),
                        challenge_id=ch.id,
                        org_id=u_id,
                        match_score=score,
                        match_reason=f"Strong research alignment in {ch.domain} and territorial capability in {ch.district}.",
                        status="accepted" if is_accepted else "suggested"
                    ))

        db.bulk_save_objects(matches)
        db.commit()

        # ── 6. SEED ROUTING BATCHES & INVITATIONS ───────────────────────────
        print("[seed_mock_data] Creating routing batches and invitations...")
        routing_batches = []
        routing_invitations = []

        # (a) Routed challenges (Active government dispatch with impending deadlines)
        routed_challenges = [c for c in challenges if c.status == "routed"]
        for idx, ch in enumerate(routed_challenges):
            batch_id = f"batch-{ch.id.lower()}"
            dl = now + timedelta(days=random.randint(5, 14))
            routing_batches.append(RoutingBatch(
                id=batch_id,
                challenge_id=ch.id,
                deadline=dl,
                note="Priority routing under State Innovation Mission. Please submit technical proposal before SLA expiration.",
                status="active",
                created_at=ch.created_at + timedelta(hours=12)
            ))

            # Assign invitations to 2-3 universities
            # Ensure org-univ-1 (RIMS) has 4 invitations so Dr. Sharma sees them in University Innovation Portal!
            if idx < 4:
                invitees = ["org-univ-1", "org-univ-3", "org-univ-5"]
            elif idx < 8:
                invitees = ["org-univ-2", "org-univ-4", "org-univ-7"]
            elif idx < 12:
                invitees = ["org-univ-1", "org-univ-6", "org-univ-8"]
            else:
                invitees = random.sample(all_unis, 3)

            for u_id in invitees:
                routing_invitations.append(RoutingInvitation(
                    id=f"inv-{uuid.uuid4().hex[:8]}",
                    batch_id=batch_id,
                    org_id=u_id,
                    status="pending",
                    created_at=ch.created_at + timedelta(hours=14)
                ))

        # (b) In-project and Resolved challenges (Completed batches with accepted invitations)
        active_and_done = [c for c in challenges if c.status in ["in_project", "resolved"]]
        for ch in active_and_done:
            spec = specs_by_id.get(ch.id)
            uni_id = spec.get("uni_id") if spec else "org-univ-1"
            batch_id = f"batch-{ch.id.lower()}"
            dl = ch.created_at + timedelta(days=10)

            routing_batches.append(RoutingBatch(
                id=batch_id,
                challenge_id=ch.id,
                deadline=dl,
                note="Formally dispatched to empaneled academic research institution.",
                status="completed",
                created_at=ch.created_at + timedelta(hours=8)
            ))

            # Accepted invitation for the assigned university
            routing_invitations.append(RoutingInvitation(
                id=f"inv-{uuid.uuid4().hex[:8]}",
                batch_id=batch_id,
                org_id=uni_id,
                status="accepted",
                responded_at=ch.created_at + timedelta(days=2),
                created_at=ch.created_at + timedelta(hours=10)
            ))

            # Other closed invitations
            other_uni = "org-univ-3" if uni_id != "org-univ-3" else "org-univ-2"
            routing_invitations.append(RoutingInvitation(
                id=f"inv-{uuid.uuid4().hex[:8]}",
                batch_id=batch_id,
                org_id=other_uni,
                status="closed",
                responded_at=None,
                created_at=ch.created_at + timedelta(hours=10)
            ))

        db.bulk_save_objects(routing_batches)
        db.bulk_save_objects(routing_invitations)
        db.commit()

        # ── 7. SEED PROJECTS & PROPOSALS ───────────────────────────────────
        print("[seed_mock_data] Populating active R&D projects and industry proposals...")
        projects = []
        proposals = []

        for ch in active_and_done:
            spec = specs_by_id.get(ch.id, {})
            uni_id = spec.get("uni_id", "org-univ-1")
            ind_id = spec.get("ind_id", "org-ind-1")

            p_status = "deployed" if ch.status == "resolved" else random.choice(["prototype", "in_progress", "field_pilot"])
            proj_id = f"proj-{ch.id.lower()}"

            milestones = [
                {
                    "title": "Phase 1: Field Site Inspection & Baseline Telemetry Audit",
                    "status": "completed",
                    "description": f"Comprehensive on-ground sample gathering and telemetry baseline across {ch.location}.",
                    "completed_at": (ch.created_at + timedelta(days=3)).isoformat()
                },
                {
                    "title": "Phase 2: Hardware Prototype Engineering & Lab Benchmark",
                    "status": "completed" if p_status in ["in_progress", "field_pilot", "deployed"] else "in_progress",
                    "description": "Lab fabrication and micro-controller sensory benchmark testing.",
                    "completed_at": (ch.created_at + timedelta(days=6)).isoformat() if p_status in ["in_progress", "field_pilot", "deployed"] else None
                },
                {
                    "title": "Phase 3: Field Pilot Deployment & Community Trials",
                    "status": "completed" if p_status == "deployed" else ("in_progress" if p_status == "field_pilot" else "pending"),
                    "description": "Pilot deployment across trial habitations with stakeholder feedback verification.",
                    "completed_at": (ch.created_at + timedelta(days=10)).isoformat() if p_status == "deployed" else None
                },
                {
                    "title": "Phase 4: District Administration Handover & Impact Audit",
                    "status": "completed" if p_status == "deployed" else "pending",
                    "description": "Full operational integration with state nodal officers and measurable citizen impact dossier.",
                    "completed_at": (ch.created_at + timedelta(days=12)).isoformat() if p_status == "deployed" else None
                }
            ]

            projects.append(Project(
                id=proj_id,
                challenge_id=ch.id,
                org_id=uni_id, # Crucial: links to university for OrgDashboard!
                status=p_status,
                milestones_json=json.dumps(milestones),
                created_at=ch.created_at + timedelta(days=2)
            ))

            # Proposal record
            b_num = spec.get("budget", random.randint(650000, 1500000))
            b_req = spec.get("budget_req", f"₹{b_num:,}")
            f_status = spec.get("funding_status", "Funded" if p_status in ["field_pilot", "deployed"] else random.choice(["Open for Funding", "Partially Funded"]))
            c_status = spec.get("collab_status", "Partnered" if f_status == "Funded" else "Seeking Industry Partner")
            f_commit = spec.get("funds", b_num if f_status == "Funded" else (int(b_num * 0.5) if f_status == "Partially Funded" else 0))
            partners = spec.get("partners", ["Tata Steel CSR"] if f_status == "Funded" else [])

            proposals.append(Proposal(
                id=f"prop-{ch.id.lower()}",
                project_id=proj_id,
                challenge_id=ch.id,
                org_id=uni_id,
                title=spec.get("project_title", f"Engineered Solution for {ch.title}"),
                problem_understanding=ch.official_description,
                proposed_solution=f"Institutional technical intervention designed by {uni_id} utilizing edge sensors, field-tested methodology, and localized deployment.",
                approach_methodology="Modular engineering architecture comprising rugged edge telemetry nodes, low-power mesh connectivity, and automated anomaly alerting.",
                trl=spec.get("trl", "TRL-6 (Field Pilot Ready)"),
                budget_required=b_req,
                budget_num=b_num,
                impact_metrics=spec.get("impact", "Positively impacts 5,000+ citizens and resolves civic vulnerability."),
                timeline="4 Months",
                resources_needed="Microcontrollers, sensor instrumentation kits, field travel allowance, pilot installation hardware",
                faculty_lead=spec.get("lead", "Dr. Faculty Lead (Academic R&D)"),
                contact_email=spec.get("email", "research.lead@university.ac.in"),
                team_members="Faculty Principal Investigator, 2 Research Scholars, 4 Student Field Engineers",
                evidence_research="Documented research thesis & laboratory benchmark dossier filed under SIH 2026",
                status="accepted" if p_status == "deployed" else "submitted",
                funding_status=f_status,
                collaboration_status=c_status,
                funds_committed=f_commit,
                partners=partners,
                created_at=ch.created_at + timedelta(days=2),
                updated_at=ch.created_at + timedelta(days=3)
            ))

        db.bulk_save_objects(projects)
        db.bulk_save_objects(proposals)
        db.commit()

        print(f"[seed_mock_data] SUCCESS! Seeded {len(challenges)} challenges, {len(matches)} matches, {len(routing_batches)} routing batches, {len(routing_invitations)} invitations, {len(projects)} active projects, and {len(proposals)} proposals.")

    finally:
        db.close()

if __name__ == "__main__":
    seed()
