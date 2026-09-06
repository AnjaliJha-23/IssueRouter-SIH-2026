"""
api/proposals.py — University Proposed Solutions for Civic Challenges (SIH 2026 Industry Portal).
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import Challenge, Organization

router = APIRouter(prefix="/api/proposals", tags=["proposals"])

# In-memory store / registry for proposal status updates (collaborations, fundings, feedback)
# To persist across API requests in memory alongside database challenges
PROPOSAL_STATE_OVERRIDES: Dict[str, Dict[str, Any]] = {}

# University Solution templates mapped by domain / problem type
UNIVERSITY_SOLUTIONS_MAP = {
    "HealthTech": [
        {
            "university": "RIMS Ranchi",
            "faculty_lead": "Dr. S. K. Sharma (Biomedical Engineering)",
            "contact_email": "sharma.biomed@rims.ac.in",
            "proposed_solution": "IoT-enabled Solar Telemedicine Kiosk with offline ECG, vital sensors, and satellite fallback link for remote tribal primary health centres.",
            "trl": "TRL-6 (Field Pilot Ready)",
            "budget_required": "₹8,50,000",
            "budget_num": 850000,
            "impact_metrics": "Connects 40,000+ villagers to specialist doctors without 60km travel."
        },
        {
            "university": "IIT ISM Dhanbad",
            "faculty_lead": "Prof. A. K. Verma (AI & Robotics Lab)",
            "contact_email": "verma.ak@iitism.ac.in",
            "proposed_solution": "Smart Ambulance Traffic Preemption System with AI Route Guidance and automated Green Corridor signaling across high-congestion city arteries.",
            "trl": "TRL-7 (Ready for Production)",
            "budget_required": "₹14,00,000",
            "budget_num": 1400000,
            "impact_metrics": "Reduces critical emergency transit time by 42% in dense corridors."
        },
        {
            "university": "AIIMS Deoghar",
            "faculty_lead": "Dr. Meenakshi Sundaram (Community Medicine)",
            "contact_email": "m.sundaram@aiimsdeoghar.edu.in",
            "proposed_solution": "Portable Rapid Blood Storage & Cold-Chain Battery Pack with GSM temperature monitoring for rural trauma response.",
            "trl": "TRL-5 (Prototype Validated)",
            "budget_required": "₹6,20,000",
            "budget_num": 620000,
            "impact_metrics": "Zero-loss blood transportation covering 12 remote community clinics."
        }
    ],
    "BioTech": [
        {
            "university": "BIT Mesra",
            "faculty_lead": "Dr. Prerna Sengupta (Biotechnology Dept)",
            "contact_email": "psengupta@bitmesra.ac.in",
            "proposed_solution": "Low-Cost Fortified Spirulina & Millet Nutritional Supplementary wafers targeting severe acute malnutrition in tribal belts.",
            "trl": "TRL-7 (Ready for Production)",
            "budget_required": "₹5,00,000",
            "budget_num": 500000,
            "impact_metrics": "Reaches 2,500 children across 15 anganwadis within 60 days."
        },
        {
            "university": "IIT ISM Dhanbad",
            "faculty_lead": "Dr. Rajiv Ranjan (Blockchain & Cyber-Physical Systems)",
            "contact_email": "rranjan@iitism.ac.in",
            "proposed_solution": "Decentralized Pharmaceutical Traceability QR Matrix with encrypted batch verification to detect counterfeit medicine in rural dispensaries.",
            "trl": "TRL-6 (Field Pilot Ready)",
            "budget_required": "₹9,50,000",
            "budget_num": 950000,
            "impact_metrics": "Authenticates 100% of state-supplied medicine batches."
        }
    ],
    "Public Health": [
        {
            "university": "NIT Jamshedpur",
            "faculty_lead": "Dr. Rajeshwar Singh (Civil & Environmental Engineering)",
            "contact_email": "rsingh.env@nitjsr.ac.in",
            "proposed_solution": "Community-Scale Graphene-Sand Hybrid Filtration Column with automated backwashing for Arsenic and Fluoride removal from tube wells.",
            "trl": "TRL-6 (Field Pilot Ready)",
            "budget_required": "₹11,00,000",
            "budget_num": 1100000,
            "impact_metrics": "Supplies 50,000 liters/day of WHO-compliant drinking water."
        },
        {
            "university": "Kolhan University",
            "faculty_lead": "Dr. Anita Tirkey (Urban Sanitation Group)",
            "contact_email": "anita.tirkey@kolhanuniv.ac.in",
            "proposed_solution": "Automated Bio-Hazard Incineration Unit with electrostatic precipitators for zero-emission hospital waste management.",
            "trl": "TRL-5 (Prototype Validated)",
            "budget_required": "₹12,00,000",
            "budget_num": 1200000,
            "impact_metrics": "Treats 300 kg/day biomedical waste on-site, eliminating open dump hazards."
        }
    ],
    "EdTech": [
        {
            "university": "IIT ISM Dhanbad",
            "faculty_lead": "Dr. Manish Swaroop (Computer Science & Education)",
            "contact_email": "mswaroop@iitism.ac.in",
            "proposed_solution": "Solar Mesh Offline Learning Server (Santhali & Hindi localized) with gamified STEM curriculum for off-grid rural schools.",
            "trl": "TRL-7 (Ready for Production)",
            "budget_required": "₹7,50,000",
            "budget_num": 750000,
            "impact_metrics": "Equips 20 off-grid schools impacting 4,200 tribal students."
        }
    ],
    "AgriTech": [
        {
            "university": "Birsa Agricultural University",
            "faculty_lead": "Prof. B. N. Mahato (Soil Science & Agronomy)",
            "contact_email": "bnmahato@baujharkhand.org",
            "proposed_solution": "AI-Powered Optical Soil Scanner and Bio-Formulation Spray Kit to reverse soil pathogen blight in Dhanbad & Bokaro farm clusters.",
            "trl": "TRL-6 (Field Pilot Ready)",
            "budget_required": "₹6,80,000",
            "budget_num": 680000,
            "impact_metrics": "Increases per-acre crop yield by 28% for 800 smallholder farmers."
        }
    ],
    "Default": [
        {
            "university": "NIT Jamshedpur",
            "faculty_lead": "Dr. S. K. Mukherjee (Innovation Center)",
            "contact_email": "skmukherjee@nitjsr.ac.in",
            "proposed_solution": "Solar-Powered Hybrid Microgrid with IoT Inverter telemetry for uninterrupted utility operations.",
            "trl": "TRL-6 (Field Pilot Ready)",
            "budget_required": "₹10,00,000",
            "budget_num": 1000000,
            "impact_metrics": "Provides 99.9% uptime for essential public infrastructure."
        }
    ]
}

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
    proposed_solution: str
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
        "proposed_solution": sol_tmpl["proposed_solution"],
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

@router.get("/", response_model=List[ProposalOut])
def list_proposals(
    search: Optional[str] = Query(None),
    domain: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    university: Optional[str] = Query(None),
    funding_status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    challenges = db.query(Challenge).order_by(Challenge.priority_score.desc()).all()
    proposals = []
    
    for idx, c in enumerate(challenges):
        p = _build_proposal(c, idx)
        
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
    challenges = db.query(Challenge).all()
    proposals = [_build_proposal(c, idx) for idx, c in enumerate(challenges)]
    
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
def collaborate_on_proposal(proposal_id: str, req: CollaborateRequest):
    current = PROPOSAL_STATE_OVERRIDES.get(proposal_id, {})
    partners = current.get("partners", [])
    if req.partner_name not in partners:
        partners.append(req.partner_name)
        
    current["partners"] = partners
    current["collaboration_status"] = "Partnered"
    current["last_collaboration_note"] = req.note
    current["collaboration_type"] = req.collaboration_type
    PROPOSAL_STATE_OVERRIDES[proposal_id] = current
    
    return {
        "status": "success",
        "message": f"Collaboration offer sent to university research team for {proposal_id}",
        "proposal_id": proposal_id,
        "collaboration_status": "Partnered",
        "partners": partners
    }

@router.post("/{proposal_id}/fund")
def fund_proposal(proposal_id: str, req: FundRequest):
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
