from datetime import date
import json
from dataclasses import dataclass

@dataclass
class batchData:
    name: str
    recipe_id: int
    fementation_start_date:date
    fermentation_end_date:date
    secondary_fermentation_start_date:date
    secondary_fermentation_end_date:date
    honey_id:int
    yeast_id:int
    volume_litres:float
    initial_gravity:float
    final_gravity:float
    abv:float
    status:str
    notes:str
    created_at:date
    updated_at:date

@dataclass
class yeastData:
    name:str
    max_abv:float
    price_per_gram:float
    volume_in_stock_grams:float
    notes:str
    created_at:date
    updated_at:date

@dataclass
class honeyData:
    name:str
    price_per_kilo:float
    volume_in_stock_kilos:float
    notes:str
    created_at:date
    updated_at:date

@dataclass
class recipeData:
    name:str
    style:str
    honey_volume:float
    water_volume:float
    honey_id:int
    yeast_id:int
    ingredients:json
    notes:str
    created_at:date
    updated_at:date
