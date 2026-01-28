import sqlite3

def migrate_categories():
    conn = sqlite3.connect('math_bot.db')
    cursor = conn.cursor()
    
    # Clear existing categories
    cursor.execute("DELETE FROM categories")
    cursor.execute("DELETE FROM tests") # Clear tests as they will have invalid category_ids
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='categories'")
    
    # Insert fixed categories
    categories = [
        ("Oson", "Oson darajadagi testlar"),
        ("O'rtacha", "O'rtacha darajadagi testlar"),
        ("Qiyin", "Qiyin darajadagi testlar")
    ]
    
    cursor.executemany("INSERT INTO categories (category_name, description) VALUES (?, ?)", categories)
    
    print("Categories reset to: Oson, O'rtacha, Qiyin")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate_categories()
