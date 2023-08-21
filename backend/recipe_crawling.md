```python
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import json
import urllib.request

with open('/js/ingredient.json', 'r',encoding='UTF-8') as f:
    json_data = json.load(f)
    
new_dict = {}
for i in range(len(json_data)):
    new_list = []
    for k,v in json_data[i].items():
        new_list.append(v)
    new_dict[new_list[1]] = new_list[0]

def toJson(recipe_dict, title):
    file_path = '/js/recipe/' + title + '.json'
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(recipe_dict, file, ensure_ascii=False, indent='\t')

def url_func(n,m):
    url = 'https://www.10000recipe.com/recipe/list.html?order=reco&page='
    url_list = []
    
    for num in range(n,m):
        n_nrl = url + str(num)
        print(n_nrl)
        response = requests.get(n_nrl)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            res = soup.find(class_='common_sp_list_ul ea4')
            a = 1
            for i in res.find_all('a','common_sp_link'):
                url_tmp = i.get('href')
                print(num,a)
                a += 1
                url_list.append(url_tmp)
        except(AttributeError):
            pass
    return url_list

for url_str in url_lists:
    id_title = url_str.replace('/recipe/','') 
    url = 'https://www.10000recipe.com'
    url = url + url_str
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    try:
        res = soup.find('div', 'view2_summary')
        if not(res):
            continue
        res = res.find('h3')
        menu_name = res.get_text().replace('\n',' ').replace('"','')

        res = soup.find('div', 'centeredcrop')
        if not(res):
            continue
        res = res.find('img')
        menu_img = res.get('src')

        res = soup.find('div','ready_ingre3')
        if not(res):
            continue
        ingre_dict = {}
        ingre_list = []
        new_id = []
        try:
            for n in res.find_all('ul'):
                for tmp in n.find_all('li'):
                    ingredient_name = tmp.get_text().replace('\n','').replace(' ','')
                    count = tmp.find('span')
                    if not(count):
                        continue
                    ingredient_tmp = count.get_text()
                    ingredient_name = re.sub(ingredient_tmp, '',ingredient_name)
                    ingredient_unit = ingredient_tmp.replace('/','').replace('+','')
                    ingredient_unit = ''.join([i for i in ingredient_unit if not i.isdigit()])
                    ingredient_count = re.sub(ingredient_unit, '', ingredient_tmp)

                    ingre_dict = {"ingre_name": ingredient_name,
                                 "ingre_count": ingredient_count,
                                 "ingre_unit": ingredient_unit}

                    if ingredient_name in new_dict.keys():
                        new_id.append(new_dict[str(ingredient_name)])
                    ingre_list.append(ingre_dict)
        except:
            pass

        res = soup.find('span', 'view2_summary_info2')
        if not(res):
            continue
        time = res.get_text().replace('이내','').replace('분','').replace(' ','').replace('시간','')

        recipe_list = []
        recipe_dict = []
        recipe_imges = []
        res = soup.find('div','view_step')
        if not(res):
            continue
        ind = 1
        for n in res.find_all('div', 'view_step_cont', 'media-body'):
            recipe_step_txt = n.get_text().replace('\n',' ')
            recipe_dict = {"txt":recipe_step_txt}
            recipe_list.append(str(ind) + '. ' + recipe_step_txt)
            ind += 1

        for n in res.find_all('div', 'view_step_cont', 'media-right'):
            res = n.find('img')
            if not(res):
                continue
            recipe_imges.append(res.get('src'))


        food_dict = {"id":id_title,
                    "name":menu_name,
                    "thumbnail":menu_img,
                    "url":url,
                     "ingredient_ids":new_id,
                    "time":time,
                    "ingre_list":ingre_list,
                    "recipe":recipe_list,
                    "recipe_img":recipe_imges}
        toJson(food_dict, id_title)
    except:
            pass
```

