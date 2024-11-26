import requests
import os
import subprocess
import zipfile

APP_VERSION = "1.1.0"  # Replace with your current app version
VERSION_URL = "https://raw.githubusercontent.com/ElTragedy/OverwatchTime/main/version.txt"
INSTALLER_URL = "https://github.com/ElTragedy/OverwatchTime/releases/latest/download/OverwatchTimeInstaller.zip"

def check_for_update():
    """
    Checks for updates by comparing the current version with the latest version on the server.
    """
    # Fetch the latest version from GitHub
    response = requests.get(VERSION_URL)
    response.raise_for_status()
    latest_version = response.text.strip()

    if latest_version > APP_VERSION:
        update_now = prompt_for_update()
        if update_now:
            download_and_run_installer()

def prompt_for_update():
    """
    Prompts the user to update the application.
    Returns True if the user agrees, otherwise False.
    """
    from PyQt5.QtWidgets import QMessageBox, QApplication
    import sys

    app_created = False

    # Check if a QApplication instance already exists
    if not QApplication.instance():
        app = QApplication(sys.argv)
        app_created = True

    reply = QMessageBox.question(
        None,
        "Update Available",
        "A new version of OverwatchTime is available. Do you want to update now?",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No,
    )

    # If we created a temporary QApplication, clean it up
    if app_created:
        app.quit()

    return reply == QMessageBox.Yes



def download_and_run_installer():
    """
    Downloads the installer ZIP file, extracts it, and runs the .exe file.
    """
    temp_dir = os.getenv('TEMP')
    zip_path = os.path.join(temp_dir, "OverwatchTimeInstaller.zip")
    exe_path = os.path.join(temp_dir, "OverwatchTimeInstaller.exe")

    # Download the ZIP file
    response = requests.get(INSTALLER_URL, stream=True)
    response.raise_for_status()

    with open(zip_path, 'wb') as zip_file:
        for chunk in response.iter_content(chunk_size=8192):
            zip_file.write(chunk)


    # Extract the ZIP file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)


    # Run the .exe file
    subprocess.run([exe_path], check=True)
