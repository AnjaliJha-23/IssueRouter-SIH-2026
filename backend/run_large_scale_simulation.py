"""
backend/run_large_scale_simulation.py

Large-Scale Ingestion & Multi-Source Convergence Simulation (SIH 2026).
Generates 150+ realistic multi-source civic inputs (50 Tweets + 100 Citizen Reports)
across Jharkhand, passes them through the full NLP Pipeline, deduplicates and clusters them
into Master Challenges, and outputs the complete frontend dashboard payload.

Usage:
  python run_large_scale_simulation.py
"""

import sys
import os
import time
import json
import random
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure backend root is in sys.path
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from db.database import Base
from db.models import Challenge, ChallengeEvidence, ChallengeAnalysis, ChallengeRelation
from pipeline.orchestrator import process_evidence, load_all_models
from test_mock_processor import process_mock_json


# ==============================================================================
# 1. GENERATE REALISTIC MOCK DATA (50 TWEETS + 100 CITIZEN PORTAL INPUTS)
# ==============================================================================

# Core problem topics designed to test convergence, dedup, and multi-source clustering
CORE_CLUSTERS = [
    {
        "topic": "Namkum PHC Doctor & Antivenom Shortage",
        "district": "Ranchi",
        "block": "Namkum",
        "domain": "Healthcare",
        "lat": 23.3441, "lng": 85.3096,
        "citizen_templates": [
            "Primary Health Center in Namkum, Ranchi has no doctor on duty and acute shortage of antivenom and emergency medicines for 2 months.",
            "Namkum PHC hospital is locked during daytime. Villagers in Ranchi district have no access to basic medicines and emergency staff.",
            "Critical lack of antivenom at Namkum Primary Health Centre in Ranchi. Snake bite patients are being referred to RIMS without first aid.",
            "Health center in Namkum block without regular doctor for past 60 days. Patients suffering in Ranchi.",
            "No medical officer present at PHC Namkum Ranchi. Pharmacist distributing medicines without prescription.",
            "Namkum community health clinic infrastructure dilapidated, no female doctor and absence of basic testing kits in Ranchi.",
            "Emergency ward in Namkum PHC Ranchi not operational after 4 PM due to severe doctor shortage."
        ],
        "tweet_templates": [
            "@JharkhandGovt @HealthDeptJH Namkum PHC clinic closed without doctors or medicines. Urgent intervention needed in Ranchi! #NamkumHealth",
            "Urgent! No antivenom at Namkum PHC #Ranchi. A farmer was turned away today. Please take action @dc_ranchi @MoHFW_INDIA",
            "Namkum health centre has become a ghost building. No doctors, no medicines for months. Ranchi healthcare is failing! #JharkhandHealth",
            "@CMO_Jharkhand Doctors absent at Namkum PHC Ranchi again today. When will rural health improve?",
            "Snake bite victims dying due to zero antivenom stock in Namkum PHC, Ranchi! Investigate immediately @HealthDeptJH"
        ]
    },
    {
        "topic": "Jharia Borewell Contamination & Drinking Water Crisis",
        "district": "Dhanbad",
        "block": "Jharia",
        "domain": "Water & Sanitation",
        "lat": 23.7419, "lng": 86.4132,
        "citizen_templates": [
            "Severe drinking water scarcity in Jharia, Dhanbad. Deep borewells dried up and pipeline contaminated with coal slurry.",
            "Drinking water supplied in Jharia block Dhanbad is black and emitting foul chemical odor. Waterborne diseases spreading.",
            "Water pipeline broken in Jharia coal belt Dhanbad for 3 weeks. Over 500 families drinking polluted tanker water.",
            "Groundwater in Jharia Dhanbad heavily contaminated with heavy metals. Urgent piped water connection required.",
            "No clean drinking water in residential colonies of Jharia Dhanbad. Water filtration plant is non-functional.",
            "Borewells running completely dry in Jharia, Dhanbad. Women walking 4 km daily to fetch water from mine pits.",
            "Water supply disrupted in Jharia town Dhanbad due to pipeline burst near main market."
        ],
        "tweet_templates": [
            "People in Jharia Dhanbad are forced to drink black coal-contaminated water! @dc_dhanbad where is the clean water? #JhariaWaterCrisis",
            "@JharkhandGovt Jharia Dhanbad water crisis worsening. Borewells dry, no water tankers sent. Help! #Dhanbad",
            "Severe water shortage in Jharia #Dhanbad. Toxic water coming from taps. Immediate pipeline repair needed @MinJalShakti",
            "Children falling sick in Jharia Dhanbad due to contaminated drinking water supply. Urgent intervention requested #DhanbadWater"
        ]
    },
    {
        "topic": "Kanke Culvert Collapse & Broken Road",
        "district": "Ranchi",
        "block": "Kanke",
        "domain": "Infrastructure/Transport",
        "lat": 23.4325, "lng": 85.3218,
        "citizen_templates": [
            "Broken culvert and washed out road on main arterial route in Kanke block, Ranchi. Heavy vehicles causing road collapse.",
            "Main bridge culvert connecting Kanke rural market to Ranchi city severely damaged and unsafe for commuters.",
            "Deep craters and collapsed culvert near Kanke block office Ranchi. Multiple two-wheeler accidents recorded this week.",
            "Bridge road cave-in on Kanke road Ranchi. School buses stranded and ambulances taking 15 km detour.",
            "Urgent repair needed for broken culvert in Kanke Ranchi before monsoon cuts off 12 villages."
        ],
        "tweet_templates": [
            "Huge danger! Main culvert on Kanke road Ranchi has caved in. Massive traffic jam & risk of fatal accident @dc_ranchi @JharkhandGovt",
            "Kanke Ranchi road completely broken near culvert. PWD ignoring complaints for 3 weeks. #RanchiRoads #TrafficHazard",
            "@TrafficRanchi Road collapsed at Kanke culvert, Ranchi. Please divert vehicles before disaster strikes!"
        ]
    },
    {
        "topic": "Bokaro High School Science Teachers & Lab Equipment Shortage",
        "district": "Bokaro",
        "block": "Chas",
        "domain": "Education",
        "lat": 23.6364, "lng": 86.1793,
        "citizen_templates": [
            "Government High School in Chas, Bokaro has no physics and chemistry teacher for class 9 and 10 since last session.",
            "Science laboratory in Chas government school Bokaro is completely locked with no equipment, chemicals, or lab assistants.",
            "Students in Chas block Bokaro government school failing board exams due to vacancy in Mathematics and Science faculty.",
            "No computers or science teachers in upgraded high school in Chas, Bokaro. Over 400 rural students affected.",
            "Poor educational infrastructure and faculty shortage in government high school Chas Bokaro."
        ],
        "tweet_templates": [
            "Govt High School Chas #Bokaro operating without science and maths teachers for 1 year! What about rural education? @EduMinOfIndia @JharkhandGovt",
            "@dc_bokaro Over 400 students in Chas school Bokaro have no lab or science faculty. Please deploy teachers immediately! #JharkhandEducation",
            "Science lab locked, no teachers in Chas Bokaro high school. Save student futures! #BokaroEdu"
        ]
    },
    {
        "topic": "Deoghar Jasidih Industrial Feeder Frequent Power Outages",
        "district": "Deoghar",
        "block": "Jasidih",
        "domain": "Energy",
        "lat": 24.5167, "lng": 86.6500,
        "citizen_templates": [
            "Frequent 14-hour unscheduled power cuts in Jasidih industrial and residential area, Deoghar. Small manufacturing units shutting down.",
            "Transformer burnt in Jasidih block Deoghar not replaced for 5 days. Food processing units suffering heavy losses.",
            "Low voltage and erratic power tripping in Jasidih Deoghar damaging industrial machinery and domestic appliances.",
            "Electric sub-station in Jasidih Deoghar suffering frequent transmission line breakdown. No backup power supply.",
            "Massive electricity crisis in Jasidih Deoghar area causing economic distress for local artisans and MSMEs."
        ],
        "tweet_templates": [
            "Jasidih #Deoghar facing 12+ hours daily blackout! Small businesses are ruined. Fix the power grid @JBVNL_HQ @dc_deoghar",
            "Industrial units in Jasidih Deoghar shutting down due to continuous power failure. Urgent transformer replacement needed! #DeogharPower",
            "@JharkhandGovt Darkness in Jasidih Deoghar for 4 straight days. JBVNL officials unresponsive. #ElectricityCrisis"
        ]
    },
    {
        "topic": "Adityapur Industrial Waste & River Pollution",
        "district": "East Singhbhum",
        "block": "Golmuri",
        "domain": "Environment",
        "lat": 22.7844, "lng": 86.1686,
        "citizen_templates": [
            "Untreated toxic industrial effluent being discharged directly into Subarnarekha river near Golmuri, East Singhbhum.",
            "Heavy air and water pollution from unmonitored chemical factories in industrial zone of East Singhbhum.",
            "Illegal dumping of hazardous solid industrial waste in open fields near Golmuri East Singhbhum causing groundwater toxicity.",
            "River water turning toxic black with chemical foam near East Singhbhum industrial discharge point.",
            "Severe respiratory issues in residential colonies adjacent to chemical plants in East Singhbhum."
        ],
        "tweet_templates": [
            "Subarnarekha river dying due to direct chemical effluent discharge in #EastSinghbhum! Stop industrial pollution @JSPCB_JH @moefcc",
            "Toxic chemical fumes choking residents in Golmuri East Singhbhum every night. Strict environmental audit needed! #PollutionAlert",
            "@dc_eastsinghbhum Industrial waste dumping poisoning drinking groundwater in Golmuri. Urgent inspection required!"
        ]
    },
    {
        "topic": "Hazaribagh Forest Fringe Human-Elephant Conflict",
        "district": "Hazaribagh",
        "block": "Ichak",
        "domain": "Rural Livelihoods",
        "lat": 24.0833, "lng": 85.4500,
        "citizen_templates": [
            "Wild elephant herd damaged standing paddy crops and destroyed 8 farmer huts in Ichak block, Hazaribagh.",
            "Lack of solar fencing and rapid forest fragmentation causing recurring human-wildlife conflict in Ichak Hazaribagh.",
            "Farmers in Ichak Hazaribagh suffering complete livelihood loss due to nightly wild elephant herd attacks.",
            "Forest department compensation delayed by 6 months for crop damage in Ichak block Hazaribagh.",
            "Urgent request for elephant tracking sensors and anti-depredation squad in Ichak Hazaribagh."
        ],
        "tweet_templates": [
            "Elephants destroy 10 acres of crops in Ichak #Hazaribagh overnight. Farmers helpless! Forest dept must deploy team @HazaribaghForest",
            "@JharkhandGovt Recurring elephant attacks in Ichak Hazaribagh destroying rural livelihoods. Need solar fences & quick compensation! #WildlifeConflict"
        ]
    },
    {
        "topic": "Palamu Daltonganj Solar Micro-Grid Grid Failure",
        "district": "Palamu",
        "block": "Daltonganj",
        "domain": "Energy",
        "lat": 24.0333, "lng": 84.0667,
        "citizen_templates": [
            "Rural solar mini-grid in Daltonganj block Palamu has broken battery storage. Solar street lights inactive for 3 months.",
            "Solar powered water pump non-operational in Daltonganj Palamu leaving agricultural fields parched.",
            "Defective solar inverters in off-grid tribal villages of Daltonganj, Palamu. Contractor not providing maintenance."
        ],
        "tweet_templates": [
            "Solar microgrid in Daltonganj #Palamu abandoned without battery replacement. Tribal village in darkness again @MNREindia @dc_palamu",
            "@JharkhandGovt Palamu Daltonganj solar water irrigation system broken for 6 months. Farmers facing drought! #Palamu"
        ]
    }
]

