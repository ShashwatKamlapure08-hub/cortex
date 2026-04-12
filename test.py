from huggingface_hub import login
import os
from dotenv import load_dotenv

load_dotenv()
login(token=os.getenv("HUGGINGFACE_API_KEY"))
print("✅ Cortex connected to Hugging Face!")