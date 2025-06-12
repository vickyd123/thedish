from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import psycopg2
import requests
from bs4 import BeautifulSoup
import os
import json
import boto3
from dotenv import load_dotenv


load_dotenv()

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_REGION = os.environ.get('AWS_REGION', 'us-west-1')
S3_BUCKET = os.environ['S3_BUCKET']


app = Flask(__name__)

@app.route('/api/daily_digest')
def daily_digest():
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    filename = f"{yesterday}.txt"
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
    conn = get_db_conn()
    cur = conn.cursor()
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    # Determine minimum at-bats based on the number of days
    min_ab = 50 if days >= 30 else 20

    query = """
        SELECT player_id, player_name, team,
               SUM(hits) AS hits, SUM(at_bats) AS at_bats,
               SUM(home_runs) AS home_runs, SUM(rbi) AS rbi, SUM(runs) AS runs
        FROM baseballdb.player_daily_stats
        WHERE game_date >= %s
        GROUP BY player_id, player_name, team
        HAVING SUM(at_bats) >= %s
        ORDER BY (SUM(hits)::float / NULLIF(SUM(at_bats), 0)) DESC
        LIMIT 100
    """
    cur.execute(query, (since, min_ab))
    rows = cur.fetchall()

    trending = []
    for row in rows:
        hits = row[3] or 0
        at_bats = row[4] or 0
        avg = f"{(hits / at_bats):.3f}" if at_bats else ".000"
        trending.append({
            'player_id': row[0],
            'player_name': row[1],
            'team': row[2],
            'hits': hits,
            'at_bats': at_bats,
            'home_runs': row[5] or 0,
            'rbi': row[6] or 0,
            'runs': row[7] or 0,
            'avg': avg
        })

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

#this is all for batter vs pitcher

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

@app.route('/api/batter-vs-pitcher')
def batter_vs_pitcher():
    batter = request.args.get('batter')
    pitcher = request.args.get('pitcher')
    if not batter or not pitcher:
        return jsonify({"error": "Both batter and pitcher names are required."}), 400

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
                            "AVG": f"{avg:.3f}",
                            "OBP": f"{obp:.3f}",
                            "SLG": f"{slg:.3f}",
                            "OPS": f"{ops:.3f}"
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



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
