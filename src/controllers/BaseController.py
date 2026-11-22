from helpers.config import get_settings
from pathlib import Path
class BaseController:
    
    def __init__(self):
        self.app_settings= get_settings()
        
        #C:\Users\mw865\OneDrive\Desktop\mini-rag-enhanced\src
        self.base_dir = Path(__file__).parent.parent

        #C:\Users\mw865\OneDrive\Desktop\mini-rag-enhanced\src\assets\files
        self.files_dir = Path(__file__).parent.parent / "assets/files"
