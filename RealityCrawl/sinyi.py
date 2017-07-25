#coding=utf-8

from selenium import webdriver
import time
from bs4 import BeautifulSoup
import re
import sys
import sqlite3
from taiwan import TWcode
import os.path




class Real_Estate:
    def __init__(self):
        global  dict
        dict = {u'零': 0, u'一': 1, u'二': 2, u'三': 3, u'四': 4,
                u'五': 5, u'六': 6, u'七': 7, u'八': 8, u'九': 9,
                u'十': 10}



# 新增 database 資料欄位：
    def Make_SQLite_DataColumns(self,datafile):

        self.conn = sqlite3.connect(datafile)
        print " Opened database successfully\n"

        # PRIMARY KEY 權限最高 ，用來判斷重複資料 對應的是 insert or replace
        self.conn.execute("CREATE TABLE  IF NOT EXISTS SINYI_COLUMNS( 'ID' INTEGER PRIMARY KEY autoincrement,'年','月',{},{},{},{},{},{},{},{},{},'備註一','備註二',\
                            UNIQUE ('年','月',{},{},{},{},{},{},{},{},{},'備註一','備註二')  )".format(
            self.title[1].encode('utf-8'),self.title[2].encode('utf-8'),
            self.title[3].encode('utf-8'),self.title[4].encode('utf-8'),self.title[5].encode('utf-8'),
            self.title[6].encode('utf-8'),self.title[7].encode('utf-8'),self.title[8].encode('utf-8'),
            self.title[9].encode('utf-8'),
            self.title[1].encode('utf-8'), self.title[2].encode('utf-8'),
            self.title[3].encode('utf-8'), self.title[4].encode('utf-8'), self.title[5].encode('utf-8'),
            self.title[6].encode('utf-8'), self.title[7].encode('utf-8'),self.title[8].encode('utf-8'),
            self.title[9].encode('utf-8')   ))
        print " Table created successfully\n";





