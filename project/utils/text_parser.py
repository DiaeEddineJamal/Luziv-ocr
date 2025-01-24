import re
import unicodedata
from datetime import datetime
from typing import Optional, Dict
import logging


class MoroccanIDExtractor:
    def __init__(self):
        """
        Initialize patterns for extracting specific fields from Moroccan ID text.
        Supports both Arabic and French text formats.
        """
        self.patterns = {
            'cin_number': r'\b[A-Z]{1,2}\d{6}\b',  # CIN: 1-2 letters followed by 6 digits
            'name': {
                'fr': r'NOM\s*ET\s*PRENOM\s*[:]*\s*([A-Z\s\-]+)',  # Adjust for possible spaces/hyphens
                'ar': r'الاسم\s*الكامل\s*[:]*\s*([\u0600-\u06FF\s]+)'  # Handles Arabic names
            },
            'birth_date': {
                'fr': r'N[eé]\s*le\s*(\d{2}[./-]\d{2}[./-]\d{4})',
                'ar': r'تاريخ\s*الازدياد\s*[:]*\s*(\d{2}[./-]\d{2}[./-]\d{4})'
            },
            'birth_place': {
                'fr': r'\b(?:\u00e0|a)\s*([A-Z\s\-]+)',  # Location in French
                'ar': r'مكان\s*الازدياد\s*[:]*\s*([\u0600-\u06FF\s]+)'  # Location in Arabic
            },
            'expiry_date': {
                'fr': r'Valable\s*jusqu\'au\s*(\d{2}[./-]\d{2}[./-]\d{4})',
                'ar': r'صالحة\s*إلى\s*غاية\s*(\d{2}[./-]\d{2}[./-]\d{4})'
            }
        }

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text by removing accents, extra spaces, and unifying format.
        """
        # Remove accents
        text = unicodedata.normalize('NFKD', text)
        text = ''.join(c for c in text if not unicodedata.combining(c))

        # Remove multiple spaces and trim
        text = re.sub(r'\s+', ' ', text).strip()

        # Standardize Arabic characters
        arabic_chars = {
            'أ': 'ا', 'إ': 'ا', 'آ': 'ا',
            'ة': 'ه',
            'ى': 'ي',
            '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
            '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
        }
        for ar_char, replacement in arabic_chars.items():
            text = text.replace(ar_char, replacement)

        return text

    @staticmethod
    def parse_date(date_str: str) -> Optional[str]:
        """
        Convert date string to standard format (YYYY-MM-DD).
        """
        if not date_str:
            return None

        # Standardize separators
        date_str = date_str.replace('.', '/').replace('-', '/')

        try:
            # Try different date formats
            for fmt in ['%d/%m/%Y', '%Y/%m/%d', '%m/%d/%Y']:
                try:
                    return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
                except ValueError:
                    continue
            return None
        except Exception:
            return None

    def clean_irrelevant_lines(self, text: str) -> str:
        """
        Remove irrelevant lines and text patterns.
        """
        patterns_to_remove = [
            r'(ROYAUME DU MAROC|CARTE NATIONALE D\'IDENTITE)',
            r'(المملكة المغربية|البطاقة الوطنية للتعريف)',
            r'الحة\s*إلى\s*غَاية\s*\d{2}\.\d{4}'  # Ignore expiry-like irrelevant lines
        ]
        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        return text.strip()

    def extract(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract relevant fields from Moroccan ID card text.
        Handles both Arabic and French text.
        """
        # Normalize and clean text
        text = self.normalize_text(text)
        text = self.clean_irrelevant_lines(text)

        # Initialize results dictionary with only relevant fields
        extracted = {
            'CIN Number': None,
            'Full Name': None,
            'Date of Birth': None,
            'Place of Birth': None,
            'Expiry Date': None
        }

        # Extract fields using regex
        for key, patterns in self.patterns.items():
            if isinstance(patterns, dict):  # Handle language-specific patterns
                for lang, pattern in patterns.items():
                    match = re.search(pattern, text, flags=re.IGNORECASE)  # Added re.IGNORECASE
                    if match:
                        if key == 'birth_date' or key == 'expiry_date':
                            extracted[key.replace('_', ' ').title()] = self.parse_date(match.group(1))
                        else:
                            extracted[key.replace('_', ' ').title()] = match.group(1).strip()
                        break
            else:
                match = re.search(patterns, text, flags=re.IGNORECASE)  # Added re.IGNORECASE
                if match:
                    extracted[key.replace('_', ' ').title()] = match.group(0).strip()

        return extracted
