from config import AFTER_N_DAYS, NUMBER_OF_GUESTS, TIME
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from time import *
from datetime import date,timedelta

driver = webdriver.Chrome()
driver.get('https://kiaraseattle.securecafe.com/residentservices/kiara/userlogin.aspx')

def wait_until(callback,time=60):
    tick=0
    while tick<time:
        if callback():
            return
        tick+=1
        sleep(1)

def select_value(id,value,extra_criteria=''):
    wait_until(lambda: is_displayed('//select[@id="{}"]{}'.format(id,extra_criteria)))
    if driver.find_element_by_xpath('//select@id="{}"]'.format(id)).is_enabled():
        driver.find_element_by_xpath('//select[@id="{}"]'.format(id)).click()
        driver.find_element_by_xpath('//select[@id="{}"]/option[text() = "{}"]'.format(id,value)).click()
    else:
        print('[WARN] {} not availabe".format(value)'.format(value))
        raise RuntimeWarning("{} not availabe".format(value))

def fill_input(id,value,extra_step=None):
    driver.find_element_by_xpath('//input[@id="{}"]'.format(id)).click()
    if extra_step:
        extra_step()
    driver.find_element_by_xpath('//input[@id="{}"]'.format(id)).send_keys(str(value))

def click_button(id):
    wait_until(lambda:is_displayed('//button[@id="{}"]'.format(id)))
    driver.find_element_by_xpath('//button[@id="{}"]'.format(id)).click()

def is_displayed(xpath):
    try:
        return driver.find_element_by_xpath(xpath=xpath).is_displayed()
    except NoSuchElementException:
        return False

def get_alert():
    WebDriverWait(driver=driver, timeout= 60).until(EC.alert_is_present(),
    'Timed out waiting for PA creation confirmation popup to appear.')
    return driver.switch_to.alert
    
def select_date(days_later):
    driver.find_element_by_xpath('//input[@id="StartDate"]').click()
    wait_until(lambda: is_displayed('//div[@id="ui-datepicker-div"]'))
    td = date.today()
    ed = td + timedelta(days=days_later)

    currentMonth = driver.find_element_by_xpath('//div[@id="ui-datepicker-div"]//span[@class="ui-datepicker-month"]').text
    expectedMonth = ed.strftime('%B')
    if currentMonth != expectedMonth:
        driver.find_element_by_xpath('//div[@id="ui-datepicker-div"]//a[contains(@class,"ui-datepicker-next")]').click()
    driver.find_element_by_xpath('//div[@id="ui-datepicker-div"]//a[text()={}]'.format(ed.day)).click()

def booking_time(time):
    for t in time:
        ampm = t['ampm']
        hour = t['hour']
        try:
            select_value('AmPmStart',ampm)
            sleep(2)
            select_value('HoursStart',hour)
            print('{}:00 {} {} guest ')
            break
        except RuntimeWarning:
            continue
    
def switch_to_document_page():
    wait_until(lambda:is_displayed('//iframe[@id="ySignatureDocViewer"]'))
    driver.switch_to.frame(driver.find_elements_by_xpath('//iframe[@id="ySignatureDocViewer"]')[0])


#####Log in#####
fill_input('Username','dingdingvsjj@gmail.com')
fill_input('Password','5511774aA!')
click_button('SignIn')
wait_until(lambda: driver.current_url == 'https://kiaraseattle.securecafe.com/residentservices/kiara/home.aspx')

#####Go to booking page#####
driver.find_element_by_xpath('//a[@id="Concierge_MenuLink"]').click()
driver.find_element_by_xpath('//a[@id="conciergereservationsaspx_SubmenuLink"]').click()
wait_until(lambda: driver.current_url == 'https://kiaraseattle.securecafe.com/residentservices/kiara/conciergereservations.aspx#tab_MakeAReservation')

#####Book Fitness center#####
select_value('ResourceId','Fitness Center')
select_value('OverbookReason','Fitness','[not(@disabled)]')
fill_input('GuestCount',NUMBER_OF_GUESTS,lambda: driver.find_element_by_xpath('//input[@id="GuestCount"]').send_keys(Keys.BACK_SPACE))

wait_until(lambda:is_displayed('//div[@id="page_loading"'),time=10)
wait_until(lambda:not is_displayed('//div[@id="page_loading"'),time=10)

select_date(AFTER_N_DAYS)
booking_time(TIME)
click_button('btnCreateReservation')

click_button('btnPayNow')
get_alert().accept()

#### this URL is not correct
switch_to_document_page()
click_button('BUTTON_SIGNA01_1')
click_button('docFooterRightButton')
click_button('messageModalButton')
print('DONE')