# 抓資料：
    def Parse(self,page_start,page_end=None):

        self.driver = webdriver.PhantomJS(
            executable_path='/usr/local/Cellar/phantomjs/2.1.1/bin/phantomjs')  # must use brew install phantomjs first and copy the file path

        ZC =raw_input(' Enter:    District,City  \n').split(',')
        TZC= str(TWcode.ZipCodeTW(ZC[0],ZC[1]))

        for a, b, filename in os.walk(os.getcwd()):
            s = (filename)
            break

        CompileDataBase = re.compile('.*.db')
        ExistedDataBase = [l for i, l in enumerate(s) if CompileDataBase.search(l) != None]
        print " 目前已存在的.db檔，從中選ㄧ 或另外輸入 :\n"
        print "{}".format(ExistedDataBase)

        da= raw_input('file name:')
        datafile = da

        try:
            self.driver.set_page_load_timeout(30)
            self.driver.get('http://tradeinfo.sinyi.com.tw/itemList.html?a1='+ TZC +'&s2=10602_10607&p=' + str(1) )
        except :
            print ' \n      🤑 ~~~~連線太久啦~~~~🤑    \n '
            sys.exit()
            self.driver.close()


        time.sleep(3)
        soup = BeautifulSoup(self.driver.page_source, "lxml")
        self.Title_soup = soup.find_all('th')
        self.title = []
        for i in self.Title_soup:
            self.title.append(i.text)
        del self.title[0:len(self.title)-10]


        global data
        data = []
        if page_end==None :
            page= page_start
            pass
        else:
            page = page_end - page_start + 1
        for i in range(page):
            if i != page_start-1 and page_end==None:
                pass
            else:
                if page_end == None:
                    print ''
                    print '\n   🤣🤣🤣  STARTING LOADING PAGE {} 🤣🤣🤣 \n'.format(page_start)
                    print ''
                    self.driver.get('http://tradeinfo.sinyi.com.tw/itemList.html?a1='+ TZC +'&s2=10602_10607&p='+ str(page_start) )
                else:
                    print ''
                    print '\n   🤣🤣🤣  STARTING LOADING PAGE {} 🤣🤣🤣 \n'.format(page_start + i)
                    print ''
                    self.driver.get('http://tradeinfo.sinyi.com.tw/itemList.html?a1='+ TZC +'&s2=10602_10607&p='+str(page_start+i))
                time.sleep(3)
                #print driver.page_source.encode('utf-8','ignore') # this code can see really java script
                soup = BeautifulSoup(self.driver.page_source, "lxml")

                # f=codecs.open("tt.html", 'r')
                # #print f.read()
                # soup = BeautifulSoup(f,"lxml")
                num=0
                for string in soup.stripped_strings: # delete unneeded spcace
                    data.append(string)
                    num= num+1

                #print type(data[0]) # is unicode ,it means it is already decoded as  u'string' .(unicode is default as python's output so can't be decoded anymore)
                # decode: 卸載編碼  encode: 包裝成另種編碼


                # << 這邊放置正則表達式要用的比對字串 >>
                pattern= re.compile('年')
                pattern2 = re.compile(u'.*車.*$')
                pat_room = re.compile(u'[0-9]房/.*')
                pat_s_end=re.compile(u'含車位.*坪')
                par_no_car =re.compile(u'無車位')
                par_no_mrt =re.compile(u'無社區無近捷運')
                pat_car_note =re.compile(u'含車位')
                pa_car = re.compile(u'(.*)')
                pa_size = re.compile(u'([0-9]*\.[0-9]*)坪')
                pa_price = re.compile(u'([0-9]*)萬')
                pat_mrt =re.compile(u'近捷運')
                pat_commity =re.compile(u'社區')
                pat_for_pure=re.compile(u'.*純.*')
                adress_is_weired = re.compile(u'[0-9]')
                adress_with_chinesenumber= re.compile('{}'.format(dict.keys()))


                # 先篩選出106年：
                for ii in range(len(data)):
                    if  pattern.search(data[ii].encode('UTF-8')):
                        if ( len(data[ii].encode('UTF-8'))==6 and len(data[ii])==4):  # len('106年'encode) == 6 and len('106年) == 4
                            data_mark = ii
                            break
                        else:
                            pass
                    else:
                        pass
                data= data[data_mark:]
                del ii
                del data_mark

                # 篩選不是房子資訊：
                mark_106=[]
                mark_land= []
                mark_x=[]
                for ii in range(len(data)):
                    if  pattern.search(data[ii].encode('UTF-8')):
                        if ( data[ii]==u'106年' and len(data[ii])==4):  # len('106年'encode) == 6 and len('106年) == 4
                            #print '106年所在位置：{}'.format(ii)
                            mark_106.append(ii)
                            mark_x.append(ii)
                            if data[ii+4]==u'純土地' or data[ii+4]==u'純車位'or data[ii+5]==u'純土地' or data[ii+5]==u'純車位'or \
                                    pat_for_pure.search(data[ii+4])!= None  or pat_for_pure.search(data[ii+5])!= None:
                              mark_land.append(ii+4)
                              #print '純土地或車位所在位置在+4 or i+5：{}'.format(ii+4)
                              mark_x.append('X')
                            else:
                                pass
                                #print ''
                        else:
                            pass
                    else:
                        pass

                for index,label in enumerate(mark_x):
                    if label == 'X' :
                        try:
                            #print 'Del: {}~{}'.format( mark_x[index-1],mark_x[index+1] )
                            for ix in range(mark_x[index-1],mark_x[index+1]):
                                data[ix]= data[ix].replace(data[ix],'X')
                        except:
                            #print 'Del: {}~'.format( mark_x[index-1] )
                            for ix in range(mark_x[index-1],len(data)):
                                data[ix]= data[ix].replace(data[ix],'X')
                    else:
                        pass
                for ind,ixx in enumerate(data):
                    if ixx==u'-':
                        ixx=ixx.replace(ixx,'X')
                        for xx in range(ind,len(data)):
                            data[xx] = data[xx].replace(data[xx], 'X')
                        break



                temp=None
                for ii in range(len(data)-1,-1,-1):
                    if data[ii]==u'備註資料：':
                        temp=ii
                    if temp!= None:
                        if data[ii] == u'106年' :
                            for iii in range(temp-ii+1-1,-1,-1):
                                data[temp-iii] = data[temp-iii].replace(data[temp-iii], 'X')
                            data[temp+1] = data[temp+1].replace(data[temp+1], 'X')
                            #data[temp] = data[temp].replace(data[temp], 'X')
                            temp= None
                        else:
                            pass
                    else:
                        pass

                # 第一次篩選: 把'檢視位置'踢掉：
                data[:]=[it for it in data if it!='X' and it!=u'檢視位置']  # Delete 'X' and '檢視位置'


                # 開始把車位資訊挪動：
                #print ("**** ⚠️ Start ⚠️ ****\n ")
                Parking_Space = []
                Temp_Park2=[]
                room_locate=[]
                car_locate=[]
                appendix=[]
                Replace=[]
                count = 0
                for index,label in enumerate(data):
                    b = pattern2.search(label) # 有車就丟到b
                    if pat_room.search(label) != None:
                        room_locate.append(index)
                    if b != None  :  # 在這裡面只有車才會進來
                        Replace.append(index)
                        if count<=1:
                            if len(Temp_Park2)!=0:
                                Parking_Space.append(Temp_Park2[0])
                                Temp_Park2 = []

                            if b.group() == u'含車位':
                                count= count+1
                            if pat_s_end.search(b.group())!=None:
                                count = count + 1
                                car_locate.append(index)
                            Parking_Space.append(b.group())
                        else:
                            if count ==2 :
                                try: # 有要整合的車位資訊會打印出來
                                    # print u'{},{},{} #{}'.format((pa_car.search(Parking_Space[0])).group(),
                                    #                                 (pa_size.search(Parking_Space[3])).group(),
                                    #                                 (pa_price.search(Parking_Space[1])).group(),
                                    #                                 (Parking_Space[2]))
                                    ap= (u'{},{},{} #{}'.format((pa_car.search(Parking_Space[0])).group(),
                                                                    (pa_size.search(Parking_Space[3])).group(),
                                                                    (pa_price.search(Parking_Space[1])).group(),
                                                                    (Parking_Space[2])) )
                                    appendix.append(ap)
                                except:# 有要整合的車位資訊會打印出來
                                    if pa_size.search(Parking_Space[2]) == None:
                                        pa_size2 = u'--坪'
                                    else:
                                        pa_size2 = pa_size.search(Parking_Space[2]).group()
                                    if pa_price.search(Parking_Space[1]) == None:
                                        pa_price2 = u'--萬'
                                    else:
                                        pa_price2 = pa_price.search(Parking_Space[1]).group()
                                    #print u'{},{},{}'.format((pa_car.search(Parking_Space[0])).group(),pa_size2,pa_price2 )
                                    ap = (u'{},{},{}'.format((pa_car.search(Parking_Space[0])).group(),pa_size2,pa_price2 ))
                                    appendix.append(ap)
                            count=1
                            Parking_Space=[]
                            Temp_Park2.append(b.group())
                            pass

                if Parking_Space !=[]:
                    try: # 有要整合的車位資訊會打印出來

                        # print u'{},{},{} #{}'.format((pa_car.search(Parking_Space[0])).group(),
                        #                                      (pa_size.search(Parking_Space[3])).group(),
                        #                                      (pa_price.search(Parking_Space[1])).group(),
                        #                                      (Parking_Space[2]))
                        ap = (u'{},{},{} #{}'.format((pa_car.search(Parking_Space[0])).group(),
                                                     (pa_size.search(Parking_Space[3])).group(),
                                                     (pa_price.search(Parking_Space[1])).group(),
                                                     (Parking_Space[2])))
                        appendix.append(ap)
                    except:  # 有要整合的車位資訊會打印出來
                        if pa_size.search(Parking_Space[2]) == None:
                            pa_size2 = u'--坪'
                        else:
                            pa_size2 = pa_size.search(Parking_Space[2]).group()

                        if pa_price.search(Parking_Space[1]) == None:
                            pa_price2 = u'--萬'
                        else:
                            pa_price2 = pa_price.search(Parking_Space[1]).group()

                        #print u'{},{},{}'.format((pa_car.search(Parking_Space[0])).group(), pa_size2, pa_price2)
                        ap = (u'{},{},{}'.format((pa_car.search(Parking_Space[0])).group(), pa_size2, pa_price2))
                        appendix.append(ap)
                else:
                    pass

                # 把有車的都標記X:
                for i in Replace:
                    data[i]=data[i].replace(data[i],'X')

                # room locate 是 幾房/幾廳 的位置，取得目的是之後appendix資料要補在其之後，因為幾房幾廳是每筆資料都有,但是要有'車'的資料才需替換，所以要將幾房/幾廳 的位置 與 含車*坪 的位置做比較確認。
                room_locate[:]=[  r for r in room_locate if r-4 in car_locate ]

                # 把appendix資料 替補在後面, 做reverse的目的是因為從最後插入不會影響插入的ndex順序,較為簡單：
                appendix.reverse()
                room_locate.reverse()
                for ind,r in enumerate(room_locate):
                    data.insert(r+1,appendix[ind])


                # 第二次篩選：把有車的都刪掉！！！
                data[:]=[it for it in data if it!='X' ]



                # 找106年的字符,因為要比對用,所以最一開頭的沒用要踢掉,最後也要補一個虛擬的106位置才方便比對：
                # mark_106=[]  # 之前有用到，確保安全 先清空
                # mark_106[:]= [ i for i,l in enumerate(data) if data[i]==u'106年']
                # mark_106.remove(mark_106[0])
                # mark_106.append(len(data))
                #


                #找幾房幾廳的字符,要與106年比對用：
                room_locate=[]  # 之前有用到，確保安全 先清空
                room_locate[:]=[ i for i,l in enumerate(data) if pat_room.search(data[i]) != None ]



                # 把沒車位資訊補上欄位：
                for i in range(len(room_locate)-1,-1,-1):
                    if len(data)-1 ==room_locate[i]:
                        data.insert(room_locate[i] + 1, U'無車位 ')
                    else:
                        if pat_car_note.search(data[room_locate[i]+1])== None:
                            data.insert(room_locate[i]+1, U'無車位 ')




                # 再重整一次，把標籤插入
                note3 = []  # 存標誌用的資訊
                note4 = []
                room_locate=[]  # 之前有用到，確保安全 先清空
                room_locate[:]=[ i for i,l in enumerate(data) if pat_room.search(data[i]) != None ]
                # 找106年的字符,因為要比對用,所以最一開頭的沒用要踢掉,最後也要補一個虛擬的106位置才方便比對：
                mark_106=[]  # 之前有用到，確保安全 先清空
                mark_106[:]= [ i for i,l in enumerate(data) if data[i]==u'106年']
                mark_106.remove(mark_106[0])
                mark_106.append(len(data))
                for i, l in enumerate(room_locate):
                    if mark_106[i] - l == 1:
                        pass
                    else:
                        m_r = (mark_106[i] - l) - 1
                        lp = str(l)

                        note3.append(lp)  # 第一個先插入幾房幾廳的位置資訊
                        for j in range(m_r):
                            note3.append(data[l + 1 + j])
                        note4.append(m_r)

                note3[:] = [l for i, l in enumerate(note3) if pat_s_end.search(note3[i]) == None]  # 不存有車的
                note3[:] = [l for i, l in enumerate(note3) if par_no_car.search(note3[i]) == None] # 不存‘無車位’
                note3[:] = [l for i, l in enumerate(note3) if par_no_mrt.search(note3[i]) == None] # 不存‘無社區無近捷運’
                note3.reverse()



                # 把集合後的標籤插入
                cc=0
                for i,l in enumerate(note3):
                    pa = u''
                    if type(l)== str:  # 數字已轉str 文字是unicode

                        for ii in xrange(cc,i):
                            pa= note3[ii]+ pa
                        data.insert(int(l)+1,pa)
                        del pa
                        cc=i+1
                # 把空的踢掉：
                data[:]=[  i for i in data if len(i)!=0 ]


                print  ''
                print  ''


                for i in data:
                    print i

                print  ''
                print  ''




                # 再補上無社區捷運資訊上去
                room_locate=[]  # 之前有用到，確保安全 先清空
                room_locate[:]=[ i for i,l in enumerate(data) if pat_room.search(data[i]) != None ]


                for i in range(len(room_locate) - 1, -1, -1):

                    if pat_mrt.search(data[room_locate[i] + 1])    or  \
                                pat_commity.search(data[room_locate[i] + 1])  :
                        pass
                    else:
                        data.insert(room_locate[i] + 1, U'無社區無近捷運 ')


                # 整理地址：
                adress=[]
                i1=[]
                i2=[]
                adress2=[]

                ad_count=0  # adress count
                ad_count2= 0  # adress count
                for i,l in enumerate(data):
                    if l ==u'106年':
                        if adress_is_weired.match(data[i+4])==None :  # 規則是i+4欄位 應該是"類型" 也就是會是中文不應該是數字,若配到中文 則i+2 i+3 的地址相加
                            ad = data[i + 2] + data[i + 3]
                            adress.append(ad)
                            i1.append(i)

                        else:
                            adress2.append(ad)
                            i2.append(i)

                        # dd = (data[i + 3])
                        # curr = []
                        # for count in range(len(data[i+3])):
                        #     curr_char = dd[count]
                        #     curr_digit = dict.get(curr_char, None)
                        #     curr.append(curr_digit)
                        #
                        # if curr[0] != None:                 # 這裡做地址比對,如果data[i+3]的地址訊息是中文一二三四五 則當作是地址的路名
                        #     ad = data[i + 2] + data[i + 3]
                        #     adress.append(ad)
                        #     i1.append(i)
                        #
                        # else:
                        #     if adress_is_weired.match(data[i+3])!=None:  # 若 data[i+3]的地址出來是阿拉伯數字，那當作是地址的路名
                        #         ad= data[i+2]+data[i+3]
                        #         adress.append(ad)
                        #         i1.append(i)
                        #
                        #     else:                        # 不然就代表地址沒有分兩行表達
                        #         adress2.append(ad)
                        #         i2.append(i)
                # 做everse是為了從後面補上資訊才不會影響i 的排序
                adress.reverse()
                adress2.reverse()
                i1.reverse()
                i2.reverse()


                # 補上整理後的地址資訊： 若地址分兩行 則補上整禮後的資訊一次（共三行），若地址資訊只有一行，則再補上一行的地址資訊兩次（共三行）
                for i in range(len(data)-1,-1,-1):
                    if data[i] == u'106年':

                        if adress_is_weired.match(data[i+4])==None :
                            data.insert(i+2,adress[ad_count])
                            ad_count= ad_count+1

                        else:

                            data.insert(i+2,adress2[ad_count2])
                            data.insert(i+3,adress2[ad_count2])
                            ad_count2= ad_count2+1

                    # dd = (data[i + 3])
                        # curr = []
                        # for count in range(len(data[i + 3])):
                        #     curr_char = dd[count]
                        #     curr_digit = dict.get(curr_char, None)
                        #     curr.append(curr_digit)
                        #
                        # if curr[0] != None:
                        #     data.insert(i + 2, adress[ad_count])
                        #     ad_count = ad_count + 1
                        #
                        # else:
                        #     if adress_is_weired.match(data[i + 3]) != None:
                        #         data.insert(i+2,adress[ad_count])
                        #         ad_count= ad_count+1
                        #     else:
                        #         data.insert(i+2,adress2[ad_count2])
                        #         data.insert(i+3,adress2[ad_count2])
                        #         ad_count2= ad_count2+1



                # 剔除多餘的標籤：
                mark_106=[]  # 之前有用到，確保安全 先清空
                mark_106[:]= [ i for i,l in enumerate(data) if data[i]==u'106年']

                # 在前面的過程中 因為增加車位資訊地址資訊等等 共有17欄位 ，其中最後兩欄位為多餘的 因為已有備註資訊補上去，所以要刪掉
                # 規則已建立，所以只要每15個取出來就好，最後兩欄位就被遺棄
                data2=[]
                for i in mark_106:
                    for d in range(15):
                        data2.append(data[i+d])
                data=data2
                del data2

                # 在data的第三第四地址資訊是多餘的，把他踢除：
                data[:]=[l for i,l in enumerate(data) if i%15!=3 and i%15!=4  ]


                print ('')
                print ('****🗣  End 🗣  ****\n')

                print ('===== !!!   ☠  Hail Hydra ☠   !!!!======\n')
                for i in data:
                    print i
                print ('')
                print ('****🗣  End 🗣  ****\n')

                self.data=(data)
                Test.SaveData(datafile)
                data = []
        self.driver.close()
        #return self.data


