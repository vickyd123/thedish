from flask import Flask, request, jsonify
from datetime import datetime, timedelta, timezone
import psycopg2
import requests
from bs4 import BeautifulSoup
import os
import json
import boto3
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv
from zoneinfo import ZoneInfo



load_dotenv()

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_REGION = os.environ.get('AWS_REGION', 'us-west-1')
S3_BUCKET = os.environ['S3_BUCKET']


app = Flask(__name__)

@app.route('/api/daily_digest')
def daily_digest():
    pdt = ZoneInfo("America/Los_Angeles")
    now = datetime.now(pdt)
    yesterday = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    filename = f"{yesterday}.txt"
    print(filename)
    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET]):
        return jsonify({"digest": "Server misconfiguration: AWS credentials or bucket missing."}), 500
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=filename)
        digest = obj['Body'].read().decode('utf-8')
        return jsonify({"digest": digest})
    except s3.exceptions.NoSuchKey:
        return jsonify({"digest": "Digest not yet available."}), 404
    except NoCredentialsError:
        return jsonify({"digest": "AWS credentials not found."}), 500
    except ClientError as e:
        return jsonify({"digest": f"Error accessing S3: {str(e)}"}), 500

@app.route('/api/daily_trivia')
def daily_trivia():
    # S3 setup (reuse your existing S3 config)
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    try:
        # Download the JSON file from S3
        obj = s3.get_object(Bucket=S3_BUCKET, Key='trivia_questions.json')
        questions = json.loads(obj['Body'].read().decode('utf-8'))
        # Pick today's question (cycle through if more than 100 days)
        day_of_year = (datetime.now().timetuple().tm_yday - 1) % len(questions)
        question = questions[day_of_year]
        return jsonify(question)
    except s3.exceptions.NoSuchKey:
        return jsonify({"error": "Trivia questions file not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

def get_db_conn():
    # Edit these with your actual DB credentials or use env vars
    return psycopg2.connect(
        host="baseball-db.cbc0qowcmrna.us-west-1.rds.amazonaws.com",
        dbname="postgres",
        user="postgres",
        password="Federals123$",
        port=5432
    )

@app.route('/api/search_player')
def search_player():
    name = request.args.get('name', '').strip()
    if not name:
        return jsonify([])
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT player_id, player_name, team
        FROM baseballdb.player_daily_stats
        WHERE LOWER(player_name) LIKE %s
        ORDER BY player_name
        LIMIT 20
    """, ('%' + name.lower() + '%',))
    results = [{'player_id': r[0], 'player_name': r[1], 'team': r[2]} for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(results)

@app.route('/api/whos_hot/<int:days>')
def whos_hot(days):
    sort_by = request.args.get('sort', 'avg')
    print(f"DEBUG: sort_by = '{sort_by}'")  # Debug line
    
    conn = get_db_conn()
    cur = conn.cursor()
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    min_ab = 50 if days >= 30 else 20

    query = """
        SELECT player_id, player_name, team,
               SUM(hits) AS hits, SUM(at_bats) AS at_bats,
               SUM(home_runs) AS home_runs, SUM(rbi) AS rbi, SUM(runs) AS runs
        FROM baseballdb.player_daily_stats
        WHERE game_date >= %s
        GROUP BY player_id, player_name, team
    """
    params = [since]

    # Only filter by min AB if sorting by AVG
    if sort_by == 'avg':
        query += " HAVING SUM(at_bats) >= %s"
        params.append(min_ab)
        print(f"DEBUG: Added HAVING clause with min_ab = {min_ab}")  # Debug line
    else:
        print("DEBUG: No HAVING clause added")  # Debug line

    # Sorting logic
    sort_map = {
        'avg': "(SUM(hits)::float / NULLIF(SUM(at_bats), 0)) DESC",
        'home_runs': "SUM(home_runs) DESC",
        'rbi': "SUM(rbi) DESC",
        'hits': "SUM(hits) DESC",
        'at_bats': "SUM(at_bats) DESC"
    }
    order_by = sort_map.get(sort_by, sort_map['avg'])
    query += f" ORDER BY {order_by} LIMIT 3000"
    
    print(f"DEBUG: Final query = {query}")  # Debug line
    print(f"DEBUG: Params = {params}")  # Debug line

    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    
    print(f"DEBUG: Found {len(rows)} total rows")  # Debug line

    trending = []
    for row in rows:
        hits = row[3] or 0
        at_bats = row[4] or 0
        avg = f"{(hits / at_bats):.3f}" if at_bats else None
        player_dict = {
            'player_id': row[0],
            'player_name': row[1],
            'team': row[2],
            'hits': hits,
            'at_bats': at_bats,
            'home_runs': row[5] or 0,
            'rbi': row[6] or 0,
            'runs': row[7] or 0,
            'avg': avg
        }
        trending.append(player_dict)

    # Check if Casey Schmitt is in the results
    casey_schmitt = [p for p in trending if 'Casey Schmitt' in p['player_name']]
    if casey_schmitt:
        print(f"DEBUG: Casey Schmitt found: {casey_schmitt[0]}")
    else:
        print("DEBUG: Casey Schmitt NOT found in results")

    cur.close()
    conn.close()
    return jsonify(trending)

@app.route('/api/player_stats/<player_id>')
def player_stats(player_id):
    days = request.args.get('days', '7')
    conn = get_db_conn()
    cur = conn.cursor()
    if days == 'season':
        cur.execute("""
            SELECT
                player_name,
                team,
                SUM(hits) as hits,
                SUM(at_bats) as at_bats,
                SUM(home_runs) as home_runs,
                SUM(rbi) as rbi,
                SUM(walks) as walks
            FROM baseballdb.player_daily_stats
            WHERE player_id = %s
            GROUP BY player_name, team
        """, (player_id,))
    else:
        days_int = int(days)
        since = (datetime.now() - timedelta(days=days_int)).strftime("%Y-%m-%d")
        cur.execute("""
            SELECT
                player_name,
                team,
                SUM(hits) as hits,
                SUM(at_bats) as at_bats,
                SUM(home_runs) as home_runs,
                SUM(rbi) as rbi,
                SUM(walks) as walks
            FROM baseballdb.player_daily_stats
            WHERE player_id = %s AND game_date >= %s
            GROUP BY player_name, team
        """, (player_id, since))
    rows = cur.fetchall()
    results = []
    for row in rows:
        hits = row[2] or 0
        at_bats = row[3] or 0
        home_runs = row[4] or 0
        rbi = row[5] or 0
        walks = row[6] or 0
        avg = f"{(hits / at_bats):.3f}" if at_bats else ".000"
        obp_denom = at_bats + walks
        obp = f"{((hits + walks) / obp_denom):.3f}" if obp_denom else ".000"
        results.append({
            "player_name": row[0],
            "team": row[1],
            "hits": hits,
            "at_bats": at_bats,
            "home_runs": home_runs,
            "rbi": rbi,
            "walks": walks,
            "avg": avg,
            "obp": obp
        })
    cur.close()
    conn.close()
    if not results:
        return jsonify({})
    elif len(results) == 1:
        return jsonify(results[0])
    else:
        return jsonify(results)
    
@app.route('/health')
def health():
    return jsonify({"status": "ok"})

def is_valid_pa(result): return result.strip() and result.strip().lower() != "no play"
def is_ab(result): return is_valid_pa(result) and not result.lower().startswith("walk") and not result.lower().startswith("hit by pitch") and not result.lower().startswith("sacrifice")
def is_hit(result): return any(word in result.lower() for word in ["single", "double", "triple", "home run"])
def is_walk(result): return result.lower().startswith("walk")
def is_hbp(result): return result.lower().startswith("hit by pitch")
def total_bases(result):
    if "single" in result.lower(): return 1
    elif "double" in result.lower(): return 2
    elif "triple" in result.lower(): return 3
    elif "home run" in result.lower(): return 4
    return 0

@app.route('/api/batter-vs-pitcher')
def batter_vs_pitcher():
    batter = request.args.get('batter')
    pitcher = request.args.get('pitcher')
    if not batter or not pitcher:
        return jsonify({"error": "Both batter and pitcher names are required."}), 400

    url = f"https://doinksports.com/research/mlb/batter-vs-pitcher?batter={batter.replace(' ', '+')}&pitcher={pitcher.replace(' ', '+')}"

    # Set up Selenium options
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0")

    # Specify the path to your ChromeDriver (adjust as needed)
    service = Service('C:\\Users\\victo\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)

    try:
        print(f"Requesting URL with Selenium: {url}")
        driver.get(url)
        time.sleep(2)  # Wait for JavaScript to load
        html = driver.page_source
        print(f"Page source length: {len(html)}")

        soup = BeautifulSoup(html, "html.parser")
        plate_logs_header = soup.find(lambda tag: tag.name == "h3" and "Plate Appearance Logs" in tag.text)
        if plate_logs_header:
            print("Found Plate Appearance Logs header")
            table = plate_logs_header.find_next("table")
            if table:
                print("Found table after Plate Appearance Logs header")
                rows = table.find_all("tr")[1:]
                print(f"Found {len(rows)} rows in table")

                pa = 0
                ab = 0
                hits = 0
                walks = 0
                hbp = 0
                total_bases_sum = 0

                for row in rows:
                    cols = [col.get_text(strip=True) for col in row.find_all("td")]
                    print("\nRow:", cols)
                    if not cols or len(cols) < 6:
                        print("Skipping row (not enough columns)")
                        continue

                    result = cols[3]
                    print("Result:", result)

                    valid_pa = is_valid_pa(result)
                    ab_flag = is_ab(result)
                    hit_flag = is_hit(result)
                    walk_flag = is_walk(result)
                    hbp_flag = is_hbp(result)
                    tb = total_bases(result)

                    print(f"is_valid_pa: {valid_pa}")
                    print(f"is_ab: {ab_flag}")
                    print(f"is_hit: {hit_flag}")
                    print(f"is_walk: {walk_flag}")
                    print(f"is_hbp: {hbp_flag}")
                    print(f"total_bases: {tb}")

                    if valid_pa:
                        pa += 1
                    if ab_flag:
                        ab += 1
                    if hit_flag:
                        hits += 1
                    if walk_flag:
                        walks += 1
                    if hbp_flag:
                        hbp += 1
                    total_bases_sum += tb

                print(f"\nFinal counts - PA: {pa}, AB: {ab}, H: {hits}, BB: {walks}, HBP: {hbp}, Total Bases: {total_bases_sum}")

                if pa == 0:
                    return jsonify({"error": "No valid plate appearances found."}), 404
                else:
                    avg = hits / ab if ab else 0
                    obp = (hits + walks + hbp) / pa
                    slg = total_bases_sum / ab if ab else 0
                    ops = obp + slg

                    print(f"Calculated stats - AVG: {avg:.3f}, OBP: {obp:.3f}, SLG: {slg:.3f}, OPS: {ops:.3f}")

                    return jsonify({
                        "batter": batter,
                        "pitcher": pitcher,
                        "stats": {
                            "PA": pa,
                            "AB": ab,
                            "H": hits,
                            "BB": walks,
                            "HBP": hbp,
                            "AVG": f"{avg:.3f}",
                            "OBP": f"{obp:.3f}",
                            "SLG": f"{slg:.3f}",
                            "OPS": f"{ops:.3f}"
                        }
                    })
            else:
                print("No table found after Plate Appearance Logs header")
                return jsonify({"error": "Table not found after Plate Appearance Logs header."}), 404
        else:
            print("Plate Appearance Logs header not found")
            return jsonify({"error": "Plate Appearance Logs header not found."}), 404
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        driver.quit()



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
