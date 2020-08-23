#-*- coding: utf-8 -*-
#Vstream https://github.com/Kodi-vStream/venom-xbmc-addons
# Ovni-crea
from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.comaddon import progress, VSlog, dialog
from resources.lib.util import cUtil, Unquote
import re, base64
#import web_pdb;

from resources.lib.packer import cPacker


SITE_IDENTIFIER = 'newslive'
SITE_NAME = 'News live tv'
SITE_DESC = 'Site pour les news en anglais'

URL_MAIN = 'https://www.newslive.com/'
URL_SEARCH = (URL_MAIN + '/frx/fanclubs/?q=', 'showMovies4')
FUNCTION_SEARCH = 'showMovies4'

NEWS_NEWS = (URL_MAIN , 'showMovies') #Les new en direct
#SPORT_SPORTSCLASS = (URL_MAIN + '/frx/calendar/411/', 'showClass')# Les classements
NETS_GENRES = (True, 'showGenres') #Les clubs de football

def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Rechercher l\'équipe', 'search.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', NEWS_NEWS[0])
    oGui.addDir(SITE_IDENTIFIER, NEWS_NEWS[1], 'Les infos en direct', 'news.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', NETS_GENRES[0])
    oGui.addDir(SITE_IDENTIFIER, NETS_GENRES[1], 'Les clubs de foot (urlresolver requis)', 'genres.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showSearch():
    oGui = cGui()

    sSearchText = oGui.showKeyBoard()
    if (sSearchText != False):
        sUrl = URL_SEARCH[0] + sSearchText
        showMovies4(sUrl) #showMovies4 car c'est pour afficher le club recherché'
        oGui.setEndOfDirectory()
        return


def showGenres(): #affiche les clubs de foot
    oGui = cGui()

    liste = []
    liste.append( ['PSG', URL_MAIN + '/frx/team/1_4_216_psg/fanclub/'] )
    liste.append( ['Marseille (OM)', URL_MAIN + '/frx/team/1_310_383_marseille/fanclub/'] )
    liste.append( ['Barcelone', URL_MAIN + '/frx/team/1_3_227_barcelona/fanclub/'] )
    liste.append( ['Real-Madrid', URL_MAIN + '/frx/team/1_163_317_real_madrid/fanclub/'] )
    liste.append( ['Marchester Utd', URL_MAIN + '/frx/team/1_350_421_manchester_utd/fanclub/'] )
    liste.append( ['Chelsea', URL_MAIN + '/frx/team/1_351_397_chelsea/fanclub/'] )
    liste.append( ['Bayern Munich', URL_MAIN + '/frx/team/1_5_227_bayern/fanclub/'] )
    liste.append( ['Juventus', URL_MAIN + '/frx/team/1_244_365_juventus/fanclub/'] )
    liste.append( ['Arsenal', URL_MAIN + '/frx/team/1_353_406_arsenal/fanclub/'] )
    liste.append( ['Liverpool', URL_MAIN + '/frx/team/1_352_412_liverpool/fanclub/'] )
    liste.append( ['Manchester City', URL_MAIN + '/frx/team/1_363_446_manchester_city/fanclub/'] )
    liste.append( ['France', URL_MAIN + '/frx/team/1_77_258_france/fanclub/'] )
    liste.append( ['Dortmund', URL_MAIN + '/frx/team/1_136_296_dortmund/fanclub/'] )
    liste.append( ['Monaco', URL_MAIN + '/frx/team/1_319_383_monaco/fanclub/'] )
    liste.append( ['Portugal', URL_MAIN + '/frx/team/1_79_269_portugal/fanclub/'] )
    liste.append( ['Argentine', URL_MAIN + '/frx/team/1_62_253_argentina/fanclub/'] )
    liste.append( ['Belgique', URL_MAIN + '/frx/team/1_83_270_belgium/fanclub/'] )

    for sTitle, sUrl in liste:

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sUrl)
        oGui.addDir(SITE_IDENTIFIER, 'showMenu', sTitle, 'genres.png', oOutputParameterHandler)
        #showMenu car c'est pour afficher les infos du club seul resultat est fonctionnel pour l'instant''

    oGui.setEndOfDirectory()

