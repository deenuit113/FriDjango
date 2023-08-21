import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "save_your_ingredient.settings")
django.setup()

from random import shuffle
import datetime
from dateutil.parser import parse as dateparse
import datetime as pydatetime
import json

from recipe.models import Recipe
from stock.models import Stock


# list to json
def list_to_json(list):
    lst = []
    for pn in list:
        d = {}
        d["id"] = pn
        lst.append(d)
    return json.dumps(lst) #python 객체를 json 문자열로 변환

"""
# 사용자 재고 리스트 가져오기 => 이건 이제필요없어짐
def get_stock_list():
    all_stock = Stock.objects.all() # filter 넣어야함: .objects.filter(author=request.user)
    stock_list = []
    for stock in all_stock:
        stock_list.append(stock.ingredient_id.id)
    return stock_list
"""
#------------------------------------------------------------------------------------------------------------
# 재료 기반 레시피 추천
def recommend_max_ingredient(my_stock):
    GapofDuplicated_ingredients = 0
    all_recipes = Recipe.objects.all() #모든 레시피 
    recommend_recipe_id_list = [] #추천 레시피 아이디 배열
    this_stock = my_stock #내 재료 this_stock 배열에
    stock_list = [] #재료 목록
    for stock in this_stock: 
        stock_list.append(stock.ingredient_id.id) #내 재료에 있는 재료들의 id 재료 목록에 추가
    for recipe in all_recipes:
        if not(recipe.ingredient_ids): #id 일치하지 않으면 넘김
            continue
        split_ingredient_list = recipe.ingredient_ids.split(',') #각 id를 ,로 쪼갬
        re_list = [] # 추천 레시피의 재료 id 리스트
        for x in split_ingredient_list: #ss에 있는 id들 각 항목에 대하여
            re_list.append(int(x)) #각 id들을 re_list에 저장
# 재고에 있는 재료를 모두 사용해서 만들 수 있는 요리부터 추천
        if len(re_list) != 0 and len(set(stock_list) - set(re_list)) == GapofDuplicated_ingredients:#재료들 모두 소비할 수 있으면 (내 재료 - 레시피 재료)
            if len(recommend_recipe_id_list) < 20: #추천된 레시피의 id가 20개 미만이면
                recommend_recipe_id_list.append(recipe.reci_id) #리스트에 id추가

    if len(recommend_recipe_id_list) < 10: #추천된 레시피의 id가 10개 미만이면
        for recipe in all_recipes:
            if not (recipe.ingredient_ids):
                continue
            split_ingredient_list = recipe.ingredient_ids.split(',')   
            re_list = []
            for x in split_ingredient_list:
                re_list.append(int(x))
            if len(re_list) != 0 and 0 < len(set(stock_list) - set(re_list)) < 1:  #내 재료 리스트랑 추천 레시피의 재료 리스트의 차이가 2개 미만일 경우
                if len(recommend_recipe_id_list) < 20:
                    recommend_recipe_id_list.append(recipe.reci_id)

    if len(recommend_recipe_id_list) < 10:
        for recipe in all_recipes:
            if not (recipe.ingredient_ids):
                continue
            split_ingredient_list = recipe.ingredient_ids.split(',')
            re_list = []
            for x in split_ingredient_list:
                re_list.append(int(x))
            if len(re_list) != 0 and 1 < len(set(stock_list) - set(re_list)) < 2:
                if len(recommend_recipe_id_list) < 20:
                    recommend_recipe_id_list.append(recipe.reci_id)
    result = {}
    result['ids'] = recommend_recipe_id_list
    return result
#----------------------------------------------------------------------------------------------------------
#recommend_ingredient 수정해야할 사항
#코드가 너무 rough 함 반복문 돌려서
#코드 간략하게 하고 추천 레시피 개수 20개 이상되면 멈추기
#혹은 재료가 너무 안 겹칠 경우 멈추기
#----------------------------------------------------------------------------------------------------------
def parse_korean_type_date(d, assert_min_year=1900): #한국 서버 시간 반환
    """
    날짜문자열(년도가 앞, 일자가 뒤 형태)을 입력받아 datetime 인스턴스를 반환
    파싱이 불가능한 경우 또는 assert_min_year년도 이전인 경우 None 반환
    """
    try:
        d_parsed = dateparse(d, yearfirst=True, dayfirst=False)
        if d_parsed.year < assert_min_year: # 보장해야하는 최소 년도보다 작은 경우 None 반환
            return None
        else:
            return d_parsed
    except: # 파싱이 불가능한 경우 None 반환
        return None


