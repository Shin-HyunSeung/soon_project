from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
import urllib
import json
from haversine import haversine
import pandas as pd
import random
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer  # 피체 벡터화
from sklearn.metrics.pairwise import cosine_similarity  # 코사인 유사도
from urllib.parse import unquote_plus
import re
# Create your views here.
def index(request):

    return render(request, 'soonfood_app/base.html')


def food(request):
    all_obs = soon_food.objects.all()
    get_cat = request.get_full_path()
    get_cat = urllib.parse.unquote(get_cat).split('cate=')[1]
    object_cat = soon_food.objects.filter(categori = get_cat)
    cnt_object_cat = len(object_cat)
    rand_lst = []
    select_cate_list = []
    

    [rand_lst.append(random.randrange(cnt_object_cat)) for i in range(10)]
    [select_cate_list.append(object_cat[a]) for a in set(rand_lst)]


    return render(request, 'soonfood_app/foodbase.html', {'all_ob' : all_obs,'get_cat':get_cat, 'select_cate_list':select_cate_list})

def df_btn_click(request):
    return HttpResponseRedirect(reverse(index))
    # return HttpResponse('hihi')

def random_cate(request):
    all_tours = tourlist.objects.all()
    all_obs = soon_food.objects.all()

    get_cat = request.get_full_path()
    get_cat = urllib.parse.unquote(get_cat).split('cate=')[1]
    cate_food_lst = soon_food.objects.filter(categori=get_cat)
    food_num = len(cate_food_lst) 
    food_random = random.randrange(food_num)
    ran_food = cate_food_lst[food_random]

    tours_res = []
    tours_lat = []
    tours_long = []
    tours_address = []
    tours_real_address = []
    obs_address = []
    haver_list=[]

    [tours_res.append(str(tour.restaurant)) for tour in all_tours] # 관광지 이름 데이터
    [tours_lat.append(str(tour.lat)) for tour in all_tours] # 관광지 위도 데이터
    [tours_long.append(str(tour.long)) for tour in all_tours] #관광지 경도 데이터
    [tours_address.append([tour.lat, tour.long]) for tour in all_tours] #관광지 위도 경도 데이터
    [tours_real_address.append(str(tour.address)) for tour in all_tours] #관광지 경도 데이터

    obs_address.append(ran_food.lat)
    obs_address.append(ran_food.long)

    [haver_list.append(haversine(obs_address, tours, unit='km')) for tours in tours_address]
    tours_data = pd.DataFrame({
        '관광지':tours_res,
        '위도':tours_lat,
        '경도':tours_long,
        '사이거리':haver_list,
        '주소':tours_real_address
    })
    tours_data = tours_data[tours_data['사이거리'] < 5]

    data_tours_res = [i for i in tours_data['관광지']]
    data_tours_lat = [i for i in tours_data['위도']]
    data_tours_long = [i for i in tours_data['경도']]
    data_tours_address = [i for i in tours_data['주소']]

    res_name = []
    res_menu = []
    res_sig_menu = []
    [res_name.append(obs.restaurant) for obs in all_obs]
    [res_menu.append(obs.menu) for obs in all_obs]
    [res_sig_menu.append(obs.sig_menu) for obs in all_obs]
    res_data = pd.DataFrame({
        '식당명':res_name,
        '메뉴':res_menu,
        '대표메뉴':res_sig_menu
    })
    

    # 시그니처 메뉴 텍스트 데이터 간의 텍스트 피쳐 벡터라이징
    count_vect_sig_menu = CountVectorizer(min_df=2, ngram_range=(1,2))
    place_sig_menu = count_vect_sig_menu.fit_transform(res_data['대표메뉴']) 
    # 시그니처 메뉴 텍스트 간의 코사인 유사도 따지기
    place_simi_sig_menu = cosine_similarity(place_sig_menu, place_sig_menu) 
    place_simi_sig_menu_sorted_ind = place_simi_sig_menu.argsort()[:, ::-1]

    # 메뉴 텍스트 데이터 간의 텍스트 피쳐 벡터라이징
    count_vect_menu = CountVectorizer(min_df=2, ngram_range=(1,2))
    place_menu = count_vect_menu.fit_transform(res_data['메뉴']) 
    # 메뉴 텍스트 간의 코사인 유사도 따지기
    place_simi_menu = cosine_similarity(place_menu, place_menu)
    place_simi_menu_sorted_ind = place_simi_menu.argsort()[:, ::-1]

    place_simi_co = (
        + place_simi_sig_menu * 0.3 # 공식 1. 시그니처 메뉴 유사도
        + place_simi_menu * 0.7 # 공식 2. 메뉴 텍스트 유사도
    )
    place_simi_co_sorted_ind = place_simi_co.argsort()[:, ::-1] 

    place_title = res_data[res_data['식당명'] == ran_food.restaurant]
    place_index = place_title.index.values
    similar_indexes = place_simi_co_sorted_ind[place_index, :(4)]
    similar_indexes = similar_indexes.reshape(-1)
    
    sug_food = res_data.iloc[similar_indexes]
    sug_food_name = []
    # sug_food_menu = []
    sug_food_sig = []
    [sug_food_name.append(name) for name in sug_food['식당명']]
    # [sug_food_menu.append(menu) for menu in sug_food['메뉴']]
    [sug_food_sig.append(sig) for sig in sug_food['대표메뉴']]
    return render(request, 'soonfood_app/random_cate_base.html', {'get_cat' : get_cat, 'ran_food':ran_food,'data_tours_address':data_tours_address,'data_tours_res':data_tours_res,'data_tours_lat':data_tours_lat,'data_tours_long':data_tours_long,'sug_food_name_1':sug_food_name[1],'sug_food_name_2':sug_food_name[2],'sug_food_name_3':sug_food_name[3],'sug_food_sig_1':sug_food_sig[1],'sug_food_sig_2':sug_food_sig[2],'sug_food_sig_3':sug_food_sig[3]})

