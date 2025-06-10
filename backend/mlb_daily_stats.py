import requests
import psycopg2
from datetime import datetime, timedelta

def get_db_conn():
    # For security, consider using environment variables or a .env file in production!
    return psycopg2.connect(
        host="baseball-db.cbc0qowcmrna.us-west-1.rds.amazonaws.com",
        dbname="postgres",
        user="postgres",
        password="Federals123$",
        port=5432
    )

def fetch_game_ids(game_date):
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={game_date}"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    game_ids = []
    for date_info in data.get('dates', []):
        for game in date_info.get('games', []):
            game_ids.append(game['gamePk'])
    return game_ids

def fetch_boxscore(game_id):
    url = f"https://statsapi.mlb.com/api/v1/game/{game_id}/boxscore"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def extract_batter_stats(boxscore, game_date):
    stats = []
    for team_type in ['home', 'away']:
        team = boxscore['teams'][team_type]
        players = team['players']
        for pid, pdata in players.items():
            bat = pdata.get('stats', {}).get('batting')
            if bat:
                stats.append({
                    'player_id': pid,
                    'player_name': pdata['person']['fullName'],
                    'team': team['team']['name'],
                    'game_date': game_date,
                    'hits': bat.get('hits', 0),
                    'at_bats': bat.get('atBats', 0),
                    'home_runs': bat.get('homeRuns', 0),
                    'rbi': bat.get('rbi', 0),
                    'runs': bat.get('runs', 0),
                    'walks': bat.get('baseOnBalls', 0),
                    'strikeouts': bat.get('strikeOuts', 0)
                })
    return stats

def store_stats(stats, conn):
    if not stats:
        print("No stats to store.")
        return
    cur = conn.cursor()
    for row in stats:
        cur.execute("""
            INSERT INTO baseballdb.player_daily_stats (
                player_id, player_name, team, game_date, hits, at_bats, home_runs, rbi, runs, walks, strikeouts
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (player_id, game_date) DO NOTHING
        """, (
            row['player_id'], row['player_name'], row['team'], row['game_date'],
            row['hits'], row['at_bats'], row['home_runs'], row['rbi'],
            row['runs'], row['walks'], row['strikeouts']
        ))
    conn.commit()
    cur.close()
    print(f"Stored {len(stats)} player records.")

def fetch_and_store_for_date(game_date, conn):
    print(f"Fetching games for {game_date}...")
    game_ids = fetch_game_ids(game_date)
    print(f"Found {len(game_ids)} games.")
    all_stats = []
    for game_id in game_ids:
        print(f"Fetching boxscore for game {game_id}...")
        boxscore = fetch_boxscore(game_id)
        stats = extract_batter_stats(boxscore, game_date)
        all_stats.extend(stats)
    print(f"Storing {len(all_stats)} player records...")
    store_stats(all_stats, conn)

if __name__ == "__main__":
    try:
        conn = get_db_conn()
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        fetch_and_store_for_date(date, conn)
        conn.close()
        print(f"Success for {date}")
    except Exception as e:
        print(f"Error: {e}")
