from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'lucky_star_secret_key'

CHALDEAN_MAP = {
    'A':1, 'I':1, 'J':1, 'Q':1, 'Y':1,
    'B':2, 'K':2, 'R':2,
    'C':3, 'G':3, 'L':3, 'S':3,
    'D':4, 'M':4, 'T':4,
    'E':5, 'H':5, 'N':5, 'X':5,
    'U':6, 'V':6, 'W':6,
    'O':7, 'Z':7,
    'F':8, 'P':8
}

PYTHAGOREAN_MAP = {
    'A':1, 'J':1, 'S':1,
    'B':2, 'K':2, 'T':2,
    'C':3, 'L':3, 'U':3,
    'D':4, 'M':4, 'V':4,
    'E':5, 'N':5, 'W':5,
    'F':6, 'O':6, 'X':6,
    'G':7, 'P':7, 'Y':7,
    'H':8, 'Q':8, 'Z':8,
    'I':9, 'R':9
}

BIRTH_DEGREES = {
    1: 36.40, 2: 26.40, 3: 40.00, 4: 36.40, 5: 40.00,
    6: 40.00, 7: 46.40, 8: 53.20, 9: 40.00
}

NAME_FREQ_MAP = {
    'A': 1,
    'B': 200, 'R': 200,
    'I': 10, 'J': 10, 'Y': 10,
    'C': 300, 'G': 300,
    'K': 20,
    'D': 400, 'T': 400,
    'L': 30, 'S': 30,
    'E': 500, 'H': 500, 'X': 500,
    'M': 40,
    'W': 600,
    'N': 50,
    'Z': 700,
    'U': 60, 'V': 60,
    'F': 800,
    'O': 70,
    'P': 80,
    'Q': 100
}

RELATIONS = {
    1: {'friends': [1, 2, 3, 5, 6, 9], 'enemies': [8], 'neutral': [4, 7]},
    2: {'friends': [1, 2, 3, 5], 'enemies': [4, 8, 9], 'neutral': [6, 7]},
    3: {'friends': [1, 2, 3, 5, 7], 'enemies': [6], 'neutral': [4, 8, 9]},
    4: {'friends': [1, 5, 6, 7, 8], 'enemies': [2, 9], 'neutral': [3, 4]},
    5: {'friends': [1, 5, 6, 9], 'enemies': [], 'neutral': [2, 3, 4, 7, 8]},
    6: {'friends': [1, 4, 5, 6, 7, 8], 'enemies': [3], 'neutral': [2, 9]},
    7: {'friends': [1, 3, 4, 5, 6], 'enemies': [], 'neutral': [2, 7, 8, 9]},
    8: {'friends': [3, 4, 5, 6, 7, 8], 'enemies': [1, 2, 9], 'neutral': []},
    9: {'friends': [1, 3, 5, 6, 9], 'enemies': [2, 4, 8], 'neutral': [7]}
}

