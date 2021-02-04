from stout_setup import StdWithTimeStamp
from config import AFTER_N_DAYS, NUMBER_OF_GUESTS, TIME
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from time import sleep
import sys
from datetime import date,timedelta

opt = webdriver.ChromeOptions()
opt.add_argument("--no-sandbox")
opt.add_argument("--disable-gpu")
opt.add_argument("--headless")
opt.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=opt)
driver.get('https://kiaraseattle.securecafe.com/residentservices/kiara/userlogin.aspx')
sys.stdout = StdWithTimeStamp(sys.stdout)
booked_time = 'hh:mm XX'

def wait_until(callback,time=60):
    tick=0
    while tick<time:
        if callback():
            return
        tick+=1
        sleep(1)

def select_value(id,value,extra_criteria=''):
    wait_until(lambda: is_displayed('//select[@id="{}"]{}'.format(id,extra_criteria)))
    if driver.find_element_by_xpath('//select[@id="{}"]/option[text() = "{}"]'.format(id,value)).is_enabled():
        driver.find_element_by_xpath('//select[@id="{}"]'.format(id)).click()
        driver.find_element_by_xpath('//select[@id="{}"]/option[text() = "{}"]'.format(id,value)).click()
    else:
        raise RuntimeWarning("{} not availabe".format(value))

def fill_input(id,value,extra_step=None):
    wait_until(lambda: is_displayed('//input[@id="{}"]'.format(id)))
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
    try:
        select_value('AmPmStart','PM')
    except RuntimeWarning:
        #For some reason, the website will fail at the first time when you select 
        #the PM selection dropdown. We will pass the first exception
        sleep(2)
        pass

    for t in time:
        ampm = t['ampm']
        hour = t['hour']
        try:
            select_value('AmPmStart',ampm)
            sleep(2)
            select_value('HoursStart',hour)
            return '{}:00 {}'.format(hour, ampm)
        except RuntimeWarning as e:
            print('[WARN] {}:00 --- {}'.format(hour,str(e)))
            sleep(2)
            continue
    raise RuntimeError('Failed to book the fitness room for {}'.format(time))
    
def switch_to_document_page():
    wait_until(lambda:is_displayed('//iframe[@id="ySignatureDocViewer"]'))
    driver.switch_to.frame(driver.find_elements_by_xpath('//iframe[@id="ySignatureDocViewer"]')[0])


print('[START] Booking fitness room with {} guest at {}. Potential pickable time {}'.format(NUMBER_OF_GUESTS,date.today()+timedelta(AFTER_N_DAYS),TIME))
#####Log in#####
fill_input('Username','dingdingvsjj@gmail.com')
fill_input('Password','5511774aA!')
click_button('SignIn')
wait_until(lambda: driver.current_url == 'https://kiaraseattle.securecafe.com/residentservices/kiara/home.aspx')
print('[INFO] Signed in')

#####Go to booking page#####
driver.find_element_by_xpath('//a[@id="Concierge_MenuLink"]').click()
driver.find_element_by_xpath('//a[@id="conciergereservationsaspx_SubmenuLink"]').click()
wait_until(lambda: driver.current_url == 'https://kiaraseattle.securecafe.com/residentservices/kiara/conciergereservations.aspx#tab_MakeAReservation')
print('[INFO] In the booking page')

#####Book Fitness center#####
select_value('ResourceId','Fitness Center')
fill_input('GuestCount',NUMBER_OF_GUESTS,lambda: driver.find_element_by_xpath('//input[@id="GuestCount"]').send_keys(Keys.BACK_SPACE))

wait_until(lambda:is_displayed('//div[@id="page_loading"'),time=3)
wait_until(lambda:not is_displayed('//div[@id="page_loading"'),time=10)

select_date(AFTER_N_DAYS)
try:
    booked_time = booking_time(TIME)
except RuntimeError as e:
    print("[ERROR] {}".format(str(e)))
    driver.quit()
    exit(0)

click_button('btnCreateReservation')
click_button('btnPayNow')
get_alert().accept()
print('[INFO] Booked fitness room at {}'.format(booked_time))

#####Sign Document#####
switch_to_document_page()
click_button('BUTTON_SIGNA01_1')
click_button('docFooterRightButton')
click_button('messageModalButton')
print('[INFO] Signed all documentation')

#####Check Result#####
wait_until(lambda: driver.current_url == 'https://kiaraseattle.securecafe.com/residentservices/kiara/conciergereservations.aspx#tab_ViewReservations')
wait_until(lambda:is_displayed('//table[@id="ReservationStatus"]'))

booked_date = driver.find_element_by_xpath('//table[@id="ReservationStatus"]/tbody/tr[1]/td[3]').text
status = driver.find_element_by_xpath('//table[@id="ReservationStatus"]/tbody/tr[1]/td[7]').text

print('[INFO] Successfully booked {} {} {}'.format(booked_date, booked_time, status))
driver.quit()
print('[DONE] :-)\n')