def search_food_btn(request):
    all_obs = soon_food.objects.all()
    all_tours = tourlist.objects.all()
    search_contetns = request.GET.get('main_search')
    
    select_food = soon_food.objects.filter(restaurant = search_contetns)[0]
    tours_res = []
    tours_lat = []
    tours_long = []
    tours_address = []
    tours_real_address = []
    obs_address = []
    haver_list=[]

    [tours_res.append(str(tour.restaurant)) for tour in all_tours] # 관광지 이름 데이터
    [tours_lat.append(str(tour.lat)) for tour in all_tours] # 관광지 위도 데이터
    [tours_long.append(str(tour.long)) for tour in all_tours] #관광지 경도 데이터
    [tours_address.append([tour.lat, tour.long]) for tour in all_tours] #관광지 위도 경도 데이터
    [tours_real_address.append(str(tour.address)) for tour in all_tours] #관광지 경도 데이터

    obs_address.append(select_food.lat)
    obs_address.append(select_food.long)
    # print(select_food[0].restaurant)

    [haver_list.append(haversine(obs_address, tours, unit='km')) for tours in tours_address]
    tours_data = pd.DataFrame({
        '관광지':tours_res,
        '위도':tours_lat,
        '경도':tours_long,
        '사이거리':haver_list,
        '주소':tours_real_address
    })
    tours_data_5 = tours_data[tours_data['사이거리'] < 5]

    data_tours_res = [i for i in tours_data_5['관광지']]
    data_tours_lat = [i for i in tours_data_5['위도']]
    data_tours_long = [i for i in tours_data_5['경도']]
    data_tours_address = [i for i in tours_data_5['주소']]


    res_name = []
    res_menu = []
    res_sig_menu = []
    [res_name.append(obs.restaurant) for obs in all_obs]
    [res_menu.append(obs.menu) for obs in all_obs]
    [res_sig_menu.append(obs.sig_menu) for obs in all_obs]
    res_data = pd.DataFrame({
        '식당명':res_name,
        '메뉴':res_menu,
        '대표메뉴':res_sig_menu
    })
    

    # 시그니처 메뉴 텍스트 데이터 간의 텍스트 피쳐 벡터라이징
    count_vect_sig_menu = CountVectorizer(min_df=2, ngram_range=(1,2))
    place_sig_menu = count_vect_sig_menu.fit_transform(res_data['대표메뉴']) 
    # 시그니처 메뉴 텍스트 간의 코사인 유사도 따지기
    place_simi_sig_menu = cosine_similarity(place_sig_menu, place_sig_menu) 
    place_simi_sig_menu_sorted_ind = place_simi_sig_menu.argsort()[:, ::-1]

    # 메뉴 텍스트 데이터 간의 텍스트 피쳐 벡터라이징
    count_vect_menu = CountVectorizer(min_df=2, ngram_range=(1,2))
    place_menu = count_vect_menu.fit_transform(res_data['메뉴']) 
    # 메뉴 텍스트 간의 코사인 유사도 따지기
    place_simi_menu = cosine_similarity(place_menu, place_menu)
    place_simi_menu_sorted_ind = place_simi_menu.argsort()[:, ::-1]

    place_simi_co = (
        + place_simi_sig_menu * 0.3 # 공식 1. 시그니처 메뉴 유사도
        + place_simi_menu * 0.7 # 공식 2. 메뉴 텍스트 유사도
    )
    place_simi_co_sorted_ind = place_simi_co.argsort()[:, ::-1] 

    place_title = res_data[res_data['식당명'] == select_food.restaurant]
    place_index = place_title.index.values
    similar_indexes = place_simi_co_sorted_ind[place_index, :(4)]
    similar_indexes = similar_indexes.reshape(-1)
    
    sug_food = res_data.iloc[similar_indexes]
    sug_food_name = []
    # sug_food_menu = []
    sug_food_sig = []
    [sug_food_name.append(name) for name in sug_food['식당명']]
    # [sug_food_menu.append(menu) for menu in sug_food['메뉴']]
    [sug_food_sig.append(sig) for sig in sug_food['대표메뉴']]
    # print(similar_indexes)
    # print(place_simi_co)

    return render(request, 'soonfood_app/random_cate_base.html', {'ran_food':select_food,'data_tours_address':data_tours_address, 'data_tours_res':data_tours_res,'data_tours_lat':data_tours_lat,'data_tours_long':data_tours_long,'sug_food_name_1':sug_food_name[1],'sug_food_name_2':sug_food_name[2],'sug_food_name_3':sug_food_name[3],'sug_food_sig_1':sug_food_sig[1],'sug_food_sig_2':sug_food_sig[2],'sug_food_sig_3':sug_food_sig[3],'sug_food_name':sug_food_name,'sug_food_sig':sug_food_sig})