NUMBER_PROPS = {
    1: {'colors': 'ಹಳದಿ, ಕಿತ್ತಳೆ, ಗೋಲ್ಡನ್', 'direction': 'ಪೂರ್ವ', 'gemstone': 'ಕೆಂಪು ಮಾಣಿಕ್ಯ', 'profession': 'ಸರ್ಕಾರಿ ಉದ್ಯೋಗ, ರಾಜಕೀಯ, ನಾಯಕತ್ವ', 'lucky_days': 'ಭಾನುವಾರ, ಗುರುವಾರ'},
    2: {'colors': 'ಬಿಳಿ, ಹಸಿರು, ಬೆಳ್ಳಿ ಬಣ್ಣ', 'direction': 'ವಾಯುವ್ಯ', 'gemstone': 'ಮುತ್ತು / ಚಂದ್ರಕಾಂತ ರತ್ನ', 'profession': 'ಕಲಾವಿದರು, ಪ್ರಯಾಣ, ದ್ರವ ಪದಾರ್ಥಗಳು', 'lucky_days': 'ಸೋಮವಾರ, ಬುಧವಾರ'},
    3: {'colors': 'ಹಳದಿ, ಗುಲಾಬಿ, ನೇರಳೆ', 'direction': 'ಈಶಾನ್ಯ', 'gemstone': 'ಹಳದಿ ಪುಷ್ಯರಾಗ', 'profession': 'ಶಿಕ್ಷಣ, ಬೋಧನೆ, ಸಲಹೆಗಾರರು', 'lucky_days': 'ಗುರುವಾರ, ಮಂಗಳವಾರ'},
    4: {'colors': 'ಬೂದು, ನೀಲಿ, ಮಣ್ಣಿನ ಬಣ್ಣ', 'direction': 'ನೈಋತ್ಯ', 'gemstone': 'ಗೋಮೇಧಿಕ / ನೀಲಮಣಿ', 'profession': 'ತಂತ್ರಜ್ಞಾನ, ಸಾಫ್ಟ್‌ವೇರ್, ಇಂಜಿನಿಯರಿಂಗ್', 'lucky_days': 'ಬುಧವಾರ, ಶನಿವಾರ'},
    5: {'colors': 'ಹಸಿರು, ತಿಳಿ ಬಣ್ಣಗಳು', 'direction': 'ಉತ್ತರ', 'gemstone': 'ಪಚ್ಚೆ', 'profession': 'ವ್ಯವಹಾರ, ಮಾರ್ಕೆಟಿಂಗ್, ಷೇರು ಮಾರುಕಟ್ಟೆ', 'lucky_days': 'ಬುಧವಾರ, ಶುಕ್ರವಾರ'},
    6: {'colors': 'ಬಿಳಿ, ತಿಳಿ ನೀಲಿ, ಗುಲಾಬಿ', 'direction': 'ಆಗ್ನೇಯ', 'gemstone': 'ವೈಡೂರ್ಯ / ವಜ್ರ', 'profession': 'ಸೌಂದರ್ಯ ವರ್ಧಕಗಳು, ಫ್ಯಾಷನ್, ಸಿನಿಮಾ', 'lucky_days': 'ಶುಕ್ರವಾರ, ಬುಧವಾರ'},
    7: {'colors': 'ಸ್ಮೋಕಿ ಗ್ರೇ, ಬಿಳಿ, ಹಸಿರು', 'direction': 'ಈಶಾನ್ಯ / ವಾಯುವ್ಯ', 'gemstone': 'ಬೆಕ್ಕು ಕಣ್ಣಿನ ರತ್ನ', 'profession': 'ಆಧ್ಯಾತ್ಮ, ಸಂಶೋಧನೆ, ಜ್ಯೋತಿಷ್ಯ', 'lucky_days': 'ಸೋಮವಾರ, ಗುರುವಾರ'},
    8: {'colors': 'ಕಪ್ಪು, ಗಾಢ ನೀಲಿ, ದಟ್ಟ ಬೂದು', 'direction': 'ಪಶ್ಚಿಮ', 'gemstone': 'ನೀಲಮಣಿ', 'profession': 'ವೈದ್ಯರು, ನರ್ಸ್‌ಗಳು, ಕಬ್ಬಿಣ/ಉಕ್ಕು ಉದ್ಯಮ', 'lucky_days': 'ಶನಿವಾರ, ಬುಧವಾರ'},
    9: {'colors': 'ಕೆಂಪು, ಗುಲಾಬಿ, ಮರೂನ್', 'direction': 'ದಕ್ಷಿಣ', 'gemstone': 'ಕೆಂಪು ಹವಳ', 'profession': 'ರಕ್ಷಣೆ, ಪೊಲೀಸ್, ಸೈನ್ಯ, ರಿಯಲ್ ಎಸ್ಟೇಟ್', 'lucky_days': 'ಮಂಗಳವಾರ, ಭಾನುವಾರ'}
}

