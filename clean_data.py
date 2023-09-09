import json
import os
import csv

rule = {}
# 优先级从上到下

# 空字符串代表规则不生效(不支持正则)
rule['default_include_keywords'] = ''
rule['default_exclude_keywords'] = ''

# 用,分隔开
rule['default_include_tags'] = ''
rule['default_exclude_tags'] = ''
rule['default_include_labels'] = ''
rule['default_exclude_labels'] = ''

# 空值填充
default_supplemental_label = ''
default_supplemental_tag = '' 

def pack_up_data(dir_name:str,keyword:str='origin_data_',putout_name:str='all_data.json') -> str:
    data_all = []
    if not os.path.exists(dir_name):
        raise FileExistsError
    files = os.listdir(dir_name)
    for file in files:
        if keyword in file:
            fp = os.path.join(dir_name,file)
            with open(fp,'r',encoding='utf-8') as f:
                data = json.loads(f.read())
                if (not 'results' in data.keys()) or len(data['results']) == 0:
                    print(f'不是有效的数据文件:\n{str(file)}')
                    continue

                data_all.append(data)

    if len(data_all) == 0:
        print('没有读取到有效的数据!\n{}'.format(dir_name))
        return ''

    fp = os.path.join(dir_name,putout_name)
    with open(fp,'w',encoding='utf-8') as f:
        json.dump(data_all,f,ensure_ascii=False,indent=4)

    return fp

def check_data(dir_name:str,prefix:str= '') -> str:
    all_poi = []
    all_unknow = []
    all_del = []

    files = os.listdir(dir_name)

    for file in files:
        # 只查找特定数据文件
        if prefix in file:
            datalist = _clean(os.path.join(dir_name,file))
            all_poi = all_poi.extend(datalist[0])
            all_del = all_del.extend(datalist[1])
            all_unknow = all_unknow.extend(datalist[2])

    with open(os.path.join(dir_name,'data' + '_check' + '.json'),'w',encoding='utf-8') as f:
        json.dump(all_poi,f,ensure_ascii=False,indent=4)

    with open(os.path.join(dir_name,'data' + '_del' + '.json'),'w',encoding='utf-8') as f:
        json.dump(all_del,f,ensure_ascii=False,indent=4)
    
    with open(os.path.join(dir_name,'data' + '_exclude' + '.json'),'w',encoding='utf-8') as f:
        json.dump(all_unknow,f,ensure_ascii=False,indent=4)

    return os.path.join(dir_name,'data' + '_check' + '.json')

# 这个函数写的超烂
def _clean(fp:str,
           include_keywords:str = rule['default_include_keywords'],
           exclude_keywords:str = rule['default_exclude_keywords'],
           include_tags:str = rule['default_include_tags'],
           include_labels:str = rule['default_include_labels'],
           exclude_tags:str = rule['default_exclude_tags'],
           exclude_labels:str = rule['default_exclude_labels'],         
           supplemental_label:str = default_supplemental_label,
           supplemental_tag:str = default_supplemental_tag
           ) -> tuple[list,list,list]:
    
    poi_list = []
    unknow_list = []
    del_list = []
    
    # 规则集为空时不进行过滤
    no_rule = True
    for key in rule.keys():
        if not len(rule[key]) == 0:
            no_rule = False
            break

    if no_rule :
        with open(fp,'r',encoding='utf-8') as f:
            data =json.loads(f.read())
        for city in data:
            poi_list.extend(city['results'])
        return poi_list,del_list,unknow_list
        

    with open(fp,'r',encoding='utf-8') as f:
        data =json.loads(f.read())
    for city in data:
        for poi in city['results']:
            # 关键词
            check_name = False
            if include_keywords in poi['name'] and len(include_keywords) != 0:
                poi_list.append(poi)
                check_name = True     
                continue
            else:
                if exclude_keywords in poi['name'] and len(exclude_keywords) != 0:
                    del_list.append(poi)
                    check_name = True     
                    continue

            # 没有tag也没有label
            if not 'tag' in poi['detail_info'].keys():
                if not 'label' in poi['detail_info'].keys():
                    unknow_list.append(poi)

            # 有tag
            check_tag = False
            if 'tag' in poi['detail_info'].keys():
                for tag in include_tags.split(','):
                    # 排除没有填筛选tag的情况
                    if tag in poi['detail_info']['tag'] and len(tag) != 0:
                        poi_list.append(poi)
                        check_tag = True     
                        break
                if not check_tag:
                    for tag in exclude_tags.split(','):
                        if tag in poi['detail_info']['tag'] and len(tag) != 0:
                            del_list.append(poi)
                            check_tag = True     
                            break
                
            # 有lable
            check_label = False
            if 'label' in poi['detail_info'].keys():
                for label in include_labels.split(','):
                    if label in poi['detail_info']['label'] and len(label) != 0:
                        poi_list.append(poi)
                        check_label = True     
                        break
                if not check_label:
                    for label in exclude_labels.split(','):
                        if label in poi['detail_info']['label'] and len(label) != 0:
                            poi_list.append(poi)
                            check_label = True     
                            break
            
            # 保底
            if not (check_label or check_tag or check_name):
                unknow_list.append(poi)

    return poi_list,del_list,unknow_list


def repack(fp:str,
           supplemental_tag:str=default_supplemental_tag, 
           supplemental_labels:str=default_supplemental_tag):

    with open(fp,'r',encoding='utf-8') as f:
        data =json.loads(f.read())

    data_repack = []

    for poi in data:
        poi_dict = {
            'name': poi['name'],
            'longitude': poi['location']['lng'],
            'latitude': poi['location']['lat'],
            'address': poi['address'],
            'province': poi['province'],
            'city': poi['city'],
        }

        try:
            poi_dict['label'] = poi['detail_info']['label']
        except Exception:
            poi_dict['label'] = supplemental_labels
        
        try:
            poi_dict['tag'] = poi['detail_info']['tag']
        except Exception:
            poi['tag'] = supplemental_tag
        
        data_repack.append(poi_dict)


    putout = os.path.join(os.path.dirname(fp),
                          os.path.splitext(os.path.basename(fp))[0] + '_pre' + '.csv')

    result = _to_csv(putout,data_repack[0].keys(),data_repack)

    return result


def _to_csv(fp:str,keys:list,data):
    try:
        with open(fp, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)

            writer.writeheader()
            for row in data:
                writer.writerow(row)
    except IndexError:
        print(f'不正确的数据!\n{fp}!')

# todo
# 将距离太近的点去除
def deduplcation(fp:str,encode:str='utf-8',distance:int=100,putout_name='') -> str:
    if not os.path.exists(fp):
        raise FileExistsError
    
    data_ded = []
    p_set = {}

    with open(fp,'r',encoding=encode) as f:
        data_all = json.load(f.read())
        for poi in data_all:
            # 距离小于0.001的将被视为同一地物
            coordinate = [int(poi['detail_info']['navi_location']['lng']*100000 / distance),
                          int(poi['detail_info']['navi_location']['lat']*100000 / distance)]
            if not coordinate in p_set:
                p_set.add(coordinate)
                data_ded.append(poi)

        if putout_name == '':
            fp = os.path.join(os.path.dirname(fp),putout_name)
        else:
            fp = os.path.splitext(fp)(0) + '_ded' + os.path.splitext(fp)(1)
            
        with open(fp,'w',encoding='utf-8') as f:
            json.dump(data_ded,f,ensure_ascii=False,indent=4)

    return fp