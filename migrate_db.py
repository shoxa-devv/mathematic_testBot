import sqlite3

def migrate_db():
    conn = sqlite3.connect('math_bot.db')
    cursor = conn.cursor()
    
    # Check and add category_id
    try:
        cursor.execute("ALTER TABLE tests ADD COLUMN category_id INTEGER REFERENCES categories(category_id)")
        print("Column 'category_id' added.")
    except sqlite3.OperationalError as e:
        print(f"Skipping category_id: {e}")

    # Check and add question_text
    try:
        cursor.execute("ALTER TABLE tests ADD COLUMN question_text TEXT")
        print("Column 'question_text' added.")
    except sqlite3.OperationalError as e:
        print(f"Skipping question_text: {e}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate_db()
