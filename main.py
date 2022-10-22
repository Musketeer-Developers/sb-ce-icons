import glob
import pandas as pd
import selenium
from selenium import webdriver
import time
import requests
import os
import io
import hashlib
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import base64
from fastapi import FastAPI
import os
app = FastAPI()
###########################################CODE1 of SVG FOLDER ICONS################################################
label=[]
path=[]
read_images = [] 
folders = glob.glob('svg/*')
imagenames_list = []
for folder in folders:
    for f in glob.glob(folder+'/*.svg'):
        label.append(folder)
        path.append(f)


df = pd.DataFrame(columns = ['label' , 'path'])
df['label']=label
df['path']=path
df['label'] = df['label'].str.replace('svg','',regex=True)
df['label'] = df['label'].str.replace('\\','',regex=True)
df['label'] = df['label'].str.replace('\d+', '',regex=True)

base_64_list=[]
def search_icon(text):
    check=df.loc[df['label'].str.contains(text, case=False)]
    values_df=list(check['path'].iloc[0:10].values)

    for i in values_df:
        with open(i, "rb") as img_file:
            my_string = base64.b64encode(img_file.read())
            base_64_list.append(my_string)
   
    return base_64_list

###########################################CODE2 of GOOGLE SCRAPPED ICONS LINKS################################################


def fetch_image_urls(query:str, max_links_to_fetch:int, wd:webdriver, sleep_between_interactions:int=1):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)    
    
    # build the google query
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

    # load the page
    wd.get(search_url.format(q=query))

    image_urls = set()
    image_count = 0
    results_start = 0
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail_results = wd.find_elements(By.CSS_SELECTOR,"img.Q4LuWd")
        number_results = len(thumbnail_results)
        
        # print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")
        
        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail such that we can get the real image behind it
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            # extract image urls    
            actual_images = wd.find_elements(By.CSS_SELECTOR,'img.n3VNCb')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.add(actual_image.get_attribute('src'))

            image_count = len(image_urls)

            if len(image_urls) >= max_links_to_fetch:
                # print(f"Found: {len(image_urls)} image links, done!")
                break
        else:
            # print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(30)
            return
            load_more_button = wd.find_element_by_css_selector(".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")

        # move the result startpoint further down
        
        results_start = len(thumbnail_results)
            # wd.quit()
    return image_urls




links_img=[]
@app.get("/")
def root():
    return {"message": "Hello User"}

@app.post("/Search_Icon")
def search_and_download(search_term:str):
    
    # DRIVER_PATH = 'chromedriver.exe'

    query=search_term + " icon"

    number_images=10
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")

    with webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),chrome_options=chrome_options) as wd:
        res = fetch_image_urls(query, number_images, wd=wd, sleep_between_interactions=0.5)
        links_img.append(res)
    
    links_img.append(search_icon(search_term))
    
    return links_img

