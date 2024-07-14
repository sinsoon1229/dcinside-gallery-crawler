import asyncio
from datetime import datetime
import json
import os
import shutil
import subprocess
import time

# Import pip modules
import importlib.util

if importlib.util.find_spec('httpx') is None or \
   importlib.util.find_spec('aiofiles') is None or \
   importlib.util.find_spec('bs4') is None:
    print('======================================================================')
    print('Module import error raised, installing required modules.')
    print('======================================================================')
    subprocess.run(['pip', 'install', '-r', './requirements.txt'])
    print('======================================================================')

import aiofiles
from bs4 import BeautifulSoup
import httpx

# Set core variables with config values
with open('./config.json', 'r') as f:
    config = json.load(f)

GALLERY_ID: str = config['gallery_id']
GALLERY_URL: str = 'https://gall.dcinside.com/m/' + GALLERY_ID
start_from: int = config['start_from']

SAVE_DIR: str = config['save_dir'].rstrip('/')

UPDATE_INTERVAL: int = config['update_interval_second']
RETRY_INTERVAL: int = config['retry_interval_second']

ESSENTIAL_HEADERS: dict[str, str] = config['essential_header']
VIDEO_IFRAME_HEADERS: dict[str, str] = ESSENTIAL_HEADERS | config['additional_video_iframe_header']
VIDEO_HEADERS: dict[str, str] = ESSENTIAL_HEADERS | config['additional_video_header']

def log_print(log_type: str, message: str):
    print(f'{log_type:<8} | {datetime.now():%Y-%m-%d %X}: {message}')

async def http_get(url: str, headers: dict[str, str], *, until_ok=True) -> bytes:
    async with httpx.AsyncClient(follow_redirects=True) as client:
        while True:
            try:
                response = await client.get(url, headers=headers)
                if response.status_code < 300:
                    return await response.aread()
                elif response.status_code < 500:
                    response.raise_for_status()
            except httpx.HTTPStatusError:
                raise
            except:
                if not until_ok:
                    raise

            time.sleep(RETRY_INTERVAL)

async def get_latest_article_number() -> int:
    while True:
        response = await http_get(GALLERY_URL, headers=ESSENTIAL_HEADERS)
        soup = BeautifulSoup(response.decode(), 'html.parser')

        latest_article = soup.select_one('tr:not([data-type="icon_notice"]).us-post')

        if latest_article is not None:
            latest_article_number = latest_article.select_one('td.gall_num')

            if latest_article_number is not None:
                return int(latest_article_number.text)

        time.sleep(RETRY_INTERVAL)

async def save_binary(data: bytes, path: str):
    async with aiofiles.open(path, 'wb') as f:
        await f.write(data)

