# Mojibake Detector

A smart detection tool for character encoding errors (mojibake) in text files. This tool identifies various types of encoding issues that can corrupt text, particularly when UTF-8 content is incorrectly interpreted as Windows-1252 or ISO-8859-1.

## What is Mojibake?

Mojibake (文字化け) refers to garbled text that occurs when text is decoded using an unintended character encoding. Common examples include:
- `itâ€™s` instead of `it's`
- `â‚¬100` instead of `€100`
- `â€œquotesâ€` instead of `"quotes"`

## Features

- **Pattern Recognition**: Detects 50+ known mojibake patterns
- **Regex Analysis**: Uses advanced regex patterns to identify encoding issues
- **Statistical Analysis**: Analyzes character distribution for anomalies
- **Confidence Scoring**: Provides confidence percentage for detected issues
- **Sample Extraction**: Shows problematic text samples for review
- **File Support**: Works with any text file format

## Installation

No installation required! Just ensure you have Python 3.6+ installed.

```bash
git clone https://github.com/leoyin1127/mojibake_fixer.git
cd mojibake_fixer
```

## Usage

### Check a specific file:
```bash
python detector.py "path/to/your/file.csv"
```

### Test with built-in sample:
```bash
python detector.py
```

## Example Output

```
============================================================
MOJIBAKE DETECTION REPORT
============================================================

⚠️  MOJIBAKE DETECTED!
Confidence: 85.0%

Found 3 issue type(s):
----------------------------------------
• "â€™" should be "'"
  Found 15 occurrence(s)
• "â‚¬" should be "€"
  Found 8 occurrence(s)
• Quote/punctuation mojibake
  Found 12 match(es)
  Samples: ['â€œ', 'â€', 'â€¦']

Statistics:
----------------------------------------
• Total characters: 50847
• Non-ASCII ratio: 12.34%
• Suspicious sequences: 35
• Weird characters found: 127

Sample problematic lines:
----------------------------------------
1. The companyâ€™s revenue was â‚¬1.2 million in Q3.
2. She said, â€œThis is exactly what we needed.â€
3. The reportâ€™s findings show significant growth...
============================================================
```

## Detection Methods

The detector uses multiple approaches:

### 1. Known Pattern Matching
Identifies common mojibake transformations:
- Smart quotes: `â€™` → `'`, `â€œ` → `"`
- Currency symbols: `â‚¬` → `€`, `Â£` → `£`
- Accented characters: `Ã¡` → `á`, `Ã©` → `é`
- Special symbols: `â€¢` → `•`, `â€"` → `—`

### 2. Regex Pattern Analysis
Detects suspicious character sequences:
- UTF-8 byte sequences misinterpreted as individual characters
- Common mojibake prefixes (`Ã`, `Â`, `â€`)
- Replacement character patterns (`�`)

### 3. Statistical Analysis
Analyzes text characteristics:
- High-byte character distribution
- Control character presence
- Non-ASCII ratio analysis
- Suspicious character combinations

## Common Mojibake Patterns

| Mojibake | Correct | Description        |
| -------- | ------- | ------------------ |
| `â€™`    | `'`     | Right single quote |
| `â€œ`    | `"`     | Left double quote  |
| `â€`     | `"`     | Right double quote |
| `â‚¬`    | `€`     | Euro symbol        |
| `â€"`    | `—`     | Em dash            |
| `â€¦`    | `…`     | Ellipsis           |
| `Ã©`     | `é`     | Accented e         |
| `Â `     | ` `     | Non-breaking space |

## File Types Supported

- CSV files
- Text files (.txt)
- Log files
- Any UTF-8 encoded text file

## Technical Details

### Character Encoding Issues Detected

1. **UTF-8 → Windows-1252**: Most common mojibake source
2. **Double encoding**: UTF-8 encoded multiple times
3. **Replacement characters**: Data loss indicators
4. **Mixed encodings**: Files with multiple encoding types

### Confidence Scoring

The confidence score (0-100%) is calculated based on:
- Number of known patterns found (40% weight)
- Regex pattern matches (30% weight)
- Statistical anomalies (20% weight)
- Character distribution analysis (10% weight)
