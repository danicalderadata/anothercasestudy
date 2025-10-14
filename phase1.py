import re, json
from typing import List, Dict

EMAIL_RE = re.compile(r"[\w._%+-]+@[\w.-]+\.[A-Za-z]{2,}")

def midpoint_k(s):
  # handles 12–15k, 12-15k, 12 k to 15 k
  m = re.search(r"(\d+[\.,]?\d*)\s*[kK]?\s*[–-]\s*(\d+[\.,]?\d*)\s*[kK]?", s)
  if not m: 
    return 0
  a, b = float(m.group(1)), float(m.group(2))
  return int(((a + b) / 2) * (1000 if 'k' in s.lower() else 1))

def parse_brief(txt: str) -> dict:
  txt = txt or ""

  country = "Peru" if re.search(r"\bPeru\b", txt, re.I) else ""

  city_matches = re.findall(r"Lima|Arequipa", txt, re.I)
  cities: List[str] = sorted({c.title() for c in city_matches})

  need = "AI RFP flow" if re.search(r"RFP|proposal", txt, re.I) else ""

  langs: List[str] = []
  if re.search(r"\b(Spanish|ES)\b", txt, re.I):
    langs.append("es")
  if re.search(r"\b(English|EN)\b", txt, re.I):
    langs.append("en")

  m_weeks = re.search(r"(\d+)\s*weeks?", txt, re.I)
  weeks = int(m_weeks.group(1)) if m_weeks else 0

  budget = midpoint_k(txt)
  if budget == 0:
    budget = 13500

  m_email = EMAIL_RE.search(txt)
  email = m_email.group(0) if m_email else ""

return = {
  "company": "Retail Group",
  "country": country,
  "cities": cities,
  "need": need,
  "languages": langs,
  "budget_usd": budget,
  "timeline_weeks": weeks,
  "contact_email": email,
  }

if __name__ == "__main__":
  messy = ("We’re a Peru-based retail group opening pop-ups in Lima and Arequipa. Need an AI-driven RFP/proposal flow (Spanish and English), push lead records into CRM, and track budgets. Target: launch in 4 weeks. Budget: ~USD 12–15k. Contact: camila.ramos@retail.pe")
  print(json.dumps(parse_brief(messy), ensure_ascii=False, indent=2))
