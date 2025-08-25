import requests
import csv
from bs4 import BeautifulSoup

def get_athlete_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get athlete name
    name_tag = soup.find('h1', class_='athlete-name')
    if name_tag:
        name = name_tag.text.strip()
    else:
        # fallback: try title
        title = soup.find('title')
        if title:
            name = title.text.split('|')[0].strip()
        else:
            name = "Unknown"

    # Get this month's distance
    distance = find_elements_in_monthly_stats(soup)
    # Try to find the section with this month's stats
    stats = soup.find_all('div', class_='athlete-stats')

    print("Athlete Name:", name)
    print("This Month's Distance:", distance if distance else "Not found")

def find_elements_in_monthly_stats(soup):
    """
    Return all text contents inside the div[data-testid="monthly-stats"]
    where the text matches numbers followed by a space and 'km'.
    """
    import re
    container = soup.find('div', attrs={'data-testid': 'monthly-stats'})
    if not container:
        return []
    result = None
    pattern = re.compile(r'^\s*\d+(?:\.\d+)?\s+km\s*$', re.IGNORECASE)
    for el in container.find_all(string=True):
        text = el.strip()
        if pattern.match(text):
            result = text
    return result

def resolve_final_url(url):
    """Resolve deep links by following redirects and parsing fallback HTML for final URL.

    Strategy:
    - Use a desktop User-Agent to encourage web fallback instead of app deep link.
    - Follow HTTP redirects normally.
    - If the resulting page contains meta refresh, canonical, or JS redirects, extract them.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
    }
    try:
        with requests.Session() as session:
            session.headers.update(headers)
            response = session.get(url, allow_redirects=True, timeout=20)
            final_url = response.url

            # If we already landed on a Strava web URL, return it
            if "strava.com" in final_url:
                return final_url

            # Parse HTML for potential meta refresh, canonical, or JS-based redirects
            content_type = response.headers.get("Content-Type", "")
            if "text/html" in content_type and response.text:
                soup = BeautifulSoup(response.text, 'html.parser')

                # 1) Meta refresh
                meta = soup.find('meta', attrs={'http-equiv': lambda v: v and v.lower() == 'refresh'})
                if meta and meta.get('content'):
                    content = meta['content']
                    # Format: "0; url=https://..."
                    parts = content.split('url=')
                    if len(parts) > 1:
                        candidate = parts[1].strip().strip('"\'')
                        if candidate:
                            return candidate

                # 2) Canonical link
                canonical = soup.find('link', rel=lambda v: v and 'canonical' in v)
                if canonical and canonical.get('href'):
                    return canonical['href']

                # 3) JS redirects (very simple regex search)
                import re
                js_redirect = re.search(r"window\.location(?:\.href)?\s*=\s*['\"]([^'\"]+)['\"]", response.text)
                if js_redirect:
                    return js_redirect.group(1)

            return final_url
    except requests.RequestException:
        return url

if __name__ == "__main__":
    with open("allathletes.txt", "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    with open("all_distance.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["athlete_name", "distance", "final_url"])

        for url in urls:
            final_url = resolve_final_url(url)
            response = requests.get(final_url, timeout=20)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Get athlete name
            name_tag = soup.find('h1', class_='athlete-name')
            if name_tag:
                name = name_tag.text.strip()
            else:
                # fallback: try title
                title = soup.find('title')
                if title:
                    name = title.text.split('|')[0].strip()
                else:
                    name = "Unknown"

            # Get this month's distance
            distance = find_elements_in_monthly_stats(soup)
            if distance:
                distance_val = distance.replace("km", "").strip()
            else:
                distance_val = ""

            writer.writerow([name, distance_val, final_url])
