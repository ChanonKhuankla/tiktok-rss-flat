from http import cookies
import os
import asyncio
import csv
import time
import json
from datetime import datetime, timezone
import traceback
from feedgen.feed import FeedGenerator
# from tiktokapipy.api import TikTokAPI
from TikTokApi import TikTokApi
import config
from playwright.async_api import async_playwright, Playwright
from pathlib import Path
from urllib.parse import urlparse


# Edit config.py to change your URLs
ghRawURL = config.ghRawURL

api = TikTokApi()

# ms_token = os.environ.get(
#     "MS_TOKEN", None
# )


async def runscreenshot(playwright: Playwright, url, screenshotpath):
    chromium = playwright.chromium  # or "firefox" or "webkit".
    browser = await chromium.launch()
    page = await browser.new_page()
    await page.goto(url)
    # Save the screenshot
    await page.screenshot(path=screenshotpath, quality=20, type='jpeg')
    await browser.close()


async def user_videos():
    ms_token = ""
    try:
        async with async_playwright() as playwright:
            chromium = playwright.chromium  # or "firefox" or "webkit".
            browser = await chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto('https://www.tiktok.com/@pdkm.tech')
            cookies_list = await page.context.cookies()
            for cookie in cookies_list:
                if cookie['name'] == 'msToken':
                    ms_token = cookie['value']
                    print(f'Found msToken cookie: {ms_token}')
                    break
            await browser.close()
    except Exception as e:
        print(f"❌ Error taking screenshot: {e}")

    with open('subscriptions.csv') as f:
        cf = csv.DictReader(f, fieldnames=['username'])
        for row in cf:
            user = row['username']

            print(f'Running for user \'{user}\'')

            fg = FeedGenerator()
            fg.id('https://www.tiktok.com/@' + user)
            fg.title(user + ' TikTok')
            fg.author({'name': 'Conor ONeill',
                      'email': 'conor@conoroneill.com'})
            fg.link(href='http://tiktok.com', rel='alternate')
            fg.logo(ghRawURL + 'tiktok-rss.png')
            fg.subtitle('OK Boomer, all the latest TikToks from ' + user)
            fg.link(href=ghRawURL + 'rss/' + user + '.xml', rel='self')
            fg.language('en')

            # Set the last modification time for the feed to be the most recent post, else now.
            updated = None

            # Prepare JSON data structure for the user
            user_json_data = {
                "user": user,
                "updated": None,
                "videos": []
            }

            async with TikTokApi() as api:
                await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, headless=False)
                ttuser = api.user(user)
                try:
                    user_data = await ttuser.info()
                    # Store user info in JSON data
                    user_json_data["user_info"] = {
                        "username": user,
                        "retrieved_at": datetime.now(timezone.utc).isoformat()
                    }

                    async for video in ttuser.videos(count=10):
                        # RSS feed entry
                        fe = fg.add_entry()
                        link = "https://tiktok.com/@" + user + "/video/" + video.id
                        fe.id(link)
                        ts = datetime.fromtimestamp(
                            video.as_dict['createTime'], timezone.utc)
                        fe.published(ts)
                        fe.updated(ts)
                        updated = max(ts, updated) if updated else ts

                        # Extract video data
                        title = video.as_dict['desc'] if video.as_dict['desc'] else "No Title"
                        content = video.as_dict['desc'] if video.as_dict['desc'] else "No Description"

                        # Set RSS entry data
                        fe.title(title[0:255] if title else "No Title")
                        fe.link(href=link)

                        # Handle thumbnail
                        thumbnail_url = None
                        if video.as_dict['video']['cover']:
                            videourl = video.as_dict['video']['cover']
                            parsed_url = urlparse(videourl)
                            path_segments = parsed_url.path.split('/')
                            last_segment = [
                                seg for seg in path_segments if seg][-1]

                            screenshotsubpath = "thumbnails/" + user + \
                                "/screenshot_" + last_segment + ".jpg"
                            screenshotpath = os.path.dirname(
                                os.path.realpath(__file__)) + "/" + screenshotsubpath
                            if not os.path.isfile(screenshotpath):
                                async with async_playwright() as playwright:
                                    await runscreenshot(playwright, videourl, screenshotpath)
                            screenshoturl = ghRawURL + screenshotsubpath
                            thumbnail_url = screenshoturl
                            content = '<img src="' + screenshoturl + '" / > ' + content

                        fe.content(content)

                        # Add to JSON data
                        video_json = {
                            "id": video.id,
                            "link": link,
                            "title": title,
                            "description": video.as_dict['desc'] if video.as_dict['desc'] else "",
                            "created_time": ts.isoformat(),
                            "thumbnail_url": thumbnail_url,
                            "cover_url": video.as_dict['video']['cover'] if video.as_dict.get('video', {}).get('cover') else None,
                            "author": user,
                            "stats": {
                                "views": video.as_dict.get('stats', {}).get('playCount', 0),
                                "likes": video.as_dict.get('stats', {}).get('diggCount', 0),
                                "comments": video.as_dict.get('stats', {}).get('commentCount', 0),
                                "shares": video.as_dict.get('stats', {}).get('shareCount', 0)
                            }
                        }
                        user_json_data["videos"].append(video_json)

                    # Update timestamps
                    fg.updated(updated)
                    user_json_data["updated"] = updated.isoformat(
                    ) if updated else datetime.now(timezone.utc).isoformat()

                    # Create directories if they don't exist
                    os.makedirs('rss', exist_ok=True)
                    os.makedirs('json', exist_ok=True)

                    # Write the RSS feed to a file
                    fg.rss_file('rss/' + user + '.xml', pretty=True)

                    # Write the JSON data to a file
                    json_filename = f'json/{user}.json'
                    with open(json_filename, 'w', encoding='utf-8') as json_file:
                        json.dump(user_json_data, json_file,
                                  indent=2, ensure_ascii=False)

                    print(
                        f'✅ Generated RSS: rss/{user}.xml and JSON: {json_filename}')
                    # print(video)
                    # print(video.as_dict)
                except Exception as e:
                    print(f'❌ Error processing user {user}: {e}')


if __name__ == "__main__":
    asyncio.run(user_videos())
