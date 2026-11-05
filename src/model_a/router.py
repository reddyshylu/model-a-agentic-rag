"""Rule-based router: decides what kind of turn this is before any model runs.

Routes:
  red_flag        fixed urgent message + escalation (never generated)
  refuse_privacy  fixed refusal; only the signed-in patient's records
  out_of_scope    fixed "no information" answer + care team
  clarify         one clarifying question
  answer          grounded answer from the patient's records and/or the glossary
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import safety

LAB_ALIASES = {
    r"\balt\b": "ALT", r"\bast\b": "AST", r"\balp\b|alkaline phosphatase": "ALP", r"\bggt\b": "GGT",
    r"bilirubin": "Bilirubin Total", r"albumin": "Albumin", r"\binr\b": "INR", r"platelets?": "Platelets",
    r"\ba1c\b|hba1c|blood sugar|sugar is high|my sugar|my diabetes": "A1c", r"glucose": "Glucose",
    r"sodium": "Sodium", r"potassium": "Potassium", r"creatinine": "Creatinine", r"hemoglobin": "Hemoglobin",
    r"\bwbc\b|white blood": "WBC", r"\bafp\b": "AFP", r"\bldl\b": "LDL", r"\bhdl\b": "HDL",
    r"cholesterol": "Cholesterol Total", r"triglycerides?": "Triglycerides", r"\bbun\b": "BUN",
}
SCORE_ALIASES = {r"\bmeld\b": "meld3", r"\bfib-?\s?4\b": "fib4"}
TOPIC_PATTERNS = {
    "fibroscan": r"fibroscan|stiffness|\bcap\b",
    "ultrasound": r"ultrasound|\bscan\b|imaging",
    "meds": r"medicines?|medications?|\bmeds\b|pills?|what am i taking|prescriptions?",
    "nsaid": r"ibuprofen|advil|motrin|naproxen|aleve|nsaids?|diclofenac",
    "supplement": r"supplements?|extract|herbal|vitamin",
    "watch": r"\bsteps?\b|walk(ed)?\b|sleep|watch|fitbit|active minutes",
    "weight": r"\bmy weight\b|\bi weigh\b|\bscale\b|need to lose|weight (last|this) week|weighed",
    "note": r"\bnote\b|summari[sz]e|visit summary",
    "changes": r"what changed|changes since|since my last visit|anything new",
    "stage": r"\bmy stage\b|\bmy (fibrosis|liver) stage\b|\bam i (an? )?f[0-4]\b|which one am i|"
             r"difference between .*(fatty liver|steatosis|mash|fibrosis|cirrhosis)",
    "care_plan": r"care plan|\bmy plan\b|next visit|next appointment|follow.?up",
    "allergies": r"allerg",
}
EDUCATION_CUES = (r"\b(what is|what's|what does|what do|mean|means|how does|why|difference|explain|affect|"
                  r"is that bad|is it bad|worse|reverse|help my|safe|what happens|what if|hurt|harm)\b")
CONTINUE_OUT_OF_SCOPE = r"\b(just tell me|yes or no|so should i|then should i|come on|please just)\b"
CONSENT_CUES = r"\b(ok|okay|permission|allowed|said it is|said it's|consent|husband|wife|family)\b"
VAGUE = r"^\s*(is (it|that|this) (bad|ok|okay|normal|good)\??|what about (it|that)\??|and\??|so\??)\s*$"


@dataclass
class Route:
    kind: str
    tags: list[str] = field(default_factory=list)
    labs: list[str] = field(default_factory=list)
    scores: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    red_flag_terms: list[str] = field(default_factory=list)
    med_names: list[str] = field(default_factory=list)
    inherited: bool = False

    @property
    def has_record_topic(self) -> bool:
        return bool(self.labs or self.scores or self.topics or self.med_names)


@dataclass
class Session:
    patient_id: str
    escalation_open: bool = False
    history: list[dict] = field(default_factory=list)  # {"q": text, "route": Route}

    @property
    def last(self) -> Route | None:
        return self.history[-1]["route"] if self.history else None


def extract_topics(text: str, med_list: list[str]) -> Route:
    low = text.lower()
    r = Route(kind="answer")
    r.labs = [t for p, t in LAB_ALIASES.items() if re.search(p, low)]
    r.scores = [s for p, s in SCORE_ALIASES.items() if re.search(p, low)]
    r.topics = [t for t, p in TOPIC_PATTERNS.items() if re.search(p, low)]
    r.med_names = [m for m in med_list if m.lower() in low]
    if r.med_names and "meds" not in r.topics:
        r.topics.append("meds")
    return r


def route(text: str, session: Session, med_list: list[str], other_names: list[str]) -> Route:
    low = text.lower()
    last = session.last

    # 1) Red flags first, always. Once escalated, every turn repeats the urgent message.
    hits = safety.detect_red_flag(text)
    if hits or session.escalation_open:
        return Route(kind="red_flag", red_flag_terms=hits, inherited=not hits)

    # 2) Someone else's records (or insisting after a refusal)
    named_possessive = re.search(r"\b[A-Z][a-z]+ [A-Z][a-z]+'s\b", text)
    if safety.detect_privacy(text, other_names, session.patient_id) or named_possessive:
        return Route(kind="refuse_privacy")
    if last and last.kind == "refuse_privacy" and re.search(CONSENT_CUES, low):
        return Route(kind="refuse_privacy", inherited=True)

    # Empty or symbol-only messages: ask what they mean
    if not re.search(r"[a-z0-9]", low):
        return Route(kind="clarify")

    topics = extract_topics(text, med_list)

    # Identifiers (MRN, address, phone) are not read out in chat
    if safety.detect_identifier_request(text):
        return Route(kind="out_of_scope", tags=["identifier"])

    # 3) Scope rule (and follow-ups that push on an out-of-scope answer)
    if last and last.kind == "out_of_scope" and re.search(CONTINUE_OUT_OF_SCOPE, low):
        return Route(kind="out_of_scope", inherited=True)
    if safety.detect_out_of_scope(text):
        return Route(kind="out_of_scope")

    # 4) Follow-up with no topic of its own: inherit the previous answer's topics
    if not topics.has_record_topic and last and last.kind == "answer" and last.has_record_topic \
            and re.search(r"\b(that|it|this|one|those|them|number|last time)\b", low):
        topics.labs, topics.scores, topics.topics, topics.med_names = \
            last.labs, last.scores, list(last.topics), last.med_names
        topics.inherited = True
        if re.search(r"which one am i", low) and "stage" not in topics.topics:
            topics.topics.append("stage")

    # 5) Too vague to answer without guessing
    if re.search(VAGUE, low) and not topics.has_record_topic:
        return Route(kind="clarify")

    if topics.has_record_topic:
        topics.tags.append("record")
    if re.search(EDUCATION_CUES, low) or not topics.has_record_topic:
        topics.tags.append("education")
    if "nsaid" in topics.topics or "supplement" in topics.topics:
        topics.tags.append("safety")
    return topics
