# encoding:utf-8
#!/usr/bin/python3

"""
 Copyright (c) 2023 ZeyuWu

 Permission is hereby granted, free of charge, to any person obtaining a copy of
 this software and associated documentation files (the "Software"), to deal in
 the Software without restriction, including without limitation the rights to
 use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
 the Software, and to permit persons to whom the Software is furnished to do so,
 subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 """

import json
import os

import select_citys
import get_data
import clean_data

# debug模式启动表示只对一个城市进行一次api请求
debug = False

# 接口地址
url = "https://api.map.baidu.com/place/v2/search"

# 此处填写你在控制台-应用管理-创建应用后获取的AK和SK
ak = "your AK"
sk = "your SK"

# regions = select_citys.province(['广东省','广西壮族自治区'])
regions = [
    "citys"
]
keyword = 'keyword'



def get_poi(base_dir:str = os.path.dirname(__file__)) -> str:
    """
    Args:
        base_dir (str, optional): Defaults to os.path.dirname(__file__).

    Returns:
        str: dir of putout
    """
    data_dir = os.path.join(base_dir, f"{keyword}_data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    all_data = []

    for region in regions:
        data = get_data.from_cities(url,ak,sk,keyword,region,debug)
        all_data.append(data)
        file_name = 'origin_data'+f'_{region}'+'.json'
        with open(os.path.join(data_dir,file_name), 'w',encoding='utf-8') as f:  
            json.dump(data, f,ensure_ascii=False,indent=4) 

    return data_dir
    
if __name__ == '__main__':
    # poi_data = get_poi()
    # checked_data = clean_data.check_data(f'{os.path.dirname(poi_data)}','all')
    # clean_data.repack(checked_data)

    file_data = clean_data.pack_up_data('医院_data')
    checked_data = clean_data.check_data('医院_data','all')
    clean_data.repack(checked_data)
    