MISSING_REMEDIES = {
    1: 'ಸೂರ್ಯನ ಬಲ ಹೆಚ್ಚಿಸಲು ಪ್ರತಿದಿನ ಸೂರ್ಯ ನಮಸ್ಕಾರ ಮಾಡಿ ಮತ್ತು ತಾಮ್ರದ ಪಾತ್ರೆಯಲ್ಲಿ ನೀರು ಕುಡಿಯಿರಿ.',
    2: 'ಚಂದ್ರನ ಬಲ ಹೆಚ್ಚಿಸಲು ಬೆಳ್ಳಿಯ ಪಾತ್ರೆಯನ್ನು ಬಳಸಿ ಮತ್ತು ತಾಯಿಯವರ ಆಶೀರ್ವಾದ ಪಡೆಯಿರಿ.',
    3: 'ಗುರುವಿನ ಬಲ ಹೆಚ್ಚಿಸಲು ಹಳದಿ ಬಣ್ಣದ ವಸ್ತುಗಳನ್ನು ಬಳಸಿ ಮತ್ತು ಹಿರಿಯರನ್ನು ಗೌರವಿಸಿ.',
    4: 'ರಾಹುವಿನ ಬಲಕ್ಕಾಗಿ ಪಕ್ಷಿಗಳಿಗೆ ಧಾನ್ಯಗಳನ್ನು ಹಾಕಿ ಮತ್ತು ಪ್ರಕೃತಿಯೊಂದಿಗೆ ಇರಿ.',
    5: 'ಬುಧನ ಬಲಕ್ಕಾಗಿ ಹಸಿರು ಬಣ್ಣದ ಬಟ್ಟೆ ಧರಿಸಿ ಮತ್ತು ಗಣಪತಿ ಆರಾಧನೆ ಮಾಡಿ.',
    6: 'ಶುಕ್ರನ ಬಲಕ್ಕಾಗಿ ಸೌಂದರ್ಯ ಮತ್ತು ಸ್ವಚ್ಛತೆಗೆ ಆದ್ಯತೆ ನೀಡಿ, ಮಹಾಲಕ್ಷ್ಮಿ ಪೂಜೆ ಮಾಡಿ.',
    7: 'ಕೇತುವಿನ ಬಲಕ್ಕಾಗಿ ಗಣೇಶನ ಪ್ರಾರ್ಥನೆ ಮಾಡಿ ಮತ್ತು ಪ್ರಾಣಿಗಳಿಗೆ ಸಹಾಯ ಮಾಡಿ.',
    8: 'ಶನಿಯ ಬಲಕ್ಕಾಗಿ ಬಡವರಿಗೆ ಮತ್ತು ನಿರ್ಗತಿಕರಿಗೆ ಅನ್ನದಾನ ಅಥವಾ ಸೇವೆ ಮಾಡಿ.',
    9: 'ಮಂಗಳನ ಬಲಕ್ಕಾಗಿ ಕೆಂಪು ಬಣ್ಣ ಬಳಸಿ ಮತ್ತು ಯೋಗ, ವ್ಯಾಯಾಮ ರೂಢಿಸಿಕೊಳ್ಳಿ.'
}

PERSONAL_YEAR_PREDICTIONS = {
    1: 'ಹೊಸ ಆರಂಭ, ಹೊಸ ಯೋಜನೆಗಳು ಮತ್ತು ನಾಯಕತ್ವ ವಹಿಸಲು ಅತ್ಯುತ್ತಮ ವರ್ಷ.',
    2: 'ಸಹನೆ, ಪಾಲುದಾರಿಕೆ, ಸಂಬಂಧಗಳ ಸುಧಾರಣೆ ಮತ್ತು ಶಾಂತಿಯಿಂದ ಕೆಲಸ ಸಾಧಿಸುವ ವರ್ಷ.',
    3: 'ಸೃಜನಶೀಲತೆ, ಕಲೆ, ಮಾತಿನ ಚಾತುರ್ಯ, ಆರ್ಥಿಕ ಪ್ರಗತಿ ಮತ್ತು ಸಂತೋಷದ ವರ್ಷ.',
    4: 'ಕಠಿಣ ಪರಿಶ್ರಮ, ವ್ಯವಸ್ಥಿತ ಯೋಜನೆ, ವೃತ್ತಿಜೀವನದಲ್ಲಿ ಸ್ಥಿರತೆ.',
    5: 'ಪ್ರಯಾಣ, ಹೊಸ ಬದಲಾವಣೆಗಳು, ವ್ಯಾಪಾರ ವಿಸ್ತರಣೆ ಮತ್ತು ಸ್ವಾತಂತ್ರ್ಯ.',
    6: 'ಕುಟುಂಬದೊಂದಿಗೆ ಕಾಲ ಕಳೆಯುವುದು, ಮನೆ ಅಲಂಕಾರ, ಮದುವೆ ಅಥವಾ ಶುಭ ಕಾರ್ಯಗಳು.',
    7: 'ಆಧ್ಯಾತ್ಮಿಕ ಚಿಂತನೆ, ಸ್ವಯಂ ಅರಿವು, ಸಂಶೋಧನೆ ಮತ್ತು ಏಕಾಂತದಲ್ಲಿ ಜ್ಞಾನ ಸಂಪಾದನೆ.',
    8: 'ಹಣಕಾಸಿನ ಯಶಸ್ಸು, ಅಧಿಕಾರ ಪ್ರಾಪ್ತಿ, ವ್ಯಾಪಾರದಲ್ಲಿ ದೊಡ್ಡ ಲಾಭ.',
    9: 'ಹಳೆಯ ಕೆಲಸಗಳ ಮುಕ್ತಾಯ, ದಾನ-ಧರ್ಮ, ಸಮಾಜ ಸೇವೆ ಮತ್ತು ಮುಂದಿನ ಚಕ್ರಕ್ಕೆ ಸಿದ್ಧತೆ.'
}

