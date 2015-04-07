"""
Identify images, upload them to google plus, post in hangouts
"""

import asyncio
import aiohttp
import asyncio
import os
import io

def _initialise(Handlers, bot=None):
    Handlers.register_handler(_watch_image_link, type="message")
    return []


@asyncio.coroutine
def _watch_image_link(bot, event, command):
    # Don't handle events caused by the bot himself
    if event.user.is_self:
        return

    if " " in event.text:
        """immediately reject anything with spaces, must be a link"""
        return

    probable_image_link = False
    event_text_lower = event.text.lower()
    if event_text_lower.startswith(("imgur.com/", "i.imgur.com/")):
        """special processing for naked imgur links with no protocol"""
        probable_image_link = True
    elif event_text_lower.startswith(("http://", "https://")):
        if event_text_lower.startswith(("http://imgur.com/", "https://imgur.com/")):
            """standard imgur links may not have an extension"""
            probable_image_link = True
        elif event_text_lower.endswith((".png", ".gif", ".gifv", ".jpg")):
            """all other image links should have a protocol and end with a valid extension"""
            probable_image_link = True
    if probable_image_link and "googleusercontent" in event_text_lower:
        """reject links posted by google to prevent endless attachment loop"""
        print("_watch_image_link(): rejected link {}".format(event.text))
        return

    if probable_image_link:
        link_image = event.text

        if "imgur.com" in link_image:
            """special imgur link handling"""
            if not link_image.endswith((".jpg", ".gif", "gifv", "png")):
                link_image = link_image + ".gif"
            link_image = "https://i.imgur.com/" + os.path.basename(link_image)
 
        link_image = link_image.replace(".gifv",".gif")

        print("_watch_image_link(): getting {}".format(link_image))

        filename = os.path.basename(link_image)
        r = yield from aiohttp.request('get', link_image)
        raw = yield from r.read()
        image_data = io.BytesIO(raw)

        image_id = yield from bot._client.upload_image(image_data, filename=filename)

        yield from bot._client.sendchatmessage(event.conv.id_, None, image_id=image_id)