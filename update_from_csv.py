import sqlite3
from core import *


class DB(object):
    def __init__(self, path: str):
        self.con = sqlite3.connect(path)
        self.cur = self.con.cursor()
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS `accounts` (
                `id` TEXT,
                `rating` REAL
            )''')
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS `contests` (
                `id` INT AUTO INCREMENT,
                `title` TEXT
            )''')
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS `records` (
                `aid` TEXT,
                `cid` INT,
                `rank` INT,
                `old_rating` REAL,
                `new_rating` REAL
            )''')

    def get_contest_id(self, contest: str) -> int:
        sql = "SELECT `id` FROM `contests` WHERE `title`='%s'" % contest
        res = self.cur.execute(sql)
        row = res.fetchone()
        if row is None: return 0
        return int(row[0])

    def insert_contest(self, contest: str) -> int:
        sql = "SELECT MAX(`id`) FROM `contests`"
        res = self.cur.execute(sql)
        row = res.fetchone()[0]
        cid = 0
        if row is not None: cid = row
        cid += 1

        sql = "INSERT INTO `contests` VALUES(%d, '%s')" % (cid, contest)
        self.cur.execute(sql)
        return cid

    def get_rating(self, uid: str) -> float:
        sql = "SELECT `rating` FROM `accounts` WHERE `id`='%s'" % uid
        res = self.cur.execute(sql)
        row = res.fetchone()
        if row is None: return 1500
        return float(row[0])

    def insert_record(self, uid: str, cid: int, rank: float, old_rating: float, new_rating: float):
        sql = "INSERT INTO `records` VALUES ('%s', %d, %d, %.2f, %.2f)" % (uid, cid, int(rank), old_rating, new_rating)
        self.cur.execute(sql)

    def user_exists(self, uid: str) -> bool:
        sql = "SELECT COUNT(*) FROM `accounts` WHERE `id`='%s'" % uid
        res = self.cur.execute(sql)
        cnt = res.fetchone()[0]
        return cnt == 1

    def select_user(self, uid: str) -> []:
        sql = "SELECT * FROM `accounts` WHERE `id`='%s'" % uid
        res = self.cur.execute(sql)
        row = res.fetchone()
        return row

    def insert_user(self, uid: str, rating: float):
        sql = "INSERT INTO `accounts` VALUES ('%s', %.2f)" % (uid, rating)
        self.cur.execute(sql)

    def update_user(self, uid: str, rating: float):
        sql = "UPDATE `accounts` SET `rating`=%.2f WHERE `id`='%s'" % (rating, uid)
        self.cur.execute(sql)

    def get_users(self) -> []:
        res = self.cur.execute("SELECT * FROM `accounts` ORDER BY `rating` DESC")
        return res

    def get_history(self) -> []:
        res = self.cur.execute("SELECT * FROM `contests` ORDER BY `id` DESC")
        contests = res.fetchall()
        res = self.cur.execute("SELECT * FROM `accounts` ORDER BY `rating` DESC")
        users = res.fetchall()

        print("姓名\t當前積分", end="")
        for c in contests:
            title = c[1]
            print("\t排名\t%s" % title, end="")
        print("\t初始積分")

        for u in users:
            uid = u[0]
            rating = float(u[1])
            print("%s\t%8.2f" % (uid, rating), end="")
            for c in contests:
                cid = int(c[0])
                res = self.cur.execute("SELECT * FROM `records` WHERE `aid`='%s' AND `cid`=%d" % (uid, cid))
                row = res.fetchone()
                rank, rating = 0, 0
                if row is not None:
                    rank, rating = row[2], row[4]
                print("\t%d\t%8.2f" % (rank, rating), end="")
            print("\t1500.00")


class Zero1Result(object):
    def __init__(self, csv_path: str, db_path: str):
        self.db = DB(db_path)
        contest = csv_path.split("/")[-1].split(".")[0]
        if self.db.get_contest_id(contest) > 0:
            print("「%s」之前已經處理完畢" % contest)
        else:
            print("正在處理「%s」..." % contest)
            cid = self.db.insert_contest(contest)

            print("\t正在讀取csv數據...")
            self.users = []
            with open(csv_path, "r", encoding="UTF-8") as f:
                for line in f.readlines():
                    a = line.strip().split(",")
                    if not a[0].isnumeric(): continue
                    if len(a) == 10:
                        rank, uid = float(a[0]), a[1]
                        self.users.append(User(uid, rank, 1500))
                    elif len(a) <= 11:
                        pass
                    elif len(a) == 12:
                        rank, uid_a, uid_b = float(a[0]), a[10].strip(), a[11].strip()
                        if len(uid_a) > 0: self.users.append(User(uid_a, rank, 1500))
                        if len(uid_b) > 0: self.users.append(User(uid_b, rank, 1500))

            print("\t正在讀取過往積分...")
            for user in self.users:
                user.rating = self.db.get_rating(user.uid)

            print("\t正在計算新的積分...")
            self.calc_all_rating()

            print("\t數據正在更新...")
            for u in self.users:
                self.db.insert_record(u.uid, cid, u.rank, u.rating, u.new_rating)
            self.update_users()
            self.db.con.close()
            print("\t順利完成")

    def calc_all_rating(self):
        c = Calculator(self.users)
        c.calc_all_rating()

    def update_users(self):
        for user in self.users:
            if self.db.user_exists(user.uid):
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
        "data/校內編程競賽2021第一季.csv",
        "data/校內編程競賽2021第二季.csv",
        "data/校內編程競賽2021第三季.csv",
        "data/校內編程競賽2022第一季.csv"
    ]
    _db_path = "data/demo.db"

    for _csv_path in _csv_paths:
        _zr = Zero1Result(_csv_path, _db_path)

    _db = DB(_db_path)
    # _users = _db.get_users()
    # for _user in _users:
    #     print("%s\t%.2f" % (_user[0], _user[1]))

    _db.get_history()
    _db.con.close()