GOOD_PAIRS = {'11', '12', '13', '15', '17', '19', '25', '31', '33', '37', '39', '51', '52', '55', '57', '59', '66', '69', '71', '73', '75', '77', '83', '91', '92', '93', '95', '96', '99'}
BAD_PAIRS = {'14', '16', '21', '22', '23', '24', '26', '27', '28', '30', '32', '34', '35', '36', '38', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '53', '54', '56', '58', '60', '61', '62', '63', '64', '65', '67', '68', '70', '72', '74', '76', '78', '79', '80', '81', '82', '84', '85', '86', '87', '88', '89', '90', '94', '97', '98'}

def reduce_to_single(num):
    while num > 9:
        num = sum(int(c) for c in str(num))
    return num

def get_relation(name_num, target_num):
    if not name_num or not target_num:
        return "-"
    rel = RELATIONS.get(target_num, {'friends': [], 'enemies': [], 'neutral': []})
    if name_num in rel['friends']:
        return "Friend (ಸ್ನೇಹ - ಅತ್ಯುತ್ತಮ ಹೊಂದಾಣಿಕೆ)"
    elif name_num in rel['enemies']:
        return "Enemy (ಶತ್ರು - ಎಚ್ಚರಿಕೆ ವಹಿಸಬೇಕು)"
    else:
        return "Neutral (ಸಮ - ಸಾಮಾನ್ಯ ಹೊಂದಾಣಿಕೆ)"

def calculate_kua(year):
    yr_sum = sum(int(c) for c in str(year))
    yr_single = reduce_to_single(yr_sum)
    kua = 11 - yr_single if yr_single <= 9 else 2
    if kua > 9:
        kua = reduce_to_single(kua)
    if kua == 5:
        kua = 2
    return kua

def analyze_mobile_advanced(phone_str):
    digits = [c for c in phone_str if c.isdigit()]
    if len(digits) < 10:
        return None
    
    pair_results = []
    for i in range(len(digits) - 1):
        p = digits[i] + digits[i+1]
        if p in GOOD_PAIRS:
            pair_results.append({'pair': p, 'type': 'good'})
        elif p in BAD_PAIRS:
            pair_results.append({'pair': p, 'type': 'bad'})
        else:
            pair_results.append({'pair': p, 'type': 'neutral'})
            
    total_sum = sum(int(d) for d in digits)
    root_no = reduce_to_single(total_sum)
    ending_no = int(digits[-1])
    
    return {
        'pair_results': pair_results,
        'total_sum': total_sum,
        'root_no': root_no,
        'ending_no': ending_no
    }

def calculate_pyramid(name_str):
    upper_name = ''.join([ch for ch in name_str.upper() if ch in CHALDEAN_MAP])
    if not upper_name:
        return []
    row = [CHALDEAN_MAP[ch] for ch in upper_name]
    pyramid_rows = [row.copy()]
    while len(row) > 1:
        next_row = []
        for i in range(len(row) - 1):
            val = reduce_to_single(row[i] + row[i+1])
            next_row.append(val)
        pyramid_rows.append(next_row.copy())
        row = next_row
    return pyramid_rows

