# How to Upgrade Python to 3.12 on Ubuntu

Since the automated tools failed, here are the manual steps to upgrade your Python version.

## 1. Add the Deadsnakes PPA
This repository contains the latest Python versions for Ubuntu.

```bash
sudo apt-get update
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
```

## 2. Install Python 3.12
Install the interpreter and the virtual environment module.

```bash
sudo apt-get install -y python3.12 python3.12-venv python3.12-dev python3.12-distutils
```

## 3. Re-create Virtual Environment
Navigate to your project folder (`solution3-2`) and run:

```bash
# Delete existing venv
rm -rf .venv

# Create new venv with Python 3.12
python3.12 -m venv .venv

# Activate
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 4. Run the App
```bash
python app.py
```
