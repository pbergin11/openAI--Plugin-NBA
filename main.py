import json
import requests
import urllib.parse
import os

import quart
import quart_cors
from quart import request

import datetime


# Note: Setting CORS to allow chat.openapi.com is only required when running a localhost plugin
app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

#@app.get("/team_ID_by_Name")
# Gets team ID from Database key teams_data
#def get_team_id_by_name(full_name):
#    teams_data = db.get("teams_data")
#    if teams_data:
#        for team in teams_data["data"]:
#            if team["full_name"] == full_name:
#                return team["id"]
#    return None


# Gets team ID from Database key teams_data
#def get_team_abv_by_name(full_name):
#    teams_data = db.get("teams_data")
#    if teams_data:
#        for team in teams_data["data"]:
#            if team["full_name"] == full_name:
#                return team["abbreviation"]
#    return None

def get_filtered_roster(roster):
    filtered_roster = []
    keys_to_keep = ["Team", "Jersey", "PositionCategory", "Position", "FirstName", "LastName",
                    "BirthDate", "BirthCity", "BirthState", "BirthCountry", "Height", "Weight"]

    for player in roster:
        filtered_player = {key: player[key] for key in keys_to_keep}
        filtered_roster.append(filtered_player)

    return filtered_roster

def filter_game_data(game):
    return {
        "GameEndDateTime": game["GameEndDateTime"],
        "GameID": game["GameID"],
        "Season": game["Season"],
        "SeasonType": game["SeasonType"],
        "Status": game["Status"],
        "Day": game["Day"],
        "DateTime": game["DateTime"],
        "AwayTeam": game["AwayTeam"],
        "HomeTeam": game["HomeTeam"],
        "AwayTeamID": game["AwayTeamID"],
        "HomeTeamID": game["HomeTeamID"],
        "StadiumID": game["StadiumID"],
        "AwayTeamScore": game["AwayTeamScore"],
        "HomeTeamScore": game["HomeTeamScore"],
        "Updated": game["Updated"],
        "IsClosed": game["IsClosed"],
        "NeutralVenue": game["NeutralVenue"],
        "DateTimeUTC": game["DateTimeUTC"],
    }

@app.get("/player_stats")
# Get all players stats
def get_player_stats(player_id, year):
    url = "https://www.balldontlie.io/api/v1/season_averages?player_ids[]={}&season={}".format(player_id, year)
    response = requests.get(url)
    data = response.json()["data"]
    if data:
        return data[0]
    else:
        return None


@app.get("/current_games")
def get_current_games():
    current_date = datetime.date.today()
    api_url_today = f"https://api.sportsdata.io/v3/nba/scores/json/ScoresBasic/{current_date}?key=48a287166d5d4ecabd71c344439ee80c"
    response = requests.get(api_url_today)
    raw_scores = response.json()
    if "HttpStatusCode" in raw_scores and raw_scores["HttpStatusCode"] == 400:
        print(f"Error: {raw_scores['Description']}")
        current_scores = "No games found"
    else:
        current_scores = {
            "Season": raw_scores["Season"],
            "Status": raw_scores["Status"],
            "Day": raw_scores["Day"],
            "DateTime": raw_scores["DateTime"],
            "AwayTeam": raw_scores["AwayTeam"],
            "HomeTeam": raw_scores["HomeTeam"],
            "AwayTeamScore": raw_scores["AwayTeamScore"],
            "HomeTeamScore": raw_scores["HomeTeamScore"],
            "Updated": raw_scores["Updated"],
        }
    return quart.Response(response=json.dumps(current_scores), status=200)


@app.get("/year_standings")
def get_standings():
    year = request.args.get("year")
    api_url_today = f"https://api.sportsdata.io/v3/nba/scores/json/Standings/{year}?key=48a287166d5d4ecabd71c344439ee80c"
    response = requests.get(api_url_today)
    raw_standings = response.json()
    standings = []

    if "HttpStatusCode" in raw_standings and raw_standings["HttpStatusCode"] == 400:
        print(f"Error: {raw_standings['Description']}")
        standings = "No standings found"
    else:
        for team in raw_standings:
            standings = {
                "Season": team["Season"],
                "City": team["City"],
                "Name": team["Name"],
                "Conference": team["Conference"],
                "Division": team["Division"],
                "Wins": team["Wins"],
                "Losses": team["Losses"],
                "Percentage": team["Percentage"],
                "ConferenceWins": team["ConferenceWins"],
                "ConferenceLosses": team["ConferenceLosses"],
                "DivisionWins": team["DivisionWins"],
                "DivisionLosses": team["DivisionLosses"],
                "HomeWins": team["HomeWins"],
                "HomeLosses": team["HomeLosses"],
                "AwayWins": team["AwayWins"],
                "AwayLosses": team["AwayLosses"],
                "LastTenWins": team["LastTenWins"],
                "LastTenLosses": team["LastTenLosses"],
                "PointsPerGameFor": team["PointsPerGameFor"],
                "PointsPerGameAgainst": team["PointsPerGameAgainst"],
                "Streak": team["Streak"],
                "GamesBack": team["GamesBack"],
                "StreakDescription": team["StreakDescription"],
                "ConferenceRank": team["ConferenceRank"],
                "DivisionRank": team["DivisionRank"],
            }
    return quart.Response(response=json.dumps(standings), status=200)


def main():
    app.run(debug=True, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()

