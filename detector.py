#!/usr/bin/env python3
"""
Smart Mojibake Detection Script
Detects various character encoding errors in text files or strings
"""

import re
import sys
from collections import Counter
from typing import Dict, List, Tuple, Set
import unicodedata

class MojibakeDetector:
    def __init__(self):
        # Common mojibake patterns (UTF-8 → Windows-1252/ISO-8859-1)
        self.common_patterns = {
            # Quotes and apostrophes
            'â€™': "'",  # Right single quote
            'â€˜': "'",  # Left single quote
            'â€œ': '"',  # Left double quote
            'â€': '"',   # Right double quote
            'â€¦': '…',  # Ellipsis
            'â€"': '—',  # Em dash
            'â€"': '–',  # En dash
            
            # Spaces and breaks
            'Â ': ' ',    # Non-breaking space
            'Â\xa0': ' ', # Non-breaking space variant
            'Â\xad': '',  # Soft hyphen
            
            # Common accented characters
            'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
            'Ã ': 'à', 'Ã¨': 'è', 'Ã¬': 'ì', 'Ã²': 'ò', 'Ã¹': 'ù',
            'Ã¢': 'â', 'Ãª': 'ê', 'Ã®': 'î', 'Ã´': 'ô', 'Ã»': 'û',
            'Ã£': 'ã', 'Ã±': 'ñ', 'Ãµ': 'õ',
            'Ã¤': 'ä', 'Ã«': 'ë', 'Ã¯': 'ï', 'Ã¶': 'ö', 'Ã¼': 'ü',
            
            # Currency and symbols
            'â‚¬': '€',  # Euro
            'Â£': '£',   # Pound
            'Â¥': '¥',   # Yen
            'Â©': '©',   # Copyright
            'Â®': '®',   # Registered
            'â„¢': '™',  # Trademark
            
            # Math symbols
            'Ã—': '×',   # Multiplication
            'Ã·': '÷',   # Division
            'Â±': '±',   # Plus-minus
            'â‰': '≠',   # Not equal
            'â‰¤': '≤',  # Less than or equal
            'â‰¥': '≥',  # Greater than or equal
            
            # Bullets and special
            'â€¢': '•',  # Bullet
            'Â°': '°',   # Degree
            'Â§': '§',   # Section
            'Â¶': '¶',   # Pilcrow
        }
        
        # Regex patterns for common mojibake
        self.regex_patterns = [
            # UTF-8 sequences misinterpreted
            (r'[\xC2-\xDF][\x80-\xBF]', 'Possible 2-byte UTF-8 sequence'),
            (r'[\xE0-\xEF][\x80-\xBF]{2}', 'Possible 3-byte UTF-8 sequence'),
            (r'[\xF0-\xF4][\x80-\xBF]{3}', 'Possible 4-byte UTF-8 sequence'),
            
            # Common mojibake character sequences
            (r'Ã[\x80-\xFF]', 'Latin-1/Windows-1252 interpretation of UTF-8'),
            (r'Â[\x80-\xFF]', 'Common mojibake prefix'),
            (r'â€[\x80-\xFF]', 'Quote/punctuation mojibake'),
            (r'â[\x80-\xFF]{2}', 'Special character mojibake'),
            
            # Replacement character patterns
            (r'�+', 'Replacement characters (data loss)'),
            (r'[\ufffd]+', 'Unicode replacement characters'),
            (r'\?{3,}', 'Multiple question marks (possible encoding error)'),
            
            # Double-encoded UTF-8
            (r'Ã\x83Â', 'Possible double-encoded UTF-8'),
            (r'Ã¢â‚¬', 'Double-encoded quote pattern'),
        ]
        
        # Character combinations that rarely occur naturally
        self.suspicious_combos = [
            'Ã¢', 'â€', 'Â£', 'Ã©', 'Ã¨', 'Ã ', 'Ã¡', 'Ã§', 'Ã±',
            'â‚¬', 'â€™', 'â€œ', 'â€', 'â€¦', 'Â©', 'Â®', 'â„¢',
            'Ã¼', 'Ã¶', 'Ã¤', 'ÃŸ', 'Ã…', 'Ã†', 'Ã˜', 'Ã¥', 'Ã¦', 'Ã¸'
        ]

    def detect_mojibake(self, text: str) -> Dict:
        """Main detection function that runs all checks"""
        results = {
            'has_mojibake': False,
            'confidence': 0.0,
            'issues': [],
            'statistics': {},
            'samples': []
        }
        
        # Check for common patterns
        pattern_matches = self._check_patterns(text)
        if pattern_matches:
            results['issues'].extend(pattern_matches)
            results['has_mojibake'] = True
        
        # Check with regex
        regex_matches = self._check_regex(text)
        if regex_matches:
            results['issues'].extend(regex_matches)
            results['has_mojibake'] = True
        
        # Statistical analysis
        stats = self._analyze_statistics(text)
        results['statistics'] = stats
        
        # Calculate confidence
        results['confidence'] = self._calculate_confidence(
            pattern_matches, regex_matches, stats
        )
        
        # Get sample problematic sections
        results['samples'] = self._get_samples(text, 5)
        
        return results
    
    def _check_patterns(self, text: str) -> List[Dict]:
        """Check for known mojibake patterns"""
        found = []
        for pattern, correct in self.common_patterns.items():
            count = text.count(pattern)
            if count > 0:
                found.append({
                    'type': 'known_pattern',
                    'pattern': pattern,
                    'expected': correct,
                    'count': count,
                    'description': f'"{pattern}" should be "{correct}"'
                })
        return found
    
    def _check_regex(self, text: str) -> List[Dict]:
        """Check text with regex patterns"""
        found = []
        for pattern, description in self.regex_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            if matches:
                unique_matches = list(set(matches[:10]))  # Limit samples
                found.append({
                    'type': 'regex_match',
                    'pattern': pattern,
                    'description': description,
                    'count': len(matches),
                    'samples': unique_matches[:5]
                })
        return found
    
    def _analyze_statistics(self, text: str) -> Dict:
        """Statistical analysis of character distribution"""
        stats = {
            'total_chars': len(text),
            'high_bytes': 0,
            'control_chars': 0,
            'suspicious_sequences': 0,
            'non_ascii_ratio': 0.0,
            'unusual_char_ratio': 0.0
        }
        
        if not text:
            return stats
        
        # Count character types
        for char in text:
            code = ord(char)
            if code > 127:
                stats['high_bytes'] += 1
            if code < 32 and code not in (9, 10, 13):  # Tab, LF, CR
                stats['control_chars'] += 1
        
        # Check for suspicious combinations
        for combo in self.suspicious_combos:
            stats['suspicious_sequences'] += text.count(combo)
        
        # Calculate ratios
        stats['non_ascii_ratio'] = stats['high_bytes'] / len(text)
        stats['unusual_char_ratio'] = (
            stats['control_chars'] + stats['suspicious_sequences']
        ) / len(text)
        
        # Check for specific weird characters
        weird_chars = ['Â', 'Ã', 'â', '€', '™', '¬', '¦', '¢', '¥', '§']
        stats['weird_char_count'] = sum(text.count(c) for c in weird_chars)
        
        return stats
    
    def _calculate_confidence(self, patterns: List, regex: List, stats: Dict) -> float:
        """Calculate confidence score that text has mojibake"""
        confidence = 0.0
        
        # Known patterns are strong indicators
        if patterns:
            confidence += min(len(patterns) * 10, 40)
        
        # Regex matches add confidence
        if regex:
            confidence += min(len(regex) * 8, 30)
        
        # Statistical indicators
        if stats.get('suspicious_sequences', 0) > 5:
            confidence += 20
        
        if stats.get('weird_char_count', 0) > 10:
            confidence += 15
        
        # High ratio of unusual characters
        if stats.get('unusual_char_ratio', 0) > 0.01:
            confidence += 10
        
        # Non-ASCII ratio (suspicious if between 0.1 and 0.5)
        non_ascii = stats.get('non_ascii_ratio', 0)
        if 0.1 < non_ascii < 0.5:
            confidence += 5
        
        return min(confidence, 100.0)
    
    def _get_samples(self, text: str, max_samples: int = 5) -> List[str]:
        """Extract sample sections with mojibake"""
        samples = []
        lines = text.split('\n')
        
        for line in lines[:100]:  # Check first 100 lines
            if any(pattern in line for pattern in self.common_patterns.keys()):
                # Get context around the problematic part
                if len(line) > 100:
                    line = line[:100] + '...'
                samples.append(line)
                if len(samples) >= max_samples:
                    break
        
        return samples
    
    def check_file(self, filepath: str) -> Dict:
        """Check a file for mojibake"""
        try:
            # Try UTF-8 first
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        except UnicodeDecodeError:
            # Try with error handling
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                text = f.read()
        
        return self.detect_mojibake(text)
    
    def print_report(self, results: Dict):
        """Print a formatted report of findings"""
        print("\n" + "="*60)
        print("MOJIBAKE DETECTION REPORT")
        print("="*60)
        
        if results['has_mojibake']:
            print(f"\n⚠️  MOJIBAKE DETECTED!")
            print(f"Confidence: {results['confidence']:.1f}%")
        else:
            print("\n✓ No mojibake detected")
        
        if results['issues']:
            print(f"\nFound {len(results['issues'])} issue type(s):")
            print("-" * 40)
            
            for issue in results['issues']:
                if issue['type'] == 'known_pattern':
                    print(f"• {issue['description']}")
                    print(f"  Found {issue['count']} occurrence(s)")
                elif issue['type'] == 'regex_match':
                    print(f"• {issue['description']}")
                    print(f"  Found {issue['count']} match(es)")
                    if issue.get('samples'):
                        print(f"  Samples: {issue['samples'][:3]}")
        
        if results['statistics']:
            stats = results['statistics']
            print("\nStatistics:")
            print("-" * 40)
            print(f"• Total characters: {stats['total_chars']}")
            print(f"• Non-ASCII ratio: {stats['non_ascii_ratio']:.2%}")
            print(f"• Suspicious sequences: {stats['suspicious_sequences']}")
            print(f"• Weird characters found: {stats.get('weird_char_count', 0)}")
        
        if results['samples']:
            print("\nSample problematic lines:")
            print("-" * 40)
            for i, sample in enumerate(results['samples'], 1):
                print(f"{i}. {sample}")
        
        print("\n" + "="*60)


def main():
    """Command-line interface"""
    detector = MojibakeDetector()
    
    if len(sys.argv) > 1:
        # File mode
        filepath = sys.argv[1]
        print(f"Checking file: {filepath}")
        results = detector.check_file(filepath)
    else:
        # Test with sample text
        sample_text = """
        This text has mojibake: itâ€™s not displayed correctly.
        The companyâ€™s report shows â‚¬100 in revenue.
        Special chars: Ã© Ã¡ Ã± â€œquotesâ€ and â€" dashes.
        Normal text is fine, but Ã¢â‚¬â„¢ this isn't.
        """
        print("Checking sample text...")
        results = detector.detect_mojibake(sample_text)
    
    detector.print_report(results)
    
    # Return exit code based on detection
    sys.exit(1 if results['has_mojibake'] else 0)


if __name__ == "__main__":
    main()