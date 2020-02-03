import requests as r
import re
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, HTML
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
import sys

def help():
    return """
DESCRIPCCION
Muestra datos estadisticos de los jugadores de la NBA
Kobe Bryant, LeBron James y Michael Jordan
        
    --playoffs:  Muestra los datos de playoffs
    --name=NAME:  Le pasamos el nombre del jugador que queremos
        ver las estadisticas
    --totals: Muetra datos totales
    -c: Muestra las estadisticas de las temporadas que el jugador gano el
        campeonato NBA
    -m: Muestra las estadisticas de las temporadas que el jugador fue
            Most Valuable Player  
    --graph: Muestra las estadisticas totales de la temporada 
        regular de todos los jugadores en forma de grafico
    --mailto=EMAIL: envia el grafico generado al email indicado
"""

def dataFrame(namePlayers):
    stats = pd.read_csv("allgames_stats.csv")
    stats.X = stats.X.apply(lambda x: "at" if x == "@" else "vs")
    del stats["GS"]
    del stats["GmSc"]
    for player in namePlayers:
        if player == "Lebron James":
            lebron2018 = statsSeason("lebron", "2018", "LAL")
            lebron2019 = statsSeason("lebron", "2019", "LAL")
            stats.append(lebron2018)
            stats.append(lebron2019)
    stats["Season"] = stats.Date.apply(season)
    players = stats.Player.drop_duplicates(keep="first").tolist()
    premios = [mvp_champion(i.replace(" ", "_")) for i in players]
    for i in range(0, len(premios)):
        premios[i]["mvp"] = season_award(premios[i]["mvp"])
        premios[i]["champion"] = season_award(premios[i]["champion"])
    listaPlayers = year_award(premios, stats)
    allStats = pd.concat([i for i in listaPlayers])
    return allStats

def who_win(game):
    if game["home_team"] == "LAL":
        return "L" if game["home_team_score"] < game["visitor_team_score"] else "W"
    else:
        return "L" if game["home_team_score"] > game["visitor_team_score"] else "W"

def find_team(team, teams):
    for i in teams:
        if i["abbreviation"] == team:
            return i["id"]

def all_games(games):
    valuesGame = [{
        "id": 0,
        "idGame": key["id"],
        "date": key["date"].split("T")[0],
        "home_team": key["home_team"]["abbreviation"],
        "home_team_score": key["home_team_score"],
        "visitor_team": key["visitor_team"]["abbreviation"],
        "visitor_team_score": key["visitor_team_score"],
        "competition": "Playoffs" if key["postseason"] else "Regular Season"
    } for key in games]
    return sorted(valuesGame, key=lambda x: x["date"])

def statsSeason(name, season, team):
    urlPlayer = f"https://www.balldontlie.io/api/v1/players?search={name}"
    dataPlayer = r.get(urlPlayer).json()
    player = {
        "id": dataPlayer["data"][0]["id"],
        "name": f"{dataPlayer['data'][0]['first_name']} {dataPlayer['data'][0]['last_name']}"
    }
    urlTeam = f"https://balldontlie.io/api/v1/teams"
    dataTeam = r.get(urlTeam).json()
    idTeam = find_team(team, dataTeam["data"])
    urlGames = f"https://balldontlie.io/api/v1/games?seasons[]={season}&per_page=100&team_ids[]={idTeam}"
    dataGames = r.get(urlGames).json()
    allGames = all_games(dataGames["data"])
    urlStats = f"https://balldontlie.io/api/v1/stats?player_ids[]={player['id']}&per_page=100"
    for i in range(0, len(allGames)):
        urlStats += f"&game_ids[]={allGames[i]['idGame']}"
    dataStats = r.get(urlStats).json()
    urlStats = f"https://balldontlie.io/api/v1/stats?player_ids[]={player['id']}&per_page=100"
    statsGames = list(zip(dataStats["data"], allGames))
    allStats = [{
        "G": i + 1,
        "Date": statsGames[i][1]["date"],
        "Tm": "LAL",
        "X": "vs" if statsGames[i][1]["home_team"] == "LAL" else "at",
        "Opp": statsGames[i][1]["home_team"] if statsGames[i][1]["home_team"] != "LAL" else statsGames[i][1]["visitor_team"],
        "Result": who_win(statsGames[i][1]),
        "MP": statsGames[i][0]["min"],
        "FG": statsGames[i][0]["fgm"],
        "FGA": statsGames[i][0]["fga"],
        "FG%": statsGames[i][0]["fg_pct"],
        "3P": statsGames[i][0]["fg3m"],
        "3PA": statsGames[i][0]["fg3a"],
        "3P%": statsGames[i][0]["fg3_pct"],
        "FT": statsGames[i][0]["ftm"],
        "FTA": statsGames[i][0]["fta"],
        "FT%": statsGames[i][0]["ft_pct"],
        "ORB": statsGames[i][0]["oreb"],
        "DRB": statsGames[i][0]["dreb"],
        "TRB": statsGames[i][0]["reb"],
        "AST": statsGames[i][0]["ast"],
        "STL": statsGames[i][0]["stl"],
        "BLK": statsGames[i][0]["blk"],
        "TOV": statsGames[i][0]["turnover"],
        "PF": statsGames[i][0]["pf"],
        "PTS": statsGames[i][0]["pts"],
        "Player": player["name"],
        "RSorPO": statsGames[i][1]["competition"]
    } for i in range(0, len(statsGames))]
    return allStats

