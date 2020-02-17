from datetime import datetime, timedelta, timezone

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
import requests
requests.packages.urllib3.disable_warnings()
from django.http import HttpResponse
import urllib.request
from bs4 import BeautifulSoup
from fuzzywuzzy import process
import pandas as pd
from django.shortcuts import render
# import json to load json data to python dictionary
import json
# urllib.request to make a request to api
import urllib.request

# Create your views here.
from .models import Companies


def company_list(request):
    session = requests.Session()
    ## initializing the UserAgent object
    session.headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}

    # creating our own def to parse urls
    def make_soup(url):
        ## getting the reponse from the page using get method of requests module
        page = session.get(url, verify=False, headers=session.headers)

        ## storing the content of the page in a variable
        html = page.content

        ## creating BeautifulSoup object
        soup = BeautifulSoup(html, "html.parser")

        return soup

    data_list = []
    url_collection = []
    html_table = []
    excel_link = []
    indexlink = []
    company_inf =[]
    cik = []
    primarysymbol = []
    companyname = []
    markettier = []
    sicdescription = []

    if request.method == 'POST':

        try:
            ticker = request.POST['test']
            print(request.POST['test'])
        except:

            csv_file1 = request.FILES["csv_file1"]


            c = csv_file1.read().decode("utf-8")

            ticker = c.replace('\r', ",", (c.count('\r')-1)).replace('\n', "").replace("\r", "")


        #the api link provides meta data about companies like cik, ticker symbol, entity id or market tier.
        url = urllib.request.urlopen('https://datafied.api.edgar-online.com/v2/companies?primarysymbols=' + ticker + '&appkey=a76c61e85f9225192ce5cbbd0b22fb52').read()
        print(url)

        # converting JSON data to a dictionary
        list_of_data = json.loads(url)
        print(list_of_data)
        y = int(list_of_data['result']['totalrows']) # find total number of the rows. if its 0, then ticker symbol doen't match with sec edgar db

        if y == 0:
            messages.success(request, "Unmatched Ticker Symbol or No Available Financial Data.") #if it's 0, give error
            return redirect('EaganJones:company_list') #show error on search page
        # data for variable list_of_data
        for i in range(0, y):
                    data = {
                    "cik": str(list_of_data['result']['rows'][i]['values'][0]['value']),
                    "companyname": str(list_of_data['result']['rows'][i]['values'][1]['value']),
                    "entityid": str(list_of_data['result']['rows'][i]['values'][2]['value']),
                    "primaryexchange": str(list_of_data['result']['rows'][i]['values'][3]['value']),
                    "marketoperator": str(list_of_data['result']['rows'][i]['values'][4]['value']),
                    "markettier": str(list_of_data['result']['rows'][i]['values'][5]['value']),
                    "primarysymbol": str(list_of_data['result']['rows'][i]['values'][6]['value']),
                    "siccode": str(list_of_data['result']['rows'][i]['values'][7]['value']),
                    "sicdescription": str(list_of_data['result']['rows'][i]['values'][8]['value']),

                        }

                    companyname = data.get("companyname", "")
                    cik = data.get("cik", "")
                    primarysymbol = data.get("primarysymbol", "")
                    markettier = data.get("markettier", "")
                    sicdescription = data.get("sicdescription", "")

                    data_list.append(data) # all the data which came from edgar's api is in this list. We'll show those in the detail page.




        ticker_list = ticker.split(",") # split the tickers that user entered when searchirng for data.
        print("bu ticker list" +str(ticker.split(",")))
        for i in ticker_list: #iter over ticker symbols and we're able to get each companies profile on sec edgar
            url2 = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=' + i + '&type=10-k&dateb=&owner=exclude&count=40'
            url_collection.append(url2) # company profile links stored in a list. Our journey starts from this point.
            # We'll go through to the requested cash flows table step by step
            print("bunlar urller" +str(url2))
            print(url_collection) # scrapping starts from this url collection

        b = []
        for z in url_collection:
            souped_link = make_soup(z) #parse the link
            b.append(souped_link)
            print(b)
            return HttpResponse("hi")
            table = b.find("table", {"class": "tableFile2"})

            indexlink_list = [] # the links which contain 10-k filings will be in this link

            for row in table.find_all("tr"):
                cells = row.findAll("td")
                if len(cells) == 5: # if len(cells) is not 5, it means the company registered to edgar's website but there no data. table is empty.
                    #I should write an error message here, I tried but failed.

                    if cells[0].text.strip() == '10-K': # make sure we are at the write row. when we search for 10-k, it pulss 10-ka too.

                        link = cells[1].find("a", {"id": "documentsbutton"})['href'] # get the link from documents button.
                        url = "https://www.sec.gov" + link
                        indexlink_list.append(url)
                        indexlink = indexlink_list[0]  # get latest 10=k filing link
                        print(indexlink_list)

            souped_button = make_soup(indexlink) # parse the link. we're so close to 10-k filing
            table2 = souped_button.find("div", {"id": "seriesDiv"})
            tables_page = "https://www.sec.gov" + table2.find("a")["href"] # get link from "interactive" button.

            souped_excel_button = make_soup(tables_page)
            excel_button = souped_excel_button.find("td").find_all("a")[1]['href']
            excel_link = "https://www.sec.gov" + excel_button #get excel link from "view excel document" button. this excel file includes all data from latest 10-k filing.
            print(excel_link)


            excel_sheet_name = pd.ExcelFile(excel_link).sheet_names #the problem with this excel file is, there are too much sheets.
            #the table we're looking for is sometimes named as "cash flows statements". sometimes "consolidated statements of cash"

            print(excel_sheet_name)

            choice_one = process.extractOne("CASH FLOWS STATEMENTS", excel_sheet_name) # use fuzzywuzzy libray and choose the highest score as sheetname
            choice_two = process.extractOne("CONSOLIDATED STATEMENTS OF CASH", excel_sheet_name)
            if choice_two[1] > choice_one[1]:
                cash_flows_sheet = choice_two[0]
            else:
                cash_flows_sheet = choice_one[0]  # the table cash_flows_sheet is the sheet we're looking for.
                print(choice_one)
                print(choice_two)

            df = pd.read_excel(excel_link, sheet_name=cash_flows_sheet, na_filter=False) #read the excel file
            print(df)

            html_table = df.to_html(index=False) #store table as html


            json_table = df.to_json() #store table as json.
            print(json_table)
            # it's time to store and display the data on our website
            rf = Companies.objects.get_or_create(cik=cik,
                                     primarysymbol=primarysymbol,
                                     companyname=companyname,
                                     jsonnn=json_table,
                                     table=html_table,
                                     markettier=markettier,
                                     sicdescription = sicdescription)
            #m2 = Companies(table=html_table, jsonnn=json_table, **data)

            print(rf)

            #for y in ticker_list:
            company_inf = Companies.objects.filter(primarysymbol__iexact=data.get("primarysymbol", ""))
            print(company_inf)



        context = {
            'data_list': data_list,
            'excel_link': excel_link,
            'html_table': html_table,
            'company_inf': company_inf

            }

        messages.success(request, "Data Parsed")
        return render(request, "company_list.html", context)

    else:
        Companies()
    return render(request, "company_list.html", {})


def company_detail(request, id, primarysymbol):
    company = get_object_or_404(Companies, id=id, primarysymbol=primarysymbol)
    companies = Companies.objects.all()
    context = {'company': company,
               'companies': companies,
               }
    return render(request, 'company_detail.html', context)

