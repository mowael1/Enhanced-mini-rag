from helpers.config import get_settings
from pathlib import Path
import os

class BaseController:
    
    def __init__(self):
        self.app_settings= get_settings()
        
        #C:\Users\mw865\OneDrive\Desktop\mini-rag-enhanced\src
        self.base_dir = Path(__file__).parent.parent

        #C:\Users\mw865\OneDrive\Desktop\mini-rag-enhanced\src\assets\files
        self.files_dir = Path(__file__).parent.parent / "assets/files"
        
        
        self.database_dir = os.path.join(
            self.base_dir,
            "assets/database"
        )

    def get_database_path(self, db_name: str):
        
        database_path = os.path.join(
            self.database_dir,
            db_name
        )
        
        if not os.path.exists(database_path):
            os.makedirs(database_path)
            
        return database_path