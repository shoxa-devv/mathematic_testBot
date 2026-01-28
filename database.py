import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_name: str = "math_bot.db"):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Foydalanuvchilar jadvali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Foydalanuvchi profillari
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                middle_name TEXT,
                phone_number TEXT NOT NULL,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Bloklangan foydalanuvchilar
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blocked_users (
                user_id INTEGER PRIMARY KEY,
                phone_number TEXT,
                blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reason TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Adminlar jadvali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                admin_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Kategoriyalar jadvali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Testlar jadvali (category_id qo'shildi)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tests (
                test_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                level TEXT,
                question_text TEXT,
                question_image TEXT,
                option_a TEXT,
                option_b TEXT,
                option_c TEXT,
                option_d TEXT,
                correct_answer TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(category_id)
            )
        """)
        
        # Test natijalari
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category_id INTEGER,
                total_questions INTEGER NOT NULL,
                correct_answers INTEGER NOT NULL,
                percentage REAL NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (category_id) REFERENCES categories(category_id)
            )
        """)
        
        # Har bir savolga berilgan javoblar
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_answers (
                answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                result_id INTEGER NOT NULL,
                test_id INTEGER NOT NULL,
                user_answer TEXT,
                is_correct INTEGER DEFAULT 0,
                FOREIGN KEY (result_id) REFERENCES test_results(result_id),
                FOREIGN KEY (test_id) REFERENCES tests(test_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    # Admin funksiyalari
    def is_admin(self, user_id: int) -> bool:
        """Foydalanuvchi admin ekanligini tekshirish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM admins WHERE admin_id = ?", (user_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    
    def add_admin(self, admin_id: int, username: str = None, first_name: str = None) -> bool:
        """Yangi admin qo'shish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO admins (admin_id, username, first_name)
            VALUES (?, ?, ?)
        """, (admin_id, username, first_name))
        added = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return added
    
    def remove_admin(self, admin_id: int) -> bool:
        """Adminni o'chirish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM admins WHERE admin_id = ?", (admin_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    def get_all_admins(self) -> List[Dict]:
        """Barcha adminlarni olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT admin_id, username, first_name FROM admins")
        admins = []
        for row in cursor.fetchall():
            admins.append({
                "admin_id": row[0],
                "username": row[1],
                "first_name": row[2]
            })
        conn.close()
        return admins
    
    # Foydalanuvchi funksiyalari
    def add_user(self, user_id: int, username: str = None, first_name: str = None):
        """Foydalanuvchini qo'shish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        """, (user_id, username, first_name))
        conn.commit()
        conn.close()
    
    def is_user_registered(self, user_id: int) -> bool:
        """Foydalanuvchi ro'yxatdan o'tganmi"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM user_profiles WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    
    def add_user_profile(self, user_id: int, first_name: str, last_name: str, 
                        middle_name: str = None, phone_number: str = None) -> bool:
        """Foydalanuvchi profilini qo'shish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_profiles 
            (user_id, first_name, last_name, middle_name, phone_number)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, first_name, last_name, middle_name, phone_number))
        conn.commit()
        conn.close()
        return True
    
    def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """Foydalanuvchi profilini olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT first_name, last_name, middle_name, phone_number
            FROM user_profiles WHERE user_id = ?
        """, (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "first_name": row[0],
                "last_name": row[1],
                "middle_name": row[2],
                "phone_number": row[3]
            }
        return None
    
    def is_user_blocked(self, user_id: int) -> bool:
        """Foydalanuvchi bloklanganmi"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM blocked_users WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Username orqali foydalanuvchini topish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        # Username @ bilan yoki @ siz bo'lishi mumkin
        username_clean = username.lstrip('@')
        cursor.execute("SELECT user_id, username, first_name FROM users WHERE username = ?", (username_clean,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "user_id": row[0],
                "username": row[1],
                "first_name": row[2]
            }
        return None
    
    def block_user(self, user_id: int = None, phone_number: str = None, username: str = None, reason: str = None) -> bool:
        """Foydalanuvchini bloklash"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if username:
            # Username orqali user_id ni topish
            user_data = self.get_user_by_username(username)
            if not user_data:
                conn.close()
                return False
            user_id = user_data['user_id']
        elif phone_number:
            # Telefon raqami orqali user_id ni topish
            cursor.execute("SELECT user_id FROM user_profiles WHERE phone_number = ?", (phone_number,))
            user_row = cursor.fetchone()
            if not user_row:
                conn.close()
                return False
            user_id = user_row[0]
        
        if not user_id:
            conn.close()
            return False
        
        cursor.execute("""
            INSERT OR REPLACE INTO blocked_users (user_id, phone_number, reason)
            VALUES (?, ?, ?)
        """, (user_id, phone_number, reason))
        conn.commit()
        conn.close()
        return True
    
    def unblock_user(self, user_id: int = None, phone_number: str = None, username: str = None) -> bool:
        """Foydalanuvchini blokdan chiqarish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if username:
            user_data = self.get_user_by_username(username)
            if user_data:
                user_id = user_data['user_id']
        elif phone_number:
            cursor.execute("SELECT user_id FROM user_profiles WHERE phone_number = ?", (phone_number,))
            user_row = cursor.fetchone()
            if user_row:
                user_id = user_row[0]
        
        if not user_id:
            conn.close()
            return False
        
        cursor.execute("DELETE FROM blocked_users WHERE user_id = ?", (user_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    def get_all_users(self) -> List[Dict]:
        """Barcha foydalanuvchilarni olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.user_id, u.username, u.first_name, up.phone_number
            FROM users u
            LEFT JOIN user_profiles up ON u.user_id = up.user_id
        """)
        users = []
        for row in cursor.fetchall():
            users.append({
                "user_id": row[0],
                "username": row[1],
                "first_name": row[2],
                "phone_number": row[3]
            })
        conn.close()
        return users
    
    def get_total_users_count(self) -> int:
        """Jami foydalanuvchilar soni"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_active_users_count(self, days: int = 7) -> int:
        """Oxirgi N kun davomida botdan foydalangan foydalanuvchilar soni"""
        conn = self.get_connection()
        cursor = conn.cursor()
        start_date = datetime.now() - timedelta(days=days)
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) FROM test_results
            WHERE completed_at >= ?
        """, (start_date.strftime("%Y-%m-%d %H:%M:%S"),))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    # Kategoriyalar funksiyalari
    def add_category(self, category_name: str, description: str = None) -> int:
        """Yangi kategoriya qo'shish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO categories (category_name, description)
            VALUES (?, ?)
        """, (category_name, description))
        category_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return category_id
    
    def update_category(self, category_id: int, category_name: str = None, description: str = None) -> bool:
        """Kategoriyani tahrirlash"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if category_name:
            updates.append("category_name = ?")
            params.append(category_name)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        
        if not updates:
            conn.close()
            return False
        
        params.append(category_id)
        query = f"UPDATE categories SET {', '.join(updates)} WHERE category_id = ?"
        cursor.execute(query, params)
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated
    
    def delete_category(self, category_id: int) -> bool:
        """Kategoriyani o'chirish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE category_id = ?", (category_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    def get_all_categories(self) -> List[Dict]:
        """Barcha kategoriyalarni olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category_id, category_name, description
            FROM categories
            ORDER BY category_name
        """)
        categories = []
        for row in cursor.fetchall():
            categories.append({
                "category_id": row[0],
                "category_name": row[1],
                "description": row[2]
            })
        conn.close()
        return categories
    
    def get_category(self, category_id: int) -> Optional[Dict]:
        """Kategoriyani olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category_id, category_name, description
            FROM categories WHERE category_id = ?
        """, (category_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "category_id": row[0],
                "category_name": row[1],
                "description": row[2]
            }
        return None
    
    # Testlar funksiyalari
    def add_test(self, category_id: int = None, level: str = None, question_text: str = None,
                 question_image: str = None, option_a: str = None, option_b: str = None,
                 option_c: str = None, option_d: str = None, correct_answer: str = None) -> int:
        """Yangi test qo'shish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tests (category_id, level, question_text, question_image,
                             option_a, option_b, option_c, option_d, correct_answer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (category_id, level, question_text, question_image, option_a, option_b,
              option_c, option_d, correct_answer))
        test_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return test_id
    
    def update_test(self, test_id: int, category_id: int = None, level: str = None,
                   question_text: str = None, question_image: str = None,
                   option_a: str = None, option_b: str = None, option_c: str = None,
                   option_d: str = None, correct_answer: str = None) -> bool:
        """Testni tahrirlash"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if category_id is not None:
            updates.append("category_id = ?")
            params.append(category_id)
        if level:
            updates.append("level = ?")
            params.append(level)
        if question_text:
            updates.append("question_text = ?")
            params.append(question_text)
        if question_image:
            updates.append("question_image = ?")
            params.append(question_image)
        if option_a:
            updates.append("option_a = ?")
            params.append(option_a)
        if option_b:
            updates.append("option_b = ?")
            params.append(option_b)
        if option_c:
            updates.append("option_c = ?")
            params.append(option_c)
        if option_d is not None:
            updates.append("option_d = ?")
            params.append(option_d)
        if correct_answer:
            updates.append("correct_answer = ?")
            params.append(correct_answer)
        
        if not updates:
            conn.close()
            return False
        
        params.append(test_id)
        query = f"UPDATE tests SET {', '.join(updates)} WHERE test_id = ?"
        cursor.execute(query, params)
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated
    
    def delete_test(self, test_id: int) -> bool:
        """Testni o'chirish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tests WHERE test_id = ?", (test_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    def get_test(self, test_id: int) -> Optional[Dict]:
        """Testni olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT test_id, category_id, level, question_text, question_image,
                   option_a, option_b, option_c, option_d, correct_answer
            FROM tests WHERE test_id = ?
        """, (test_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "test_id": row[0],
                "category_id": row[1],
                "level": row[2],
                "question_text": row[3],
                "question_image": row[4],
                "option_a": row[5],
                "option_b": row[6],
                "option_c": row[7],
                "option_d": row[8],
                "correct_answer": row[9]
            }
        return None
    
    def get_tests_by_category(self, category_id: int, limit: int = 20) -> List[Dict]:
        """Kategoriya bo'yicha testlarni olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT test_id, question_text, question_image, option_a, option_b,
                   option_c, option_d, correct_answer
            FROM tests
            WHERE category_id = ?
            ORDER BY RANDOM()
            LIMIT ?
        """, (category_id, limit))
        tests = []
        for row in cursor.fetchall():
            tests.append({
                "test_id": row[0],
                "question_text": row[1],
                "question_image": row[2],
                "option_a": row[3],
                "option_b": row[4],
                "option_c": row[5],
                "option_d": row[6],
                "correct_answer": row[7]
            })
        conn.close()
        return tests
    
    def get_tests_by_level(self, level: str) -> List[Dict]:
        """Daraja bo'yicha testlarni olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT test_id, category_id, question_text, question_image,
                   option_a, option_b, option_c, option_d, correct_answer
            FROM tests
            WHERE level = ?
            ORDER BY created_at DESC
        """, (level,))
        tests = []
        for row in cursor.fetchall():
            tests.append({
                "test_id": row[0],
                "category_id": row[1],
                "question_text": row[2],
                "question_image": row[3],
                "option_a": row[4],
                "option_b": row[5],
                "option_c": row[6],
                "option_d": row[7],
                "correct_answer": row[8]
            })
        conn.close()
        return tests
    
    def get_all_tests(self) -> List[Dict]:
        """Barcha testlarni olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT test_id, category_id, level, question_text, question_image,
                   option_a, option_b, option_c, option_d
            FROM tests
            ORDER BY created_at DESC
        """)
        tests = []
        for row in cursor.fetchall():
            tests.append({
                "test_id": row[0],
                "category_id": row[1],
                "level": row[2],
                "question_text": row[3],
                "question_image": row[4],
                "option_a": row[5],
                "option_b": row[6],
                "option_c": row[7],
                "option_d": row[8]
            })
        conn.close()
        return tests
    
    # Test natijalari funksiyalari
    def save_test_result(self, user_id: int, category_id: int, total_questions: int,
                        correct_answers: int, percentage: float) -> int:
        """Test natijasini saqlash"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO test_results (user_id, category_id, total_questions,
                                     correct_answers, percentage)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, category_id, total_questions, correct_answers, percentage))
        result_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return result_id
    
    def save_test_answer(self, result_id: int, test_id: int, user_answer: str, is_correct: bool):
        """Har bir savolga berilgan javobni saqlash"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO test_answers (result_id, test_id, user_answer, is_correct)
            VALUES (?, ?, ?, ?)
        """, (result_id, test_id, user_answer, 1 if is_correct else 0))
        conn.commit()
        conn.close()
    
    def get_test_result_details(self, result_id: int) -> List[Dict]:
        """Test natijasi tafsilotlarini olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ta.test_id, t.question_text, ta.user_answer, t.correct_answer, ta.is_correct
            FROM test_answers ta
            JOIN tests t ON ta.test_id = t.test_id
            WHERE ta.result_id = ?
            ORDER BY ta.answer_id
        """, (result_id,))
        details = []
        for row in cursor.fetchall():
            details.append({
                "test_id": row[0],
                "question_text": row[1],
                "user_answer": row[2],
                "correct_answer": row[3],
                "is_correct": bool(row[4])
            })
        conn.close()
        return details
    
    def get_user_stats(self, period: str = "day") -> int:
        """period: day, week, month, year"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now()
        
        if period == "day":
            start_date = now - timedelta(days=1)
        elif period == "week":
            start_date = now - timedelta(weeks=1)
        elif period == "month":
            start_date = now - timedelta(days=30)
        elif period == "year":
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=1)
        
        cursor.execute("""
            SELECT COUNT(*) FROM users
            WHERE joined_at >= ?
        """, (start_date.strftime("%Y-%m-%d %H:%M:%S"),))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_test_completions_stats(self, period: str = "week") -> int:
        """Test topshirgan foydalanuvchilar soni"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now()
        
        if period == "week":
            start_date = now - timedelta(weeks=1)
        elif period == "month":
            start_date = now - timedelta(days=30)
        elif period == "year":
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(weeks=1)
        
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) FROM test_results
            WHERE completed_at >= ?
        """, (start_date.strftime("%Y-%m-%d %H:%M:%S"),))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_general_stats(self) -> Dict:
        """Umumiy statistika"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Jami foydalanuvchilar
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # Ro'yxatdan o'tgan foydalanuvchilar
        cursor.execute("SELECT COUNT(*) FROM user_profiles")
        registered_users = cursor.fetchone()[0]
        
        # Jami testlar
        cursor.execute("SELECT COUNT(*) FROM tests")
        total_tests = cursor.fetchone()[0]
        
        # Jami kategoriyalar
        cursor.execute("SELECT COUNT(*) FROM categories")
        total_categories = cursor.fetchone()[0]
        
        # Jami test natijalari
        cursor.execute("SELECT COUNT(*) FROM test_results")
        total_results = cursor.fetchone()[0]
        
        # Oxirgi hafta test topshirganlar
        week_ago = datetime.now() - timedelta(weeks=1)
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) FROM test_results
            WHERE completed_at >= ?
        """, (week_ago.strftime("%Y-%m-%d %H:%M:%S"),))
        week_completions = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_users": total_users,
            "registered_users": registered_users,
            "total_tests": total_tests,
            "total_categories": total_categories,
            "total_results": total_results,
            "week_completions": week_completions
        }
