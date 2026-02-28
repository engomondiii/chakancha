"""
FAQ Validator
Validates FAQ JSON files before merging to prevent errors
"""

import json
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger('chatbot')


class FAQValidator:
    """
    Validates FAQ JSON structure and content
    """
    
    REQUIRED_FIELDS = ['id', 'category', 'question', 'answer']
    OPTIONAL_FIELDS = ['keywords', 'related_faqs']
    VALID_CATEGORIES = [
        'tea_production', 'tea_processing', 'market_information',
        'pricing', 'quality_standards', 'business_operations',
        'employment', 'investment', 'export', 'general',
        'company', 'products', 'ordering', 'shipping', 'chakan_tree'
    ]
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_file(self, filepath: str) -> Tuple[bool, List[str], List[str]]:
        """
        Validate entire FAQ file
        
        Returns:
            Tuple[bool, List[str], List[str]]: (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON format: {str(e)}")
            return False, self.errors, self.warnings
        except FileNotFoundError:
            self.errors.append(f"File not found: {filepath}")
            return False, self.errors, self.warnings
        
        # Check top-level structure
        if 'faqs' not in data:
            self.errors.append("Missing 'faqs' key in JSON")
            return False, self.errors, self.warnings
        
        if not isinstance(data['faqs'], list):
            self.errors.append("'faqs' must be a list")
            return False, self.errors, self.warnings
        
        # Validate metadata if present
        if 'metadata' in data:
            self._validate_metadata(data['metadata'])
        else:
            self.warnings.append("No metadata found (recommended but not required)")
        
        # Validate each FAQ
        faq_ids = set()
        for i, faq in enumerate(data['faqs']):
            self._validate_faq(faq, i, faq_ids)
        
        is_valid = len(self.errors) == 0
        
        if is_valid:
            logger.info(f"✅ Validation passed for {filepath}")
        else:
            logger.error(f"❌ Validation failed for {filepath}")
        
        return is_valid, self.errors, self.warnings
    
    def _validate_metadata(self, metadata: Dict):
        """Validate metadata structure"""
        recommended = ['version', 'language', 'last_updated', 'total_faqs']
        
        for field in recommended:
            if field not in metadata:
                self.warnings.append(f"Metadata missing recommended field: {field}")
    
    def _validate_faq(self, faq: Dict, index: int, faq_ids: set):
        """Validate single FAQ item"""
        faq_ref = f"FAQ #{index + 1}"
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in faq:
                self.errors.append(f"{faq_ref}: Missing required field '{field}'")
            elif not faq[field] or (isinstance(faq[field], str) and not faq[field].strip()):
                self.errors.append(f"{faq_ref}: Field '{field}' is empty")
        
        # Check ID uniqueness
        if 'id' in faq:
            if faq['id'] in faq_ids:
                self.errors.append(f"{faq_ref}: Duplicate ID '{faq['id']}'")
            else:
                faq_ids.add(faq['id'])
            
            # Check ID format
            if not isinstance(faq['id'], str) or not faq['id'].startswith('faq_'):
                self.warnings.append(f"{faq_ref}: ID should start with 'faq_' (e.g., 'faq_001')")
        
        # Check category
        if 'category' in faq:
            if faq['category'] not in self.VALID_CATEGORIES:
                self.warnings.append(
                    f"{faq_ref}: Category '{faq['category']}' not in standard list. "
                    f"Valid: {', '.join(self.VALID_CATEGORIES)}"
                )
        
        # Check question and answer length
        if 'question' in faq and len(faq['question']) > 500:
            self.warnings.append(f"{faq_ref}: Question is very long ({len(faq['question'])} chars)")
        
        if 'answer' in faq and len(faq['answer']) > 2000:
            self.warnings.append(f"{faq_ref}: Answer is very long ({len(faq['answer'])} chars)")
        
        # Check keywords format
        if 'keywords' in faq:
            if not isinstance(faq['keywords'], list):
                self.errors.append(f"{faq_ref}: 'keywords' must be a list")
            elif len(faq['keywords']) == 0:
                self.warnings.append(f"{faq_ref}: 'keywords' is empty")
        
        # Check related_faqs format
        if 'related_faqs' in faq:
            if not isinstance(faq['related_faqs'], list):
                self.errors.append(f"{faq_ref}: 'related_faqs' must be a list")
    
    def get_faq_count(self, filepath: str) -> int:
        """Get number of FAQs in file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return len(data.get('faqs', []))
        except:
            return 0
    
    def get_categories(self, filepath: str) -> List[str]:
        """Get unique categories in file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            categories = set()
            for faq in data.get('faqs', []):
                if 'category' in faq:
                    categories.add(faq['category'])
            
            return sorted(list(categories))
        except:
            return []