async def crawl_article(article_number: int):
    try:
        response = await http_get(f'{GALLERY_URL}/{article_number}', ESSENTIAL_HEADERS)
        article = BeautifulSoup(response.decode(), 'html.parser')
    except:
        log_print('FAIL', f'Failed to get article {article_number}')
        return

    # Step 1. Query select core elements
    title_element = article.select_one('span.title_subject')
    writer_element = article.select_one('div.gall_writer.ub-writer')
    date_element = article.select_one('span.gall_date')
    text_element = article.select_one('div.write_div')
    image_elements = article.select('ul.appending_file > li > a')
    video_iframe_elements = article.select('iframe[id^="movie"]')

    # Step 2. Check if any core elements are not exist
    #         We don't need to check image and video elements(It can be not exist)
    try:
        assert title_element is not None
        assert writer_element is not None
        assert date_element is not None
        assert text_element is not None
    except AssertionError:
        log_print('FAIL', f'Some of core elements are not found\n\tAt article {article_number}')
        return

    # Step 3. Get string data including title, nickname, id, date and text of article
    title = title_element.text
    nickname = writer_element.attrs.get('data-nick')
    id = writer_element.attrs.get('data-uid') or\
         writer_element.attrs.get('data-ip')
    date = date_element.attrs.get('title')
    text = text_element.get_text()

    # Step 4. Check if any writer/date elements are not exist
    try:
        assert nickname is not None
        assert id is not None
        assert date is not None
    except AssertionError:
        log_print('FAIL', f'Some of elements(writer, date) are not found\n\tAt article {article_number}')
        return

    # Step 5-1. Create folder that we need to save in
    folder_path = f'{SAVE_DIR}/{article_number}'
    os.makedirs(folder_path, exist_ok=True)

    # Step 5-2. Get media data including images and videos
    #           We can process it asynchronously
    #           So, start async tasks first and finally gather all
    tasks = []

    # Step 5-3. Get image files
    for i, image_element in enumerate(image_elements, 1):
        image_url = image_element.attrs.get('href')

        if image_url is None:
            log_print('WARNING', f'Failed to find URL of image element\n\tAt article {article_number}, image {i}')
            continue

        try:
            response = await http_get(image_url, ESSENTIAL_HEADERS)
        except:
            log_print('WARNING', f'Failed to get image\n\tAt article {article_number}, image {i}')
            continue

        image_extension = image_url[image_url.rindex('.') + 1:]

        save_image_task = save_binary(response, f'{folder_path}/{i}.{image_extension}')
        tasks.append(save_image_task)

    # Step 5-4. Get video files
    for i, video_iframe_element in enumerate(video_iframe_elements, 1):
        video_iframe_url = video_iframe_element.attrs.get('src')

        if video_iframe_url is None:
            log_print('WARNING', f'Failed to find URL of video iframe\n\tAt article {article_number}, video {i}')
            continue

        try:
            response = await http_get(video_iframe_url, VIDEO_IFRAME_HEADERS)
        except:
            log_print('WARNING', f'Failed to get video\n\tAt article {article_number}, video {i}')
            continue

        iframe_soup = BeautifulSoup(response.decode(), 'html.parser')

        try:
            video_element = iframe_soup.select_one('video > source')
            assert video_element is not None

            video_url = video_element.attrs.get('src')
            assert video_url is not None
        except AssertionError:
            log_print('WARNING', f'Failed to find URL of video\n\tAt article {article_number}, video {i}')
            continue

        try:
            response = await http_get(video_url, VIDEO_HEADERS)
        except:
            log_print('WARNING', f'Failed to get video\n\tAt article {article_number}, video {i}')
            continue

        video_extension = video_url[video_url.rfind('=') + 1:]

        save_video_task = save_binary(response, f'{folder_path}/{i}.{video_extension}')
        tasks.append(save_video_task)

    # Step 6. Save text file of article
    with open(f'{folder_path}/content.txt', 'w', encoding='utf-8') as f:
        f.write('======================\n')
        f.write(f'Title: {title}\n')
        f.write(f'Nickname: {nickname}\n')
        f.write(f'ID: {id}\n')
        f.write(f'Date: {date}\n')
        f.write('======================\n')
        f.write(text)

    # Step 7. Gather all media get tasks
    #         If exception occurred while gathering, remove directory
    try:
        await asyncio.gather(*tasks)
    except:
        shutil.rmtree(folder_path)
        raise
    else:
        log_print('OK', f'Article {article_number} has been successfully crawled')

async def main():
    global start_from
    while True:
        latest_article_number = await get_latest_article_number()

        if start_from > latest_article_number:
            time.sleep(RETRY_INTERVAL)
            continue

        for i in range(start_from, latest_article_number + 1):
            await crawl_article(i)
            time.sleep(UPDATE_INTERVAL)

        start_from = latest_article_number + 1

if __name__ == '__main__':
    try:
        log_print('START', 'Crawler has been started')
        asyncio.run(main())
    except KeyboardInterrupt:
        log_print('STOP', 'Keyboard interrupt(Ctrl-C)')
