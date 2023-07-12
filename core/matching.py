import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
from mongoConn import Collections, Connection

def checkUserAvailability(username: str) -> dict:
    user = collection.findByUsername(username)
    if user is None:
        id = collection.create({'username': username})
        user = collection.findById(id)
    return user

extractUsername = lambda user: user.get("username")
extractAnswers = lambda user: np.array(user.get("answers")).reshape(1, -1)


CONNECTION_URI = "mongodb+srv://helloworld:helloworld123@pymongo.mtdg3j5.mongodb.net/"
DB_NAME = "personality"
COLLECTION_NAME = "users"

database = Connection(connection_uri=CONNECTION_URI).use_db(db_name=DB_NAME)
collection = Collections(db=database)
collection.use_collection(collection_name=COLLECTION_NAME)

######################################## user section #########################################
user = checkUserAvailability(input("\n\nenter your username: "))
user_id, user_username = user.get("_id"), user.get("username")

""" with open("myApp/assets/test.json") as f:
    answers = []
    data = json.load(f)
    for question in data.keys():
        answers.append(int(input(f"\n{data[question]} : ")) / 100)
    collection.update(document_id=user_id, data={'answers': answers})
 """
######################################## app section #############################################
all_users = list(collection.findAll())
users_count = len(all_users)

# Calculate matching rates between users
matching_rates = np.zeros((users_count, users_count))  # Initialize a matrix to store the matching rates
for i in range(users_count):
    for j in range(users_count):
        if i != j:
            user_i_answers = extractAnswers(all_users[i])
            user_j_answers = extractAnswers(all_users[j])
            similarity_score = cosine_similarity(user_i_answers, user_j_answers)
            matching_rates[i][j] = similarity_score[0][0]

################################# Display matching rates per current user ##################################
for i in range(users_count):
    if extractUsername(all_users[i]) == user_username:
        matching_list = []
        best_match = max(matching_rates[i])
        for j in range(users_count):
            if i != j:
                other: str = extractUsername(all_users[j])
                score: int = round(matching_rates[i][j]*100)
                matching_list.append({"name": other, "score": score})
                ###### update other user matching_list #######
                other_id: str = all_users[j].get("_id")
                other_value = {"name": user_username, "score": score}
                other_matching_list: list = all_users[j].get("matching_list").copy()
                other_matching_list.append(other_value)
                other_best_score = [x.get('score') for x in other_matching_list]
                other_best_name = [y.get('name') for y in other_matching_list]
                other_best_match = other_best_name[other_best_score.index(max(other_best_score))]
                collection.update(other_id, {"matching_list": other_matching_list, "bestMatch": other_best_match})
                print(f"{user_username} && {other}: {score}%")
        best_match_username = extractUsername(all_users[list(matching_rates[i]).index(best_match)])
        collection.update(user_id, {"bestMatch": best_match_username, "matching_list": matching_list})
        print(f'best match for {user_username} is {best_match_username}')
