import sqlite3
from core import *


class DB(object):
    def __init__(self, path: str):
        self.con = sqlite3.connect(path)
        self.cur = self.con.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS `user`(`uid`, `rating`)")

    def get_rating(self, uid: str) -> float:
        sql = "SELECT `rating` FROM `user` WHERE `uid`='%s'" % uid
        res = self.cur.execute(sql)
        row = res.fetchone()
        if row is None: return 1500
        return float(row[0])

    def is_existed(self, uid: str) -> bool:
        sql = "SELECT COUNT(*) FROM `user` WHERE `uid`='%s'" % uid
        res = self.cur.execute(sql)
        cnt = res.fetchone()[0]
        return cnt == 1

    def insert_user(self, uid: str, rating: float):
        sql = "INSERT INTO `user` VALUES ('%s', %.2f)" % (uid, rating)
        self.cur.execute(sql)

    def update_user(self, uid: str, rating: float):
        sql = "UPDATE `user` SET `rating`=%.2f WHERE `uid`='%s'" % (rating, uid)
        self.cur.execute(sql)

    def get_users(self) -> []:
        res = self.cur.execute("SELECT * FROM `user` ORDER BY `rating` DESC")
        return res


class Zero1Result(object):
    def __init__(self, csv_path: str, db_path: str):
        self.users = []
        with open(csv_path, "r", encoding="UTF-8") as f:
            for line in f.readlines():
                a = line.strip().split(",")
                if not a[0].isnumeric(): continue
                rank, uid = float(a[0]), a[1]
                self.users.append(User(uid, rank, 1500))

        self.db = DB(db_path)
        for user in self.users:
            user.rating = self.db.get_rating(user.uid)

    def calc_all_rating(self):
        c = Calculator(self.users)
        c.calc_all_rating()

    def update_users(self):
        for user in self.users:
            if self.db.is_existed(user.uid):
                self.db.update_user(user.uid, user.new_rating)
            else:
                self.db.insert_user(user.uid, user.new_rating)
        self.db.con.commit()

    def get_db_users(self) -> [User]:
        users = []
        res = self.db.get_users()
        for i, row in enumerate(res):
            users.append(User(row[0], i + 1, float(row[1])))
        return users

    def close(self):
        self.db.con.close()


if __name__ == "__main__":
    _csv_paths = [
        "data/demo_1.csv",
        "data/demo_2.csv",
        "data/demo_3.csv"
    ]
    _db_path = "data/demo.db"

    for _csv_path in _csv_paths:
        _zr = Zero1Result(_csv_path, _db_path)
        _zr.calc_all_rating()
        _zr.update_users()

        print("# %s" % _csv_path)
        for _user in _zr.users:
            print(_user)
        _zr.close()
