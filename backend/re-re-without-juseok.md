```python
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import json
import urllib.request

def recommend_max_ingredient(my_stock):
    GapofDuplicated_ingredients = 0
    all_recipes = Recipe.objects.all()
    recommend_recipe_id_list = []
    stock_list = my_stock
    stock_id_list = []
    for stock in stock_list:
        stock_id_list.append(stock.ingredient_id.id)
    while len(recommend_recipe_id_list) <= 30 or GapofDuplicated_ingredients < len(set(stock_id_list))/2:
        for recipe in all_recipes:
            if not(recipe.ingredient_ids):
                continue
            split_ingredient_list = recipe.ingredient_ids.split(',')
            recommend_ingre_list = []
            for x in split_ingredient_list:
                recommend_ingre_list.append(int(x))
            if len(recommend_ingre_list) != 0 :
                if len(set(stock_id_list) - set(recommend_ingre_list)) <= GapofDuplicated_ingredients:
                    recommend_recipe_id_list.append(recipe.reci_id)
            if len(recommend_recipe_id_list) > 30: break
        GapofDuplicated_ingredients += 1
    result = {}
    result['ids'] = recommend_recipe_id_list
    return result

def parse_korean_type_date(d, MinYear=1900):
    try:
        d_parsed = dateparse(d, yearfirst=True, dayfirst=False)
        if d_parsed.year < MinYear: 
            return None
        else:
            return d_parsed
    except: 
        return None

def get_time_diff(start_date, end_date, unit='second'):
    assert isinstance(start_date, pydatetime.datetime), 'start_date required datetime instance'
    assert isinstance(end_date,   pydatetime.datetime), 'end_date   required datetime instance'
    _timedelta = end_date - start_date
    if unit=='day':
        return abs(_timedelta.days)
    return abs((_timedelta.days * (_timedelta.max.seconds + 1)) + _timedelta.seconds)

def recommend_expiration_date(my_stock):
    cur = datetime.datetime.now()
    curDates = cur.strftime('%Y-%m-%d')
    curDate = curDates.replace('-', '')
    stock_list = my_stock
    expiration_count = 2
    GapofDuplicated_ingredients = 0
    priority = 0
    ex_URGENT_my_id_list = []
    ex_my_id_list = []
    recommend_recipe_list = []
    while len(recommend_recipe_id_list) <= 30 or expiration_count < 14:
        for stock in stock_list:
            stock_time = str(stock.expiration_date).replace('-', '')
            ex_date = get_time_diff(parse_korean_type_date(curDate), parse_korean_type_date(stock_time), unit='day')
            if ex_date < expiration_count: 
                ex_my_id_list.append(stock.ingredient_id.id)
                if ex_date <= 2:
                    ex_URGENT_my_id_list.append(stock.ingredient_id.id)
        all_recipes = Recipe.objects.all()
        for recipe in all_recipes:
            if not(recipe.ingredient_ids):
                continue
            split_ingredient_list = recipe.ingredient_ids.split(',')
            recommend_ingre_list = [] 
            for x in split_ingredient_list:
                recommend_ingre_list.append(int(x))
            GapofDuplicated_ingredients = 0
            if len(recommend_ingre_list) != 0:
                if len(set(ex_URGENT_my_id_list) - set(recommend_ingre_list)) == 0:
                    recommend_recipe_list.append(recipe.reci_id)
                elif priority == 1 and len(set(ex_URGENT_my_id_list) - set(recommend_ingre_list)) == 0:
                    while GapofDuplicated_ingredients < 3:
                        if len(set(ex_my_id_list) - set(recommend_ingre_list)) <= GapofDuplicated_ingredients:
                            recommend_recipe_list.append(recipe.reci_id)
                            break
                        else
                            GapofDuplicated_ingredients += 1
            if len(recommend_recipe_id_list) > 30:
                break
        expiration_count += 1
        if expiration_count >= 7:
            priority = 1
        elif expiration_count == 14: break
    result = dict()
    result['ids'] = recommend_recipe_list
    return result
