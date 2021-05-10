import language_check
import matplotlib.pyplot as plt
import pylab
from time import sleep
from requests import get
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json

tool = language_check.LanguageTool('en-US')
driver=webdriver.Firefox()


def get_driver():
    from selenium import webdriver
    return webdriver.Firefox()


def scroll(wait, nbr_of_scroll=1, time_to_sleep=15):
    for _ in range(nbr_of_scroll):
        # print("scroll")
        wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body"))).send_keys(Keys.END)
        sleep(time_to_sleep)


def get_commentary_list(wait):
    return [comment.text for comment in wait.until(EC.presence_of_all_elements_located((By.ID, "comment")))]


def accept_youtube_terms(driver):
    driver.find_element_by_tag_name('button').click()


def get_commentary_list_from_youtube_url(url):
    driver = get_driver()
    wait = WebDriverWait(driver, 15)
    driver.get(url)
    accept_youtube_terms(driver)
    driver.execute_script("window.scrollTo(0, 100)")
    sleep(4)
    driver.execute_script("window.scrollTo(0, 100)")
    scroll(wait, nbr_of_scroll=3)

    return [element.text for element in driver.find_elements_by_id('comment')]


def click_see_all_reviews(driver):
    driver.find_element_by_link_text('See all reviews').click()
    print('See all reviews')


def get_commentary_list_from_amazon_url(url):
    driver = get_driver()
    wait = WebDriverWait(driver, 15)
    driver.get(url)
    driver.execute_script("window.scrollTo(0, 100)")
    sleep(4)
    scroll(wait, nbr_of_scroll=2)
    click_see_all_reviews(driver)
    return [element.text for element in
            driver.find_elements_by_xpath("//div[contains(@class,'a-section a-spacing-none review-views celwidget')]")]


def get_table_amazon(comment_list):
    Amazon_Table = []
    for comment in comment_list:
        text_list = comment.split("\n")
        if len(text_list) < 4: continue
        text_list = text_list[:-1]
        commentary = "|".join(text_list[2:-1])
        Amazon_Table.append(commentary)
    Amazon_Table_Split = Amazon_Table[0].split("|")
    with open('Amazon.json', 'w', encoding='utf8') as out:
        json.dump(Amazon_Table_Split, out, indent=4, ensure_ascii=False)


def get_table_youtube(comment_list):
    Youtube_Table = []
    for comment in comment_list:
        text_list = comment.split("\n")
        if len(text_list) < 4: continue
        text_list = text_list[:-1]
        commentary = "|".join(text_list[2:-1])
        Youtube_Table.append(commentary)
    with open('Youtube.json', 'w', encoding='utf8') as out:
        json.dump(Youtube_Table, out, indent=4, ensure_ascii=False)

def display_mistakes(name):
    name_json = open(name + '.json', encoding='utf8')

    name_data = json.load(name_json)
    name_mistakes = 0

    for i in name_data:
        matches = tool.check(i)
        name_mistakes = name_mistakes + len(matches)

    name_mistakes_average = name_mistakes / len(name_data)
    print("Mistakes average on " + name + " : ", name_mistakes_average)
    return name_mistakes_average


def display():
    Youtube_mistakes_average = display_mistakes("Youtube")
    Times_mistakes_average = display_mistakes("Times")
    Amazon_mistakes_average = display_mistakes("Amazon")
    Twitter_mistakes_average = display_mistakes("Twitter")

    plt.figure()

    x = [1, 2, 3, 4]
    height = [Amazon_mistakes_average, Times_mistakes_average, Twitter_mistakes_average, Youtube_mistakes_average]
    BarName = ['Amazon', 'Times', 'Twitter', 'Youtube']

    plt.bar(x, height, color="cyan")

    plt.ylabel('Mistakes averages')
    plt.title('Mistakes averages on the Internet')

    pylab.xticks(x, BarName, rotation=40)

    plt.savefig('Mistakes averages on the Internet.png')
    plt.show()


def beautifulsoup():
    Times_Table = []
    reponse = get("https://www.nytimes.com/2021/05/07/style/elon-musk-memes.html")

    html_soup = BeautifulSoup(reponse.text, 'html.parser')

    texte = html_soup.find_all('p')
    for element in texte:
        Times_Table.append(element.text)

    with open('Times.json', 'w', encoding='utf8') as out:
        json.dump(Times_Table, out, indent=4, ensure_ascii=False)


def getReply_twitter(url):
    driver.get(url)

    time.sleep(5)

    wait = WebDriverWait(driver, 15)
    scroll(wait)
    scroll(wait)
    reptexts = driver.find_elements_by_xpath("//div[contains(@class,'css-901oao r-1fmj7o5 r-1qd0xha r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-bnwqim r-qvutc0')]")

    time.sleep(3)

    repList = []
    i = 0
    print(len(reptexts))
    while i < 15:
        texte = reptexts[i].text
        repList.append(texte)
        i += 1

    with open('Twitter.json', 'w', encoding='utf8') as out:
        json.dump(repList, out, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    url = 'https://twitter.com/elonmusk/status/1390387635961610242'
    getReply_twitter(url)

    url = "https://www.youtube.com/watch?v=fCF8I_X1qKI"
    comment_list = get_commentary_list_from_youtube_url(url)
    get_table_youtube(comment_list)

    url = "https://www.amazon.com/Elon-Musk-Ashlee-Vance-audiobook/dp/B00UVY52JO/ref=sr_1_1?crid=1PQZ3JHWYNB5W&dchild=1&keywords=elon+musk&qid=1620593404&sprefix=elon+%2Caps%2C230&sr=8-1"
    comment_list = get_commentary_list_from_amazon_url(url)
    get_table_amazon(comment_list)

    beautifulsoup()

    display()
