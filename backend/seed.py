"""
seed.py — Seeds the SQLite database with 150 realistic, Indianised complaint clusters.

Usage:
    python seed.py            # seed fresh (wipes existing data)
    python seed.py --append   # append without wiping

Each cluster has:
  - Real Delhi area coordinates (lat/lng)
  - Authentic Hinglish sample tweets
  - created_at spread over the last 7 days for velocity-chart accuracy
"""
import sys
import random
from datetime import datetime, timedelta
from pathlib import Path

# Allow running from the backend/ directory
sys.path.insert(0, str(Path(__file__).parent))

from db.database import engine, SessionLocal, Base
from db.models import Cluster, Tweet

# ── Seed control ───────────────────────────────────────────────────────────
WIPE_FIRST = "--append" not in sys.argv
random.seed(42)

# ── Delhi area → (lat, lng) ────────────────────────────────────────────────
AREAS = {
    "Rohini, North-West Delhi":         (28.7041, 77.1025),
    "Pitampura, North-West Delhi":       (28.7005, 77.1306),
    "Shalimar Bagh, North Delhi":        (28.7152, 77.1605),
    "Model Town, North Delhi":           (28.7154, 77.1930),
    "Civil Lines, North Delhi":          (28.6814, 77.2226),
    "Burari, North Delhi":               (28.7441, 77.2046),
    "Bawana, North Delhi":               (28.7919, 77.0518),
    "Mayur Vihar, East Delhi":           (28.6089, 77.2952),
    "Shahdara, East Delhi":              (28.6731, 77.2882),
    "Dilshad Garden, East Delhi":        (28.6820, 77.3108),
    "Preet Vihar, East Delhi":           (28.6463, 77.2928),
    "Geeta Colony, East Delhi":          (28.6541, 77.2791),
    "Vasundhara Enclave, East Delhi":    (28.6171, 77.3211),
    "Laxmi Nagar, East Delhi":           (28.6289, 77.2767),
    "Dwarka, South-West Delhi":          (28.5921, 77.0460),
    "Janakpuri, West Delhi":             (28.6219, 77.0878),
    "Uttam Nagar, West Delhi":           (28.6210, 77.0588),
    "Vikaspuri, West Delhi":             (28.6447, 77.0700),
    "Punjabi Bagh, West Delhi":          (28.6685, 77.1319),
    "Rajouri Garden, West Delhi":        (28.6487, 77.1202),
    "Paschim Vihar, West Delhi":         (28.6759, 77.1038),
    "Tilak Nagar, West Delhi":           (28.6401, 77.1022),
    "Connaught Place, Central Delhi":    (28.6315, 77.2167),
    "Karol Bagh, Central Delhi":         (28.6520, 77.1901),
    "Paharganj, Central Delhi":          (28.6428, 77.2173),
    "Chandni Chowk, Old Delhi":          (28.6506, 77.2300),
    "Kashmere Gate, Old Delhi":          (28.6645, 77.2290),
    "Lajpat Nagar, South Delhi":         (28.5665, 77.2433),
    "Saket, South Delhi":                (28.5244, 77.2090),
    "Nehru Place, South Delhi":          (28.5494, 77.2510),
    "Hauz Khas, South Delhi":            (28.5494, 77.2021),
    "Green Park, South Delhi":           (28.5597, 77.2082),
    "Malviya Nagar, South Delhi":        (28.5349, 77.2080),
    "Vasant Kunj, South Delhi":          (28.5196, 77.1553),
    "Vasant Vihar, South Delhi":         (28.5611, 77.1680),
    "R.K. Puram, South-West Delhi":      (28.5650, 77.1720),
    "AIIMS, South Delhi":                (28.5672, 77.2100),
    "Sarai Kale Khan, South-East Delhi": (28.5850, 77.2680),
    "Okhla, South-East Delhi":           (28.5498, 77.2783),
    "Jasola, South-East Delhi":          (28.5430, 77.2860),
}

AREA_NAMES = list(AREAS.keys())

DEPTS = ["MCD", "PWD", "DJB", "BSES", "NDMC", "DDA", "DMRC", "Traffic Police", "DTC", "Delhi Police", "Delhi Forest Dept"]

