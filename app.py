from flask import Flask, request, render_template_string
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'lucky_star_secret_key'

CHALDEAN_MAP = {
    'A': 1, 'I': 1, 'J': 1, 'Q': 1, 'Y': 1,
    'B': 2, 'K': 2, 'R': 2,
    'C': 3, 'G': 3, 'L': 3, 'S': 3,
    'D': 4, 'M': 4, 'T': 4,
    'E': 5, 'H': 5, 'N': 5, 'X': 5,
    'U': 6, 'V': 6, 'W': 6,
    'O': 7, 'Z': 7,
    'F': 8, 'P': 8
}

PYTHAGOREAN_MAP = {
    'A': 1, 'J': 1, 'S': 1,
    'B': 2, 'K': 2, 'T': 2,
    'C': 3, 'L': 3, 'U': 3,
    'D': 4, 'M': 4, 'V': 4,
    'E': 5, 'N': 5, 'W': 5,
    'F': 6, 'O': 6, 'X': 6,
    'G': 7, 'P': 7, 'Y': 7,
    'H': 8, 'Q': 8, 'Z': 8,
    'I': 9, 'R': 9
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

UI_TEXT = {
    'kn': {
        'title': 'ಲಕ್ಕಿ ಸ್ಟಾರ್ ಆಸ್ಟ್ರೋ — ಸಂಖ್ಯಾಶಾಸ್ತ್ರ ವರದಿ',
        'subtitle': 'ವೈಯಕ್ತಿಕ ಸಂಖ್ಯಾಶಾಸ್ತ್ರ, ವೇದಿಕ್ ಗ್ರಿಡ್, ಪಿರಮಿಡ್ ಮತ್ತು ಹೊಂದಾಣಿಕೆ ವಿಶ್ಲೇಷಣೆ',
        'lang_label': 'ಭಾಷೆ (Language)',
        'name': 'ಹೆಸರು (Name)',
        'dob': 'ಜನ್ಮ ದಿನಾಂಕ (DOB)',
        'mobile': 'ಮೊಬೈಲ್ ಸಂಖ್ಯೆ (Mobile)',
        'p2_name': 'ಪಾಲುದಾರರ ಹೆಸರು (Partner Name)',
        'p2_dob': 'ಪಾಲುದಾರರ DOB',
        'calc_btn': 'ವರದಿ ಸಿದ್ಧಪಡಿಸಿ',
        'print_btn': 'Print / Save PDF',
        'strength_title': 'ಜನ್ಮ ಮತ್ತು ಹೆಸರಿನ ಬಲ ವಿಶ್ಲೇಷಣೆ',
        's1_title': '1. ಜನ್ಮ ದಿನಾಂಕ ಮತ್ತು ವೇದಿಕ್ ಗ್ರಿಡ್ (DOB & Vedic Grid)',
        's2_title': '2. ವೇದಿಕ್ ಗ್ರಿಡ್ ಯೋಗಗಳು (Vedic Grid Yogas)',
        's3_title': '3. ಪಿರಮಿಡ್ ಸಂಖ್ಯಾ ವಿಶ್ಲೇಷಣೆ (Name, DOB & Mobile Pyramid Analysis)',
        's4_title': '4. ವಿವಾಹ ಅಥವಾ ವ್ಯವಹಾರ ಪಾಲುದಾರಿಕೆ ಹೊಂದಾಣಿಕೆ',
        's5_title': '5. ಪರ್ಸನಲ್ ಇಯರ್ ಮತ್ತು ಪರ್ಸನಲ್ ಮಂತ್ ಫಲ',
        's6_title': '6. ಅದೃಷ್ಟ ಬಣ್ಣ, ದಿಕ್ಕು, ರತ್ನ, ಕುವಾ ಸಂಖ್ಯೆ ಮತ್ತು ವೃತ್ತಿ',
        's7_title': '7. ಕೊರತೆಯಿರುವ ಸಂಖ್ಯೆಗಳು ಮತ್ತು ಪರಿಹಾರಗಳು',
        's8_title': '8. ಹೆಸರಿನ ವಿಶ್ಲೇಷಣೆ ಮತ್ತು ತಿದ್ದುಪಡಿ ಸಲಹೆ',
        's9_title': '9. ಹೆಸರು ಮತ್ತು ಜನ್ಮ ಸಂಖ್ಯೆಗಳ ಹೊಂದಾಣಿಕೆ',
        's10_title': '10. ಸಾಮಾನ್ಯ ಅದೃಷ್ಟ ಸಂಖ್ಯೆಗಳು (Common Lucky Numbers)',
        'friend': 'ಮಿತ್ರ / ಸ್ನೇಹ (ಅತ್ಯುತ್ತಮ ಹೊಂದಾಣಿಕೆ)',
        'enemy': 'ಶತ್ರು (ಎಚ್ಚರಿಕೆ ಅಗತ್ಯ)',
        'neutral': 'ಸಮ (ಸಾಮಾನ್ಯ ಹೊಂದಾಣಿಕೆ)',
        'auspicious': 'ಶುಭ (Good)',
        'bad': 'ಅಶುಭ (Bad)',
        'no_yoga': 'ಯಾವುದೇ ವಿಶೇಷ ಯೋಗ ಪತ್ತೆಯಾಗಿಲ್ಲ ಅಥವಾ DOB ನಮೂದಿಸಿಲ್ಲ.',
    },
    'en': {
        'title': 'Lucky Star Astro — Numerology Report',
        'subtitle': 'Birth & Name Strength, Vedic Grid, Pyramids & Compatibility Analysis',
        'lang_label': 'Language',
        'name': 'Full Name',
        'dob': 'Date of Birth (DOB)',
        'mobile': 'Mobile Number',
        'p2_name': 'Partner Name',
        'p2_dob': 'Partner DOB',
        'calc_btn': 'Calculate Report',
        'print_btn': 'Print / Save PDF',
        'strength_title': 'Birth & Name Strength Analysis',
        's1_title': '1. Date of Birth and Vedic Grid (DOB & Vedic Grid)',
        's2_title': '2. Vedic Grid Yogas',
        's3_title': '3. Pyramid Number Analysis (Name, DOB & Mobile Pyramid Analysis)',
        's4_title': '4. Marital or Business Partnership Matching',
        's5_title': '5. Personal Year & Month Predictions',
        's6_title': '6. Lucky Color, Direction, Gemstone, Kua Number & Profession',
        's7_title': '7. Missing Numbers and Remedies',
        's8_title': '8. Name Analysis & Correction Tool',
        's9_title': '9. Name vs DOB Compatibility',
        's10_title': '10. Common Lucky Numbers',
        'friend': 'Friend (Best Compatibility)',
        'enemy': 'Enemy (Caution Advised)',
        'neutral': 'Neutral (Normal Compatibility)',
        'auspicious': 'auspicious',
        'bad': 'bad',
        'no_yoga': 'No special yoga detected or DOB not entered yet.',
    },
    'te': {
        'title': 'లక్కీ స్టార్ ఆస్ట్రో — సంఖ్యాశాస్త్ర నివేదిక',
        'subtitle': 'పుట్టిన తేదీ, పేరు బలం, వేదిక్ గ్రిడ్, పిరమిడ్ మరియు అనుకూలత విశ్లేషణ',
        'lang_label': 'భాష (Language)',
        'name': 'పూర్తి పేరు (Name)',
        'dob': 'పుట్టిన తేదీ (DOB)',
        'mobile': 'మొబైల్ నంబర్ (Mobile)',
        'p2_name': 'భాగస్వామి పేరు (Partner Name)',
        'p2_dob': 'భాగస్వామి DOB',
        'calc_btn': 'నివేదిక రూపొందించండి',
        'print_btn': 'Print / Save PDF',
        'strength_title': 'పుట్టిన తేదీ మరియు పేరు బల విశ్లేషణ',
        's1_title': '1. పుట్టిన తేదీ మరియు వేదిక్ గ్రిడ్ (DOB & Vedic Grid)',
        's2_title': '2. వేదిక్ గ్రిడ్ యోగాలు (Vedic Grid Yogas)',
        's3_title': '3. పిరమిడ్ సంఖ్యా విశ్లేషణ (Name, DOB & Mobile Pyramid Analysis)',
        's4_title': '4. వివాహ లేదా వ్యాపార భాగస్వామ్య సరిపోలిక',
        's5_title': '5. పర్సనల్ ఇయర్ మరియు మంత్ ఫలితాలు',
        's6_title': '6. అదృష్ట రంగు, దిశ, రత్నం, కువా నంబర్ మరియు వృత్తి',
        's7_title': '7. లోపించిన సంఖ్యలు మరియు పరిహారాలు',
        's8_title': '8. పేరు విశ్లేషణ మరియు సవరణ సూచన',
        's9_title': '9. పేరు మరియు పుట్టిన సంఖ్యల అనుకూలత',
        's10_title': '10. ఉమ్మడి అదృష్ట సంఖ్యలు (Common Lucky Numbers)',
        'friend': 'మిత్రుడు (ఉత్తమ అనుకూలత)',
        'enemy': 'శత్రువు (జాగ్రత్త అవసరం)',
        'neutral': 'సమం (సాధారణ అనుకూలత)',
        'auspicious': 'శుభం (Good)',
        'bad': 'అశుభం (Bad)',
        'no_yoga': 'ప్రత్యేక యోగం లేదు లేదా DOB నమోదు చేయలేదు.',
    },
    'hi': {
        'title': 'लकी स्टार एस्ट्रो — अंकशास्त्र रिपोर्ट',
        'subtitle': 'जन्म तिथि, नाम शक्ति, वैदिक ग्रिड, पिरामिड और अनुकूलता विश्लेषण',
        'lang_label': 'भाषा (Language)',
        'name': 'पूरा नाम (Name)',
        'dob': 'जन्म तिथि (DOB)',
        'mobile': 'मोबाइल नंबर (Mobile)',
        'p2_name': 'पार्टनर का नाम (Partner Name)',
        'p2_dob': 'पार्टनर की DOB',
        'calc_btn': 'रिपोर्ट तैयार करें',
        'print_btn': 'Print / Save PDF',
        'strength_title': 'जन्म और नाम शक्ति विश्लेषण',
        's1_title': '1. जन्म तिथि और वैदिक ग्रिड (DOB & Vedic Grid)',
        's2_title': '2. वैदिक ग्रिड योग (Vedic Grid Yogas)',
        's3_title': '3. पिरामिड अंक विश्लेषण (Name, DOB & Mobile Pyramid Analysis)',
        's4_title': '4. विवाह या व्यवसाय साझेदारी मिलान',
        's5_title': '5. पर्सनल ईयर और पर्सनल मंथ भविष्यफल',
        's6_title': '6. शुभ रंग, दिशा, रत्न, कुआ नंबर और पेशा',
        's7_title': '7. अनुपस्थित अंक और उपाय',
        's8_title': '8. नाम विश्लेषण और सुधार सुझाव',
        's9_title': '9. नाम बनाम जन्म अंक अनुकूलता',
        's10_title': '10. सामान्य शुभ अंक (Common Lucky Numbers)',
        'friend': 'मित्र (सर्वोत्तम अनुकूलता)',
        'enemy': 'शत्रु (सावधानी आवश्यक)',
        'neutral': 'सम (सामान्य अनुकूलता)',
        'auspicious': 'शुभ (Good)',
        'bad': 'अशुभ (Bad)',
        'no_yoga': 'कोई विशेष योग नहीं मिला या DOB दर्ज नहीं की गई है।',
    },
    'ta': {
        'title': 'லக்கி ஸ்டார் ஆஸ்ட்ரோ — எண் கணித அறிக்கை',
        'subtitle': 'பிறந்த தேதி, பெயர் வலிமை, வேதிக் கிரிட், பிரமிடு மற்றும் பொருத்தம்',
        'lang_label': 'மொழி (Language)',
        'name': 'முழுப் பெயர் (Name)',
        'dob': 'பிறந்த தேதி (DOB)',
        'mobile': 'மொபைல் எண் (Mobile)',
        'p2_name': 'துணைவர் பெயர் (Partner Name)',
        'p2_dob': 'துணைவர் DOB',
        'calc_btn': 'அறிக்கை உருவாக்கு',
        'print_btn': 'Print / Save PDF',
        'strength_title': 'பிறப்பு மற்றும் பெயர் வலிமை பகுப்பாய்வு',
        's1_title': '1. பிறந்த தேதி மற்றும் வேதிக் கிரிட் (DOB & Vedic Grid)',
        's2_title': '2. வேதிக் கிரிட் யோகங்கள் (Vedic Grid Yogas)',
        's3_title': '3. பிரமிடு எண் பகுப்பாய்வு (Name, DOB & Mobile Pyramid Analysis)',
        's4_title': '4. திருமண அல்லது வணிக கூட்டாண்மை பொருத்தம்',
        's5_title': '5. தனிப்பட்ட ஆண்டு மற்றும் மாத பலன்கள்',
        's6_title': '6. அதிர்ஷ்ட நிறம், திசை, ரத்தினம், குவா எண் மற்றும் தொழில்',
        's7_title': '7. விடுபட்ட எண்கள் மற்றும் பரிகாரங்கள்',
        's8_title': '8. பெயர் பகுப்பாய்வு மற்றும் திருத்த ஆலோசனை',
        's9_title': '9. பெயர் மற்றும் பிறப்பு எண்கள் பொருத்தம்',
        's10_title': '10. பொதுவான அதிர்ஷ்ட எண்கள் (Common Lucky Numbers)',
        'friend': 'நட்பு (சிறந்த பொருத்தம்)',
        'enemy': 'பகை (கவனம் தேவை)',
        'neutral': 'சமம் (சாதாரண பொருத்தம்)',
        'auspicious': 'சுபம் (Good)',
        'bad': 'அசுபம் (Bad)',
        'no_yoga': 'சிறப்பு யோகம் இல்லை அல்லது DOB உள்ளிடப்படவில்லை.',
    }
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
        2: {'colors': 'White, Green, Silver', 'direction': 'Northwest', 'gemstone': 'Pearl / Moonstone', 'profession': 'Arts, Travel, Liquids & Hospitality', 'lucky_days': 'Monday, Wednesday'},
        3: {'colors': 'Yellow, Pink, Purple', 'direction': 'Northeast', 'gemstone': 'Yellow Sapphire', 'profession': 'Education, Teaching, Advisory', 'lucky_days': 'Thursday, Tuesday'},
        4: {'colors': 'Grey, Blue, Earthy', 'direction': 'Southwest', 'gemstone': 'Hessonite / Blue Sapphire', 'profession': 'Technology, Software, Engineering', 'lucky_days': 'Wednesday, Saturday'},
        5: {'colors': 'Green, Light Shades', 'direction': 'North', 'gemstone': 'Emerald', 'profession': 'Business, Marketing, Share Market', 'lucky_days': 'Wednesday, Friday'},
        6: {'colors': 'White, Light Blue, Pink', 'direction': 'Southeast', 'gemstone': 'Opal / Diamond', 'profession': 'Cosmetics, Fashion, Media & Cinema', 'lucky_days': 'Friday, Wednesday'},
        7: {'colors': 'Smoky Grey, White, Green', 'direction': 'Northeast / Northwest', 'gemstone': 'Cat’s Eye', 'profession': 'Spirituality, Research, Astrology', 'lucky_days': 'Monday, Thursday'},
        8: {'colors': 'Black, Dark Blue, Charcoal', 'direction': 'West', 'gemstone': 'Blue Sapphire', 'profession': 'Medical, Healthcare, Steel & Heavy Industry', 'lucky_days': 'Saturday, Wednesday'},
        9: {'colors': 'Red, Pink, Maroon', 'direction': 'South', 'gemstone': 'Red Coral', 'profession': 'Defence, Police, Army, Real Estate', 'lucky_days': 'Tuesday, Sunday'}
    },
    'te': {
        1: {'colors': 'పసుపు, నారింజ, బంగారు', 'direction': 'తూర్పు', 'gemstone': 'కెంపు (Ruby)', 'profession': 'ప్రభుత్వ ఉద్యోగం, రాజకీయాలు, నాయకత్వం', 'lucky_days': 'ఆదివారం, గురువారం'},
        2: {'colors': 'తెలుపు, ఆకుపచ్చ, వెండి', 'direction': 'వాయువ్యం', 'gemstone': 'ముత్యం (Pearl)', 'profession': 'కళలు, ప్రయాణాలు, ద్రవ వ్యాపారం', 'lucky_days': 'సోమవారం, బుధవారం'},
        3: {'colors': 'పసుపు, గులాబీ, ఊదా', 'direction': 'ఈశాన్యం', 'gemstone': 'కనకపుష్యరాగం', 'profession': 'విద్య, బోధన, కన్సల్టింగ్', 'lucky_days': 'గురువారం, మంగళవారం'},
        4: {'colors': 'బూడిద, నీలం, మట్టి రంగులు', 'direction': 'నైరుతి', 'gemstone': 'గోమేధికం / నీలం', 'profession': 'టెక్నాలజీ, సాఫ్ట్‌వేర్, ఇంజనీరింగ్', 'lucky_days': 'బుధవారం, శనివారం'},
        5: {'colors': 'ఆకుపచ్చ, లేత రంగులు', 'direction': 'ఉత్తరం', 'gemstone': 'పచ్చ (Emerald)', 'profession': 'వ్యాపారం, మార్కెటింగ్, స్టాక్ మార్కెట్', 'lucky_days': 'బుధవారం, శుక్రవారం'},
        6: {'colors': 'తెలుపు, లేత నీలం, గులాబీ', 'direction': 'ఆగ్నేయం', 'gemstone': 'వజ్రం / ఓపల్', 'profession': 'ఫ్యాషన్, సౌందర్య సాధనాలు, సినిమా', 'lucky_days': 'శుక్రవారం, బుధవారం'},
        7: {'colors': 'స్మోకీ గ్రే, తెలుపు, ఆకుపచ్చ', 'direction': 'ఈశాన్యం / వాయువ్యం', 'gemstone': 'వైఢూర్యం (Cat’s Eye)', 'profession': 'ఆధ్యాత్మికత, పరిశోధన, జ్యోతిష్యం', 'lucky_days': 'సోమవారం, గురువారం'},
        8: {'colors': 'నలుపు, ముదురు నీలం, బూడిద', 'direction': 'పడమర', 'gemstone': 'నీలం (Blue Sapphire)', 'profession': 'వైద్యం, నర్సింగ్, స్టీల్ / ఇండస్ట్రీ', 'lucky_days': 'శనివారం, బుధవారం'},
        9: {'colors': 'ఎరుపు, గులాబీ, మెరూన్', 'direction': 'దక్షిణం', 'gemstone': 'పగడం (Red Coral)', 'profession': 'రక్షణ, పోలీస్, సైన్యం, రియల్ ఎస్టేట్', 'lucky_days': 'మంగళవారం, ఆదివారం'}
    },
    'hi': {
        1: {'colors': 'पीला, नारंगी, सुनहरा', 'direction': 'पूर्व', 'gemstone': 'माणिक्य (Ruby)', 'profession': 'सरकारी नौकरी, राजनीति, नेतृत्व', 'lucky_days': 'रविवार, गुरुवार'},
        2: {'colors': 'सफेद, हरा, चांदी जैसा', 'direction': 'उत्तर-पश्चिम', 'gemstone': 'मोती (Pearl)', 'profession': 'कला, यात्रा, तरल पदार्थ एवं सेवाएं', 'lucky_days': 'सोमवार, बुधवार'},
        3: {'colors': 'पीला, गुलाबी, बैंगनी', 'direction': 'ईशान (उत्तर-पूर्व)', 'gemstone': 'पुखराज (Yellow Sapphire)', 'profession': 'शिक्षा, शिक्षण, परामर्श', 'lucky_days': 'गुरुवार, मंगलवार'},
        4: {'colors': 'ग्रे, नीला, मिट्टी के रंग', 'direction': 'दक्षिण-पश्चिम', 'gemstone': 'गोमेद / नीलम', 'profession': 'तकनीक, सॉफ्टवेयर, इंजीनियरिंग', 'lucky_days': 'बुधवार, शनिवार'},
        5: {'colors': 'हरा, हल्के रंग', 'direction': 'उत्तर', 'gemstone': 'पन्ना (Emerald)', 'profession': 'व्यापार, मार्केटिंग, शेयर बाजार', 'lucky_days': 'बुधवार, शुक्रवार'},
        6: {'colors': 'सफेद, हल्का नीला, गुलाबी', 'direction': 'दक्षिण-पूर्व', 'gemstone': 'हीरा / ओपल', 'profession': 'फैशन, सौंदर्य, मीडिया एवं सिनेमा', 'lucky_days': 'शुक्रवार, बुधवार'},
        7: {'colors': 'स्मोकी ग्रे, सफेद, हरा', 'direction': 'ईशान / उत्तर-पश्चिम', 'gemstone': 'लहसुनिया (Cat’s Eye)', 'profession': 'आध्यात्म, शोध, ज्योतिष', 'lucky_days': 'सोमवार, गुरुवार'},
        8: {'colors': 'काला, गहरा नीला, स्लेटी', 'direction': 'पश्चिम', 'gemstone': 'नीलम (Blue Sapphire)', 'profession': 'चिकित्सा, स्वास्थ्य, स्टील एवं उद्योग', 'lucky_days': 'शनिवार, बुधवार'},
        9: {'colors': 'लाल, गुलाबी, मैरून', 'direction': 'दक्षिण', 'gemstone': 'मूंगा (Red Coral)', 'profession': 'रक्षा, पुलिस, सेना, रियल एस्टेट', 'lucky_days': 'मंगलवार, रविवार'}
    },
    'ta': {
        1: {'colors': 'மஞ்சள், ஆரஞ்சு, தங்கம்', 'direction': 'கிழக்கு', 'gemstone': 'மாணிக்கம் (Ruby)', 'profession': 'அரசுப் பணி, அரசியல், தலைமைத்துவம்', 'lucky_days': 'ஞாயிறு, வியாழன்'},
        2: {'colors': 'வெள்ளை, பச்சை, வெள்ளி', 'direction': 'வடமேற்கு', 'gemstone': 'முத்து (Pearl)', 'profession': 'கலை, பயணம், திரவத் துறைகள்', 'lucky_days': 'திங்கள், புதன்'},
        3: {'colors': 'மஞ்சள், இளஞ்சிவப்பு, ஊதா', 'direction': 'வடகிழக்கு', 'gemstone': 'கனகபுஷ்பராகம்', 'profession': 'கல்வி, கற்பித்தல், ஆலோசனை', 'lucky_days': 'வியாழன், செவ்வாய்'},
        4: {'colors': 'சாம்பல், நீலம், மண் நிறம்', 'direction': 'தென்மேற்கு', 'gemstone': 'கோமேதகம் / நீலம்', 'profession': 'தொழில்நுட்பம், மென்பொருள், பொறியியல்', 'lucky_days': 'புதன், சனி'},
        5: {'colors': 'பச்சை, வெளிர் நிறங்கள்', 'direction': 'வடக்கு', 'gemstone': 'மரகதம் (Emerald)', 'profession': 'வணிகம், சந்தைப்படுத்தல், பங்குச் சந்தை', 'lucky_days': 'புதன், வெள்ளி'},
        6: {'colors': 'வெள்ளை, வெளிர் நீலம், இளஞ்சிவப்பு', 'direction': 'தென்கிழக்கு', 'gemstone': 'வைரம் / ஓபல்', 'profession': 'பேஷன், அழகு சாதனங்கள், சினிமா', 'lucky_days': 'வெள்ளி, புதன்'},
        7: {'colors': 'சாம்பல், வெள்ளை, பச்சை', 'direction': 'வடகிழக்கு / வடமேற்கு', 'gemstone': 'வைடூரியம் (Cat’s Eye)', 'profession': 'ஆன்மீகம், ஆராய்ச்சி, ஜோதிடம்', 'lucky_days': 'திங்கள், வியாழன்'},
        8: {'colors': 'கருப்பு, அடர் நீலம், சாம்பல்', 'direction': 'மேற்கு', 'gemstone': 'நீலக்கல் (Blue Sapphire)', 'profession': 'மருத்துவம், சுகாதாரம், எஃகு & தொழில்', 'lucky_days': 'சனி, புதன்'},
        9: {'colors': 'சிவப்பு, இளஞ்சிவப்பு, மெரூன்', 'direction': 'தெற்கு', 'gemstone': 'பவளம் (Red Coral)', 'profession': 'பாதுகாப்பு, காவல், ராணுவம், ரியல் எஸ்டேட்', 'lucky_days': 'செவ்வாய், ஞாயிறு'}
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
        2: 'Use silver utensils and seek blessings from your mother to strengthen Moon energy.',
        3: 'Use yellow accents and respect elders and teachers to strengthen Jupiter energy.',
        4: 'Feed grains to birds and spend time in nature to balance Rahu energy.',
        5: 'Wear green and pray to Lord Ganesha to strengthen Mercury energy.',
        6: 'Maintain harmony, cleanliness, and beauty, and worship Goddess Mahalakshmi for Venus strength.',
        7: 'Pray to Lord Ganesha and help animals/strays to balance Ketu energy.',
        8: 'Donate food or serve the underprivileged and needy to balance Saturn energy.',
        9: 'Use warm red tones mindfully and practice yoga and regular exercise for Mars strength.'
    },
    'te': {
        1: 'సూర్య శక్తి పెరగడానికి ప్రతిరోజూ సూర్య నమస్కారం చేయండి మరియు రాగి పాత్రలో నీరు తాగండి.',
        2: 'చంద్ర బలం కోసం వెండి పాత్రలు వాడండి మరియు తల్లి ఆశీర్వాదం తీసుకోండి.',
        3: 'గురు బలం కోసం పసుపు రంగు వస్తువులు వాడండి మరియు పెద్దలను గౌరవించండి.',
        4: 'రాహు బలం కోసం పక్షులకు గింజలు వేయండి మరియు ప్రకృతితో సమయం గడపండి.',
        5: 'బుధ బలం కోసం ఆకుపచ్చ వస్త్రాలు ధరించండి మరియు గణపతిని పూజించండి.',
        6: 'శుక్ర బలం కోసం శుభ్రత, సౌందర్యానికి ప్రాధాన్యత ఇవ్వండి మరియు లక్ష్మీ పూజ చేయండి.',
        7: 'కేతు బలం కోసం గణేశ ప్రార్థన చేయండి మరియు మూగజీవాలకు సహాయం చేయండి.',
        8: 'శని బలం కోసం పేదలకు అన్నదానం లేదా సేవ చేయండి.',
        9: 'కుజ బలం కోసం యోగా, వ్యాయామం అలవాటు చేసుకోండి.'
    },
    'hi': {
        1: 'सूर्य की शक्ति बढ़ाने के लिए प्रतिदिन सूर्य नमस्कार करें और तांबे के पात्र से जल पिएं।',
        2: 'चंद्र बल के लिए चांदी का उपयोग करें और माता का आशीर्वाद लें।',
        3: 'गुरु बल के लिए पीले रंग का प्रयोग करें और बड़ों तथा गुरुओं का सम्मान करें।',
        4: 'राहु संतुलन के लिए पक्षियों को दाना डालें और प्रकृति के करीब रहें।',
        5: 'बुध बल के लिए हरे रंग के वस्त्र पहनें और भगवान गणेश की आराधना करें।',
        6: 'शुक्र बल के लिए स्वच्छता व सौंदर्य बनाए रखें और महालक्ष्मी की पूजा करें।',
        7: 'केतु संतुलन के लिए गणेश प्रार्थना करें और जीवों की सेवा करें।',
        8: 'शनि संतुलन के लिए जरूरतमंदों को अन्नदान या सेवा करें।',
        9: 'मंगल बल के लिए नियमित योग व व्यायाम करें।'
    },
    'ta': {
        1: 'சூரிய பலம் அதிகரிக்க தினமும் சூரிய நமஸ்காரம் செய்து செம்பு பாத்திரத்தில் நீர் அருந்துங்கள்.',
        2: 'சந்திர பலத்திற்கு வெள்ளிப் பாத்திரங்களைப் பயன்படுத்தி தாயின் ஆசி பெறுங்கள்.',
        3: 'குரு பலத்திற்கு மஞ்சள் நிறத்தை பயன்படுத்தி பெரியவர்களை மதிக்கவும்.',
        4: 'ராகு சமநிலைக்கு பறவைகளுக்கு தானியங்கள் இடுங்கள், இயற்கையோடு இருங்கள்.',
        5: 'புதன் பலத்திற்கு பச்சை நிற ஆடை அணிந்து விநாயகரை வழிபடுங்கள்.',
        6: 'சுக்கிர பலத்திற்கு தூய்மை, அழகை பேணி மகாலட்சுமி வழிபாடு செய்யுங்கள்.',
        7: 'கேது சமநிலைக்கு விநாயகர் பிரார்த்தனை செய்து விலங்குகளுக்கு உதவுங்கள்.',
        8: 'சனி சமநிலைக்கு ஏழைகளுக்கு அன்னதானம் அல்லது சேவை செய்யுங்கள்.',
        9: 'செவ்வாய் பலத்திற்கு தினமும் யோகா, உடற்பயிற்சி செய்யுங்கள்.'
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
        1: 'A year for fresh beginnings, new initiatives, and stepping into leadership.',
        2: 'A year of patience, partnerships, relationship harmony, and steady progress.',
        3: 'A year of creativity, expression, social growth, and joyful expansion.',
        4: 'A year of disciplined effort, structured planning, and career stability.',
        5: 'A year of travel, dynamic changes, business expansion, and adaptability.',
        6: 'A year focused on family, home, relationships, and auspicious milestones.',
        7: 'A year of spiritual reflection, self-awareness, research, and inner study.',
        8: 'A year of financial focus, authority, and meaningful business outcomes.',
        9: 'A year of completion, service, charity, and preparing for a new cycle.'
    },
    'te': {
        1: 'కొత్త ప్రారంభాలు, కొత్త ప్రణాళికలు మరియు నాయకత్వానికి అనుకూలమైన సంవత్సరం.',
        2: 'ఓపిక, భాగస్వామ్యాలు, సంబంధాల మెరుగుదల మరియు శాంతియుత పురోగతి సంవత్సరం.',
        3: 'సృజనాత్మకత, కళలు, మాట తీరు, ఆర్థిక వృద్ధి మరియు ఆనంద సంవత్సరం.',
        4: 'కఠిన శ్రమ, క్రమబద్ధ ప్రణాళిక, వృత్తిలో స్థిరత్వం ఇచ్చే సంవత్సరం.',
        5: 'ప్రయాణాలు, కొత్త మార్పులు, వ్యాపార విస్తరణ మరియు స్వేచ్ఛ సంవత్సరం.',
        6: 'కుటుంబంతో సమయం, ఇల్లు, వివాహం లేదా శుభకార్యాల సంవత్సరం.',
        7: 'ఆధ్యాత్మిక చింతన, ఆత్మపరిశీలన, పరిశోధన మరియు జ్ఞానార్జన సంవత్సరం.',
        8: 'ఆర్థిక విజయం, అధికారం, వ్యాపారంలో లాభాల సంవత్సరం.',
        9: 'పాత పనుల పూర్తి, దానధర్మాలు, సేవ మరియు కొత్త చక్రానికి సిద్ధమయ్యే సంవత్సరం.'
    },
    'hi': {
        1: 'नई शुरुआत, नई योजनाओं और नेतृत्व के लिए अनुकूल वर्ष।',
        2: 'धैर्य, साझेदारी, संबंधों में सुधार और संतुलित प्रगति का वर्ष।',
        3: 'रचनात्मकता, संवाद कौशल, आर्थिक उन्नति और आनंद का वर्ष।',
        4: 'मेहनत, सुव्यवस्थित योजना और करियर में स्थिरता का वर्ष।',
        5: 'यात्रा, नए बदलाव, व्यापार विस्तार और गतिशीलता का वर्ष।',
        6: 'परिवार, घर, रिश्तों और शुभ कार्यों पर केंद्रित वर्ष।',
        7: 'आत्मचिंतन, शोध, अध्ययन और आंतरिक समझ का वर्ष।',
        8: 'आर्थिक प्रगति, अधिकार और व्यावसायिक लाभ का वर्ष।',
        9: 'पुराने कार्यों को पूरा करने, सेवा, दान और नए चक्र की तैयारी का वर्ष।'
    },
    'ta': {
        1: 'புதிய தொடக்கங்கள், புதிய திட்டங்கள் மற்றும் தலைமைத்துவத்திற்கான சிறந்த ஆண்டு.',
        2: 'பொறுமை, கூட்டாண்மை, உறவுகளில் இணக்கம் மற்றும் நிதானமான முன்னேற்ற ஆண்டு.',
        3: 'படைப்பாற்றல், கலை, பேச்சாற்றல், பொருளாதார வளர்ச்சி மற்றும் மகிழ்ச்சி ஆண்டு.',
        4: 'கடின உழைப்பு, திட்டமிடல், பணியில் நிலைத்தன்மை தரும் ஆண்டு.',
        5: 'பயணம், புதிய மாற்றங்கள், வணிக விரிவாக்கம் மற்றும் சுதந்திரம் தரும் ஆண்டு.',
        6: 'குடும்பம், வீடு, உறவுகள் மற்றும் சுப நிகழ்ச்சிகளுக்கான ஆண்டு.',
        7: 'ஆன்மீக சிந்தனை, சுய ஆய்வு, ஆராய்ச்சி மற்றும் அறிவு தேடல் ஆண்டு.',
        8: 'பொருளாதார வெற்றி, அதிகாரம் மற்றும் வணிக லாபத்திற்கான ஆண்டு.',
        9: 'பழைய பணிகளை நிறைவு செய்யும், தானம், சேவை மற்றும் புதிய சுழற்சிக்கான ஆண்டு.'
    }
}

