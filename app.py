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

RASHIS = [
    'Mesha', 'Vrishabha', 'Mithuna', 'Karka', 'Simha', 'Kanya',
    'Tula', 'Vrishchika', 'Dhanu', 'Makara', 'Kumbha', 'Meena'
]

RASHI_LABELS = {
    'kn': {
        'Mesha': 'ಮೇಷ (Mesha)', 'Vrishabha': 'ವೃಷಭ (Vrishabha)', 'Mithuna': 'ಮಿಥುನ (Mithuna)',
        'Karka': 'ಕರ್ಕಾಟಕ (Karka)', 'Simha': 'ಸಿಂಹ (Simha)', 'Kanya': 'ಕನ್ಯಾ (Kanya)',
        'Tula': 'ತುಲಾ (Tula)', 'Vrishchika': 'ವೃಶ್ಚಿಕ (Vrishchika)', 'Dhanu': 'ಧನುಸ್ಸು (Dhanu)',
        'Makara': 'ಮಕರ (Makara)', 'Kumbha': 'ಕುಂಭ (Kumbha)', 'Meena': 'ಮೀನ (Meena)'
    },
    'en': {r: r for r in RASHIS},
    'ta': {
        'Mesha': 'மேஷம் (Mesha)', 'Vrishabha': 'ரிஷபம் (Vrishabha)', 'Mithuna': 'மிதுனம் (Mithuna)',
        'Karka': 'கடகம் (Karka)', 'Simha': 'சிம்மம் (Simha)', 'Kanya': 'கன்னி (Kanya)',
        'Tula': 'துலாம் (Tula)', 'Vrishchika': 'விருச்சிகம் (Vrishchika)', 'Dhanu': 'தனுசு (Dhanu)',
        'Makara': 'மகரம் (Makara)', 'Kumbha': 'கும்பம் (Kumbha)', 'Meena': 'மீனம் (Meena)'
    },
    'te': {
        'Mesha': 'మేషం (Mesha)', 'Vrishabha': 'వృషభం (Vrishabha)', 'Mithuna': 'మిథునం (మిథునం)',
        'Karka': 'కర్కాటకం (Karka)', 'Simha': 'సింహం (Simha)', 'Kanya': 'కన్య (Kanya)',
        'Tula': 'తుల (Tula)', 'Vrishchika': 'వృశ్చికం (Vrishchika)', 'Dhanu': 'ధనుస్సు (Dhanu)',
        'Makara': 'మకరం (Makara)', 'Kumbha': 'కుంభం (Kumbha)', 'Meena': 'మీనం (Meena)'
    },
    'hi': {
        'Mesha': 'मेष (Mesha)', 'Vrishabha': 'वृषभ (Vrishabha)', 'Mithuna': 'मिथुन (Mithuna)',
        'Karka': 'कर्क (Karka)', 'Simha': 'सिंह (Simha)', 'Kanya': 'कन्या (Kanya)',
        'Tula': 'तुला (Tula)', 'Vrishchika': 'वृश्चिक (Vrishchika)', 'Dhanu': 'धनु (Dhanu)',
        'Makara': 'मकर (Makara)', 'Kumbha': 'कुंभ (Kumbha)', 'Meena': 'मीन (Meena)'
    }
}

NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Pubba', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swathi', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Moola', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta',
    'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

NAKSHATRA_LABELS = {
    'kn': {
        'Ashwini': 'ಅಶ್ವಿನಿ (Ashwini)', 'Bharani': 'ಭರಣಿ (Bharani)', 'Krittika': 'ಕೃತ್ತಿಕಾ (Krittika)',
        'Rohini': 'ರೋಹಿಣಿ (Rohini)', 'Mrigashira': 'ಮೃಗಶಿರ (Mrigashira)', 'Ardra': 'ಆರ್ದ್ರಾ (Ardra)',
        'Punarvasu': 'ಪುನರ್ವಸು (Punarvasu)', 'Pushya': 'ಪುಷ್ಯ (Pushya)', 'Ashlesha': 'ಆಶ್ಲೇಷ (Ashlesha)',
        'Magha': 'ಮಘಾ (Magha)', 'Pubba': 'ಹುಬ್ಬ / ಪೂರ್ವಾ ಫಲ್ಗುಣಿ (Pubba)', 'Uttara Phalguni': 'ಉತ್ತರಾ ಫಲ್ಗುಣಿ (Uttara Phalguni)',
        'Hasta': 'ಹಸ್ತ (Hasta)', 'Chitra': 'ಚಿತ್ರಾ (Chitra)', 'Swathi': 'ಸ್ವಾತಿ (Swathi)',
        'Vishakha': 'ವಿಶಾಖಾ (Vishakha)', 'Anuradha': 'ಅನುರಾಧಾ (Anuradha)', 'Jyeshtha': 'ಜ್ಯೇಷ್ಠಾ (Jyeshtha)',
        'Moola': 'ಮೂಲ (Moola)', 'Purva Ashadha': 'ಪೂರ್ವಾಷಾಢ (Purva Ashadha)', 'Uttara Ashadha': 'ಉತ್ತರಾಷಾಢ (Uttara Ashadha)',
        'Shravana': 'ಶ್ರವಣ (Shravana)', 'Dhanishta': 'ಧನಿಷ್ಠಾ (Dhanishta)', 'Shatabhisha': 'ಶತಭಿಷಾ (Shatabhisha)',
        'Purva Bhadrapada': 'ಪೂರ್ವಾಭಾದ್ರ (Purva Bhadrapada)', 'Uttara Bhadrapada': 'ಉತ್ತರಾಭಾದ್ರ (Uttara Bhadrapada)', 'Revati': 'ರೇವತಿ (Revati)'
    },
    'en': {n: n for n in NAKSHATRAS},
    'ta': {
        'Ashwini': 'அஸ்வினி (Ashwini)', 'Bharani': 'பரணி (Bharani)', 'Krittika': 'கார்த்திகை (Krittika)',
        'Rohini': 'ரோகிணி (Rohini)', 'Mrigashira': 'மிருகசீரிடம் (Mrigashira)', 'Ardra': 'திருவாதிரை (Ardra)',
        'Punarvasu': 'புனர்பூசம் (Punarvasu)', 'Pushya': 'பூசம் (Pushya)', 'Ashlesha': 'ஆயில்யம் (Ashlesha)',
        'Magha': 'மகம் (Magha)', 'Pubba': 'பூரம் / புப்பா (Pubba)', 'Uttara Phalguni': 'உத்திரம் (Uttara Phalguni)',
        'Hasta': 'அஸ்தம் (Hasta)', 'Chitra': 'சித்திரை (Chitra)', 'Swathi': 'சுவாதி (Swathi)',
        'Vishakha': 'விசாகம் (Vishakha)', 'Anuradha': 'அனுஷம் (Anuradha)', 'Jyeshtha': 'கேட்டை (Jyeshtha)',
        'Moola': 'மூலம் (Moola)', 'Purva Ashadha': 'பூராடம் (Purva Ashadha)', 'Uttara Ashadha': 'உத்திராடம் (Uttara Ashadha)',
        'Shravana': 'திருவோணம் (Shravana)', 'Dhanishta': 'அவிட்டம் (Dhanishta)', 'Shatabhisha': 'சதயம் (Shatabhisha)',
        'Purva Bhadrapada': 'பூரட்டாதி (Purva Bhadrapada)', 'Uttara Bhadrapada': 'உத்திரட்டாதி (Uttara Bhadrapada)', 'Revati': 'ரேவதி (Revati)'
    },
    'te': {
        'Ashwini': 'అశ్విని (Ashwini)', 'Bharani': 'భరణి (Bharani)', 'Krittika': 'కృత్తిక (Krittika)',
        'Rohini': 'రోహిణి (Rohini)', 'Mrigashira': 'మృగశిర (Mrigashira)', 'Ardra': 'ఆర్ద్ర (Ardra)',
        'Punarvasu': 'పునర్వసు (Punarvasu)', 'Pushya': 'పుష్యమి (Pushya)', 'Ashlesha': 'ఆశ్లేష (Ashlesha)',
        'Magha': 'మఖ (Magha)', 'Pubba': 'పుబ్బ (Pubba)', 'Uttara Phalguni': 'ఉత్తర (Uttara Phalguni)',
        'Hasta': 'హస్త (Hasta)', 'Chitra': 'చిత్త (Chitra)', 'Swathi': 'స్వాతి (Swathi)',
        'Vishakha': 'విశాఖ (Vishakha)', 'Anuradha': 'అనూరాధ (Anuradha)', 'Jyeshtha': 'జ్యేష్ఠ (Jyeshtha)',
        'Moola': 'మూల (Moola)', 'Purva Ashadha': 'పూర్వాషాఢ (Purva Ashadha)', 'Uttara Ashadha': 'ఉత్తరాషాఢ (Uttara Ashadha)',
        'Shravana': 'శ్రవణం (Shravana)', 'Dhanishta': 'ధనిష్ఠ (Dhanishta)', 'Shatabhisha': 'శతభిషం (Shatabhisha)',
        'Purva Bhadrapada': 'పూర్వాభాద్ర (Purva Bhadrapada)', 'Uttara Bhadrapada': 'ఉత్తరాభాద్ర (Uttara Bhadrapada)', 'Revati': 'రేవతి (Revati)'
    },
    'hi': {
        'Ashwini': 'अश्विनी (Ashwini)', 'Bharani': 'भरणी (Bharani)', 'Krittika': 'कृत्तिका (Krittika)',
        'Rohini': 'रोहिणी (Rohini)', 'Mrigashira': 'मृगशिरा (Mrigashira)', 'Ardra': 'आर्द्रा (Ardra)',
        'Punarvasu': 'पुनर्वसु (Punarvasu)', 'Pushya': 'पुष्य (Pushya)', 'Ashlesha': 'अश्लेषा (Ashlesha)',
        'Magha': 'मघा (Magha)', 'Pubba': 'पूर्वा फाल्गुनी / पुब्बा (Pubba)', 'Uttara Phalguni': 'उत्तरा फाल्गुनी',
        'Hasta': 'हस्त (Hasta)', 'Chitra': 'चित्रा (Chitra)', 'Swathi': 'स्वाती (Swathi)',
        'Vishakha': 'विशाखा (Vishakha)', 'Anuradha': 'अनुराधा (Anuradha)', 'Jyeshtha': 'ज्येष्ठा (Jyeshtha)',
        'Moola': 'मूल (Moola)', 'Purva Ashadha': 'पूर्वाषाढ़ा (Purva Ashadha)', 'Uttara Ashadha': 'उत्तराषाढ़ा',
        'Shravana': 'श्रवण (Shravana)', 'Dhanishta': 'धनिष्ठा (Dhanishta)', 'Shatabhisha': 'शतभिषा (Shatabhisha)',
        'Purva Bhadrapada': 'पूर्वाभाद्रपद', 'Uttara Bhadrapada': 'उत्तराभाद्रपद', 'Revati': 'रेवती (Revati)'
    }
}

TARA_NAMES_LANG = {
    'kn': {
        1: ('ಜನ್ಮ ತಾರೆ (Janma)', 'ಶುಭ/ಮಿಶ್ರ - ದೇಹ/ಆರೋಗ್ಯ ಗಮನ ಅಗತ್ಯ'),
        2: ('ಸಂಪತ್ ತಾರೆ (Sampat)', 'ಅತ್ಯುತ್ತಮ ಶುಭ - ಸಂಪತ್ತು ಮತ್ತು ಲಾಭ'),
        3: ('ವಿಪತ್ ತಾರೆ (Vipat)', 'ಅಶುಭ / ಮಧಭೂಡ - ಅಡೆತಡೆ, ಎಚ್ಚರಿಕೆ ಅಗತ್ಯ'),
        4: ('ಕ್ಷೇಮ ತಾರೆ (Kshema)', 'ಅತ್ಯುತ್ತಮ ಶುಭ - ಸುಖ, ನೆಮ್ಮದಿ ಮತ್ತು ರಕ್ಷಣೆ'),
        5: ('ಪ್ರತ್ಯರಿ ತಾರೆ (Pratyari)', 'ಅಶುಭ / ಮಧಭೂಡ - ವಿರೋಧ, ತೊಂದರೆ ಎಚ್ಚರಿಕೆ'),
        6: ('ಸಾಧಕ ತಾರೆ (Sadhaka)', 'ಅತ್ಯುತ್ತಮ ಶುಭ - ಕಾರ್ಯಸಿದ್ಧಿ ಮತ್ತು ಯಶಸ್ಸು'),
        7: ('ವಧೆ ತಾರೆ (Vadha)', 'ಅಶುಭ / ಮಧಭೂಡ - ತೀವ್ರ ಎಚ್ಚರಿಕೆ ಮತ್ತು ಶಾಂತಿ ಅಗತ್ಯ'),
        8: ('ಮಿತ್ರ ತಾರೆ (Mitra)', 'ಶುಭ - ಸ್ನೇಹ, ಸಹಕಾರ ಮತ್ತು ಬೆಂಬಲ'),
        9: ('ಅತಿಮಿತ್ರ ತಾರೆ (Atimitra)', 'ಅತ್ಯುತ್ತಮ ಶುಭ - ಮಹಾ ಯಶಸ್ಸು ಮತ್ತು ಅನುಕೂಲ')
    },
    'en': {
        1: ('Janma Tara (1st)', 'Mixed / Caution - Pay attention to health & energy'),
        2: ('Sampat Tara (2nd)', 'Auspicious - Wealth, gain, and prosperity'),
        3: ('Vipat Tara (3rd)', 'Inauspicious / Madabhuda - Obstacles & caution'),
        4: ('Kshema Tara (4th)', 'Auspicious - Comfort, safety, and well-being'),
        5: ('Pratyari Tara (5th)', 'Inauspicious / Madabhuda - Opposition & hurdles'),
        6: ('Sadhaka Tara (6th)', 'Auspicious - Achievement and completion of tasks'),
        7: ('Vadha Tara (7th)', 'Inauspicious / Madabhuda - High caution advised'),
        8: ('Mitra Tara (8th)', 'Auspicious - Support, friendship, and cooperation'),
        9: ('Atimitra Tara (9th)', 'Very Auspicious - Strong support and success')
    },
    'ta': {
        1: ('ஜன்ம தாரை (1)', 'மிஸ்ர / கவனம் - உடல் நலம் மற்றும் ஆற்றலில் கவனம்'),
        2: ('சம்பத் தாரை (2)', 'சுபம் - செல்வம், லாபம் மற்றும் வளம்'),
        3: ('விபத் தாரை (3)', 'அசுபம் / மதபூட - தடைகள், எச்சரிக்கை தேவை'),
        4: ('க்ஷேம தாரை (4)', 'சுபம் - நலம், பாதுகாப்பு மற்றும் அமைதி'),
        5: ('ப்ரத்யரி தாரை (5)', 'அசுபம் / மதபூட - எதிர்ப்பு மற்றும் தடங்கல்'),
        6: ('சாதக தாரை (6)', 'சுபம் - காரிய வெற்றி மற்றும் சித்தி'),
        7: ('வதை தாரை (7)', 'அசுபம் / மதபூட - கூடுதல் எச்சரிக்கை அவசியம்'),
        8: ('மித்ர தாரை (8)', 'சுபம் - நட்பு, உதவி மற்றும் ஒத்துழைப்பு'),
        9: ('அதிமித்ர தாரை (9)', 'மிகச் சுபம் - சிறந்த வெற்றி மற்றும் ஆதரவு')
    },
    'te': {
        1: ('జన్మ తార (1)', 'మిశ్ర / జాగ్రత్త - ఆరోగ్యం మరియు శక్తిపై శ్రద్ధ అవసరం'),
        2: ('సంపత్ తార (2)', 'శుభం - సంపద, లాభం మరియు అభివృద్ధి'),
        3: ('విపత్ తార (3)', 'అశుభం / మధభూడ - ఆటంకాలు, జాగ్రత్త అవసరం'),
        4: ('క్షేమ తార (4)', 'శుభం - రక్షణ, సౌఖ్యం మరియు ప్రశాంతత'),
        5: ('ప్రత్యరి తార (5)', 'అశుభం / మధభూడ - వ్యతిరేకత, అడ్డంకుల జాగ్రత్త'),
        6: ('సాధక తార (6)', 'శుభం - కార్యసిద్ధి మరియు విజయం'),
        7: ('వధ తార (7)', 'అశుభం / మధభూడ - అధిక జాగ్రత్త అవసరం'),
        8: ('మిత్ర తార (8)', 'శుభం - స్నేహం, సహకారం మరియు తోడ్పాటు'),
        9: ('అతిమిత్ర తార (9)', 'అత్యంత శుభం - మంచి విజయం మరియు అనుకూలత')
    },
    'hi': {
        1: ('जन्म तारा (1)', 'मिश्र / ध्यान दें - स्वास्थ्य और ऊर्जा पर ध्यान दें'),
        2: ('संपत्ति तारा (2)', 'शुभ - धन, लाभ और समृद्धि'),
        3: ('विपत्ति तारा (3)', 'अशुभ / मधभूड़ - बाधाएं, सावधानी आवश्यक'),
        4: ('क्षेम तारा (4)', 'शुभ - सुख, सुरक्षा और शांति'),
        5: ('प्रत्यरि तारा (5)', 'अशुभ / मधभूड़ - विरोध और अवरोध से सतर्क रहें'),
        6: ('साधक तारा (6)', 'शुभ - कार्य सिद्धि और सफलता'),
        7: ('वध तारा (7)', 'अशुभ / मधभूड़ - विशेष सावधानी आवश्यक'),
        8: ('मित्र तारा (8)', 'शुभ - मित्रता, सहयोग और सहायता'),
        9: ('अतिमित्र तारा (9)', 'अत्यधिक शुभ - उत्तम सफलता और अनुकूलता')
    }
}

BAV_OFFSETS = {
    'Sun': {1, 2, 4, 7, 8, 9, 10, 11},
    'Moon': {3, 6, 7, 8, 10, 11},
    'Mars': {1, 2, 4, 7, 8, 10, 11},
    'Mercury': {5, 6, 9, 11, 12},
    'Jupiter': {5, 6, 7, 9, 10, 11},
    'Venus': {6, 7, 8, 9, 11, 12},
    'Saturn': {3, 5, 6, 10, 11}
}

