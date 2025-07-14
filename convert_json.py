import json
import sqlite3
import os

from utils.utils import sql2skeleton  


# === LẤY TABLE VÀ COLUMN TỪ SQLITE ===
def get_table_and_columns(path_db):
    con = sqlite3.connect(path_db)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cur.fetchall()]

    table_columns = {}
    for table in tables:
        cur.execute(f"PRAGMA table_info({table});")
        cols = [row[1] for row in cur.fetchall()]
        table_columns[table] = cols

    cur.close()
    con.close()
    return tables, table_columns


# === TỰ ĐỘNG LINK TOKEN ===
def auto_link_and_mask(question, tables, columns):
    tokens = question.split()
    sc_link = {"q_tab_match": {}, "q_col_match": {}}
    cv_link = {"num_date_match": [], "cell_match": {}}

    for idx, token in enumerate(tokens):
        token_lower = token.lower().strip("?")
        if any(token_lower in tbl.lower() for tbl in tables):
            sc_link["q_tab_match"][f"{idx},0"] = "TEM"
        elif any(token_lower in col.lower() for col in columns):
            sc_link["q_col_match"][f"{idx},0"] = "CEM"
        elif token.isdigit() and len(token) == 4:
            cv_link["num_date_match"].append(f"{idx},0")

    return sc_link, cv_link, tokens


# === CHUYỂN TỪNG ITEM ===
def convert_item(item, db_root="./database"):
    db_id = item["db_id"]
    question = item["question"]
    query = item["SQL"] if "SQL" in item else item["query"]

    path_db = "/home/thanhtung/Downloads/DAIL-SQL-main/database/vpbank/vpbank.sqlite"
    if not os.path.exists(path_db):
        raise FileNotFoundError(f"SQLite not found: {path_db}")

    tables, table_columns = get_table_and_columns(path_db)

    # Gộp all columns
    all_columns = []
    for cols in table_columns.values():
        all_columns.extend(cols)

    sc_link, cv_link, tokens = auto_link_and_mask(question, tables, all_columns)

    # === GỌI sql2skeleton ===
    if "PRAGMA" in query.upper():
        pre_skeleton = "PRAGMA table_info(_)"
    else:
        # sql2skeleton cần schema Spider-style:
        schema = {
            "table_names_original": tables,
            "column_names_original": []
        }
        for tid, tbl in enumerate(tables):
            for col in table_columns[tbl]:
                schema["column_names_original"].append((tid, col))

        pre_skeleton = sql2skeleton(query, schema)

    converted = {
        "question": question,
        "query": query,
        "db_id": db_id,
        "sc_link": sc_link,
        "cv_link": cv_link,
        "question_for_copying": tokens,
        "path_db": os.path.abspath(path_db),
        "pre_skeleton": pre_skeleton
    }
    return converted


# === MAIN ===
def main():
    input_file = "original.json"   # File gốc input
    output_file = "converted.json" # File output

    with open(input_file, "r") as f:
        original_data = json.load(f)

    converted_data = []
    for idx, item in enumerate(original_data):
        try:
            converted = convert_item(item)
            converted_data.append(converted)
            print(f"[{idx+1}/{len(original_data)}] ✅ Converted: {item['question']}")
        except Exception as e:
            print(f"[{idx+1}] ❌ ERROR: {e}")

    with open(output_file, "w") as f:
        json.dump(converted_data, f, indent=2)

    print(f"\n✅ Done! Saved to {output_file}")


if __name__ == "__main__":
    main()