# 存取資料：
    def SaveData(self,datafile):
        Test.Make_SQLite_DataColumns(datafile)
        num_info= len(data)/13
        num_count=13
        self.conn = sqlite3.connect(datafile)
        c=self.conn.cursor()
        print '   ◻️ ◼️ ◻️ ◼️ ◻️ ◼️ ◻️ ◼️ ◻️ ◼️ ◻️ ◼️  '

        for i in range(num_info):
            # 先確認sqlite 裡面是否有資料：
            c.execute("SELECT * FROM SINYI_COLUMNS GROUP BY {}  HAVING COUNT(?)>0 ".format( self.title[1].encode('utf-8') ),( self.title[1],)   )
            cc = c.fetchone()
            if cc==None : # 沒有的話就先建立資料：
                print '  No Data Yet, Now Will Adding Data  \n '
                print "✏️ : {}\n   ".format(data[2 + i * num_count].encode('utf-8'))
                c.execute(
                    " REPLACE into SINYI_COLUMNS ('年','月',{},{},{},{},{},{},{},{},{},'備註一','備註二' )VALUES (?,?,?,?,?,?,?,?,?,?,?,?,? ) ".format(
                        self.title[1].encode('utf-8'), self.title[2].encode('utf-8'),
                        self.title[3].encode('utf-8'), self.title[4].encode('utf-8'), self.title[5].encode('utf-8'),
                        self.title[6].encode('utf-8'), self.title[7].encode('utf-8'), self.title[8].encode('utf-8'),
                        self.title[9].encode('utf-8'))
                    ,(data[0+i*num_count],data[1+i*num_count],data[2+i*num_count],data[3+i*num_count],
                       data[4+i*num_count],data[5+i*num_count],data[6+i*num_count],data[7+i*num_count],
                       data[8+i*num_count],data[9+i*num_count],data[10+i*num_count],data[11+i*num_count],data[12+i*num_count],)  )

            else:
                # 確認資料重複的話就pass：比對地址跟價錢
                c.execute("SELECT * FROM SINYI_COLUMNS  WHERE  {}=?  and   {}=? ".format(self.title[1].encode('utf-8'),  self.title[3].encode('utf-8')    ), (data[2+i*num_count], data[4+i*num_count]   ))
                dd= c.fetchone()
                if dd != None:
                    print 'Same Data ,No need to Write in \n'
                    pass
                # 新的資料就寫進去
                else:
                    print "✏️ : {}\n   ".format(data[2+i*num_count].encode('utf-8'))
                    c.execute(
                        " REPLACE into SINYI_COLUMNS ('年','月',{},{},{},{},{},{},{},{},{},'備註一','備註二' )VALUES (?,?,?,?,?,?,?,?,?,?,?,?,? ) ".format(
                            self.title[1].encode('utf-8'), self.title[2].encode('utf-8'),
                            self.title[3].encode('utf-8'), self.title[4].encode('utf-8'), self.title[5].encode('utf-8'),
                            self.title[6].encode('utf-8'), self.title[7].encode('utf-8'), self.title[8].encode('utf-8'),
                            self.title[9].encode('utf-8'))
                        , (data[0 + i * num_count], data[1 + i * num_count], data[2 + i * num_count],
                           data[3 + i * num_count],
                           data[4 + i * num_count], data[5 + i * num_count], data[6 + i * num_count],
                           data[7 + i * num_count],
                           data[8 + i * num_count], data[9 + i * num_count], data[10 + i * num_count],
                           data[11 + i * num_count], data[12 + i * num_count],))

            self.conn.commit()
        print " Records created successfully \n";

        self.conn.close()



# 刪除整個 SQLite 資料庫：
    def Drop_SQLite(self,datafile):
        try:
            self.conn = sqlite3.connect(datafile)
            self.conn.execute('DROP TABLE SINYI_COLUMNS')
            self.conn.commit()
            self.conn.close()
            print " SQLite data drop successfully \n   "
        except:
            print " Actually there has no SQLite file exist. \n"
        return




#刪除特定 id 欄位：
    def DelData(self,datafile,id_num):
        self.conn = sqlite3.connect(datafile)
        c=self.conn.cursor()
        c.execute("DELETE  FROM  SINYI_COLUMNS WHERE ID={} ".format(id_num )  )
        print ' Deldata ID: {} is Done'.format(id_num)
        self.conn.commit()
        self.conn.close()






Test= Real_Estate()
Test.Parse(1,60)