NUMBER_PROPS_LANG = {
    'kn': {
        1: {'colors': 'ಹಳದಿ, ಕಿತ್ತಳೆ, ಗೋಲ್ಡನ್', 'direction': 'ಪೂರ್ವ', 'gemstone': 'ಕೆಂಪು ಮಾಣಿಕ್ಯ', 'profession': 'ಸರ್ಕಾರಿ ಉದ್ಯೋಗ, ರಾಜಕೀಯ, ನಾಯಕತ್ವ', 'lucky_days': 'ಭಾನುವಾರ, ಗುರುವಾರ'},
        2: {'colors': 'ಬಿಳಿ, ಹಸಿರು, ಬೆಳ್ಳಿ ಬಣ್ಣ', 'direction': 'ವಾಯುವ್ಯ', 'gemstone': 'ಮುತ್ತು / ಚಂದ್ರಕಾಂತ ರತ್ನ', 'profession': 'ಕಲಾವಿದರು, ಪ್ರಯಾಣ, ದ್ರವ ಪದಾರ್ಥಗಳು', 'lucky_days': 'ಸೋಮವಾರ, ಬುಧವಾರ'},
        3: {'colors': 'ಹಳದಿ, ಗುಲಾಬಿ, ನೇರಳೆ', 'direction': 'ಈಶಾನ್ಯ', 'gemstone': 'ಹಳದಿ ಪುಷ್ಯರಾಗ', 'profession': 'ಶಿಕ್ಷಣ, ಬೋಧನೆ, ಸಲಹೆಗಾರರು', 'lucky_days': 'ಗುರುವಾರ, ಮಂಗಳವಾರ'},
        4: {'colors': 'ಬೂದು, ನೀಲಿ, ಮಣ್ಣಿನ ಬಣ್ಣ', 'direction': 'ನೈಋತ್ಯ', 'gemstone': 'ಗೋಮೇಧಿಕ / ನೀಲಮಣಿ', 'profession': 'ತಂತ್ರಜ್ಞಾನ, ಸಾಫ್ಟ್‌ವೇರ್, ಇಂಜಿನಿಯರಿಂಗ್', 'lucky_days': 'ಬುಧವಾರ, ಶನಿವಾರ'},
        5: {'colors': 'ಹಸಿರು, ತಿಳಿ ಬಣ್ಣಗಳು', 'direction': 'ಉತ್ತರ', 'gemstone': 'ಪಚ್ಚೆ', 'profession': 'ವ್ಯವಹಾರ, ಮಾರ್ಕೆಟಿಂಗ್, ಷೇರು ಮಾರುಕಟ್ಟೆ', 'lucky_days': 'ಬುಧವಾರ, ಶುಕ್ರವಾರ'},
        6: {'colors': 'ಬಿಳಿ, ತಿಳಿ ನೀಲಿ, ಗುಲಾಬಿ', 'direction': 'ಆಗ್ನೇಯ', 'gemstone': 'ವೈಡೂರ್ಯ / ವಜ್ರ', 'profession': 'ಸೌಂದರ್ಯ ವರ್ಧಕಗಳು, ಫ್ಯಾಷನ್, ಸಿನಿಮಾ', 'lucky_days': 'ಶುಕ್ರವಾರ, ಬುಧವಾರ'},
        7: {'colors': 'ಸ್ಮೋಕಿ ಗ್ರೇ, ಬಿಳಿ, ಹಸಿರು', 'direction': 'ಈಶಾನ್ಯ / ವಾಯುವ್ಯ', 'gemstone': 'ಬೆಕ್ಕು ಕಣ್ಣಿನ ರತ್ನ', 'profession': 'ಆಧ್ಯಾತ್ಮ, ಸಂಶೋಧನೆ, ಜ್ಯೋತಿಷ್ಯ', 'lucky_days': 'ಸೋಮವಾರ, ಗುರುವಾರ'},
        8: {'colors': 'ಕಪ್ಪು, ಗಾಢ ನೀಲಿ, ದಟ್ಟ ಬೂದು', 'direction': 'ಪಶ್ಚಿಮ', 'gemstone': 'ನೀಲಮಣಿ', 'profession': 'ವೈದ್ಯರು, ನರ್ಸ್‌ಗಳು, ಕಬ್ಬಿಣ/ಉಕ್ಕು ಉದ್ಯಮ', 'lucky_days': 'ಶನಿವಾರ, ಬುಧವಾರ'},
        9: {'colors': 'ಕೆಂಪು, ಗುಲಾಬಿ, ಮರೂನ್', 'direction': 'ದಕ್ಷಿಣ', 'gemstone': 'ಕೆಂಪು ಹವಳ', 'profession': 'ರಕ್ಷಣೆ, ಪೊಲೀಸ್, ಸೈನ್ಯ, ರಿಯಲ್ ಎಸ್ಟೇಟ್', 'lucky_days': 'ಮಂಗಳವಾರ, ಭಾನುವಾರ'}
    },
    'en': {
        1: {'colors': 'Yellow, Orange, Golden', 'direction': 'East', 'gemstone': 'Ruby', 'profession': 'Government, Politics, Leadership', 'lucky_days': 'Sunday, Thursday'},
        2: {'colors': 'White, Green, Silver', 'direction': 'North-West', 'gemstone': 'Pearl / Moonstone', 'profession': 'Arts, Travel, Liquids', 'lucky_days': 'Monday, Wednesday'},
        3: {'colors': 'Yellow, Pink, Purple', 'direction': 'North-East', 'gemstone': 'Yellow Sapphire', 'profession': 'Education, Teaching, Consulting', 'lucky_days': 'Thursday, Tuesday'},
        4: {'colors': 'Grey, Blue, Earthy', 'direction': 'South-West', 'gemstone': 'Hessonite / Blue Sapphire', 'profession': 'Technology, Software, Engineering', 'lucky_days': 'Wednesday, Saturday'},
        5: {'colors': 'Green, Light Shades', 'direction': 'North', 'gemstone': 'Emerald', 'profession': 'Business, Marketing, Stock Market', 'lucky_days': 'Wednesday, Friday'},
        6: {'colors': 'White, Light Blue, Pink', 'direction': 'South-East', 'gemstone': 'Diamond / Opal', 'profession': 'Beauty, Fashion, Cinema', 'lucky_days': 'Friday, Wednesday'},
        7: {'colors': 'Smoky Grey, White, Green', 'direction': 'North-East / North-West', 'gemstone': "Cat's Eye", 'profession': 'Spirituality, Research, Astrology', 'lucky_days': 'Monday, Thursday'},
        8: {'colors': 'Black, Dark Blue, Charcoal', 'direction': 'West', 'gemstone': 'Blue Sapphire', 'profession': 'Doctors, Nurses, Iron & Steel', 'lucky_days': 'Saturday, Wednesday'},
        9: {'colors': 'Red, Pink, Maroon', 'direction': 'South', 'gemstone': 'Red Coral', 'profession': 'Defence, Police, Army, Real Estate', 'lucky_days': 'Tuesday, Sunday'}
    },
    'ta': {
        1: {'colors': 'மஞ்சள், ஆரஞ்சு, பொன்னிறம்', 'direction': 'கிழக்கு', 'gemstone': 'மாணிக்கம்', 'profession': 'அரசுப் பணி, அரசியல், தலைமை', 'lucky_days': 'ஞாயிறு, வியாழன்'},
        2: {'colors': 'வெள்ளை, பச்சை, வெள்ளி', 'direction': 'வடமேற்கு', 'gemstone': 'முத்து / சந்திரகாந்தம்', 'profession': 'கலை, பயணம், திரவப் பொருட்கள்', 'lucky_days': 'திங்கள், புதன்'},
        3: {'colors': 'மஞ்சள், இளஞ்சிவப்பு, ஊதா', 'direction': 'வடகிழக்கு', 'gemstone': 'கனகபுஷ்பராகம்', 'profession': 'கல்வி, கற்பித்தல், ஆலோசனை', 'lucky_days': 'வியாழன், செவ்வாய்'},
        4: {'colors': 'சாம்பல், நீலம், மண் நிறம்', 'direction': 'தென்மேற்கு', 'gemstone': 'கோமேதகம் / நீலம்', 'profession': 'தொழில்நுட்பம், மென்பொருள், பொறியியல்', 'lucky_days': 'புதன், சனி'},
        5: {'colors': 'பச்சை, வெளிர் நிறங்கள்', 'direction': 'வடக்கு', 'gemstone': 'மரகதம்', 'profession': 'வணிகம், சந்தைப்படுத்தல், பங்குச் சந்தை', 'lucky_days': 'புதன், வெள்ளி'},
        6: {'colors': 'வெள்ளை, வெளிர் நீலம், இளஞ்சிவப்பு', 'direction': 'தென்கிழக்கு', 'gemstone': 'வைரம்', 'profession': 'அழகு, ஃபேஷன், சினிமா', 'lucky_days': 'வெள்ளி, புதன்'},
        7: {'colors': 'சாம்பல், வெள்ளை, பச்சை', 'direction': 'வடகிழக்கு / வடமேற்கு', 'gemstone': 'வைடூரியம்', 'profession': 'ஆன்மீகம், ஆராய்ச்சி, ஜோதிடம்', 'lucky_days': 'திங்கள், வியாழன்'},
        8: {'colors': 'கருப்பு, அடர் நீலம், சாம்பல்', 'direction': 'மேற்கு', 'gemstone': 'நீலக்கல்', 'profession': 'மருத்துவர்கள், செவிலியர்கள், இரும்பு & எஃகு', 'lucky_days': 'சனி, புதன்'},
        9: {'colors': 'சிவப்பு, இளஞ்சிவப்பு, மெரூன்', 'direction': 'தெற்கு', 'gemstone': 'பவளம்', 'profession': 'பாதுகாப்பு, காவல், இராணுவம், ரியல் எஸ்டேட்', 'lucky_days': 'செவ்வாய், ஞாயிறு'}
    },
    'te': {
        1: {'colors': 'పసుపు, నారింజ, బంగారు', 'direction': 'తూర్పు', 'gemstone': 'కెంపు', 'profession': 'ప్రభుత్వ ఉద్యోగం, రాజకీయాలు, నాయకత్వం', 'lucky_days': 'ఆదివారం, గురువారం'},
        2: {'colors': 'తెలుపు, ఆకుపచ్చ, వెండి', 'direction': 'వాయువ్యం', 'gemstone': 'ముత్యం / చంద్రకాంతం', 'profession': 'కళలు, ప్రయాణాలు, ద్రవ పదార్థాలు', 'lucky_days': 'సోమవారం, బుధవారం'},
        3: {'colors': 'పసుపు, గులాబీ, ఊదా', 'direction': 'ఈశాన్యం', 'gemstone': 'కనకపుష్యరాగం', 'profession': 'విద్య, బోధన, సలహాలు', 'lucky_days': 'గురువారం, మంగళవారం'},
        4: {'colors': 'బూడిద, నీలం, మట్టి రంగు', 'direction': 'నైరుతి', 'gemstone': 'గోమేధికం / నీలం', 'profession': 'టెక్నాలజీ, సాఫ్ట్‌వేర్, ఇంజనీరింగ్', 'lucky_days': 'బుధవారం, శనివారం'},
        5: {'colors': 'ఆకుపచ్చ, లేత రంగులు', 'direction': 'ఉత్తరం', 'gemstone': 'పచ్చ', 'profession': 'వ్యాపారం, మార్కెటింగ్, స్టాక్ మార్కెట్', 'lucky_days': 'బుధవారం, శుక్రవారం'},
        6: {'colors': 'తెలుపు, లేత నీలం, గులాబీ', 'direction': 'ఆగ్నేయం', 'gemstone': 'వజ్రం', 'profession': 'సౌందర్య, ఫ్యాషన్, సినిమా', 'lucky_days': 'శుక్రవారం, బుధవారం'},
        7: {'colors': 'స్మోకీ గ్రే, తెలుపు, ఆకుపచ్చ', 'direction': 'ఈశాన్యం / వాయువ్యం', 'gemstone': 'వైడూర్యం', 'profession': 'ఆధ్యాత్మికత, పరిశోధన, జ్యోతిష్యం', 'lucky_days': 'సోమవారం, గురువారం'},
        8: {'colors': 'నలుపు, ముదురు నీలం, బూడిద', 'direction': 'పశ్చిమం', 'gemstone': 'నీలమణి', 'profession': 'వైద్యులు, నర్సులు, ఇనుము & ఉక్కు', 'lucky_days': 'శనివారం, బుధవారం'},
        9: {'colors': 'ఎరుపు, గులాబీ, మెరూన్', 'direction': 'దక్షిణం', 'gemstone': 'పగడం', 'profession': 'రక్షణ, పోలీసు, సైన్యం, రియల్ ఎస్టేట్', 'lucky_days': 'మంగళవారం, ఆదివారం'}
    },
    'hi': {
        1: {'colors': 'पीला, नारंगी, सुनहरा', 'direction': 'पूर्व', 'gemstone': 'माणिक्य', 'profession': 'सरकारी नौकरी, राजनीति, नेतृत्व', 'lucky_days': 'रविवार, गुरुवार'},
        2: {'colors': 'सफेद, हरा, चांदी', 'direction': 'वायव्य', 'gemstone': 'मोती / मूनस्टोन', 'profession': 'कला, यात्रा, तरल पदार्थ', 'lucky_days': 'सोमवार, बुधवार'},
        3: {'colors': 'पीला, गुलाबी, बैंगनी', 'direction': 'ईशान', 'gemstone': 'पुखराज', 'profession': 'शिक्षा, अध्यापन, परामर्श', 'lucky_days': 'गुरुवार, मंगलवार'},
        4: {'colors': 'स्लेटी, नीला, मिट्टी का रंग', 'direction': 'नैऋत्य', 'gemstone': 'गोमेद / नीलम', 'profession': 'तकनीक, सॉफ्टवेयर, इंजीनियरिंग', 'lucky_days': 'बुधवार, शनिवार'},
        5: {'colors': 'हरा, हल्के रंग', 'direction': 'उत्तर', 'gemstone': 'पन्ना', 'profession': 'व्यापार, मार्केटिंग, शेयर बाजार', 'lucky_days': 'बुधवार, शुक्रवार'},
        6: {'colors': 'सफेद, हल्का नीला, गुलाबी', 'direction': 'आग्नेय', 'gemstone': 'हीरा', 'profession': 'सौंदर्य, फैशन, सिनेमा', 'lucky_days': 'शुक्रवार, बुधवार'},
        7: {'colors': 'धुएँ जैसा ग्रे, सफेद, हरा', 'direction': 'ईशान / वायव्य', 'gemstone': 'लहसुनिया', 'profession': 'आध्यात्म, शोध, ज्योतिष', 'lucky_days': 'सोमवार, गुरुवार'},
        8: {'colors': 'काला, गहरा नीला, स्लेटी', 'direction': 'पश्चिम', 'gemstone': 'नीलम', 'profession': 'डॉक्टर, नर्स, लोहा व स्टील', 'lucky_days': 'शनिवार, बुधवार'},
        9: {'colors': 'लाल, गुलाबी, मैरून', 'direction': 'दक्षिण', 'gemstone': 'मूंगा', 'profession': 'रक्षा, पुलिस, सेना, रियल एस्टेट', 'lucky_days': 'मंगलवार, रविवार'}
    }
}

