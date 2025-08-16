
import psycopg
import string
from psycopg_pool import ConnectionPool
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
                    updated_at TIMESTAMP DEFAULT NOW(),
                    CONSTRAINT ingredients_is_array CHECK (jsonb_typeof(ingredients) = 'array')
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
                    farmer TEXT,
                    price_per_gram NUMERIC(6,2),
                    volume_in_stock_grams NUMERIC(10,5),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                ); 
                """
                cur.execute(query=query)

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
    
    def select_honey_type(self, name):
        with self.pool.connection() as conn, conn.transaction():
            with conn.cursor() as cur:
                cur.execute("SELECT * from honey_types WHERE name = %s", (name,))
                return cur.fetchall()

# yeast table
# honey table
# shopping list table