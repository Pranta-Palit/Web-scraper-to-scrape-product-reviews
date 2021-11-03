import csv
import datetime as dt
from time import sleep
from selenium import webdriver as wd
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.common.exceptions import NoSuchElementException # for missing element

# global variables
global temp
temp = []

# to compare dates, format it first
def format_date(day):
    return dt.datetime.strptime(day,'%B %d, %Y').date()

# read reviews from current page, return true if review date is still higher than target date
def read_reviews(driver, target_date, count_review=0):
    for day in driver.find_elements_by_class_name('review-date-submissionTime'):
        if format_date(day.text)>=target_date :
            review_date =  str(day.text)
            name = str(driver.find_elements_by_class_name('review-footer-userNickname')[count_review].text)
            
            try:
                title = str( (driver.find_elements_by_class_name('review-heading')[count_review]).find_element_by_class_name('review-title').text )
            except NoSuchElementException:
                title = ''
            
            description = str( driver.find_elements_by_class_name('review-text')[count_review].text )
            rating = str( driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div[1]/div/div[6]/div[1]/div['+ str(count_review+1) +']/div/div[1]/div/div[1]/div[1]/div/div/span[3]/span[2]').text )

            temp.append((review_date,name,title,description,rating))

            count_review += 1

            print("#"+str(count_review)+" collecting "+name+"'s review on "+review_date)
        
        else:
            return False

    return True


# control speed: set low value of x to make the process faster
x = 1

# set webdriver address
driver = wd.Chrome('./web driver/chromedriver95.exe')

target_url = 'https://www.walmart.com/ip/Clorox-Disinfecting-Wipes-225-Count-Value-Pack-Crisp-Lemon-and-Fresh-Scent-3-Pack-75-Count-Each/14898365'

# before opening the page, shows press and hold(xpath: /html/body) verification captcha, this iframe cannot be located, occurs randomly among 10 iframes, returns a dictionary and not possible to switch to that frame! it is an [object HTMLIFrameElement]
# blocked_url = 'https://www.walmart.com/blocked?url=L2lwL0Nsb3JveC1EaXNpbmZlY3RpbmctV2lwZXMtMjI1LUNvdW50LVZhbHVlLVBhY2stQ3Jpc3AtTGVtb24tYW5kLUZyZXNoLVNjZW50LTMtUGFjay03NS1Db3VudC1FYWNoLzE0ODk4MzY1&uuid=9ed7f800-f288-11eb-ad50-1b3c9c7d7310&vid=9cf07351-f288-11eb-9ab5-ef26d206453b&g=b'

# open the given url in Google chrome

driver.get(target_url)
WebDriverWait(driver, x*30)

driver.maximize_window()
WebDriverWait(driver, x*300)

# find and click xpath of 'See all reviews' button
see_all_reviews = driver.find_element_by_xpath('//*[@id="customer-reviews-header"]/div[2]/div/div[3]/a[2]/span')
see_all_reviews.location_once_scrolled_into_view
WebDriverWait(driver, x*20)
see_all_reviews.click()
WebDriverWait(driver, x*50)


# find and click xpath of sort option 'newest to oldest' button
# driver.find_element_by_xpath("//select[@aria-label='Sort by']/option[text()='newest to oldest']").click()
# sort = driver.find_element_by_xpath("/html/body/div[1]/div/div/div/div[1]/div/div[5]/div/div[2]/div/div[2]/div/div[2]/select/option[3]")
sort_by = driver.find_element_by_xpath("//select[@aria-label='Sort by']")
# Performs mouse move action onto the element
wd.ActionChains(driver).move_to_element(sort_by).perform()
WebDriverWait(driver, x*100)

# sort by newest to oldest
select_newest = Select(sort_by)
WebDriverWait(driver, x*100)
select_newest.select_by_visible_text('newest to oldest')
WebDriverWait(driver, x*150)
sleep(20)
print('reviews sorted by most recent first!')

target_date = format_date('December 1, 2020')
print('collecting all reviews till ',target_date)

# iterate pages to read reviews
page = 1
while True:
    print(f'\n\n\ncollecting reviews from page #{page}')
    WebDriverWait(driver,300)
    if read_reviews(driver,target_date):
        try:
            driver.find_element_by_class_name('paginator-btn.paginator-btn-next').click()
            WebDriverWait(driver, x*300)
            page += 1
        except:
            print('No more page available!')
            break
    else:
        break

# web driver task completed!
driver.quit()


# processing to write csv
print('writing collected data to excel file....',end='')

# field names 
fields = ['Review Date','Reviewer Name','Review Title','Review Body (Description)','Rating given by the user'] 
# name of csv file 
filename = "./src/output.csv"

# writing to csv file 
with open(filename, 'w', newline='', encoding='utf-8') as file: 
    # creating a csv dict writer object 
    writer = csv.writer(file) 
    # writing headers (field names) 
    writer.writerow(fields)
    # writing all data rows / all reviews
    writer.writerows(temp) 

print('[completed] | total printed rows: ',len(temp))