def detail_content(request):

    get_res = request.get_full_path()
    get_res = get_res.split('select_detail/?=')[1]
    get_res = unquote_plus(get_res)

    all_obs = soon_food.objects.all()
    all_tours = tourlist.objects.all()
    select_food = soon_food.objects.filter(restaurant = get_res)[0]
    tours_res = []
    tours_lat = []
    tours_long = []
    tours_address = []
    tours_real_address = []
    obs_address = []
    haver_list=[]

    [tours_res.append(str(tour.restaurant)) for tour in all_tours] # 관광지 이름 데이터
    [tours_lat.append(str(tour.lat)) for tour in all_tours] # 관광지 위도 데이터
    [tours_long.append(str(tour.long)) for tour in all_tours] #관광지 경도 데이터
    [tours_real_address.append(str(tour.address)) for tour in all_tours] #관광지 경도 데이터
    [tours_address.append([tour.lat, tour.long]) for tour in all_tours] #관광지 위도 경도 데이터
    obs_address.append(select_food.lat)
    obs_address.append(select_food.long)
    # print(select_food[0].restaurant)

    [haver_list.append(haversine(obs_address, tours, unit='km')) for tours in tours_address]
    tours_data = pd.DataFrame({
        '관광지':tours_res,
        '위도':tours_lat,
        '경도':tours_long,
        '사이거리':haver_list,
        '주소':tours_real_address
    })
    tours_data_5 = tours_data[tours_data['사이거리'] < 5]

    data_tours_res = [i for i in tours_data_5['관광지']]
    data_tours_lat = [i for i in tours_data_5['위도']]
    data_tours_long = [i for i in tours_data_5['경도']]
    data_tours_address = [i for i in tours_data_5['주소']]


    res_name = []
    res_menu = []
    res_sig_menu = []
    [res_name.append(obs.restaurant) for obs in all_obs]
    [res_menu.append(obs.menu) for obs in all_obs]
    [res_sig_menu.append(obs.sig_menu) for obs in all_obs]
    res_data = pd.DataFrame({
        '식당명':res_name,
        '메뉴':res_menu,
        '대표메뉴':res_sig_menu
    })
    

    # 시그니처 메뉴 텍스트 데이터 간의 텍스트 피쳐 벡터라이징
    count_vect_sig_menu = CountVectorizer(min_df=2, ngram_range=(1,2))
    place_sig_menu = count_vect_sig_menu.fit_transform(res_data['대표메뉴']) 
    # 시그니처 메뉴 텍스트 간의 코사인 유사도 따지기
    place_simi_sig_menu = cosine_similarity(place_sig_menu, place_sig_menu) 
    place_simi_sig_menu_sorted_ind = place_simi_sig_menu.argsort()[:, ::-1]

    # 메뉴 텍스트 데이터 간의 텍스트 피쳐 벡터라이징
    count_vect_menu = CountVectorizer(min_df=2, ngram_range=(1,2))
    place_menu = count_vect_menu.fit_transform(res_data['메뉴']) 
    # 메뉴 텍스트 간의 코사인 유사도 따지기
    place_simi_menu = cosine_similarity(place_menu, place_menu)
    place_simi_menu_sorted_ind = place_simi_menu.argsort()[:, ::-1]

    place_simi_co = (
        + place_simi_sig_menu * 0.3 # 공식 1. 시그니처 메뉴 유사도
        + place_simi_menu * 0.7 # 공식 2. 메뉴 텍스트 유사도
    )
    place_simi_co_sorted_ind = place_simi_co.argsort()[:, ::-1] 

    place_title = res_data[res_data['식당명'] == select_food.restaurant]
    place_index = place_title.index.values
    similar_indexes = place_simi_co_sorted_ind[place_index, :(4)]
    similar_indexes = similar_indexes.reshape(-1)
    
    sug_food = res_data.iloc[similar_indexes]
    sug_food_name = []
    # sug_food_menu = []
    sug_food_sig = []
    [sug_food_name.append(name) for name in sug_food['식당명']]
    # [sug_food_menu.append(menu) for menu in sug_food['메뉴']]
    [sug_food_sig.append(sig) for sig in sug_food['대표메뉴']]
    # print(place_simi_co)

    return render(request, 'soonfood_app/random_cate_base.html', {'ran_food':select_food, 'data_tours_address':data_tours_address,'data_tours_res':data_tours_res,'data_tours_lat':data_tours_lat,'data_tours_long':data_tours_long,'sug_food_name_1':sug_food_name[1],'sug_food_name_2':sug_food_name[2],'sug_food_name_3':sug_food_name[3],'sug_food_sig_1':sug_food_sig[1],'sug_food_sig_2':sug_food_sig[2],'sug_food_sig_3':sug_food_sig[3],'sug_food_name':sug_food_name,'sug_food_sig':sug_food_sig})