ISSUE_TEMPLATES = [
    # (problem_fmt, summary_fmt, dept, priority_range, count_range, recommended_action)
    (
        "Severe pothole — {area_short}",
        "Multiple deep craters on {area} road causing vehicle damage and near-misses. Residents have complained repeatedly.",
        "PWD", (1, 2), (80, 420),
        "Deploy emergency repair team within 24 hrs. Barricade hazardous craters immediately.",
    ),
    (
        "Waterlogging — {area_short}",
        "Heavy rain caused waterlogging on main road in {area}. Underpass submerged, commuters stranded.",
        "MCD", (1, 2), (60, 450),
        "Pump out standing water. Inspect and clear storm drain blockages.",
    ),
    (
        "Garbage not collected — {area_short}",
        "Sanitation trucks have skipped {area} for {n} days. Bins overflowing, foul smell, health hazard.",
        "MCD", (2, 3), (40, 210),
        "Schedule emergency pickup. Review collection route frequency for this zone.",
    ),
    (
        "Street lights out — {area_short}",
        "Over {pct}% of street lights non-functional on main stretch in {area}. Snatching incidents reported.",
        "BSES", (2, 3), (50, 180),
        "Night audit and immediate replacement of faulty ballasts. Coordinate with police.",
    ),
    (
        "Water supply disruption — {area_short}",
        "No piped water for {n} hours in {area}. Residents buying tankers at inflated prices.",
        "DJB", (1, 2), (70, 280),
        "Dispatch emergency tanker. Inspect main supply valve at local node.",
    ),
    (
        "Sewer overflow — {area_short}",
        "Sewer drain overflowing onto road in {area}. Foul smell and contamination risk for {n} blocks.",
        "DJB", (2, 3), (45, 160),
        "Desilting scheduled. Residents advised to avoid contact. Health dept to inspect.",
    ),
    (
        "Open manhole — {area_short}",
        "Uncovered manhole on busy road in {area} posing serious accident risk, especially at night.",
        "MCD", (1, 2), (50, 200),
        "Immediate barricading and cover installation. Night lighting required.",
    ),
    (
        "Traffic signal failure — {area_short}",
        "Signals non-functional at major intersection in {area} causing severe congestion and near-accidents.",
        "Traffic Police", (1, 1), (100, 400),
        "Manual traffic control deployed. Signal repair within 12 hrs.",
    ),
    (
        "Illegal construction — {area_short}",
        "Encroachment on public road in {area} reduced lane width causing daily traffic jams.",
        "DDA", (2, 3), (60, 190),
        "Issue notice to encroacher. Site survey required before demolition order.",
    ),
    (
        "Broken footpath — {area_short}",
        "Footpath slabs uplifted and cracked across long stretch in {area}. Multiple injury reports.",
        "NDMC", (3, 3), (40, 160),
        "Barricade hazardous sections. Schedule slab replacement in next maintenance cycle.",
    ),
    (
        "Stray dog menace — {area_short}",
        "Pack of aggressive stray dogs attacking residents near school gates and parks in {area}.",
        "MCD", (2, 3), (30, 120),
        "Deploy ABC team for sterilisation. Increase patrolling near school hours.",
    ),
    (
        "Fire hazard — exposed wires — {area_short}",
        "Dangling electric wires sparking above busy market in {area}. High fire and electrocution risk.",
        "BSES", (1, 1), (90, 320),
        "Urgent inspection and rewiring. Shut down unsafe connections immediately.",
    ),
    (
        "Noise pollution — {area_short}",
        "Loud music from {venue} exceeding legal limits till late night in {area}. Sleep deprivation for residents.",
        "Delhi Police", (3, 4), (30, 130),
        "Night patrol and strict enforcement of noise norms. Issue challans.",
    ),
    (
        "Encroachment by vendors — {area_short}",
        "Footpaths fully occupied by vendors in {area}, making pedestrian movement nearly impossible.",
        "MCD", (3, 3), (50, 180),
        "Clear encroachments and designate official vending zones.",
    ),
    (
        "Park maintenance — {area_short}",
        "Broken benches, overgrown grass and damaged lighting in {area} park. Elderly and children affected.",
        "NDMC", (4, 4), (25, 90),
        "Routine maintenance, landscaping and broken fixture replacement.",
    ),
    (
        "Bus delay / route disruption — {area_short}",
        "Buses on route through {area} consistently delayed by {n} minutes. Large crowds at stops.",
        "DTC", (3, 4), (35, 110),
        "Review route schedule and increase frequency during peak hours.",
    ),
    (
        "Metro escalator failure — {area_short}",
        "Multiple escalators out of service at metro station near {area} causing overcrowding.",
        "DMRC", (2, 2), (60, 260),
        "Immediate repair and crowd control during peak hours.",
    ),
    (
        "Air pollution — construction dust — {area_short}",
        "Unregulated construction site in {area} creating massive dust clouds. Air quality index critical.",
        "DDA", (2, 3), (55, 190),
        "Issue stop-work notice. Mandate dust suppression measures and site screening.",
    ),
    (
        "Public toilet unusable — {area_short}",
        "Dirty and broken public toilets at {area} bus stand causing inconvenience to thousands.",
        "DTC", (3, 4), (30, 110),
        "Immediate cleaning and maintenance audit. Appoint caretaker.",
    ),
    (
        "Fallen tree blocking road — {area_short}",
        "Large tree uprooted by storm blocking main road in {area}. Traffic diverted, risk of power line contact.",
        "Delhi Forest Dept", (1, 2), (50, 180),
        "Emergency tree removal team and BSES coordination if power lines affected.",
    ),
    (
        "Illegal parking — {area_short}",
        "Vehicles parked illegally blocking lanes in {area}. Traffic bottlenecks daily.",
        "Traffic Police", (3, 4), (40, 160),
        "Deploy towing vans and enforce stricter parking penalties.",
    ),
    (
        "Overflowing dustbins — {area_short}",
        "Public dustbins overflowing in {area} for days. Flies, stray animals and bad odour reported.",
        "MCD", (3, 3), (35, 140),
        "Increase bin capacity and collection frequency.",
    ),
    (
        "Road repair quality — {area_short}",
        "Freshly repaired road in {area} already broken again within {n} weeks. Contractor negligence suspected.",
        "PWD", (2, 3), (55, 200),
        "Inspect contractor work quality. Issue notice and redo repairs under warranty.",
    ),
    (
        "Stagnant water / mosquito breeding — {area_short}",
        "Stagnant water pools in {area} not draining. Dengue and malaria risk; residents alarmed.",
        "MCD", (1, 2), (65, 240),
        "Fogging operation. Fill/cover stagnant pits. Health alert to residents.",
    ),
    (
        "School road safety — {area_short}",
        "No speed breakers or crossing guards near school in {area}. Multiple near-miss accidents reported.",
        "Traffic Police", (1, 2), (70, 220),
        "Install speed breakers and crossing. Deploy traffic warden during school hours.",
    ),
]

