import requests
from bs4 import BeautifulSoup

def scrape_keys(url):
    """
    Scrapes the given URL to extract 'Access Key' and 'Secret Key' fields.

    Args:
        url (str): The URL of the website to scrape.

    Returns:
        dict: A dictionary containing the extracted keys.
    """
    try:
        # Send a GET request to the website
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP errors

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the keys
        access_key = None
        secret_key = None

        # Find all <dl> elements
        dl_elements = soup.find_all("dl")

        for dl in dl_elements:
            dt = dl.find("dt")
            dd = dl.find("dd")
            if dt and dd:
                label = dt.text.strip()
                value = dd.text.strip()
                if label == "Access Key":
                    access_key = value
                elif label == "Secret Key":
                    secret_key = value

        # Return the extracted keys
        return {
            "access_key": access_key,
            "secret_key": secret_key
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None
    except Exception as e:
        print(f"Error parsing the HTML: {e}")
        return None


if __name__ == "__main__":
    # Example usage
    url = "http://127.0.0.1:8004/ui"  # Replace with the actual URL
    keys = scrape_keys(url)
    if keys:
        print("Extracted Keys:")
        print(f"Access Key: {keys.get('Access Key')}")
        print(f"Secret Key: {keys.get('Secret Key')}")
    else:
        print("Failed to extract keys.")