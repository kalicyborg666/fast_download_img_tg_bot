import time
from PIL import Image
from io import BytesIO
import os
import asyncio
import httpx
from auth_data import unplush_token  # file with API


# check valid folder and create folder if non-valid
def check_and_create_folder(query: str):
    if os.path.exists(f"$HOME/Pictures/{query}"):
        pass
    else:
        os.system(f"cd $HOME/Pictures;mkdir {query}")


# search and download image
async def download_as(query: str, num_page: int, size_img: str, lll: list, lst_url_img: list, download_img_in_server: bool):
    """
    https://api.unsplash.com/
    About:
    Default per_page = 10
    50 req/hour and lock api (if demo account)
    """
    header = {"Authorization": f"Client-ID {unplush_token}"}
    params = {'page': num_page + 1, 'per_page': 10, 'query': query}
    url = f"https://api.unsplash.com/search/photos"

    async with httpx.AsyncClient(http2=True) as client:
        r = await client.get(url, headers=header, params=params, timeout=None)
        if r.status_code == 200:
            r_json = r.json().get('results')
            if r_json:
                for i in r_json:
                    if download_img_in_server:
                        attrs = i.get('width'), i.get('height'), i.get(
                            'id'), i.get('urls').get(size_img)
                        response = await client.get(attrs[3], timeout=None)
                        image = Image.open(BytesIO(response.content))
                        num_photo = f'{attrs[2]}_{attrs[0]}x{attrs[1]}pixel'
                        query = query.lower().replace(' ', '_')
                        path_img = f"/home/joi/Pictures/{query}/{query}_{num_photo}.{attrs[3][attrs[3].find('fm=')+3:attrs[3].find('&', attrs[3].find('fm=')+4, attrs[3].find('fm=')+9)]}"
                        image.save(path_img)
                        lll.append(1)
                        lst_url_img.append(path_img)
                    else:
                        img_url = i.get('urls').get(size_img)
                        lst_url_img.append(img_url)
                        lll.append(1)
        else:
            print(r.status_code)


async def main_as(query: str, query_count: int, size_img: str, lll: list, lst_url_img: list, download_img_in_server: bool):
    await asyncio.gather(*[download_as(query, num_page, size_img, lll, lst_url_img, download_img_in_server) for num_page in range(query_count//10)])


def main(search_word, search_count, size_img):
    download_img_in_server = False
    if size_img == 'full':
        check_and_create_folder(search_word.lower().replace(' ', '_'))
        download_img_in_server = True
    lll = []  # List for counting the number of results found
    lst_url_img = []
    s_t = time.time()
    asyncio.run(main_as(search_word, search_count, size_img,
                lll, lst_url_img, download_img_in_server))
    e_t = time.time()
    return f"Loading time: {round(e_t - s_t,2)}sec.", f"Number of photos: {len(lll)}", \
        lst_url_img, len(lll), download_img_in_server