def season(date):
    listDate = date.split("-")
    return f"{int(listDate[0]) - 1}/{listDate[0]}" if int(listDate[1]) <= 6 else f"{listDate[0]}/{int(listDate[0]) + 1}"

def mvp_champion(name):
    names = {
        "lebron_james": "Lebron_James",
        "michael_jordan": "Michael_Jordan",
        "kobe_bryant": "Kobe_Bryant"
    }
    urlMvp = f"https://en.wikipedia.org/wiki/{names[name.lower()]}"
    mvpData = r.get(urlMvp).text
    soupMvp = BeautifulSoup(mvpData, 'html.parser')
    mvpTable = soupMvp.find_all("table", {"class": "infobox vcard"})[0]
    mvpTableData = mvpTable.find_all("li")
    mvp = []
    champion = []
    year = ""
    for i in range(0, 3, 2):
        if i == 2:
            listaMvp = re.findall(r"\d{4}", mvpTableData[i].text)
            for z in listaMvp:
                mvp.append(z)
        lines = mvpTableData[i].text.split(" ")
        for e in lines:
            if "(" in e or ")" in e or ",":
                if "–" in e:
                    year = e[1:-1] if "(" in e else e[0:-1]
                    years = year.split("–")
                    for x in range(int(years[0]), int(years[1]) + 1):
                        champion.append(str(x))
                else:
                    listaChampion = re.findall(r"\d{4}", e)
                    for j in listaChampion:
                        champion.append(j)
    for i in range(0, len(champion)):
        if int(champion[i]) > int(champion[i+1]):
            champion = champion[0: i+1]
            break
    return {
        "player": names[name.lower()],
        "mvp": mvp,
        "champion": champion
    }

def season_award(awards):
    litaAwards = [f"{int(i) - 1}/{i}" for i in awards]
    return litaAwards

def year_award(premios, stats):
    listPlayers = []
    for i in range(0, len(premios)):
        player = stats.loc[stats.Player == premios[i]["player"].replace("_", " ")]
        playerAward = premios[i]
        playerSeason = player.Season.tolist()
        playerMvpYear = ["Y" if i in playerAward["mvp"] else "N" for i in playerSeason]
        playerChampionYear = ["Y" if i in playerAward["champion"] else "N" for i in playerSeason]
        player.insert(len(player.columns), column="MVP", value=playerMvpYear)
        player.insert(len(player.columns), column="NBA_Champion", value=playerChampionYear)
        listPlayers.append(player)
    return listPlayers