def get_time_diff(start_date, end_date, unit='second'): #유통기한과 Current time 차이
    """
    datetime 인스턴스의 시작과 종료일자를 받아 시간차이를 반환
    unit이 day인 경우 일수 차이 반환
    unit이 second 등일 경우 초 차이 반환
    """
    assert isinstance(start_date, pydatetime.datetime), 'start_date required datetime instance'
    assert isinstance(end_date,   pydatetime.datetime), 'end_date   required datetime instance'
    _timedelta = end_date - start_date
    if unit=='day':
        return abs(_timedelta.days)
    return abs((_timedelta.days * (_timedelta.max.seconds + 1)) + _timedelta.seconds)

#----------------------------------------------------------------------------------------------------------
# 유통기한 기반 레시피 추천
def recommend_expiration_date(my_stock):
    cur = datetime.datetime.now() #현재시간
    curDates = cur.strftime('%Y-%m-%d') #현재시간 day
    curDate = curDates.replace('-', '') #현재시간 데이터 처리
    this_stock = my_stock #내 재료
    # print(all_stocks)
    expiration_list = [] #유통기한 임박한 재료들의 id 리스트
    for stock in this_stock:
        # print(stock.expiration_date, type(stock.expiration_date))
        stock_time = str(stock.expiration_date).replace('-', '') #내 재료들의 유통기한을 stock_time
        ex_day = get_time_diff(parse_korean_type_date(curDate), parse_korean_type_date(stock_time), unit='day') #유통기한까지 남은 시간 '일'단위로 
        if ex_day < 5: #5일 미만이면
            expiration_list.append(stock.ingredient_id.id) #5일 미만 남은 재료들의 id를 배열에 추가
    # print(expiration_list)

    recommend_recipe_list = [] #추천 레시피 목록 배열
    all_recipes = Recipe.objects.all()
    for recipe in all_recipes:
        if not(recipe.ingredient_ids):
            continue
        ss = recipe.ingredient_ids.split(',')
        re_list = []
        for x in ss:
            re_list.append(int(x))
            # 유통기한이 얼마 안남은 재고가 모두 포함되는 레시피들을 담자
        if len(re_list) != 0 and len(set(expiration_list) - set(re_list)) == 0:
            if len(recommend_recipe_list) < 20:
                recommend_recipe_list.append(recipe.reci_id)
                # 리스트에 10개도 안담겼다면 유통기한이 얼마 안남은 재고중 하나를 제외하고 만들수 있는 레시피들을 추가로 담자
        if len(recommend_recipe_list) < 10:
            for recipe in all_recipes:
                if not (recipe.ingredient_ids):
                    continue
                ss = recipe.ingredient_ids.split(',')
                re_list = []
                for x in ss:
                    re_list.append(int(x))
                if len(re_list) != 0 and len(set(expiration_list) - set(re_list)) == 1:
                    if len(recommend_recipe_list) < 20:
                        recommend_recipe_list.append(recipe.reci_id)
    result = dict()
    result['ids'] = recommend_recipe_list

    return result
#-----------------------------------------------------------------------------------------------------------
# 랜덤으로 레시피 추천(만개의 레시피에서 인기레시피 100을 가져오면 우리가 파싱해온 레시피중에 없는게 있을수도 있어서 걍 랜덤으로 받음요)
def recommend_random():
    my_qset = Recipe.objects.all()
    my_list = list(my_qset)
    shuffle(my_list)
    recommend_recipe_list = []
    for item in my_list[:20]:
        print(item.reci_id)
        recommend_recipe_list.append(item.reci_id)
    result = dict()
    result['ids'] = recommend_recipe_list
    return result