# ui/messages.py
import random
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

MESSAGES = [
    # Bijli themed
    "Bijli aa gayi — commit karo jaldi.",
    "UPS pe ho? Backup le lo pehle.",
    "Load shedding schedule check kiya?",
    
    # Internet themed  
    "Submarine cable theek hai aaj.",
    "SMW4 kal se behtar lag raha hai.",
    "PTCL raat ko slow hota hai — seedha raho.",
    "GitHub ka DNS resolve ho gaya. Barkat hai.",
    
    # General desi dev humor
    "Chai pee lo — npm install chal raha hai.",
    "Stack Overflow band nahi hai. Alhamdulillah.",
    "Kaam karo. Guardian jaag raha hai.",
    "Aaj ka commit: Kal ki neend.",
    "Production pe mat daal abhi. Bijli nahi hai.",
    "Git push ho gaya. Allah ka shukar.",
    "Deadline kal hai. Chai banao.",
    "Senior ne approve kiya. Subhanallah.",
]

def get_message():
    return random.choice(MESSAGES)

if __name__ == "__main__":
    print(get_message())