# Additional distinct societal issues across other districts (Dumka, Ramgarh, Giridih, Latehar, etc.)
DISTINCT_ISSUES = [
    {
        "district": "Dumka", "block": "Dumka", "domain": "Education",
        "citizen": "Primary school building in Dumka rural lacks functional toilets for girl students, leading to dropouts.",
        "tweet": "No toilets for girls in Dumka rural primary school! Basic dignity denied. Fix school infra @dc_dumka #Dumka"
    },
    {
        "district": "Ramgarh", "block": "Patratu", "domain": "Infrastructure/Transport",
        "citizen": "Patratu valley road in Ramgarh district has damaged crash barriers and missing solar cat-eyes, risking tourist accidents.",
        "tweet": "Dangerous turns on Patratu road #Ramgarh with broken safety barriers. Life hazard! @RamgarhAdmin"
    },
    {
        "district": "Giridih", "block": "Giridih", "domain": "Environment",
        "citizen": "Unregulated mica dump runoff polluting local agricultural soil and ponds in Giridih district.",
        "tweet": "Mica mining waste poisoning water ponds in #Giridih. Immediate ecological survey needed! @JSPCB_JH"
    },
    {
        "district": "Latehar", "block": "Latehar", "domain": "Healthcare",
        "citizen": "No emergency ambulance available at Latehar district hospital for critical maternal transfer cases.",
        "tweet": "Latehar hospital ambulance out of service! Pregnant woman transported on cot. Shameful! @HealthDeptJH #Latehar"
    },
    {
        "district": "Ranchi", "block": "Ratu", "domain": "Urban Development",
        "citizen": "Open drainage overflow flooding residential streets and breeding mosquitoes in Ratu block, Ranchi.",
        "tweet": "Ratu Ranchi streets submerged in sewer water. Dengue outbreak risk high! Clear drains @RanchiMunicipal"
    },
    {
        "district": "Dhanbad", "block": "Govindpur", "domain": "Public Administration",
        "citizen": "Block office in Govindpur Dhanbad has 3-month backlog for land mutation and caste certificate verification.",
        "tweet": "Endless queue and delays for caste certificates at Govindpur block #Dhanbad. System reform needed @dc_dhanbad"
    },
    {
        "district": "Khunti", "block": "Khunti", "domain": "Rural Livelihoods",
        "citizen": "Lac and minor forest produce procurement center in Khunti offering prices below minimum support price.",
        "tweet": "Tribal lac farmers in #Khunti being exploited by middlemen below MSP. Set up govt mandi @TRIFEDJharkhand"
    },
    {
        "district": "Godda", "block": "Godda", "domain": "Energy",
        "citizen": "High tension electric wire hanging dangerously low over farming fields in Godda block, Godda district.",
        "tweet": "Sagging 11kV live power cable over fields in Godda! Fatal electrocution risk to farmers @JBVNL_HQ #Godda"
    }
]


