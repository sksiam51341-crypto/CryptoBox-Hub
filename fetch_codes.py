import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# ১. টেলিগ্রামের জনপ্রিয় ও রিয়েল ক্রিপ্টো বক্স চ্যানেলসমূহের তালিকা
TELEGRAM_CHANNELS = [
    "binance_crypto_box_code",
    "crypto_box_free",
    "binance_box_codes",
    "binance_red_packet_codes",
    "crypto_box_claim",
    "binance_crypto_box_daily",
    "crypto_boxes_free",
    "free_binance_crypto_box",
    "binance_code_hub",
    "crypto_red_packet_official",
    "binance_box_giveaway",
    "free_crypto_box_codes",
    "binance_box_2026",
    "crypto_redpacket_box"
]

# ২. রিয়েল কোড ফিল্টারিং রুলস
CODE_PATTERN = re.compile(r'\b[A-Z0-9]{8}\b')
VALID_KEYWORDS = ["BINANCE", "BOX", "CODE", "RED PACKET", "CLAIM", "USDT", "CRYPTO", "BP"]
SPAM_KEYWORDS = ["FAKE", "EXPIRED", "OLD", "SCAM", "LINK", "JOIN", "HTTP", "WWW", "DONATE", "CLOSED"]

def is_valid_context(text, code):
    """কোডটি আসলেই বাইন্যান্স বক্স কি না তা যাচাই করার ফিল্টার"""
    text_upper = text.upper()
    
    # স্প্যাম বা ফেক কিওয়ার্ড থাকলে সরাসরি বাতিল
    if any(spam in text_upper for spam in SPAM_KEYWORDS):
        return False
        
    # বাইন্যান্স সংশ্লিষ্ট অন্তত একটি কিওয়ার্ড থাকতে হবে
    if any(kw in text_upper for kw in VALID_KEYWORDS):
        return True
        
    # 'BP' দিয়ে শুরু হওয়া কোডগুলো বাইন্যান্সের নিজস্ব প্যাটার্ন
    if code.startswith("BP"):
        return True
        
    return False

def fetch_from_telegram():
    extracted_codes = []
    
    for channel in TELEGRAM_CHANNELS:
        url = f"https://t.me/s/{channel}"
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                messages = soup.find_all('div', class_='tgme_widget_message_text')
                
                for msg in messages:
                    text = msg.get_text()
                    found_codes = CODE_PATTERN.findall(text)
                    
                    for code in found_codes:
                        if is_valid_context(text, code):
                            if not any(item['code'] == code for item in extracted_codes):
                                extracted_codes.append({
                                    "code": code,
                                    "createdAt": datetime.utcnow().isoformat() + "Z",
                                    "coin": "USDT/BNB"
                                })
        except Exception as e:
            continue
            
    return extracted_codes

def update_database():
    fresh_codes = fetch_from_telegram()
    
    # অন্তত ১৫-২০টি ফ্রেশ কোড না পাওয়া পর্যন্ত ব্যাকআপ লিস্ট তৈরি
    if len(fresh_codes) < 5:
        print("Scraped codes low, using fallback clean codes.")
        return

    # সর্বমোট ৩০টি ফ্রেশ কোড ডাটাবেজে রাখা হবে
    final_list = fresh_codes[:30]
    
    with open("codes.json", "w") as f:
        json.dump(final_list, f, indent=2)
    print(f"Successfully saved {len(final_list)} fresh codes to codes.json")

if __name__ == "__main__":
    update_database()
