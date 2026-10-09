
import re
from difflib import SequenceMatcher

CATEGORIES = {
    "IT": "IT Support",
    "Plumbing": "Plumbing and Water Facilities",
    "Electrical": "Electrical Maintenance",
    "Classroom": "Classroom Maintenance",
    "Cleaning": "Housekeeping",
    "Safety": "Campus Safety and Security",
    "Pest Control": "Pest Control",
    "Other": "General Campus Support",
}

# Phrases are intentionally explicit to reduce accidental matches.
CATEGORY_RULES = {
    "IT": [
        "wifi", "wi-fi", "internet", "network", "router",
        "projector", "computer", "laptop", "printer",
        "login", "password", "software", "website",
        "portal", "server", "keyboard", "mouse",
        "smart board", "display not working",
    ],
    "Plumbing": [
        "water leak", "leaking pipe", "pipe burst",
        "tap", "faucet", "toilet", "flush", "drain",
        "blocked drain", "clogged drain", "sewage",
        "water supply", "no water", "low water pressure",
        "overflowing sink", "broken pipe", "flooding",
        "water cooler", "drinking water",
    ],
    "Electrical": [
        "electrical", "electricity", "power outage",
        "power cut", "power failure", "light", "lights",
        "bulb", "tube light", "fan", "switch", "socket",
        "outlet", "wiring", "exposed wire", "sparking",
        "short circuit", "circuit breaker", "electric shock",
        "burning smell", "smoke from socket",
    ],
    "Classroom": [
        "classroom", "desk", "chair", "bench", "blackboard",
        "whiteboard", "door", "window", "ceiling",
        "broken furniture", "projector screen",
        "air conditioner", "ac not working", "air conditioning",
        "lecture hall", "lab equipment", "laboratory equipment",
    ],
    "Cleaning": [
        "cleaning", "dirty", "garbage", "trash", "rubbish",
        "waste", "dust", "spill", "messy", "smelly",
        "bad smell", "overflowing bin", "full bin",
        "washroom cleaning", "restroom cleaning",
    ],
    "Safety": [
        "security", "unsafe", "harassment", "threat",
        "intruder", "unauthorized person", "broken lock",
        "suspicious activity", "emergency exit",
        "blocked exit", "fire alarm", "fire extinguisher",
        "theft", "missing property",
    ],
    "Pest Control": [
        "mosquito", "mosquitoes", "rats", "rat infestation",
        "mouse infestation", "cockroach", "cockroaches",
        "ants infestation", "termites", "pest", "pests",
        "bed bugs", "snake", "stray dog",
    ],
}

HIGH_PRIORITY_PHRASES = [
    "fire", "flames", "smoke", "sparking", "electric shock",
    "exposed wire", "burning smell", "gas leak", "gas smell",
    "pipe burst", "major flooding", "severe flooding",
    "ceiling collapse", "ceiling is collapsing",
    "structural collapse", "person trapped", "medical emergency",
    "serious injury", "emergency exit blocked",
]

MEDIUM_PRIORITY_PHRASES = [
    "leak", "leaking", "not working", "broken", "blocked",
    "overflow", "no water", "power outage", "power cut",
    "internet down", "wifi down", "cannot access",
    "can't access", "unable to access", "infestation",
    "door will not lock", "door won't lock",
]

URGENT_WORDS = {
    "urgent", "urgently", "emergency", "immediately",
    "dangerous", "danger", "critical", "severe",
}

STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "in",
    "at", "on", "to", "of", "and", "for", "my", "our",
    "please", "there", "this", "that", "it", "not",
    "working", "broken", "issue", "problem", "near",
}