def build_150_dataset():
    """Generates an array of at least 50 tweets and 100 citizen reports (150+ total)."""
    dataset = []
    
    # 1. Expand Core Clusters (creates dense clusters for multi-source convergence)
    for cluster in CORE_CLUSTERS:
        # Add all citizen templates
        for text in cluster["citizen_templates"]:
            dataset.append({
                "source": "citizen",
                "raw_text": text,
                "submitted_lat": cluster["lat"] + random.uniform(-0.01, 0.01),
                "submitted_lng": cluster["lng"] + random.uniform(-0.01, 0.01),
                "expected_topic": cluster["topic"],
                "expected_district": cluster["district"],
                "expected_domain": cluster["domain"]
            })
        # Add all tweet templates
        for text in cluster["tweet_templates"]:
            dataset.append({
                "source": "twitter",
                "raw_text": text,
                "submitted_lat": None,
                "submitted_lng": None,
                "expected_topic": cluster["topic"],
                "expected_district": cluster["district"],
                "expected_domain": cluster["domain"]
            })

    # 2. Add Distinct Issue items
    for item in DISTINCT_ISSUES:
        dataset.append({
            "source": "citizen",
            "raw_text": item["citizen"],
            "submitted_lat": 23.5,
            "submitted_lng": 85.5,
            "expected_topic": f"{item['district']} {item['domain']} Issue",
            "expected_district": item["district"],
            "expected_domain": item["domain"]
        })
        dataset.append({
            "source": "twitter",
            "raw_text": item["tweet"],
            "submitted_lat": None,
            "submitted_lng": None,
            "expected_topic": f"{item['district']} {item['domain']} Issue",
            "expected_district": item["district"],
            "expected_domain": item["domain"]
        })

    # 3. Scale up to ensure at least 100 citizen inputs + 50 tweets (150+ total)
    citizen_count = sum(1 for d in dataset if d["source"] == "citizen")
    tweet_count = sum(1 for d in dataset if d["source"] == "twitter")

    # Generate slight variations of citizen reports to reach >= 100
    variation_prefixes = [
        "Urgent report from residents: ",
        "Submitting on behalf of village committee: ",
        "Repeated grievance: ",
        "Public welfare notice: ",
        "Formal citizen petition: "
    ]
    
    idx = 0
    while citizen_count < 100:
        base_item = random.choice([d for d in dataset if d["source"] == "citizen"])
        prefix = variation_prefixes[idx % len(variation_prefixes)]
        dataset.append({
            "source": "citizen",
            "raw_text": f"{prefix}{base_item['raw_text']}",
            "submitted_lat": base_item.get("submitted_lat"),
            "submitted_lng": base_item.get("submitted_lng"),
            "expected_topic": base_item["expected_topic"],
            "expected_district": base_item["expected_district"],
            "expected_domain": base_item["expected_domain"]
        })
        citizen_count += 1
        idx += 1

    # Generate slight variations of tweets to reach >= 50
    tweet_hashtags = [" #JharkhandNews", " #PublicGrievance", " #CivicAlert", " #ImmediateAction"]
    idx = 0
    while tweet_count < 50:
        base_item = random.choice([d for d in dataset if d["source"] == "twitter"])
        hashtag = tweet_hashtags[idx % len(tweet_hashtags)]
        dataset.append({
            "source": "twitter",
            "raw_text": f"{base_item['raw_text']}{hashtag}",
            "submitted_lat": None,
            "submitted_lng": None,
            "expected_topic": base_item["expected_topic"],
            "expected_district": base_item["expected_district"],
            "expected_domain": base_item["expected_domain"]
        })
        tweet_count += 1
        idx += 1

    # Shuffle to simulate random asynchronous arrival
    random.seed(42)
    random.shuffle(dataset)
    return dataset


