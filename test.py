import requests
from bs4 import BeautifulSoup

url1 = "https://movie.douban.com/top250"
head = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

        }

for start_num in range(0,250,25):
    start_string = f"?start={start_num}"
    url = url1+start_string
    # print(url)
    response = requests.get(url=url, headers=head)
    response.encoding = "utf-8"
    content = response.text

    soup = BeautifulSoup(content, "html.parser")
    all_titles = soup.findAll("span", attrs={"class": "title"})
    for title in all_titles:
        title_str = title.string
        if "/" not in title_str:
            print(title_str)