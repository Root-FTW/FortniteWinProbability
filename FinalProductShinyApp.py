import sys
import re
import os
import datetime
import pandas as pd

# Leemos los nombres desde el archivo names.txt
with open(r"C:\Users\rootf\Downloads\Compressed\FortniteWinProbability-main\FortniteWinProbability-main\names.txt", 'r', encoding='utf-8') as f:
    player_names = [line.strip() for line in f]

# Generamos el DataFrame con los nombres de los jugadores
df = pd.DataFrame(player_names, columns=['player_name'])

# A continuación, comienza la parte de API Connect, deja todo igual a partir de aquí

import json
import requests
import pandas as pd

url = 'https://fortnite-api.com/v2/stats/br/v2'

account_types = ['epic'] #, 'xbl', 'psn'

headers = dict(
    Authorization = 'YOUR API KEY'
)

data_rows = []
for name in player_names:
    found = False
    for account_type in account_types:
        params = dict(
            name=name,
            AccountType=account_type,
            timeWindow='lifetime',
            image='none'
        )
        data = requests.get(url=url, params=params, headers=headers)
        if data.status_code == 200:
            data_json = data.json()
            # get player stats
            indent1_stats = data_json["data"]
            indent2_stats = indent1_stats['stats']
            indent3_stats = indent2_stats['all']
            indent4_stats = indent3_stats['solo']

            # This is the unique players solo data
            # df = pd.DataFrame(d.indent4_stats(), columns=['group', 'value'])
            df_stats = pd.DataFrame([indent4_stats])
            df_stats = df_stats.rename_axis("group").reset_index()
            df_stats['player_name'] = name
            df_stats['status'] = 'public'
            data_rows.append(df_stats)
            found = True
            break
    if not found:
        df_stats = pd.DataFrame({'player_name': [name], 'status': ['private']})
        data_rows.append(df_stats)

if data_rows:
    df_stats = pd.concat(data_rows)

    # left join df stats on df
    merged_df = pd.merge(df, df_stats, on="player_name", how="inner")
else:
    print("No player data found")
    sys.exit()

unique_df = merged_df.drop_duplicates()


unique_df['match_number'] = 1

# MONTE CARLO SIMULATION

## Get player and skill measure
import numpy as np

latest_match = unique_df[unique_df["match_number"] == unique_df["match_number"].max()]
#latest_match = latest_match[["player_name", "kd"]]
latest_match = latest_match.loc[:, ["player_name", "kd"]][~latest_match["kd"].isna()]
latest_match = latest_match.reset_index(drop=True)

## Get the overall outcome of the match based on skill


# Define a function to simulate a game
def simulate_game(kd1, kd2):
    p1_score = np.random.normal(kd1, 1)
    p2_score = np.random.normal(kd2, 1)
    if p1_score > p2_score:
        return 1
    else:
        return 2



def overall_rankings(latest_match):
    # Create a DataFrame to store the win-loss records for each player
    records = pd.DataFrame({'player_name': latest_match['player_name'], 'wins': 0, 'losses': 0})
    
    # Iterate through all player matchups and update records accordingly
    for i, row in latest_match.iterrows():
        for j, other_row in latest_match.iterrows():
            if i != j:
                num_wins = 0
                num_losses = 0
                num_simulations = 10000
                for _ in range(num_simulations):
                    winner = simulate_game(row['kd'], other_row['kd'])
                    if winner == 1:
                        num_wins += 1
                    else:
                        num_losses += 1
                records.loc[records['player_name'] == row['player_name'], 'wins'] += num_wins
                records.loc[records['player_name'] == row['player_name'], 'losses'] += num_losses
    
    # Calculate win percentages and add a rank column
    records['win_pct'] = records['wins'] / (records['wins'] + records['losses'])
    records = records.sort_values('win_pct', ascending=False).reset_index(drop=True)
    records['rank'] = records.index + 1
    
    return records


overall_rankings_df = overall_rankings(latest_match)
#print(overall_rankings_df)


## Get the individual probability of win against oppenent

def simulate_matchups(latest_match):
    num_players = len(latest_match)
    matchups = pd.DataFrame(np.zeros((num_players, num_players)), index=latest_match['player_name'], columns=latest_match['player_name'])
    
    for i, p1 in enumerate(latest_match['player_name']):
        for j, p2 in enumerate(latest_match['player_name']):
            if i != j:
                p1_wins = 0
                num_simulations = 10000
                for _ in range(num_simulations):
                    if simulate_game(latest_match['kd'][i], latest_match['kd'][j]) == 1:
                        p1_wins += 1
                matchups.loc[p1, p2] = p1_wins / num_simulations
    user_name = 'RootFTW'
    a_wins = matchups.loc[user_name].sort_values(ascending=False)
    ranks = pd.DataFrame({'player_name': a_wins.index, 'win_prob': a_wins.values, 'rank': range(1, num_players + 1)})
    
    return ranks

rankings = simulate_matchups(latest_match)
#print(rankings)


# SHINY APP
# Run shiny app file