def showMovies(sSearch = ''):#affiche les catégories qui ont des lives'

    oGui = cGui()
    if sSearch:
        sUrl = sSearch
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = '<a\s+href="([^"]+/category/([^"]+))"'

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    VSlog(str(aResult))

    if (aResult[0] == False):
        oGui.addText(SITE_IDENTIFIER)

    if (aResult[0] == True):
        total = len(aResult[1])
        progress_ = progress().VScreate(SITE_NAME)

        for aEntry in aResult[1]:
            progress_.VSupdate(progress_, total)
            if progress_.iscanceled():
                break

            sUrl2 = aEntry[0]
            #sUrl2 = URL_MAIN + sUrl2

            sTitle = aEntry[1]
            sTitle = sTitle.decode("iso-8859-1", 'ignore')
            sTitle = cUtil().unescape(sTitle)
            sTitle = sTitle.encode("utf-8", 'ignore')

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl2', sUrl2)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)

            oGui.addDir(SITE_IDENTIFIER, 'showMovies2', sTitle, 'news.png', oOutputParameterHandler)

        progress_.VSclose(progress_)

    if not sSearch:
        oGui.setEndOfDirectory()

def showMovies2(): #affiche les matchs en direct depuis la section showMovie
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl2 = oInputParameterHandler.getValue('siteUrl2')

    oRequestHandler = cRequestHandler(sUrl2)
    sHtmlContent = oRequestHandler.request()

    #sPattern = '<a class="live" href="([^>]+)">([^>]+)</a>\s*(?:<br><img src=".+?/img/live.gif"><br>|<br>)\s*<span class="evdesc">([^>]+)\s*<br>\s*([^>]+)</span>'
    sPattern = '<a\s+href="([^"]+)"\s+rel="bookmark"\s+title="([A-Za-z0-9 ]+)"'
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

            sTitle2 = aEntry[1].replace('<br>', ' ')
            sUrl3 = aEntry[0]
            sThumb = ''
            #sLang = aEntry[3]
            sQual = ''
            sHoster = ''

            sTitle2 = sTitle2.decode("iso-8859-1", 'ignore')
            sTitle2 = cUtil().unescape(sTitle2)
            sTitle2 = sTitle2.encode("utf-8")

            sHoster = sHoster.decode("iso-8859-1", 'ignore')
            sHoster = cUtil().unescape(sHoster)
            sHoster = sHoster.encode("utf-8")

            sQual = sQual.decode("iso-8859-1", 'ignore')
            sQual = cUtil().unescape(sQual)
            sQual = sQual.encode("utf-8", 'ignore')

            sTitle2 = ('%s (%s) [COLOR yellow]%s[/COLOR]') % (sTitle2, sHoster, sQual)

            sUrl3 = sUrl3
            VSlog(sUrl3)

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl4', sUrl3)
            oOutputParameterHandler.addParameter('sMovieTitle2', sTitle2)
            oOutputParameterHandler.addParameter('sThumb', sThumb)

            oGui.addDir(SITE_IDENTIFIER, 'showHosters', sTitle2, 'news.png', oOutputParameterHandler)

        progress_.VSclose(progress_)

    oGui.setEndOfDirectory()

