Write-Output "Creating python virtual environment ..."
python -m venv venv
Write-Output "Python virtual environment created ..."
Write-Output "Switching console to python venv ..."
.\venv\Scripts\activate
Write-Output "Switched console to python venv ..."
Write-Output "Installing python packages from requirements.txt ..."
pip install -r requirements.txt
Write-Output "Python packages installation completed ..."