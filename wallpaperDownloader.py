import os
import arrow as moment

import pandas as pd
import urllib.request as imgReq

from time import sleep as wait
from pathlib import Path
from random import randint

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement

#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#

PATH_WEB_SCRAPER = str(f'{Path().absolute()}').replace('\\', "/")
PATH_DOWNLOAD = f'{PATH_WEB_SCRAPER}/downloads'
PATH_GAMES_LIST = f'{PATH_WEB_SCRAPER}/gamesLists'

#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#
"""
Please make sure you change the links below to refer to your Steam account!
They are, in order, Perfect Games, All Games and Recently Played.
If you have trouble finding the links:
- Go to your Steam profile on any browser
- Select 'Games' on the side-menu on the right
- Now you have a bunch of tabs and three of them will be labeled with what you want!
"""
URL_STEAM_PERFECT_GAMES = 'https://steamcommunity.com/id/Baby_Wolf/games?tab=perfect&fbclid=IwAR23-EperiAcuhECLmMipgDlAe4Qyj8fabhBo-TCq5mv3uCz374bF3Mecs4&sort=name'
URL_STEAM_ALL_GAMES = 'https://steamcommunity.com/id/Baby_Wolf/games?fbclid=IwAR23-EperiAcuhECLmMipgDlAe4Qyj8fabhBo-TCq5mv3uCz374bF3Mecs4&sort=name&tab=all'
URL_STEAM_RECENTLY_PLAYED = 'https://steamcommunity.com/id/Baby_Wolf/games?fbclid=IwAR23-EperiAcuhECLmMipgDlAe4Qyj8fabhBo-TCq5mv3uCz374bF3Mecs4&tab=recent'
#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#

URL_STEAM_PREFIX = 'https://store.steampowered.com/app/'
URL_BACKGROUND_VIEWER = 'https://www.steamcardexchange.net/index.php?backgroundviewer'
URL_WALLPAPER_PREFIX = 'https://steamcommunity.com/economy/profilebackground/items' #{appid}/#{id}.jpg
URL_WALLPAPER_DOWNLOAD = 'https://cdn.steamstatic.com/steamcommunity/public/images/items' #{appid}/#{id}.jpg

CLASS_GAME_DIV_CONTAINER = 'gameslistitems_GamesListItemContainer_29H3o'
CLASS_GAME_A = 'gameslistitems_GameName_22awl'

ID_INPUT_BACKGROUND_VIEWER = 'background-search-input'
CLASS_DIV_SEARCH_RESULT = 'background-result'
ID_DIV_SEARCH_LIST = 'background-search-results'
ID_DIV_BG_CONTAINER = 'background-slider'

DEFAULT_WAIT_TIME = 0.1
DEFAULT_TIMEOUT = 10
DEFAULT_RETRIES = 3
LOGIN_TIMEOUT = 300

#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#
"""
Using this controllers you may skip unnecessary parts of the code that
you already executed.
Here you may also select which games lists you want to access from your Steam Profile
"""
ACTIONS = {
    'accessGames': True,
    'searchForUrl': False,
    'downloadWallpapers': True,
    'zipImgs': False,
    'deleteImgs': False
}
GAMES_LIST_SELECTOR = {
    '100%': True,
    'AllGames': False,
    'RecentlyPlayed': False
}
#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#

HEADER = ['title', 'appid', 'url']
NOT_ALLOWED_CHARS = ['<', '>', ':', '\"', '/', '\\', '|', '?', '*']

#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#

def randomTime(min = 0, max = 10, decimal = 0):
    '''
    Returns a float between minimun and maximum defined with a set number of decimals
    '''
    power = 10 ** decimal
    time = randint(min * power, max * power) / power
    return time

def chromeOptionsSetup():
    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")
    return options

def startWebDriver ():
    driver = webdriver.Chrome(options = chromeOptionsSetup())
    driver.maximize_window()
    print('WebDriver started\n')
    return driver

def waitSteamLogin (driver: WebDriver):
    print("\n#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#\n")
    print('Waiting login')
    loggedIn = EC.presence_of_element_located((By.CLASS_NAME, CLASS_GAME_DIV_CONTAINER))
    WebDriverWait(driver, LOGIN_TIMEOUT, DEFAULT_WAIT_TIME).until(loggedIn)
    print('Logged in')
    print("\n#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#\n")

def accessSteam100edGames (driver: WebDriver):
    print(f"Accessing 100%ed games\n")
    driver.get(URL_STEAM_PERFECT_GAMES)
    waitSteamLogin(driver)
    wait(1)

def accessSteamAllGames (driver: WebDriver):
    print("Accessing all games\n")
    driver.get(URL_STEAM_ALL_GAMES)
    waitSteamLogin(driver)
    wait(1)

def accessSteamRecentlyPlayed (driver: WebDriver):
    print("Accessing recently played games\n")
    driver.get(URL_STEAM_RECENTLY_PLAYED)
    waitSteamLogin(driver)
    wait(1)