def calculate_dob_pyramid(dob_str):
    digits = [int(ch) for ch in dob_str if ch.isdigit() and ch != '0']
    if not digits:
        return []
    row = digits.copy()
    pyramid_rows = [row.copy()]
    while len(row) > 1:
        next_row = []
        for i in range(len(row) - 1):
            s = row[i] + row[i+1]
            val = reduce_to_single(s) if s > 0 else 0
            next_row.append(val)
        pyramid_rows.append(next_row.copy())
        row = next_row
    return pyramid_rows

def calculate_mobile_pyramid(phone_str):
    digits = [int(ch) for ch in phone_str if ch.isdigit() and ch != '0']
    if len(digits) < 10:
        return []
    row = digits.copy()
    pyramid_rows = [row.copy()]
    while len(row) > 1:
        next_row = []
        for i in range(len(row) - 1):
            s = row[i] + row[i+1]
            val = reduce_to_single(s) if s > 0 else 0
            next_row.append(val)
        pyramid_rows.append(next_row.copy())
        row = next_row
    return pyramid_rows

def analyze_vedic_grid_yogas(present_numbers):
    yogas = []
    if {3, 6, 9}.issubset(present_numbers):
        yogas.append({
            'name': '✨ 3-6-9 ವೈಭವ ಮತ್ತು ಸಂಪತ್ತು ಯೋಗ (Wealth & Glory Yoga)',
            'desc': 'ಗುರು (3), ಶುಕ್ರ (6) ಮತ್ತು ಮಂಗಳ (9) ಒಟ್ಟಿಗೆ ಇರುವುದರಿಂದ ಜೀವನದಲ್ಲಿ ಐಷಾರಾಮಿ ಜೀವನ ಹಾಗೂ ಅಭಿವೃದ್ಧಿ ಪ್ರಾಪ್ತಿಯಾಗುತ್ತದೆ.'
        })
    if {1, 5, 9}.issubset(present_numbers):
        yogas.append({
            'name': '👑 1-5-9 ರಾಜಯೋಗ ಮತ್ತು ನಾಯಕತ್ವ (Leadership & Rajayoga)',
            'desc': 'ಸೂರ್ಯ (1), ಬುಧ (5) ಮತ್ತು ಮಂಗಳ (9) ಸಂಯೋಗದಿಂದ ಸಮಾಜದಲ್ಲಿ ಉನ್ನತ ಸ್ಥಾನ, ಅಧಿಕಾರ ಹಾಗೂ ಕೀರ್ತಿ ಲಭಿಸುತ್ತದೆ.'
        })
    if {3, 1, 9}.issubset(present_numbers):
        yogas.append({
            'name': '🧠 3-1-9 ಜ್ಞಾನ ಮತ್ತು ಬೌದ್ಧಿಕ ಯೋಗ (Mental & Knowledge Yoga)',
            'desc': 'ತೀವ್ರವಾದ ಸ್ಮರಣಶಕ್ತಿ, ಉತ್ತಮ ನಿರ್ಧಾರ ಕೈಗೊಳ್ಳುವ ಸಾಮರ್ಥ್ಯ ಹಾಗೂ ಬಲವಾದ ಇಚ್ಛಾಶಕ್ತಿಯನ್ನು ಸೂಚಿಸುತ್ತದೆ.'
        })
    if {2, 5, 8}.issubset(present_numbers):
        yogas.append({
            'name': '🏡 2-5-8 ಸ್ಥಿರತೆ ಮತ್ತು ಆಸ್ತಿ ಯೋಗ (Stability & Property Yoga)',
            'desc': 'ಚಂದ್ರ (2), ಬುಧ (5) ಮತ್ತು ಶನಿ (8) ಸಂಯೋಜನೆಯು ರಿಯಲ್ ಎಸ್ಟೇಟ್ ಹಾಗೂ ಆಸ್ತಿ ಖರೀದಿ ಯೋಗವನ್ನು ನೀಡುತ್ತದೆ.'
        })
    return yogas

