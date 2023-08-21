```python
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import json
import urllib.request

def recommend_max_ingredient(my_stock): #최대한 재료를 소비할 수 있는 로직
    GapofDuplicated_ingredients = 0
    all_recipes = Recipe.objects.all() #모든 레시피 
    recommend_recipe_id_list = [] #추천 레시피 아이디 배열
    stock_list = my_stock #내 재료 stock_list 배열에
    stock_id_list = [] #재료 목록
    for stock in stock_list:
        stock_id_list.append(stock.ingredient_id.id) # #내 재료에 있는 재료들의 id 재료 목록에 추가

    while len(recommend_recipe_id_list) <= 30 or GapofDuplicated_ingredients < len(set(stock_id_list))/2:
    #추천 레시피의 갯수가 30개가 되거나 30개가 안 됐을 때에도 재료 절반이상 소비할 수 있을 때까지만
        for recipe in all_recipes:
            if not(recipe.ingredient_ids): #id 일치하지 않으면 넘김
                continue

            split_ingredient_list = recipe.ingredient_ids.split(',') #각 id를 ,로 구분
            recommend_ingre_list = [] # 추천 레시피의 재료 id 리스트

            for x in split_ingredient_list: #,로 구분해놓은 재료들 목록에 있는 id들 각 항목에 대하여
                recommend_ingre_list.append(int(x)) #각 id들을 re_list에 저장

            if len(recommend_ingre_list) != 0 :
                if len(set(stock_id_list) - set(recommend_ingre_list)) <= GapofDuplicated_ingredients:#재료들 모두 소비할 수 있으면 (내 재료 - 레시피 재료) GapofDuplicated_ingredients (겹치는 재료 뺀 값이 0)
                    recommend_recipe_id_list.append(recipe.reci_id) #리스트에 레시피 id추가하면 중지

            # 모든 레시피 1번 검색이 끝나면 허용치 1늘림 (허용치: 냉장고에 남아도 되는 재료의 종류 갯수)
            if len(recommend_recipe_id_list) > 30: break #모든 레시피 돌면서 30개를 일찍 찾았을 경우 빠르게 루프 탈출
        GapofDuplicated_ingredients += 1 #최대한 재료를 소비할 수 있도록 겹치지지 않는 재료 수를 1개씩 허용하며 검색
            
    result = {}
    result['ids'] = recommend_recipe_id_list
    return result

#--------------------------------------------------------------------------------------------------
def parse_korean_type_date(d, MinYear=1900): #한국 서버 시간 반환 
    """
    날짜문자열(년도가 앞, 일자가 뒤 형태)을 입력받아 datetime 인스턴스를 반환
    파싱이 불가능한 경우 또는 assert_min_year년도 이전인 경우 None 반환
    """
    try:
        d_parsed = dateparse(d, yearfirst=True, dayfirst=False)
        if d_parsed.year < MinYear: 
            return None
        else:
            return d_parsed
    except: 
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

#-------------------------------------------------------------------------------------------------

def recommend_expiration_date(my_stock):
    cur = datetime.datetime.now() #현재시간
    curDates = cur.strftime('%Y-%m-%d') #현재시간 day
    curDate = curDates.replace('-', '') #현재시간 데이터 처리
    stock_list = my_stock #내 재료
    
    expiration_count = 2
    GapofDuplicated_ingredients = 0 #내 재료 - 레시피에 필요한 재료
    priority = 0 #유통기한과 겹치는 재료들간의 우선순위 (유통기한 짧으면 유통기한 우선) (유통기한 어느정도 이상이면 재료 우선)
    ex_URGENT_my_id_list = [] #유통기한이 임박한 내 재료들의 id 리스트 (1,2일) (우선순위 높음) 
    ex_my_id_list = [] #유통기한 내의 내 재료들의 id 리스트
    recommend_recipe_list = [] #추천 레시피 목록 배열
    

    while len(recommend_recipe_id_list) <= 30 or expiration_count < 14:
        #추천 레시피의 갯수가 30개 이상이고 유통기한 14일 내의 재료를 처리할 수 있으면
        
        for stock in stock_list: #유통기한 n(expiration_count)일 남은 재료들 id 추가
            stock_time = str(stock.expiration_date).replace('-', '') #내 재료들의 유통기한을 stock_time
            ex_date = get_time_diff(parse_korean_type_date(curDate), parse_korean_type_date(stock_time), unit='day') #유통기한까지 남은 시간 '일'단위로 
            if ex_date < expiration_count: 
                ex_my_id_list.append(stock.ingredient_id.id) #n일 미만 남은 재료들의 id를 배열에 추가 (2일부터 시작)
                if ex_date <= 2: #유통기한 2일이하 남은 재료들은
                    ex_URGENT_my_id_list.append(stock.ingredient_id.id)
            
#------------여기까지 유통기한 체크--------------아래부터 레시피 추가하는 로직------------
        all_recipes = Recipe.objects.all()
        for recipe in all_recipes:
            if not(recipe.ingredient_ids):
                continue
            split_ingredient_list = recipe.ingredient_ids.split(',')
            recommend_ingre_list = [] 

            for x in split_ingredient_list:
                recommend_ingre_list.append(int(x))
        
            GapofDuplicated_ingredients = 0

            if len(recommend_ingre_list) != 0: #추천 레시피 재료가 존재하는 경우
                if len(set(ex_URGENT_my_id_list) - set(recommend_ingre_list)) == 0:
                    recommend_recipe_list.append(recipe.reci_id)
                        
                elif priority == 1 and len(set(ex_URGENT_my_id_list) - set(recommend_ingre_list)) == 0:

                    while GapofDuplicated_ingredients < 3:
                        if len(set(ex_my_id_list) - set(recommend_ingre_list)) <= GapofDuplicated_ingredients:
                            recommend_recipe_list.append(recipe.reci_id)
                            break
                        else
                            GapofDuplicated_ingredients += 1
                            
            if len(recommend_recipe_id_list) > 30: #모든 레시피를 다 검색하기 전에 30개 채우면 루프 빠른 통과
                break

        expiration_count += 1

        if expiration_count >= 7:
            priority = 1

        elif expiration_count == 14: break #30개를 채우지 못 할 경우 유통기한 2주까지 확인해보고 루프 나가기

    result = dict()
    result['ids'] = recommend_recipe_list

    return result
