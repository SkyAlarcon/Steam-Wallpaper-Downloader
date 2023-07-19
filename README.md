# Steam Wallpaper Downloader
This project was created with the intention of studying web scraping and downloading images.

I merged the desire to download wallpapers to my Desktop and practice web scraping.

The documentation won't be too long, but I'm sure that you can figure out something that you need.

# What it does
This web scraper will look for games that you bought on your Steam account (Can be filtered to 'All games', 'Perfect Games' and/or 'Recently Played').

It find all wallpapers that Steam makes available to put in your profile and download them.

Pretty straight forward.

# How to use it

This code was developed in **Python**. So you may need to install Python3 to use it.

You will need to install some dependencies too:
- **pandas**
- **arrow**
- **selenium**

To set up everything properly, open **wallpaperDownloader.py** and insert your links on the variables:
- **URL_STEAM_PLATINUM** | Perfect Games
- **URL_STEAM_ALL_GAMES** | All Games
- **URL_STEAM_RECENTLY_PLAYED** | Recently Played

After that look for the variable **ACTIONS** and make sure that, at least for the first time you run the downloader **accessGames** is set to `True`. To do everything at once, be sure to set **searchForUrl** and **downloadWallpapers** to `True` also.

Right below **ACTIONS**, on **GAMES_LIST_SELECTOR**, set, AT LEAST, one of the fields to `True`, so the downloader knows where to retrieve the information.

I'm working on zipping all downloaded wallpapers to make the file lighter.