def showMovies3(): #affiche les videos disponible du live
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl3 = oInputParameterHandler.getValue('siteUrl3')

    oRequestHandler = cRequestHandler(sUrl3)
    sHtmlContent = oRequestHandler.request()
    sMovieTitle2 = oInputParameterHandler.getValue('sMovieTitle2')

    # VSlog("============= contenu =============") 
    #VSlog(sHtmlContent)

    sPattern = '<a title=".+?" *href="(.+?)"'

    sPatternType = 't=([A-Za-z0-9]+)&'
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

            sTitle = sMovieTitle2
            sUrl4 = aEntry
            sThumb = ''
            #sLang = aEntry[3]
            #sQual = aEntry[3]
            sHoster = 'NA'
            #sDesc = ''
            aResult2 = re.findall(sPatternType, sUrl4)
            if aResult2:
                sHoster = aResult2[0]


            sTitle = ('[COLOR green]%s[COLOR] - %s') % (sHoster, sMovieTitle2)
            sUrl4 = "http:" + sUrl4

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl4', sUrl4)
            oOutputParameterHandler.addParameter('sMovieTitle2', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)

            oGui.addDir(SITE_IDENTIFIER, 'showHosters', sTitle, 'sport.png', oOutputParameterHandler)

        progress_.VSclose(progress_)

    oGui.setEndOfDirectory()

def showHosters(): #affiche les videos disponible du live
    oGui = cGui()
    UA = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'
    oInputParameterHandler = cInputParameterHandler()
    sUrl4 = oInputParameterHandler.getValue('siteUrl4')
    sMovieTitle2 = oInputParameterHandler.getValue('sMovieTitle2')
    sThumb = oInputParameterHandler.getValue('sThumb')

    oRequestHandler = cRequestHandler(sUrl4)
    sHtmlContent = oRequestHandler.request()

    oParser = cParser()
    sPattern = 'file: "([^"]+\.m3u8[^"]*)"'
    aResult = oParser.parse(sHtmlContent, sPattern)
    
    # Si vide on cherche youtube
    if (aResult[0] == False):
        sPattern = 'src="([^"]+youtube[^"]+/embed/[^"]+)'
        aResult = oParser.parse(sHtmlContent, sPattern)

    
    VSlog(str(aResult))
    if (aResult[0]):

        sHosterUrl = ''

        Referer =sUrl4
        url = aResult[1][0]

        #url = 'http://www.sporcanli.com/frame2.html' #a garder peut etre utils pour ajouter un hébergeur

        VSlog(url)
        if str(url).startswith('http') == False :
            url = 'http:'+url
            
        if 'cbsn' in Referer:         
	        oRequestHandler = cRequestHandler(url)
	        oRequestHandler.addHeaderEntry('User-Agent', UA)
                oRequestHandler.addHeaderEntry('Referer', Referer)
                sHtmlContent2 = oRequestHandler.request()
	        sElementUrl = sHtmlContent2.split('\n')
	        VSlog('CBS M3U')
	        VSlog(str(sElementUrl))
	        for iElement in sElementUrl :
		        if iElement.startswith('#') == False :
		            url = iElement
		            break
          
        if 'fox' in Referer:         
	        oRequestHandler = cRequestHandler(url)
	        oRequestHandler.addHeaderEntry('User-Agent', UA)
                oRequestHandler.addHeaderEntry('Referer', Referer)
                sHtmlContent2 = oRequestHandler.request()
	        sElementUrl = sHtmlContent2.split('\n')
	        VSlog('fox M3U')
	        VSlog(str(sElementUrl))
	        for iElement in sElementUrl:
		        if iElement.startswith('#') == False:
		            url = url.replace('index.m3u8', iElement)
		            break

        if 'm3u8' in url:
            sHosterUrl = url + '|User-Agent=' + UA + '&referer=' + Referer
             
        if 'emb.apl' in url:#Terminé - Supporte emb.aplayer et emb.apl3
            Referer = url
            oRequestHandler = cRequestHandler(url)
            oRequestHandler.addHeaderEntry('User-Agent', UA)
            sHtmlContent2 = oRequestHandler.request()
            sPattern2 = 'source: *\'(.+?)\''
            aResult = re.findall(sPattern2, sHtmlContent2)
            if aResult:
                sHosterUrl = aResult[0] + '|User-Agent=' + UA + '&referer=' + Referer
            else:
                sPattern2 = "pl.\init\('([^']+)'\);"
                aResult = re.findall(sPattern2, sHtmlContent2)
                if aResult:
                    sHosterUrl = aResult[0] + '|User-Agent=' + UA + '&referer=' + Referer
    
        if 'youtube' in url:#Je sais pas
            #dialog().VSinfo('Youtube peut ne pas marcher c\'est de la faute de Kodi', "Livetv", 15)
            sPattern2 = 'youtube.com/embed/(.+)'
            aResult = re.findall(sPattern2, url)

            if aResult:
                video_id = aResult[0]
                VSlog(video_id)

                #url1 = url.replace('/embed/', '/watch?v=').replace('?autoplay=1', '')

                url2 = 'https://youtube.com/get_video_info?video_id=' + video_id + '&sts=17488&hl=fr'

                oRequestHandler = cRequestHandler(url2)
                oRequestHandler.addHeaderEntry('User-Agent', UA)
                sHtmlContent3 = Unquote(oRequestHandler.request())

                sPattern3 = 'hlsManifestUrl":"(.+?)"'
                aResult = re.findall(sPattern3, sHtmlContent3)

                if aResult:
                    sHosterUrl = aResult[0] + '|User-Agent=' + UA + '&Host=manifest.googlevideo.com'

        if 'box-live.stream' in url: #Terminé
            oRequestHandler = cRequestHandler(url)
            oRequestHandler.addHeaderEntry('User-Agent', UA)
            oRequestHandler.addHeaderEntry('Referer', sUrl4)

            sHtmlContent2 = oRequestHandler.request()
            sPattern2 = 'source: \'(.+?)\''
            aResult = re.findall(sPattern2, sHtmlContent2)
            if aResult:
                sHosterUrl = aResult[0] + '|User-Agent=' + UA + '&referer=' + url
            else:
                sPattern2 = 'var source = \"(.+?)\"'
                aResult = re.findall(sPattern2, sHtmlContent2)
                if aResult:
                    sHosterUrl = aResult[0]
                else:
                    sPattern2 = '<iframe.+?src="(http.+?)".+?</iframe>'
                    aResult = re.findall(sPattern2, sHtmlContent2)
                    if aResult:
                        Referer = url
                        url = aResult[0]    # decryptage plus bas (telerium)
            
        if 'telerium.tv' in url: #WIP
            oRequestHandler = cRequestHandler(url)
            if(Referer):
                oRequestHandler.addHeaderEntry('User-Agent', UA)
                oRequestHandler.addHeaderEntry('Referer', Referer)
            sHtmlContent2 = oRequestHandler.request()
            sPattern2 = '(\s*eval\s*\(\s*function(?:.|\s)+?{}\)\))'
            aResult = re.findall(sPattern2, sHtmlContent2)

            if aResult:
                str2 = aResult[0]
                if not str2.endswith(';'):
                    str2 = str2 + ';'

                strs = cPacker().unpack(str2)
