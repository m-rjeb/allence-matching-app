class Vars:
    user_username: str
    user_id: str
    best_match: str
    answers: dict = {}
    other_usernames: list[str] = []
    scores: list[float] = []
    
    CONNECTION_URI = "mongodb+srv://helloworld:helloworld123@pymongo.mtdg3j5.mongodb.net/"
    DB_NAME = "personality"
    COLLECTION_NAME = "users"
    app_secret_key = "6be400ac88b98282c53b01c3b9462258c74603b00742c0db21773696d8dfd770"