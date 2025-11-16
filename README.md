> [!NOTE]  
> Work in progress, this has worked on macos but not ubuntu (raspberry pi)

> [!CAUTION]    
> You must deactivate MFA (sorry)

# enbridge-gas-green-button
 
Inspired by [toronto-hydro-green-button](https://github.com/benwebber/toronto-hydro-green-button)

Export [Green Button](https://green-button.github.io/) ([ESPI](https://www.naesb.org//ESPI_Standards.asp)) energy usage data from your [Enbridge Gas](https://enbridgegas.com/) account.

Enbridge Gas offers a Green Button XML export through the customer portal, but does not offer programmatic API access.
This script logs into the dashboard and downloads the file with [Selenium](https://selenium.dev/).

## Requirements

* a [Enbridge Gas](https://enbridgegas.com/) account
* Python 3.6+
* Firefox 57+ or Google Chrome and ChromeDriver

## Installation

1. Clone the repository
2. Setup the package
```
python -m venv .
pip install .
```

## Usage

1. Activate the python virtual environment
```
source bin/activate
```
2. Run the script
```
python enbridge_gas_green_button.py --username USERNAME --password PASSWORD --account-id ACCOUNT_ID --output enbridge_gas.xml
```

The script takes the following arguments:
- `username`
- `password`
- `account-id`

You can find you account ID by manually downloading your green button data, and inspecting the url components of the request made to `https://myaccount.enbridgegas.com/api/ShareMyData/Download`

```
usage: enbridge_gas_green_button.py [-h] [--version] [--username USERNAME] [--password PASSWORD] [--start-date START_DATE] [--end-date END_DATE] [--browser {firefox,chrome}] [--output OUTPUT]

Export Green Button (ESPI) energy usage data from your Enbridge Gas account.

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --username, -u USERNAME
                        Enbridge Gas username. Will prompt if not set. [ENBRIDGE_GAS_USERNAME]
  --password, -p PASSWORD
                        Enbridge Gas password. Will prompt if not set. [ENBRIDGE_GAS_PASSWORD]
  --start-date START_DATE
                        Fetch usage data from this date (inclusive, YYYY-mm-dd). Defaults to eight days ago (2025-11-08).
  --end-date END_DATE   Fetch usage data through this date (inclusive, YYYY-mm-dd). Defaults to one day ago (2025-11-15).
  --browser {firefox,chrome}
                        Headless browser to use to access Enbridge Gas dashboard (default: firefox).
  --output, -o OUTPUT   Write XML data to this file. Defaults to standard output.
```

If ChromeDriver is installed, the script attempts to use it by default.
Otherwise it falls back on headless Firefox.
ChromeDriver was slightly faster in my limited testing.

## Tips

You can't get data for the current day, so this script defaults to getting data from yesterday.

## License

MIT
