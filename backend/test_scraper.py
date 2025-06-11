import requests
from bs4 import BeautifulSoup

def is_hit(result):
    return result in ["Single", "Double", "Triple", "Home Run"]

def total_bases(result):
    if result == "Single":
        return 1
    elif result == "Double":
        return 2
    elif result == "Triple":
        return 3
    elif result == "Home Run":
        return 4
    else:
        return 0

def is_walk(result):
    return result in ["Walk", "Intentional Walk"]

def is_hbp(result):
    return result == "Hit By Pitch"

def is_sacrifice(result):
    return result in ["Sacrifice Fly", "Sacrifice Bunt"]

def is_valid_pa(result):
    # Countable plate appearances (exclude sacrifices)
    return not is_sacrifice(result)

def is_ab(result):
    # ABs exclude Walks, HBP, Sacrifices, Catcher Interference
    return not (is_walk(result) or is_hbp(result) or is_sacrifice(result) or result == "Catcher Interference")

batter = input("Enter batter name (e.g., Heliot Ramos): ")
pitcher = input("Enter pitcher name (e.g., Bryan Woo): ")

url = f"https://doinksports.com/research/mlb/batter-vs-pitcher?batter={batter.replace(' ', '+')}&pitcher={pitcher.replace(' ', '+')}"
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Extract Plate Appearance Logs table
plate_logs_header = soup.find(lambda tag: tag.name == "h3" and "Plate Appearance Logs" in tag.text)
if plate_logs_header:
    table = plate_logs_header.find_next("table")
    if table:
        rows = table.find_all("tr")[1:]  # Skip header row
        pa = 0
        ab = 0
        hits = 0
        walks = 0
        hbp = 0
        total_bases_sum = 0

        for row in rows:
            cols = [col.get_text(strip=True) for col in row.find_all("td")]
            if not cols or len(cols) < 6:
                continue

            result = cols[3]  # assuming 4th column is 'Result'

            if is_valid_pa(result):
                pa += 1
            if is_ab(result):
                ab += 1
            if is_hit(result):
                hits += 1
            if is_walk(result):
                walks += 1
            if is_hbp(result):
                hbp += 1

            total_bases_sum += total_bases(result)

        if pa == 0:
            print("No valid plate appearances found.")
        else:
            avg = hits / ab if ab else 0
            obp = (hits + walks + hbp) / pa
            slg = total_bases_sum / ab if ab else 0
            ops = obp + slg

            print(f"\nStats for {batter} vs {pitcher}:")
            print(f"PA: {pa}, AB: {ab}, H: {hits}, BB: {walks}, HBP: {hbp}")
            print(f"AVG: {avg:.3f}")
            print(f"OBP: {obp:.3f}")
            print(f"SLG: {slg:.3f}")
            print(f"OPS: {ops:.3f}")
    else:
        print("Table not found after Plate Appearance Logs header.")
else:
    print("Plate Appearance Logs header not found.")