def get_name_correction_advice(chaldean_total):
    auspicious_targets = [15, 24, 33, 42, 51, 19, 37, 46, 14, 23, 32, 41, 50, 59]
    diffs = []
    for t in auspicious_targets:
        if t > chaldean_total:
            diffs.append((t, t - chaldean_total))
    if not diffs:
        return f"ಪ್ರಸ್ತುತ ಮೊತ್ತ {chaldean_total} ಆಗಿದೆ. ಹೆಸರಿನಲ್ಲಿ ಸ್ವಲ್ಪ ಬದಲಾವಣೆ ಮಾಡಿ ಶುಭ ಸಂಖ್ಯೆಗೆ ತರಬಹುದು."
    best_target, needed = min(diffs, key=lambda x: x[1])
    return f"ಪ್ರಸ್ತುತ ಚಾಲ್ಡಿಯನ್ ಮೊತ್ತ: {chaldean_total}. ಇದನ್ನು ಅತ್ಯುತ್ತಮ ಶುಭ ಸಂಖ್ಯಾ ಯೋಗಕ್ಕೆ ({best_target}) ತರಲು **+{needed}** ಮೌಲ್ಯದ ಅಕ್ಷರವನ್ನು ಸೇರಿಸುವುದು ಉತ್ತಮ."

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['name'] = request.form.get('name')
        session['phone'] = request.form.get('phone')
        session['district'] = request.form.get('district')
        session['state'] = request.form.get('state')
        return redirect(url_for('calculator'))
    return render_template('login.html')

