import sys
import os
import time
from requests import get

raw_pastes_folder = "data/raw_pastes"
raw_pastes_folder_pasteorg = "data/raw_pastes_pasteorg"
password_files_folder = "data/files_with_passwords"
archive_folder = "archive"
os.system("clear")


while True:
        print("""


        \t\t  ___|
        \t\t\___ \   __|  _` |\ \   / _ \ __ \   _` |  _ \  __|
        \t\t      | (    (   | \ \ /  __/ |   | (   |  __/ |
        \t\t_____/ \___|\__,_|  \_/ \___|_|  _|\__, |\___|_|
        \t\t                                   |___/

        """)

        print("-----------------------------------------------------")

        numfiles_raw_pastes = (len([f for f in os.listdir(raw_pastes_folder) if os.path.isfile(os.path.join(raw_pastes_folder, f)) and f[0] != '.']) -1)
        numfiles_raw_pastes_pasteorg = (len([f for f in os.listdir(raw_pastes_folder_pasteorg) if os.path.isfile(os.path.join(raw_pastes_folder_pasteorg, f)) and f[0] != '.']) -1)
        numfiles_password_files = (len([f for f in os.listdir(password_files_folder) if os.path.isfile(os.path.join(password_files_folder, f)) and f[0] != '.']) -1)
        numfiles_archives = (len([f for f in os.listdir(archive_folder) if os.path.isfile(os.path.join(archive_folder, f)) and f[0] != '.']) -1)

        print("|\tNumber of raw pastes (Pastebin.com): " + str(numfiles_raw_pastes))
        print("|\tNumber of raw pastes (Paste.org): " + str(numfiles_raw_pastes_pasteorg))
        print("|\tNumber of files with passwords: " + str(numfiles_password_files))
        print("|\tNumber of archives: " + str(numfiles_archives))
        print("-----------------------------------------------------\n")
        print("Note: If you do not have a PRO account, pastebin might ban your IP")
        print(f"      Current IP Address: {get('https://api.ipify.org').text}")
        time.sleep(5)
        os.system("clear")