#                 print strs
#                fh = open('f:\\test.txt', "w")
#                fh.write(strs)
#                fh.close()

                sPattern3 = '{url:window\.atob\((.+?)\)\.slice.+?\+window\.atob\((.+?)\)'
                aResult1 = re.findall(sPattern3, strs)
                if aResult1:
                    m3u=aResult1[0][0]
                    sPatternM3u = m3u+'="(.+?)"'
                    m3u = re.findall(sPatternM3u, strs)
                    m3u = base64.b64decode(m3u[0])[14:]
                    
                    token=aResult1[0][1]
                    sPatterntoken = token+'="(.+?)"'
                    token = re.findall(sPatterntoken, strs)
                    token = base64.b64decode(token[0])

                    sHosterUrl = 'https://telerium.tv/'+m3u+token + '|referer='+url
                
        VSlog('HOTE ='+ sHosterUrl)
        if sHosterUrl:
            oHoster = cHosterGui().checkHoster("m3u8")
            if (oHoster != False):
                    oHoster.setDisplayName(sMovieTitle2) #nom affiche
                    oHoster.setFileName(sMovieTitle2) #idem
                    cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumb)

        oGui.setEndOfDirectory()

def showMovies4(sSearch = ''):#Afficher le club recherché
    oGui = cGui()
    if sSearch:
        sUrl = sSearch
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = '<a href="([^"]+)"><span class="sltitle">([^<>]+)</span></a>\s*<br>\s*<font color=".+?">([^<>]+)</font>'

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    #VSlog(str(aResult))

    if (aResult[0] == False):
        oGui.addText(SITE_IDENTIFIER)

    if (aResult[0] == True):
        total = len(aResult[1])
        progress_ = progress().VScreate(SITE_NAME)

        for aEntry in aResult[1]:
            progress_.VSupdate(progress_, total)
            if progress_.iscanceled():
                break

            sTitle = aEntry[1]
            sUrl2 = aEntry[0]
            sThumb = ''
            #sLang = aEntry[3]
            #sQual = aEntry[4]
            sHoster = aEntry[2]
            sDesc = ''

            sTitle = sTitle.decode("iso-8859-1", 'ignore')
            sTitle = sTitle.encode("utf-8", 'ignore')
            sTitle = ('%s (%s)') % (sTitle, sHoster)

            sUrl2 = URL_MAIN + sUrl2

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl2)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)

            if '/series' in sUrl:
                oGui.addTV(SITE_IDENTIFIER, 'ShowSerieSaisonEpisodes', sTitle, '', sThumb, sDesc, oOutputParameterHandler)
            else:
                oGui.addMovie(SITE_IDENTIFIER, 'showMenu', sTitle, '', sThumb, sDesc, oOutputParameterHandler)

        progress_.VSclose(progress_)

    if not sSearch:
        oGui.setEndOfDirectory()