MISSING_REMEDIES_LANG = {
    'kn': {
        1: 'ಸೂರ್ಯನ ಬಲ ಹೆಚ್ಚಿಸಲು ಪ್ರತಿದಿನ ಸೂರ್ಯ ನಮಸ್ಕಾರ ಮಾಡಿ ಮತ್ತು ತಾಮ್ರದ ಪಾತ್ರೆಯಲ್ಲಿ ನೀರು ಕುಡಿಯಿರಿ.',
        2: 'ಚಂದ್ರನ ಬಲ ಹೆಚ್ಚಿಸಲು ಬೆಳ್ಳಿಯ ಪಾತ್ರೆಯನ್ನು ಬಳಸಿ ಮತ್ತು ತಾಯಿಯವರ ಆಶೀರ್ವಾದ ಪಡೆಯಿರಿ.',
        3: 'ಗುರುವಿನ ಬಲ ಹೆಚ್ಚಿಸಲು ಹಳದಿ ಬಣ್ಣದ ವಸ್ತುಗಳನ್ನು ಬಳಸಿ ಮತ್ತು ಹಿರಿಯರನ್ನು ಗೌರವಿಸಿ.',
        4: 'ರಾಹುವಿನ ಬಲಕ್ಕಾಗಿ ಪಕ್ಷಿಗಳಿಗೆ ಧಾನ್ಯಗಳನ್ನು ಹಾಕಿ ಮತ್ತು ಪ್ರಕೃತಿಯೊಂದಿಗೆ ಇರಿ.',
        5: 'ಬುಧನ ಬಲಕ್ಕಾಗಿ ಹಸಿರು ಬಣ್ಣದ ಬಟ್ಟೆ ಧರಿಸಿ ಮತ್ತು ಗಣಪತಿ ಆರಾಧನೆ ಮಾಡಿ.',
        6: 'ಶುಕ್ರನ ಬಲಕ್ಕಾಗಿ ಸೌಂದರ್ಯ ಮತ್ತು ಸ್ವಚ್ಛತೆಗೆ ಆದ್ಯತೆ ನೀಡಿ, ಮಹಾಲಕ್ಷ್ಮಿ ಪೂಜೆ ಮಾಡಿ.',
        7: 'ಕೇತುವಿನ ಬಲಕ್ಕಾಗಿ ಗಣೇಶನ ಪ್ರಾರ್ಥನೆ ಮಾಡಿ ಮತ್ತು ಪ್ರಾಣಿಗಳಿಗೆ ಸಹಾಯ ಮಾಡಿ.',
        8: 'ಶನಿಯ ಬಲಕ್ಕಾಗಿ ಬಡವರಿಗೆ ಮತ್ತು ನಿರ್ಗತಿಕರಿಗೆ ಅನ್ನದಾನ ಅಥವಾ ಸೇವೆ ಮಾಡಿ.',
        9: 'ಮಂಗಳನ ಬಲಕ್ಕಾಗಿ ಕೆಂಪು ಬಣ್ಣ ಬಳಸಿ ಮತ್ತು ಯೋಗ, ವ್ಯಾಯಾಮ ರೂಢಿಸಿಕೊಳ್ಳಿ.'
    },
    'en': {
        1: 'Practice Surya Namaskar daily and drink water from a copper vessel to strengthen Sun energy.',
        2: 'Use silver utensils and seek motherly blessings to strengthen Moon energy.',
        3: 'Use yellow items and respect elders and teachers to strengthen Jupiter energy.',
        4: 'Feed grains to birds and spend time in nature for Rahu balance.',
        5: 'Wear green attire and worship Lord Ganesha for Mercury balance.',
        6: 'Maintain harmony, cleanliness, and worship Mahalakshmi for Venus balance.',
        7: 'Pray to Lord Ganesha and help animals for Ketu balance.',
        8: 'Offer food/service to the needy and practice discipline for Saturn balance.',
        9: 'Use red accents and practice yoga/exercise for Mars balance.'
    },
    'ta': {
        1: 'சூரிய பலம் அதிகரிக்க தினமும் சூரிய நமஸ்காரம் செய்து செம்பு பாத்திரத்தில் நீர் அருந்துங்கள்.',
        2: 'சந்திர பலம் அதிகரிக்க வெள்ளிப் பொருட்களைப் பயன்படுத்தி தாயின் ஆசி பெறுங்கள்.',
        3: 'குரு பலம் அதிகரிக்க மஞ்சள் நிறப் பொருட்களைப் பயன்படுத்தி பெரியோரை மதியுங்கள்.',
        4: 'ராகு சமநிலைக்கு பறவைகளுக்கு தானியங்கள் இட்டு இயற்கையோடு இணைந்திருங்கள்.',
        5: 'புதன் பலத்திற்கு பச்சை நிற ஆடை அணிந்து விநாயகரை வழிபடுங்கள்.',
        6: 'சுக்கிர பலத்திற்கு தூய்மை, அழகு மற்றும் மகாலட்சுமி வழிபாட்டைக் கடைப்பிடியுங்கள்.',
        7: 'கேது பலத்திற்கு விநாயக வழிபாடு செய்து விலங்குகளுக்கு உதவுங்கள்.',
        8: 'சனி பலத்திற்கு ஏழைகளுக்கு அன்னதானம் மற்றும் சேவை செய்யுங்கள்.',
        9: 'செவ்வாய் பலத்திற்கு சிவப்பு நிறம் மற்றும் யோகா, உடற்பயிற்சி மேற்கொள்ளுங்கள்.'
    },
    'te': {
        1: 'సూర్య బలం పెరగడానికి రోజూ సూర్య నమస్కారం చేసి రాగి పాత్రలో నీరు త్రాగండి.',
        2: 'చంద్ర బలం పెరగడానికి వెండి పాత్రలు వాడి తల్లి ఆశీర్వాదం తీసుకోండి.',
        3: 'గురు బలం పెరగడానికి పసుపు రంగు వస్తువులు వాడి పెద్దలను గౌరవించండి.',
        4: 'రాహు సమతుల్యత కోసం పక్షులకు గింజలు వేసి ప్రకృతితో గడపండి.',
        5: 'బుధ బలం కోసం ఆకుపచ్చ దుస్తులు ధరించి గణపతిని పూజించండి.',
        6: 'శుక్ర బలం కోసం శుభ్రత, కళాత్మకత మరియు మహాలక్ష్మి పూజ చేయండి.',
        7: 'కేతు బలం కోసం గణేశ ప్రార్థన చేసి మూగజీవాలకు సహాయం చేయండి.',
        8: 'శని బలం కోసం పేదలకు అన్నదానం మరియు సేవ చేయండి.',
        9: 'కుజ బలం కోసం ఎరుపు రంగు మరియు యోగా, వ్యాయామం అలవాటు చేసుకోండి.'
    },
    'hi': {
        1: 'सूर्य बल बढ़ाने के लिए प्रतिदिन सूर्य नमस्कार करें और तांबे के पात्र से जल पिएं।',
        2: 'चंद्र बल बढ़ाने के लिए चांदी का उपयोग करें और माता का आशीर्वाद लें।',
        3: 'गुरु बल बढ़ाने के लिए पीले रंग का उपयोग करें और बड़ों का सम्मान करें।',
        4: 'राहु संतुलन के लिए पक्षियों को दाना डालें और प्रकृति के करीब रहें।',
        5: 'बुध बल के लिए हरे रंग का प्रयोग करें और गणेश जी की आराधना करें।',
        6: 'शुक्र बल के लिए स्वच्छता, सामंजस्य और महालक्ष्मी पूजन करें।',
        7: 'केतु बल के लिए गणेश जी की प्रार्थना करें और जीवों की सहायता करें।',
        8: 'शनि बल के लिए जरूरतमंदों को भोजन/सेवा दें और अनुशासन रखें।',
        9: 'मंगल बल के लिए लाल रंग और योग, व्यायाम को अपनाएं।'
    }
}

PERSONAL_YEAR_LANG = {
    'kn': {
        1: 'ಹೊಸ ಆರಂಭ, ಹೊಸ ಯೋಜನೆಗಳು ಮತ್ತು ನಾಯಕತ್ವ ವಹಿಸಲು ಅತ್ಯುತ್ತಮ ವರ್ಷ.',
        2: 'ಸಹನೆ, ಪಾಲುದಾರಿಕೆ, ಸಂಬಂಧಗಳ ಸುಧಾರಣೆ ಮತ್ತು ಶಾಂತಿಯಿಂದ ಕೆಲಸ ಸಾಧಿಸುವ ವರ್ಷ.',
        3: 'ಸೃಜನಶೀಲತೆ, ಕಲೆ, ಮಾತಿನ ಚಾತುರ್ಯ, ಆರ್ಥಿಕ ಪ್ರಗತಿ ಮತ್ತು ಸಂತೋಷದ ವರ್ಷ.',
        4: 'ಕಠಿಣ ಪರಿಶ್ರಮ, ವ್ಯವಸ್ಥಿತ ಯೋಜನೆ, ವೃತ್ತಿಜೀವನದಲ್ಲಿ ಸ್ಥಿರತೆ.',
        5: 'ಪ್ರಯಾಣ, ಹೊಸ ಬದಲಾವಣೆಗಳು, ವ್ಯಾಪಾರ ವಿಸ್ತರಣೆ ಮತ್ತು ಸ್ವಾತಂತ್ರ್ಯ.',
        6: 'ಕುಟುಂಬದೊಂದಿಗೆ ಕಾಲ ಕಳೆಯುವುದು, ಮನೆ ಅಲಂಕಾರ, ಮದುವೆ ಅಥವಾ ಶುಭ ಕಾರ್ಯಗಳು.',
        7: 'ಆಧ್ಯಾತ್ಮಿಕ ಚಿಂತನೆ, ಸ್ವಯಂ ಅರಿವು, ಸಂಶೋಧನೆ ಮತ್ತು ಏಕಾಂತದಲ್ಲಿ ಜ್ಞಾನ ಸಂಪಾದನೆ.',
        8: 'ಹಣಕಾಸಿನ ಯಶಸ್ಸು, ಅಧಿಕಾರ ಪ್ರಾಪ್ತಿ, ವ್ಯಾಪಾರದಲ್ಲಿ ದೊಡ್ಡ ಲಾಭ.',
        9: 'ಹಳೆಯ ಕೆಲಸಗಳ ಮುಕ್ತಾಯ, ದಾನ-ಧರ್ಮ, ಸಮಾಜ ಸೇವೆ ಮತ್ತು ಮುಂದಿನ ಚಕ್ರಕ್ಕೆ ಸಿದ್ಧತೆ.'
    },
    'en': {
        1: 'Excellent year for fresh starts, new ventures, and taking leadership.',
        2: 'Year of patience, partnerships, harmony in relationships, and steady progress.',
        3: 'Year of creativity, arts, expression, financial growth, and joy.',
        4: 'Year of hard work, structured planning, and career stability.',
        5: 'Year of travel, positive changes, business expansion, and freedom.',
        6: 'Year of family bonding, home improvement, marriage, or auspicious events.',
        7: 'Year of spiritual reflection, inner wisdom, research, and deep study.',
        8: 'Year of financial success, authority, and major business gains.',
        9: 'Year of completions, charity, social service, and preparing for a new cycle.'
    },
    'ta': {
        1: 'புதிய தொடக்கங்கள், புதிய திட்டங்கள் மற்றும் தலைமை ஏற்க சிறந்த ஆண்டு.',
        2: 'பொறுமை, கூட்டாண்மை, உறவுகளில் மேம்பாடு மற்றும் அமைதியான முன்னேற்ற ஆண்டு.',
        3: 'படைப்பாற்றல், கலை, பேச்சாற்றல், பொருளாதார வளர்ச்சி மற்றும் மகிழ்ச்சியான ஆண்டு.',
        4: 'கடின உழைப்பு, திட்டமிடல் மற்றும் பணியில் நிலைத்தன்மை தரும் ஆண்டு.',
        5: 'பயணங்கள், புதிய மாற்றங்கள், தொழில் விரிவாக்கம் மற்றும் சுதந்திர ஆண்டு.',
        6: 'குடும்ப ஒற்றுமை, வீடு மேம்பாடு, திருமணம் அல்லது சுப நிகழ்வுகளின் ஆண்டு.',
        7: 'ஆன்மீக சிந்தனை, சுய அறிவு, ஆராய்ச்சி மற்றும் ஆழமான கற்றல் ஆண்டு.',
        8: 'பொருளாதார வெற்றி, அதிகாரம் மற்றும் தொழிலில் பெரிய லாபம் தரும் ஆண்டு.',
        9: 'முந்தைய பணிகள் நிறைவு, தான தர்மம், சமூக சேவை மற்றும் புதிய சுழற்சிக்கான தயார்நிலை.'
    },
    'te': {
        1: 'కొత్త ప్రారంభాలు, కొత్త ప్రణాళికలు మరియు నాయకత్వానికి అనుకూల సంవత్సరం.',
        2: 'ఓర్పు, భాగస్వామ్యం, సంబంధాల మెరుగుదల మరియు ప్రశాంత పురోగతి సంవత్సరం.',
        3: 'సృజనాత్మకత, కళలు, వాక్చాతుర్యం, ఆర్థిక పురోగతి మరియు ఆనంద సంవత్సరం.',
        4: 'కఠిన శ్రమ, క్రమబద్ధమైన ప్రణాళిక మరియు వృత్తిలో స్థిరత్వం ఇచ్చే సంవత్సరం.',
        5: 'ప్రయాణాలు, కొత్త మార్పులు, వ్యాపార విస్తరణ మరియు స్వేచ్ఛ సంవత్సరం.',
        6: 'కుటుంబంతో సమయం, గృహ అలంకరణ, వివాహం లేదా శుభకార్యాల సంవత్సరం.',
        7: 'ఆధ్యాత్మిక చింతన, ఆత్మపరిశీలన, పరిశోధన మరియు జ్ఞానార్జన సంవత్సరం.',
        8: 'ఆర్థిక విజయం, అధికారం మరియు వ్యాపారంలో మంచి లాభాల సంవత్సరం.',
        9: 'పాత పనుల పూర్తి, దానధర్మాలు, సమాజ సేవ మరియు కొత్త చక్రానికి సిద్ధత.'
    },
    'hi': {
        1: 'नई शुरुआत, नई योजनाओं और नेतृत्व के लिए उत्तम वर्ष।',
        2: 'धैर्य, साझेदारी, रिश्तों में सुधार और शांत प्रगति का वर्ष।',
        3: 'रचनात्मकता, कला, वाणी कौशल, आर्थिक प्रगति और आनंद का वर्ष।',
        4: 'परिश्रम, व्यवस्थित योजना और करियर में स्थिरता का वर्ष।',
        5: 'यात्रा, सकारात्मक बदलाव, व्यापार विस्तार और स्वतंत्रता का वर्ष।',
        6: 'परिवार के साथ समय, घर की सजावट, विवाह या शुभ कार्यों का वर्ष।',
        7: 'आध्यात्मिक चिंतन, आत्मज्ञान, शोध और अध्ययन का वर्ष।',
        8: 'आर्थिक सफलता, अधिकार और व्यापार में अच्छे लाभ का वर्ष।',
        9: 'कार्यों को पूर्ण करने, दान-पुण्य, समाज सेवा और नए चक्र की तैयारी का वर्ष।'
    }
}

