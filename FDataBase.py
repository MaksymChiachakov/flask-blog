import math, sqlite3, time

class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()
    
    def addPost(self, title, text, url, author):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM posts WHERE url LIKE '{url}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Such an article with this url already exist")
                return False
            
            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO posts VALUES(NULL, ?, ?, ?, ?, ?)", (title, text, url, author, tm))
            self.__db.commit()
            print('Its good today!')
        except sqlite3.Error as e:
            print("An error while adding the posts in DB " +str(e))
            return False
        
        return True
    
    def getPost(self, alias):
        try:
            self.__cur.execute(f"SELECT title, text, author from posts WHERE url LIKE '{alias}' LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("An error while getting the posts in DB" +str(e))

        return (False, False)
    
    def getPostsAnonce(self):
        try: 
            self.__cur.execute(f"SELECT id, title, text, url FROM posts ORDER BY time DESC")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("An error while getting the posts in DB" +str(e))
        
        return []
    
    def addUser(self, name, email, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM users WHERE email LIKE '{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Such user already exists")
                return False
            
            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO users VALUES (NULL, ?, ?, ?, NULL, ?)", (name, email, hpsw, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Error adding user "+str(e))
            return False
        
        return True
    
    def deleteUser(self, email):
        try:
            self.__cur.execute("DELETE FROM users WHERE email = ?", (email,))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Error deletting user " + str(e))
            return False
        
        return True
    
    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("User not found")
                return False
            
            return res
        except sqlite3.Error as e:
            print("Database's error "+str(e))

        return False
    

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("User not found")
                return False
            
            return res
        except sqlite3.Error as e:
            print("Database's error"+str(e))

        return False
    
    def updateUserAvatar(self, avatar, user_id):
        if not avatar:
            return False
        
        try: 
            binary = sqlite3.Binary(avatar)
            self.__cur.execute(f"UPDATE users SET avatar = ? WHERE id = ?", (binary, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Upload's error"+str(e))
            return False
        return True
    

    def updateUserData(self, name, email, hpsw, user_id):
        if len(name) < 2 and len(email) < 8 and len(hpsw) < 6:
            return False
        else:
            try:
                tm = math.floor(time.time())
                self.__cur.execute("UPDATE users SET name = ?, email = ?, psw = ?, time = ? WHERE id = ?", (name, email, hpsw, tm, user_id))
                self.__db.commit()
            except sqlite3.Error as e:
                print("Error updating user "+str(e))
                return False
        
        return True