import pickle
from pathlib import Path

import streamlit_authenticator as stauth

names = ["Wahyu Hidayat", "Admin Zobu","Roger Tumewu"]
usernames = ["hidayat", "admzobu", "roger"]
paswords = ["123456", "12345678", "zone2000"]

hashed_passwords = stauth.Hasher(passwords).generate()

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file:
	pickle.dump(hashed_passwords, file)
