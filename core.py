
class User(object):
    def __init__(self, uid: str, rank: float, rating: float):
        self.uid = uid
        self.rank = rank
        self.rating = rating
        self.seed = 1.0
        self.delta = 0.0
        self.new_rating = rating

    def __str__(self):
        return "%s { RANK: %6.2f, RATING: %6.2f, NEW: %6.2f}" % (
            self.uid,
            self.rank,
            self.rating,
            self.new_rating
        )


class Calculator(object):
    def __init__(self, users: [User]):
        self.users = {}
        for user in users:
            self.users[user.uid] = user

    @staticmethod
    def calc_p(a: User, b: User):
        return 1.0 / (1.0 + pow(10, (b.rating - a.rating) / 400.0))

    def calc_seed(self, target: User, rating: float):
        res = 1.0
        for uid, user in self.users.items():
            if uid == target.uid: continue
            res += self.calc_p(user, User("", 0.0, rating))
        return res

    def calc_rating(self, user, rank):
        L, R = 1, 8000
        while R - L > 1:
            M = (L + R) // 2
            if self.calc_seed(user, M) < rank:
                R = M
            else:
                L = M
        return L

    def calc_all_rating(self):
        for uid_i, user_i in self.users.items():
            user_i.seed = 1.0
            for uid_j, user_j in self.users.items():
                if uid_i == uid_j: continue
                user_i.seed += self.calc_p(user_j, user_i)

        sum_delta = 0.0
        for uid, user in self.users.items():
            rating = (user.rank * user.seed) ** 0.5
            user.delta = (self.calc_rating(user, rating) - user.rating) / 2
            sum_delta += user.delta

        inc = -sum_delta / len(self.users) - 1
        for uid, user in self.users.items():
            user.delta += inc
        s = min(len(self.users), int(4 * round(len(self.users) ** 0.5)))
        sum_s = 0.0
        for uid, user in self.users.items():
            sum_s += user.delta
        inc = min(max(int(-sum_s / s), -10), 0)

        for uid, user in self.users.items():
            user.delta += inc
            user.new_rating = user.rating + user.delta

    def __str__(self):
        res = ""
        for uid, user in self.users.items():
            res += str(user) + "\n"
        return res.strip()


if __name__ == "__main__":
    _users = [
        User("uid_1", 1, 1500),
        User("uid_2", 2, 2000),
        User("uid_3", 3, 1500),
        User("uid_4", 4, 1300),
        User("uid_5", 5, 1600)
    ]
    _calculator = Calculator(_users)
    _calculator.calc_all_rating()
    print(_calculator)