def menu_lst(request):
    all_obs = soon_food.objects.all()
    all_tours = tourlist.objects.all()
    get_res = request.get_full_path()
    get_res = get_res.split('res=')[1]
    get_res = unquote_plus(get_res)
    get_object = soon_food.objects.filter(restaurant = get_res)[0]
    
    tours_res = []
    tours_lat = []
    tours_long = []
    tours_address = []
    tours_real_address = []
    obs_address = []
    haver_list=[]

    [tours_res.append(str(tour.restaurant)) for tour in all_tours] # 관광지 이름 데이터
    [tours_lat.append(str(tour.lat)) for tour in all_tours] # 관광지 위도 데이터
    [tours_long.append(str(tour.long)) for tour in all_tours] #관광지 경도 데이터
    [tours_real_address.append(str(tour.address)) for tour in all_tours] #관광지 경도 데이터
    [tours_address.append([tour.lat, tour.long]) for tour in all_tours] #관광지 위도 경도 데이터
    obs_address.append(get_object.lat)
    obs_address.append(get_object.long)

    [haver_list.append(haversine(obs_address, tours, unit='km')) for tours in tours_address]
    tours_data = pd.DataFrame({
        '관광지':tours_res,
        '위도':tours_lat,
        '경도':tours_long,
        '사이거리':haver_list,
        '주소':tours_real_address
    })
    tours_data = tours_data[tours_data['사이거리'] < 5]

    data_tours_res = [i for i in tours_data['관광지']]
    data_tours_lat = [i for i in tours_data['위도']]
    data_tours_long = [i for i in tours_data['경도']]
    data_tours_address = [i for i in tours_data['주소']]


    res_name = []
    res_menu = []
    res_sig_menu = []
    [res_name.append(obs.restaurant) for obs in all_obs]
    [res_menu.append(obs.menu) for obs in all_obs]
    [res_sig_menu.append(obs.sig_menu) for obs in all_obs]
    res_data = pd.DataFrame({
        '식당명':res_name,
        '메뉴':res_menu,
        '대표메뉴':res_sig_menu
    })

    price = get_object.price
    price_list = []
    [price_list.append(i) for i in price.split('.')]
    

    return render(request, 'soonfood_app/detail_menu.html', {'get_object':get_object,'data_tours_address':data_tours_address,'get_res' : get_res, 'ran_food':get_object,'data_tours_res':data_tours_res,'data_tours_lat':data_tours_lat,'data_tours_long':data_tours_long,'price_list':price_list})

