
#-------------------------------------------------------------------------------
# Name:        Rgpv Result Scraper 
# Purpose:  scrape rgpv result of whole batch
#
# Author:      Ayush 
#
#-------------------------------------------------------------------------------
import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
import pytesseract
import time
from bs4 import BeautifulSoup
import sqlite3

conn = sqlite3.connect('result.sqlite')
curr = conn.cursor()
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract'
driver = webdriver.Chrome("chromedriver.exe")


def start(roll,driver): #start driver
    driver.get("http://result.rgpv.ac.in/result/BErslt.aspx")
    inputelement(roll,driver)
    

def inputelement(roll,driver): #input roll number and semester
    input_element = driver.find_element_by_id("ctl00_ContentPlaceHolder1_txtrollno")
    input_element.send_keys(roll)
    sem = driver.find_element_by_id("ctl00_ContentPlaceHolder1_drpSemester")
    sem.send_keys(Keys.DOWN)
    sem.send_keys(Keys.DOWN)
    sem.send_keys(Keys.DOWN)
    sem.send_keys(Keys.DOWN)
    sem.send_keys(Keys.ENTER)
    sem.send_keys(Keys.ENTER)
    captecha_read(roll,driver)


def captecha_read(roll,driver): #read Captcha and fill
    lst = list()
    lst.clear()
    captecha_box = driver.find_element_by_id("ctl00_ContentPlaceHolder1_TextBox1")
    captecha_box.clear()
    images = driver.find_elements_by_tag_name('img')
    for image in images:
        a = image.get_attribute('src')
        lst.append(a)
    src = lst[1]
    response = requests.get(src)
    if response.status_code == 200:
        with open("sample.jpg", 'wb') as f:
            f.write(response.content)
    im = Image.open('sample.jpg')
    text = pytesseract.image_to_string(im)
    text = text.replace(" ", "").upper()
    captecha_box.send_keys(text)
    time.sleep(5)
    click(driver)
    get_result(roll,driver)

def click(driver): #click on submit button and try to click again it will help if capatcha cant be red correctly
    driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnviewresult").click()
    # print('clicked')
    try:
        driver.find_element_by_id('ctl00_ContentPlaceHolder1_btnviewresult').click()
    except:
        pass


def get_result(roll,driver): #get html of retult
    try:
        result = driver.find_element_by_id('ctl00_ContentPlaceHolder1_pnlGrading')
        html = result.get_attribute('innerHTML')
        #table_parser(html, roll)
        #file = open('result.txt','w')
        #file.write(html)
        with open('parsed.txt','a') as f:
              f.write(roll + '\n')
        table_parser(html,roll)
    except:pass

    try:
        time.sleep(5)
        driver.switch_to_alert().accept()
        
        captecha_read(roll,driver)
    except:
        with open('parsed.txt','a') as f:
              f.write(roll + '\n')
        with open('skiped.txt','a') as f:
              f.write(roll + '\n')
              





def table_parser(html ,roll): #extract student result from html
    #file = open('tele_html.txt').read()
    #file = open('result.txt').read()
    soup = BeautifulSoup(html, 'lxml')
    index = [3,4,5,6,7,8,9,10,11,12,13]
    table = str(soup.find_all('td')[1])
    table = BeautifulSoup(table, 'lxml')
    name = table.find_all('td')[2]
    name = name.get_text()

    table = str(soup.find_all('td')[61])
    table = BeautifulSoup(table, 'lxml')
    sgpa = table.get_text()


    table = str(soup.find_all('td')[62])
    table = BeautifulSoup(table, 'lxml')
    cgpa = table.get_text()


    table = str(soup.find_all('td')[60])
    table = BeautifulSoup(table, 'lxml')
    status = table.get_text()



    for i in index:
        table = soup.find_all('table')[i]
        for row in table.find_all('tr'):
            clm = row.find_all('td')
            clm = str(clm)
            #print(clm)
            containt_finder(clm,roll,name,sgpa,cgpa,status)


def containt_finder(clm,roll,name,sgpa,cgpa,status): #get grade for every subject

    soup = BeautifulSoup(clm, 'lxml')
    code = soup.find_all('td')[0]
    grade = soup.find_all('td')[3]
    code = code.get_text()
    grade = grade.get_text()
    code = code.replace("-", "")
    code = code.replace("[T]", "T")
    code = code.replace("[P]", "P")
    code = code.replace(" ", "_")


    create_db(code,roll)
    add_to_db(code,grade,roll,name,sgpa,cgpa,status)


def add_to_db(code,grade,roll,name,sgpa,cgpa,status): #fill grades in table
    curr.execute('INSERT or IGNORE into result(roll,Name,sgpa,cgpa,status) values(?,?,?,?,?) ', (roll,name,sgpa,cgpa,status,))
    curr.execute('UPDATE result set  {} = ? where roll = ? '.format(code), (grade,roll))
    conn.commit()



def create_db(code, roll): #create table
    curr.execute('''CREATE TABLE if NOT EXISTS result
              (roll text UNIQUE,Name text ,  sgpa text,cgpa text,status text)''')


    try:
        curr.execute(''' ALTER TABLE result
          ADD  '%s' text; '''%code )
        conn.commit()
    except:
        pass


def roll_list_gen(): #generate list of roll number
    #first = input('Enter First Roll number: ')
    #last = input('Enter Last Roll number: ')
    first  = '0702cs151001'
    last = '0702cs151040'
    roll_list = list()
    start = int(first[-4:])
    end = int(last[-4:])+1
    commen = first[:8]
    for i in range(start,end):
        i = str(i)
        roll = commen + i
        roll_list.append(roll)
    return(roll_list)


for roll in roll_list_gen():
    parsed = open('parsed.txt','r+').read().split()
    if roll not in parsed:
                start(roll,driver)
                print('parsing for '+roll)
driver.close()

