import requests
from flask import Blueprint, request, jsonify

bp = Blueprint('batter_vs_pitcher', __name__)

def is_hit(result):
    return result in ["Single", "Double", "Triple", "Home Run"]

def total_bases(result):
    return {"Single": 1, "Double": 2, "Triple": 3, "Home Run": 4}.get(result, 0)

def is_walk(result):
    return result in ["Walk", "Intentional Walk"]

def is_hbp(result):
    return result == "Hit By Pitch"

def is_sacrifice(result):
    return result in ["Sacrifice Fly", "Sacrifice Bunt"]

def is_valid_pa(result):
    return not is_sacrifice(result)

def is_ab(result):
    return not (is_walk(result) or is_hbp(result) or is_sacrifice(result) or result == "Catcher Interference")

@bp.route('/batter-vs-pitcher', methods=['GET'])
def batter_vs_pitcher():
    batter = request.args.get('batter')
    pitcher = request.args.get('pitcher')
    if not batter or not pitcher:
        return jsonify({"error": "Both batter and pitcher names are required"}), 400

    url = f"https://doinksports.com/research/mlb/batter-vs-pitcher?batter={batter.replace(' ', '+')}&pitcher={pitcher.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        plate_logs_header = soup.find(lambda tag: tag.name == "h3" and "Plate Appearance Logs" in tag.text)
        if plate_logs_header:
            table = plate_logs_header.find_next("table")
            if table:
                rows = table.find_all("tr")[1:]
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

                    result = cols[3]

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
                    return jsonify({"error": "No valid plate appearances found."}), 404
                else:
                    avg = hits / ab if ab else 0
                    obp = (hits + walks + hbp) / pa
                    slg = total_bases_sum / ab if ab else 0
                    ops = obp + slg

                    return jsonify({
                        "batter": batter,
                        "pitcher": pitcher,
                        "stats": {
                            "PA": pa,
                            "AB": ab,
                            "H": hits,
                            "BB": walks,
                            "HBP": hbp,
                            "AVG": round(avg, 3),
                            "OBP": round(obp, 3),
                            "SLG": round(slg, 3),
                            "OPS": round(ops, 3)
                        }
                    })
            else:
                return jsonify({"error": "Table not found after Plate Appearance Logs header."}), 404
        else:
            return jsonify({"error": "Plate Appearance Logs header not found."}), 404
    except requests.HTTPError as e:
        return jsonify({"error": f"HTTP Error: {e.response.status_code}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500