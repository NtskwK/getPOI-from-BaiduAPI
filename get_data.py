import requests 
import json
import urllib
import hashlib

from urllib.parse import urlparse

def from_cities(url:str, ak:str, sk:str, keyword:str, region:str, debug:bool=False) -> dict:
    '''
    Args:
        url (str): Baidu API
        ak (str): Baidu API
        sk (str): Baidu API
        keyword (str): keyword of query
        regions (list): region of query
        debug (bool, optional): get data from first city once only. Defaults to False.

    Returns:
        list: poi data of the region
    '''
    page_num = 0
    data = {
        'results': []
    }
    keys = ['status','messages','total','poi_type']

    while True:
        data_dict = _request(url, ak, sk, keyword, region, page_num)
        print(data_dict)
        # 不正确的结果
        if not 'results' in data_dict.keys():
            print(data_dict['message'])
            quit()

        # 如果没有内容则说明已经到达到最大页数
        if len(data_dict['results']) == 0:
            # 重排序增强数据可读性
            data_keys = sorted(data, key=lambda k: len(str(data[k])))
            data_rebuild = {}
            for key in data_keys:
                data_rebuild[key] = data[key]
            return data_rebuild

        # 截取最后的信息
        for key in keys:
            if key in data_dict.keys():
                data[key] = data_dict[key]
        
        # 添加数据 
        data['province'] = data_dict['results'][0]['province']
        data['city'] = data_dict['results'][0]['city'] 
        for poi in data_dict['results']:
            data['results'].append(poi)
        
        # debug表示只请求一次
        if debug == True:
            with open('origin_data'+f'_debug'+'.json', 'w',encoding='utf-8') as f:  
                json.dump(data, f,ensure_ascii=False,indent=4)
            quit()
        
        page_num = page_num + 1

        


def _request(url:str, ak:str, sk:str, keyword:str, region:str, page_num:int) -> dict:
    
    params = {
                "ak":           ak,
                "query":        keyword,
                "region":       region,
                "city_limit":   True,
                "output":       "json",
                "scope":        2,
                "coord_type":   1,
                "page_size":    20,
                "page_num":     page_num,
                "address_result": True,
            }
    
    params['sn'] = _computer_sn(url, sk, params)

    #  参数说明
    #  https://lbs.baidu.com/faq/api?title=webapi/guide/webservice-placeapi

    response = requests.get(url=url, params=params)

    if response.status_code == 200:
        # 返回内容正确
        if response.json()['status'] == 0:
            return response.json()
        
        elif response.json()['status'] == 4 or response.json()['status'] == 302:
            print('账户余额不足！')

        # IP 和 SN 分别对应两种不同的校验方式
        elif response.json()['status'] == 210:
            print('IP校验失败!')
        elif response.json()['status'] == 211:
            print('SN校验失败!')
        elif response.json()['status'] == 252:
            print('该账户已被拉黑!')

        elif response.json()['status'] == 404:
            print('当前请求的资源不存在')
        elif response.json()['status'] == 261:
            print('该服务已下线!')
        print(f'unknow error:{response.json()["status"]}\nhttps://lbs.baidu.com/faq/api?title=webapi/appendix')

    # 尝试解释常见的api返回状态码，但不解释http响应状态码
    else:
        print(f'http error:{response.status_code}!')

    # 除了正常返回，其他都退出
    quit()



# sn计算方式
# https://lbs.baidu.com/faq/api?title=webapi/appendix

def _computer_sn(url:str, sk:str, params:dict) -> str:
    # 使用urlparse函数解析URL
    parsed_url = urlparse(url)

    # 提取出域名
    base_url = parsed_url.scheme + '://' + parsed_url.netloc

    # 获取域名部分之后的路由
    rest_of_url = url.replace(base_url, '')

    # 使用字符串操作方法将字典转换为查询字符串  
    queryStr = '?'
    for index, (key, value) in enumerate(params.items()):  
        queryStr = queryStr + f'{key}={value}'
        if not index == len(params.items()) - 1:
            queryStr = queryStr + '&'

    queryStr = rest_of_url + queryStr

    print(queryStr)

    # 对queryStr进行转码，safe内的保留字符不转换
    encodedStr = urllib.parse.quote(queryStr, safe='/:=&?#+!$,;"@()*[]')

    # 在最后直接追加上你的sk
    rawStr = encodedStr + sk
    
    return hashlib.md5(urllib.parse.quote_plus(rawStr).encode('utf-8')).hexdigest()