def findGamesFromSteam (driver: WebDriver):
    gamesLoaded = EC.presence_of_all_elements_located((By.CLASS_NAME, CLASS_GAME_DIV_CONTAINER))
    WebDriverWait(driver, DEFAULT_TIMEOUT, DEFAULT_WAIT_TIME).until(gamesLoaded)
    wait(1)
    gamesDivList = driver.find_elements(By.CLASS_NAME, CLASS_GAME_DIV_CONTAINER)
    gamesToPd = {'title': [gameDiv.find_element(By.CLASS_NAME, CLASS_GAME_A).text for gameDiv in gamesDivList],
                'appid': [gameDiv.find_element(By.CLASS_NAME, CLASS_GAME_A).get_attribute('href').removeprefix(URL_STEAM_PREFIX) for gameDiv in gamesDivList]}
    dfToAppend = pd.DataFrame(gamesToPd)
    return dfToAppend

def haveUrl(game: dict):
    try:
        if len(game['url']) > 0 : return True
    except: return False

def sendKeysWithInterval(keys: str, element: WebElement):
    try:
        for char in keys:
            element.send_keys(char)
            wait(randomTime(4, 5)/100)
    except: pass

def waitSearchList (driver: WebDriver):
    try:
        searchListLoaded = EC.presence_of_element_located((By.ID, ID_DIV_SEARCH_LIST))
        WebDriverWait(driver, DEFAULT_TIMEOUT, DEFAULT_WAIT_TIME).until(searchListLoaded)
        wait(1)
    except: pass

def findGameInList(driver: WebDriver, appid: int, lastSearch: list):
    retries = 0
    while retries < DEFAULT_RETRIES:
        try:
            resultsList = driver.find_elements(By.CLASS_NAME, CLASS_DIV_SEARCH_RESULT)
            if resultsList == lastSearch:
                wait(1)
                continue
            for gameInList in resultsList:
                if int(gameInList.get_attribute('data-appid')) == appid:
                    driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", gameInList)
                    wait(randomTime(4, 5, 1)/10)
                    gameInList.click()
                    return {'hasWallpaper': True, 'lastSearch': resultsList}
            wait(1)
            retries += 1
        except:
            retries += 1
    return {'hasWallpaper': False, 'lastSearch': resultsList}

def waitWallpaperListLoad(driver: WebDriver):
    listLoaded = EC.presence_of_element_located((By.ID, ID_DIV_BG_CONTAINER))
    WebDriverWait(driver, DEFAULT_TIMEOUT, DEFAULT_WAIT_TIME).until(listLoaded)
    wait(1)    

def strToList(string: str):
    lst = string.replace('\'', '').replace('[', '').replace(']', '').replace(' ', '').split(sep=',')
    jpgList = [jpgUrl for jpgUrl in lst if jpgUrl.endswith('.jpg')]
    return jpgList

def isWallpaperAlreadyDownloaded(url: str, title: str, appid: int, downloadedList: list):
    img = prepareDownloadLinkAndFileName(url, title, appid)
    if img['filename'] in downloadedList:
        img['downloaded'] = True
    return img

def removeEspecialChars(string: str):
    dirName = string
    for char in NOT_ALLOWED_CHARS:
        dirName = dirName.replace(char, '')
    return dirName

def prepareDownloadLinkAndFileName(url: str, title: str,appid: int):
    partialFilename = url.removeprefix(f'{URL_WALLPAPER_PREFIX}/{appid}/')
    downloadLink = f'{URL_WALLPAPER_DOWNLOAD}/{appid}/{partialFilename}'
    titleToFile = removeEspecialChars(title)
    filename = f'{titleToFile}_{partialFilename}'
    return {'filename': filename, 'downloadLink': downloadLink, 'downloaded': False}

#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#

print('Creating directory (gamesLists)\n')
path = Path(f'{PATH_GAMES_LIST}')
path.mkdir(parents = True, exist_ok = True)

def initializeWebDriver():
    print('Starting WebDriver\n')
    global driver
    driver = startWebDriver()

def accessGames():
    try:
        if GAMES_LIST_SELECTOR['100%'] or GAMES_LIST_SELECTOR['AllGames']:
            df = pd.DataFrame(columns = HEADER)
            if(GAMES_LIST_SELECTOR['100%']):
                accessSteam100edGames(driver)
                gamesToPd = findGamesFromSteam(driver)
                df = pd.concat([df, gamesToPd])
            if(GAMES_LIST_SELECTOR['AllGames']):
                accessSteamAllGames(driver)
                gamesToPd = findGamesFromSteam(driver)
                df = pd.concat([df, gamesToPd])
            if(GAMES_LIST_SELECTOR['RecentlyPlayed']):
                accessSteamRecentlyPlayed(driver)
                gamesToPd = findGamesFromSteam(driver)
                df = pd.concat([df, gamesToPd])
            df.drop_duplicates(inplace = True)
            print('Saving games information\n')
            timestamp = moment.now().format("YYYY_MM_DD-HH_mm_ss") 
            df.to_csv(f'{PATH_GAMES_LIST}/gamesList-{timestamp}.csv', index = False)
    except Exception as error:
        print('-----------------------------------------------------------')
        print('Access and save game titles')
        print('-----------------------------------------------------------')
        print(error)
        try: print(error['message'])
        except: pass
        exit()