# ==============================================================================
# 2. RUN SIMULATION & AGGREGATE CLUSTER INTELLIGENCE
# ==============================================================================

def run_large_scale_simulation():
    print("=" * 80)
    print("      ISSUEROUTER — LARGE SCALE INGESTION & CLUSTERING SIMULATION")
    print("=" * 80)
    
    dataset = build_150_dataset()
    total_citizens = sum(1 for d in dataset if d["source"] == "citizen")
    total_tweets = sum(1 for d in dataset if d["source"] == "twitter")
    print(f"\n[Generated Dataset]: Total {len(dataset)} items ({total_citizens} Citizen Reports + {total_tweets} Tweets)")

    # Initialize in-memory database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    print("\n[Step 1/3] Warming up NLP models (BART MNLI, spaCy Gazetteer, all-MiniLM)...")
    t0 = time.time()
    load_all_models()
    print(f"  --> Models initialized in {time.time() - t0:.2f}s\n")

    print(f"[Step 2/3] Processing {len(dataset)} items through Ingestion -> NLP Pipeline...")
    action_counts = {"new_challenge": 0, "link": 0, "flag_related": 0}
    
    start_sim = time.time()
    for i, item in enumerate(dataset, 1):
        res = process_evidence(item, db)
        action_counts[res["action"]] = action_counts.get(res["action"], 0) + 1
        
        if i % 25 == 0 or i == len(dataset):
            print(f"  Processed {i:3d}/{len(dataset)} items... (New: {action_counts['new_challenge']}, Linked/Merged: {action_counts['link']}, Flagged: {action_counts['flag_related']})")

    total_time = time.time() - start_sim
    print(f"\n  --> Completed 150+ ingestion pipeline runs in {total_time:.2f}s (Avg: {(total_time / len(dataset))*1000:.1f}ms per item)\n")

    # ==============================================================================
    # 3. BUILD COMPLETE FRONTEND DASHBOARD PAYLOAD
    # ==============================================================================
    print("[Step 3/3] Generating Consolidated Clustered Dashboard Payload...")

    challenges = db.query(Challenge).order_by(Challenge.priority_score.desc()).all()
    dashboard_payload = {
        "_meta": {
            "total_raw_inputs_processed": len(dataset),
            "citizen_reports_count": total_citizens,
            "tweets_count": total_tweets,
            "master_challenges_created": len(challenges),
            "auto_linked_duplicates": action_counts["link"],
            "flagged_related_duplicates": action_counts["flag_related"],
            "simulation_completed_at": datetime.now(timezone.utc).isoformat()
        },
        "challenges": []
    }

    print("\n" + "=" * 80)
    print("                MASTER CHALLENGE CLUSTERS CREATED (FOR DASHBOARD)")
    print("=" * 80)
    print(f"{'Challenge ID':<13} | {'Domain':<18} | {'District':<12} | {'Evidences':<9} | {'Priority':<8} | Title")
    print("-" * 80)

    for c in challenges:
        evidences = db.query(ChallengeEvidence).filter(ChallengeEvidence.challenge_id == c.id).all()
        analysis = db.query(ChallengeAnalysis).filter(ChallengeAnalysis.challenge_id == c.id).first()
        relations = db.query(ChallengeRelation).filter(ChallengeRelation.source_challenge_id == c.id).all()

        citizen_ev = sum(1 for e in evidences if e.source == "citizen")
        tweet_ev = sum(1 for e in evidences if e.source == "twitter")

        print(f"{c.id:<13} | {c.domain or 'General':<18} | {c.district or 'Unknown':<12} | {len(evidences):>2d} ({citizen_ev}C,{tweet_ev}T) | {c.priority_score:>3d}/100  | {c.title[:30]}")

        challenge_data = {
            "id": c.id,
            "title": c.title,
            "description": c.ai_generated_summary or c.official_description or "",
            "domain": c.domain,
            "subdomain": analysis.subdomain if analysis else None,
            "status": c.status or "pending_verification",
            "priority_score": c.priority_score,
            "location": c.location,
            "district": c.district,
            "block": c.block,
            "lat": c.lat,
            "lng": c.lng,
            "complaint_count": len(evidences),
            "source_breakdown": {
                "citizen_count": citizen_ev,
                "twitter_count": tweet_ev
            },
            "trend": analysis.trend if analysis else "stable",
            "ai_analysis": {
                "priority_breakdown": {
                    "score": analysis.priority_score if analysis else c.priority_score,
                    "factors": analysis.priority_factors if analysis else {},
                    "explanation": analysis.explanation if analysis else ""
                },
                "domain_scores": analysis.domain_scores if analysis else {},
                "related_challenges": [
                    {"target_id": r.target_challenge_id, "similarity_score": r.similarity_score}
                    for r in relations
                ]
            },
            "evidences": [
                {
                    "id": ev.id,
                    "source": ev.source,
                    "clean_text": ev.clean_text,
                    "raw_text": ev.raw_text,
                    "submitted_lat": ev.submitted_lat,
                    "submitted_lng": ev.submitted_lng,
                    "created_at": ev.created_at.isoformat() if hasattr(ev, "created_at") and ev.created_at else datetime.now(timezone.utc).isoformat()
                } for ev in evidences
            ]
        }
        dashboard_payload["challenges"].append(challenge_data)

    # Save to disk for frontend consumption
    output_filepath = os.path.join(BACKEND_DIR, "dashboard_clustered_output.json")
    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(dashboard_payload, f, indent=2)

    print("=" * 80)
    print(f"\n[Success] Processed {len(dataset)} inputs into {len(challenges)} Master Challenge Clusters.")
    print(f"[Success] Dashboard-Ready Payload saved to: {output_filepath}")
    print("=" * 80)


if __name__ == "__main__":
    run_large_scale_simulation()
