import os

# ---------------------------------------------------------
# CATEGORY IDs
# ---------------------------------------------------------
CATEGORY_IDS = {
    "Acts": 39,
    "General Epistles": 33,
    "Gospels": 26,
    "Historical Books": 28,
    "Jesus’ Teachings": 35,
    "Major Prophets": 30,
    "Minor Prophets": 31,
    "Miracles": 36,
    "Parables": 37,
    "Pauline Epistles": 32,
    "Apocrypha": 28  # You can change this if needed
}

# ---------------------------------------------------------
# FULL BIBLE BOOK LIST WITH CHAPTER COUNTS + CATEGORY
# ---------------------------------------------------------
BOOKS = {
    # Pentateuch / Torah
    "Genesis": (50, "Historical Books"),
    "Exodus": (40, "Historical Books"),
    "Leviticus": (27, "Historical Books"),
    "Numbers": (36, "Historical Books"),
    "Deuteronomy": (34, "Historical Books"),

    # Historical Books
    "Joshua": (24, "Historical Books"),
    "Judges": (21, "Historical Books"),
    "Ruth": (4, "Historical Books"),
    "1 Samuel": (31, "Historical Books"),
    "2 Samuel": (24, "Historical Books"),
    "1 Kings": (22, "Historical Books"),
    "2 Kings": (25, "Historical Books"),
    "1 Chronicles": (29, "Historical Books"),
    "2 Chronicles": (36, "Historical Books"),
    "Ezra": (10, "Historical Books"),
    "Nehemiah": (13, "Historical Books"),
    "Esther": (10, "Historical Books"),

    # Wisdom Books
    "Job": (42, "Historical Books"),
    "Psalms": (150, "Historical Books"),
    "Proverbs": (31, "Historical Books"),
    "Ecclesiastes": (12, "Historical Books"),
    "Song of Solomon": (8, "Historical Books"),

    # Major Prophets
    "Isaiah": (66, "Major Prophets"),
    "Jeremiah": (52, "Major Prophets"),
    "Lamentations": (5, "Major Prophets"),
    "Ezekiel": (48, "Major Prophets"),
    "Daniel": (12, "Major Prophets"),

    # Minor Prophets
    "Hosea": (14, "Minor Prophets"),
    "Joel": (3, "Minor Prophets"),
    "Amos": (9, "Minor Prophets"),
    "Obadiah": (1, "Minor Prophets"),
    "Jonah": (4, "Minor Prophets"),
    "Micah": (7, "Minor Prophets"),
    "Nahum": (3, "Minor Prophets"),
    "Habakkuk": (3, "Minor Prophets"),
    "Zephaniah": (3, "Minor Prophets"),
    "Haggai": (2, "Minor Prophets"),
    "Zechariah": (14, "Minor Prophets"),
    "Malachi": (4, "Minor Prophets"),

    # Gospels
    "Matthew": (28, "Gospels"),
    "Mark": (16, "Gospels"),
    "Luke": (24, "Gospels"),
    "John": (21, "Gospels"),

    # Acts
    "Acts": (28, "Acts"),

    # Pauline Epistles
    "Romans": (16, "Pauline Epistles"),
    "1 Corinthians": (16, "Pauline Epistles"),
    "2 Corinthians": (13, "Pauline Epistles"),
    "Galatians": (6, "Pauline Epistles"),
    "Ephesians": (6, "Pauline Epistles"),
    "Philippians": (4, "Pauline Epistles"),
    "Colossians": (4, "Pauline Epistles"),
    "1 Thessalonians": (5, "Pauline Epistles"),
    "2 Thessalonians": (3, "Pauline Epistles"),
    "1 Timothy": (6, "Pauline Epistles"),
    "2 Timothy": (4, "Pauline Epistles"),
    "Titus": (3, "Pauline Epistles"),
    "Philemon": (1, "Pauline Epistles"),

    # General Epistles
    "Hebrews": (13, "General Epistles"),
    "James": (5, "General Epistles"),
    "1 Peter": (5, "General Epistles"),
    "2 Peter": (3, "General Epistles"),
    "1 John": (5, "General Epistles"),
    "2 John": (1, "General Epistles"),
    "3 John": (1, "General Epistles"),
    "Jude": (1, "General Epistles"),

    # Revelation
    "Revelation": (22, "General Epistles")
}

# ---------------------------------------------------------
# APOCRYPHA BOOKS
# ---------------------------------------------------------
APOCRYPHA = {
    "Tobit": 14,
    "Judith": 16,
    "Wisdom": 19,
    "Sirach": 51,
    "Baruch": 6,
    "1 Maccabees": 16,
    "2 Maccabees": 15,
    "1 Esdras": 9,
    "2 Esdras": 16,
    "Prayer of Manasseh": 1,
    "Susanna": 1,
    "Bel and the Dragon": 1,
    "Additions to Esther": 10
}

# ---------------------------------------------------------
# GENERATOR
# ---------------------------------------------------------
def generate_bible_study_files(base_path="Bible_Study_Guide"):
    os.makedirs(base_path, exist_ok=True)

    # Canonical books
    for book, (chapter_count, category_name) in BOOKS.items():
        category_id = CATEGORY_IDS.get(category_name, "UNKNOWN")

        folder_name = book.replace(" ", "_")
        folder_path = os.path.join(base_path, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        for chapter in range(1, chapter_count + 1):
            filename = f"{folder_name}_SG_Chapter_{chapter}.txt"
            file_path = os.path.join(folder_path, filename)

            content = (
                f"Study Notes for {book} Chapter {chapter}\n"
                f"categories: {category_id}\n\n"
                f"Summary of {book} Chapter {chapter}\n"
            )

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

    # Apocrypha folder
    apocrypha_root = os.path.join(base_path, "Apocrypha")
    os.makedirs(apocrypha_root, exist_ok=True)

    # Apocrypha books
    for book, chapter_count in APOCRYPHA.items():
        category_id = CATEGORY_IDS["Apocrypha"]

        folder_name = book.replace(" ", "_")
        folder_path = os.path.join(apocrypha_root, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        for chapter in range(1, chapter_count + 1):
            filename = f"{folder_name}_SG_Chapter_{chapter}.txt"
            file_path = os.path.join(folder_path, filename)

            content = (
                f"Study Notes for {book} Chapter {chapter}\n"
                f"categories: {category_id}\n\n"
                f"Summary of {book} Chapter {chapter}\n"
            )

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

    print("Bible + Apocrypha study guide files generated successfully!")

# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------
generate_bible_study_files()
