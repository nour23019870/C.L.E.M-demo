# Phone Information Utility

![Phone Info Tool Screenshot](img/img.jpg)

A Python utility for retrieving detailed information about phone numbers using phonenumbers library and IP Quality Score API.

## Features

- Validate phone numbers
- Retrieve carrier information
- Determine phone number location and region
- Check phone number reputation and risk factors
- Detect VOIP, prepaid, and spammer flags
- Save phone number data to CSV for further analysis

## Requirements

- Python 3.6+
- Required packages:
  - phonenumbers
  - requests
  - colorama (for the hacker UI)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/nour23019870/phone-info-utility.git
   cd phone-info-utility
   ```

2. Install required packages:
   ```
   pip install phonenumbers requests colorama
   ```

3. Set up your IP Quality Score API key:
   - Sign up at [IP Quality Score](https://www.ipqualityscore.com/) to get an API key
   - Replace `YOUR_API_KEY_HERE` in `main.py` with your actual API key

## Usage

Run the script:
```
python main.py
```

1. Enter a phone number in international format (e.g., +12125552368)
2. Review the detailed information about the phone number
3. Choose whether to save the data to a CSV file

![Tool Interface](img/img.jpg)

## Data Points

The utility provides the following information about phone numbers:

- Basic formatting and validation
- Carrier information
- Geographic location (country, region, city)
- Line type (mobile, landline, etc.)
- Time zone
- Risk assessment factors:
  - Fraud score
  - Recent abuse indicators
  - VOIP status
  - Do Not Call list presence
  - Spammer detection

## File Structure

- `main.py`: Core script with the phone number lookup functionality
- `phone_log.csv`: CSV file where phone number data is stored
- `phone_info.docx`: Documentation file (if applicable)

## License

[MIT License](https://opensource.org/licenses/MIT)

## Disclaimer

This tool is for informational purposes only. Always respect privacy laws and regulations when collecting or processing phone number data.