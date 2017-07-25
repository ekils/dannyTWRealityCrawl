#coding=utf-8

import sqlite3
import re
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from colour import Color
import os.path
import folium
from folium.plugins import MarkerCluster
import geocoder
from geopy.exc import GeocoderTimedOut
import webbrowser







class Analysis:

    def __init__(self):
        global dat
        global  datafile
        global origin_path
        dat= raw_input("Enter .db file name to Plot: ")
        datafile= dat+'.db'
        origin_path= os.getcwd()
        os.chdir('/Users/bobobo746/Desktop/stuff/python/Test/RealityCrawl')

        conn = sqlite3.connect(datafile)

        # DataFrame的排序方式是依照月 由大排到小：
        global df
        df = pd.read_sql("select * from SINYI_COLUMNS order by {} desc ".format('月'), con=conn)


    # plot_Trend:

        # 要踢掉字串的欄位：
        global Jianpin
        global ZongJia
        global MeiPingDanJia
        global month
        global pat_BZ2_1
        global pat_BZ2_2
        global Beizhu1
        Jianpin = [float(i) for i in df['建坪'].str.strip(u'坪')]
        ZongJia = [float(i) for i in df['總價'].str.strip(u'萬')]
        MeiPingDanJia = [float(i) for i in df['每坪單價'].str.strip(u'萬')]
        month = [int(i) for i in df['月'].str.strip(u'月')]
        Beizhu1=[i.encode('utf-8') for i in df['備註一']]
        pat_BZ2_1 = re.compile(u',.*坪,')
        pat_BZ2_2 = re.compile(u'...萬')


        # 創建 12個月份的空矩陣,第一個為0月份,所以沒用
        global M
        M = []
        for i in range(13):
            M_i = []
            M.append(M_i)
        get_current_month = month[0]
        for i, l in enumerate(month):
            (M[l]).append(MeiPingDanJia[i])  # 依照找到的月份丟到空集合去


        # 針對備註二的車位坪數做扣除 ：
        for i in range(len(df['備註二'])):

            if df['備註二'][i] == u'無車位 ':
                # print '無車位'
                pass
            else:
                try:
                    BZ2_1 = pat_BZ2_1.search(df['備註二'][i]).group()
                    try:
                        BZ2_1 = float(BZ2_1.strip(u'坪,'))
                        # print BZ2_1
                    except:
                        BZ2_1 = 0.0
                        # print BZ2_1
                    Jianpin[i] = Jianpin[i] - BZ2_1
                except:
                    BZ2_1 = 0.0
                    Jianpin[i] = Jianpin[i] - BZ2_1
                try:
                    BZ2_2 = pat_BZ2_2.search(df['備註二'][i]).group()
                    try:
                        BZ2_2 = float(BZ2_2.strip(u' 萬'))
                        ZongJia[i] = ZongJia[i] - BZ2_2
                    except:
                        BZ2_2 = (BZ2_2.strip(u' 萬'))
                        BZ2_2 = float(BZ2_2.strip(u','))
                        ZongJia[i] = ZongJia[i] - BZ2_2
                        # print BZ2_2
                except:
                    BZ2_2 = 0.0
                    # print BZ2_2
                    ZongJia[i] = ZongJia[i] - BZ2_2

                MeiPingDanJia[i] = round(float(ZongJia[i] / Jianpin[i]), 1)

    # plot_Pie_Type:

        # 派圖 房子類型：

        BT = [u'大樓', u'華廈', u'公寓', u'透天厝', u'套房',u'店面']
        global Pie_for_BuildingType
        Pie_for_BuildingType = []
        for i in range(len(BT)):
            B_i = []
            Pie_for_BuildingType.append(B_i)

        pat_Building_0 = re.compile(u'{}'.format(BT[0]))
        pat_Building_1 = re.compile(u'{}'.format(BT[1]))
        pat_Building_2 = re.compile(u'{}'.format(BT[2]))
        pat_Building_3 = re.compile(u'{}'.format(BT[3]))
        pat_Building_4 = re.compile(u'{}'.format(BT[4]))
        pat_Building_5 = re.compile(u'{}'.format(BT[5]))
        pat_Building_6 = re.compile(u'多層樓組合')

        Lexing = [i for i in df['類型']]

        for i, l in enumerate(Lexing):
            if pat_Building_0.search(l) != None:
                Pie_for_BuildingType[0].append(l)
            elif pat_Building_1.search(l) != None:
                Pie_for_BuildingType[1].append(l)
            elif pat_Building_2.search(l) != None:
                Pie_for_BuildingType[2].append(l)
            elif pat_Building_3.search(l) != None:
                Pie_for_BuildingType[3].append(l)
            elif pat_Building_4.search(l) != None:
                Pie_for_BuildingType[4].append(l)
            elif pat_Building_5.search(l) != None:
                Pie_for_BuildingType[5].append(l)
            elif pat_Building_6.search(l) != None:
                Pie_for_BuildingType[4].append(l)
            else:
                print 'Error of BuildingType: {}'.format(l)

        # 派圖 單價類型：

        PT = ['600K Upper','450~600K','300~450K','150~300K','Lower 150k']
        global Pie_for_PriceType
        Pie_for_PriceType = []
        for i in range(len(PT)):
            p_i = []
            Pie_for_PriceType.append(p_i)
        for i,l in  enumerate(MeiPingDanJia):
            if l> 60.0:
                Pie_for_PriceType[0].append(l)
            elif 45.0< l <= 60.0:
                Pie_for_PriceType[1].append(l)
            elif 30.0< l <= 45.0:
                Pie_for_PriceType[2].append(l)
            elif 15.0< l <= 30.0:
                Pie_for_PriceType[3].append(l)
            elif l <= 15.0 :
                Pie_for_PriceType[4].append(l)
            else:
                print 'Error of PriceType: {}'.format(l)

        # 派圖 總價類型：

        TT = ['20M Upper','15~20M','10~15M','5~10M','Lower 5M']
        global Pie_for_TotalPriceType
        Pie_for_TotalPriceType = []
        for i in range(len(TT)):
            T_i = []
            Pie_for_TotalPriceType.append(T_i)
        for i,l in  enumerate(ZongJia):
            if l> 2000.0:
                Pie_for_TotalPriceType[0].append(l)
            elif 1500.0< l <= 2000.0:
                Pie_for_TotalPriceType[1].append(l)
            elif 1000.0< l <= 1500.0:
                Pie_for_TotalPriceType[2].append(l)
            elif 500.0< l <= 1000.0:
                Pie_for_TotalPriceType[3].append(l)
            elif l <= 500.0 :
                Pie_for_TotalPriceType[4].append(l)
            else:
                print 'Error of TotalPriceType: {}'.format(l)

        # BAR圖 房屋類型對單價：

        global Bar_for_BuildingSinglePrice
        Bar_for_BuildingSinglePrice = []
        for i in range(len(BT)):
            Bp_i = []
            Bar_for_BuildingSinglePrice.append(Bp_i)
        for i ,l in enumerate(Lexing):
            if pat_Building_0.search(l) != None:
                Bar_for_BuildingSinglePrice[0].append(MeiPingDanJia[i])
            elif pat_Building_1.search(l) != None:
                Bar_for_BuildingSinglePrice[1].append(MeiPingDanJia[i])
            elif pat_Building_2.search(l) != None:
                Bar_for_BuildingSinglePrice[2].append(MeiPingDanJia[i])
            elif pat_Building_3.search(l) != None:
                Bar_for_BuildingSinglePrice[3].append(MeiPingDanJia[i])
            elif pat_Building_4.search(l) != None:
                Bar_for_BuildingSinglePrice[4].append(MeiPingDanJia[i])
            elif pat_Building_5.search(l) != None:
                Bar_for_BuildingSinglePrice[5].append(MeiPingDanJia[i])
            elif pat_Building_6.search(l) != None:
                Bar_for_BuildingSinglePrice[4].append(MeiPingDanJia[i])
            else:
                print 'Error of BuildingSinglePrice: {}'.format(l)


    def plot_Trend(self):

        # 畫圖用的bar定義：
        Xbar_of_MeiPingDanJia = range(len(df['每坪單價'].str.strip(u'萬')))


        # 畫圖實現  走勢圖：
        cc = Color("blue")
        colors = list(cc.range_to(Color("green"), 12))

        plt.figure(figsize=(12, 5))
        M_start = 0
        for i in range(len(M)):
            if len(M[i])>0:
                ymin = round(np.mean(M[i]),1)
                yy = [ymin] * len(M[i])
                x= Xbar_of_MeiPingDanJia[M_start:M_start+len(M[i])]
                y= M[i]

                #  基礎線段：
                plt.plot(x,y,c='{}'.format(colors[i]),alpha=1.0,label='month:{}, Avg:{} '.format(i,ymin))
                plt.plot(x,y, c='k', lw=10, alpha=0.1)
                M_start= M_start+len(M[i])

                #  平均線：
                plt.plot(x, yy, c='r', alpha=0.3)
            else:
                pass
        plt.xlabel(' Total House ',fontsize=10)
        plt.ylabel(' Price/flat',fontsize=10)
        plt.suptitle(  dat +' District Reality Price per flat')
        plt.legend()
        plt.show()
        os.chdir(origin_path)


    def plot_Pie_Type(self):

        fig = plt.figure(figsize=(13,7))
        fig.subplots_adjust(left=0.2, wspace=0.6)
    # 派圖 房子類型：
        ax1 = fig.add_subplot(221)
        labels = 'Building', 'Mansion', 'Apartment', 'Villa', 'Suite','store'
        sizes = [ len(Pie_for_BuildingType[0]),len(Pie_for_BuildingType[1]) ,len(Pie_for_BuildingType[2]) ,
                  len(Pie_for_BuildingType[3]),len(Pie_for_BuildingType[4]),len(Pie_for_BuildingType[5])]
        colors = ['mediumorchid','plum','purple','fuchsia','orchid','thistle']
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%.1f%%', shadow=False, startangle=140)
        plt.axis('equal')
        plt.title('Pie_for_BuildingType')


    # 派圖 單價類型：
        #plt.figure
        ax2 = fig.add_subplot(222)
        labels = '600K Upper','450~600K','300~450K','150~300K','Lower 150k'
        sizes = [len(Pie_for_PriceType[0]), len(Pie_for_PriceType[1]), len(Pie_for_PriceType[2]),
                 len(Pie_for_PriceType[3]), len(Pie_for_PriceType[4])]
        colors = ['c' ,'cadetblue', 'lightskyblue','lightslategray', 'steelblue','powderblue']
        ax2.pie(sizes, labels=labels, colors=colors, autopct='%.1f%%', shadow=False, startangle=140)
        plt.axis('equal')
        plt.title('Pie_for_PriceType')

    # 派圖 總價類型：
        #plt.figure()
        ax3 = fig.add_subplot(223)
        labels = '20M Upper','15~20M','10~15M','5~10M','Lower 5M'
        sizes = [len(Pie_for_TotalPriceType[0]), len(Pie_for_TotalPriceType[1]), len(Pie_for_TotalPriceType[2]),
                 len(Pie_for_TotalPriceType[3]), len(Pie_for_TotalPriceType[4])]
        colors = ['green','mediumseagreen', 'mediumaquamarine', 'darkslategray', 'teal','yellowgreen']
        ax3.pie(sizes, labels=labels, colors=colors, autopct='%.1f%%', shadow=False, startangle=140)
        plt.axis('equal')
        plt.title('Pie_for_TotalPriceType')

    # BAR圖 房屋類型對單價：
        #plt.figure()
        ax4 = fig.add_subplot(224)
        objects = ('Building', 'Mansion', 'Apartment', 'Villa', 'Suite','store')
        y_pos = np.arange(len(objects))
        performance = [ np.mean(Bar_for_BuildingSinglePrice[0]),np.mean(Bar_for_BuildingSinglePrice[1]) ,np.mean(Bar_for_BuildingSinglePrice[2]),
                        np.mean(Bar_for_BuildingSinglePrice[3]) ,np.mean(Bar_for_BuildingSinglePrice[4]),np.mean(Bar_for_BuildingSinglePrice[5]) ]
        ax4.barh(y_pos, performance, align='center', alpha=0.5)
        plt.yticks(y_pos, objects)
        plt.xlabel('Price per Flat')
        plt.title('House Type with Price flat')


        plt.show()
        os.chdir(origin_path)



    def marker_to_map(self):
        name_for_map= raw_input('Enter save name for map:')

        print 'It takes time ,please wait\n'

        District_Map=[ (i).encode('utf-8') for i in df['地址'] ]
        # 有些地址是沒有數字的 這種會找不到確切位置，乾脆刪掉
        pat_no_number_in_adress = re.compile('[0-9]')
        District_Map= [i for i in District_Map if pat_no_number_in_adress.search(i)!=None ]

        #刪掉 詳細門牌資訊以免地圖找不到:
        pat_cut =re.compile('\d{1,3}~[0-9]*號') # 刪除 digital 1~3位數
        cut= [ pat_cut.search(i).group()  for i in District_Map  if  pat_cut.search(i)!=None ]
        District_Map= [ l.strip(cut[i]) for i,l  in  enumerate(District_Map)   ]
        MeiPingDanJia_str=[ str(i) for i in MeiPingDanJia ]

        map_locator_lat= []
        map_locator_lng = []
        for i,l  in enumerate(District_Map):
            try:
                print i ,l
                a= geocoder.arcgis(l)
                map_locator_lat.append(a.lat)
                map_locator_lng.append(a.lng)
                print(a.lat, a.lng)

            except GeocoderTimedOut:
                print i, l
                a= geocoder.arcgis(l)
                map_locator_lat.append(a.lat)
                map_locator_lng.append(a.lng)
                print(a.lat, a.lng)

        map_locator =list(zip(map_locator_lat,map_locator_lng))

        #新店座標  地址轉座標網址：http://gps.uhooamber.com/address-to-lat-lng.html
        TPE_COORDINATES = (24.9664922,121.53976779999994)
        District_Map_unicode =[  unicode(i, 'utf-8')   for i in  District_Map  ]
        MeiPingDanJia_str_unicode=[ unicode(i,'utf-8')  for i in MeiPingDanJia_str ]
        map_osm = folium.Map(location=TPE_COORDINATES,zoom_start=15)
        pop_Dis= [u'{}'.format( i )  for i in District_Map_unicode]
        pop_Mei= [u'{}'.format( i )  for i in MeiPingDanJia_str_unicode]
        ppp= [  u'{}, {}萬/坪'.format(l,MeiPingDanJia_str_unicode[i]) for i,l  in enumerate(pop_Dis)]
        map_osm.add_child(  MarkerCluster(locations=map_locator, popups=ppp ))


        if os.path.isfile(name_for_map+'.html')==True:
            print 'Already Exist '
        else:
            os.chdir(origin_path)
            map_osm.save(name_for_map+'.html')
            print 'Saved Done'




        print ''
        print 'Done'
        os.chdir(origin_path)


    def plot_map(self):
        name_for_map= raw_input('Enter filename to show map:')
        chrome_path = 'open -a /Applications/Safari.app %s'
        os.chdir(origin_path)
        webbrowser.get(chrome_path).open('file://'+ origin_path +'/'+ name_for_map +'.html' )



Ana=Analysis()
Ana.plot_Trend()
Ana.plot_Pie_Type()
Ana.marker_to_map()
Ana.plot_map()

