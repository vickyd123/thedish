from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import psycopg2
import os
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
    cur.execute("""
        SELECT player_id, player_name, team,
               SUM(hits) AS hits, SUM(at_bats) AS at_bats,
               SUM(home_runs) AS home_runs, SUM(rbi) AS rbi, SUM(runs) AS runs
        FROM baseballdb.player_daily_stats
        WHERE game_date >= %s
        GROUP BY player_id, player_name, team
        HAVING SUM(at_bats) >= 20
        ORDER BY (SUM(hits)::float / NULLIF(SUM(at_bats),0)) DESC
    """, (since,))
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

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