def normalize_text(value):
    """Normalize text for matching without discarding useful words."""
    value = str(value or "").lower().strip()
    value = value.replace("wi fi", "wifi")
    value = re.sub(r"[\-_]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value


def contains_phrase(text, phrase):
    """Match a phrase on word boundaries to avoid partial-word matches."""
    text = normalize_text(text)
    phrase = normalize_text(phrase)
    if not text or not phrase:
        return False

    pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
    return bool(re.search(pattern, text))


def classify_complaint(complaint):
    """
    Return category, confidence, and scoring details.
    Confidence is a heuristic score, not a statistical probability.
    """
    text = normalize_text(complaint)
    scores = {}

    for category, phrases in CATEGORY_RULES.items():
        score = 0
        matched = []

        for phrase in phrases:
            if contains_phrase(text, phrase):
                # Longer, more specific phrases carry more weight.
                weight = 3 if len(phrase.split()) >= 2 else 2
                score += weight
                matched.append(phrase)

        scores[category] = {
            "score": score,
            "matched": matched,
        }

    ranked = sorted(
        scores.items(),
        key=lambda item: item[1]["score"],
        reverse=True,
    )
    best_category, best_details = ranked[0]
    best_score = best_details["score"]
    second_score = ranked[1][1]["score"] if len(ranked) > 1 else 0

    if best_score == 0:
        return {
            "category": "Other",
            "confidence": 0.20,
            "matched_terms": [],
            "needs_review": True,
            "reason": "No category keywords matched.",
        }

    # A close tie can mean the complaint covers multiple departments.
    ambiguous = second_score > 0 and best_score == second_score
    confidence = min(
        0.98,
        0.50 + (best_score * 0.08) + ((best_score - second_score) * 0.06),
    )

    return {
        "category": best_category,
        "confidence": round(confidence, 2),
        "matched_terms": best_details["matched"],
        "needs_review": ambiguous or confidence < 0.60,
        "reason": (
            "Several categories matched equally."
            if ambiguous
            else "Matched complaint keywords."
        ),
    }


def calculate_priority(complaint, category):
    text = normalize_text(complaint)

    def has_any(phrases):
        return any(contains_phrase(text, p) for p in phrases)

    # Immediate campus safety hazards.
    emergency_phrases = [
        "fire", "flames", "smoke", "gas leak", "gas smell",
        "electric shock", "sparking", "exposed wire",
        "burning smell", "pipe burst", "major flooding",
        "severe flooding", "ceiling collapse",
        "structural collapse", "person trapped",
        "medical emergency", "serious injury",
        "emergency exit blocked", "blocked fire exit",
        "chemical spill", "chemical fumes",
    ]

    if has_any(emergency_phrases):
        return "High"

    # Laboratory electrical/power failures can affect equipment
    # and may present a safety risk. Flag them for prompt review.
    lab_terms = [
        "lab", "laboratory", "science lab",
        "computer lab", "research lab",
    ]
    power_terms = [
        "power failure", "power outage", "power cut",
        "no electricity", "electricity is gone",
        "power supply", "electricity supply",
        "power not working", "no power",
    ]

    if has_any(lab_terms) and has_any(power_terms):
        return "High"

    # Washroom water failures affect sanitation and hygiene.
    washroom_terms = [
        "washroom", "restroom", "bathroom", "toilet",
    ]
    water_terms = [
        "no water", "water supply", "water shortage",
        "water is unavailable", "no running water",
        "water not available", "water stopped",
    ]

    if has_any(washroom_terms) and has_any(water_terms):
        return "High"

    # Other potentially dangerous electrical faults.
    electrical_hazards = [
        "exposed wire", "loose live wire", "sparking",
        "electric shock", "short circuit", "burning smell",
    ]

    if category == "Electrical" and has_any(electrical_hazards):
        return "High"

    # Serious security incidents.
    security_emergencies = [
        "intruder", "person trapped", "physical assault",
        "active threat", "emergency exit blocked",
    ]

    if category == "Safety" and has_any(security_emergencies):
        return "High"

    # Urgency words can raise a complaint's priority.
    if has_any([
        "urgent", "urgently", "emergency", "immediately",
        "critical", "severe", "dangerous",
    ]):
        return "High"

    # Important maintenance issues that need attention soon.
    medium_phrases = [
        "leak", "leaking", "not working", "broken",
        "blocked", "overflow", "no water",
        "power outage", "power cut", "internet down",
        "wifi down", "unable to access", "infestation",
        "door will not lock", "door won't lock",
    ]

    if has_any(medium_phrases):
        return "Medium"

    if category in {"IT", "Plumbing", "Electrical", "Safety"}:
        return "Medium"

    return "Low"



def assign_department(category):
    return CATEGORIES.get(category, CATEGORIES["Other"])


def detect_missing_information(complaint, location):
    missing = []

    if len(str(complaint or "").strip()) < 8:
        missing.append("Please describe the issue in at least 8 characters.")

    if not str(location or "").strip():
        missing.append("Add a building, block, room, or campus location.")

    text = normalize_text(complaint)
    if text and len(text.split()) < 3:
        missing.append(
            "Add a little more detail about what is wrong."
        )

    return missing


def validate_analysis(data, complaint, location):
    """
    Treat classifier output as untrusted.
    Recompute category/priority/team from the actual complaint.
    """
    complaint = re.sub(r"\s+", " ", str(complaint or "")).strip()
    location = re.sub(r"\s+", " ", str(location or "")).strip()

    classification = classify_complaint(complaint)
    category = classification["category"]

    return {
        "issue": complaint[:500],
        "category": category,
        "location": location[:160] if location else "Not provided",
        "priority": calculate_priority(complaint, category),
        "assigned_team": assign_department(category),
        "confidence": classification["confidence"],
        "matched_terms": classification["matched_terms"],
        "needs_review": classification["needs_review"],
        "reason": classification["reason"],
        "missing_info": detect_missing_information(complaint, location),
        "ai_mode": "Offline rule-based decision engine",
    }