VEDIC_YOGAS_8_LANG = {
    'kn': [
        {'nums': {3, 6, 9}, 'name': '✨ 1. 3-6-9 ವೈಭವ ಮತ್ತು ಸಂಪತ್ತು ಯೋಗ (Wealth & Glory Yoga)', 'desc': 'ಗುರು (3), ಶುಕ್ರ (6) ಮತ್ತು ಮಂಗಳ (9) ಒಟ್ಟಿಗೆ ಇರುವುದರಿಂದ ಜೀವನದಲ್ಲಿ ಐಷಾರಾಮಿ ಜೀವನ ಹಾಗೂ ಅಭಿವೃದ್ಧಿ ಪ್ರಾಪ್ತಿಯಾಗುತ್ತದೆ.'},
        {'nums': {1, 5, 9}, 'name': '👑 2. 1-5-9 ರಾಜಯೋಗ ಮತ್ತು ನಾಯಕತ್ವ (Leadership & Rajayoga)', 'desc': 'ಸೂರ್ಯ (1), ಬುಧ (5) ಮತ್ತು ಮಂಗಳ (9) ಸಂಯೋಗದಿಂದ ಸಮಾಜದಲ್ಲಿ ಉನ್ನತ ಸ್ಥಾನ, ಅಧಿಕಾರ ಹಾಗೂ ಕೀರ್ತಿ ಲಭಿಸುತ್ತದೆ.'},
        {'nums': {3, 1, 9}, 'name': '🧠 3. 3-1-9 ಜ್ಞಾನ ಮತ್ತು ಬೌದ್ಧಿಕ ಯೋಗ (Mental & Knowledge Yoga)', 'desc': 'ತೀವ್ರವಾದ ಸ್ಮರಣಶಕ್ತಿ, ಉತ್ತಮ ನಿರ್ಧಾರ ಕೈಗೊಳ್ಳುವ ಸಾಮರ್ಥ್ಯ ಹಾಗೂ ಬಲವಾದ ಇಚ್ಛಾಶಕ್ತಿಯನ್ನು ಸೂಚಿಸುತ್ತದೆ.'},
        {'nums': {2, 5, 8}, 'name': '🏡 4. 2-5-8 ಸ್ಥಿರತೆ ಮತ್ತು ಆಸ್ತಿ ಯೋಗ (Stability & Property Yoga)', 'desc': 'ಚಂದ್ರ (2), ಬುಧ (5) ಮತ್ತು ಶನಿ (8) ಸಂಯೋಜನೆಯು ರಿಯಲ್ ಎಸ್ಟೇಟ್ ಹಾಗೂ ಆಸ್ತಿ ಖರೀದಿ ಯೋಗವನ್ನು ನೀಡುತ್ತದೆ.'},
        {'nums': {4, 9, 2}, 'name': '💞 5. 4-9-2 ಕೌಟುಂಬಿಕ ಮತ್ತು ಭಾವನಾತ್ಮಕ ಸಮತೋಲನ ಯೋಗ (Family & Emotional Yoga)', 'desc': 'ರಾಹು (4), ಮಂಗಳ (9) ಮತ್ತು ಚಂದ್ರ (2) ಸಂಯೋಗವು ಕುಟುಂಬ ಜವಾಬ್ದಾರಿ, ಭಾವನಾತ್ಮಕ ಬಲ ಹಾಗೂ ಸಮತೋಲನವನ್ನು ನೀಡುತ್ತದೆ.'},
        {'nums': {8, 1, 6}, 'name': '💼 6. 8-1-6 ವ್ಯವಹಾರ ಮತ್ತು ಸಾಧನಾ ಯೋಗ (Business & Achievement Yoga)', 'desc': 'ಶನಿ (8), ಸೂರ್ಯ (1) ಮತ್ತು ಶುಕ್ರ (6) ಸಂಯೋಗವು ಶಿಸ್ತು, ಕಠಿಣ ಶ್ರಮದಿಂದ ವೃತ್ತಿ ಹಾಗೂ ಆರ್ಥಿಕ ಸಾಧನೆಯನ್ನು ತರುತ್ತದೆ.'},
        {'nums': {2, 7, 6}, 'name': '🎨 7. 2-7-6 ಕಲೆ, ಆಕರ್ಷಣೆ ಮತ್ತು ಸೃಜನಶೀಲ ಯೋಗ (Creative & Charm Yoga)', 'desc': 'ಚಂದ್ರ (2), ಕೇತು (7) ಮತ್ತು ಶುಕ್ರ (6) ಸಂಯೋಗವು ಸೃಜನಶೀಲತೆ, ಕಲಾತ್ಮಕತೆ, ಅಂತರ್ಬೋಧೆ ಮತ್ತು ಆಕರ್ಷಣೆಯನ್ನು ಹೆಚ್ಚಿಸುತ್ತದೆ.'},
        {'nums': {4, 5, 6}, 'name': '⚖️ 8. 4-5-6 ಸಮೃದ್ಧಿ ಮತ್ತು ಸಮತೋಲನ ಯೋಗ (Prosperity & Balance Yoga)', 'desc': 'ರಾಹು (4), ಬುಧ (5) ಮತ್ತು ಶುಕ್ರ (6) ಸಂಯೋಗವು ವ್ಯವಹಾರ ಬುದ್ಧಿ, ಆರ್ಥಿಕ ಸ್ಥಿರತೆ ಹಾಗೂ ಸಮೃದ್ಧಿಯನ್ನು ನೀಡುತ್ತದೆ.'}
    ],
    'en': [
        {'nums': {3, 6, 9}, 'name': '✨ 1. 3-6-9 Wealth & Glory Yoga', 'desc': 'Combination of Jupiter (3), Venus (6), and Mars (9) supports prosperity, comfort, and overall growth.'},
        {'nums': {1, 5, 9}, 'name': '👑 2. 1-5-9 Leadership & Rajayoga', 'desc': 'Combination of Sun (1), Mercury (5), and Mars (9) brings authority, recognition, and leadership.'},
        {'nums': {3, 1, 9}, 'name': '🧠 3. 3-1-9 Mental & Knowledge Yoga', 'desc': 'Indicates sharp memory, strong willpower, analytical thinking, and sound decision-making.'},
        {'nums': {2, 5, 8}, 'name': '🏡 4. 2-5-8 Stability & Property Yoga', 'desc': 'Combination of Moon (2), Mercury (5), and Saturn (8) supports stability, property, and real estate.'},
        {'nums': {4, 9, 2}, 'name': '💞 5. 4-9-2 Family & Emotional Harmony Yoga', 'desc': 'Combination of Rahu (4), Mars (9), and Moon (2) supports emotional resilience and family dedication.'},
        {'nums': {8, 1, 6}, 'name': '💼 6. 8-1-6 Business & Achievement Yoga', 'desc': 'Combination of Saturn (8), Sun (1), and Venus (6) brings disciplined effort and tangible success.'},
        {'nums': {2, 7, 6}, 'name': '🎨 7. 2-7-6 Creativity & Charm Yoga', 'desc': 'Combination of Moon (2), Ketu (7), and Venus (6) enhances intuition, artistry, and personal appeal.'},
        {'nums': {4, 5, 6}, 'name': '⚖️ 8. 4-5-6 Prosperity & Balance Yoga', 'desc': 'Combination of Rahu (4), Mercury (5), and Venus (6) supports smart enterprise and balanced wealth.'}
    ],
    'ta': [
        {'nums': {3, 6, 9}, 'name': '✨ 1. 3-6-9 செல்வம் மற்றும் புகழ் யோகம்', 'desc': 'குரு (3), சுக்கிரன் (6), செவ்வாய் (9) சேர்க்கை வளம், மகிழ்ச்சி மற்றும் முன்னேற்றத்தைத் தரும்.'},
        {'nums': {1, 5, 9}, 'name': '👑 2. 1-5-9 ராஜயோகம் மற்றும் தலைமை யோகம்', 'desc': 'சூரியன் (1), புதன் (5), செவ்வாய் (9) சேர்க்கை அதிகாரம், கௌரவம் மற்றும் தலைமைப் பண்பை அளிக்கும்.'},
        {'nums': {3, 1, 9}, 'name': '🧠 3. 3-1-9 ஞானம் மற்றும் அறிவு யோகம்', 'desc': 'நல்ல நினைவாற்றல், மன உறுதியும் தெளிவான முடிவெடுக்கும் திறனையும் குறிக்கும்.'},
        {'nums': {2, 5, 8}, 'name': '🏡 4. 2-5-8 நிலைத்தன்மை மற்றும் சொத்து யோகம்', 'desc': 'சந்திரன் (2), புதன் (5), சனி (8) சேர்க்கை நிலையான வளர்ச்சி மற்றும் சொத்து சேர்க்கையைத் தரும்.'},
        {'nums': {4, 9, 2}, 'name': '💞 5. 4-9-2 குடும்ப மற்றும் உணர்வு சமநிலை யோகம்', 'desc': 'ராகு (4), செவ்வாய் (9), சந்திரன் (2) சேர்க்கை குடும்ப அர்ப்பணிப்பும் உணர்வு வலிமையும் தரும்.'},
        {'nums': {8, 1, 6}, 'name': '💼 6. 8-1-6 தொழில் மற்றும் சாதனை யோகம்', 'desc': 'சனி (8), சூரியன் (1), சுக்கிரன் (6) சேர்க்கை உழைப்பு மற்றும் உறுதியான வெற்றியைத் தரும்.'},
        {'nums': {2, 7, 6}, 'name': '🎨 7. 2-7-6 கலை மற்றும் கவர்ச்சி யோகம்', 'desc': 'சந்திரன் (2), கேது (7), சுக்கிரன் (6) சேர்க்கை படைப்பாற்றல், கலை உணர்வு மற்றும் கவர்ச்சியை அதிகரிக்கும்.'},
        {'nums': {4, 5, 6}, 'name': '⚖️ 8. 4-5-6 செழிப்பு மற்றும் சமநிலை யோகம்', 'desc': 'ராகு (4), புதன் (5), சுக்கிரன் (6) சேர்க்கை வணிகத் திறனும் பொருளாதார சமநிலையும் தரும்.'}
    ],
    'te': [
        {'nums': {3, 6, 9}, 'name': '✨ 1. 3-6-9 వైభవం మరియు సంపద యోగం', 'desc': 'గురువు (3), శుక్రుడు (6), కుజుడు (9) కలయిక శ్రేయస్సు, సౌకర్యం మరియు అభివృద్ధిని ఇస్తుంది.'},
        {'nums': {1, 5, 9}, 'name': '👑 2. 1-5-9 రాజయోగం మరియు నాయకత్వ యోగం', 'desc': 'సూర్యుడు (1), బుధుడు (5), కుజుడు (9) కలయిక గౌరవం, అధికారం మరియు నాయకత్వాన్ని ఇస్తుంది.'},
        {'nums': {3, 1, 9}, 'name': '🧠 3. 3-1-9 జ్ఞాన మరియు మేధో యోగం', 'desc': 'మంచి జ్ఞాపకశక్తి, సంకల్పబలం మరియు స్పష్టమైన నిర్ణయ సామర్థ్యాన్ని సూచిస్తుంది.'},
        {'nums': {2, 5, 8}, 'name': '🏡 4. 2-5-8 స్థిరత్వం మరియు ఆస్తి యోగం', 'desc': 'చంద్రుడు (2), బుధుడు (5), శని (8) కలయిక స్థిరత్వం మరియు ఆస్తి అభివృద్ధిని ఇస్తుంది.'},
        {'nums': {4, 9, 2}, 'name': '💞 5. 4-9-2 కుటుంబ మరియు భావోద్వేగ సమతుల్య యోగం', 'desc': 'రాహువు (4), కుజుడు (9), చంద్రుడు (2) కలయిక కుటుంబ బాధ్యత మరియు భావోద్వేగ బలాన్ని ఇస్తుంది.'},
        {'nums': {8, 1, 6}, 'name': '💼 6. 8-1-6 వ్యాపార మరియు సాధన యోగం', 'desc': 'శని (8), సూర్యుడు (1), శుక్రుడు (6) కలయిక క్రమశిక్షణతో కూడిన విజయాన్ని అందిస్తుంది.'},
        {'nums': {2, 7, 6}, 'name': '🎨 7. 2-7-6 కళాత్మకత మరియు ఆకర్షణ యోగం', 'desc': 'చంద్రుడు (2), కేతువు (7), శుక్రుడు (6) కలయిక సృజనాత్మకత, అంతర్దృష్టి మరియు ఆకర్షణను పెంచుతుంది.'},
        {'nums': {4, 5, 6}, 'name': '⚖️ 8. 4-5-6 సమృద్ధి మరియు సమతుల్య యోగం', 'desc': 'రాహువు (4), బుధుడు (5), శుక్రుడు (6) కలయిక వ్యాపార నైపుణ్యం మరియు ఆర్థిక సమతుల్యతను ఇస్తుంది.'}
    ],
    'hi': [
        {'nums': {3, 6, 9}, 'name': '✨ 1. 3-6-9 वैभव और समृद्धि योग', 'desc': 'गुरु (3), शुक्र (6) और मंगल (9) का संयोग सुख-सुविधा, समृद्धि और उन्नति प्रदान करता है।'},
        {'nums': {1, 5, 9}, 'name': '👑 2. 1-5-9 राजयोग और नेतृत्व योग', 'desc': 'सूर्य (1), बुध (5) और मंगल (9) का संयोग मान-सम्मान, अधिकार और नेतृत्व क्षमता देता है।'},
        {'nums': {3, 1, 9}, 'name': '🧠 3. 3-1-9 ज्ञान और बौद्धिक योग', 'desc': 'तीव्र स्मरण शक्ति, दृढ़ संकल्प और स्पष्ट निर्णय लेने की क्षमता को दर्शाता है।'},
        {'nums': {2, 5, 8}, 'name': '🏡 4. 2-5-8 स्थिरता और संपत्ति योग', 'desc': 'चंद्र (2), बुध (5) और शनि (8) का संयोग स्थिरता, भूमि-भवन और संपत्ति लाभ देता है।'},
        {'nums': {4, 9, 2}, 'name': '💞 5. 4-9-2 पारिवारिक और भावनात्मक संतुलन योग', 'desc': 'राहु (4), मंगल (9) और चंद्र (2) का संयोग पारिवारिक समर्पण और भावनात्मक संतुलन देता है।'},
        {'nums': {8, 1, 6}, 'name': '💼 6. 8-1-6 व्यापार और उपलब्धि योग', 'desc': 'शनि (8), सूर्य (1) और शुक्र (6) का संयोग अनुशासन और परिश्रम से सफलता दिलाता है।'},
        {'nums': {2, 7, 6}, 'name': '🎨 7. 2-7-6 रचनात्मकता और आकर्षण योग', 'desc': 'चंद्र (2), केतु (7) और शुक्र (6) का संयोग कलात्मकता, अंतर्ज्ञान और आकर्षण बढ़ाता है।'},
        {'nums': {4, 5, 6}, 'name': '⚖️ 8. 4-5-6 समृद्धि और संतुलन योग', 'desc': 'राहु (4), बुध (5) और शुक्र (6) का संयोग व्यावहारिक समझ और संतुलित समृद्धि देता है।'}
    ]
}

LOSHU_YOGAS_8_LANG = {
    'kn': [
        {'nums': {4, 9, 2}, 'name': '💞 1. 4-9-2 ಭಾವನಾತ್ಮಕ ಮತ್ತು ಕೌಟುಂಬಿಕ ಯೋಗ (Emotional & Family Plane)', 'desc': 'ಲೋ ಶು ಗ್ರಿಡ್‌ನ ಮೇಲಿನ ಸಾಲಿನ 4-9-2 ಸಂಯೋಗವು ಭಾವನಾತ್ಮಕ ಬಲ, ಸಂಬಂಧಗಳು ಮತ್ತು ಕೌಟುಂಬಿಕ ಬದ್ಧತೆಯನ್ನು ಸೂಚಿಸುತ್ತದೆ.'},
        {'nums': {3, 5, 7}, 'name': '🧘 2. 3-5-7 ಆತ್ಮಶಕ್ತಿ ಮತ್ತು ಸಮತೋಲನ ಯೋಗ (Willpower & Balance Plane)', 'desc': 'ಮಧ್ಯದ ಸಾಲಿನ 3-5-7 ಸಂಯೋಗವು ಇಚ್ಛಾಶಕ್ತಿ, ಆಂತರಿಕ ಸಮತೋಲನ ಮತ್ತು ಆಧ್ಯಾತ್ಮಿಕ ಒಳನೋಟವನ್ನು ತೋರಿಸುತ್ತದೆ.'},
        {'nums': {8, 1, 6}, 'name': '🛠️ 3. 8-1-6 ಪ್ರಾಯೋಗಿಕ ಮತ್ತು ವ್ಯವಹಾರ ಯೋಗ (Practical & Business Plane)', 'desc': 'ಕೆಳಗಿನ ಸಾಲಿನ 8-1-6 ಸಂಯೋಗವು ಶಿಸ್ತು, ಕಠಿಣ ಪರಿಶ್ರಮ ಹಾಗೂ ವೃತ್ತಿ/ವ್ಯವಹಾರ ಯಶಸ್ಸನ್ನು ನೀಡುತ್ತದೆ.'},
        {'nums': {4, 3, 8}, 'name': '📐 4. 4-3-8 ಚಿಂತನೆ ಮತ್ತು ಯೋಜನಾ ಯೋಗ (Thought Plane)', 'desc': 'ಎಡ ಲಂಬ ಸಾಲಿನ 4-3-8 ಸಂಯೋಗವು ವ್ಯವಸ್ಥಿತ ಚಿಂತನೆ, ಯೋಜನೆ ಹಾಗೂ ವಿಶ್ಲೇಷಣಾ ಸಾಮರ್ಥ್ಯವನ್ನು ಸೂಚಿಸುತ್ತದೆ.'},
        {'nums': {9, 5, 1}, 'name': '⚡ 5. 9-5-1 ಇಚ್ಛಾಶಕ್ತಿ ಮತ್ತು ಕಾರ್ಯಯೋಗ (Will & Action Plane)', 'desc': 'ಮಧ್ಯ ಲಂಬ ಸಾಲಿನ 9-5-1 ಸಂಯೋಗವು ದೃಢನಿರ್ಧಾರ, ಶಕ್ತಿ ಮತ್ತು ಗುರಿ ಸಾಧಿಸುವ ವೇಗವನ್ನು ನೀಡುತ್ತದೆ.'},
        {'nums': {2, 7, 6}, 'name': '🎭 6. 2-7-6 ಸೃಜನಶೀಲತೆ ಮತ್ತು ಆಕರ್ಷಣ ಯೋಗ (Creative & Action Plane)', 'desc': 'ಬಲ ಲಂಬ ಸಾಲಿನ 2-7-6 ಸಂಯೋಗವು ಕಲೆ, ಸೃಜನಶೀಲತೆ, ಸಂವಹನ ಮತ್ತು ಆಕರ್ಷಣೆಯನ್ನು ಹೆಚ್ಚಿಸುತ್ತದೆ.'},
        {'nums': {4, 5, 6}, 'name': '✨ 7. 4-5-6 ಸಮೃದ್ಧಿ ಮತ್ತು ಯಶಸ್ಸಿನ ಕರ್ಣ ಯೋಗ (Golden Success Diagonal)', 'desc': '4-5-6 ಕರ್ಣ ರೇಖೆಯು ಸಮತೋಲನ, ಆರ್ಥಿಕ ಸ್ಥಿರತೆ ಮತ್ತು ಸರ್ವಾಂಗೀಣ ಯಶಸ್ಸನ್ನು ಸೂಚಿಸುತ್ತದೆ.'},
        {'nums': {2, 5, 8}, 'name': '🏛️ 8. 2-5-8 ಸ್ಥಿರತೆ ಮತ್ತು ಆಸ್ತಿ ಕರ್ಣ ಯೋಗ (Silver Stability Diagonal)', 'desc': '2-5-8 ಕರ್ಣ ರೇಖೆಯು ಸ್ಥಿರತೆ, ಆಸ್ತಿ/ಭೂಮಿ ಯೋಗ ಮತ್ತು ದೀರ್ಘಕಾಲೀನ ಭದ್ರತೆಯನ್ನು ನೀಡುತ್ತದೆ.'}
    ],
    'en': [
        {'nums': {4, 9, 2}, 'name': '💞 1. 4-9-2 Emotional & Family Plane (Top Row)', 'desc': 'Top row 4-9-2 in Lo Shu Grid reflects emotional warmth, relationships, and family harmony.'},
        {'nums': {3, 5, 7}, 'name': '🧘 2. 3-5-7 Willpower & Balance Plane (Middle Row)', 'desc': 'Middle row 3-5-7 in Lo Shu Grid highlights inner balance, willpower, and deeper insight.'},
        {'nums': {8, 1, 6}, 'name': '🛠️ 3. 8-1-6 Practical & Business Plane (Bottom Row)', 'desc': 'Bottom row 8-1-6 in Lo Shu Grid supports discipline, steady effort, and practical results.'},
        {'nums': {4, 3, 8}, 'name': '📐 4. 4-3-8 Mental / Thought Plane (Left Column)', 'desc': 'Left column 4-3-8 indicates structured planning, memory, and analytical thinking.'},
        {'nums': {9, 5, 1}, 'name': '⚡ 5. 9-5-1 Determination & Drive Plane (Center Column)', 'desc': 'Center column 9-5-1 reflects strong drive, clarity, and decisive action.'},
        {'nums': {2, 7, 6}, 'name': '🎭 6. 2-7-6 Creativity & Charm Plane (Right Column)', 'desc': 'Right column 2-7-6 enhances creativity, artistic expression, and social appeal.'},
        {'nums': {4, 5, 6}, 'name': '✨ 7. 4-5-6 Golden Success Diagonal', 'desc': 'Diagonal 4-5-6 signifies balance, opportunity, and overall progress.'},
        {'nums': {2, 5, 8}, 'name': '🏛️ 8. 2-5-8 Stability & Property Diagonal', 'desc': 'Diagonal 2-5-8 represents grounding, stability, and long-term security.'}
    ],
    'ta': [
        {'nums': {4, 9, 2}, 'name': '💞 1. 4-9-2 உணர்வு மற்றும் குடும்ப நிலை (மேல் வரிசை)', 'desc': 'லோ ஷு கட்டத்தின் 4-9-2 சேர்க்கை உணர்வு வலிமை, உறவுகள் மற்றும் குடும்ப நல்லிணக்கத்தைக் குறிக்கும்.'},
        {'nums': {3, 5, 7}, 'name': '🧘 2. 3-5-7 மன உறுதி மற்றும் சமநிலை நிலை (நடு வரிசை)', 'desc': 'லோ ஷு கட்டத்தின் 3-5-7 சேர்க்கை மன சமநிலை, உறுதியான விருப்பம் மற்றும் ஆழமான சிந்தனையைத் தரும்.'},
        {'nums': {8, 1, 6}, 'name': '🛠️ 3. 8-1-6 செயல்பாடு மற்றும் தொழில் நிலை (கீழ் வரிசை)', 'desc': 'லோ ஷு கட்டத்தின் 8-1-6 சேர்க்கை ஒழுக்கம், உழைப்பு மற்றும் நடைமுறை வெற்றியைத் தரும்.'},
        {'nums': {4, 3, 8}, 'name': '📐 4. 4-3-8 சிந்தனை மற்றும் திட்டமிடல் நிலை', 'desc': '4-3-8 வரிசை திட்டமிடல், நினைவாற்றல் மற்றும் பகுப்பாய்வுத் திறனைக் குறிக்கும்.'},
        {'nums': {9, 5, 1}, 'name': '⚡ 5. 9-5-1 தன்னம்பிக்கை மற்றும் செயல் நிலை', 'desc': '9-5-1 வரிசை துணிச்சல், தெளிவு மற்றும் இலக்கை அடையும் வேகத்தைத் தரும்.'},
        {'nums': {2, 7, 6}, 'name': '🎭 6. 2-7-6 படைப்பாற்றல் மற்றும் கவர்ச்சி நிலை', 'desc': '2-7-6 வரிசை கலை உணர்வு, படைப்பாற்றல் மற்றும் கவர்ச்சியை அதிகரிக்கும்.'},
        {'nums': {4, 5, 6}, 'name': '✨ 7. 4-5-6 வெற்றி மூலைவிட்ட யோகம்', 'desc': '4-5-6 மூலைவிட்டம் சமநிலை, வளம் மற்றும் வெற்றியைக் குறிக்கும்.'},
        {'nums': {2, 5, 8}, 'name': '🏛️ 8. 2-5-8 நிலைத்தன்மை மற்றும் சொத்து மூலைவிட்ட யோகம்', 'desc': '2-5-8 மூலைவிட்டம் நிலைத்தன்மை, சொத்து மற்றும் நீடித்த பாதுகாப்பைத் தரும்.'}
    ],
    'te': [
        {'nums': {4, 9, 2}, 'name': '💞 1. 4-9-2 భావోద్వేగ మరియు కుటుంబ యోగం (పై వరుస)', 'desc': 'లో షూ గ్రిడ్‌లోని 4-9-2 కలయిక భావోద్వేగ బలం, సంబంధాలు మరియు కుటుంబ సమతుల్యతను సూచిస్తుంది.'},
        {'nums': {3, 5, 7}, 'name': '🧘 2. 3-5-7 సంకల్పబలం మరియు సమతుల్య యోగం (మధ్య వరుస)', 'desc': 'లో షూ గ్రిడ్‌లోని 3-5-7 కలయిక అంతర్గత సమతుల్యత, సంకల్పబలం మరియు ఆధ్యాత్మిక దృష్టిని ఇస్తుంది.'},
        {'nums': {8, 1, 6}, 'name': '🛠️ 3. 8-1-6 ఆచరణ మరియు వ్యాపార యోగం (క్రింది వరుస)', 'desc': 'లో షూ గ్రిడ్‌లోని 8-1-6 కలయిక క్రమశిక్షణ, కృషి మరియు వృత్తిపరమైన విజయాన్ని ఇస్తుంది.'},
        {'nums': {4, 3, 8}, 'name': '📐 4. 4-3-8 ఆలోచన మరియు ప్రణాళిక యోగం', 'desc': '4-3-8 కలయిక ప్రణాళికాబద్ధమైన ఆలోచన మరియు విశ్లేషణ సామర్థ్యాన్ని సూచిస్తుంది.'},
        {'nums': {9, 5, 1}, 'name': '⚡ 5. 9-5-1 పట్టుదల మరియు కార్యాచరణ యోగం', 'desc': '9-5-1 కలయిక దృఢ సంకల్పం, స్పష్టత మరియు లక్ష్య సాధనను ఇస్తుంది.'},
        {'nums': {2, 7, 6}, 'name': '🎭 6. 2-7-6 సృజనాత్మకత మరియు ఆకర్షణ యోగం', 'desc': '2-7-6 కలయిక కళాత్మకత, సృజనాత్మకత మరియు ఆకర్షణను పెంచుతుంది.'},
        {'nums': {4, 5, 6}, 'name': '✨ 7. 4-5-6 విజయ కర్ణ యోగం', 'desc': '4-5-6 కర్ణ రేఖ సమతుల్యత, శ్రేయస్సు మరియు పురోగతిని సూచిస్తుంది.'},
        {'nums': {2, 5, 8}, 'name': '🏛️ 8. 2-5-8 స్థిరత్వం మరియు ఆస్తి కర్ణ యోగం', 'desc': '2-5-8 కర్ణ రేఖ స్థిరత్వం, ఆస్తి యోగం మరియు దీర్ఘకాల భద్రతను ఇస్తుంది.'}
    ],
    'hi': [
        {'nums': {4, 9, 2}, 'name': '💞 1. 4-9-2 भावनात्मक और पारिवारिक योग (ऊपरी पंक्ति)', 'desc': 'लो शू ग्रिड की 4-9-2 पंक्ति भावनात्मक संतुलन, रिश्तों और पारिवारिक सामंजस्य को दर्शाती है।'},
        {'nums': {3, 5, 7}, 'name': '🧘 2. 3-5-7 संकल्पशक्ति और संतुलन योग (मध्य पंक्ति)', 'desc': 'लो शू ग्रिड की 3-5-7 पंक्ति आंतरिक संतुलन, इच्छाशक्ति और गहरी समझ प्रदान करती है।'},
        {'nums': {8, 1, 6}, 'name': '🛠️ 3. 8-1-6 व्यावहारिक और व्यापार योग (निचली पंक्ति)', 'desc': 'लो शू ग्रिड की 8-1-6 पंक्ति अनुशासन, परिश्रम और व्यावहारिक सफलता देती है।'},
        {'nums': {4, 3, 8}, 'name': '📐 4. 4-3-8 विचार और योजना योग', 'desc': '4-3-8 संयोजन व्यवस्थित सोच, योजना और विश्लेषण क्षमता को दर्शाता है।'},
        {'nums': {9, 5, 1}, 'name': '⚡ 5. 9-5-1 दृढ़ संकल्प और कार्य योग', 'desc': '9-5-1 संयोजन आत्मविश्वास, स्पष्टता और लक्ष्य प्राप्ति की गति देता है।'},
        {'nums': {2, 7, 6}, 'name': '🎭 6. 2-7-6 रचनात्मकता और आकर्षण योग', 'desc': '2-7-6 संयोजन कलात्मकता, रचनात्मकता और आकर्षण बढ़ाता है।'},
        {'nums': {4, 5, 6}, 'name': '✨ 7. 4-5-6 सफलता विकर्ण योग', 'desc': '4-5-6 विकर्ण रेखा संतुलन, समृद्धि और उन्नति को दर्शाती है।'},
        {'nums': {2, 5, 8}, 'name': '🏛️ 8. 2-5-8 स्थिरता और संपत्ति विकर्ण योग', 'desc': '2-5-8 विकर्ण रेखा स्थिरता, संपत्ति लाभ और दीर्घकालिक सुरक्षा देती है।'}
    ]
}

