# Selenium Techleap Scraper

Warning: The code written in this project is not provided with any gurranties or warranties. Use it on your own risk.

## How to setup

### Clone the repository and go inside it

```
git clone https://github.com/SNathJr/Accelerator_Scraper.git
cd Accelerator_Scraper
```

### Create a Python virtual environment

```
python3 -m venv venv
```

### Activate the said environment

On Windows Powershell:

```
.\venv\Scripts\Activate.ps1
```

On Linux / Mac:

```
source ./venv/bin/activate
```

### Install Dependencies

```
pip install -r requirements.txt
```

### Create an environment file

You can use any IDE to create a new file `.env` inside `Accelerator_Scraper` folder.

And use the following snipped to customize and use your own variables (SIB is Send In Blue).

```
SIB_API_KEY="bfnkjhfjdkjgfdsjhklfgsjklkjldfkljkljdaf"
SIB_SENDER="example@example.com"
SIB_RECIPIENT="example@example.com"
TECHLEAP_USER="example@example.com"
TECHLEAP_PASS="password"
```

### Run the selenium file

```
python techleap.py
```
