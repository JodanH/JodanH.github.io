from flask import Flask, render_template
import gspread
from google.oauth2 import service_account
import os

app = Flask(__name__)

# Function to authenticate and get data from Google Sheets
def get_leaderboard():
    # Get the path to the JSON key file from environment variable
    key_file_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

    # Define the scope
    scope = ['https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/spreadsheets']

    # Add credentials to the account
    creds = service_account.Credentials.from_service_account_file(key_file_path, scopes=scope)

    # Authorize the client
    client = gspread.authorize(creds)

    # Open the spreadsheet
    spreadsheet = client.open('Yuzulounge')  # Update with your spreadsheet name

    # Get the worksheet by name
    worksheet = spreadsheet.worksheet('PlayerHistory')

    # Get all values in the worksheet
    values = worksheet.get_all_values()

    # Skip the header row (row 1)
    player_data = values[1:]

    # Extract player names and MMRs
    player_mmr_data = []
    for row in player_data:
        if row[0] and row[6]:  # Ensure both player name and MMR are not empty
            try:
                mmr = int(row[6])  # Convert MMR to integer
                player_mmr_data.append((row[0], mmr))
            except ValueError:
                pass  # Skip rows where MMR is not a valid integer

    # Sort player data based on MMR in descending order
    sorted_player_mmr_data = sorted(player_mmr_data, key=lambda x: x[1], reverse=True)

    # Assign ranks based on sorted order
    ranked_leaderboard_data = [(i+1, *sorted_player_mmr_data[i]) for i in range(len(sorted_player_mmr_data))]

    return ranked_leaderboard_data

@app.route('/')
def leaderboard():
    leaderboard_data = get_leaderboard()
    return render_template('index.html', leaderboard_data=leaderboard_data)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