def showMenu(sSearch = ''):#affiche le menu du club
    oGui = cGui()
    if sSearch:
        sUrl = sSearch
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = '<a href="([^"]+)" *class="white">(.+?)</a></td>'

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    #VSlog(str(aResult))

    if (aResult[0] == False):
        oGui.addText(SITE_IDENTIFIER)

    if (aResult[0] == True):
        total = len(aResult[1])
        progress_ = progress().VScreate(SITE_NAME)

        for aEntry in aResult[1]:
            progress_.VSupdate(progress_, total)
            if progress_.iscanceled():
                break

            sTitle = aEntry[1]
            sUrl2 = aEntry[0]
            sThumb = ''
            #sLang = aEntry[3]
            #sQual = aEntry[4]
            #sHoster = aEntry[2]
            sDesc = ''

            sTitle = sTitle.decode("iso-8859-1", 'ignore')
            sTitle = sTitle.encode("utf-8", 'ignore')
            sTitle = ('%s') % (sTitle)

            sUrl2 = URL_MAIN + sUrl2

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl2)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)

            if '/series' in sUrl:
                oGui.addTV(SITE_IDENTIFIER, 'ShowSerieSaisonEpisodes', sTitle, '', sThumb, sDesc, oOutputParameterHandler)
            else:
                oGui.addMovie(SITE_IDENTIFIER, 'showResult', sTitle, '', sThumb, sDesc, oOutputParameterHandler)

        progress_.VSclose(progress_)

    if not sSearch:
        oGui.setEndOfDirectory()

