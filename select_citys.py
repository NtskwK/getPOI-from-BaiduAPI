import json

def province(provinces:list,fp:str=None) -> list:
    # 几年来行政区划分在村镇县层级有所变化
    # 但百度api仅支持市级检索
    # 所以暂时没有影响
    with open('./resource/city_object.json','r',encoding='utf-8') as f:
        all_cities =json.loads(f.read())

    city_list = []

    for city_id,city_info in all_cities.items():
        for province in provinces: 
            if city_info["province"] == province:
                city_list.append(city_info['name'])
                break

    if fp:
        with open(fp,'w',encoding='utf-8') as f:
            json.dump(city_list,f,indent=4,ensure_ascii=False)

    return city_list