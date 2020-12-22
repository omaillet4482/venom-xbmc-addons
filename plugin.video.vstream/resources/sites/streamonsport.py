# -*- coding: utf-8 -*-
# Vstream https://github.com/Kodi-vStream/venom-xbmc-addons
# source 40 https://www.streamonsport version 2

from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.comaddon import progress #, VSlog
from resources.lib.util import  Quote
import re, base64

from resources.lib.packer import cPacker
from datetime import datetime, timedelta
import json

UA = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'

SITE_IDENTIFIER = 'streamonsport'
SITE_NAME = 'Streamonsport'
SITE_DESC = 'Site pour regarder du sport en direct'

URL_MAIN = 'https://www.streamonsport.info/'

SPORT_TV = (URL_MAIN + '31-sport-tv-fr-streaming.html', 'showMovies')
CHAINE_TV = (URL_MAIN + '2370162-chaines-tv-streaming.html', 'showMovies')
SPORT_LIVE = (URL_MAIN, 'showMovies')

SPORT_GENRES = (True, 'showGenres')
URL_SEARCH = (URL_MAIN + '?search=', 'showMovies') # recherche hs

SPORT_SPORTS = (True, 'showMenuHomeSport') 

def load():
    oGui = cGui()

    #oOutputParameterHandler = cOutputParameterHandler()
    #oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    #oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Rechercher', 'search.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SPORT_TV [0])
    oGui.addDir(SITE_IDENTIFIER, SPORT_TV[1], 'Chaines Sport TV', 'genres.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SPORT_LIVE[0])
    oGui.addDir(SITE_IDENTIFIER, SPORT_LIVE[1], 'Les Sports en direct', 'news.png', oOutputParameterHandler)

    # menu souvent vide 
    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SPORT_GENRES[0])
    oGui.addDir(SITE_IDENTIFIER, SPORT_GENRES[1], 'Sports (Genre)', 'genres.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', CHAINE_TV[0])
    oGui.addDir(SITE_IDENTIFIER, CHAINE_TV[1], 'Chaines generaliste TV', 'genres.png', oOutputParameterHandler)
    
    oGui.setEndOfDirectory()


def showMenuHomeSport():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SPORT_TV [0])
    oGui.addDir(SITE_IDENTIFIER, SPORT_TV[1], 'Chaines Sport TV', 'genres.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SPORT_LIVE[0])
    oGui.addDir(SITE_IDENTIFIER, SPORT_LIVE[1], 'Les Sports en direct', 'news.png', oOutputParameterHandler)

    # menu souvent vide 
    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SPORT_GENRES[0])
    oGui.addDir(SITE_IDENTIFIER, SPORT_GENRES[1], 'Sports (Genre)', 'genres.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showGenres():
    oGui = cGui()

    liste = []
    liste.append(['FootBall', URL_MAIN + '1-foot-streaming-ligue.html'])
    liste.append(['Rugby', URL_MAIN + '2-rugby-streaming.html'])
    liste.append(['Basketball', URL_MAIN + '3-basketball-streaming.html'])
    liste.append(['Real-Madrid', URL_MAIN + '4-formule-1-grand-prix-despagne-en-streaming-gratuit.html'] )
    liste.append(['Handball', URL_MAIN + '6-handball-streaming.html'])
    liste.append(['Tennis', URL_MAIN + '5-tennis-streaming.html'])
    liste.append(['Moto', URL_MAIN + '7-moto-gp-streaming-portugal.html'])
    #liste.append( ['Radio', URL_MAIN + '76-ecouter-la-radio-streaming.html'])

    for sTitle, sUrl in liste:
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sUrl)
        oGui.addDir(SITE_IDENTIFIER, 'showMovies', sTitle, 'genres.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


# inactif
def showSearch():
    oGui = cGui()

    sSearchText = oGui.showKeyBoard()
    if (sSearchText != False):
        sUrl = URL_SEARCH[0] + sSearchText
        showMovies(sUrl) 
        oGui.setEndOfDirectory()
        return

def showMovies(sSearch = ''):

    oGui = cGui()
    if sSearch:
        sUrl = sSearch
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    
    # THUMB ref title desc1 desc2
    sPattern = '<img class=".+?<img class=".+?src="([^"]+).+?<a class="game-name".+?href="([^"]+).+?title="([^"]+).+?class="date">([^<]+).+?sct_event_time">([^<]+)'

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == False):
        oGui.addText(SITE_IDENTIFIER)

    if (aResult[0] == True):
        total = len(aResult[1])
        progress_ = progress().VScreate(SITE_NAME)

        for aEntry in aResult[1]:
            progress_.VSupdate(progress_, total)
            if progress_.iscanceled():
                break

            sThumb = aEntry[0]
            sUrl2 = aEntry[1]
            sTitle = aEntry[2].replace(' streaming gratuit', '')
            sdesc1 = aEntry[3]
            sdesc2 = aEntry[4]
            sDisplayTitle = sTitle 
            if sUrl != CHAINE_TV[0] and sUrl != SPORT_TV[0]:
                sDisplayTitle = sTitle  + '-' + sdesc1 + '-' + sdesc2
            else:
                sTitle = sTitle.upper()
                sDisplayTitle = sTitle

            if 'http' not in sUrl2:
                sUrl2 = URL_MAIN[:-1] + sUrl2

            if 'http' not in sThumb:
                sThumb = URL_MAIN[:-1] + sThumb

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl2)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)

            oGui.addMisc(SITE_IDENTIFIER, 'showLive', sDisplayTitle, 'sport.png', sThumb, '', oOutputParameterHandler)

        progress_.VSclose(progress_)

    if not sSearch:
        oGui.setEndOfDirectory()