GOOD_PAIRS = {
    '11', '12', '13', '15', '17', '19', '25', '31', '33', '37', '39',
    '51', '52', '55', '57', '59', '66', '69', '71', '73', '75', '77',
    '83', '91', '92', '93', '95', '96', '99'
}
BAD_PAIRS = {
    '14', '16', '21', '22', '23', '24', '26', '27', '28', '30', '32', '34', '35', '36', '38',
    '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '53', '54', '56', '58',
    '60', '61', '62', '63', '64', '65', '67', '68', '70', '72', '74', '76', '78', '79', '80',
    '81', '82', '84', '85', '86', '87', '88', '89', '90', '94', '97', '98'
}


def reduce_to_single(num):
    while num > 9:
        num = sum(int(c) for c in str(num))
    return num


def get_relation(name_num, target_num, lang='kn'):
    if not name_num or not target_num:
        return "-"
    ui = UI_TEXT.get(lang, UI_TEXT['kn'])
    rel = RELATIONS.get(target_num, {'friends': [], 'enemies': [], 'neutral': []})
    if name_num in rel['friends']:
        return ui['friend']
    elif name_num in rel['enemies']:
        return ui['enemy']
    else:
        return ui['neutral']


def calculate_kua(year):
    yr_sum = sum(int(c) for c in str(year))
    yr_single = reduce_to_single(yr_sum)
    kua = (11 - yr_single) if yr_single <= 9 else 2
    if kua > 9:
        kua = reduce_to_single(kua)
    if kua == 5:
        kua = 2
    return kua


