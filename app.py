from fastapi import FastAPI
from pydantic import BaseModel
from phase1 import parse_brief

app = FastAPI(title = "AI RFP NORMALIZER")

class BriefIn(BaseModel): 
  brief: str
  
@app.post("/normalize")
def normalize(b: BriefIn):
  return parse_brief(b.brief)