def showResult(sSearch = ''):# le menu resultat quand on a choisi le club
    oGui = cGui()
    if sSearch:
        sUrl = sSearch
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = '<span class="date">([^<>]+)</span>.+?<span class="graydesc">([^<>]+)</span>.+?<td align="right">([^<>]+).+?<td align="center">\s*<b>([^<>]+)</b>.+?<td>([^<>]+)</td>.+?<font color=".+?">.+?</font>.+?<a class="small" *href="([^"]+)"'

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    #VSlog(str(aResult))

    if (aResult[0] == False):
        oGui.addText(SITE_IDENTIFIER)

    if (aResult[0] == True):
        total = len(aResult[1])
        progress_ = progress().VScreate(SITE_NAME)

        for aEntry in aResult[1]:
            progress_.VSupdate(progress_, total)
            if progress_.iscanceled():
                break

            sTitle = aEntry[2] + aEntry[4]
            sUrl2 = aEntry[5]
            sDate = aEntry[0]
            sComp = aEntry[1]
            sEquip = aEntry[2]
            sScore = aEntry[3]
            sEquipe = aEntry[4]
            sThumb = ''
            #sLang = aEntry[3]
            #sQual = aEntry[4]
            #sHoster = aEntry[2]
            sDesc = ''

            sTitle = sTitle.decode("iso-8859-1", 'ignore')
            sTitle = cUtil().unescape(sTitle)
            sTitle = sTitle.encode("utf-8", 'ignore')

            sDate = sDate.decode("iso-8859-1", 'ignore')
            sDate = cUtil().unescape(sDate)
            sDate = sDate.encode("utf-8", 'ignore')

            sScore = sScore.decode("iso-8859-1", 'ignore')
            sScore = cUtil().unescape(sScore)
            sScore = sScore.encode("utf-8", 'ignore')

            sComp = sComp.decode("iso-8859-1", 'ignore')
            sComp = cUtil().unescape(sComp)
            sComp = sComp.encode("utf-8", 'ignore')
            sTitle = ('%s  [%s] (%s) [COLOR]%s[/COLOR]]') % (sTitle, sScore, sDate, sComp)
            sUrl2 = URL_MAIN + sUrl2

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl2)
            oOutputParameterHandler.addParameter('sMovieTitlebis', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)

            if '/series' in sUrl:
                oGui.addTV(SITE_IDENTIFIER, 'ShowSerieSaisonEpisodes', sTitle, '', sThumb, sDesc, oOutputParameterHandler)
            else:
                oGui.addMovie(SITE_IDENTIFIER, 'showHosters2', sTitle, '', sThumb, sDesc, oOutputParameterHandler)

        progress_.VSclose(progress_)

    if not sSearch:
        oGui.setEndOfDirectory()

#def showDecode(): #les hosters des lives celui que je suis bloqué
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle2 = oInputParameterHandler.getValue('sMovieTitle2')
    sThumb = oInputParameterHandler.getValue('sThumb')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    oParser = cParser()
    sPattern = '.+?(http://.+?).+?'
    #urllib.unquote(sPattern)

    aResult = oParser.parse(sHtmlContent, sPattern)
    #VSlog(str(aResult))

    if (aResult[0] == True):
        for aEntry in aResult[1]:

            sHosterUrl = str(aEntry)
            sHosterUrl = sHosterUrl.decode("iso-8859-1", 'ignore')
            #sHosterUrl = cUtil().unescape(sHosterUrl)
            sHosterUrl = sHosterUrl.encode("utf-8", 'ignore')
            oHoster = cHosterGui().checkHoster(sHosterUrl)
            if (oHoster != False):
                oHoster.setDisplayName(sMovieTitle2)
                oHoster.setFileName(sMovieTitle2)
                cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumb)

    oGui.setEndOfDirectory()

def showHosters2(): #Les hosters des videos (pas des lives attentions)
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitlebis = oInputParameterHandler.getValue('sMovieTitlebis')
    sThumb = oInputParameterHandler.getValue('sThumb')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    oParser = cParser()
    sPattern = '<iframe.+?src="(http.+?)".+?</iframe>'

    aResult = oParser.parse(sHtmlContent, sPattern)
    #VSlog(str(aResult))

    if (aResult[0] == True):
        for aEntry in aResult[1]:

            sHosterUrl = aEntry
            #sHosterUrl = sHosterUrl.decode("iso-8859-1", 'ignore')
            #sHosterUrl = cUtil().unescape(sHosterUrl)
            #sHosterUrl = sHosterUrl.encode("utf-8", 'ignore')
            oHoster = cHosterGui().checkHoster(sHosterUrl)
            if (oHoster != False):
                oHoster.setDisplayName(sMovieTitlebis)
                oHoster.setFileName(sMovieTitlebis)
                cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumb)

    oGui.setEndOfDirectory()