@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    user_name = session.get('name', 'Guest')
    
    vedic_grid = [
        [3, 1, 9],
        [6, 7, 5],
        [2, 8, 4]
    ]
    
    formatted_grid = {num: '' for num in range(1, 10)}
    missing_numbers = []
    present_numbers = set()
    grid_yogas = []
    dob = ''
    birth_no = 0
    destiny_no = 0
    destiny_total = 0
    year_no = 0
    year_total = 0
    birth_year = 2000
    
    analysed_name = ''
    chaldean_total = 0
    chaldean_root = 0
    chaldean_breakdown = ''
    pythagorean_total = 0
    pythagorean_root = 0
    pythagorean_breakdown = ''
    name_advice = ''
    pyramid_data = []
    dob_pyramid_data = []
    mobile_pyramid_data = []
    
    compat = {}
    lucky_details = {}
    astrology_props = {}
    missing_remedies_list = []
    kua_number = 0
    mobile_data = None
    input_mobile = ''
    
    p2_name = ''
    p2_dob = ''
    p2_birth_no = 0
    partner_compatibility = ''
    
    p_year_val = 0
    p_year_desc = ''
    p_month_val = 0
    p_month_desc = ''
    current_year = datetime.now().year
    current_month = datetime.now().month

    birth_strength_avg = 0.0
    birth_lifestyle = ''
    name_sound_freq = 0
    name_lifestyle = ''
    
    if request.method == 'POST':
        dob = request.form.get('dob', '').strip()
        analysed_name = request.form.get('analysed_name', '').strip()
        input_mobile = request.form.get('input_mobile', '').strip()
        
        p2_name = request.form.get('p2_name', '').strip()
        p2_dob = request.form.get('p2_dob', '').strip()
        
        if dob:
            clean_digits = [int(ch) for ch in dob if ch.isdigit()]
            
            if len(clean_digits) >= 8:
                day_val = clean_digits[0]*10 + clean_digits[1]
                raw_birth_no = clean_digits[0] if day_val > 31 else day_val
                birth_no = reduce_to_single(raw_birth_no)
                
                destiny_total = sum(clean_digits)
                destiny_no = reduce_to_single(destiny_total)
                
                birth_year = clean_digits[4]*1000 + clean_digits[5]*100 + clean_digits[6]*10 + clean_digits[7]
                year_total = sum(clean_digits[4:8])
                year_no = reduce_to_single(year_total)
                
                birth_day_sum = reduce_to_single(day_val)
                birth_month_sum = reduce_to_single(clean_digits[2]*10 + clean_digits[3])
                curr_yr_sum = reduce_to_single(current_year)
                p_year_val = reduce_to_single(birth_day_sum + birth_month_sum + curr_yr_sum)
                p_year_desc = PERSONAL_YEAR_PREDICTIONS.get(p_year_val, 'ವಿಶೇಷ ಬದಲಾವಣೆಗಳ ವರ್ಷ.')
                
                curr_mth_sum = reduce_to_single(current_month)
                p_month_val = reduce_to_single(p_year_val + curr_mth_sum)
                p_month_desc = PERSONAL_YEAR_PREDICTIONS.get(p_month_val, 'ಪ್ರಸ್ತುತ ತಿಂಗಳ ಅನುಕೂಲಕರ ಫಲ.')

            # ವೇದಿಕ್ ಗ್ರಿಡ್ ಲಾಜಿಕ್: 
            # 1) ಜನ್ಮ ದಿನಾಂಕದ ಎಲ್ಲಾ ನೈಜ ಅಂಕಿಗಳು
            # 2) ಬರ್ತ್ ನಂಬರ್ ಡಬಲ್ ಡಿಜಿಟ್ ಆಗಿದ್ದು ಸಿಂಗಲ್ ಆಗಿ ಕನ್ವರ್ಟ್ ಆಗಿದ್ದರೆ ಮಾತ್ರ ಸೇರಿಸುವುದು
            # 3) ಭಾಗ್ಯ ಸಂಖ್ಯೆ (Destiny No) ಕಡ್ಡಾಯವಾಗಿ ಸೇರಿಸುವುದು
            grid_numbers = [d for d in clean_digits if d != 0]
            
            if raw_birth_no > 9 and birth_no > 0:
                grid_numbers.append(birth_no)
                
            if destiny_no > 0:
                grid_numbers.append(destiny_no)
            
            counts = {}
            for d in grid_numbers:
                if d != 0:
                    counts[d] = counts.get(d, 0) + 1
                    present_numbers.add(d)
                    
            for num in range(1, 10):
                if num in counts:
                    formatted_grid[num] = str(num) * counts[num]
                else:
                    formatted_grid[num] = '-'
                    missing_numbers.append(num)
                    
            astrology_props = NUMBER_PROPS.get(birth_no, NUMBER_PROPS[1])
            kua_number = calculate_kua(birth_year)
            dob_pyramid_data = calculate_dob_pyramid(dob)
            grid_yogas = analyze_vedic_grid_yogas(present_numbers)
            
            for m in missing_numbers:
                missing_remedies_list.append({'num': m, 'remedy': MISSING_REMEDIES.get(m, '')})

            total_deg = sum(BIRTH_DEGREES.get(d, 0) for d in grid_numbers)
            total_serial_no = len(grid_numbers)
            if total_serial_no > 0:
                birth_strength_avg = round(total_deg / total_serial_no, 2)
            else:
                birth_strength_avg = 0.0

            if birth_strength_avg <= 30:
                birth_lifestyle = 'Below average life'
            elif birth_strength_avg <= 35:
                birth_lifestyle = 'Average life'
            elif birth_strength_avg <= 40:
                birth_lifestyle = 'Above Average life'
            else:
                birth_lifestyle = 'Idented & purposeful life'
                
        if analysed_name:
            upper_name = analysed_name.upper()
            c_sum = 0
            c_parts = []
            for ch in upper_name:
                if ch in CHALDEAN_MAP:
                    val = CHALDEAN_MAP[ch]
                    c_sum += val
                    c_parts.append(f"{ch}({val})")
            chaldean_total = c_sum
            chaldean_root = reduce_to_single(c_sum)
            chaldean_breakdown = " + ".join(c_parts)
            name_advice = get_name_correction_advice(chaldean_total)
            pyramid_data = calculate_pyramid(analysed_name)
            
            p_sum = 0
            p_parts = []
            for ch in upper_name:
                if ch in PYTHAGOREAN_MAP:
                    val = PYTHAGOREAN_MAP[ch]
                    p_sum += val
                    p_parts.append(f"{ch}({val})")
            pythagorean_total = p_sum
            pythagorean_root = reduce_to_single(p_sum)
            pythagorean_breakdown = " + ".join(p_parts)

            n_freq_sum = 0
            for ch in upper_name:
                if ch in NAME_FREQ_MAP:
                    n_freq_sum += NAME_FREQ_MAP[ch]
            name_sound_freq = n_freq_sum

            if name_sound_freq <= 500:
                name_lifestyle = 'Below average life'
            elif name_sound_freq <= 1000:
                name_lifestyle = 'Average life'
            elif name_sound_freq <= 1500:
                name_lifestyle = 'Above Average life'
            elif name_sound_freq <= 2000:
                name_lifestyle = 'Spending & Comfortable'
            else:
                name_lifestyle = 'Celebrity & Identified life'
            
        if p2_dob:
            p2_clean = [int(ch) for ch in p2_dob if ch.isdigit()]
            if len(p2_clean) >= 8:
                p2_day_val = p2_clean[0]*10 + p2_clean[1]
                p2_birth_no = reduce_to_single(p2_clean[0]) if p2_day_val > 31 else reduce_to_single(p2_day_val)
                rel_check = get_relation(birth_no, p2_birth_no)
                partner_compatibility = f"ವ್ಯಕ್ತಿ 1 ರ ಮೂಲ ಸಂಖ್ಯೆ ({birth_no}) ಮತ್ತು ಪಾಲುದಾರರ ಮೂಲ ಸಂಖ್ಯೆ ({p2_birth_no}) ನಡುವಿನ ಹೊಂದಾಣಿಕೆ: {rel_check}"
            
        if dob and analysed_name:
            compat = {
                'c_birth': get_relation(chaldean_root, birth_no),
                'c_destiny': get_relation(chaldean_root, destiny_no),
                'c_year': get_relation(chaldean_root, year_no),
                'p_birth': get_relation(pythagorean_root, birth_no),
                'p_destiny': get_relation(pythagorean_root, destiny_no),
                'p_year': get_relation(pythagorean_root, year_no),
            }
            
            b_friends = set(RELATIONS.get(birth_no, {}).get('friends', []))
            d_friends = set(RELATIONS.get(destiny_no, {}).get('friends', []))
            common_lucky = sorted(list(b_friends.intersection(d_friends)))
            lucky_details = {
                'birth_friends': ", ".join(map(str, sorted(list(b_friends)))),
                'destiny_friends': ", ".join(map(str, sorted(list(d_friends)))),
                'common': ", ".join(map(str, common_lucky)) if common_lucky else "1, 5, 6"
            }
            
        if input_mobile:
            mobile_data = analyze_mobile_advanced(input_mobile)
            mobile_pyramid_data = calculate_mobile_pyramid(input_mobile)

    return render_template('calculator.html', user_name=user_name, vedic_grid=vedic_grid, formatted_grid=formatted_grid, missing_numbers=missing_numbers, grid_yogas=grid_yogas, dob=dob, birth_no=birth_no, destiny_no=destiny_no, destiny_total=destiny_total, year_no=year_no, year_total=year_total, analysed_name=analysed_name, chaldean_total=chaldean_total, chaldean_root=chaldean_root, chaldean_breakdown=chaldean_breakdown, pythagorean_total=pythagorean_total, pythagorean_root=pythagorean_root, pythagorean_breakdown=pythagorean_breakdown, name_advice=name_advice, pyramid_data=pyramid_data, dob_pyramid_data=dob_pyramid_data, mobile_pyramid_data=mobile_pyramid_data, compat=compat, lucky_details=lucky_details, astrology_props=astrology_props, missing_remedies_list=missing_remedies_list, kua_number=kua_number, input_mobile=input_mobile, mobile_data=mobile_data, p_year_val=p_year_val, p_year_desc=p_year_desc, p_month_val=p_month_val, p_month_desc=p_month_desc, current_year=current_year, p2_name=p2_name, p2_dob=p2_dob, p2_birth_no=p2_birth_no, partner_compatibility=partner_compatibility, birth_strength_avg=birth_strength_avg, birth_lifestyle=birth_lifestyle, name_sound_freq=name_sound_freq, name_lifestyle=name_lifestyle)

if __name__ == '__main__':
    app.run(debug=True)