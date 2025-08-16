from db.dataAccess import DataAccess
import json
def testDbCreationStuff():
    with open('config.json', 'r') as f:
        cfg = json.load(f)
    connInfo = f"dbname={cfg['DB_NAME']} user={cfg['DB_USER']} password={cfg['DB_PASSWORD']} host={cfg['DB_HOST']}"
    daccess = DataAccess(conninfo=connInfo)
    daccess.CreateBasetables()
    print("tables created")
    print(daccess.insert_honey_type("test_honey", "farmer jerry", 25, 2, "random notes about things crazy"))
    print(daccess.select_honey_type("test_honey"))


if __name__ == "__main__":
    testDbCreationStuff()