def showLive():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sThumb = oInputParameterHandler.getValue('sThumb')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    oParser = cParser()

    # liens visibles
    sPattern = 'btn btn-success btn-sm.+?src=\'([^\']*)'
    aResult = oParser.parse(sHtmlContent, sPattern)

    i = 0
    if (aResult[0] == True):
        total = len(aResult[1])
        progress_ = progress().VScreate(SITE_NAME)

        for aEntry in aResult[1]:
            progress_.VSupdate(progress_, total)
            if progress_.iscanceled():
                break

            i += 1 
            sUrl2 = aEntry
            sDisplayTitle = sMovieTitle + ' Link' + str(i)

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl2)
            oOutputParameterHandler.addParameter('sMovieTitle', sMovieTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oOutputParameterHandler.addParameter('siterefer', sUrl)
            oGui.addMisc(SITE_IDENTIFIER, 'Showlink', sDisplayTitle, 'sport.png','','', oOutputParameterHandler)

        progress_.VSclose(progress_)


    # 1 seul liens tv telerium
    sPattern = 'iframe id="video".src.+?id=([^"]+)'
    oParser = cParser()

    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0] == True):
        url2 = aResult[1][0]
        oRequestHandler = cRequestHandler(url2)
        sHtmlContent = oRequestHandler.request()

        sPattern = '<iframe.+?src="([^"]+)"'
        aResult = oParser.parse(sHtmlContent, sPattern)
        if aResult[0] == True:
               
            sUrl2 = aResult[1][0] # https://telerium.tv/embed/35001.html
            sDisplayTitle = sMovieTitle 

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl2)
            oOutputParameterHandler.addParameter('sMovieTitle', sMovieTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oOutputParameterHandler.addParameter('siterefer', sUrl)
            oGui.addDir(SITE_IDENTIFIER, 'Showlink', sDisplayTitle, 'sport.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def Showlink():
    oGui = cGui()

    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sThumb = oInputParameterHandler.getValue('sThumb')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    siterefer = oInputParameterHandler.getValue('siterefer')
    sUrl2 = ''
    shosterurl = ""

    if 'allfoot' in sUrl or 'channelstream' in sUrl:
        oRequestHandler = cRequestHandler(sUrl)
        oRequestHandler.addHeaderEntry('User-Agent', UA)
        #oRequestHandler.addHeaderEntry('Referer', siterefer) # a verifier
        sHtmlContent = oRequestHandler.request()
        sHosterUrl = ''
        oParser = cParser()
        sPattern = '<iframe.+?src="([^"]+)'
        aResult = oParser.parse(sHtmlContent, sPattern)

        if (aResult[0] == False):
            # https://embed.telerium.net/embed2.js
            # </iframe> ...src="//telerium.live/embed/'+id+'.html"></iframe>');
            # fichier js pas mis a jour car telerium.live pas valide
            sPattern = 'id=.(\d+).+?embed.telerium.+?<.script>'
            aResult2 = oParser.parse(sHtmlContent, sPattern) 
            if (aResult2[0] == True): 
                sUrl2 = 'https://telerium.club/embed/' + aResult2[1][0] + '.html'

        if (aResult[0] == True):
            sUrl2 = aResult[1][0]

    # pas de pre requete
    if 'laylow.cyou' in sUrl:
        sUrl2 = sUrl

    if 'telerium' in sUrl:  # chaine TV
        sUrl2 = sUrl

    if sUrl2:

        if 'telerium' in sUrl2:
            bvalid, shosterurl = Hoster_Telerium(sUrl2, sUrl)
            if bvalid:
                sHosterUrl = shosterurl

        if 'andrhino' in sUrl2:
            bvalid, shosterurl = Hoster_Andrhino(sUrl2, sUrl)
            if bvalid:
                sHosterUrl = shosterurl

        if 'wigistream' in sUrl2:
            bvalid, shosterurl = Hoster_Wigistream(sUrl2, sUrl)
            if bvalid:
                sHosterUrl = shosterurl

        # a verifier
        if 'laylow' in sUrl2:
            bvalid, shosterurl = Hoster_Laylow(sUrl2, sUrl)
            if bvalid:
                sHosterUrl = shosterurl

        if sHosterUrl:

            sHosterUrl = sHosterUrl.strip()
            oHoster = cHosterGui().checkHoster(sHosterUrl)
            if(oHoster != False):
                oHoster.setDisplayName(sMovieTitle)
                oHoster.setFileName(sMovieTitle)
                cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumb)

    oGui.setEndOfDirectory()


def Hoster_Telerium(url, referer):
    oRequestHandler = cRequestHandler(url)
    oRequestHandler.addHeaderEntry('User-Agent', UA)
    oRequestHandler.addHeaderEntry('Referer', referer)
    sHtmlContent = oRequestHandler.request()

    urlrederict = oRequestHandler.getRealUrl()
    urlmain = 'https://' + urlrederict.split('/')[2] # ex https://telerium.club

    sPattern = 'var\s+cid[^\'"]+[\'"]{1}([0-9]+)'
    aResult = re.findall(sPattern, sHtmlContent)

    if aResult:
        str2 = aResult[0]
        datetoken = int(getTimer()) * 1000

        jsonUrl = urlmain + '/streams/' + str2 + '/' + str(datetoken) + '.json'
        tokens = getRealTokenJson(jsonUrl, urlrederict)
        m3url = tokens['url']
        nxturl = urlmain + tokens['tokenurl']
        realtoken = getRealTokenJson(nxturl, urlrederict)[10][::-1]
        try:
            m3url = m3url.decode("utf-8")
        except:
            pass

        sHosterUrl = 'https:' + m3url + realtoken
        sHosterUrl += '|User-Agent=' + UA + '&Referer=' + Quote(urlrederict) # + '&Sec-F'

        return True, sHosterUrl

    return True, False

def Hoster_Andrhino(url, referer):
    oRequestHandler = cRequestHandler(url)
    oRequestHandler.addHeaderEntry('User-Agent', UA)
    oRequestHandler.addHeaderEntry('Referer', referer)
    sHtmlContent = oRequestHandler.request()

    sPattern = "atob\('([^']+)"
    aResult = re.findall(sPattern, sHtmlContent)

    if aResult:
        url2 = base64.b64decode(aResult[0])
        return True, url2.strip() + '|User-Agent=' + UA + '&Referer=' + Quote(url)

    # fichier vu mais ne sait plus dans quel cas
    sPattern = "source:\s'(https.+?m3u8)"
    aResult = re.findall(sPattern, sHtmlContent)

    if aResult:
        return True, aResult[0] + '|User-Agent=' + UA + '&Referer=' + Quote(url)

    return False, False


def Hoster_Wigistream(url, referer):
    oRequestHandler = cRequestHandler(url)
    oRequestHandler.addHeaderEntry('User-Agent', UA)
    oRequestHandler.addHeaderEntry('Referer', referer)
    sHtmlContent = oRequestHandler.request()

    sPattern = '(\s*eval\s*\(\s*function(?:.|\s)+?{}\)\))'
    aResult = re.findall(sPattern, sHtmlContent)

    if aResult:
        sstr = aResult[0]
        if not sstr.endswith(';'):
            sstr = sstr + ';'
            sUnpack = cPacker().unpack(sstr)
            sPattern = 'source:"(.+?)"'
            aResult = re.findall(sPattern, sUnpack)
            if aResult:
                return True, aResult[0]  + '|User-Agent=' + UA + '&Referer=' + Quote(url)

    return False, False


def Hoster_Laylow(url, referer):
    oRequestHandler = cRequestHandler(url)
    oRequestHandler.addHeaderEntry('User-Agent', UA)
    oRequestHandler.addHeaderEntry('Referer', referer)
    sHtmlContent = oRequestHandler.request()

    sPattern = "source:\s'(https.+?m3u8)"
    aResult = re.findall(sPattern, sHtmlContent)
    if aResult:
        return True, aResult[0] + '|User-Agent=' + UA + '&Referer=' + Quote(url)

    return False, False


def getRealTokenJson(link, referer):

    realResp = ''
    oRequestHandler = cRequestHandler(link)
    # oRequestHandler.addHeaderEntry('Host', 'telerium.tv')
    oRequestHandler.addHeaderEntry('User-Agent', UA)
    # oRequestHandler.addHeaderEntry('Accept', 'application/json, text/javascript, */*; q=0.01')
    # oRequestHandler.addHeaderEntry('Accept', 'application/json')
    oRequestHandler.addHeaderEntry('Accept-Language', 'pl,en-US;q=0.7,en;q=0.3')
    oRequestHandler.addHeaderEntry('X-Requested-With', 'XMLHttpRequest')
    oRequestHandler.addHeaderEntry('Referer', referer)
    oRequestHandler.addCookieEntry('elVolumen', '100')
    oRequestHandler.addCookieEntry('__ga', '100')

    try:
        realResp = oRequestHandler.request()
    except:
        pass

    if not realResp:#and False:
        oRequestHandler = cRequestHandler(link)
        # oRequestHandler.addHeaderEntry('Host', 'telerium.tv')
        oRequestHandler.addHeaderEntry('User-Agent', UA)
        # oRequestHandler.addHeaderEntry('Accept', 'application/json, text/javascript, */*; q=0.01')
        oRequestHandler.addHeaderEntry('Accept', 'application/json')
        oRequestHandler.addHeaderEntry('Accept-Language', 'pl,en-US;q=0.7,en;q=0.3')
        oRequestHandler.addHeaderEntry('X-Requested-With', 'XMLHttpRequest')
        oRequestHandler.addHeaderEntry('Referer', referer)
        oRequestHandler.addCookieEntry('elVolumen', '100')
        oRequestHandler.addCookieEntry('__ga', '100')
        realResp = oRequestHandler.request()

    return json.loads(realResp)


def getTimer():
    datenow = datetime.utcnow().replace(second = 0, microsecond = 0)
    datenow = datenow + timedelta(days = 1 )
    epoch = datetime(1970, 1, 1)
    return (datenow - epoch).total_seconds() // 1