UI_TEXT = {
    'kn': {
        'lang_label': 'ಭಾಷೆ (Language)', 'welcome': 'ಸ್ವಾಗತ (Welcome)',
        'portal_title': 'ಸಂಪೂರ್ಣ ಸಂಖ್ಯಾಶಾಸ್ತ್ರ, ಗ್ರಿಡ್‌ಗಳು, ವಿವಾಹ ಹೊಂದಾಣಿಕೆ, ತಾರಾಬಲ ಮತ್ತು ಅಷ್ಟಕವರ್ಗ ಪೋರ್ಟಲ್',
        'p1_heading': 'ವ್ಯಕ್ತಿ 1 (Person 1) ವಿವರಗಳು:',
        'dob_ph': 'ಜನ್ಮ ದಿನಾಂಕ (DD-MM-YYYY)', 'name_ph': 'ಪೂರ್ಣ ಹೆಸರು (Full Name)',
        'mobile_ph': 'ಮೊಬೈಲ್ ಸಂಖ್ಯೆ (ಉದಾ: 9513129695)', 'time_ph': 'ಜನ್ಮ ಸಮಯ (ಉದಾ: 7.36 AM)',
        'place_ph': 'ಜನ್ಮ ಸ್ಥಳ (ಉದಾ: Halebidu, Hassan)',
        'lagna_lbl': 'ಲಗ್ನ (Lagna):', 'rashi_lbl': 'ರಾಶಿ (Rashi):', 'nak_lbl': 'ನಕ್ಷತ್ರ (Nakshatra):',
        'transit_nak_lbl': 'ದಿನದ / ಗೋಚರ ನಕ್ಷತ್ರ (Tarabala & Madabhuda):',
        'p2_heading': 'ಪಾಲುದಾರರ / ಸಂಗಾತಿಯ (Partner / Spouse) ವಿವರಗಳು:',
        'p2_name_ph': 'ಪಾಲುದಾರರ ಹೆಸರು (Partner Name)', 'p2_dob_ph': 'ಪಾಲುದಾರರ ಜನ್ಮ ದಿನಾಂಕ (DD-MM-YYYY)',
        'ashtaka_heading': 'ಅಷ್ಟಕವರ್ಗ ಗ್ರಹಗಳ ರಾಶಿ ಸ್ಥಾನ (Ashtakavargha Planet Positions):',
        'calc_btn': 'ಸಂಪೂರ್ಣ ವಿಶ್ಲೇಷಣೆ (Calculate Yogas, Matching & Reports)',
        'strength_title': '🌟 ಜನ್ಮ ಬಲ ಮತ್ತು ಹೆಸರಿನ ಫ್ರೀಕ್ವೆನ್ಸಿ ಬಲ (Birth & Name Strength Analysis)',
        'birth_deg_lbl': '📅 ಜನ್ಮ ಬಲದ ಸರಾಸರಿ ಡಿಗ್ರಿ (Birth Strength):', 'lifestyle_lbl': '🎯 ಜೀವನ ಶೈಲಿ (Lifestyle):',
        'name_freq_lbl': '🔤 ಹೆಸರಿನ ಸೌಂಡ್ ಫ್ರೀಕ್ವೆನ್ಸಿ (Name Sound Frequency):',
        'grid_title': '1. ಜನ್ಮ ದಿನಾಂಕ, ವೇದಿಕ್ ಗ್ರಿಡ್ (3-1-9) ಮತ್ತು ಲೋ ಶು ಗ್ರಿಡ್ (4-9-2)',
        'vedic_grid_lbl': 'ವೇದಿಕ್ ಗ್ರಿಡ್ (Vedic Grid: 3-1-9 / 6-7-5 / 2-8-4)',
        'loshu_grid_lbl': 'ಲೋ ಶು ಗ್ರಿಡ್ (Lo Shu Grid: 4-9-2 / 3-5-7 / 8-1-6)',
        'dob_lbl': 'ಜನ್ಮ ದಿನಾಂಕ:', 'birth_no_lbl': 'ಮೂಲ ಸಂಖ್ಯೆ (Birth No):',
        'destiny_no_lbl': 'ಭಾಗ್ಯ ಸಂಖ್ಯೆ (Destiny No):', 'year_no_lbl': 'ವರ್ಷದ ಸಂಖ್ಯೆ (Year Root):',
        'yogas_title': '2. ವೇದಿಕ್ ಗ್ರಿಡ್ (8 ಯೋಗಗಳು) ಮತ್ತು ಲೋ ಶು ಗ್ರಿಡ್ (8 ಯೋಗಗಳು)',
        'vedic_yogas_hdr': 'ವೇದಿಕ್ ಗ್ರಿಡ್ ವಿಶೇಷ ಯೋಗಗಳು (8 Vedic Grid Yogas):',
        'loshu_yogas_hdr': 'ಲೋ ಶು ಗ್ರಿಡ್ ವಿಶೇಷ ಯೋಗಗಳು (8 Lo Shu Grid Yogas):',
        'no_yoga_msg': 'ಈ ಜನ್ಮ ದಿನಾಂಕದ ಗ್ರಿಡ್‌ನಲ್ಲಿ 8 ಪ್ರಮುಖ ಯೋಗಗಳು ನೇರವಾಗಿ ರೂಪುಗೊಂಡಿಲ್ಲ. ಮಿಸ್ ಆಗಿರುವ ಸಂಖ್ಯೆಗಳಿಗೆ ಪರಿಹಾರಗಳನ್ನು ಅನುಸರಿಸಬಹುದು.',
        'pyramid_title': '3. ಪಿರಮಿಡ್ ನಂಬರ್ ವಿಶ್ಲೇಷಣೆ (Name, DOB & Mobile Pyramid Analysis)',
        'name_pyr_hdr': 'ಹೆಸರಿನ ಪಿರಮಿಡ್ (Name Pyramid):', 'final_name_pyr': '✨ ಹೆಸರಿನ ಅಂತಿಮ ಪಿರಮಿಡ್ ಸಂಖ್ಯೆ (Final Name Pyramid Number):',
        'dob_pyr_hdr': 'ಜನ್ಮ ದಿನಾಂಕದ ಪಿರಮಿಡ್ (DOB Pyramid):', 'final_dob_pyr': '✨ ಜನ್ಮ ದಿನಾಂಕದ ಅಂತಿಮ ಪಿರಮಿಡ್ ಸಂಖ್ಯೆ (Final DOB Pyramid Number):',
        'mob_pyr_hdr': 'ಮೊಬೈಲ್ ಸಂಖ್ಯೆಯ ಪಿರಮಿಡ್ (Mobile Pyramid):', 'final_mob_pyr': '✨ ಮೊಬೈಲ್ ಸಂಖ್ಯೆಯ ಅಂತಿಮ ಪಿರಮಿಡ್ ಸಂಖ್ಯೆ (Final Mobile Pyramid Number):',
        'partner_title': '4. ವಿವಾಹ ಅಥವಾ ವ್ಯಾಪಾರ ಪಾಲುದಾರಿಕೆ ಹೊಂದಾಣಿಕೆ (Marriage & Partnership Matching)',
        'p1_lbl': 'ವ್ಯಕ್ತಿ 1:', 'p2_lbl': 'ಪಾಲುದಾರರು:', 'spouse_default': 'ಸಂಗಾತಿ',
        'tara_mad_title': '5. ತಾರಾಬಲ ಮತ್ತು ಮಧಭೂಡ ವಿಶ್ಲೇಷಣೆ (Tarabala & Madabhuda)',
        'tara_count_lbl': 'ತಾರೆ ಎಣಿಕೆ (1–9):', 'tara_name_lbl': 'ತಾರೆ ವಿಧ:',
        'tara_result_lbl': 'ತಾರಾಬಲ ಫಲ:', 'madabhuda_lbl': 'ಮಧಭೂಡ (Madabhuda) ಸ್ಥಿತಿ:',
        'ashtaka_title': '6. ಅಷ್ಟಕವರ್ಗ ವಿಶ್ಲೇಷಣೆ (Ashtakavargha Bindus)',
        'sav_total_lbl': 'ಒಟ್ಟು ಅಷ್ಟಕವರ್ಗ ಬಿಂದುಗಳು:', 'best_rashi_lbl': 'ಅತ್ಯಧಿಕ ಬಿಂದುಗಳ ರಾಶಿ:',
        'py_pm_title': '7. ವಾರ್ಷಿಕ ಮತ್ತು ಮಾಸಿಕ ಭವಿಷ್ಯ (Personal Year & Month Predictions)',
        'py_lbl': 'ವಾರ್ಷಿಕ ಭವಿಷ್ಯ (Personal Year', 'num_force_lbl': 'ಸಂಖ್ಯಾ ಬಲ:', 'pm_lbl': 'ಮಾಸಿಕ ಭವಿಷ್ಯ (Personal Month -',
        'lucky_title': '8. ಅದೃಷ್ಟ ಬಣ್ಣ, ದಿಕ್ಕು, ರತ್ನ, ಕುವಾ ನಂಬರ್ ಮತ್ತು ವೃತ್ತಿ',
        'colors_lbl': '🎨 ಅದೃಷ್ಟ ಬಣ್ಣಗಳು (Lucky Colors):', 'dir_lbl': '🧭 ಅದೃಷ್ಟ ದಿಕ್ಕು (Lucky Direction):',
        'gem_lbl': '💎 ಅದೃಷ್ಟ ರತ್ನ (Lucky Gemstone):', 'days_lbl': '📅 ಅದೃಷ್ಟ ವಾರಗಳು (Lucky Days):',
        'kua_lbl': '☯️ ಕುವಾ ನಂಬರ್ (Kua Number):', 'prof_lbl': '💼 ಅದೃಷ್ಟ ವೃತ್ತಿ / ಉದ್ಯೋಗ (Lucky Profession):',
        'mob_adv_title': '📱 ಮೊಬೈಲ್ ಸಂಖ್ಯೆ ಆಳವಾದ ವಿಶ್ಲೇಷಣೆ (9 ಜೋಡಿಗಳು)',
        'mob_sum_lbl': 'ಸಂಖ್ಯೆಯ ಮೊತ್ತ:', 'mob_end_lbl': 'ಕೊನೆಯ ಅಂಕಿ:', 'mob_pairs_lbl': '9 ಜೋಡಿಗಳ ವಿಶ್ಲೇಷಣೆ:',
        'good_tag': 'ಶುಭ', 'bad_tag': 'ಅಶುಭ',
        'pair_note': '* ಹಸಿರು ಬಣ್ಣದಲ್ಲಿರುವ ಜೋಡಿಗಳು ಶುಭಕರ (Good Pairs), ಕೆಂಪು ಬಣ್ಣದಲ್ಲಿರುವವು ಅಶುಭ (Bad Pairs) ಎಂದು ಪರಿಗಣಿಸಲಾಗಿದೆ.',
        'missing_title': '9. ಮಿಸ್ ಆಗಿರುವ ಸಂಖ್ಯೆಗಳು ಮತ್ತು ಪರಿಹಾರಗಳು (Missing Numbers Remedies)',
        'num_prefix': 'ಸಂಖ್ಯೆ', 'all_present_msg': 'ಅದ್ಭುತ! ನಿಮ್ಮ ಜನ್ಮ ದಿನಾಂಕದಲ್ಲಿ ಎಲ್ಲಾ ಸಂಖ್ಯೆಗಳೂ ಲಭ್ಯವಿವೆ.',
        'name_ana_title': '10. ಹೆಸರಿನ ವಿಶ್ಲೇಷಣೆ ಮತ್ತು ತಿದ್ದುಪಡಿ ಸಲಹೆಗಾರ (Name Analysis & Correction Tool)',
        'chaldean_lbl': 'ಚಾಲ್ಡಿಯನ್ (Chaldean):', 'total_lbl': 'ಒಟ್ಟು ಮೊತ್ತ:',
        'advice_title': '✨ ಹೆಸರು ತಿದ್ದುಪಡಿ ಸಲಹೆ (Name Correction Advice):',
        'pythag_lbl': 'ಪೈಥಾಗರಿಯನ್ (Pythagorean):',
        'compat_title': '11. ಹೆಸರು ಮತ್ತು ಜನ್ಮ ದಿನಾಂಕ ಹೊಂದಾಣಿಕೆ (Name vs DOB Compatibility)',
        'chal_card_title': 'ಚಾಲ್ಡಿಯನ್ ಹೆಸರಿನ ಸಂಖ್ಯೆ (Chaldean Root:',
        'pyth_card_title': 'ಪೈಥಾಗರಿಯನ್ ಹೆಸರಿನ ಸಂಖ್ಯೆ (Pythagorean Root:',
        'common_lucky_title': '12. ಸಾಮಾನ್ಯ ಅದೃಷ್ಟ ಸಂಖ್ಯೆಗಳು (Lucky Numbers)',
        'b_friends_lbl': 'ಮೂಲ ಸಂಖ್ಯೆ', 'd_friends_lbl': 'ಭಾಗ್ಯ ಸಂಖ್ಯೆ', 'friends_suffix': 'ಸ್ನೇಹ ಸಂಖ್ಯೆಗಳು:',
        'common_lbl': '✨ ಅತ್ಯಂತ ಶುಭ ಸಂಖ್ಯೆಗಳು (Common Lucky Numbers):',
        'print_btn': '📥 Download / Save Full Numerology Report as PDF'
    },
    'en': {
        'lang_label': 'Language', 'welcome': 'Welcome',
        'portal_title': 'Complete Numerology, Grids, Marriage Matching, Tarabala & Ashtakavargha Portal',
        'p1_heading': 'Person 1 Details:',
        'dob_ph': 'Date of Birth (DD-MM-YYYY)', 'name_ph': 'Full Name',
        'mobile_ph': 'Mobile Number (e.g. 9513129695)', 'time_ph': 'Birth Time (e.g. 7.36 AM)',
        'place_ph': 'Birth Place (e.g. Halebidu, Hassan)',
        'lagna_lbl': 'Lagna:', 'rashi_lbl': 'Rashi:', 'nak_lbl': 'Nakshatra:',
        'transit_nak_lbl': 'Transit / Day Nakshatra (Tarabala & Madabhuda):',
        'p2_heading': 'Partner / Spouse Details:',
        'p2_name_ph': 'Partner Name', 'p2_dob_ph': 'Partner Date of Birth (DD-MM-YYYY)',
        'ashtaka_heading': 'Ashtakavargha Planet Signs:',
        'calc_btn': 'Calculate Yogas, Matching & Reports',
        'strength_title': '🌟 Birth & Name Strength Analysis',
        'birth_deg_lbl': '📅 Average Degree of Birth Strength:', 'lifestyle_lbl': '🎯 Lifestyle:',
        'name_freq_lbl': '🔤 Name Sound Frequency:',
        'grid_title': '1. Date of Birth, Vedic Grid (3-1-9) & Lo Shu Grid (4-9-2)',
        'vedic_grid_lbl': 'Vedic Grid (3-1-9 / 6-7-5 / 2-8-4)',
        'loshu_grid_lbl': 'Lo Shu Grid (4-9-2 / 3-5-7 / 8-1-6)',
        'dob_lbl': 'Date of Birth:', 'birth_no_lbl': 'Birth Number:',
        'destiny_no_lbl': 'Destiny Number:', 'year_no_lbl': 'Year Root:',
        'yogas_title': '2. Vedic Grid (8 Yogas) & Lo Shu Grid (8 Yogas)',
        'vedic_yogas_hdr': '8 Vedic Grid Yogas:', 'loshu_yogas_hdr': '8 Lo Shu Grid Yogas:',
        'no_yoga_msg': 'None of the 8 major yogas formed directly in this grid. Remedies for missing numbers can be followed.',
        'pyramid_title': '3. Name, DOB & Mobile Pyramid Analysis',
        'name_pyr_hdr': 'Name Pyramid:', 'final_name_pyr': '✨ Final Name Pyramid Number:',
        'dob_pyr_hdr': 'DOB Pyramid:', 'final_dob_pyr': '✨ Final DOB Pyramid Number:',
        'mob_pyr_hdr': 'Mobile Pyramid:', 'final_mob_pyr': '✨ Final Mobile Pyramid Number:',
        'partner_title': '4. Marriage & Partnership Matching',
        'p1_lbl': 'Person 1:', 'p2_lbl': 'Partner:', 'spouse_default': 'Partner',
        'tara_mad_title': '5. Tarabala & Madabhuda Analysis',
        'tara_count_lbl': 'Tara Count (1–9):', 'tara_name_lbl': 'Tara Name:',
        'tara_result_lbl': 'Tarabala Result:', 'madabhuda_lbl': 'Madabhuda Status:',
        'ashtaka_title': '6. Ashtakavargha Analysis',
        'sav_total_lbl': 'Total Ashtakavargha Bindus:', 'best_rashi_lbl': 'Highest Bindus Sign:',
        'py_pm_title': '7. Personal Year & Month Predictions',
        'py_lbl': 'Personal Year', 'num_force_lbl': 'Number Force:', 'pm_lbl': 'Personal Month -',
        'lucky_title': '8. Lucky Colors, Direction, Gemstone, Kua & Profession',
        'colors_lbl': '🎨 Lucky Colors:', 'dir_lbl': '🧭 Lucky Direction:',
        'gem_lbl': '💎 Lucky Gemstone:', 'days_lbl': '📅 Lucky Days:',
        'kua_lbl': '☯️ Kua Number:', 'prof_lbl': '💼 Lucky Profession:',
        'mob_adv_title': '📱 Advanced Mobile Analysis (9 Pairs)',
        'mob_sum_lbl': 'Digit Sum:', 'mob_end_lbl': 'Ending Digit:', 'mob_pairs_lbl': '9 Pairs Analysis:',
        'good_tag': 'Good', 'bad_tag': 'Bad',
        'pair_note': '* Green pairs indicate Good Pairs; Red pairs indicate Bad Pairs.',
        'missing_title': '9. Missing Numbers & Remedies',
        'num_prefix': 'Number', 'all_present_msg': 'Great! All numbers 1 to 9 are present in your birth grid.',
        'name_ana_title': '10. Name Analysis & Correction Tool',
        'chaldean_lbl': 'Chaldean:', 'total_lbl': 'Total:',
        'advice_title': '✨ Name Correction Advice:', 'pythag_lbl': 'Pythagorean:',
        'compat_title': '11. Name vs DOB Compatibility',
        'chal_card_title': 'Chaldean Name Number (Chaldean Root:',
        'pyth_card_title': 'Pythagorean Name Number (Pythagorean Root:',
        'common_lucky_title': '12. Common Lucky Numbers',
        'b_friends_lbl': 'Birth Number', 'd_friends_lbl': 'Destiny Number', 'friends_suffix': 'Friendly Numbers:',
        'common_lbl': '✨ Common Lucky Numbers:',
        'print_btn': '📥 Download / Save Full Numerology Report as PDF'
    },
    'ta': {
        'lang_label': 'மொழி (Language)', 'welcome': 'வணக்கம் (Welcome)',
        'portal_title': 'முழுமையான எண்கணிதம், கட்டங்கள், திருமண பொருத்தம், தாராபலம் மற்றும் அஷ்டகவர்க்கம்',
        'p1_heading': 'நபர் 1 (Person 1) விவரங்கள்:',
        'dob_ph': 'பிறந்த தேதி (DD-MM-YYYY)', 'name_ph': 'முழுப் பெயர் (Full Name)',
        'mobile_ph': 'கைபேசி எண் (எ.கா: 9513129695)', 'time_ph': 'பிறந்த நேரம் (எ.கா: 7.36 AM)',
        'place_ph': 'பிறந்த இடம்', 'lagna_lbl': 'லக்னம்:', 'rashi_lbl': 'ராசி:', 'nak_lbl': 'நட்சத்திரம்:',
        'transit_nak_lbl': 'நாள் / கோச்சார நட்சத்திரம் (தாராபலம் & மதபூட):',
        'p2_heading': 'துணைவர் / பங்குதாரர் விவரங்கள்:',
        'p2_name_ph': 'துணைவர் பெயர்', 'p2_dob_ph': 'துணைவர் பிறந்த தேதி (DD-MM-YYYY)',
        'ashtaka_heading': 'அஷ்டகவர்க்க கிரக நிலைகள்:',
        'calc_btn': 'முழு பகுப்பாய்வு (Calculate Yogas, Matching & Reports)',
        'strength_title': '🌟 பிறப்பு பலம் மற்றும் பெயர் ஒலி அதிர்வெண் (Birth & Name Strength Analysis)',
        'birth_deg_lbl': '📅 பிறப்பு பல சராசரி டிகிரி:', 'lifestyle_lbl': '🎯 வாழ்க்கை முறை (Lifestyle):',
        'name_freq_lbl': '🔤 பெயர் ஒலி அதிர்வெண் (Name Sound Frequency):',
        'grid_title': '1. பிறந்த தேதி, வேதிக் கிரிட் (3-1-9) மற்றும் லோ ஷு கிரிட் (4-9-2)',
        'vedic_grid_lbl': 'வேதிக் கிரிட் (Vedic Grid: 3-1-9 / 6-7-5 / 2-8-4)',
        'loshu_grid_lbl': 'லோ ஷு கிரிட் (Lo Shu Grid: 4-9-2 / 3-5-7 / 8-1-6)',
        'dob_lbl': 'பிறந்த தேதி:', 'birth_no_lbl': 'மூல எண் (Birth No):',
        'destiny_no_lbl': 'பாக்கிய எண் (Destiny No):', 'year_no_lbl': 'ஆண்டு எண் (Year Root):',
        'yogas_title': '2. வேதிக் கிரிட் (8 யோகங்கள்) மற்றும் லோ ஷு கிரிட் (8 யோகங்கள்)',
        'vedic_yogas_hdr': 'வேதிக் கிரிட் 8 சிறப்பு யோகங்கள்:', 'loshu_yogas_hdr': 'லோ ஷு கிரிட் 8 சிறப்பு யோகங்கள்:',
        'no_yoga_msg': 'இந்த பிறந்த தேதி கட்டத்தில் 8 முக்கிய யோகங்கள் நேரடியாக அமையவில்லை. விடுபட்ட எண்களுக்கான பரிகாரங்களைப் பின்பற்றலாம்.',
        'pyramid_title': '3. பிரமிடு எண் பகுப்பாய்வு (Name, DOB & Mobile Pyramid Analysis)',
        'name_pyr_hdr': 'பெயர் பிரமிடு (Name Pyramid):', 'final_name_pyr': '✨ இறுதி பெயர் பிரமிடு எண்:',
        'dob_pyr_hdr': 'பிறந்த தேதி பிரமிடு (DOB Pyramid):', 'final_dob_pyr': '✨ இறுதி பிறந்த தேதி பிரமிடு எண்:',
        'mob_pyr_hdr': 'கைபேசி எண் பிரமிடு (Mobile Pyramid):', 'final_mob_pyr': '✨ இறுதி கைபேசி பிரமிடு எண்:',
        'partner_title': '4. திருமண அல்லது தொழில் கூட்டணி பொருத்தம்',
        'p1_lbl': 'நபர் 1:', 'p2_lbl': 'துணைவர்:', 'spouse_default': 'துணைவர்',
        'tara_mad_title': '5. தாராபலம் மற்றும் மதபூட பகுப்பாய்வு',
        'tara_count_lbl': 'தாரை எண்ணிக்கை (1–9):', 'tara_name_lbl': 'தாரை பெயர்:',
        'tara_result_lbl': 'தாராபல பலன்:', 'madabhuda_lbl': 'மதபூட நிலை:',
        'ashtaka_title': '6. அஷ்டகவர்க்கம் பகுப்பாய்வு',
        'sav_total_lbl': 'மொத்த அஷ்டகவர்க்க புள்ளிகள்:', 'best_rashi_lbl': 'அதிக புள்ளிகள் கொண்ட ராசி:',
        'py_pm_title': '7. ஆண்டு மற்றும் மாத பலன்கள் (Personal Year & Month Predictions)',
        'py_lbl': 'ஆண்டு பலன் (Personal Year', 'num_force_lbl': 'எண் பலம்:', 'pm_lbl': 'மாத பலன் (Personal Month -',
        'lucky_title': '8. அதிர்ஷ்ட நிறம், திசை, ரத்தினம், குவா எண் மற்றும் தொழில்',
        'colors_lbl': '🎨 அதிர்ஷ்ட நிறங்கள்:', 'dir_lbl': '🧭 அதிர்ஷ்ட திசை:',
        'gem_lbl': '💎 அதிர்ஷ்ட ரத்தினம்:', 'days_lbl': '📅 அதிர்ஷ்ட நாட்கள்:',
        'kua_lbl': '☯️ குவா எண் (Kua Number):', 'prof_lbl': '💼 அதிர்ஷ்ட தொழில்:',
        'mob_adv_title': '📱 கைபேசி எண் ஆழமான பகுப்பாய்வு (9 ஜோடிகள்)',
        'mob_sum_lbl': 'எண்களின் கூட்டுத்தொகை:', 'mob_end_lbl': 'கடைசி எண்:', 'mob_pairs_lbl': '9 ஜோடிகள் பகுப்பாய்வு:',
        'good_tag': 'சுபம்', 'bad_tag': 'அசுபம்',
        'pair_note': '* பச்சை நிற ஜோடிகள் சுபமானவை (Good), சிவப்பு நிற ஜோடிகள் எச்சரிக்கைக்குரியவை (Bad).',
        'missing_title': '9. விடுபட்ட எண்கள் மற்றும் பரிகாரங்கள்',
        'num_prefix': 'எண்', 'all_present_msg': 'சிறப்பு! உங்கள் பிறந்த தேதி கட்டத்தில் அனைத்து எண்களும் உள்ளன.',
        'name_ana_title': '10. பெயர் பகுப்பாய்வு மற்றும் திருத்த ஆலோசனை',
        'chaldean_lbl': 'கால்டியன் (Chaldean):', 'total_lbl': 'மொத்தம்:',
        'advice_title': '✨ பெயர் திருத்த ஆலோசனை:', 'pythag_lbl': 'பைதாகோரியன் (Pythagorean):',
        'compat_title': '11. பெயர் மற்றும் பிறந்த தேதி பொருத்தம்',
        'chal_card_title': 'கால்டியன் பெயர் எண் (Chaldean Root:',
        'pyth_card_title': 'பைதாகோரியன் பெயர் எண் (Pythagorean Root:',
        'common_lucky_title': '12. பொதுவான அதிர்ஷ்ட எண்கள்',
        'b_friends_lbl': 'மூல எண்', 'd_friends_lbl': 'பாக்கிய எண்', 'friends_suffix': 'நட்பு எண்கள்:',
        'common_lbl': '✨ மிகவும் சுப எண்கள்:',
        'print_btn': '📥 Download / Save Full Numerology Report as PDF'
    },
    'te': {
        'lang_label': 'భాష (Language)', 'welcome': 'స్వాగతం (Welcome)',
        'portal_title': 'సంపూర్ణ సంఖ్యాశాస్త్రం, గ్రిడ్‌లు, వివాహ పొంతన, తారాబలం మరియు అష్టకవర్గ పోర్టల్',
        'p1_heading': 'వ్యక్తి 1 (Person 1) వివరాలు:',
        'dob_ph': 'పుట్టిన తేదీ (DD-MM-YYYY)', 'name_ph': 'పూర్తి పేరు (Full Name)',
        'mobile_ph': 'మొబైల్ నంబర్ (ఉదా: 9513129695)', 'time_ph': 'పుట్టిన సమయం (ఉదా: 7.36 AM)',
        'place_ph': 'పుట్టిన ప్రదేశం', 'lagna_lbl': 'లగ్నం:', 'rashi_lbl': 'రాశి:', 'nak_lbl': 'నక్షత్రం:',
        'transit_nak_lbl': 'రోజు / గోచార నక్షత్రం (తారాబలం & మధభూడ):',
        'p2_heading': 'భాగస్వామి / జీవిత భాగస్వామి వివరాలు:',
        'p2_name_ph': 'భాగస్వామి పేరు', 'p2_dob_ph': 'భాగస్వామి పుట్టిన తేదీ (DD-MM-YYYY)',
        'ashtaka_heading': 'అష్టకవర్గ గ్రహ రాశి స్థానాలు:',
        'calc_btn': 'పూర్తి విశ్లేషణ (Calculate Yogas, Matching & Reports)',
        'strength_title': '🌟 పుట్టుక బలం మరియు పేరు ధ్వని ఫ్రీక్వెన్సీ (Birth & Name Strength Analysis)',
        'birth_deg_lbl': '📅 పుట్టుక బలం సగటు డిగ్రీ:', 'lifestyle_lbl': '🎯 జీవనశైలి (Lifestyle):',
        'name_freq_lbl': '🔤 పేరు ధ్వని ఫ్రీక్వెన్సీ (Name Sound Frequency):',
        'grid_title': '1. పుట్టిన తేదీ, వేదిక్ గ్రిడ్ (3-1-9) మరియు లో షూ గ్రిడ్ (4-9-2)',
        'vedic_grid_lbl': 'వేదిక్ గ్రిడ్ (Vedic Grid: 3-1-9 / 6-7-5 / 2-8-4)',
        'loshu_grid_lbl': 'లో షూ గ్రిడ్ (Lo Shu Grid: 4-9-2 / 3-5-7 / 8-1-6)',
        'dob_lbl': 'పుట్టిన తేదీ:', 'birth_no_lbl': 'మూల సంఖ్య (Birth No):',
        'destiny_no_lbl': 'భాగ్య సంఖ్య (Destiny No):', 'year_no_lbl': 'సంవత్సర సంఖ్య (Year Root):',
        'yogas_title': '2. వేదిక్ గ్రిడ్ (8 యోగాలు) మరియు లో షూ గ్రిడ్ (8 యోగాలు)',
        'vedic_yogas_hdr': 'వేదిక్ గ్రిడ్ 8 ప్రత్యేక యోగాలు:', 'loshu_yogas_hdr': 'లో షూ గ్రిడ్ 8 ప్రత్యేక యోగాలు:',
        'no_yoga_msg': 'ఈ పుట్టిన తేదీ గ్రిడ్‌లో 8 ప్రధాన యోగాలు నేరుగా ఏర్పడలేదు. లోపించిన సంఖ్యలకు పరిహారాలు పాటించవచ్చు.',
        'pyramid_title': '3. పిరమిడ్ సంఖ్య విశ్లేషణ (Name, DOB & Mobile Pyramid Analysis)',
        'name_pyr_hdr': 'పేరు పిరమిడ్ (Name Pyramid):', 'final_name_pyr': '✨ తుది పేరు పిరమిడ్ సంఖ్య:',
        'dob_pyr_hdr': 'పుట్టిన తేదీ పిరమిడ్ (DOB Pyramid):', 'final_dob_pyr': '✨ తుది పుట్టిన తేదీ పిరమిడ్ సంఖ్య:',
        'mob_pyr_hdr': 'మొబైల్ పిరమిడ్ (Mobile Pyramid):', 'final_mob_pyr': '✨ తుది మొబైల్ పిరమిడ్ సంఖ్య:',
        'partner_title': '4. వివాహ లేదా వ్యాపార భాగస్వామ్య అనుకూలత',
        'p1_lbl': 'వ్యక్తి 1:', 'p2_lbl': 'భాగస్వామి:', 'spouse_default': 'భాగస్వామి',
        'tara_mad_title': '5. తారాబలం మరియు మధభూడ విశ్లేషణ',
        'tara_count_lbl': 'తార లెక్కింపు (1–9):', 'tara_name_lbl': 'తార పేరు:',
        'tara_result_lbl': 'తారాబల ఫలితం:', 'madabhuda_lbl': 'మధభూడ స్థితి:',
        'ashtaka_title': '6. అష్టకవర్గ విశ్లేషణ',
        'sav_total_lbl': 'మొత్తం అష్టకవర్గ బిందువులు:', 'best_rashi_lbl': 'అత్యధిక బిందువుల రాశి:',
        'py_pm_title': '7. వార్షిక మరియు మాసిక ఫలితాలు (Personal Year & Month Predictions)',
        'py_lbl': 'వార్షిక ఫలితం (Personal Year', 'num_force_lbl': 'సంఖ్యా బలం:', 'pm_lbl': 'మాసిక ఫలితం (Personal Month -',
        'lucky_title': '8. అదృష్ట రంగు, దిశ, రత్నం, కువా నంబర్ మరియు వృత్తి',
        'colors_lbl': '🎨 అదృష్ట రంగులు:', 'dir_lbl': '🧭 అదృష్ట దిశ:',
        'gem_lbl': '💎 అదృష్ట రత్నం:', 'days_lbl': '📅 అదృష్ట రోజులు:',
        'kua_lbl': '☯️ కువా నంబర్ (Kua Number):', 'prof_lbl': '💼 అదృష్ట వృత్తి:',
        'mob_adv_title': '📱 మొబైల్ నంబర్ లోతైన విశ్లేషణ (9 జతలు)',
        'mob_sum_lbl': 'అంకెల మొత్తం:', 'mob_end_lbl': 'చివరి అంకె:', 'mob_pairs_lbl': '9 జతల విశ్లేషణ:',
        'good_tag': 'శుభం', 'bad_tag': 'అశుభం',
        'pair_note': '* ఆకుపచ్చ జతలు శుభప్రదం (Good), ఎరుపు జతలు జాగ్రత్త (Bad).',
        'missing_title': '9. లోపించిన సంఖ్యలు మరియు పరిహారాలు',
        'num_prefix': 'సంఖ్య', 'all_present_msg': 'అద్భుతం! మీ పుట్టిన తేదీ గ్రిడ్‌లో అన్ని సంఖ్యలు ఉన్నాయి.',
        'name_ana_title': '10. పేరు విశ్లేషణ మరియు సవరణ సలహా',
        'chaldean_lbl': 'చాల్డియన్ (Chaldean):', 'total_lbl': 'మొత్తం:',
        'advice_title': '✨ పేరు సవరణ సలహా:', 'pythag_lbl': 'పైథాగోరియన్ (Pythagorean):',
        'compat_title': '11. పేరు మరియు పుట్టిన తేదీ అనుకూలత',
        'chal_card_title': 'చాల్డియన్ పేరు సంఖ్య (Chaldean Root:',
        'pyth_card_title': 'పైథాగోరియన్ పేరు సంఖ్య (Pythagorean Root:',
        'common_lucky_title': '12. సాధారణ అదృష్ట సంఖ్యలు',
        'b_friends_lbl': 'మూల సంఖ్య', 'd_friends_lbl': 'భాగ్య సంఖ్య', 'friends_suffix': 'మిత్ర సంఖ్యలు:',
        'common_lbl': '✨ అత్యంత శుభ సంఖ్యలు:',
        'print_btn': '📥 Download / Save Full Numerology Report as PDF'
    },
    'hi': {
        'lang_label': 'भाषा (Language)', 'welcome': 'स्वागत है (Welcome)',
        'portal_title': 'संपूर्ण अंकशास्त्र, ग्रिड, विवाह मिलान, ताराबल एवं अष्टकवर्ग पोर्टल',
        'p1_heading': 'व्यक्ति 1 (Person 1) विवरण:',
        'dob_ph': 'जन्म तिथि (DD-MM-YYYY)', 'name_ph': 'पूरा नाम (Full Name)',
        'mobile_ph': 'मोबाइल नंबर (उदा: 9513129695)', 'time_ph': 'जन्म समय (उदा: 7.36 AM)',
        'place_ph': 'जन्म स्थान', 'lagna_lbl': 'लग्न:', 'rashi_lbl': 'राशि:', 'nak_lbl': 'नक्षत्र:',
        'transit_nak_lbl': 'दिन / गोचर नक्षत्र (ताराबल व मधभूड़):',
        'p2_heading': 'जीवनसाथी / पार्टनर विवरण:',
        'p2_name_ph': 'पार्टनर का नाम', 'p2_dob_ph': 'पार्टनर की जन्म तिथि (DD-MM-YYYY)',
        'ashtaka_heading': 'अष्टकवर्ग ग्रह राशियाँ:',
        'calc_btn': 'संपूर्ण विश्लेषण (Calculate Yogas, Matching & Reports)',
        'strength_title': '🌟 जन्म बल और नाम ध्वनि फ्रीक्वेंसी (Birth & Name Strength Analysis)',
        'birth_deg_lbl': '📅 जन्म बल औसत डिग्री:', 'lifestyle_lbl': '🎯 जीवनशैली (Lifestyle):',
        'name_freq_lbl': '🔤 नाम ध्वनि फ्रीक्वेंसी (Name Sound Frequency):',
        'grid_title': '1. जन्म तिथि, वैदिक ग्रिड (3-1-9) और लो शू ग्रिड (4-9-2)',
        'vedic_grid_lbl': 'वैदिक ग्रिड (Vedic Grid: 3-1-9 / 6-7-5 / 2-8-4)',
        'loshu_grid_lbl': 'लो शू ग्रिड (Lo Shu Grid: 4-9-2 / 3-5-7 / 8-1-6)',
        'dob_lbl': 'जन्म तिथि:', 'birth_no_lbl': 'मूलांक (Birth No):',
        'destiny_no_lbl': 'भाग्यांक (Destiny No):', 'year_no_lbl': 'वर्षांक (Year Root):',
        'yogas_title': '2. वैदिक ग्रिड (8 योग) और लो शू ग्रिड (8 योग)',
        'vedic_yogas_hdr': 'वैदिक ग्रिड के 8 विशेष योग:', 'loshu_yogas_hdr': 'लो शू ग्रिड के 8 विशेष योग:',
        'no_yoga_msg': 'इस जन्म तिथि ग्रिड में 8 प्रमुख योग सीधे नहीं बने हैं। छूटे हुए अंकों के उपाय अपनाए जा सकते हैं।',
        'pyramid_title': '3. पिरामिड अंक विश्लेषण (Name, DOB & Mobile Pyramid Analysis)',
        'name_pyr_hdr': 'नाम पिरामिड (Name Pyramid):', 'final_name_pyr': '✨ अंतिम नाम पिरामिड अंक:',
        'dob_pyr_hdr': 'जन्म तिथि पिरामिड (DOB Pyramid):', 'final_dob_pyr': '✨ अंतिम जन्म तिथि पिरामिड अंक:',
        'mob_pyr_hdr': 'मोबाइल पिरामिड (Mobile Pyramid):', 'final_mob_pyr': '✨ अंतिम मोबाइल पिరమిड अंक:',
        'partner_title': '4. विवाह या व्यावसायिक साझेदारी अनुकूलता',
        'p1_lbl': 'व्यक्ति 1:', 'p2_lbl': 'पार्टनर:', 'spouse_default': 'पार्टनर',
        'tara_mad_title': '5. ताराबल और मधभूड़ विश्लेषण',
        'tara_count_lbl': 'तारा गणना (1–9):', 'tara_name_lbl': 'तारा नाम:',
        'tara_result_lbl': 'ताराबल फल:', 'madabhuda_lbl': 'मधभूड़ स्थिति:',
        'ashtaka_title': '6. अष्टकवर्ग विश्लेषण',
        'sav_total_lbl': 'कुल अष्टकवर्ग बिंदु:', 'best_rashi_lbl': 'सर्वाधिक बिंदु वाली राशि:',
        'py_pm_title': '7. वार्षिक और मासिक भविष्यफल (Personal Year & Month Predictions)',
        'py_lbl': 'वार्षिक भविष्यफल (Personal Year', 'num_force_lbl': 'अंक बल:', 'pm_lbl': 'मासिक भविष्यफल (Personal Month -',
        'lucky_title': '8. शुभ रंग, दिशा, रत्न, कुआ नंबर और करियर',
        'colors_lbl': '🎨 शुभ रंग:', 'dir_lbl': '🧭 शुभ दिशा:',
        'gem_lbl': '💎 शुभ रत्न:', 'days_lbl': '📅 शुभ दिन:',
        'kua_lbl': '☯️ कुआ नंबर (Kua Number):', 'prof_lbl': '💼 शुभ करियर / व्यवसाय:',
        'mob_adv_title': '📱 मोबाइल नंबर गहन विश्लेषण (9 जोड़ियाँ)',
        'mob_sum_lbl': 'अंकों का योग:', 'mob_end_lbl': 'अंतिम अंक:', 'mob_pairs_lbl': '9 जोड़ियों का विश्लेषण:',
        'good_tag': 'शुभ', 'bad_tag': 'अशुभ',
        'pair_note': '* हरे रंग की जोड़ियाँ शुभ (Good), लाल रंग की जोड़ियाँ अशुभ (Bad) मानी जाती हैं।',
        'missing_title': '9. छूटे हुए अंक और उपाय (Missing Numbers Remedies)',
        'num_prefix': 'अंक', 'all_present_msg': 'उत्तम! आपकी जन्म तिथि ग्रिड में सभी अंक उपस्थित हैं।',
        'name_ana_title': '10. नाम विश्लेषण और सुधार सुझाव',
        'chaldean_lbl': 'चाल्डियन (Chaldean):', 'total_lbl': 'कुल योग:',
        'advice_title': '✨ नाम सुधार सुझाव:', 'pythag_lbl': 'पाइथागोरियन (Pythagorean):',
        'compat_title': '11. नाम और जन्म तिथि अनुकूलता',
        'chal_card_title': 'चाल्डियन नाम अंक (Chaldean Root:',
        'pyth_card_title': 'पाइथागोरियन नाम अंक (Pythagorean Root:',
        'common_lucky_title': '12. सामान्य शुभ अंक (Lucky Numbers)',
        'b_friends_lbl': 'मूलांक', 'd_friends_lbl': 'भाग्यांक', 'friends_suffix': 'मित्र अंक:',
        'common_lbl': '✨ सर्वाधिक शुभ अंक:',
        'print_btn': '📥 Download / Save Full Numerology Report as PDF'
    }
}

