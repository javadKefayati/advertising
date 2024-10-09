import sqlite3

class adv_db:
    db_address = "adv.db"


    def insert_new_adver(self, user_id, username, first_name, last_name):
        try:
            con = sqlite3.connect(self.db_address)
            cur = con.cursor()

            # Get the current max advertisement_id and increment it
            cur.execute('SELECT IFNULL(MAX(adv_id), 0) + 1 FROM Advertisement')
            new_adv_id = cur.fetchone()[0]
            
            
            # Insert the new advertisement with the calculated advertisement_id
            query = '''
            INSERT INTO Advertisement (adv_id, user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?, ?);
            '''
            
            cur.execute(query, (new_adv_id, user_id, username, first_name, last_name))
            con.commit()
            
            print(f"Record inserted successfully with adve_id: {new_adv_id}")
            return new_adv_id
            
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            if con:
                con.close()

    def get_user_info(self, adv_id: int):
        try:
            con = sqlite3.connect(self.db_address)
            cur = con.cursor()

            # Query to retrieve user information based on the adv_id
            query = '''
            SELECT user_id, username, first_name, last_name 
            FROM Advertisement 
            WHERE adv_id = ?;
            '''
            
            cur.execute(query, (adv_id,))
            user_info = cur.fetchone()

            if user_info:
                user_data = {
                    "user_id": user_info[0],
                    "username": user_info[1],
                    "first_name": user_info[2],
                    "last_name": user_info[3]
                }
                return user_data
            else:
                return None  # adv_id does not exist

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return None
        finally:
            if con:
                con.close()