HINGLISH_TWEET_TEMPLATES = [
    "@{dept} {area_short} mein {issue_type} ka haal dekho — {n} din se complaint kar rahe hain, koi sunne wala nahi. #DelhiComplaints",
    "Aaj phir {issue_type} wali problem {area_short} mein. @{dept} kab tak ignore karoge? #Delhi#{dept}",
    "{area_short} ke log pareshan hain {issue_type} se. {n} din ho gaye, koi action nahi. @CMODelhi @{dept} #DelhiComplaints",
    "Yaar {issue_type} {area_short} mein serious ho gayi hai. Koi bhi zimedar nahi? @{dept} please act. #DelhiComplaints",
    "Third time this month — {issue_type} in {area_short}. @{dept} wake up! #Delhi #Complaints",
    "@{dept} {area_short} complaints forwarded from local RWA. This is {n}th complaint. Still pending. #DelhiComplaints",
    "Itni garmi mein bhi {area_short} mein {issue_type}. Bache, buzurg sab affected. @{dept} emergency action lo. #DelhiComplaints",
    "{area_short} se {n}+ complaints @{dept} ko bheje — still no response. Media ko involve karna padega. #DelhiComplaints",
    "URGENT: {issue_type} near {area_short} — life risk for commuters. @{dept} @DelhiPolice please respond NOW. #DelhiComplaints",
    "Ek aur din {area_short} mein same problem — {issue_type}. Social media par aane ki zarurat kyun padti hai? @{dept} #DelhiComplaints",
]

VENUES = ["pub", "dhaba", "farmhouse party", "wedding venue", "club", "open-air market"]
ISSUE_TYPES = ["pothole", "waterlogging", "garbage issue", "street light failure", "water supply problem",
               "sewage overflow", "open manhole", "traffic chaos", "illegal construction", "footpath damage"]


