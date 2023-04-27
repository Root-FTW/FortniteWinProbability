import sys
import re
import os
import datetime
import pandas as pd
import json
import requests
import numpy as np
import time
from tqdm import tqdm
import xlsxwriter

start_time = time.time()

# Read the list of player names from the file
with open(r"C:\Users\rootf\Downloads\Compressed\FortniteWinProbability-main\FortniteWinProbability-main\names.txt", 'r', encoding='utf-8') as f:
    player_names = [line.strip() for line in f]

# Create a data frame with a player_name column
df = pd.DataFrame(player_names, columns=['player_name'])

# API base URL
url = 'https://fortnite-api.com/v2/stats/br/v2'

account_types = ['epic']

headers = dict(
    Authorization = '3bb03286-20da-4033-9bdc-b70bbdb3399e'
)

data_rows = []
for name in player_names:
    found = False
    for account_type in account_types:
        # Set the API request parameters
        params = dict(
            name=name,
            AccountType=account_type,
            timeWindow='lifetime',
            image='none'
        )
        # Make the API request
        data = requests.get(url=url, params=params, headers=headers)
        
        # If the player data is found
        if data.status_code == 200:
            data_json = data.json()
            indent1_stats = data_json["data"]
            indent2_stats = indent1_stats['stats']
            indent3_stats = indent2_stats['all']
            indent4_stats = indent3_stats['solo']
            df_stats = pd.DataFrame([indent4_stats])
            df_stats = df_stats.rename_axis("group").reset_index()
            df_stats['player_name'] = name
            df_stats['status'] = 'public'
            data_rows.append(df_stats)
            found = True
            break
            
    # If no player data is found, create an entry in the list with a 'private' status
    if not found:
        df_stats = pd.DataFrame({'player_name': [name], 'status': ['private']})
        data_rows.append(df_stats)

if data_rows:
    df_stats = pd.concat(data_rows)
    merged_df = pd.merge(df, df_stats, on="player_name", how="inner")
else:
    print("No player data found")
    sys.exit()

unique_df = merged_df.drop_duplicates()
unique_df['match_number'] = 1

latest_match = unique_df[unique_df["match_number"] == unique_df["match_number"].max()]
latest_match = latest_match.loc[:, ["player_name", "kd"]][~latest_match["kd"].isna()]
latest_match = latest_match.reset_index(drop=True)

# Function to simulate a game between two players based on their kd values
def simulate_game(kd1, kd2):
    p1_score = np.random.normal(kd1, 1)
    p2_score = np.random.normal(kd2, 1)
    if p1_score > p2_score:
        return 1
    else:
        return 2

# Function to calculate overall rankings based on game simulations
def overall_rankings(latest_match):
    records = pd.DataFrame({'player_name': latest_match['player_name'], 'wins': 0, 'losses': 0})

    for i in tqdm(range(len(latest_match)), desc="Simulating overall match-ups"):
        row = latest_match.iloc[i]
        for j in range(len(latest_match)):
            if i != j:
                other_row = latest_match.iloc[j]
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

    records['win_pct'] = records['wins'] / (records['wins'] + records['losses'])
    records = records.sort_values('win_pct', ascending=False).reset_index(drop=True)
    records['rank'] = records.index + 1

    return records

overall_rankings_df = overall_rankings(latest_match)

# Function to simulate individual match-ups
def simulate_matchups(latest_match):
    num_players = len(latest_match)
    matchups = pd.DataFrame(np.zeros((num_players, num_players)), index=latest_match['player_name'], columns=latest_match['player_name'])

    for i, p1 in enumerate(tqdm(latest_match['player_name'], desc="Simulating individual match-ups")):
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

print(overall_rankings_df)
print(rankings)

# Save the overall rankings and individual match-ups to an Excel file
with pd.ExcelWriter('output_data.xlsx', engine='xlsxwriter') as writer:
    overall_rankings_df.to_excel(writer, sheet_name='Overall Rankings', index=False)
    rankings.to_excel(writer, sheet_name='Individual Matchups', index=False)

elapsed_time = time.time() - start_time
print("\nElapsed time: {:.2f} minutes".format(elapsed_time / 60))
