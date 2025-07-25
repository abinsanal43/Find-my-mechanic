from mysql import connector

class Db:
    def __init__(self):
        self.con=connector.connect(host="localhost", database="find_my_mechanic", user="root", password="")
        self.cur=self.con.cursor(dictionary=True)

    def nonreturn(self, q):
        self.cur.execute(q)
        self.con.commit()
        return self.cur.lastrowid

    def selectone(self, q):
        self.cur.execute(q)
        res=self.cur.fetchone()
        return res

    def selectall(self, q):
        self.cur.execute(q)
        res=self.cur.fetchall()
        return res