def fmt(template: str, area: str, dept: str) -> str:
    area_short = area.split(",")[0]
    n = random.randint(2, 7)
    pct = random.choice([40, 50, 60, 70])
    venue = random.choice(VENUES)
    issue_type = random.choice(ISSUE_TYPES)
    return template.format(
        area=area, area_short=area_short, dept=dept,
        n=n, pct=pct, venue=venue, issue_type=issue_type,
    )


def make_tweets(cluster_id: str, area: str, dept: str, issue_type_hint: str) -> list[dict]:
    count = random.randint(2, 3)
    tweets = []
    for tmpl in random.sample(HINGLISH_TWEET_TEMPLATES, count):
        tweets.append({
            "cluster_id": cluster_id,
            "handle": f"@{area.split(',')[0].replace(' ', '')}{random.randint(10,999)}",
            "text": fmt(tmpl, area, dept),
        })
    return tweets


def seed():
    print("[seed] Creating tables…")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if WIPE_FIRST:
            print("[seed] Wiping existing data…")
            db.query(Tweet).delete()
            db.query(Cluster).delete()
            db.commit()

        now = datetime.utcnow()
        cluster_records = []
        tweet_records   = []
        used_ids        = set()

        # We'll create ~4 clusters per template, cycling through all 40 areas
        target = 150
        template_cycle = ISSUE_TEMPLATES * 10   # enough repeats
        area_pool = AREA_NAMES * 10

        for i in range(target):
            tmpl_entry = template_cycle[i % len(ISSUE_TEMPLATES)]
            prob_fmt, sum_fmt, dept, prio_range, count_range, rec_action = tmpl_entry

            area = area_pool[(i * 7 + i // len(ISSUE_TEMPLATES)) % len(AREA_NAMES)]
            area_short = area.split(",")[0]
            lat, lng = AREAS[area]
            # Add small jitter so pins don't overlap perfectly
            lat += random.uniform(-0.008, 0.008)
            lng += random.uniform(-0.008, 0.008)

            priority  = random.randint(*prio_range)
            complaint_count = random.randint(*count_range)
            rt_reach  = int(complaint_count * random.uniform(2.5, 9.0))
            trend     = random.choice(["up", "up", "stable", "down"])
            status    = random.choices(
                ["pending", "inprogress", "resolved"],
                weights=[55, 30, 15], k=1
            )[0]

            # Spread created_at over last 7 days (weighted toward recent)
            days_ago  = random.choices(range(7), weights=[30, 20, 15, 12, 10, 8, 5], k=1)[0]
            created_at = now - timedelta(
                days=days_ago,
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            cluster_id = f"CLU-{str(i + 1).zfill(4)}"
            while cluster_id in used_ids:
                cluster_id = f"CLU-{str(i + 1000 + i).zfill(4)}"
            used_ids.add(cluster_id)

            problem = fmt(prob_fmt, area, dept)
            summary = fmt(sum_fmt, area, dept)

            cluster_records.append(Cluster(
                cluster_id=cluster_id,
                priority=priority,
                problem=problem,
                summary=summary,
                location=area,
                lat=round(lat, 6),
                lng=round(lng, 6),
                department=dept,
                complaint_count=complaint_count,
                rt_reach=rt_reach,
                trend=trend,
                recommended_action=rec_action,
                time_window="Last 24 hours",
                status=status,
                created_at=created_at,
            ))

            for tw in make_tweets(cluster_id, area, dept, area_short):
                tweet_records.append(Tweet(**tw))

        db.bulk_save_objects(cluster_records)
        db.commit()
        db.bulk_save_objects(tweet_records)
        db.commit()

        total_clusters = db.query(Cluster).count()
        total_tweets   = db.query(Tweet).count()
        print(f"[seed] ✅  {total_clusters} clusters and {total_tweets} tweets seeded successfully.")

        # Summary
        from collections import Counter
        statuses = Counter(c.status for c in db.query(Cluster).all())
        depts    = Counter(c.department for c in db.query(Cluster).all())
        print("\n=== Status Breakdown ===")
        for k, v in statuses.most_common():
            print(f"  {k:<15} {v}")
        print("\n=== Department Load ===")
        for k, v in depts.most_common(8):
            print(f"  {k:<20} {v}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()