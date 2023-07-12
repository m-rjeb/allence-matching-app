import json
import numpy as np
from flask import Flask, render_template, request
from sklearn.metrics.pairwise import cosine_similarity
from core.mongoConn import Collections, Connection
from helpers.vars import Vars as var
from helpers.methods import Methods as meth

app = Flask(__name__)
app.secret_key = var.app_secret_key

database = Connection(connection_uri=var.CONNECTION_URI).use_db(db_name=var.DB_NAME)
collection = Collections(db=database)
collection.use_collection(collection_name=var.COLLECTION_NAME)


def checkUserAvailability(username: str) -> dict:
    user = collection.findByUsername(username)
    if user is None:
        id = collection.create({'username': username})
        user = collection.findById(id)
    return user


def update_answers():
    try:
        var.answers = dict(sorted(var.answers.items()))
        collection.update(document_id=var.user_id, data={'answers': list(var.answers.values())})
        return True
    except:
        app.logger.error('An error occurred while updating')
        return False


def match():
    all_users = list(collection.findAll())
    users_count = len(all_users)
    # Calculate matching rates between users
    matching_rates = np.zeros((users_count, users_count))  # Initialize a matrix to store the matching rates
    for row in range(users_count):
        for col in range(users_count):
            if row != col:
                user_i_answers = meth.extractAnswers(all_users[row])
                user_j_answers = meth.extractAnswers(all_users[col])
                similarity_score = cosine_similarity(user_i_answers, user_j_answers)
                matching_rates[row][col] = similarity_score[0][0]
    return all_users, users_count, matching_rates


def display(user_username: str, user_id: str, users_count: int, all_users: list, matching_rates: np.ndarray[float]):
    for i in range(users_count):
        if meth.extractUsername(all_users[i]) == user_username:
            matching_list = []
            best_match = max(matching_rates[i])
            for j in range(users_count):
                if i != j:
                    other: str = meth.extractUsername(all_users[j])
                    score: int = round(matching_rates[i][j]*100)
                    matching_list.append({"name": other, "score": score})
                    ###### update other users matching_list #######
                    other_id: str = all_users[j].get("_id")
                    other_value = {"name": user_username, "score": score}
                    other_matching_list: list = all_users[j].get("matching_list").copy()
                    other_matching_list.append(other_value)
                    other_best_score = [x.get('score') for x in other_matching_list]
                    other_best_name = [y.get('name') for y in other_matching_list]
                    other_best_match = other_best_name[other_best_score.index(max(other_best_score))]
                    collection.update(other_id, {"matching_list": other_matching_list, "bestMatch": other_best_match})
                    # print(f"{user_username} && {other}: {score}%")
                    var.other_usernames.append(other)
                    var.scores.append(score)
            best_match_username = meth.extractUsername(all_users[list(matching_rates[i]).index(best_match)])
            collection.update(user_id, {"bestMatch": best_match_username, "matching_list": matching_list})
            # print(f'best match for {user_username} is {best_match_username}')
            var.best_match = best_match_username


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/form', methods=['POST'])
def form():
    username = request.form['username']
    user = checkUserAvailability(username)
    var.user_id, var.user_username = user.get("_id"), user.get("username")
    data = get_json_data("assets/questions.json")
    return render_template('form.html', data=data, username=var.user_username)


@app.route("/get_json", methods=['POST'])
def get_json_data(filename):
    with open(filename) as f:
        data = json.load(f)
    return data


@app.route('/button-clicked', methods=['POST'])
def button_clicked():
    data = request.get_json()
    button_value = data['value']
    question_index = data['questionIndex']
    var.answers[question_index] = int(button_value) / 100
    return ''


@app.route('/results', methods=['POST'])
def on_submit():
    # updated, rates = asyncio.gather(update_answers(), match())
    updated = update_answers()
    if updated:
        users, users_count, matching_rates = match()
        display(
            user_id=var.user_id,
            user_username=var.user_username,
            users_count=users_count,
            all_users=users,
            matching_rates=matching_rates)
    return ''


@app.route('/modal', methods=['POST'])
def show_modal():
    length = len(var.other_usernames)
    return render_template('modal.html', length=length, scores=var.scores, best_match=var.best_match,
                           other_usernames=var.other_usernames)


@app.route('/dismiss-modal', methods=['POST'])
def dismiss_modal():
    var.best_match, var.other_usernames, var.scores, var.answers, var.user_username, var.user_id = '', [], [], {}, '', ''
    return ''


@app.route('/index-modal', methods=['POST'])
def index_modal():
    return render_template('username-modal.html')


@app.route('/get-index-modal-username', methods=['POST'])
def get_index_modal_username():
    data = request.get_json()
    username = data.get('existUsername')
    user = collection.findByUsername(username)
    
    if user is None:
        return render_template('error.html', username=username)
    
    matching_users = user.get("matching_list")
    other_usernames = [entry['name'] for entry in matching_users]
    scores = [entry['score'] for entry in matching_users]
    length = len(matching_users)
    best_match = user.get("bestMatch")
    
    return render_template(
        'results-modal.html', length=length, scores=scores,
        best_match=best_match, other_usernames=other_usernames)


if __name__ == '__main__':
    app.run(debug=True)
