import streamlit as st
import pandas as pd
from collections import defaultdict, deque

class PlayerTracker:
    def __init__(self, n):
        self.n = n
        self.player_records = defaultdict(lambda: {'consecutive_games': 0, 'recent_games': deque(maxlen=n)})

    def update_records(self, team1, team2, result):
        winner = team1 if result == 'Team 1' else team2 if result == 'Team 2' else None
        players = team1 + team2

        players_so_far = set(players) | set(self.player_records.keys())
        for player in players_so_far:
            if player in players:
                self.player_records[player]['consecutive_games'] += 1
                if winner is not None:
                    self.player_records[player]['recent_games'].append(1 if player in winner else 0)
            else:
                self.player_records[player]['consecutive_games'] = 0

    def get_player_stats(self, player):
        record = self.player_records[player]
        consecutive_games = record['consecutive_games']
        recent_games = record['recent_games']
        if recent_games:
            wins = sum(recent_games)
            losses = len(recent_games) - wins
            return consecutive_games, wins, losses
        else:
            return consecutive_games, 0, 0

    def get_all_players(self):
        return self.player_records.keys()

def create_team_selection(team_number, team_size, all_players):
    st.subheader(f'Team {team_number}')
    team = []
    roles = ['Tank', 'DPS', 'Support']
    role_counts = {
        3: [1, 1, 1],
        4: [1, 1, 2],
        5: [1, 2, 2],
        6: [2, 2, 2]
    }
    
    sorted_players = sorted(all_players, key=str.lower)
    
    for role, count in zip(roles, role_counts[team_size]):
        for i in range(count):
            player = st.selectbox(f'Team {team_number} {role} {i+1}', [''] + sorted_players, key=f't{team_number}_{role.lower()}_{i}')
            team.append(player)
    
    return team

def main():
    st.title('Team Creation and Player Tracking')

    # Initialize session state of the app.
    if 'tracker' not in st.session_state:
        st.session_state.tracker = PlayerTracker(n=4)
    if 'all_players' not in st.session_state:
        st.session_state.all_players = set()
    if 'warnings' not in st.session_state:
        st.session_state.warnings = []
    if 'reset_session' not in st.session_state:
        st.session_state.reset_session = False

    # Check if we need to reset the session
    if st.session_state.reset_session:
        st.session_state.tracker = PlayerTracker(n=4)
        st.session_state.all_players = set()
        st.session_state.warnings = []
        st.session_state.reset_session = False
        st.success('Session reset successfully!')

    # Add multiple players
    st.header('Add Players')
    new_players = st.text_area('Add new players (separate by commas or newlines)', height=100)
    if st.button('Add Players'):
        player_list = [player.strip().capitalize() for player in new_players.replace('\n', ',').split(',') if player.strip()]
        
        if player_list:
            newly_added = set(player_list) - st.session_state.all_players
            st.session_state.all_players.update(newly_added)
            
            if newly_added:
                st.success(f"Added {len(newly_added)} new player(s) to the pool.")
            else:
                st.info("All entered players were already in the pool.")
        else:
            st.warning('No valid player names entered.')

    # Display current player pool
    st.subheader('Current Player Pool')
    st.write(', '.join(sorted(st.session_state.all_players, key=str.lower)))

    # Team size selection
    st.header('Team Size')
    team_size = st.slider('Select number of players per team', min_value=3, max_value=6, value=5)

    # Team creation
    st.header('Create Teams')
    col1, col2 = st.columns(2)
    
    with col1:
        team1 = create_team_selection(1, team_size, st.session_state.all_players)
    
    with col2:
        team2 = create_team_selection(2, team_size, st.session_state.all_players)

    # Match result
    st.header('Match Result')
    result = st.radio('Which team won?', ['Team 1', 'Team 2', 'Draw'])

    if st.button('Record Match Result'):
        if '' in team1 or '' in team2:
            st.error('Please fill in all player slots before recording the match result.')
        else:
            st.session_state.tracker.update_records(team1, team2, result)
            st.success('Match result recorded successfully!')

    # Display player warnings
    st.header('Player Warnings')
    st.session_state.warnings = []
    for player in st.session_state.tracker.get_all_players():
        cons_games, wins, losses = st.session_state.tracker.get_player_stats(player)
        if cons_games >= 4:
            st.session_state.warnings.append(f'{player} has played {cons_games} games in a row.')
        if losses >= 3:
            st.session_state.warnings.append(f'{player} has lost {losses} games out of their last {wins+losses} games.')
    
    if st.session_state.warnings:
        for warning in st.session_state.warnings:
            st.warning(warning)
    else:
        st.info("No warnings to display.")

    # Reset session
    if st.button('Reset Session', help="Clear all tracked stats for the current session."):
        st.session_state.reset_session = True
        st.rerun()

if __name__ == '__main__':
    main()