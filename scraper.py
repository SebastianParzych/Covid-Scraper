#--------------------------------- DATA SCRAPPER------------------------------------#
import requests
import pandas as pd
from bs4 import BeautifulSoup
import os


list_of_folders=["data","data/csv_format"]


class Corona:
    def __init__(self):
        self.all_countries =self.country_list()
        self.country =None
        self.columns=0
        self.soup=None
        self.error_data=None
        self.all_titles=[]
        self.exist= None
        self.csv_file_name =''
        self.df=pd.DataFrame()
    def reset(self): # reseting class variables while getting data from all countries
        self.country =None
        self.columns=0
        self.soup=None
        self.error_data=None
        self.all_titles=[]
        self.exist= None
        self.csv_file_name =''
        self.df=pd.DataFrame()

    def run(self):
        if self.country == None:
            for country in self.all_countries.values():
                try:
                    self.request(country)
                    self.reset()
                except:
                    continue
        else:
            self.request(self.country)

    def request (self, country ): # requests page resources
        print(country)
        self.files_management(country)
        url = "https://www.worldometers.info/coronavirus/country/" + country + "/"
        page = requests.get(url)
        self.soup = BeautifulSoup(page.text, 'html.parser')
        all_scripts = self.soup.find_all('script')
        for script in all_scripts:
            if 'Highcharts.chart' in str(script):  # excract data only from script ,that contain chart
                self.minedata(str(script), self.columns)
        self.csv_writer()  # making .csv file

    def title_formatting(self, script):
        tittle=script.split('name:',1)[1]
        tittle=tittle.split('\n',1)[0]
        tittle= str(tittle).replace("'", '').replace(',' ,'').replace(' ', '')
        if not self.all_titles: # is empty
            self.all_titles.append(tittle)
        elif self.all_titles[-1] == tittle: # doubled tittle
            pass
        elif tittle[0] == '3':
            self.all_titles.append(self.all_titles[-1]+'- '+ tittle)
        elif tittle[0] == '7':
            self.all_titles.append(self.all_titles[-2] +'- '+ tittle)
        else:
            self.all_titles.append(tittle)

    def minedata (self,script, columns): # Extract all all data with tittles from each script
        self.title_formatting(str(script))  # save tittle of first set of data
        sec_str=0
        last_str=0
        fst_str = script.split('data:', 1)[1]
        try:
            self.title_formatting(fst_str) # save tittle of second set of data
            last_str=sec_str = fst_str.split('data:', 1)[1]
            sec_str = sec_str.split(']', 1)[0].replace('[', '').replace(' ','')
            try:
                self.title_formatting(last_str,) # save tittle of third set of data
                last_str = last_str.split('data:', 1)[1]
                last_str = last_str.split(']', 1)[0].replace('[', '').replace(' ', '')
            except:
                last_str=0

        except:
            sec_str = 0

        fst_str = fst_str.split(']', 1)[0].replace('[','').replace(' ','')
        if fst_str != sec_str and type(sec_str)== str: # Check if data sets  are the same
            fst_str = fst_str.split(',', len(fst_str) - 1)
            sec_str = sec_str.split(',', len(sec_str) - 1)
            self.columns = self.columns + 1
            self.prep_data(fst_str,script)
            self.columns = self.columns +1
            self.prep_data(sec_str, script)
            if type(last_str) == str:
                last_str  = last_str .split(',', len(last_str ) - 1)
                self.columns = self.columns + 1
                self.prep_data(last_str, script)
        else:
            fst_str = fst_str.split(',', len(fst_str) - 1)
            self.columns = self.columns + 1
            self.prep_data(fst_str,script)

    def prep_data (self, raw_str, script,): # making proper dat
        xAxis = self.xAxis_data(script)  # Exctracting xAxis info
        try:
            data = [0 if item=='null' or item=='"nan"' else int(str(item)) for item in raw_str]
        except:
            data=[0 if item=='null'  or item=='"nan"' else float(str(item)) for item in raw_str]

        data_dict = dict(zip(xAxis, data))  # making set of excrated data
        last= False
        temp = {}
        if self.exist: ## making dictionary only from nesseciary data
            for date in data_dict.keys():
                try:
                    if date ==  self.last_day:
                        last = True
                        continue
                    if last :
                        temp[date] = data_dict[date]
                except:
                    self.error_data= True
                    break
            if last:
                data_dict = temp
        self.data_Frame(data_dict)

    def xAxis_data(self,script):
        xname = '["' + script.split('categories: ["', 1)[1]
        xname = xname.split(']', 1)[0] + ']'
        xAxis = []
        string = ""
        single_date = False
        for char in xname: # converting single string to list of strings ( dates ).
            if char == '"':
                if single_date == True:
                    xAxis.append(string)
                single_date= not single_date
                string=""
                continue
            if single_date == True:
                string += char
        return  xAxis
    def csv_writer(self): # write formatted dataFrames to csv file.
        if self.exist:
            self.temp.to_csv(self.csv_file_name,
                             sep=',',
                             float_format="%.3f",
                             mode='a',
                             header=False,
                             index=True,)
        elif not self.exist or  self.error_data == True:
            self.df.to_csv(self.csv_file_name,
                           sep=',',
                           index=True,
                           index_label='Days',
                           float_format="%.3f")
    def data_pad (self, dict,dataFrame):
        if not dataFrame.empty  and len(dict)< len(dataFrame['Date']): # Some data has not the same length, here is padding empty values
            pad = {}
            for date in dataFrame['Date']:
                if not  date in dict:
                  pad[date]='-'
            pad.update(dict)
            return pad
        else:
            return dict

    def data_Frame(self, dict):# making, updating, database.
        columns = self.columns - 1
        if  self.exist:
            dict=self.data_pad(dict, self.temp)
            self.temp['Date'] = dict.keys()
            self.temp[self.all_titles[columns]] = dict.values()
            self.temp.index=pd.RangeIndex(start= len(self.df['Days']), stop= len(self.df['Days'])+len(dict))
        elif not self.exist  or  self.error_data ==  True:
                dict=self.data_pad(dict,self.df)
                self.df['Date'] = dict.keys()
                self.df[str(columns)+'_'+ self.all_titles[columns]] = dict.values()


    def country_list(self):
        page = requests.get('https://www.worldometers.info/coronavirus')
        soup = BeautifulSoup(page.text, 'html.parser')
        all_names= {}
        for key,line  in enumerate(soup.find_all(class_="news_li")):
            a = line.find('a')['href']
            value = a.split('/')
            value=value[-2]
            all_names[key]=value
        # There is over 960 <a href> positions, a most of it is duplicated, so it has to be removed
        temp = [] # temp tuple to collect  not duplicated countries
        number = 0
        all_countries = {}
        for val in all_names.values():
            if val not in temp:
                number= number +1
                temp.append(val)
                all_countries [number]=val
        return all_countries

    def country_pick (self):
        pol=0
        for key in self.all_countries:
            print(str(key)+'     '+self.all_countries[key])
            if self.all_countries[key]=='china':
                pol=key
        print("Type the number from the above list to get the data of a given country")
        print('Example:' + str(pol) + ' ->  Extracting all data about ' + str(self.all_countries[pol]))
        print('Your number:')
        nr = input ()
        country=self.all_countries.get(int(nr))
        self.country=country
        self.files_management(country)
    def files_management(self, country):
        for folder in list_of_folders:
            if not os.path.isdir(folder):
                os.makedirs(folder)
        self.csv_file_name = 'data/csv_format/' + country + '_data_storage.csv'  # name of csv file
        try:
            self.df = pd.read_csv(self.csv_file_name, sep=';', index_col=None)
            self.temp = pd.DataFrame()
            self.last_day = self.df['Date'].iloc[-1]
            self.exist = True
        except:
            self.df = pd.DataFrame(list())  # creating empty csv, to collect data
            self.df.to_csv(self.csv_file_name)
            self.exist = False

def one_country( ): # General purpose, excract all data sets about chosen country
    scrape = Corona()
    scrape.country_pick()
    scrape.run()
def pull_alldata(): # Extract data from all countries.
    scrape = Corona()
    scrape.run()

#one_country()
pull_alldata()