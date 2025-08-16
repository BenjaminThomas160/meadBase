
import json
import psycopg
import string
from psycopg_pool import ConnectionPool
import db.dataObjects as dataObjects
class DataAccess:
    def __init__(self, conninfo):
        self.pool = ConnectionPool(conninfo)

    def CreateBasetables(self):
        self.CreateYeastTypesTable()
        self.CreateHoneyTypesTable()
        self.CreateRecipesTable()
        self.CreateBatchesTable()

    def CreateBatchesTable(self):
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                query = """
                CREATE TABLE IF NOT EXISTS mead_batches (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    recipe_id INT,
                    batch_number TEXT UNIQUE,  
                    fermentation_start_date DATE NOT NULL,
                    fermentation_end_date DATE,
                    secondary_fermentation_start_date DATE,
                    secondary_fermentation_end_date DATE,
                    honey_id INT,
                    yeast_id INT,
                    volume_litres NUMERIC(10,5) NOT NULL,
                    initial_gravity NUMERIC(10,5),
                    final_gravity NUMERIC(10,5),
                    abv NUMERIC(4,2),
                    status TEXT DEFAULT 'fermenting',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    CONSTRAINT fk_recipe FOREIGN KEY (recipe_id) REFERENCES mead_recipes,
                    CONSTRAINT fk_honey FOREIGN KEY (honey_id) REFERENCES honey_types,
                    CONSTRAINT fk_yeast FOREIGN KEY (yeast_id) REFERENCES yeast_types
                );
                """
                cur.execute(query=query)

    def CreateRecipesTable(self):
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                query = """
                CREATE TABLE IF NOT EXISTS mead_recipes (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    style TEXT,
                    honey_volume NUMERIC(10,5),
                    water_volume NUMERIC(10,5),
                    honey_id INT,
                    yeast_id INT,
                    ingredients JSONB NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
                """
                cur.execute(query=query)

    def CreateHoneyTypesTable(self):
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                query = """
                CREATE TABLE IF NOT EXISTS honey_types (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    farmer TEXT,
                    price_per_kilo NUMERIC(6,2),
                    volume_in_stock_kilos NUMERIC(10,5) DEFAULT 0,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                ); 
                """
                cur.execute(query=query)

    def CreateYeastTypesTable(self):
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                query = """
                CREATE TABLE IF NOT EXISTS yeast_types (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    max_abv Numeric(10,5),
                    price_per_gram NUMERIC(6,2),
                    volume_in_stock_grams NUMERIC(10,5),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                ); 
                """
                cur.execute(query=query)

    def insert_new_batch(self, data: dataObjects.batchData): 
        with self.pool.connection() as conn, conn.transaction():
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM mead_batches b INNER JOIN mead_recipes r on b.recipe_id = r.id WHERE b.recipe_id = %s", (data.recipe_id))
                num_batches = len(cur.fetchall()) + 1
                cur.execute("""
                INSERT INTO mead_batches (
                    name,
                    recipe_id,
                    batch_number,  
                    fermentation_start_date,
                    fermentation_end_date,
                    secondary_fermentation_start_date,
                    secondary_fermentation_end_date,
                    honey_id,
                    yeast_id,
                    volume_litres,
                    initial_gravity,
                    final_gravity,
                    abv,
                    status,
                    notes,
                    created_at,
                    updated_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (data.name, 
                      data.recipe_id, 
                      num_batches, 
                      data.fementation_start_date, 
                      data.fermentation_end_date,
                      data.secondary_fermentation_start_date,
                      data.secondary_fermentation_end_date,
                      data.honey_id,
                      data.yeast_id,
                      data.volume_litres,
                      data.initial_gravity,
                      data.final_gravity,
                      data.abv,
                      data.status,
                      data.notes,
                      data.created_at,
                      data.updated_at))

    def insert_honey_type(self, name: string, farmer: string, price_per_kilo: float, volume: float, notes: string) -> int:
        with self.pool.connection() as conn, conn.transaction():
            with conn.cursor() as cur:
                cur.execute("SELECT id from honey_types WHERE name = %s AND farmer = %s", (name,farmer)) # apparently this stops sql injection becuase psycopg does it for us
                exists = cur.fetchone()
                if exists:
                    return exists[0]
                cur.execute("""
                INSERT INTO honey_types (name, farmer, price_per_kilo, volume_in_stock_kilos, notes)
                VALUES (%s, %s, %s, %s, %s);
                """, (name, farmer, price_per_kilo, volume, notes))
    
    def insert_yeast_type(self, data: dataObjects.yeastData):
        with self.pool.connection() as conn, conn.transaction():
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO yeast_types (name, max_abv, price_per_gram, volume_in_stock_grams, notes)
                VALUES (%s, %s, %s, %s, %s)
                """, (data.name, data.max_abv, data.price_per_gram, data.volume_in_stock_grams, data.notes))

    def insert_new_recipe(self, data: dataObjects.recipeData):
        with self.pool.connection() as conn, conn.transaction():
            with conn.cursor() as cur:
                ingredients = json.dumps(data.ingredients)
                cur.execute("""
                INSERT INTO mead_recipes (
                    name,
                    style,
                    honey_volume,
                    water_volume,
                    honey_id,
                    yeast_id,
                    ingredients,
                    notes)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """, (data.name, data.style, data.honey_volume, data.water_volume, data.honey_id, data.yeast_id, ingredients, data.notes))

    def select_honey_type(self, name):
        with self.pool.connection() as conn, conn.transaction():
            with conn.cursor() as cur:
                cur.execute("SELECT * from honey_types WHERE name = %s", (name,))
                return cur.fetchall()

    def select_batches(self):
        with self.pool.connection() as conn, conn.transaction():
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM mead_batches;")
                return cur.fetchall()

    def select_yeast_types(self):
        with self.pool.connection() as conn, conn.transaction():
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM yeast_types;")
                return cur.fetchall()

    def select_honey_types(self):
        with self.pool.connection() as conn, conn.transaction():
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM honey_types;")
                return cur.fetchall()

    def select_recipes(self):
        with self.pool.connection() as conn, conn.transaction():
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM mead_recipes;")
                return cur.fetchall()
# add user security and stuff for diff users once auth stuff is taken care of