GOOD_PAIRS = {'11', '12', '13', '15', '17', '19', '25', '31', '33', '37', '39', '51', '52', '55', '57', '59', '66', '69', '71', '73', '75', '77', '83', '91', '92', '93', '95', '96', '99'}
BAD_PAIRS = {'14', '16', '21', '22', '23', '24', '26', '27', '28', '30', '32', '34', '35', '36', '38', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '53', '54', '56', '58', '60', '61', '62', '63', '64', '65', '67', '68', '70', '72', '74', '76', '78', '79', '80', '81', '82', '84', '85', '86', '87', '88', '89', '90', '94', '97', '98'}

def normalize_lang(lang_code):
    return lang_code if lang_code in UI_TEXT else 'kn'

def reduce_to_single(num):
    while num > 9:
        num = sum(int(c) for c in str(num))
    return num

def get_relation(name_num, target_num, lang='kn'):
    if not name_num or not target_num:
        return "-"
    rel = RELATIONS.get(target_num, {'friends': [], 'enemies': [], 'neutral': []})
    labels = {
        'kn': {'f': 'Friend (ಸ್ನೇಹ - ಅತ್ಯುತ್ತಮ ಹೊಂದಾಣಿಕೆ)', 'e': 'Enemy (ಶತ್ರು - ಎಚ್ಚರಿಕೆ ವಹಿಸಬೇಕು)', 'n': 'Neutral (ಸಮ - ಸಾಮಾನ್ಯ ಹೊಂದಾಣಿಕೆ)'},
        'en': {'f': 'Friend (Good Harmony)', 'e': 'Enemy (Needs Caution)', 'n': 'Neutral (Moderate)'},
        'ta': {'f': 'Friend (நட்பு - மிகச் சிறந்த பொருத்தம்)', 'e': 'Enemy (பகை - கவனம் தேவை)', 'n': 'Neutral (சமம் - சாதாரண பொருத்தம்)'},
        'te': {'f': 'Friend (మిత్ర - ఉత్తమ అనుకూలత)', 'e': 'Enemy (శత్రు - జాగ్రత్త అవసరం)', 'n': 'Neutral (సమ - సాధారణ అనుకూలత)'},
        'hi': {'f': 'Friend (मित्र - उत्तम अनुकूलता)', 'e': 'Enemy (शत्रु - सावधानी आवश्यक)', 'n': 'Neutral (सम - सामान्य अनुकूलता)'}
    }
    lb = labels.get(lang, labels['kn'])
    if name_num in rel['friends']:
        return lb['f']
    if name_num in rel['enemies']:
        return lb['e']
    return lb['n']

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
    return {
        'pair_results': pair_results,
        'total_sum': total_sum,
        'root_no': reduce_to_single(total_sum),
        'ending_no': int(digits[-1])
    }

