from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
import pytesseract
import requests
from PIL import Image
import time
from scrapper import get_result


def start(roll, driver):  # start driver
    driver.get("http://result.rgpv.ac.in/result/BErslt.aspx")
    inputelement(roll, driver)


def inputelement(roll,driver): #input roll number and semester
    semester = 6
    input_element = driver.find_element_by_id("ctl00_ContentPlaceHolder1_txtrollno")
    input_element.send_keys(roll)
    sem = driver.find_element_by_id("ctl00_ContentPlaceHolder1_drpSemester")
    sem = Select(sem)
    sem.select_by_visible_text(str(semester))
    captecha_read(roll,driver)


def captecha_read(roll, driver): #read Captcha and fill
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
    get_result(roll, driver)


def click(driver): #click on submit button and try to click again it will help if capatcha cant be red correctly
    driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnviewresult").click()
    # print('clicked')
    try:
        driver.find_element_by_id('ctl00_ContentPlaceHolder1_btnviewresult').click()
    except:
        pass