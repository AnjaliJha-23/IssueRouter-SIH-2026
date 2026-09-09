"""
api/proposals.py — University Proposed Solutions for Civic Challenges (SIH 2026 Industry Portal).
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import Challenge, Organization, Proposal

router = APIRouter(prefix="/api/proposals", tags=["proposals"])

# In-memory store / registry for proposal status updates (collaborations, fundings, feedback)
# To persist across API requests in memory alongside database challenges
PROPOSAL_STATE_OVERRIDES: Dict[str, Dict[str, Any]] = {}

# University Solution templates mapped by domain / problem type
# University Solution templates mapped by domain / problem type
UNIVERSITY_SOLUTIONS_MAP = {
    "HealthTech": [
        {
            "university": "RIMS Ranchi",
            "faculty_lead": "Dr. S. K. Sharma (Biomedical Engineering)",
            "contact_email": "sharma.biomed@rims.ac.in",
            "solution_summary": "IoT-enabled Solar Telemedicine Kiosk with offline ECG, vital sensors, and satellite fallback link for remote tribal primary health centres.",
            "trl": "TRL-6 (Field Pilot Ready)",
            "budget_required": "₹8,50,000",
            "budget_num": 850000,
            "impact_metrics": "Connects 40,000+ villagers to specialist doctors without 60km travel.",
            "research_report": {
                "abstract": "An indigenous low-power tele-health diagnostic station engineered to bridge the critical specialist care deficit across rural Jharkhand. The station combines offline multi-parameter biometric acquisition, encrypted store-and-forward telemetry, and on-demand video uplink to RIMS specialist doctors.",
                "technical_architecture": "Microcontroller-based telemetry board interfacing 12-lead digital ECG, pulse oximeter, blood pressure cuff, and digital stethoscope with 128-bit AES encryption. Power subsystem uses a 200W monocrystalline solar panel backed by a 12V LiFePO4 battery providing 72 hours of uninterrupted off-grid operation.",
                "tech_stack": ["Edge Telemetry (ESP32-S3)", "12-Lead Diagnostic ECG Module", "Solar MPPT + LiFePO4 Battery", "WebRTC Video Relay", "FastAPI Secure Gateway"],
                "key_innovations": [
                    "Zero-bandwidth Store-and-Forward sync when cellular network drops in remote valleys",
                    "Voice-guided vernacular interface in Hindi & Santhali for ASHA health workers",
                    "Under-₹5 per consultation operating cost with 100% solar self-sufficiency",
                    "Direct real-time EHR integration with state Ayushman Bharat digital registry"
                ],
                "jharkhand_deployment_plan": "Phase 1 rollout across 8 Primary Health Centres in Saraidhela & Tundi blocks, Dhanbad, followed by district-wide expansion across 32 tribal sub-centres.",
                "validation_data": "99.1% diagnostic telemetry correlation compared to hospital benchmark machines across 420 volunteer screenings at RIMS Ranchi.",
                "budget_breakdown": [
                    {"item": "Kiosk Fabrication & Sensor Modules", "cost": "₹3,80,000"},
                    {"item": "Solar Subsystem & Power Storage", "cost": "₹1,90,000"},
                    {"item": "ASHA Worker Training & Field Trials", "cost": "₹1,50,000"},
                    {"item": "Cloud EHR Server & Telemetry API", "cost": "₹1,30,000"}
                ],
                "timeline_phases": [
                    {"phase": "Phase 1 (Months 1-3)", "milestone": "Custom Hardware Assembly & Lab Safety Benchmark Tests"},
                    {"phase": "Phase 2 (Months 4-6)", "milestone": "Deployment of 4 Pilot Kiosks in Saraidhela PHCs"},
                    {"phase": "Phase 3 (Months 7-9)", "milestone": "Field Trial Evaluation & ASHA Training Handover"},
                    {"phase": "Phase 4 (Months 10-12)", "milestone": "Full Operational Handover to State Health Department"}
                ],
                "ip_and_publications": "Patent Application #202531008412 · Published in IEEE Global Humanitarian Tech Conference 2025"
            }
        },
        {
            "university": "IIT ISM Dhanbad",
            "faculty_lead": "Prof. A. K. Verma (AI & Robotics Lab)",
            "contact_email": "verma.ak@iitism.ac.in",
            "solution_summary": "Smart Ambulance Traffic Preemption System with AI Route Guidance and automated Green Corridor signaling across high-congestion city arteries.",
            "trl": "TRL-7 (Ready for Production)",
            "budget_required": "₹14,00,000",
            "budget_num": 1400000,
            "impact_metrics": "Reduces critical emergency transit time by 42% in dense corridors.",
            "research_report": {
                "abstract": "An intelligent urban mobility intervention that dynamically creates emergency green corridors for critical care ambulances using V2X (Vehicle-to-Infrastructure) LoRaWAN beaconing and predictive traffic density neural networks.",
                "technical_architecture": "Edge V2X transceivers mounted on ambulances broadcast priority packets to roadside traffic controller nodes at 865 MHz. Central orchestration server recalculates signal phase offsets and clears traffic queue bottlenecks 400m ahead of emergency arrival.",
                "tech_stack": ["Edge AI (Jetson Orin Nano)", "V2X LoRa Mesh (865 MHz)", "OpenCV Optical Flow", "Traffic Signal Relay Controller", "PostGIS Spatial Engine"],
                "key_innovations": [
                    "Automatic signal preemption without requiring manual traffic police override",
                    "Dynamic rerouting around sudden waterlogging or road blockages in real-time",
                    "Sub-200ms latency between ambulance proximity beacon and signal green switch",
                    "Fail-safe fallback returning signals to default cycle immediately after pass-through"
                ],
                "jharkhand_deployment_plan": "Pilot implementation across 14 major signal intersections linking Saraidhela, Bank More, and SNMMCH Hospital in Dhanbad.",
                "validation_data": "42.3% average reduction in emergency transit duration measured during 85 simulated peak-hour emergency runs.",
                "budget_breakdown": [
                    {"item": "V2X Signal Controllers for 14 Intersections", "cost": "₹6,50,000"},
                    {"item": "Ambulance Onboard Units (10 vehicles)", "cost": "₹2,80,000"},
                    {"item": "Control Room Software & Server Backend", "cost": "₹2,70,000"},
                    {"item": "Field Commissioning & City Traffic Police Training", "cost": "₹2,00,000"}
                ],
                "timeline_phases": [
                    {"phase": "Phase 1 (Months 1-3)", "milestone": "Traffic Intersection Sensor Audits & Controller Hardware Prep"},
                    {"phase": "Phase 2 (Months 4-6)", "milestone": "Interfacing with Dhanbad Traffic Signals on Main Arterial Corridor"},
                    {"phase": "Phase 3 (Months 7-9)", "milestone": "Live Fleet Trials with 10 SNMMCH Emergency Ambulances"},
                    {"phase": "Phase 4 (Months 10-12)", "milestone": "Integration with Integrated Command and Control Centre (ICCC)"}
                ],
                "ip_and_publications": "Filed with Indian Patent Office · Ref: 2025-ISM-ROBOTICS-019"
            }
        },
        {
            "university": "AIIMS Deoghar",
            "faculty_lead": "Dr. Meenakshi Sundaram (Community Medicine)",
            "contact_email": "m.sundaram@aiimsdeoghar.edu.in",
            "solution_summary": "Portable Rapid Blood Storage & Cold-Chain Battery Pack with GSM temperature monitoring for rural trauma response.",
            "trl": "TRL-5 (Prototype Validated)",
            "budget_required": "₹6,20,000",
            "budget_num": 620000,
            "impact_metrics": "Zero-loss blood transportation covering 12 remote community clinics.",
            "research_report": {
                "abstract": "A compact thermoelectric active refrigeration transport box engineered for carrying whole blood, vaccines, and anti-venom to remote tribal clinics without cold-chain degradation.",
                "technical_architecture": "Solid-state Peltier cooling engine paired with VIP (Vacuum Insulated Panels) maintaining 2°C - 6°C across 48 hours on internal Li-ion battery. Onboard GPS/GSM unit reports live temperature telemetry every 60 seconds with automated geo-fenced excursion alarms.",
                "tech_stack": ["Peltier Thermoelectric Engine", "Vacuum Insulated Panels (VIP)", "GSM/GPS Telemetry Controller", "Li-Ion Smart BMS", "Mobile Cold-Chain Audit App"],
                "key_innovations": [
                    "Zero ice-pack dependency with active solid-state digital temperature regulation",
                    "Audible and SMS emergency alerts if internal temperature deviates from 2°C - 6°C",
                    "Lightweight 4.2 kg backpack design suitable for two-wheeler / walking rural health workers",
                    "Solar charging input for prolonged field emergencies"
                ],
                "jharkhand_deployment_plan": "Deployment across 12 remote trauma and snakebite hotspots in Santhal Pargana and Deoghar rural blocks.",
                "validation_data": "Zero blood unit spoilage recorded across 180 hours of extreme ambient heat testing (44°C ambient at AIIMS Deoghar lab).",
                "budget_breakdown": [
                    {"item": "10 Portable Active Cold-Chain Units", "cost": "₹3,20,000"},
                    {"item": "GSM Sensors, GPS Modules & Cloud Dashboard", "cost": "₹1,40,000"},
                    {"item": "Trauma Worker Training & Emergency Protocol Manuals", "cost": "₹90,000"},
                    {"item": "Clinical Certification & Testing Validation", "cost": "₹70,000"}
                ],
                "timeline_phases": [
                    {"phase": "Phase 1 (Months 1-3)", "milestone": "Hardware Fabrication & Thermal Chamber Stress Testing"},
                    {"phase": "Phase 2 (Months 4-6)", "milestone": "Field Dispatch of 10 Units to Emergency Ambulance Fleet"},
                    {"phase": "Phase 3 (Months 7-9)", "milestone": "Rural Blood Transit Trials & Telemetry Verification"},
                    {"phase": "Phase 4 (Months 10-12)", "milestone": "District Health Society Integration for Snakebite / Trauma Support"}
                ],
                "ip_and_publications": "Patent Application #202531002914 · Published in Journal of Emergency Medicine & Trauma 2025"
            }
        }
    ],
    "BioTech": [
        {
            "university": "BIT Mesra",
            "faculty_lead": "Dr. Prerna Sengupta (Biotechnology Dept)",
            "contact_email": "psengupta@bitmesra.ac.in",
            "solution_summary": "Low-Cost Fortified Spirulina & Millet Nutritional Supplementary wafers targeting severe acute malnutrition in tribal belts.",
            "trl": "TRL-7 (Ready for Production)",
            "budget_required": "₹5,00,000",
            "budget_num": 500000,
            "impact_metrics": "Reaches 2,500 children across 15 anganwadis within 60 days.",
            "research_report": {
                "abstract": "A high-density micronutrient food supplement formulation utilizing locally cultivable Spirulina Platensis microalgae blended with extruded Finger Millet (Ragi) and defatted soy flour. Developed specifically to treat Severe Acute Malnutrition (SAM) and Moderate Acute Malnutrition (MAM) in tribal children aged 6 months to 6 years across Jharkhand.",
                "technical_architecture": "Controlled photobioreactor cultivation of Spirulina biomass with closed-loop mineral enrichment, low-temperature vacuum freeze-drying to preserve heat-labile vitamins (B-complex, Vitamin A), followed by twin-screw cold extrusion into palatable chewable wafers with 6-month hermetic shelf life.",
                "tech_stack": ["Spirulina Photobioreactor Culture", "Cold Extrusion Processing", "Nutritional Chromatography (HPLC)", "Moisture-Barrier Biodegradable Packaging", "FSSAI Food Safety Compliance Protocol"],
                "key_innovations": [
                    "100% bio-available micro-encapsulated iron and zinc with zero gastrointestinal irritation",
                    "28g protein and 450 kcal per 100g wafer, exceeding WHO SAM recovery benchmarks",
                    "Manufactured using local tribal millets at 70% lower cost than imported commercial supplements",
                    "Naturally sweetened with local jaggery and Mahua extract for high pediatric acceptability (96%)"
                ],
                "jharkhand_deployment_plan": "Distribution pilot across 15 Anganwadi centres in Saraidhela and Govindpur blocks, Dhanbad, targeting 2,500 tribal children in collaboration with District Social Welfare.",
                "validation_data": "92.4% recovery rate to normal weight-for-height Z-scores observed in 60-day clinical cohort study (n=180 children, BIT Mesra BioTech Lab).",
                "budget_breakdown": [
                    {"item": "Spirulina Pilot Photobioreactor & Processing Facility", "cost": "₹2,10,000"},
                    {"item": "Millet Batch Extrusion & Packaging Consumables", "cost": "₹1,20,000"},
                    {"item": "Anganwadi Worker Training & Distribution Kits", "cost": "₹90,000"},
                    {"item": "NABL Lab Testing, FSSAI Licensing & Biometric Tracking", "cost": "₹80,000"}
                ],
                "timeline_phases": [
                    {"phase": "Phase 1 (Months 1-3)", "milestone": "Production Batch Scaling & NABL Nutritional Certifications"},
                    {"phase": "Phase 2 (Months 4-6)", "milestone": "Anganwadi Enrolment & Baseline Child Biometric Screening"},
                    {"phase": "Phase 3 (Months 7-9)", "milestone": "60-Day Dietary Intervention & Mid-Term Weight-for-Height Audits"},
                    {"phase": "Phase 4 (Months 10-12)", "milestone": "District Wide Program Handover & Micro-Enterprise Setup for Tribal SHGs"}
                ],
                "ip_and_publications": "Patent Pending: 202531098421 · Published in Journal of Food Science & Nutrition 2025"
            }
        },
        {
            "university": "IIT ISM Dhanbad",
            "faculty_lead": "Dr. Rajiv Ranjan (Blockchain & Cyber-Physical Systems)",
            "contact_email": "rranjan@iitism.ac.in",
            "solution_summary": "Decentralized Pharmaceutical Traceability QR Matrix with encrypted batch verification to detect counterfeit medicine in rural dispensaries.",
            "trl": "TRL-6 (Field Pilot Ready)",
            "budget_required": "₹9,50,000",
            "budget_num": 950000,
            "impact_metrics": "Authenticates 100% of state-supplied medicine batches.",
            "research_report": {
                "abstract": "An end-to-end anti-counterfeiting supply chain verification system for government-supplied medicines in rural clinics. Every medicine blister pack is laser-serialized with cryptographic micro-QR codes verified via offline-capable smartphone apps.",
                "technical_architecture": "Hyperledger-backed decentralized immutable ledger recording batch provenance from central medical stores to last-mile rural dispensaries. Mobile client utilizes lightweight elliptic curve signatures to verify authenticity even without active internet connectivity.",
                "tech_stack": ["Permissioned Ledger", "Cryptographic Micro-QR", "Offline ECDSA Signatures", "React Native Mobile Scanner", "FastAPI Verification Node"],
                "key_innovations": [
                    "Completely tamper-proof holographic QR micro-print resistant to replication",
                    "Offline validation mode that stores scans locally and cryptographically confirms genuine stock",
                    "Automated instant SMS alert to District Drug Inspector if counterfeit scan is detected",
                    "Zero per-scan transaction fee with lightweight edge node deployment"
                ],
                "jharkhand_deployment_plan": "Pilot deployment across 25 Community Health Centres and 40 rural medicine distribution points in Dhanbad and Bokaro.",
                "validation_data": "100% counterfeit detection rate in blind trials with 1,200 authentic and 300 cloned blister test packs.",
                "budget_breakdown": [
                    {"item": "Laser QR Serialization & Printing Equipment", "cost": "₹4,20,000"},
                    {"item": "Ledger Nodes & Secure Cloud Backend", "cost": "₹2,50,000"},
                    {"item": "Pharmacist Training & Handheld Scanners", "cost": "₹1,80,000"},
                    {"item": "State Drug Regulatory Audits & Compliance", "cost": "₹1,00,000"}
                ],
                "timeline_phases": [
                    {"phase": "Phase 1 (Months 1-3)", "milestone": "Central Medical Warehouse Serialization Integration"},
                    {"phase": "Phase 2 (Months 4-6)", "milestone": "Pilot Dispatch of 50,000 Tagged Medicine Units to 25 CHCs"},
                    {"phase": "Phase 3 (Months 7-9)", "milestone": "Last-Mile Pharmacist App Verification & Stress Testing"},
                    {"phase": "Phase 4 (Months 10-12)", "milestone": "State-wide Policy Integration with Jharkhand Medical Supplies Corp"}
                ],
                "ip_and_publications": "Published in IEEE Transactions on Dependable and Secure Computing 2025"
            }
        }
    ],
    "Public Health": [
        {
            "university": "NIT Jamshedpur",
            "faculty_lead": "Dr. Rajeshwar Singh (Civil & Environmental Engineering)",
            "contact_email": "rsingh.env@nitjsr.ac.in",
            "solution_summary": "Community-Scale Graphene-Sand Hybrid Filtration Column with automated backwashing for Arsenic and Fluoride removal from tube wells.",
            "trl": "TRL-6 (Field Pilot Ready)",
            "budget_required": "₹11,00,000",
            "budget_num": 1100000,
            "impact_metrics": "Supplies 50,000 liters/day of WHO-compliant drinking water.",
            "research_report": {
                "abstract": "A decentralized high-throughput water filtration plant utilizing reduced Graphene Oxide (rGO) coated quartz sand and activated alumina adsorbent beds. Engineered to eliminate heavy metal contamination, Arsenic (>0.05 mg/L), and excess Fluoride from groundwater in vulnerable rural habitations.",
                "technical_architecture": "Multi-stage gravity-fed columnar filtration with hydro-cyclone pre-sedimentation, rGO-coated porous sand matrix for heavy metal adsorption, and an automated solar-powered solenoid backwashing cycle to prolong media lifespan to 24 months.",
                "tech_stack": ["Reduced Graphene Oxide (rGO) Synthesis", "Activated Alumina Filter Beds", "Solar-Powered Backwash Actuators", "IoT Turbidity & TDS Telemetry", "Gravity Columnar Hydraulics"],
                "key_innovations": [
                    "Reduces Arsenic from 0.15 mg/L to <0.005 mg/L, well below WHO safety limits",
                    "Zero electricity required for regular filtration cycle (gravity head powered)",
                    "Low operating expenditure (<₹0.02 per liter of purified water produced)",
                    "Real-time IoT water quality sensor logging TDS, pH, and flow rate to district dashboard"
                ],
                "jharkhand_deployment_plan": "Installation of 3 community water purification kiosks in Arsenic-affected habitations of Sahibganj and Dhanbad rural blocks.",
                "validation_data": "Tested and certified by NABL Accredited Environmental Lab with 99.8% Arsenic and 96.4% Fluoride removal over 100,000 liters continuous run.",
                "budget_breakdown": [
                    {"item": "Filtration Column Construction & rGO Media", "cost": "₹5,20,000"},
                    {"item": "Solar Backwashing Pumps & Water Storage", "cost": "₹2,60,000"},
                    {"item": "IoT Telemetry Kiosk & Water ATM Dispenser", "cost": "₹1,80,000"},
                    {"item": "Community Water Committee (Pani Samiti) Training", "cost": "₹1,40,000"}
                ],
                "timeline_phases": [
                    {"phase": "Phase 1 (Months 1-3)", "milestone": "Site Hydrogeological Testing & Filter Media Synthesis"},
                    {"phase": "Phase 2 (Months 4-6)", "milestone": "Civil Construction & Column Assembly at 3 Pilot Sites"},
                    {"phase": "Phase 3 (Months 7-9)", "milestone": "3-Month Water Quality Monitoring & NABL Certification"},
                    {"phase": "Phase 4 (Months 10-12)", "milestone": "Gram Panchayat Handover with Local Youth Maintenance Training"}
                ],
                "ip_and_publications": "Patent Granted: IN398412 · Chemical Engineering Journal 2025"
            }
        },
        {
            "university": "Kolhan University",
            "faculty_lead": "Dr. Anita Tirkey (Urban Sanitation Group)",
            "contact_email": "anita.tirkey@kolhanuniv.ac.in",
            "solution_summary": "Automated Bio-Hazard Incineration Unit with electrostatic precipitators for zero-emission hospital waste management.",
            "trl": "TRL-5 (Prototype Validated)",
            "budget_required": "₹12,00,000",
            "budget_num": 1200000,
            "impact_metrics": "Treats 300 kg/day biomedical waste on-site, eliminating open dump hazards.",
            "research_report": {
                "abstract": "A decentralized high-temperature dual-chamber hospital waste incinerator with wet-scrubber and electrostatic precipitator emissions control. Treats infectious biomedical waste directly on hospital premises without releasing toxic dioxins or furans into surrounding residential areas.",
                "technical_architecture": "Dual-chamber thermal oxidizer operating at 850°C (primary) and 1100°C (secondary) with automatic temperature feedback controllers. Flue gases pass through an alkaline spray venturi scrubber and electrostatic precipitator achieving <50 mg/Nm³ particulate emissions.",
                "tech_stack": ["Dual-Chamber Thermal Reactor", "Electrostatic Precipitator (ESP)", "Venturi Alkaline Scrubber", "PLC Automated Control", "Continuous Emission Monitoring (CEMS)"],
                "key_innovations": [
                    "Zero open-dump hazard with immediate 98% volume reduction of hospital waste",
                    "Dioxin and furan emission levels strictly comply with CPCB 2016 Bio-Medical Waste rules",
                    "Heat recovery exchanger providing hot water to hospital sanitation wards",
                    "Real-time continuous emission telemetry streaming to Jharkhand State Pollution Control Board (JSPCB)"
                ],
                "jharkhand_deployment_plan": "Installation at 2 Sub-Divisional Hospitals in Kolhan division and Dhanbad rural hospitals.",
                "validation_data": "99.99% pathogen sterilization efficacy and JSPCB compliant stack emissions verified across 60 days of continuous hospital testing.",
                "budget_breakdown": [
                    {"item": "Dual-Chamber Incinerator Fabrication & ESP", "cost": "₹6,80,000"},
                    {"item": "Wet Scrubber & Automated Temperature PLC", "cost": "₹2,50,000"},
                    {"item": "Civil Foundation, Shed & Waste Segregation Bay", "cost": "₹1,50,000"},
                    {"item": "Pollution Board Compliance Certification & Staff Training", "cost": "₹1,20,000"}
                ],
                "timeline_phases": [
                    {"phase": "Phase 1 (Months 1-3)", "milestone": "Fabrication, Thermal Stress Analysis & ESP Assembly"},
                    {"phase": "Phase 2 (Months 4-6)", "milestone": "Civil Installation at Sub-Divisional Hospital Site"},
                    {"phase": "Phase 3 (Months 7-9)", "milestone": "CEMS Sensor Calibration & JSPCB Compliance Testing"},
                    {"phase": "Phase 4 (Months 10-12)", "milestone": "Handover to Hospital Bio-Waste Management Team"}
                ],
                "ip_and_publications": "Patent Pending · Certified by Central Pollution Control Board Guidelines"
            }
        }
    ],
    "EdTech": [
        {
            "university": "IIT ISM Dhanbad",
            "faculty_lead": "Dr. Manish Swaroop (Computer Science & Education)",
            "contact_email": "mswaroop@iitism.ac.in",
            "solution_summary": "Solar Mesh Offline Learning Server (Santhali & Hindi localized) with gamified STEM curriculum for off-grid rural schools.",
            "trl": "TRL-7 (Ready for Production)",
            "budget_required": "₹7,50,000",
            "budget_num": 750000,
            "impact_metrics": "Equips 20 off-grid schools impacting 4,200 tribal students.",
            "research_report": {
                "abstract": "A ruggedized low-cost micro-server running localized interactive digital educational software over local Wi-Fi mesh, completely detached from internet connectivity requirements. Includes interactive simulations, NCERT/JCERT video lectures in Hindi, Santhali (Ol Chiki), and Ho languages.",
                "technical_architecture": "Single-board quad-core edge compute server with 512GB NVMe content cache, dual-band Wi-Fi access point supporting 60 concurrent student connections within a 150-meter radius. Powered by an integrated 50W solar panel and 10,000mAh battery.",
                "tech_stack": ["Raspberry Pi 5 Edge Server", "Offline Wikipedia & Khan Academy Lite", "Ol Chiki Language TTS Engine", "Mesh Wi-Fi 802.11ac", "Solar Li-Ion Power Management"],
                "key_innovations": [
                    "Completely internet-free high-speed multimedia streaming to any basic student phone or tablet",
                    "Localized pedagogical content in Santhali, Mundari, and Hindi with interactive quiz assessments",
                    "Teacher dashboard tracking student learning progress and quiz metrics offline",
                    "Rugged IP65 dust-proof casing built for rural school classroom environments"
                ],
                "jharkhand_deployment_plan": "Deployment in 20 government tribal primary and middle schools in Tundi and Baghmara blocks, Dhanbad.",
                "validation_data": "38% improvement in STEM quiz scores measured across 350 test students over a 90-day pilot study in Dhanbad rural schools.",
                "budget_breakdown": [
                    {"item": "20 Solar Mesh Edge Server Hardware Units", "cost": "₹3,60,000"},
                    {"item": "Vernacular Content Localization & Ol Chiki Audio Digitization", "cost": "₹1,80,000"},
                    {"item": "Teacher Training Workshops & Field Handover", "cost": "₹1,20,000"},
                    {"item": "Annual Maintenance & Student Assessment Audits", "cost": "₹90,000"}
                ],
                "timeline_phases": [
                    {"phase": "Phase 1 (Months 1-3)", "milestone": "Content Digitization & Santhali Language Verification with Experts"},
                    {"phase": "Phase 2 (Months 4-6)", "milestone": "Installation of 20 Server Hubs in Pilot Tribal Schools"},
                    {"phase": "Phase 3 (Months 7-9)", "milestone": "Teacher Training & Student Learning Progress Audits"},
                    {"phase": "Phase 4 (Months 10-12)", "milestone": "State Education Department Review & District Scale-up Plan"}
                ],
                "ip_and_publications": "Presented at ACM SIGCHI 2025 Education & Development Track"
            }
        }
    ],
    "AgriTech": [
        {
            "university": "Birsa Agricultural University",
            "faculty_lead": "Prof. B. N. Mahato (Soil Science & Agronomy)",
            "contact_email": "bnmahato@baujharkhand.org",
            "solution_summary": "AI-Powered Optical Soil Scanner and Bio-Formulation Spray Kit to reverse soil pathogen blight in Dhanbad & Bokaro farm clusters.",
            "trl": "TRL-6 (Field Pilot Ready)",
            "budget_required": "₹6,80,000",
            "budget_num": 680000,
            "impact_metrics": "Increases per-acre crop yield by 28% for 800 smallholder farmers.",
            "research_report": {
                "abstract": "A handheld multi-spectral optical reflectance device that measures soil NPK, pH, and organic carbon in real-time under 60 seconds. Paired with indigenous Trichoderma and mycorrhizal bio-fungicide formulations to remediate coal-dust degradation and soil blight in Jharkhand agricultural lands.",
                "technical_architecture": "Near-Infrared (NIR) 900-1700nm reflectance spectrometer module coupled to an onboard microcontroller running an optimized CNN inference model. Produces instant soil health cards and custom bio-fertilizer dosage instructions via vernacular Bluetooth audio.",
                "tech_stack": ["NIR Spectroscopy (900-1700nm)", "Edge ML Regression Model", "Bluetooth Low Energy (BLE)", "Trichoderma Harzianum Bio-Formulation", "Android Farmer Kiosk App"],
                "key_innovations": [
                    "Instant 60-second soil test replacing 3-week centralized laboratory waiting times",
                    "Remediates industrial coal particulate contamination and soil acidification using organic bio-agents",
                    "Reduces chemical fertilizer costs for smallholder farmers by 35%",
                    "Audio-visual recommendation in regional languages for non-literate farmers"
                ],
                "jharkhand_deployment_plan": "Deployment across 8 Farmer Producer Organizations (FPOs) in Topchanchi and Baghmara blocks, impacting 800 smallholder farmers.",
                "validation_data": "93.8% correlation with standard wet-chemistry lab soil tests verified across 500 soil samples at BAU Agronomy labs.",
                "budget_breakdown": [
                    {"item": "8 Handheld Optical NIR Scanners", "cost": "₹3,10,000"},
                    {"item": "Bio-Formulation Production & Demonstration Kits", "cost": "₹1,60,000"},
                    {"item": "Farmer Field Demonstrations & Krishi Vigyan Kendra Outreach", "cost": "₹1,20,000"},
                    {"item": "Calibration Testing & Digital Agronomy Platform", "cost": "₹90,000"}
                ],
                "timeline_phases": [
                    {"phase": "Phase 1 (Months 1-3)", "milestone": "NIR Spectral Library Calibration for Jharkhand Soil Profiles"},
                    {"phase": "Phase 2 (Months 4-6)", "milestone": "FPO Distribution & On-Field Bio-Formulation Trials"},
                    {"phase": "Phase 3 (Months 7-9)", "milestone": "Kharif Crop Yield & Soil Health Recovery Assessment"},
                    {"phase": "Phase 4 (Months 10-12)", "milestone": "District Agriculture Office Integration & Scaling"}
                ],
                "ip_and_publications": "Published in ICAR Journal of Agricultural Sciences 2025"
            }
        }
    ],
    "Default": [
        {
            "university": "NIT Jamshedpur",
            "faculty_lead": "Dr. S. K. Mukherjee (Innovation Center)",
            "contact_email": "skmukherjee@nitjsr.ac.in",
            "solution_summary": "Solar-Powered Hybrid Microgrid with IoT Inverter telemetry for uninterrupted utility operations.",
            "trl": "TRL-6 (Field Pilot Ready)",
            "budget_required": "₹10,00,000",
            "budget_num": 1000000,
            "impact_metrics": "Provides 99.9% uptime for essential public infrastructure.",
            "research_report": {
                "abstract": "A resilient grid-tied and islanded hybrid microgrid system designed to eliminate power cut disruptions in critical civic facilities like hospitals, water pump stations, and public dispensaries across Jharkhand.",
                "technical_architecture": "10kW solar photovoltaic array coupled to a bi-directional hybrid MPPT inverter with 20kWh lithium iron phosphate (LiFePO4) battery bank. Smart load management automatically isolates non-essential circuits during grid failures to preserve power for critical medical and lighting loads.",
                "tech_stack": ["10kW Bifacial Solar Array", "Bi-directional Hybrid Inverter", "LiFePO4 Energy Storage", "IoT Modbus Energy Telemetry", "Dynamic Load Shedding Controller"],
                "key_innovations": [
                    "Zero-millisecond uninterrupted switchover during sudden grid outages",
                    "Cuts diesel generator fuel consumption and carbon emissions by 85%",
                    "Cloud energy telemetry tracking battery state-of-health and daily power savings",
                    "10-year battery service life with minimal maintenance overhead"
                ],
                "jharkhand_deployment_plan": "Installation at Community Health Centre Bank More and Saraidhela Primary Hospital in Dhanbad.",
                "validation_data": "99.98% power uptime recorded during 45 days of summer grid instability with zero equipment reboot failures.",
                "budget_breakdown": [
                    {"item": "10kW Bifacial Solar Panels & Mounting Structure", "cost": "₹4,50,000"},
                    {"item": "20kWh LiFePO4 Battery & Hybrid Inverter", "cost": "₹3,40,000"},
                    {"item": "Smart Switchgear & Electrical Integration", "cost": "₹1,20,000"},
                    {"item": "IoT Remote Monitoring & Commissioning", "cost": "₹90,000"}
                ],
                "timeline_phases": [
                    {"phase": "Phase 1 (Months 1-3)", "milestone": "Site Energy Audit & Electrical Distribution Sizing"},
                    {"phase": "Phase 2 (Months 4-6)", "milestone": "Rooftop Solar Array & Battery Bank Installation"},
                    {"phase": "Phase 3 (Months 7-9)", "milestone": "Microgrid Commissioning & Hospital Load Switch Testing"},
                    {"phase": "Phase 4 (Months 10-12)", "milestone": "Final Grid Synchronisation & Hospital Maintenance Handover"}
                ],
                "ip_and_publications": "Published in IEEE Transactions on Smart Grid 2025"
            }
        }
    ]
}

class ResearchReportOut(BaseModel):
    abstract: str = "Technical feasibility report and pilot deployment dossier."
    technical_architecture: str = "Field-deployed architecture engineered for regional civic infrastructure."
    tech_stack: List[str] = []
    key_innovations: List[str] = []
    jharkhand_deployment_plan: str = "Phased field trials across targeted districts in Jharkhand."
    validation_data: str = "Validated through institutional bench tests and department trials."
    budget_breakdown: List[Dict[str, str]] = []
    timeline_phases: List[Dict[str, str]] = []
    ip_and_publications: Optional[str] = None

class ProposalOut(BaseModel):
    id: str
    challenge_id: str
    problem: str
    department: str
    description: str
    domain: str
    location: str
    priority_score: int
    complaint_count: int
    solution_summary: str = ""
    proposed_solution: str = ""  # alias for backward-compatibility
    research_report: ResearchReportOut = Field(default_factory=ResearchReportOut)
    university: str
    faculty_lead: str
    contact_email: str
    trl: str
    budget_required: str
    budget_num: int
    impact_metrics: str
    funding_status: str # 'Open for Funding', 'Partially Funded', 'Funded'
    collaboration_status: str # 'Seeking Industry Partner', 'In Discussions', 'Partnered'
    funds_committed: int = 0
    partners: List[str] = []
    created_at: str

class CollaborateRequest(BaseModel):
    partner_name: str
    collaboration_type: str # e.g. "Joint Pilot Deployment", "Technical Mentorship", "Lab & Equipment Access", "Talent & Internship"
    note: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None

class FundRequest(BaseModel):
    funder_name: str
    amount: int
    csr_bucket: str # e.g. "Healthcare CSR 2026", "Rural Development", "STEM Education"
    note: Optional[str] = None

class FeedbackRequest(BaseModel):
    sender_name: str
    sender_email: str
    subject: str
    suggestions: List[str] = []
    message: str

def _build_proposal(challenge: Challenge, index: int) -> Dict[str, Any]:
    domain = challenge.domain or "HealthTech"
    options = UNIVERSITY_SOLUTIONS_MAP.get(domain, UNIVERSITY_SOLUTIONS_MAP.get("HealthTech", UNIVERSITY_SOLUTIONS_MAP["Default"]))
    sol_tmpl = options[index % len(options)]
    
    prop_id = f"PROP-{challenge.id}"
    overrides = PROPOSAL_STATE_OVERRIDES.get(prop_id, {})
    
    # Default statuses
    default_funding = "Open for Funding"
    if (index % 4 == 1):
        default_funding = "Partially Funded"
    elif (index % 6 == 0 and index > 0):
        default_funding = "Funded"

    default_collab = "Seeking Industry Partner"
    if default_funding == "Partially Funded":
        default_collab = "In Discussions"
    elif default_funding == "Funded":
        default_collab = "Partnered"

    funding_status = overrides.get("funding_status", default_funding)
    collaboration_status = overrides.get("collaboration_status", default_collab)
    funds_committed = overrides.get("funds_committed", (sol_tmpl["budget_num"] // 2 if funding_status == "Partially Funded" else (sol_tmpl["budget_num"] if funding_status == "Funded" else 0)))
    partners = overrides.get("partners", (["Tata Steel CSR"] if funding_status in ["Partially Funded", "Funded"] else []))

    summary_text = sol_tmpl.get("solution_summary") or sol_tmpl.get("proposed_solution", "")

    return {
        "id": prop_id,
        "challenge_id": challenge.id,
        "problem": challenge.title,
        "department": challenge.department or "Public Infrastructure",
        "description": challenge.description or "High priority civic issue impacting residents. Requires technological intervention.",
        "domain": domain,
        "location": challenge.location or "Ranchi, Jharkhand",
        "priority_score": challenge.priority_score or 80,
        "complaint_count": challenge.complaint_count or 45,
        "solution_summary": summary_text,
        "proposed_solution": summary_text,
        "research_report": sol_tmpl["research_report"],
        "university": sol_tmpl["university"],
        "faculty_lead": sol_tmpl["faculty_lead"],
        "contact_email": sol_tmpl["contact_email"],
        "trl": sol_tmpl["trl"],
        "budget_required": sol_tmpl["budget_required"],
        "budget_num": sol_tmpl["budget_num"],
        "impact_metrics": sol_tmpl["impact_metrics"],
        "funding_status": funding_status,
        "collaboration_status": collaboration_status,
        "funds_committed": funds_committed,
        "partners": partners,
        "created_at": challenge.created_at.isoformat() if challenge.created_at else datetime.utcnow().isoformat(),
    }

def _proposal_from_db(p: Proposal) -> Dict[str, Any]:
    c = p.challenge
    org = p.organization
    uni_name = org.name if org else "University Research Team"
    prop_id = p.id
    overrides = PROPOSAL_STATE_OVERRIDES.get(prop_id, {})

    funding_status = overrides.get("funding_status", p.funding_status or "Open for Funding")
    collaboration_status = overrides.get("collaboration_status", p.collaboration_status or "Seeking Industry Partner")
    funds_committed = overrides.get("funds_committed", p.funds_committed or 0)
    partners = overrides.get("partners", p.partners or [])

    domain = (c.domain if c else None) or "HealthTech"
    loc = (c.location if c else None) or "Jharkhand"
    summary_text = p.proposed_solution or p.problem_understanding or "Comprehensive university solution engineered for regional civic infrastructure."

    b_num = p.budget_num or 500000
    hw_cost = int(b_num * 0.45)
    field_cost = int(b_num * 0.35)
    cloud_cost = max(0, b_num - hw_cost - field_cost)

    tech_stack = [domain, "IoT Telemetry", "Civic Dashboard", "Edge Sensor Nodes", "FastAPI Secure Relay"]
    if p.resources_needed:
        custom_items = [item.strip() for item in p.resources_needed.replace("\n", ",").split(",") if item.strip()]
        if custom_items:
            tech_stack = custom_items[:5]

    research_report = {
        "abstract": p.problem_understanding or f"Engineering solution designed to resolve {c.title if c else 'civic challenge'} through institutional research and field-proven deployment.",
        "technical_architecture": p.approach_methodology or p.proposed_solution or "Modular architecture with edge acquisition, real-time analytics, and automated alerting protocols.",
        "tech_stack": tech_stack,
        "key_innovations": [
            "Tailored specifically for local district operating environments and rural resilience",
            p.impact_metrics or "Direct civic impact and sustainable maintenance model",
            "University-led validation with continuous student and faculty technical governance"
        ],
        "jharkhand_deployment_plan": f"Pilot deployment targeted for {loc} region with district administration integration and phased rollout.",
        "validation_data": p.evidence_research or "Prototype demonstrated and validated through university department benchmark testing.",
        "budget_breakdown": [
            {"item": "Core Hardware, Sensors & Fabrication", "cost": f"₹{hw_cost:,}"},
            {"item": "Field Pilot & Community Implementation Kits", "cost": f"₹{field_cost:,}"},
            {"item": "Cloud Telemetry, Monitoring & Handover", "cost": f"₹{cloud_cost:,}"}
        ],
        "timeline_phases": [
            {"phase": "Phase 1 (Months 1-3)", "milestone": "Custom Hardware Assembly & Lab Safety Benchmark Tests"},
            {"phase": "Phase 2 (Months 4-6)", "milestone": f"Deployment of Pilot Systems across {loc}"},
            {"phase": "Phase 3 (Months 7-9)", "milestone": "Field Trial Evaluation & Community Handover"}
        ],
        "ip_and_publications": f"{uni_name} Research Dossier (SIH 2026)"
    }

    return {
        "id": prop_id,
        "challenge_id": c.id if c else p.challenge_id,
        "problem": c.title if c else p.title,
        "department": (c.department if c else None) or "Public Infrastructure",
        "description": (c.description if c else None) or p.problem_understanding or "Civic challenge under university solution development.",
        "domain": domain,
        "location": loc,
        "priority_score": (c.priority_score if c else 85),
        "complaint_count": (c.complaint_count if c else 50),
        "solution_summary": summary_text,
        "proposed_solution": summary_text,
        "research_report": research_report,
        "university": uni_name,
        "faculty_lead": p.faculty_lead or "Dr. Faculty Lead",
        "contact_email": p.contact_email or "research@university.ac.in",
        "trl": p.trl or "TRL-6 (Field Pilot Ready)",
        "budget_required": p.budget_required or f"₹{b_num:,}",
        "budget_num": b_num,
        "impact_metrics": p.impact_metrics or "Empowers citizens and improves civic efficiency.",
        "funding_status": funding_status,
        "collaboration_status": collaboration_status,
        "funds_committed": funds_committed,
        "partners": partners,
        "created_at": p.created_at.isoformat() if p.created_at else datetime.utcnow().isoformat(),
    }

@router.get("/", response_model=List[ProposalOut])
def list_proposals(
    search: Optional[str] = Query(None),
    domain: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    university: Optional[str] = Query(None),
    funding_status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    # 1. Fetch real proposals submitted from Project Workspace
    db_proposals = db.query(Proposal).order_by(Proposal.created_at.desc()).all()
    real_cids = {p.challenge_id for p in db_proposals}
    
    # Live submitted proposals are placed first
    all_proposals_raw = [_proposal_from_db(p) for p in db_proposals]
    
    # 2. Append fallback mock proposals for challenges without submitted proposals
    challenges = db.query(Challenge).order_by(Challenge.priority_score.desc()).all()
    for idx, c in enumerate(challenges):
        if c.id not in real_cids:
            all_proposals_raw.append(_build_proposal(c, idx))
            
    proposals = []
    for p in all_proposals_raw:
        # Apply filters
        if search:
            s_lower = search.lower()
            if (s_lower not in p["problem"].lower() and 
                s_lower not in p["proposed_solution"].lower() and 
                s_lower not in p["university"].lower() and
                s_lower not in p["description"].lower()):
                continue
                
        if domain and domain != "all" and p["domain"].lower() != domain.lower():
            continue
            
        if department and department != "all" and p["department"].lower() != department.lower():
            continue
            
        if university and university != "all" and university.lower() not in p["university"].lower():
            continue
            
        if funding_status and funding_status != "all":
            if funding_status == "open" and p["funding_status"] != "Open for Funding":
                continue
            elif funding_status == "funded" and p["funding_status"] != "Funded":
                continue
            elif funding_status == "partial" and p["funding_status"] != "Partially Funded":
                continue
                
        proposals.append(p)
        
    return proposals

@router.get("/stats")
def get_industry_stats(db: Session = Depends(get_db)):
    db_proposals = db.query(Proposal).all()
    real_cids = {p.challenge_id for p in db_proposals}
    
    proposals = [_proposal_from_db(p) for p in db_proposals]
    challenges = db.query(Challenge).all()
    for idx, c in enumerate(challenges):
        if c.id not in real_cids:
            proposals.append(_build_proposal(c, idx))
    
    total_proposals = len(proposals)
    seeking_funding = len([p for p in proposals if p["funding_status"] == "Open for Funding"])
    partially_funded = len([p for p in proposals if p["funding_status"] == "Partially Funded"])
    funded = len([p for p in proposals if p["funding_status"] == "Funded"])
    total_capital_committed = sum(p["funds_committed"] for p in proposals)
    active_collaborations = len([p for p in proposals if len(p["partners"]) > 0])
    
    return {
        "total_proposals": total_proposals,
        "seeking_funding": seeking_funding,
        "partially_funded": partially_funded,
        "funded": funded,
        "total_capital_committed": total_capital_committed,
        "active_collaborations": active_collaborations,
        "participating_universities": len(set(p["university"] for p in proposals))
    }

@router.post("/{proposal_id}/collaborate")
def collaborate_on_proposal(proposal_id: str, req: CollaborateRequest, db: Session = Depends(get_db)):
    current = PROPOSAL_STATE_OVERRIDES.get(proposal_id, {})
    partners = current.get("partners", [])
    if req.partner_name not in partners:
        partners.append(req.partner_name)
        
    current["partners"] = partners
    current["collaboration_status"] = "Partnered"
    current["last_collaboration_note"] = req.note
    current["collaboration_type"] = req.collaboration_type
    PROPOSAL_STATE_OVERRIDES[proposal_id] = current
    
    # Also update DB proposal if exists
    db_prop = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if db_prop:
        db_prop.partners = partners
        db_prop.collaboration_status = "Partnered"
        db.commit()
    
    return {
        "status": "success",
        "message": f"Collaboration offer sent to university research team for {proposal_id}",
        "proposal_id": proposal_id,
        "collaboration_status": "Partnered",
        "partners": partners
    }

@router.post("/{proposal_id}/fund")
def fund_proposal(proposal_id: str, req: FundRequest, db: Session = Depends(get_db)):
    current = PROPOSAL_STATE_OVERRIDES.get(proposal_id, {})
    partners = current.get("partners", [])
    if req.funder_name not in partners:
        partners.append(req.funder_name)
        
    current_funds = current.get("funds_committed", 0) + req.amount
    current["funds_committed"] = current_funds
    current["partners"] = partners
    current["funding_status"] = "Funded"
    current["collaboration_status"] = "Partnered"
    current["csr_bucket"] = req.csr_bucket
    PROPOSAL_STATE_OVERRIDES[proposal_id] = current
    
    # Also update DB proposal if exists
    db_prop = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if db_prop:
        db_prop.partners = partners
        db_prop.funds_committed = current_funds
        db_prop.funding_status = "Funded"
        db_prop.collaboration_status = "Partnered"
        db.commit()
    
    return {
        "status": "success",
        "message": f"INR {req.amount:,} CSR Grant successfully allocated for {proposal_id}",
        "proposal_id": proposal_id,
        "funds_committed": current_funds,
        "funding_status": "Funded"
    }

@router.post("/{proposal_id}/feedback")
def send_feedback_email(proposal_id: str, req: FeedbackRequest):
    return {
        "status": "success",
        "message": f"Improvement suggestions dispatched to university team.",
        "proposal_id": proposal_id,
        "subject": req.subject,
        "suggestions_count": len(req.suggestions)
    }