def calculate_pyramid(name_str):
    upper_name = ''.join([ch for ch in name_str.upper() if ch in CHALDEAN_MAP])
    if not upper_name:
        return []
    row = [CHALDEAN_MAP[ch] for ch in upper_name]
    pyramid_rows = [row.copy()]
    while len(row) > 1:
        row = [reduce_to_single(row[i] + row[i+1]) for i in range(len(row) - 1)]
        pyramid_rows.append(row.copy())
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
            next_row.append(reduce_to_single(s) if s > 0 else 0)
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
            next_row.append(reduce_to_single(s) if s > 0 else 0)
        pyramid_rows.append(next_row.copy())
        row = next_row
    return pyramid_rows

def analyze_vedic_grid_yogas(present_numbers, lang='kn'):
    yoga_defs = VEDIC_YOGAS_8_LANG.get(lang, VEDIC_YOGAS_8_LANG['kn'])
    return [{'name': y['name'], 'desc': y['desc']} for y in yoga_defs if y['nums'].issubset(present_numbers)]

def analyze_loshu_grid_yogas(present_numbers, lang='kn'):
    yoga_defs = LOSHU_YOGAS_8_LANG.get(lang, LOSHU_YOGAS_8_LANG['kn'])
    return [{'name': y['name'], 'desc': y['desc']} for y in yoga_defs if y['nums'].issubset(present_numbers)]

def calculate_tarabala_and_madabhuda(birth_nak, transit_nak, lang='kn'):
    if birth_nak not in NAKSHATRAS or transit_nak not in NAKSHATRAS:
        return None
    b_idx = NAKSHATRAS.index(birth_nak)
    t_idx = NAKSHATRAS.index(transit_nak)
    diff = (t_idx - b_idx) % 27 + 1
    tara_num = ((diff - 1) % 9) + 1
    tara_info = TARA_NAMES_LANG.get(lang, TARA_NAMES_LANG['kn']).get(tara_num, ('', ''))
    mad_msgs = {
        'kn': {
            True: f'ಮಧಭೂಡ / ಮದಬೂಡ ಪರಿಗಣನೆ: ಇದು {tara_num}ನೇ ತಾರೆಯಾಗಿದ್ದು (3/5/7 ತಾರಾ ವರ್ಗ), ಮಧಭೂಡ/ಅಡೆತಡೆ ಸೂಚನೆ ಇದೆ — ಮುಖ್ಯ ಕಾರ್ಯಗಳಲ್ಲಿ ಎಚ್ಚರಿಕೆ ಮತ್ತು ಪರಿಹಾರ ಅನುಸರಿಸಿ.',
            False: f'ಮಧಭೂಡ / ಮದಬೂಡ ಪರಿಗಣನೆ: ಇದು {tara_num}ನೇ ತಾರೆಯಾಗಿದ್ದು, ಪ್ರತಿಕೂಲ ಮಧಭೂಡ (3, 5, 7) ತಾರೆ ಅಲ್ಲ — ಕಾರ್ಯಗಳಿಗೆ ಅನುಕೂಲಕರವಾಗಿದೆ.'
        },
        'en': {
            True: f'Madabhuda Status: Tara #{tara_num} falls in the 3/5/7 caution group — exercise care and follow remedies.',
            False: f'Madabhuda Status: Tara #{tara_num} is outside the 3/5/7 Madabhuda caution group — generally favorable.'
        },
        'ta': {
            True: f'மதபூட நிலை: இது {tara_num}-வது தாரை (3/5/7 எச்சரிக்கை வகை) — கவனமாகச் செயல்படவும்.',
            False: f'மதபூட நிலை: இது {tara_num}-வது தாரை — 3, 5, 7 மதபூட எச்சரிக்கையில் இல்லை, சாதகமானது.'
        },
        'te': {
            True: f'మధభూడ స్థితి: ఇది {tara_num}వ తార (3/5/7 జాగ్రత్త వర్గం) — జాగ్రత్తగా వ్యవహరించండి.',
            False: f'మధభూడ స్థితి: ఇది {tara_num}వ తార — 3, 5, 7 మధభూడ జాగ్రత్తలో లేదు, అనుకూలం.'
        },
        'hi': {
            True: f'मधभूड़ स्थिति: यह {tara_num}वाँ तारा (3/5/7 सावधानी वर्ग) है — सावधानी बरतें और उपाय करें।',
            False: f'मधभूड़ स्थिति: यह {tara_num}वाँ तारा है — 3, 5, 7 मधभूड़ श्रेणी में नहीं है, अनुकूल है।'
        }
    }
    is_mad = tara_num in {3, 5, 7}
    nak_map = NAKSHATRA_LABELS.get(lang, NAKSHATRA_LABELS['kn'])
    return {
        'birth_nak_disp': nak_map.get(birth_nak, birth_nak),
        'transit_nak_disp': nak_map.get(transit_nak, transit_nak),
        'nak_distance': diff,
        'tara_num': tara_num,
        'tara_name': tara_info[0],
        'tara_desc': tara_info[1],
        'madabhuda_text': mad_msgs.get(lang, mad_msgs['kn'])[is_mad]
    }