def check_food(request):
    get_res = request.GET.getlist('chk_info')
    all_obs = soon_food.objects.all() # 모든 음식점
    all_tours = tourlist.objects.all() # 모든 관광지
    select_res_lat = [] #셀렉한 음식점 위도
    select_res_long = [] # 셀렉한 음식점 경도
    select_res = []
    select1_address = []
    select2_address = []
    tours_res = []
    tours_lat = []
    tours_long = []
    tours_address = []
    tours_real_address = []
    res1_haver = [] # 음식점1과 관광지들 사이거리
    res2_haver = [] # 음식점2와 관광지들 사이거리
    select_res_info = []
    
    [select_res_lat.append(obs.lat) for obs in all_obs if (obs.restaurant == get_res[0]) or (obs.restaurant == get_res[1])]
    [select_res_long.append(obs.long) for obs in all_obs if (obs.restaurant == get_res[0]) or (obs.restaurant == get_res[1])]
    [select_res.append(obs.restaurant) for obs in all_obs if (obs.restaurant == get_res[0]) or (obs.restaurant == get_res[1])]
    [select_res_info.append(obs) for obs in all_obs if (obs.restaurant == get_res[0]) or (obs.restaurant == get_res[1])]
    [tours_res.append(str(tour.restaurant)) for tour in all_tours] # 관광지 이름 데이터
    [tours_lat.append(str(tour.lat)) for tour in all_tours] # 관광지 위도 데이터
    [tours_long.append(str(tour.long)) for tour in all_tours] #관광지 경도 데이터
    [tours_address.append([tour.lat, tour.long]) for tour in all_tours] #관광지 위도 경도 데이터
    [tours_real_address.append(str(tour.address)) for tour in all_tours] #관광지 경도 데이터

    median_lat = (select_res_lat[0] + select_res_lat[1])/2
    median_long = (select_res_long[0] + select_res_long[1])/2

    
    select1_address.append(select_res_lat[0])
    select1_address.append(select_res_long[0])
    select2_address.append(select_res_lat[1])
    select2_address.append(select_res_long[1])
    haver = haversine(select1_address, select2_address, unit='km') # 두 음식점 사이 거리

    for tours in tours_address:
        res1_haver.append(haversine(select1_address, tours, unit='km'))
        res2_haver.append(haversine(select2_address, tours, unit='km')) 

    tours_data1 = pd.DataFrame({
        '관광지':tours_res,
        '위도':tours_lat,
        '경도':tours_long,
        '사이거리':res1_haver,
        '주소':tours_real_address
    })

    tours_data2 = pd.DataFrame({
        '관광지':tours_res,
        '위도':tours_lat,
        '경도':tours_long,
        '사이거리':res2_haver,
        '주소':tours_real_address
    })

    tours_data1 = tours_data1[tours_data1['사이거리'] < haver]
    tours_data2 = tours_data2[tours_data2['사이거리'] < haver]
    tours1_list = []
    tours2_list = []
    real_tourlist = []
    [tours1_list.append(tours) for tours in tours_data1['관광지']]
    [tours2_list.append(tours) for tours in tours_data2['관광지']]
    [real_tourlist.append(i) for i in tours1_list if i in tours2_list]

    data = tours_data1[tours_data1['관광지'].isin(real_tourlist)]

    data_tours_res = [i for i in data['관광지']]
    data_tours_lat = [i for i in data['위도']]
    data_tours_long = [i for i in data['경도']]
    data_tours_address = [i for i in data['주소']]

    str_select_res_lat = []
    str_select_res_long  = []
    
    [str_select_res_lat.append(str(i)) for i in select_res_lat]
    [str_select_res_long.append(str(i)) for i in select_res_long]
    return render(request, 'soonfood_app/check_food_info.html', {'median_lat':median_lat,'data_tours_address':data_tours_address,'get_res':select_res_info, 'median_long':median_long, 'data_tours_res':data_tours_res, 'data_tours_lat':data_tours_lat, 'data_tours_long':data_tours_long,'select_res1':select_res[0],'select_res2':select_res[1],'select_res_lat':str_select_res_lat,'select_res_long':str_select_res_long,'select_res':select_res})

def select_food(request):
    select_food = request.GET.get('select_food_btn')
    print(select_food)
    return render(request, 'soonfood_app/base.html')