def simpleStats(stats, name, playoffs, mvp, champion, totals):
    namePlayer = {
        "kobe": "Kobe Bryant",
        "jordan": "Michael Jordan",
        "lebron": "Lebron James"
    }
    player = stats[stats.Player == namePlayer[name[0]]]
    if champion:
        if totals:
            if playoffs:
                playerStats = player[(player["RSorPO"] == "Playoffs") & (player["NBA_Champion"] == "Y")]
                points = playerStats.PTS.sum()
                assists = playerStats.AST.sum()
                rebound = playerStats.TRB.sum()
                return points, assists, rebound
            else:
                playerStats = player[(player["RSorPO"] == "Regular Season") & (player["NBA_Champion"] == "Y")]
                points = playerStats.PTS.sum()
                assists = playerStats.AST.sum()
                rebound = playerStats.TRB.sum()
                return points, assists, rebound
        else:
            if playoffs:
                playerStats = player[(player["RSorPO"] == "Playoffs") & (player["NBA_Champion"] == "Y")]
                points = playerStats.PTS.mean()
                assists = playerStats.AST.mean()
                rebound = playerStats.TRB.mean()
                return points, assists, rebound
            else:
                playerStats = player[(player["RSorPO"] == "Regular Season") & (player["NBA_Champion"] == "Y")]
                points = playerStats.PTS.mean()
                assists = playerStats.AST.mean()
                rebound = playerStats.TRB.mean()
                return points, assists, rebound
    else:
        if totals:
            if mvp:
                if playoffs:
                    playerStats = player[(player["RSorPO"] == "Playoffs") & (player["MVP"] == "Y")]
                    points = playerStats.PTS.sum()
                    assists = playerStats.AST.sum()
                    rebound = playerStats.TRB.sum()
                    return points, assists, rebound
                else:
                    playerStats = player[(player["RSorPO"] == "Regular Season") & (player["MVP"] == "Y")]
                    points = playerStats.PTS.sum()
                    assists = playerStats.AST.sum()
                    rebound = playerStats.TRB.sum()
                    return points, assists, rebound
            else:
                if playoffs:
                    playerStats = player[(player["RSorPO"] == "Playoffs")]
                    points = playerStats.PTS.sum()
                    assists = playerStats.AST.sum()
                    rebound = playerStats.TRB.sum()
                    return points, assists, rebound
                else:
                    playerStats = player[(player["RSorPO"] == "Regular Season")]
                    points = playerStats.PTS.sum()
                    assists = playerStats.AST.sum()
                    rebound = playerStats.TRB.sum()
                    return points, assists, rebound
        else:
            if mvp:
                if playoffs:
                    playerStats = player[(player["RSorPO"] == "Playoffs") & (player["MVP"] == "Y")]
                    points = playerStats.PTS.mean()
                    assists = playerStats.AST.mean()
                    rebound = playerStats.TRB.mean()
                    return points, assists, rebound
                else:
                    playerStats = player[(player["RSorPO"] == "Regular Season") & (player["MVP"] == "Y")]
                    points = playerStats.PTS.mean()
                    assists = playerStats.AST.mean()
                    rebound = playerStats.TRB.mean()
                    return points, assists, rebound
            else:
                if playoffs:
                    playerStats = player[(player["RSorPO"] == "Playoffs")]
                    points = playerStats.PTS.mean()
                    assists = playerStats.AST.mean()
                    rebound = playerStats.TRB.mean()
                    return points, assists, rebound
                else:
                    playerStats = player[(player["RSorPO"] == "Regular Season")]
                    points = playerStats.PTS.mean()
                    assists = playerStats.AST.mean()
                    rebound = playerStats.TRB.mean()
                    return points, assists, rebound

def graphs(stats, playoffs, email, emailto):
    if playoffs:
        tabla = stats[stats["RSorPO"] == "Playoffs"].groupby('Player').agg({'PTS': 'sum', 'AST': 'sum', "TRB": "sum"})
        plot = tabla.plot(kind="bar", title="Total Stats")
        fig = plot.get_figure()
        fig.savefig("totalStats.png")
    else:
        tabla = stats[stats["RSorPO"] == "Regular Season"].groupby('Player').agg({'PTS': 'sum', 'AST': 'sum', "TRB": "sum"})
        plot = tabla.plot(kind="bar", title="Total Stats")
        fig = plot.get_figure()
        fig.savefig("totalStats.png")
    if email:
        send_email(emailto)

def send_email(emailto):
    strFrom = "eduman13pruebas@gmail.com"
    strTo = emailto

    msgRoot = MIMEMultipart("related")
    msgRoot["Subject"] = "Total Stats"
    msgRoot["From"] = strFrom
    msgRoot["To"] = strTo
    msgRoot.preamble = "This is a multi-part message in MIME format."
    msgAlternative = MIMEMultipart("alternative")
    msgRoot.attach(msgAlternative)

    msgText = MIMEText("This is the alternative plain text message.")
    msgAlternative.attach(msgText)

    template = """
        <b>Puntos, asistencias y rebotes de Kobe, LeBron y Jordan </b><br>
        <img src=cid:image1>
        <br>
        <br>
        </br>
        Siempre te recordaremos. <b>MAMBA OUT!!!</b>
        <br>
        </br>
        <br>
        <img src=https://phhstrailblazer.org/wp-content/uploads/2016/01/Kobe-Bryant-480x480.png>
        </br>
    """
    msgText = MIMEText(template, "html")
    msgAlternative.attach(msgText)

    fp = open("totalStats.png", "rb")
    msgImage = MIMEImage(fp.read())
    fp.close()

    msgImage.add_header("Content-ID", "<image1>")
    msgRoot.attach(msgImage)

    email_server_host = "smtp.gmail.com"
    port = 587
    server = smtplib.SMTP(email_server_host, port)
    server.ehlo()
    server.starttls()
    server.login(strFrom, "ironhack123")
    server.sendmail(strFrom, strTo, msgRoot.as_string())
    server.close()





#https://phhstrailblazer.org/wp-content/uploads/2016/01/Kobe-Bryant-480x480.png