def calculate_ashtakavargha(planet_positions, lang='kn'):
    rashi_bindus = {r: 0 for r in RASHIS}
    per_planet_counts = {}
    for planet, offsets in BAV_OFFSETS.items():
        p_sign = planet_positions.get(planet, 'Mesha')
        if p_sign not in RASHIS:
            p_sign = 'Mesha'
        start_idx = RASHIS.index(p_sign)
        p_total = 0
        for off in offsets:
            target_rashi = RASHIS[(start_idx + (off - 1)) % 12]
            rashi_bindus[target_rashi] += 1
            p_total += 1
        per_planet_counts[planet] = p_total
    r_map = RASHI_LABELS.get(lang, RASHI_LABELS['kn'])
    rows = [{'rashi_key': r, 'rashi_disp': r_map.get(r, r), 'bindus': rashi_bindus[r]} for r in RASHIS]
    sav_total = sum(rashi_bindus.values())
    best_row = max(rows, key=lambda x: x['bindus'])
    return {
        'rows': rows,
        'sav_total': sav_total,
        'best_rashi': f"{best_row['rashi_disp']} ({best_row['bindus']})",
        'per_planet_counts': per_planet_counts
    }

def build_marriage_matching(p1_name, p1_b_no, p1_d_no, p1_kua, p1_lagna, p1_rashi, p1_nak, p1_time, p1_place,
                            p2_name, p2_b_no, p2_d_no, p2_kua, p2_lagna, p2_rashi, p2_nak, lang='kn'):
    score = 0
    max_score = 100
    rel_b = get_relation(p1_b_no, p2_b_no, lang)
    score += 30 if 'Friend' in rel_b else (18 if 'Neutral' in rel_b else 8)

    if p1_d_no and p2_d_no:
        rel_d = get_relation(p1_d_no, p2_d_no, lang)
        score += 25 if 'Friend' in rel_d else (15 if 'Neutral' in rel_d else 7)
    else:
        rel_d = "-"

    if p1_kua and p2_kua:
        rel_k = get_relation(p1_kua, p2_kua, lang)
        score += 15 if 'Friend' in rel_k else (10 if 'Neutral' in rel_k else 5)
    else:
        rel_k = "-"

    r1_idx = RASHIS.index(p1_rashi) if p1_rashi in RASHIS else 0
    r2_idx = RASHIS.index(p2_rashi) if p2_rashi in RASHIS else 0
    r_diff = abs(r1_idx - r2_idx)
    if r_diff in {0, 4, 8}:
        score += 15
        rashi_note_type = 'good'
    elif r_diff in {2, 10, 3, 9, 6}:
        score += 10
        rashi_note_type = 'mid'
    else:
        score += 6
        rashi_note_type = 'caution'

    n1_idx = NAKSHATRAS.index(p1_nak) if p1_nak in NAKSHATRAS else 0
    n2_idx = NAKSHATRAS.index(p2_nak) if p2_nak in NAKSHATRAS else 0
    n_count = ((n2_idx - n1_idx) % 27) + 1
    n_tara = ((n_count - 1) % 9) + 1
    score += 15 if n_tara in {2, 4, 6, 8, 9} else (9 if n_tara == 1 else 5)

    r_map = RASHI_LABELS.get(lang, RASHI_LABELS['kn'])
    n_map = NAKSHATRA_LABELS.get(lang, NAKSHATRA_LABELS['kn'])
    return {
        'score': min(score, max_score), 'max_score': max_score,
        'p1_name': p1_name, 'p2_name': p2_name,
        'p1_b_no': p1_b_no, 'p2_b_no': p2_b_no,
        'rel_birth': rel_b, 'rel_destiny': rel_d, 'rel_kua': rel_k,
        'p1_lagna_disp': r_map.get(p1_lagna, p1_lagna), 'p2_lagna_disp': r_map.get(p2_lagna, p2_lagna),
        'p1_rashi_disp': r_map.get(p1_rashi, p1_rashi), 'p2_rashi_disp': r_map.get(p2_rashi, p2_rashi),
        'p1_nak_disp': n_map.get(p1_nak, p1_nak), 'p2_nak_disp': n_map.get(p2_nak, p2_nak),
        'nak_tara_num': n_tara, 'p1_time': p1_time, 'p1_place': p1_place,
        'rashi_note_type': rashi_note_type
    }

def get_name_correction_advice(chaldean_total, lang='kn'):
    auspicious_targets = [15, 24, 33, 42, 51, 19, 37, 46, 14, 23, 32, 41, 50, 59]
    diffs = [(t, t - chaldean_total) for t in auspicious_targets if t > chaldean_total]
    if not diffs:
        msg_no_up = {
            'kn': f'ಪ್ರಸ್ತುತ ಮೊತ್ತ {chaldean_total} ಆಗಿದೆ. ಹೆಸರಿನಲ್ಲಿ ಸ್ವಲ್ಪ ಬದಲಾವಣೆ ಮಾಡಿ ಶುಭ ಸಂಖ್ಯೆಗೆ ತರಬಹುದು.',
            'en': f'Current total is {chaldean_total}. Minor spelling adjustment can align it with an auspicious number.',
            'ta': f'தற்போதைய கூட்டுத்தொகை {chaldean_total}. பெயரில் சிறிய மாற்றம் செய்து சுப எண்ணுக்குக் கொண்டு வரலாம்.',
            'te': f'ప్రస్తుత మొత్తం {chaldean_total}. పేరులో చిన్న మార్పు చేసి శుభ సంఖ్యకు తీసుకురావచ్చు.',
            'hi': f'वर्तमान योग {chaldean_total} है। नाम में थोड़ा बदलाव कर शुभ अंक पर लाया जा सकता है।'
        }
        return msg_no_up.get(lang, msg_no_up['kn'])
    best_target, needed = min(diffs, key=lambda x: x[1])
    msg_up = {
        'kn': f'ಪ್ರಸ್ತುತ ಚಾಲ್ಡಿಯನ್ ಮೊತ್ತ: {chaldean_total}. ಇದನ್ನು ಶುಭ ಸಂಖ್ಯಾ ಯೋಗಕ್ಕೆ ({best_target}) ತರಲು +{needed} ಮೌಲ್ಯದ ಅಕ್ಷರವನ್ನು ಸೇರಿಸುವುದು ಉತ್ತಮ.',
        'en': f'Current Chaldean total: {chaldean_total}. Adding +{needed} value can move it toward auspicious target ({best_target}).',
        'ta': f'தற்போதைய கால்டியன் கூட்டுத்தொகை: {chaldean_total}. சுப இலக்கிற்கு ({best_target}) கொண்டு வர +{needed} மதிப்பு சேர்க்கலாம்.',
        'te': f'ప్రస్తుత చాల్డియన్ మొత్తం: {chaldean_total}. శుభ సంఖ్యకు ({best_target}) తీసుకురావడానికి +{needed} విలువ జోడించవచ్చు.',
        'hi': f'वर्तमान चाल्डियन योग: {chaldean_total}। शुभ अंक ({best_target}) के लिए +{needed} मान जोड़ना अनुकूल रहेगा।'
    }
    return msg_up.get(lang, msg_up['kn'])

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
    req_lang = request.values.get('lang')
    if req_lang:
        session['lang'] = normalize_lang(req_lang)
    lang = normalize_lang(session.get('lang', 'kn'))
    ui = UI_TEXT.get(lang, UI_TEXT['kn'])

    vedic_grid = [[3, 1, 9], [6, 7, 5], [2, 8, 4]]
    loshu_grid = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
    formatted_grid = {num: '' for num in range(1, 10)}
    formatted_loshu_grid = {num: '' for num in range(1, 10)}
    missing_numbers = []
    present_numbers = set()
    grid_yogas = []
    loshu_yogas = []
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

    p1_time = ''
    p1_place = ''
    p1_lagna = 'Kanya'
    p1_rashi = 'Mesha'
    p1_nak = 'Bharani'
    transit_nak = 'Ashwini'

    p2_name = ''
    p2_dob = ''
    p2_birth_no = 0
    p2_destiny_no = 0
    p2_kua = 0
    p2_lagna = ''
    p2_rashi = ''
    p2_nak = ''
    partner_compatibility = ''
    marriage_match_data = None
    tarabala_data = None
    ashtakavargha_data = None

    planet_positions = {
        'Sun': 'Simha', 'Moon': 'Mesha', 'Mars': 'Makara',
        'Mercury': 'Kanya', 'Jupiter': 'Vrishabha', 'Venus': 'Karka', 'Saturn': 'Vrishchika'
    }

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

    py_map = PERSONAL_YEAR_LANG.get(lang, PERSONAL_YEAR_LANG['kn'])
    props_map = NUMBER_PROPS_LANG.get(lang, NUMBER_PROPS_LANG['kn'])
    remedies_map = MISSING_REMEDIES_LANG.get(lang, MISSING_REMEDIES_LANG['kn'])

    if request.method == 'POST':
        dob = request.form.get('dob', '').strip()
        analysed_name = request.form.get('analysed_name', '').strip()
        input_mobile = request.form.get('input_mobile', '').strip()
        p1_time = request.form.get('p1_time', '').strip()
        p1_place = request.form.get('p1_place', '').strip()
        p1_lagna = request.form.get('p1_lagna', 'Kanya').strip()
        p1_rashi = request.form.get('p1_rashi', 'Mesha').strip()
        p1_nak = request.form.get('p1_nak', 'Bharani').strip()
        transit_nak = request.form.get('transit_nak', 'Ashwini').strip()

        p2_name = request.form.get('p2_name', '').strip()
        p2_dob = request.form.get('p2_dob', '').strip()
        p2_lagna = request.form.get('p2_lagna', '').strip()
        p2_rashi = request.form.get('p2_rashi', '').strip()
        p2_nak = request.form.get('p2_nak', '').strip()

        for pl in planet_positions:
            planet_positions[pl] = request.form.get(f'pos_{pl}', planet_positions[pl]).strip()

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
                p_year_desc = py_map.get(p_year_val, '')

                curr_mth_sum = reduce_to_single(current_month)
                p_month_val = reduce_to_single(p_year_val + curr_mth_sum)
                p_month_desc = py_map.get(p_month_val, '')

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
                    cell_val = str(num) * counts[num]
                    formatted_grid[num] = cell_val
                    formatted_loshu_grid[num] = cell_val
                else:
                    formatted_grid[num] = '-'
                    formatted_loshu_grid[num] = '-'
                    missing_numbers.append(num)

            astrology_props = props_map.get(birth_no, props_map[1])
            kua_number = calculate_kua(birth_year)
            dob_pyramid_data = calculate_dob_pyramid(dob)
            grid_yogas = analyze_vedic_grid_yogas(present_numbers, lang)
            loshu_yogas = analyze_loshu_grid_yogas(present_numbers, lang)
            tarabala_data = calculate_tarabala_and_madabhuda(p1_nak, transit_nak, lang)
            ashtakavargha_data = calculate_ashtakavargha(planet_positions, lang)

            for m in missing_numbers:
                missing_remedies_list.append({'num': m, 'remedy': remedies_map.get(m, '')})

            total_deg = sum(BIRTH_DEGREES.get(d, 0) for d in grid_numbers)
            total_serial_no = len(grid_numbers)
            birth_strength_avg = round(total_deg / total_serial_no, 2) if total_serial_no > 0 else 0.0

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
                    c_parts.append(f'{ch}({val})')
            chaldean_total = c_sum
            chaldean_root = reduce_to_single(c_sum)
            chaldean_breakdown = ' + '.join(c_parts)
            name_advice = get_name_correction_advice(chaldean_total, lang)
            pyramid_data = calculate_pyramid(analysed_name)

            p_sum = 0
            p_parts = []
            for ch in upper_name:
                if ch in PYTHAGOREAN_MAP:
                    val = PYTHAGOREAN_MAP[ch]
                    p_sum += val
                    p_parts.append(f'{ch}({val})')
            pythagorean_total = p_sum
            pythagorean_root = reduce_to_single(p_sum)
            pythagorean_breakdown = ' + '.join(p_parts)

            name_sound_freq = sum(NAME_FREQ_MAP.get(ch, 0) for ch in upper_name)
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

        # Partner / Spouse Details: ನೀವೇ p2_dob ಹಾಕಿದಾಗ ಮಾತ್ರ ಲೆಕ್ಕಾಚಾರವಾಗುತ್ತದೆ; ಇಲ್ಲದಿದ್ದರೆ ಖಾಲಿಯಾಗಿರುತ್ತದೆ
        if p2_dob:
            p2_clean = [int(ch) for ch in p2_dob if ch.isdigit()]
            if len(p2_clean) >= 8:
                p2_day_val = p2_clean[0]*10 + p2_clean[1]
                p2_birth_no = reduce_to_single(p2_clean[0]) if p2_day_val > 31 else reduce_to_single(p2_day_val)
                p2_destiny_no = reduce_to_single(sum(p2_clean))
                p2_yr = p2_clean[4]*1000 + p2_clean[5]*100 + p2_clean[6]*10 + p2_clean[7]
                p2_kua = calculate_kua(p2_yr)
                rel_check = get_relation(birth_no, p2_birth_no, lang)
                partner_templates = {
                    'kn': f'ವ್ಯಕ್ತಿ 1 ರ ಮೂಲ ಸಂಖ್ಯೆ ({birth_no}) ಮತ್ತು ಪಾಲುದಾರರ ಮೂಲ ಸಂಖ್ಯೆ ({p2_birth_no}) ನಡುವಿನ ಹೊಂದಾಣಿಕೆ: {rel_check}',
                    'en': f'Compatibility between Person 1 Birth No ({birth_no}) and Partner Birth No ({p2_birth_no}): {rel_check}',
                    'ta': f'நபர் 1 மூல எண் ({birth_no}) மற்றும் துணைவர் மூல எண் ({p2_birth_no}) பொருத்தம்: {rel_check}',
                    'te': f'వ్యక్తి 1 మూల సంఖ్య ({birth_no}) మరియు భాగస్వామి మూల సంఖ్య ({p2_birth_no}) అనుకూలత: {rel_check}',
                    'hi': f'व्यक्ति 1 मूलांक ({birth_no}) और पार्टनर मूलांक ({p2_birth_no}) के बीच अनुकूलता: {rel_check}'
                }
                partner_compatibility = partner_templates.get(lang, partner_templates['kn'])
                marriage_match_data = build_marriage_matching(
                    analysed_name, birth_no, destiny_no, kua_number, p1_lagna, p1_rashi, p1_nak, p1_time, p1_place,
                    p2_name if p2_name else ui['spouse_default'], p2_birth_no, p2_destiny_no, p2_kua, p2_lagna, p2_rashi, p2_nak, lang
                )
        else:
            p2_birth_no = 0
            p2_destiny_no = 0
            p2_kua = 0
            partner_compatibility = ''
            marriage_match_data = None

        if dob and analysed_name:
            compat = {
                'c_birth': get_relation(chaldean_root, birth_no, lang),
                'c_destiny': get_relation(chaldean_root, destiny_no, lang),
                'c_year': get_relation(chaldean_root, year_no, lang),
                'p_birth': get_relation(pythagorean_root, birth_no, lang),
                'p_destiny': get_relation(pythagorean_root, destiny_no, lang),
                'p_year': get_relation(pythagorean_root, year_no, lang),
            }
            b_friends = set(RELATIONS.get(birth_no, {}).get('friends', []))
            d_friends = set(RELATIONS.get(destiny_no, {}).get('friends', []))
            common_lucky = sorted(list(b_friends.intersection(d_friends)))
            lucky_details = {
                'birth_friends': ', '.join(map(str, sorted(list(b_friends)))),
                'destiny_friends': ', '.join(map(str, sorted(list(d_friends)))),
                'common': ', '.join(map(str, common_lucky)) if common_lucky else '1, 5, 6'
            }

        if input_mobile:
            mobile_data = analyze_mobile_advanced(input_mobile)
            mobile_pyramid_data = calculate_mobile_pyramid(input_mobile)

    rashi_options = [(r, RASHI_LABELS.get(lang, RASHI_LABELS['kn']).get(r, r)) for r in RASHIS]
    nak_options = [(n, NAKSHATRA_LABELS.get(lang, NAKSHATRA_LABELS['kn']).get(n, n)) for n in NAKSHATRAS]

    return render_template(
        'calculator.html',
        lang=lang, ui=ui, user_name=user_name,
        vedic_grid=vedic_grid, loshu_grid=loshu_grid,
        formatted_grid=formatted_grid, formatted_loshu_grid=formatted_loshu_grid,
        missing_numbers=missing_numbers, grid_yogas=grid_yogas, loshu_yogas=loshu_yogas,
        dob=dob, birth_no=birth_no, destiny_no=destiny_no, destiny_total=destiny_total,
        year_no=year_no, year_total=year_total, analysed_name=analysed_name,
        chaldean_total=chaldean_total, chaldean_root=chaldean_root, chaldean_breakdown=chaldean_breakdown,
        pythagorean_total=pythagorean_total, pythagorean_root=pythagorean_root, pythagorean_breakdown=pythagorean_breakdown,
        name_advice=name_advice, pyramid_data=pyramid_data, dob_pyramid_data=dob_pyramid_data, mobile_pyramid_data=mobile_pyramid_data,
        compat=compat, lucky_details=lucky_details, astrology_props=astrology_props, missing_remedies_list=missing_remedies_list,
        kua_number=kua_number, input_mobile=input_mobile, mobile_data=mobile_data,
        p_year_val=p_year_val, p_year_desc=p_year_desc, p_month_val=p_month_val, p_month_desc=p_month_desc, current_year=current_year,
        p1_time=p1_time, p1_place=p1_place, p1_lagna=p1_lagna, p1_rashi=p1_rashi, p1_nak=p1_nak, transit_nak=transit_nak,
        p2_name=p2_name, p2_dob=p2_dob, p2_birth_no=p2_birth_no, p2_lagna=p2_lagna, p2_rashi=p2_rashi, p2_nak=p2_nak,
        partner_compatibility=partner_compatibility, marriage_match_data=marriage_match_data,
        tarabala_data=tarabala_data, ashtakavargha_data=ashtakavargha_data, planet_positions=planet_positions,
        rashi_options=rashi_options, nak_options=nak_options,
        birth_strength_avg=birth_strength_avg, birth_lifestyle=birth_lifestyle, name_sound_freq=name_sound_freq, name_lifestyle=name_lifestyle
    )

if __name__ == '__main__':
    app.run(debug=True)