def analyze_mobile_advanced(phone_str, lang='kn'):
    digits = [c for c in phone_str if c.isdigit()]
    if len(digits) < 10:
        return None
    ui = UI_TEXT.get(lang, UI_TEXT['kn'])
    pair_results = []
    for i in range(len(digits) - 1):
        p = digits[i] + digits[i + 1]
        if p in GOOD_PAIRS:
            pair_results.append({'pair': p, 'type': 'good', 'label': ui['auspicious']})
        elif p in BAD_PAIRS:
            pair_results.append({'pair': p, 'type': 'bad', 'label': ui['bad']})
        else:
            pair_results.append({'pair': p, 'type': 'neutral', 'label': 'neutral'})
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
            val = reduce_to_single(row[i] + row[i + 1])
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
            s = row[i] + row[i + 1]
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
            s = row[i] + row[i + 1]
            val = reduce_to_single(s) if s > 0 else 0
            next_row.append(val)
        pyramid_rows.append(next_row.copy())
        row = next_row
    return pyramid_rows


def analyze_vedic_grid_yogas(present_numbers, lang='kn'):
    yogas = []
    texts = {
        'kn': {
            '369_n': '3-6-9 ವೈಭವ ಮತ್ತು ಸಂಪತ್ತು ಯೋಗ (Wealth & Glory Yoga)',
            '369_d': 'ಗುರು (3), ಶುಕ್ರ (6) ಮತ್ತು ಮಂಗಳ (9) ಒಟ್ಟಿಗೆ ಇರುವುದರಿಂದ ಜೀವನದಲ್ಲಿ ಐಷಾರಾಮಿ ಜೀವನ ಹಾಗೂ ಅಭಿವೃದ್ಧಿ ಪ್ರಾಪ್ತಿಯಾಗುತ್ತದೆ.',
            '159_n': '1-5-9 ರಾಜಯೋಗ ಮತ್ತು ನಾಯಕತ್ವ (Leadership & Rajayoga)',
            '159_d': 'ಸೂರ್ಯ (1), ಬುಧ (5) ಮತ್ತು ಮಂಗಳ (9) ಸಂಯೋಗದಿಂದ ಸಮಾಜದಲ್ಲಿ ಉನ್ನತ ಸ್ಥಾನ, ಅಧಿಕಾರ ಹಾಗೂ ಕೀರ್ತಿ ಲಭಿಸುತ್ತದೆ.',
            '319_n': '3-1-9 ಜ್ಞಾನ ಮತ್ತು ಬೌದ್ಧಿಕ ಯೋಗ (Mental & Knowledge Yoga)',
            '319_d': 'ತೀವ್ರವಾದ ಸ್ಮರಣಶಕ್ತಿ, ಉತ್ತಮ ನಿರ್ಧಾರ ಕೈಗೊಳ್ಳುವ ಸಾಮರ್ಥ್ಯ ಹಾಗೂ ಬಲವಾದ ಇಚ್ಛಾಶಕ್ತಿಯನ್ನು ಸೂಚಿಸುತ್ತದೆ.',
            '258_n': '2-5-8 ಸ್ಥಿರತೆ ಮತ್ತು ಆಸ್ತಿ ಯೋಗ (Stability & Property Yoga)',
            '258_d': 'ಚಂದ್ರ (2), ಬುಧ (5) ಮತ್ತು ಶನಿ (8) ಸಂಯೋಜನೆಯು ರಿಯಲ್ ಎಸ್ಟೇಟ್ ಹಾಗೂ ಆಸ್ತಿ ಖರೀದಿ ಯೋಗವನ್ನು ನೀಡುತ್ತದೆ.'
        },
        'en': {
            '369_n': '3-6-9 Wealth & Glory Yoga',
            '369_d': 'Presence of 3, 6, and 9 together supports prosperity, comfort, and overall growth.',
            '159_n': '1-5-9 Leadership & Rajayoga',
            '159_d': 'Combination of 1, 5, and 9 indicates leadership ability, recognition, and authority.',
            '319_n': '3-1-9 Mental & Knowledge Yoga',
            '319_d': 'Indicates a sharp memory, sound decision-making, and strong willpower.',
            '258_n': '2-5-8 Stability & Property Yoga',
            '258_d': 'Combination of 2, 5, and 8 supports stability, property, and practical planning.'
        },
        'te': {
            '369_n': '3-6-9 వైభవ మరియు సంపద యోగం (Wealth & Glory Yoga)',
            '369_d': '3, 6 మరియు 9 సంఖ్యలు కలిసి ఉండటం వల్ల జీవితంలో శ్రేయస్సు, సౌకర్యాలు మరియు అభివృద్ధి లభిస్తాయి.',
            '159_n': '1-5-9 రాజయోగం మరియు నాయకత్వం (Leadership & Rajayoga)',
            '159_d': '1, 5 మరియు 9 కలయిక నాయకత్వ పటిమ, గౌరవం మరియు ఉన్నత స్థానాన్ని సూచిస్తుంది.',
            '319_n': '3-1-9 జ్ఞాన మరియు మేధో యోగం (Mental & Knowledge Yoga)',
            '319_d': 'మంచి జ్ఞాపకశక్తి, సరైన నిర్ణయాలు తీసుకునే సామర్థ్యం మరియు దృఢ సంకల్పాన్ని సూచిస్తుంది.',
            '258_n': '2-5-8 స్థిరత్వ మరియు ఆస్తి యోగం (Stability & Property Yoga)',
            '258_d': '2, 5 మరియు 8 కలయిక స్థిరత్వం, ఆస్తి మరియు ఆచరణాత్మక ప్రణాళికలకు తోడ్పడుతుంది.'
        },
        'hi': {
            '369_n': '3-6-9 वैभव और समृद्धि योग (Wealth & Glory Yoga)',
            '369_d': '3, 6 और 9 की उपस्थिति जीवन में समृद्धि, सुख-सुविधा और प्रगति का संकेत देती है।',
            '159_n': '1-5-9 राजयोग और नेतृत्व (Leadership & Rajayoga)',
            '159_d': '1, 5 और 9 का संयोग नेतृत्व क्षमता, मान-सम्मान और प्रतिष्ठा प्रदान करता है।',
            '319_n': '3-1-9 ज्ञान और बौद्धिक योग (Mental & Knowledge Yoga)',
            '319_d': 'तीव्र स्मरणशक्ति, मजबूत निर्णय क्षमता और दृढ़ इच्छाशक्ति का सूचक है।',
            '258_n': '2-5-8 स्थिरता और संपत्ति योग (Stability & Property Yoga)',
            '258_d': '2, 5 और 8 का संयोग स्थिरता, संपत्ति और व्यावहारिक योजना को दर्शाता है।'
        },
        'ta': {
            '369_n': '3-6-9 செல்வ மற்றும் வளமை யோகம் (Wealth & Glory Yoga)',
            '369_d': '3, 6 மற்றும் 9 எண்கள் இணைந்து இருப்பது வாழ்வில் வளம், வசதி மற்றும் முன்னேற்றத்தைத் தருகிறது.',
            '159_n': '1-5-9 ராஜயோகம் மற்றும் தலைமைத்துவம் (Leadership & Rajayoga)',
            '159_d': '1, 5 மற்றும் 9 சேர்க்கை தலைமைப் பண்பு, மதிப்பு மற்றும் உயர்ந்த நிலையைக் குறிக்கிறது.',
            '319_n': '3-1-9 அறிவு மற்றும் சிந்தனை யோகம் (Mental & Knowledge Yoga)',
            '319_d': 'சிறந்த நினைவாற்றல், தெளிவான முடிவெடுக்கும் திறன் மற்றும் உறுதியான மனவலிமையைக் குறிக்கிறது.',
            '258_n': '2-5-8 நிலைத்தன்மை மற்றும் சொத்து யோகம் (Stability & Property Yoga)',
            '258_d': '2, 5 மற்றும் 8 சேர்க்கை நிலைத்தன்மை, சொத்து மற்றும் நடைமுறைத் திட்டமிடலுக்கு உதவுகிறது.'
        }
    }
    t = texts.get(lang, texts['kn'])
    p = set(present_numbers)
    if {3, 6, 9}.issubset(p):
        yogas.append({'name': t['369_n'], 'desc': t['369_d']})
    if {1, 5, 9}.issubset(p):
        yogas.append({'name': t['159_n'], 'desc': t['159_d']})
    if {3, 1, 9}.issubset(p):
        yogas.append({'name': t['319_n'], 'desc': t['319_d']})
    if {2, 5, 8}.issubset(p):
        yogas.append({'name': t['258_n'], 'desc': t['258_d']})
    return yogas


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{{ ui.title }}</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Segoe UI', Noto Sans Kannada, Noto Sans Telugu, Noto Sans Devanagari, Noto Sans Tamil, sans-serif;
      background: #f4f6fb;
      color: #1e293b;
      padding: 20px;
      line-height: 1.6;
    }
    .container { max-width: 1050px; margin: 0 auto; }
    .header-banner {
      background: linear-gradient(135deg, #0f172a, #1e3a8a, #312e81);
      color: #fff;
      padding: 24px 28px;
      border-radius: 14px;
      margin-bottom: 20px;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.16);
    }
    .header-banner h1 { font-size: 24px; margin-bottom: 6px; }
    .header-banner p { font-size: 14px; opacity: 0.9; }
    .form-card {
      background: #ffffff;
      padding: 22px;
      border-radius: 12px;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
      margin-bottom: 22px;
      border-top: 4px solid #2563eb;
    }
    .form-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 14px;
      margin-bottom: 16px;
    }
    .field label {
      display: block;
      font-size: 13px;
      font-weight: 600;
      margin-bottom: 5px;
      color: #334155;
    }
    .field input, .field select {
      width: 100%;
      padding: 9px 12px;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      font-size: 14px;
      background: #fff;
    }
    .btn-row { display: flex; gap: 12px; flex-wrap: wrap; }
    .btn-primary {
      background: #2563eb;
      color: #fff;
      border: none;
      padding: 10px 22px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
    }
    .btn-primary:hover { background: #1d4ed8; }
    .btn-print {
      background: #059669;
      color: #fff;
      border: none;
      padding: 10px 20px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
    }
    .btn-print:hover { background: #047857; }

    /* Distinct color accents for every section card and heading */
    .section-card {
      background: #ffffff;
      border-radius: 12px;
      padding: 20px 22px;
      margin-bottom: 18px;
      box-shadow: 0 3px 12px rgba(15, 23, 42, 0.05);
      border-left: 6px solid #2563eb;
    }
    .section-title {
      font-size: 18px;
      font-weight: 700;
      margin-bottom: 14px;
      padding-bottom: 6px;
      border-bottom: 1px dashed #e2e8f0;
    }
    .sec-strength { border-left-color: #dc2626; }
    .sec-strength .section-title { color: #b91c1c; }

    .sec-1 { border-left-color: #2563eb; }
    .sec-1 .section-title { color: #1d4ed8; }

    .sec-2 { border-left-color: #7c3aed; }
    .sec-2 .section-title { color: #6d28d9; }

    .sec-3 { border-left-color: #db2777; }
    .sec-3 .section-title { color: #be185d; }

    .sec-4 { border-left-color: #0891b2; }
    .sec-4 .section-title { color: #0e7490; }

    .sec-5 { border-left-color: #d97706; }
    .sec-5 .section-title { color: #b45309; }

    .sec-6 { border-left-color: #059669; }
    .sec-6 .section-title { color: #047857; }

    .sec-7 { border-left-color: #ea580c; }
    .sec-7 .section-title { color: #c2410c; }

    .sec-8 { border-left-color: #4f46e5; }
    .sec-8 .section-title { color: #4338ca; }

    .sec-9 { border-left-color: #0d9488; }
    .sec-9 .section-title { color: #0f766e; }

    .sec-10 { border-left-color: #9333ea; }
    .sec-10 .section-title { color: #7e22ce; }

    .grid-3x3 {
      display: grid;
      grid-template-columns: repeat(3, 72px);
      gap: 8px;
      justify-content: center;
      margin: 14px auto;
    }
    .grid-cell {
      width: 72px;
      height: 72px;
      border: 2px solid #94a3b8;
      border-radius: 10px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: #f8fafc;
    }
    .grid-cell.active {
      background: #dbeafe;
      border-color: #2563eb;
      font-weight: 700;
    }
    .grid-cell .num-val { font-size: 18px; color: #0f172a; }
    .grid-cell .num-cnt { font-size: 11px; color: #2563eb; }

    /* Centered Pyramid Box matching classic PDF layout */
    .pyramid-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
      margin-top: 10px;
    }
    .pyramid-box {
      background: #fdf2f8;
      border: 1px solid #fbcfe8;
      border-radius: 10px;
      padding: 14px;
      text-align: center;
    }
    .pyramid-box h4 {
      color: #9d174d;
      margin-bottom: 10px;
      font-size: 15px;
    }
    .pyramid-row {
      display: flex;
      justify-content: center;
      gap: 6px;
      margin-bottom: 5px;
      flex-wrap: wrap;
    }
    .pyramid-node {
      min-width: 26px;
      height: 26px;
      padding: 0 5px;
      border-radius: 6px;
      background: #ffffff;
      border: 1px solid #f472b6;
      color: #831843;
      font-weight: 700;
      font-size: 13px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }
    .final-badge {
      margin-top: 10px;
      display: inline-block;
      background: #be185d;
      color: #fff;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 700;
    }

    .info-list { list-style: none; }
    .info-list li {
      padding: 6px 0;
      border-bottom: 1px solid #f1f5f9;
      font-size: 14px;
    }
    .badge-good { color: #047857; background: #d1fae5; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 12px; }
    .badge-bad { color: #b91c1c; background: #fee2e2; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 12px; }
    .badge-neutral { color: #475569; background: #e2e8f0; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 12px; }

    @media print {
      body { background: #fff; padding: 0; }
      .form-card, .btn-print { display: none !important; }
      .section-card { box-shadow: none; break-inside: avoid; }
    }
  </style>
</head>
<body>
<div class="container">
  <div class="header-banner">
    <h1>{{ ui.title }}</h1>
    <p>{{ ui.subtitle }}</p>
  </div>

  <form method="POST" class="form-card">
    <div class="form-grid">
      <div class="field">
        <label>{{ ui.lang_label }}</label>
        <select name="lang" onchange="this.form.submit()">
          <option value="kn" {% if lang == 'kn' %}selected{% endif %}>ಕನ್ನಡ (Kannada)</option>
          <option value="en" {% if lang == 'en' %}selected{% endif %}>English</option>
          <option value="te" {% if lang == 'te' %}selected{% endif %}>తెలుగు (Telugu)</option>
          <option value="hi" {% if lang == 'hi' %}selected{% endif %}>हिन्दी (Hindi)</option>
          <option value="ta" {% if lang == 'ta' %}selected{% endif %}>தமிழ் (Tamil)</option>
        </select>
      </div>
      <div class="field">
        <label>{{ ui.name }}</label>
        <input type="text" name="name" value="{{ name }}" placeholder="Munniratnam K R" />
      </div>
      <div class="field">
        <label>{{ ui.dob }}</label>
        <input type="date" name="dob" value="{{ dob }}" />
      </div>
      <div class="field">
        <label>{{ ui.mobile }}</label>
        <input type="text" name="mobile" value="{{ mobile }}" placeholder="9513129695" />
      </div>
      <div class="field">
        <label>{{ ui.p2_name }}</label>
        <input type="text" name="p2_name" value="{{ p2_name }}" />
      </div>
      <div class="field">
        <label>{{ ui.p2_dob }}</label>
        <input type="date" name="p2_dob" value="{{ p2_dob }}" />
      </div>
    </div>
    <div class="btn-row">
      <button type="submit" class="btn-primary">{{ ui.calc_btn }}</button>
      <button type="button" class="btn-print" onclick="window.print()">{{ ui.print_btn }}</button>
    </div>
  </form>

  <!-- Strength Analysis -->
  <div class="section-card sec-strength">
    <div class="section-title">{{ ui.strength_title }}</div>
    <ul class="info-list">
      <li><strong>Driver (Mulank):</strong> {{ driver if driver else '-' }} | <strong>Conductor (Bhagyank):</strong> {{ conductor if conductor else '-' }}</li>
      <li><strong>Chaldean Name Total:</strong> {{ chaldean_total }} ({{ chaldean_single }}) | <strong>Pythagorean Name Total:</strong> {{ pythagorean_total }} ({{ pythagorean_single }})</li>
      <li><strong>Name Frequency Total:</strong> {{ freq_total }} | <strong>Birth Degree Reference:</strong> {{ birth_deg if birth_deg else '-' }}</li>
    </ul>
  </div>

  <!-- 1. DOB & Vedic Grid -->
  <div class="section-card sec-1">
    <div class="section-title">{{ ui.s1_title }}</div>
    <p><strong>DOB:</strong> {{ dob if dob else '-' }}</p>
    <div class="grid-3x3">
      {% for cell in vedic_cells %}
      <div class="grid-cell {% if cell.count > 0 %}active{% endif %}">
        <span class="num-val">{{ cell.num }}</span>
        <span class="num-cnt">{% if cell.count > 0 %}×{{ cell.count }}{% else %}-{% endif %}</span>
      </div>
      {% endfor %}
    </div>
  </div>

  <!-- 2. Vedic Grid Yogas -->
  <div class="section-card sec-2">
    <div class="section-title">{{ ui.s2_title }}</div>
    {% if yogas %}
      <ul class="info-list">
        {% for y in yogas %}
        <li><strong>{{ y.name }}:</strong> {{ y.desc }}</li>
        {% endfor %}
      </ul>
    {% else %}
      <p>{{ ui.no_yoga }}</p>
    {% endif %}
  </div>

  <!-- 3. Pyramid Number Analysis -->
  <div class="section-card sec-3">
    <div class="section-title">{{ ui.s3_title }}</div>
    <div class="pyramid-grid">
      <!-- Name Pyramid -->
      <div class="pyramid-box">
        <h4>Name Pyramid ({{ name if name else '-' }})</h4>
        {% if name_pyramid %}
          {% for row in name_pyramid %}
            <div class="pyramid-row">
              {% for val in row %}
                <span class="pyramid-node">{{ val }}</span>
              {% endfor %}
            </div>
          {% endfor %}
          <div class="final-badge">Final Name Pyramid Number: {{ name_pyramid[-1][0] }}</div>
        {% else %}
          <p>-</p>
        {% endif %}
      </div>

      <!-- DOB Pyramid -->
      <div class="pyramid-box">
        <h4>DOB Pyramid ({{ dob if dob else '-' }})</h4>
        {% if dob_pyramid %}
          {% for row in dob_pyramid %}
            <div class="pyramid-row">
              {% for val in row %}
                <span class="pyramid-node">{{ val }}</span>
              {% endfor %}
            </div>
          {% endfor %}
          <div class="final-badge">Final Pyramid Number of DOB: {{ dob_pyramid[-1][0] }}</div>
        {% else %}
          <p>-</p>
        {% endif %}
      </div>

      <!-- Mobile Pyramid -->
      <div class="pyramid-box">
        <h4>Mobile Pyramid ({{ mobile if mobile else '-' }})</h4>
        {% if mobile_pyramid %}
          {% for row in mobile_pyramid %}
            <div class="pyramid-row">
              {% for val in row %}
                <span class="pyramid-node">{{ val }}</span>
              {% endfor %}
            </div>
          {% endfor %}
          <div class="final-badge">Final Mobile Pyramid Number: {{ mobile_pyramid[-1][0] }}</div>
        {% else %}
          <p>-</p>
        {% endif %}
      </div>
    </div>
  </div>

  <!-- 4. Partnership Matching -->
  <div class="section-card sec-4">
    <div class="section-title">{{ ui.s4_title }}</div>
    <ul class="info-list">
      <li><strong>Person 1:</strong> {{ name if name else '-' }} (Driver: {{ driver if driver else '-' }}, Conductor: {{ conductor if conductor else '-' }})</li>
      <li><strong>Partner:</strong> {{ p2_name if p2_name else '-' }} (Driver: {{ p2_driver if p2_driver else '-' }}, Conductor: {{ p2_conductor if p2_conductor else '-' }})</li>
      <li><strong>Compatibility Status:</strong> {{ partner_relation }}</li>
    </ul>
  </div>

  <!-- 5. Personal Year & Month -->
  <div class="section-card sec-5">
    <div class="section-title">{{ ui.s5_title }}</div>
    <ul class="info-list">
      <li><strong>Personal Year ({{ current_year }}):</strong> {{ personal_year if personal_year else '-' }}</li>
      <li><strong>Personal Month ({{ current_month }}):</strong> {{ personal_month if personal_month else '-' }}</li>
      <li><strong>Guidance:</strong> {{ personal_year_desc if personal_year_desc else '-' }}</li>
    </ul>
  </div>

  <!-- 6. Lucky Color, Direction, Gemstone, Kua & Profession -->
  <div class="section-card sec-6">
    <div class="section-title">{{ ui.s6_title }}</div>
    {% if props %}
      <ul class="info-list">
        <li><strong>Lucky Colors:</strong> {{ props.colors }}</li>
        <li><strong>Favorable Direction:</strong> {{ props.direction }}</li>
        <li><strong>Gemstone:</strong> {{ props.gemstone }}</li>
        <li><strong>Kua Number:</strong> {{ kua_num if kua_num else '-' }}</li>
        <li><strong>Suitable Profession:</strong> {{ props.profession }}</li>
        <li><strong>Lucky Days:</strong> {{ props.lucky_days }}</li>
      </ul>
    {% else %}
      <p>-</p>
    {% endif %}
  </div>

  <!-- 7. Missing Numbers & Remedies -->
  <div class="section-card sec-7">
    <div class="section-title">{{ ui.s7_title }}</div>
    {% if missing_nums %}
      <p style="margin-bottom: 8px;"><strong>Missing Numbers:</strong> {{ missing_nums | join(', ') }}</p>
      <ul class="info-list">
        {% for m in missing_nums %}
          <li><strong>Number {{ m }}:</strong> {{ remedies[m] }}</li>
        {% endfor %}
      </ul>
    {% else %}
      <p>-</p>
    {% endif %}
  </div>

  <!-- 8. Name Analysis -->
  <div class="section-card sec-8">
    <div class="section-title">{{ ui.s8_title }}</div>
    <ul class="info-list">
      <li><strong>Chaldean Total / Compound:</strong> {{ chaldean_total }} → {{ chaldean_single }}</li>
      <li><strong>Pythagorean Total / Compound:</strong> {{ pythagorean_total }} → {{ pythagorean_single }}</li>
      <li><strong>Name vs Driver Relation:</strong> {{ rel_driver }}</li>
    </ul>
  </div>

  <!-- 9. Name vs DOB Compatibility -->
  <div class="section-card sec-9">
    <div class="section-title">{{ ui.s9_title }}</div>
    <ul class="info-list">
      <li><strong>Relation with Driver ({{ driver if driver else '-' }}):</strong> {{ rel_driver }}</li>
      <li><strong>Relation with Conductor ({{ conductor if conductor else '-' }}):</strong> {{ rel_conductor }}</li>
    </ul>
    {% if mobile_analysis %}
      <p style="margin-top: 10px;"><strong>Mobile Sum:</strong> {{ mobile_analysis.total_sum }} (Root: {{ mobile_analysis.root_no }}, Ending: {{ mobile_analysis.ending_no }})</p>
      <div style="margin-top: 8px; display: flex; flex-wrap: wrap; gap: 6px;">
        {% for pr in mobile_analysis.pair_results %}
          <span class="{% if pr.type == 'good' %}badge-good{% elif pr.type == 'bad' %}badge-bad{% else %}badge-neutral{% endif %}">
            {{ pr.pair }} ({{ pr.label }})
          </span>
        {% endfor %}
      </div>
    {% endif %}
  </div>

  <!-- 10. Common Lucky Numbers -->
  <div class="section-card sec-10">
    <div class="section-title">{{ ui.s10_title }}</div>
    <p><strong>Common Lucky Numbers:</strong> {{ common_lucky | join(', ') if common_lucky else '-' }}</p>
  </div>
</div>
</body>
</html>
"""


def parse_dob_parts(dob_str):
    if not dob_str:
        return None
    try:
        dt = datetime.strptime(dob_str, "%Y-%m-%d")
        return dt.day, dt.month, dt.year
    except ValueError:
        return None


@app.route("/", methods=["GET", "POST"])
def index():
    lang = request.form.get("lang", "kn")
    if lang not in UI_TEXT:
        lang = "kn"
    ui = UI_TEXT[lang]

    name = request.form.get("name", "Munniratnam K R").strip()
    dob = request.form.get("dob", "1974-02-13").strip()
    mobile = request.form.get("mobile", "9513129695").strip()
    p2_name = request.form.get("p2_name", "").strip()
    p2_dob = request.form.get("p2_dob", "").strip()

    upper_letters = [ch for ch in name.upper() if ch.isalpha()]
    chaldean_total = sum(CHALDEAN_MAP.get(ch, 0) for ch in upper_letters)
    pythagorean_total = sum(PYTHAGOREAN_MAP.get(ch, 0) for ch in upper_letters)
    freq_total = sum(NAME_FREQ_MAP.get(ch, 0) for ch in upper_letters)

    chaldean_single = reduce_to_single(chaldean_total) if chaldean_total > 0 else 0
    pythagorean_single = reduce_to_single(pythagorean_total) if pythagorean_total > 0 else 0

    driver = None
    conductor = None
    kua_num = None
    birth_deg = None
    present_numbers = []
    missing_nums = []
    personal_year = None
    personal_month = None
    personal_year_desc = None

    now = datetime.now()
    current_year = now.year
    current_month = now.month

    dob_parts = parse_dob_parts(dob)
    if dob_parts:
        day, month, year = dob_parts
        driver = reduce_to_single(day)
        all_dob_digits = [int(c) for c in f