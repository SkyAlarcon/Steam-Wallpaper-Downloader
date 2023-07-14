import os, csv, getpass
import arrow as moment

from time import sleep as wait
from AppOpener import close as kill
from pyautogui import press
from pynput.keyboard import Controller
from pathlib import Path
from random import randint

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#

WEB_SCRAPER_PATH = str(f'{Path().absolute()}').replace('\\', "/")
DRIVER_PATH = f'{WEB_SCRAPER_PATH}/webdriver/chromeDriver-v114'
DOWNLOAD_PATH = f'{WEB_SCRAPER_PATH}/downloads'
GAMES_LIST_PATH = f'{WEB_SCRAPER_PATH}/gamesLists'

STEAM_PLATINUM_URL = 'https://steamcommunity.com/id/Baby_Wolf/games?tab=perfect&fbclid=IwAR23-EperiAcuhECLmMipgDlAe4Qyj8fabhBo-TCq5mv3uCz374bF3Mecs4&sort=name'
STEAM_ALL_GAMES_URL = 'https://steamcommunity.com/id/Baby_Wolf/games?fbclid=IwAR23-EperiAcuhECLmMipgDlAe4Qyj8fabhBo-TCq5mv3uCz374bF3Mecs4&sort=name&tab=all' # unused, but available if wanted
BACKGROUND_VIEWER_URL = 'https://www.steamcardexchange.net/index.php?backgroundviewer'

INPUT_USERNAME_XPATH = '/html/body/div[1]/div[7]/div[4]/div[1]/div[1]/div/div/div/div[2]/div/form/div[2]'
INPUT_PASSWORD_XPATH = '/html/body/div[1]/div[7]/div[4]/div[1]/div[1]/div/div/div/div[2]/div/form/div[2]/input'
BUTTON_LOGIN_XPATH = '/html/body/div[1]/div[7]/div[4]/div[1]/div[1]/div/div/div/div[2]/div/form/div[4]/button'

GAME_DIV_CONTAINER_CLASS = 'gameslistitems_GamesListItemContainer_29H3o'
GAME_A_CLASS = 'gameslistitems_GameName_22awl'

INPUT_GAME_NAME_BACKGROUND_XPATH = '/html/body/main[1]/div[5]/input'

DEFAULT_WAIT_TIME = 0.1
LOGIN_TIMEOUT = 300

#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#

keyboard = Controller()

def randomTime(min = 0, max = 10, decimal = 0):
    '''
    Returns a float between minimun and maximum defined with a set number of decimals
    '''
    power = 10 ** decimal
    time = randint(min * power, max * power) / power
    return time

def getAllGamesNames (driver: WebDriver):
    gamesDivList = driver.find_elements(By.CLASS_NAME, 'gameslistitems_GamesListItemContainer_29H3o')
    gamesList = [gameDiv.find_element(By.CLASS_NAME, 'gameslistitems_GameName_22awl').text for gameDiv in gamesDivList]
    return gamesList

def saveGamesList (gamesList: list, fileName = 'gamesList'):
    path = Path(f'{GAMES_LIST_PATH}')
    path.mkdir(parents = True, exist_ok = True)
    timestamp = moment.now().format("YYYY_MM_DD-HH_mm_ss")
    csvFile = open(f'{GAMES_LIST_PATH}/{fileName}-{timestamp}.csv', 'w')
    gamesCSV = csv.DictWriter(csvFile, fieldnames = ['title'])
    gamesCSV.writeheader()
    for gameName in gamesList:
        gameDict = {'title': gameName}
        gamesCSV.writerow(gameDict)

#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#=-=-=-=-=-=-=-=-=-=#

path = Path(f'{DOWNLOAD_PATH}')
path.mkdir(parents = True, exist_ok = True)
try:
    driver = webdriver.Chrome()
    driver.maximize_window()

    driver.get(STEAM_PLATINUM_URL)
    loggedIn = EC.presence_of_element_located((By.CLASS_NAME, GAME_DIV_CONTAINER_CLASS))
    WebDriverWait(driver, LOGIN_TIMEOUT, DEFAULT_WAIT_TIME).until(loggedIn)
    wait(1)
    gamesList = getAllGamesNames(driver)
    saveGamesList(gamesList = gamesList)

    # driver.get(STEAM_ALL_GAMES_URL)
    # wait(1)
    # gamesList = getAllGamesNames(driver)
    # saveGamesList(gamesList = gamesList)

except Exception as error:
    print('-----------------------------------------------------------')
    print('-----------------------------------------------------------')
    print('-----------------------------------------------------------')
    print(error)
    try: print(error['message'])
    except: pass