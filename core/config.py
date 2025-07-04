import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "*")

OPENAI_TALK_MODEL = "gpt-4.1-mini"
OPENAI_SUMMARY_MODEL = "gpt-4.1-mini"
OPENAI_KG_MODEL = "gpt-4.1-mini"
