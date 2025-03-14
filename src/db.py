import psycopg2
import os
from dotenv import load_dotenv
from typing import Optional, Union

load_dotenv()

class AdvDB:
    def __init__(self):
        self.db_config = {
            "dbname": os.getenv("POSTGRES_DB"),
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "host": os.getenv("POSTGRES_HOST"),
            "port": os.getenv("POSTGRES_PORT")
        }
        
    def _get_connection(self):
        return psycopg2.connect(**self.db_config)

    def check_exist_user(self, user_id: int) -> bool:
        """Check if user exists in database by user_id"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 1 FROM users WHERE user_id = %s;
                """, (user_id,))
                return cur.fetchone() is not None

    def insert_new_user(self, 
                       user_id: int, 
                       username: str, 
                       first_name: Optional[str], 
                       last_name: Optional[str]) -> bool:
        """Insert new user into database"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO users (user_id, username, first_name, last_name)
                        VALUES (%s, %s, %s, %s);
                    """, (user_id, username, first_name, last_name))
                    conn.commit()
                    return True
        except psycopg2.IntegrityError:
            # Handle duplicate user case
            return False

    def insert_new_adver(self, 
                        user_id: int, 
                        description: str) -> Union[int, None]:
        """Insert new advertisement and return advertisement ID"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO advertisements (user_id, description)
                        VALUES (%s, %s)
                        RETURNING adv_id;
                    """, (user_id, description))
                    adv_id = cur.fetchone()[0]
                    conn.commit()
                    return adv_id
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return None

    def get_user_info(self, user_id: int) -> Optional[dict]:
        """Get user information by user_id.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            dict: User information with keys:
                - user_id
                - username
                - first_name
                - last_name
            None: If user not found
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT user_id, username, first_name, last_name
                        FROM users
                        WHERE user_id = %s;
                    """, (user_id,))
                    result = cur.fetchone()
                    
                    if result:
                        return {
                            "user_id": result[0],
                            "username": result[1],
                            "first_name": result[2],
                            "last_name": result[3]
                        }
                    return None
        except psycopg2.Error as e:
            print(f"Database error in get_user_info: {e}")
            return None

    def get_adv_info(self, adv_id: int) -> Optional[dict]:
        """Get advertisement information by adv_id.
        
        Args:
            adv_id: Advertisement ID
            
        Returns:
            dict: Advertisement details with keys:
                - adv_id
                - user_id
                - description
                - inserted_at (ISO formatted string)
            None: If advertisement not found
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT adv_id, user_id, description, inserted_at
                        FROM advertisements
                        WHERE adv_id = %s;
                    """, (adv_id,))
                    result = cur.fetchone()
                    
                    if result:
                        return {
                            "adv_id": result[0],
                            "user_id": result[1],
                            "description": result[2],
                            "inserted_at": result[3].isoformat()
                        }
                    return None
        except psycopg2.Error as e:
            print(f"Database error in get_adv_info: {e}")
            return None


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
