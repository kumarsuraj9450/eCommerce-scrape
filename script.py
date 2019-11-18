from selenium import webdriver
from xlsxwriter import Workbook
from time import sleep
import os
from selenium.webdriver.chrome.options import Options
import requests
import urllib.request

chrome_options = Options()

driver=webdriver.Chrome('C:\chromedriver_win32\chromedriver.exe')#,chrome_options=chrome_options)
# main_url=str(input("Enter URL => "))
main_url='http://akratijewelsinc.com/shopping.aspx?cat=Wholesale+Silver+Jewelry&subcat=Ring'
driver.get(main_url)

section=str(main_url.split("=")[-1])
folder_name=section+"Ring_pic"
sheet_name=section+"Ring_data.xlsx"
sleep(5)

driver.maximize_window()

input("Scroll down 'UPTO BOTTOM' then hit any BUTTON TO CONTINUE")

driver.switch_to_window(driver.window_handles[0])

ele=driver.find_elements_by_xpath("//img[@class='margin_auto']//parent::a")

for i,e in enumerate(ele):
    ele[i]=e.get_attribute('href')

print(f"\nTotal Links :=> {len(ele)}")

if not os.path.exists(folder_name):
    os.makedirs(folder_name)

workbook_name=sheet_name
workbook=Workbook(workbook_name)
worksheet=workbook.add_worksheet()
worksheet.write(0, 0,'Product Name')  # 3 --> row number, column number, value
worksheet.write(0, 1, 'Code')
worksheet.write(0, 2, 'Weight')
worksheet.write(0, 3, 'Gemstone Used')
worksheet.write(0, 4, 'Photo 1')
worksheet.write(0, 5, 'Photo 2')

for i,url in enumerate(ele):
    driver.get(url)
    sleep(2)
    
    try:
        name=driver.find_element_by_xpath("//h2[@class='page_taital']").text
    except:
        name="None"
    worksheet.write(i+1, 0,name)
    
    try:
        code=driver.find_elements_by_xpath("//tbody//tr")[0].text.split(":")[1].strip()
    except:
        code="None"
    worksheet.write(i+1, 1,code)
    
    try:
        weight=driver.find_elements_by_xpath("//tbody//tr")[1].text.split("Weight")[1].strip()
    except:
        weight="None"
    worksheet.write(i+1, 2,weight)
    
    try:
        gem_used=driver.find_elements_by_xpath("//tbody//tr")[3].text.split("Used")[1].strip()
    except:
        gem_used="None"
    worksheet.write(i+1, 3,gem_used)
        
    pic=driver.find_elements_by_xpath("//ul[@class='piclist']//img")
    
    for index,p in enumerate(pic):
        if index>1:
            continue

        try:
            src=p.get_attribute('src')
        except:
            worksheet.write(i+1, 3+index+1,"None")
            break

        try:
            pic_name=src.split('/')[-1]
        except:
            pic_name=name+"_"+str(index+1)
        
        try:
            urllib.request.urlretrieve(str(src),f'{folder_name}/{pic_name}')
        except:
            print(f"error dowloading photo : {src}")

        worksheet.write(i+1, 3+index+1,f'{folder_name}/{pic_name}')

workbook.close()
driver.quit()
