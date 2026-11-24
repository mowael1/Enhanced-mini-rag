import os
import importlib

class TemplateParser:
    
    def __init__(self, language: str = None, default_language = "en"):
        

        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.default_language = default_language
        self.language = None
        
        self.set_language(language)
        
    def set_language(self, language: str):
        language = language or self.default_language
        
        language_path = os.path.join(
            self.current_path,
            "locales",
            language
        )
        if os.path.exists(language_path):
            self.language = language
            
        else:
            self.language = self.default_language
            
    def get(self, group: str, key: str, vars: dict = None):
        
        # group: is rag.py file
        if not group or not key: 
            return None
        
        group_path = os.path.join(
            self.current_path,
            "locales",
            self.language,
            f"{group}.py"
        )
        
        targeted_lang = self.language
        
        if not os.path.exists(group_path): 
            group_path = os.path.join(
                self.current_path,
                "locales",
                self.default_language,
                f"{group}.py"
            )
            
            targeted_lang = self.default_language
            
        if not os.path.exists(group_path): 
            return None
        
        
        #import group module
        module = importlib.import_module(
            f"{__package__}.locales.{targeted_lang}.{group}"
        )
        
        
        if not module:
            return None
        
        key_attribute = getattr(module, key, None)
        if key_attribute is None:
            return None
        
        return key_attribute.substitute(vars or {})
