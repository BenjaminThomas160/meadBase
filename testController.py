from db.dataAccess import DataAccess
import db.dataObjects as dataObjects
import json
from datetime import date
def testDbCreationStuff():
    with open('config.json', 'r') as f:
        cfg = json.load(f)
    connInfo = f"dbname={cfg['DB_NAME']} user={cfg['DB_USER']} password={cfg['DB_PASSWORD']} host={cfg['DB_HOST']}"
    daccess = DataAccess(conninfo=connInfo)
    # daccess.CreateBasetables()
    # print("tables created")
    # print(daccess.insert_honey_type("test_honey", "farmer jerry", 25, 2, "random notes about things crazy"))
    honey_id = daccess.select_honey_type("test_honey")[0][0]
    # print(daccess.insert_yeast_type(dataObjects.yeastData(name="test yeast", max_abv=12, price_per_gram=1, volume_in_stock_grams=10,notes="kljsnafdjksnkf", created_at=date.today, updated_at=date.today)))
    yeast_id = daccess.select_yeast_types()[0][0]
    ingredients = {"honey": "5kg", "spices": "100kg"}
    daccess.insert_new_recipe(dataObjects.recipeData(name="test_recipe", style="traditional", honey_volume=5, water_volume=10, honey_id=honey_id, yeast_id=yeast_id, ingredients=ingredients, notes="testestset", created_at=date.today, updated_at=date.today))
    print(daccess.select_recipes())



if __name__ == "__main__":
    testDbCreationStuff()