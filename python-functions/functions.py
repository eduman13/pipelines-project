def who_win(game):
    if game["home_team"] == "LAL":
        return "L" if game["home_team_score"] < game["visitor_team_score"] else "W"
    else:
        return "L" if game["home_team_score"] > game["visitor_team_score"] else "W"