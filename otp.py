import random
import string
import time
from hashlib import sha256

otp_store = {}

def generate_otp(user_id, validity=300):

    otp = ''.join(random.choices(string.digits, k=6))
    expiry = time.time() + validity  
    otp_hash = sha256(otp.encode()).hexdigest()
    otp_store[user_id] = {"otp_hash": otp_hash, "expiry": expiry}
    
    return otp

def verify_otp(user_id, otp):

    if user_id not in otp_store:
        return False  
    stored_otp_data = otp_store[user_id]

    if time.time() > stored_otp_data["expiry"]:
        del otp_store[user_id]  
        return False

    otp_hash = sha256(otp.encode()).hexdigest()
    if otp_hash == stored_otp_data["otp_hash"]:
        del otp_store[user_id]  
        return True
    
    return False

