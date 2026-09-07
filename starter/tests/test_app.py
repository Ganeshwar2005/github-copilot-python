import pytest

from app import CURRENT, app


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    CURRENT['puzzle'] = None
    CURRENT['solution'] = None
    with app.test_client() as test_client:
        yield test_client
    CURRENT['puzzle'] = None
    CURRENT['solution'] = None


def test_index_route_loads(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'Sudoku' in response.data


def test_check_requires_an_active_game(client):
    response = client.post('/check', json={'board': [[0] * 9 for _ in range(9)]})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_new_route_returns_a_nine_by_nine_puzzle(client):
    response = client.get('/new?difficulty=easy')

    assert response.status_code == 200
    puzzle = response.get_json()['puzzle']
    assert len(puzzle) == 9
    assert all(len(row) == 9 for row in puzzle)
    assert sum(cell != 0 for row in puzzle for cell in row) == 45


@pytest.mark.parametrize('query', ['', '?difficulty=unknown', '?difficulty=HARD'])
def test_new_route_defaults_invalid_difficulty_to_medium(client, query, monkeypatch):
    requested_clues = []

    def fake_generate_puzzle(clues):
        requested_clues.append(clues)
        board = [[0] * 9 for _ in range(9)]
        return board, board

    monkeypatch.setattr('app.sudoku_logic.generate_puzzle', fake_generate_puzzle)
    client.get(f'/new{query}')

    expected_clues = 25 if query == '?difficulty=HARD' else 35
    assert requested_clues == [expected_clues]


def test_check_route_reports_incorrect_cells(client):
    client.get('/new?clues=20')

    response = client.post('/check', json={'board': [[1] * 9 for _ in range(9)]})

    assert response.status_code == 200
    incorrect = response.get_json()['incorrect']
    assert len(incorrect) > 0
    assert all(len(position) == 2 for position in incorrect)


def test_check_route_ignores_empty_cells(client):
    client.get('/new?clues=20')

    response = client.post('/check', json={'board': [[0] * 9 for _ in range(9)]})

    assert response.status_code == 200
    assert response.get_json()['incorrect'] == []


def test_hint_route_fills_one_empty_cell_and_tracks_hints(client):
    client.get('/new?clues=20')

    response = client.post('/hint')

    assert response.status_code == 200
    hint = response.get_json()
    assert hint['value'] == CURRENT['solution'][hint['row']][hint['col']]
    assert CURRENT['puzzle'][hint['row']][hint['col']] == hint['value']
    assert hint['hints_used'] == 1


def test_hint_requires_an_active_game(client):
    response = client.post('/hint')

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}