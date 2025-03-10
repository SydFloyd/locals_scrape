from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    def __init__(self):
        self.locals_username = os.getenv("LOCALS_USERNAME")
        self.locals_password = os.getenv("LOCALS_PASSWORD")
        
        self.validate()

    def validate(self):
        missing_vars = [
            var_name for var_name in ["LOCALS_USERNAME", "LOCALS_PASSWORD"]
            if not getattr(self, var_name.lower())
        ]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

cfg = Config()
