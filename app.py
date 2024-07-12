import pandas as pd
from flask import Flask, render_template, request
from typing import List, NamedTuple
from collections import defaultdict

app = Flask(__name__)


class Player(NamedTuple):
    name: str
    score: int
    position: str


def read_csv_file(filepath: str) -> List[Player]:
    df = pd.read_csv(filepath)
    return [Player(row['name'], int(row['score']), row['position']) for _, row in df.iterrows()]


def distribute_participants(participants: List[Player], num_teams: int, team_size: int) -> List[List[Player]]:

    """참가자를 팀에 배분합니다."""
    teams = [[] for _ in range(num_teams)]
    thirteen_score_players = [p for p in participants if p.score == 13]
    other_players = sorted([p for p in participants if p.score != 13], key=lambda x: -x.score)

    # 13점 참가자 배분
    for i, player in enumerate(thirteen_score_players):
        teams[i % num_teams].append(player)

    # 나머지 참가자 배분
    for player in other_players:
        team_scores = [sum(p.score for p in team) for team in teams]
        team_sizes = [len(team) for team in teams]

        # 팀 크기가 작고 점수가 낮은 팀을 우선 선택
        target_team = min(range(num_teams), key=lambda i: (team_sizes[i], team_scores[i]))

        if len(teams[target_team]) < team_size:
            teams[target_team].append(player)

    # 포지션 균형 조정 (팀 크기가 8명 이상일 때만)
    if team_size >= 8:
        balance_positions(teams)

    return teams


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_players = request.form.getlist('players')
        num_teams = int(request.form['num_teams'])
        team_size = int(request.form['team_size'])

        all_players = read_csv_file('players_2.csv')
        participants = [player for player in all_players if player.name in selected_players]

        teams = distribute_participants(participants, num_teams, team_size)

        return render_template('results.html', teams=teams)

    players = read_csv_file('players_2.csv')
    return render_template('index.html', players=players)


if __name__ == '__main__':
    app.run(debug=True)