import numpy as np

class Methods:
    extractUsername = lambda user: user.get("username")
    extractAnswers = lambda user: np.array(user.get("answers")).reshape(1, -1)