def createUniqueCsv():
    print('Creating directory (downloads)\n')
    path = Path(f'{PATH_DOWNLOAD}')
    path.mkdir(parents = True, exist_ok = True)

    print("\n#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#\n")
    print("Please move the files you want the bot to read from 'gamesLists' to 'downloads' folder")
    print("It may be the most recent file(s)")
    print('When done, please press "ENTER" and select the chrome tab the bot is running on')
    print("Please be aware that ALL CSV files will the read")
    print("All duplicate games will be removed")
    print("\n#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#")
    input()

    try:
        print('Reading all CSV files on "downloads"\n')
        filesList = os.listdir(path)
        csvList = [file for file in filesList if file.endswith('csv')]
        df = pd.DataFrame(columns = HEADER)
        for csvFile in csvList:
            dfToConcat = pd.read_csv(f'{path}/{csvFile}')
            df = pd.concat([df, dfToConcat])
        df.sort_values(['title', 'url'], inplace = True)
        df.drop_duplicates(inplace = True, subset = 'appid')
        df.reset_index(inplace = True, drop = True)
        df.to_csv(f'{PATH_DOWNLOAD}/_gamesList.csv', index = False)
    except Exception as error: 
        print('-----------------------------------------------------------')
        print('Read gamesCSV')
        print('-----------------------------------------------------------')
        print(error)
        try: print(error['message'])
        except: pass
        exit()

def searchForUrl():
    try:
        print('Accessing background viewer\n')
        driver.get(URL_BACKGROUND_VIEWER)
        wait(1)
        inputBox = driver.find_element(By.ID, ID_INPUT_BACKGROUND_VIEWER)
        df = pd.read_csv(f'{PATH_DOWNLOAD}/_gamesList.csv')
        gamesList = df.to_dict('records')
        inputBoxOutcome = {'lastSearch': ''}
        wallpaperList = ''
        wallpaperListPreviousOutcome = ''
        for game in gamesList:
            inputBox.clear()
            gameHasUrl = haveUrl(game)
            if gameHasUrl: continue
            print(f"#--- {game['title']} ---#")
            sendKeysWithInterval(game['title'], inputBox)
            wait(randomTime(6, 7)/10)
            waitSearchList(driver)
            wait(randomTime(1, 2)/10)
            inputBoxOutcome = findGameInList(driver, game['appid'], inputBoxOutcome['lastSearch'])
            if not inputBoxOutcome['hasWallpaper']: 
                print('No wallpapers found...\n')
                continue
            waitWallpaperListLoad(driver)
            divList = driver.find_element(By.ID, ID_DIV_BG_CONTAINER)
            while wallpaperListPreviousOutcome == wallpaperList:
                wait(0.2)
                wallpaperList = divList.find_elements(By.TAG_NAME, 'a')
            print(f'Found {len(wallpaperList)} wallpapers!\n')
            wallpaperListPreviousOutcome = wallpaperList
            urlList = [wallpaperElement.get_attribute('href') for wallpaperElement in wallpaperList]
            df.loc[df['title'] == game['title'], ['url']] = str(urlList)
        print('Saving all urls\n')
        df.to_csv(f'{PATH_DOWNLOAD}/_gamesList.csv', index = False)
    except Exception as error:
        print('-----------------------------------------------------------')
        print('Get Wallpaper links')
        print('-----------------------------------------------------------')
        print(error)
        try: print(error['message'])
        except: pass
        exit()

def downloadWallpapers():
    try:
        print('Downloading wallpapers\n')
        df = pd.read_csv(f'{PATH_DOWNLOAD}/_gamesList.csv')
        print('Creating directory (downloads/wallpapers)')
        path = Path(f'{PATH_DOWNLOAD}/wallpapers')
        path.mkdir(parents = True, exist_ok = True)
        downloadedList = os.listdir(path)
        gamesList = df.to_dict('records')
        for game in gamesList:
            haveWallpapers = haveUrl(game)
            if not haveWallpapers: continue
            print(f'#--- {game["title"]} ---#')
            urlList = strToList(game['url'])
            for wallpaperUrl in urlList:
                img = isWallpaperAlreadyDownloaded(wallpaperUrl, game['title'], game['appid'], downloadedList)
                if img['downloaded']: continue
                imgReq.urlretrieve(img['downloadLink'], f'{path}/{img["filename"]}')
            print(f'Downloaded {len(urlList)} wallpapers\n')
        print('Completed all downloads')
    except Exception as error:
        print('-----------------------------------------------------------')
        print('Download Wallpaper')
        print('-----------------------------------------------------------')
        print(error)
        try: print(error['message'])
        except: pass
        exit()

def zipImgs():
    pass

def main():
    if ACTIONS['accessGames'] or ACTIONS['searchForUrl']: initializeWebDriver()
    if ACTIONS['accessGames']: accessGames()
    createUniqueCsv()
    if ACTIONS['searchForUrl']: searchForUrl()
    if ACTIONS['downloadWallpapers']: downloadWallpapers()
    if ACTIONS['zipImgs']: zipImgs()

main()
