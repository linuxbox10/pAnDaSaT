from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.Button import Button
from Components.config import config, getConfigListEntry, ConfigText, ConfigInteger, ConfigSelection, ConfigSubsection, ConfigYesNo
from Components.config import configfile, ConfigNothing, NoSave, ConfigElement, ConfigPassword
from Components.config import KEY_LEFT, KEY_RIGHT, KEY_HOME, KEY_END, KEY_0, KEY_DELETE, KEY_BACKSPACE, KEY_OK, KEY_TOGGLEOW, KEY_ASCII, KEY_TIMEOUT, KEY_NUMBERS
from Components.ConfigList import ConfigListScreen
from Components.Converter.StringList import StringList
from Components.FileList import FileList
from Components.Input import Input
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Pixmap import Pixmap, MultiPixmap, MovingPixmap
from Components.ScrollLabel import ScrollLabel
from Components.SelectionList import SelectionList, SelectionEntryComponent
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.ServiceList import ServiceList
from Components.Sources.List import List
from Components.Sources.Source import Source
from Components.Sources.StaticText import StaticText
from Components.Sources.Progress import Progress
from Tools.Downloader import downloadWithProgress
from ServiceReference import ServiceReference
from enigma import *
# from enigma import eConsoleAppContainer, eListboxPythonMultiContent, eDVBDB, eListbox, ePicLoad, eServiceCenter, eServiceReference
# from enigma import eTimer
from os import environ as os_environ
from os import path, listdir, remove, mkdir, chmod, sys, rename, system
from Plugins.Plugin import PluginDescriptor
from Components.PluginComponent import plugins
import Components.PluginComponent
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.InfoBar import MoviePlayer, InfoBar
from Screens.InfoBarGenerics import *
# from Screens.InfoBarGenerics import InfoBarNotifications, InfoBarServiceNotifications, InfoBarTimeshiftState, InfoBarTimeshift, InfoBarNumberZap
# from Screens.InfoBarGenerics import InfoBarShowHide, NumberZap, InfoBarSeek, InfoBarAudioSelection, InfoBarSubtitleSupport, InfoBarEPG 
from Screens.InputBox import InputBox
from Screens.PluginBrowser import PluginBrowser
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop, Standby
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.Directories import resolveFilename, fileExists, copyfile, pathExists
from Tools.Directories import SCOPE_PLUGINS
from Tools.LoadPixmap import LoadPixmap
from twisted.web.client import downloadPage, getPage, error
from xml.dom import Node, minidom
import base64
import os, re, glob
import shutil
import time
from Components.Console import Console as iConsole
from urllib import urlencode, quote
from urllib2 import urlopen, Request, URLError, HTTPError 
from urlparse import urlparse
import StringIO
import httplib
import urllib
import urllib2
# from httplib import HTTP
# import http.client as httplib
# from enigma import eEnv
import cookielib
import gettext
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
PluginLanguageDomain = 'ListFree'
PluginLanguagePath = '/usr/lib/enigma2/python/Plugins/Extensions/fReE_iPtV_pAnDa_SaT_tEaM/res/locale'
#

def localeInit():
    lang = language.getLanguage()[:2]
    os.environ['LANGUAGE'] = lang
    gettext.bindtextdomain(PluginLanguageDomain, PluginLanguagePath)
    gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE, ''))

def _(txt):
    t = gettext.dgettext(PluginLanguageDomain, txt)
    if t == txt:
        t = gettext.dgettext('enigma2', txt)
    return t

localeInit()
language.addCallback(localeInit)

currversion = '5.4'
Version = ' 5.4 - 15.02.2018'

# currversion = ''
# date= '16.01.2018'
# if os.path.exists('/var/lib/opkg/info/enigma2-plugin-extensions-panda-freeiptv.control'):
    # with open('/var/lib/opkg/info/enigma2-plugin-extensions-panda-freeiptv.control') as origin:
        # for vers in origin:
            # if 'Version: ' not in vers:
                # continue
            # try:
                # currversion = vers.split(':')[1]
            # except IndexError:
                # print
# Version = ' '+ currversion + ' - ' + date




                
def checkInternet():
    try:
        response = urllib2.urlopen("http://google.com", None, 5)
        response.close()
    except urllib2.HTTPError:
        return False
    except urllib2.URLError:
        return False
    except socket.timeout:
        return False
    else:
        return True

def mountpcn():
    pthmpcns = []    
#    pthm3uf = []
    if os.path.isfile('/proc/mounts'):
        for line in open('/proc/mounts'):
            if '/dev/sd' in line or '/dev/disk/by-uuid/' in line or '/dev/mmc' in line or '/dev/mtdblock' in line:
                drive = line.split()[1].replace('\\040', ' ') + '/'
                if not drive in pthmpcns:  
                    pthmpcns.append(drive)
    pthmpcns.append('/usr/share/enigma2/')
    pthmpcns.append('/') 
    return pthmpcns
        
def mountm3uf():
#    pthmpcns = []
    pthm3uf = []

    if os.path.isfile('/proc/mounts'):
        for line in open('/proc/mounts'):
            if '/dev/sd' in line or '/dev/disk/by-uuid/' in line or '/dev/mmc' in line or '/dev/mtdblock' in line:
                drive = line.split()[1].replace('\\040', ' ') + '/'
                if drive== "/media/hdd/" :
                    # drive = drive.replace('/media/hdd/', '/media/hdd/movie/')
                    if not os.path.exists('/media/hdd/movie'):
                        system('mkdir /media/hdd/movie')
                    
                if drive== "/media/usb/" :
                    # drive = drive.replace('/media/usb/', '/media/usb/movie/')
                    if not os.path.exists('/media/usb/movie'):
                        system('mkdir /media/usb/movie')  

                if drive== "/omb/" :
                    drive = drive.replace('/omb/', '/omb/')
                if drive== "/ba/" :
                    drive = drive.replace('/ba/', '/ba/')                    

                        
                ##                    
                if not drive in pthm3uf: 
                      pthm3uf.append(drive)
    pthm3uf.append('/tmp/')
                
    return pthm3uf   

def isExtEplayer3Available():
    return os.path.isfile(eEnv.resolve('$bindir/exteplayer3'))   
    
sessions = []
config.plugins.fReE_iPtV_pAnDa_SaT_tEaM = ConfigSubsection()
config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.server = ConfigSelection(default='PANDASAT', choices=['PANDASAT', 'CORVONE'])
config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.code = ConfigInteger(limits=(0, 9999), default=1234)
config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.autoupd = ConfigYesNo(default=True)
config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.bouquettop = ConfigSelection(default='Bottom', choices=['Bottom', 'Top'])
config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthm3uf = ConfigSelection(choices=mountm3uf())
config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthpcns = ConfigSelection(default='/usr/share/enigma2/',choices=mountpcn())
# config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthm3uf = ConfigSelection(choices=mountm3uf())
# config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthpcns = ConfigSelection(choices=mountpcn())
config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthchs = ConfigSelection(default='/etc/pandasat/extra', choices=[('/etc/pandasat/extra', 'DEFAULT'), ('/usr/script', '/USR/SCRIPT')])
if os.path.exists ('/usr/lib/enigma2/python/Plugins/SystemPlugins/ServiceApp') and isExtEplayer3Available :
    config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.services = ConfigSelection(default='Gstreamer', choices=['Gstreamer', 'Exteplayer3'])
else:
    config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.services = ConfigSelection(default='Gstreamer', choices=[('Gstreamer')])
config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.strtext = ConfigYesNo(default=True)
config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.strtmain = ConfigYesNo(default=True)




        
   

#####4.9 change server
# global TXT_PUKPRG, upd_fr_txt, nt_upd_lnk, picon_ipk_usb, picon_ipk_hdd, picon_ipk_flash, pnd_m3u, pnd_m3ulnk #, server, host 


def server_ref():
    global server, host, TXT_PUKPRG, upd_fr_txt, nt_upd_lnk, picon_ipk_usb, picon_ipk_hdd, picon_ipk_flash, pnd_m3u, pnd_m3ulnk 
    server = ''
    host = ''
    
    TEST1 = 'aHR0cDovL3d3dy5wYW5kYXNhdC5pbmZv' #SERVER1- PANDA
    ServerS1 = base64.b64decode(TEST1)
    data_s1 = 'L2lwdHYv'
    FTP_1 = base64.b64decode(data_s1)

    TEST2 = 'aHR0cDovL3d3dy5jb3J2b25lLmNvbQ==' #server2 - CORVONE
    ServerS2 = base64.b64decode(TEST2)
    data_s2 = 'L2NvcnZvbmUuY29tL3BsdWdpbi9pcHR2Lw=='
    FTP_2 = base64.b64decode(data_s2)

    if config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.server.value == 'PANDASAT' :
        host = ServerS1
        print host
        server = ServerS1 + FTP_1
        print server
        
        
    else:
        host = ServerS2
        print host
        server = ServerS2 + FTP_2
        print server
        
        
    TXT_PUKPRG = ('%splugin/pinprogress.txt' % server)
    upd_fr_txt = ('%splugin/updatePandafree.txt' % server) 
    nt_upd_lnk = ('wget %snote.txt -O /tmp/note.txt > /dev/null' % server) #note.txt
    picon_ipk_usb = ('%splugin/picons-pandasat-freeiptv-usb_v.1.0_all.ipk' % server)
    picon_ipk_hdd = ('%splugin/picons-pandasat-freeiptv-hdd_v.1.0_all.ipk' % server)
    picon_ipk_flash = ('%splugin/picons-pandasat-freeiptv-flash_v.1.0_all.ipk' % server) 
    pnd_m3u = ('%spAnDaSAT_Free_IPTV.m3u' % server)
    pnd_m3ulnk = ('wget %spAnDaSAT_Free_IPTV.m3u -O ' % server)    
        
        
    return server,host, TXT_PUKPRG, upd_fr_txt, nt_upd_lnk, picon_ipk_usb, picon_ipk_hdd, picon_ipk_flash, pnd_m3u, pnd_m3ulnk
    
server_ref()

# TEST1 = 'aHR0cDovL3d3dy5wYW5kYXNhdC5pbmZv' #SERVER1- PANDA
# ServerS1 = base64.b64decode(TEST1)
# data_s1 = 'L2lwdHYv'
# FTP_1 = base64.b64decode(data_s1)

# TEST2 = 'aHR0cDovL3d3dy5jb3J2b25lLmNvbQ==' #server2 - CORVONE
# ServerS2 = base64.b64decode(TEST2)
# data_s2 = 'L2NvcnZvbmUuY29tL3BsdWdpbi9pcHR2Lw=='
# FTP_2 = base64.b64decode(data_s2)

# if config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.server.value == 'PANDASAT' :
    # host = ServerS1
    # print host
    # server = ServerS1 + FTP_1
    # print server
# else:
    # host = ServerS2
    # print host
    # server = ServerS2 + FTP_2
    # print server
        
# TXT_PUKPRG = ('%splugin/pinprogress.txt' % server)
# upd_fr_txt = ('%splugin/updatePandafree.txt' % server) 
# nt_upd_lnk = ('wget %snote.txt -O /tmp/note.txt > /dev/null' % server) #note.txt
# picon_ipk_usb = ('%splugin/picons-pandasat-freeiptv-usb_v.1.0_all.ipk' % server)
# picon_ipk_hdd = ('%splugin/picons-pandasat-freeiptv-hdd_v.1.0_all.ipk' % server)
# picon_ipk_flash = ('%splugin/picons-pandasat-freeiptv-flash_v.1.0_all.ipk' % server)
# pnd_m3u = ('%spAnDaSAT_Free_IPTV.m3u' % server)
# pnd_m3ulnk = ('wget %spAnDaSAT_Free_IPTV.m3u -O ' % server)

plugin_path = '/usr/lib/enigma2/python/Plugins/Extensions/fReE_iPtV_pAnDa_SaT_tEaM/'
service_types_tv = '1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 22) || (type == 25) || (type == 134) || (type == 195)'
dir_enigma2 = '/etc/enigma2/'
addFont('/usr/lib/enigma2/python/Plugins/Extensions/fReE_iPtV_pAnDa_SaT_tEaM/res/fonts/JAi.ttf', 'pndFont1', 100, 1)
addFont('/usr/lib/enigma2/python/Plugins/Extensions/fReE_iPtV_pAnDa_SaT_tEaM/res/fonts/DopeJam.ttf', 'pndFont2', 100, 1)

#brand
BRAND = '/usr/lib/enigma2/python/boxbranding.so'
BRANDP = '/usr/lib/enigma2/python/Plugins/PLi/__init__.pyo'
BRANDPLI ='/usr/lib/enigma2/python/Tools/StbHardware.pyo'


# SCREEN PATH SETTING
DESKHEIGHT = getDesktop(0).size().height()
SKIN_PATH = plugin_path
HD = getDesktop(0).size()

if HD.width() > 1280:
   SKIN_PATH = plugin_path + 'res/FullHD'
else:
   SKIN_PATH = plugin_path + 'res/HD'

#
def ReloadBouquet():
    eDVBDB.getInstance().reloadServicelist()
    eDVBDB.getInstance().reloadBouquets() 

def OnclearMem():
        system("sync")
        system("echo 3 > /proc/sys/vm/drop_caches")

def m3ulistEntry(download):
    res = [download]
    white = 16777215
    yellow = 15053379
    col = 16777215
    backcol = 0
    res.append(MultiContentEntryText(pos=(0, 0), size=(1000, 40), text=download, color=col, color_sel=white, backcolor=backcol, backcolor_sel=yellow))
    return res

def m3ulist(data, list):
    icount = 0
    mlist = []
    for line in data:
        name = data[icount]
        mlist.append(m3ulistEntry(name))
        icount = icount + 1

    list.setList(mlist)

    
class PNDM3UList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, True, eListboxPythonMultiContent)
        if DESKHEIGHT > 1000:
            self.l.setItemHeight(40)
            textfont = int(32)
            self.l.setFont(0, gFont('pndFont1', textfont))
        else:
            self.l.setItemHeight(30)
            textfont = int(22)
            self.l.setFont(0, gFont('pndFont1', textfont))
   
def remove_line(filename, what):
    if os.path.isfile(filename):
        file_read = open(filename).readlines()
        file_write = open(filename, 'w')
        for line in file_read:
            if what not in line:
                file_write.write(line)
        file_write.close()

class ABOUT(Screen):

    def __init__(self, session):
        self.session = session
        skin = SKIN_PATH + '/ABOUT.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()          
        Screen.__init__(self, session)
        self['fittitle'] = Label(_('..:: pAnDaSAT aBoUt ::..'))
        self['fitred'] = Label(_('Esci'))
        self['fitgreen'] = Label(_('Config'))
        self['fityellow'] = Label(_('Bouquet'))
        self['fityellow2'] = Label(_('Player'))
        self['fitblue'] = Label(_('Extra'))
        self['Maintainer'] = Label(_('Maintainer') + ': ')
        self['Maintainer2'] = Label(_('@Lululla'))
        self['Grafic'] = Label(_('Grafica') + ': ')
        self['Grafic2'] = Label(_('@pAnDa'))
        self['pndteam'] = Label('by tEaM dEvElOpEr pAnDa SaT\xae')
        self['version'] = Label(_('Versione %s') % Version)
        self['status'] = Label()
        self['progress'] = Progress()
        self['progresstext'] = StaticText()
        info2 = ''
        self['text'] = ScrollLabel()
        self.downloading = False

        self['actions'] = ActionMap(['OkCancelActions',
         'DirectionActions',
         'ColorActions',
         'WizardActions',
         'NumberActions',
         'EPGSelectActions'], {'ok': self.closes,
         'cancel': self.closes,
         'back': self.closes,
         'red': self.closes,
         'up': self['text'].pageUp,
         'down': self['text'].pageDown,
         'left': self['text'].pageUp,
         'right': self['text'].pageDown,
         'yellow': self.lista,
         'blue': self.extra,
         'green': self.scsetup}, -1)
        
        self.checkCfg()
        self.onLayoutFinish.append(self.checkextra)            
        # self.onLayoutFinish.append(self.checkCfg)
        
        # self.onLayoutFinish.append(self.remove)        
####       
    # def Remove(self):
        # for x in glob.glob('/usr/lib/enigma2/python/Plugins/Extensions/fReE_iPtV_pAnDa_SaT_tEaM/*'):
            # jpy = x[-3:]
            # if jpy == '.py':
                # system('rm -fr ' + x)


###extra                
    def checkextra(self):
        self.icount = 0
        self.timer1 = eTimer()
        _lstpnd = '/etc/pandasat/extra/TempClean'
        if not os.path.isfile(_lstpnd):
            try:
                self.timer1.callback.append(self.checkList)
            except:
                self.timer1_conn = self.timer1.timeout.connect(self.checkList)
            self.timer1.start(200, 1)                 
                
    def checkList(self):
        self.session.openWithCallback(self.update2, pndMessageBox, _('Nessuno script in Elenco!') + ' ' + _('Scaricare Script') + ' by pAnDa SAT ?', pndMessageBox.TYPE_YESNO)        

    def update2(self, answer):
        if answer is True:
            self.session.open(Updater)
            # self.close()
        else:
            return
####extra end            
            
                
    def checkCfg(self):
        server_ref()
        
        self.icount = 0
        self['text'].setText(_('Check Connection wait please...'))
        self.timer = eTimer()
        try:
            self.timer.callback.append(self.pndchckint)
        except:
            self.timer_conn = self.timer.timeout.connect(self.pndchckint)
        self.timer.start(100, 1)        
            
    def pndchckint(self):
        url3 = upd_fr_txt
        print 'url3:', url3
        #url3 = 'http://www.pandasat.info'
        getPage(url3).addCallback(self.ConnOK).addErrback(self.ConnNOK)
        
    def ConnOK(self, data):
        try:
            self.pnd = data
            filex = '/tmp/note.txt'
            if os.path.exists(filex):
                os.remove(filex)
            cmd15 = nt_upd_lnk
#            print 'note.txt:', cmd15
            system(cmd15)
            filex2 = open(filex, 'r')
            count2 = 0
            self.notetxt = ''
            while 1:
                srg = filex2.readline()
                count2 += 1
                self.notetxt += str(srg)
                if not srg:
                    break
            self['text'].setText(self.notetxt)
        except:
            self['text'].setText(_('Errore nel download degli aggiornamenti') + ' !')
            
    def ConnNOK(self, error):
        self['text'].setText(_('Server Off') + ' !' + '\ncontrolla SERVER in config')  
        
    def extra(self):
        self.session.open(EXTRA)

    def lista(self):
        self.session.open(OpenScript)

    def scsetup(self):
        # self.session.openWithCallback(self.close, cfgplgConfig)    
        
        self.session.open(cfgplgConfig)
        self.onShown.append(self.checkCfg)
        
    def closes(self):
        filex = '/tmp/note.txt'
        if os.path.exists(filex):
            os.remove(filex)
            OnclearMem()
            self.close()
        else:
            OnclearMem()
            self.close()

        
class OpenScript(Screen):
    def __init__(self, session):
        self.session = session
        
        if fileExists(BRAND) or fileExists(BRANDP):
            skin = SKIN_PATH + '/OpenScriptOpen.xml'
        else:
            skin = SKIN_PATH + '/OpenScript.xml'
        
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()         
        Screen.__init__(self, session)
        self.list = []
        self['list'] = MenuList([])
        self.icount = 0
        self.timer = eTimer()
        # try:
            # self.timer.callback.append(self.pndchckint)
        # except:
            # self.timer_conn = self.timer.timeout.connect(self.pndchckint)
        # self.timer.start(150, 1)
        
        server_ref()        #ok
        
        global pin       
        pin = 1306

        # self.readpin() ##########read pin online b64 ????????????????????
        
        # try:
            # self.timer.callback.append(self.readpin)
        # except:
            # self.timer_conn = self.timer.timeout.connect(self.readpin)
        # self.timer.start(250, 1)

        
        VerifyHost = self.Ver_URL(host)
        if VerifyHost == False :
            self.list = []     
            self.list.append(_("========================="))
            self.list.append(_("==CONTROLLA CONNESSIONE=="))
            self.list.append(_("========================="))
            self.list.append(_("======CHECK  SERVER======"))
            self.list.append(_("=== SUPPORT ON FORUM  ==="))
            self.list.append(_("======PANDASAT.INFO======"))
            self.list.append(_("====== CORVONE.COM ======"))
            self.list.append(_("========================="))
            self['list'] = MenuList(self.list)            
        else:
            if int(pin) == config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.code.value :        
                self.list = []
                self.list.append(_("pAnDaSAT_FREE_ALL"))
                self.list.append(_("pAnDaSAT_ITALIA"))
                self.list.append(_("pAnDaSAT_INTERNATIONAL"))                
                self.list.append(_("pAnDaSAT_MEDIAPLAY"))                
                self.list.append(_("pAnDaSAT_SPORT"))
                self.list.append(_("pAnDaSAT_MUSICA"))
                self.list.append(_("pAnDaSAT_RADIO"))
                self.list.append(_("pAnDaSAT_ADULTXXX"))
                self['list'] = MenuList(self.list)
            else:
                self.list = []     
                self.list.append(_("pAnDaSAT_FREE_ALL"))
                self.list.append(_("pAnDaSAT_ITALIA"))
                self.list.append(_("pAnDaSAT_INTERNATIONAL"))                  
                self.list.append(_("pAnDaSAT_MEDIAPLAY"))                   
                self.list.append(_("pAnDaSAT_SPORT"))
                self.list.append(_("pAnDaSAT_MUSICA"))
                self.list.append(_("pAnDaSAT_RADIO"))
                self['list'] = MenuList(self.list)

                
        #self['pndinfo'] = Label()
        self['version'] = Label(_('Versione %s') % Version)
        self['fittitle'] = Label(_('..:: pAnDaSAT fReE IPTV lIsT ::..'))
        self['pndteam'] = Label('by tEaM dEvElOpEr pAnDa SaT\xae')
        self['Maintainer'] = Label(_('Maintainer') + ': ')
        self['Maintainer2'] = Label(_('@Lululla'))
        self['Grafic'] = Label(_('Grafica') + ': ')
        self['Grafic2'] = Label(_('@pAnDa'))         
        self['fitred'] = Label(_('Esci'))
        #self['fitred2'] = Label(_(''))
        self['fitgreen'] = Label(_('Ricarica'))
        self['fitgreen2'] = Label(_('Bouquet'))        
        self['fityellow'] = Label(_('Elimina'))
        self['fityellow2'] = Label(_('Le liste canali'))
        self['fitblue'] = Label(_('Player'))
        self['fitblue2'] = Label(_('List'))
        self['fitgrey'] = Label(_('Info'))
        # self['chckon'] = Label(_('ATTIVO'))
        # self['chckoff'] = Label(_('DISATTIVO'))
        # self['pndon'] = MultiPixmap()
        # self['pndon'].setPixmapNum(0)
        # self['chckon'].hide()
        # self['chckoff'].hide()
        self['actions'] = ActionMap(['OkCancelActions',
         'DirectionActions',
         'ColorActions',
         'WizardActions',
         'NumberActions',
         'EPGSelectActions'], {'ok': self.messagerun,
         'red': self.close,
         'green': self.messagereload,
         'info': self.close,
         'yellow': self.messagedellist,
         'blue': self.M3uPlay,
         'back': self.close,
         'cancel': self.close}, -1)


    def readpin(self):
        try:
            getPage(TXT_PUKPRG).addCallback(self.gotUpdateInfo).addErrback(self.gotError)

        except Exception as error:
            print str(error)

    def gotUpdateInfo(self, html):
        tmp_infolines = html.splitlines()
        puk = tmp_infolines[0]
        pin = base64.b64decode(puk)
        
    def gotError(self, error = ''):
        pass
    
         
    def Ver_URL(self, url):
        req = urllib2.Request(url)
        try:
            response = urllib2.urlopen(req)
            the_page = response.read()
            print the_page 
            verifica = True
            
        except urllib2.HTTPError as e:
            print e.code
            the_page = '%s' % e.code
            verifica = False
            
        except urllib2.URLError as e:
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
            the_page = '%s' % e.reason
            verifica = False
        return verifica

        
    def run(self, result):
            if result:
                returnValue = self["list"].l.getCurrentSelection()#[1]
                if returnValue is not None:
                        if returnValue is "pAnDaSAT_FREE_ALL":
                                name = 'pAnDaSAT_FREE_ALL'
                                self.instal_listTv(name)
                        elif returnValue is "pAnDaSAT_ITALIA":
                                name = 'pAnDaSAT_ITALIA'
                                self.instal_listTv(name)
                        elif returnValue is "pAnDaSAT_INTERNATIONAL":
                                name = 'pAnDaSAT_internat'
                                self.instal_listTv(name)                                   
                        elif returnValue is "pAnDaSAT_MEDIAPLAY":
                                name = 'pAnDaSAT_mediaplay'
                                self.instal_listTv(name)                                
                        elif returnValue is "pAnDaSAT_SPORT":
                                name = 'pAnDaSAT_SPORT'                    
                                self.instal_listTv(name)
                        elif returnValue is "pAnDaSAT_MUSICA":
                                name = 'pAnDaSAT_MUSICA'                    
                                self.instal_listTv(name)
                        elif returnValue is "pAnDaSAT_RADIO":
                                name = 'pAnDaSAT_RADIO'                    
                                self.instal_listTv(name)
                        elif returnValue is "pAnDaSAT_ADULTXXX":
                                name = 'pAnDaSAT_ADULTXXX'                    
                                self.instal_listTv(name)
                        elif returnValue.startswith("=="):
                                name = '=='
                                self.instal_listTv(name)
                else:
                    self.mbox = self.session.open(pndMessageBox, _('Bouquet non Installato'), pndMessageBox.TYPE_ERROR, timeout=4)    
                    return
            else:
                return 
                       
    def instal_listTv(self, name):
            name = name
            if name == 'pAnDaSAT_RADIO' :
                PNDNAME = 'userbouquet.%s.radio' % name
                bouquet = 'bouquets.radio'
                ext = 'radio'
                number = '2'
            else:    
                PNDNAME = 'userbouquet.%s.tv' % name
                bouquet = 'bouquets.tv'
                ext = 'tv'
                number = '1'
            in_bouquets = 0
            if os.path.isfile('/etc/enigma2/%s' % PNDNAME):
                os.remove('/etc/enigma2/%s' % PNDNAME)
            
            #######
            cmd = ('wget %se2liste/%s -O /etc/enigma2/userbouquet.%s.%s > /dev/null' % (server, PNDNAME, name, ext))
            print "cmd = ", cmd
            # self.session.open(Consolepnd, _('Installazione Lista Favorita %s: ') % name, ['%s' % cmd], closeOnSuccess=True) #finishedCallback=self.okInstalFav(), closeOnSuccess=True)
            os.system(cmd)
            self.mbox = self.session.open(pndMessageBox, _('CONTROLLA NELLA LISTA FAVORITI...'), pndMessageBox.TYPE_INFO, timeout=5)
            
            if os.path.isfile('/etc/enigma2/%s' % bouquet) :
                for line in open('/etc/enigma2/%s' % bouquet):
                    if PNDNAME in line:
                        in_bouquets = 1
                if in_bouquets is 0:
                        # if os.path.isfile('/etc/enigma2/%s' % PNDNAME): # and os.path.isfile('/etc/enigma2/%s' % bouquet):
                            # remove_line(('/etc/enigma2/%s' % bouquet), PNDNAME)
                            new_bouquet = open('/etc/enigma2/new_bouquets.tv', 'w')
                            file_read = open('/etc/enigma2/%s' % bouquet).readlines()                        
                            
                            if config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.bouquettop.value == 'Top': #config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.bouquettop.value and config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.bouquettop.value == 'Top':
                                #top  
                                new_bouquet.write('#SERVICE 1:7:%s:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % (number, PNDNAME))   
                                for line in file_read:
                                    new_bouquet.write(line)
                                new_bouquet.close()
                            # else:
                            if config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.bouquettop.value == 'Bottom':
                                for line in file_read:
                                    new_bouquet.write(line)
                                #bottom
                                new_bouquet.write('#SERVICE 1:7:%s:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % (number, PNDNAME))                            
                                new_bouquet.close()
                            system('cp -rf /etc/enigma2/bouquets.tv /etc/enigma2/backup_bouquets.tv')
                            system('mv -f /etc/enigma2/new_bouquets.tv /etc/enigma2/bouquets.tv')
                            system('chmod 0644 /etc/enigma2/%s' %PNDNAME )
                            #chmod(("/etc/enigma2/%s" % PNDNAME), 0644) 
                self.mbox = self.session.open(pndMessageBox, _('Riordino liste Favorite in Corso') + '\n' + _('Attendere prego ...'), pndMessageBox.TYPE_INFO, timeout=5)
            #    ReloadBouquet()
                eDVBDB.getInstance().reloadServicelist()
                eDVBDB.getInstance().reloadBouquets() 
                return
            return

            
            
         
####  
    def messagerun(self):
        returnValue = self["list"].l.getCurrentSelection()#[1]
        if returnValue is None or returnValue.startswith("=="):
            self.mbox = self.session.open(pndMessageBox, _('ERRORE CONNESSIONE O UNKNOW'), pndMessageBox.TYPE_ERROR, timeout=4) 
            return
        else:
            self.session.openWithCallback(self.messagerun2, pndMessageBox, _('Installare lista %s selezionata' % returnValue), pndMessageBox.TYPE_YESNO)

    def messagerun2(self, result):
        if result:
            self.session.openWithCallback(self.run, pndMessageBox, _('Installazione in Corso') + '\n' + _('Attendere prego ...'), pndMessageBox.TYPE_INFO, timeout=3)    
            
    # def pndchckint(self):
        # url3 = upd_fr_txt
        # #url3 = 'http://www.pandasat.info'
        # getPage(url3).addCallback(self.ConnOK).addErrback(self.ConnNOK)
        
    # def ConnOK(self, data):
        # self.pnd = data
        # self['chckon'].show()
        # self['pndon'].setPixmapNum(1)
        # self['pndon'].show()
        # self['pndinfo'].setText(_('Plugin sincronizzato ...'))

    # def ConnNOK(self, error):
        # self['chckoff'].show()
        # self['pndon'].setPixmapNum(2)
        # self['pndon'].show()
        # self['pndinfo'].setText(_('Nessuna Connessione Internet ?')) 
        
    def messagereload(self):
        self.session.openWithCallback(self.reloadSettings, pndMessageBox, _('Riordino liste Favorite in Corso') + '\n' + _('Attendere prego ...'), pndMessageBox.TYPE_INFO, timeout=3)

    def reloadSettings(self, result):
        if result:
            ReloadBouquet()



    def messagedellist(self):
        self.session.openWithCallback(self.deletelist, pndMessageBox, _('ATTENZIONE') + ':\n' + _('Eliminare le liste canali pAnDa SAT') + ' ?', pndMessageBox.TYPE_YESNO)

    def deletelist(self, result):
        if result:
            for file in os.listdir('/etc/enigma2/'):
                if file.startswith('userbouquet.pAnDaSAT') or file.startswith('userbouquet.pandasat'):
                    file = '/etc/enigma2/' + file
                    if os.path.exists(file):
                        print 'permantly remove file ', file
                        os.remove(file)
                        system("sed -i '/userbouquet.pAnDaSAT/d' /etc/enigma2/bouquets.tv")
                        system("sed -i '/userbouquet.pandasat/d' /etc/enigma2/bouquets.tv")
                        self.reloadSettings2()
                    radio = '/etc/enigma2/userbouquet.pAnDaSAT_RADIO.radio'
                    if os.path.exists(radio):
                        print 'permantly remove file ', radio
                        os.remove(radio)
                        system("sed -i '/userbouquet.pAnDaSAT/d' /etc/enigma2/bouquets.radio")
                        system("sed -i '/userbouquet.pandasat/d' /etc/enigma2/bouquets.radio")
                        self.reloadSettings2()

    def reloadSettings2(self):
        ReloadBouquet()
        self.mbox = self.session.open(pndMessageBox, _('Liste canali pAnDa SAT eliminate con successo'), pndMessageBox.TYPE_INFO, timeout=4)

    def M3uPlay(self):
        self.session.open(SELECTPLAY)
        
        
#############################################################
class Updater(Screen):

    def __init__(self, session):
        self.session = session
        skin = SKIN_PATH + '/updater.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()          
        Screen.__init__(self, session)
        self['fittitle'] = Label(_('..:: pAnDaSAT uPdAtEr ::..'))
        self['version'] = Label(_('Versione %s') % Version)
        self['pndteam'] = Label('by tEaM dEvElOpEr pAnDa SaT\xae')
        self['Maintainer'] = Label(_('Maintainer') + ': ')
        self['Maintainer2'] = Label(_('@Lululla'))
        self['Grafic'] = Label(_('Grafica') + ': ')
        self['Grafic2'] = Label(_('@pAnDa'))         
        self['status'] = Label()
        self['progress'] = Progress()
        self['progresstext'] = StaticText()

        server_ref()
        
        self.onLayoutFinish.append(self.readtar)
        # self.readtar()
        
    def readtar(self):
        self['status'].setText(_('Downloading ...'))
        try:
            getPage(TXT_PUKPRG).addCallback(self.gotUpdateInfo).addErrback(self.gotError)
        except Exception as error:
            print str(error)

    def gotError(self, error = ''):
        pass

    def gotUpdateInfo(self, html):
        
        tmp_infolines = html.splitlines()
        puk = tmp_infolines[0]
        lnk = tmp_infolines[1]
        default_lnk = tmp_infolines[2]
        
        pin = base64.b64decode(puk)
        puklnk = base64.b64decode(lnk)
        default_puk_lnk = base64.b64decode(default_lnk)
        
        if int(pin) == config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.code.value:
            system('mkdir -p /tmp/pandasat')
            self.updateurl = puklnk  
            self.updateurl = server + self.updateurl
            # self.updateurl = puklnk
            self.dlfile = '/tmp/pandasat/tmp.tar'
            self.download = downloadWithProgress(self.updateurl, self.dlfile)
            self.download.addProgress(self.downloadProgress)
            self.download.start().addCallback(self.downloadFinished).addErrback(self.downloadFailed)
            
        elif int(pin) != config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.code.value:
            system('mkdir -p /tmp/pandasat')
            self.updateurl = default_puk_lnk
            self.updateurl = server + self.updateurl            
            # self.updateurl = default_puk_lnk
            self.dlfile = '/tmp/pandasat/tmp.tar'
            self.download = downloadWithProgress(self.updateurl, self.dlfile)
            self.download.addProgress(self.downloadProgress)
            self.download.start().addCallback(self.downloadFinished).addErrback(self.downloadFailed)
        else:
            self.session.open(pndMessageBox, _('Server Error!!!'), pndMessageBox.TYPE_ERROR)
        
    def downloadFinished(self, string = ''):
        self['status'].setText(_('Installazione di aggiornamenti!'))
        system('rm -rf /etc/pandasat > /dev/null')
        system('tar -xvf /tmp/pandasat/tmp.tar -C /')
        system('rm -rf /tmp/pandasat')
        system('sleep 3')
        infobox = self.session.open( pndMessageBox, _('Liste aggiornate con Successo !!!!!!'), pndMessageBox.TYPE_INFO, timeout=5)
        self.close()

    def downloadFailed(self, failure_instance = None, error_message = ''):
        text = _('Errore durante il download di file!')
        if error_message == '' and failure_instance is not None:
            error_message = failure_instance.getErrorMessage()
            text += ': ' + error_message
        self['status'].setText(text)
        return

    def downloadProgress(self, recvbytes, totalbytes):
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))


##########################################################        
class SELECTPLAY(Screen):
    def __init__(self, session):
        self.session = session
        skin = SKIN_PATH + '/SelectPlay.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()           
        Screen.__init__(self, session)
        self.list = []
        self['list'] = PNDM3UList([])
        
        global srefInit
        self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
        srefInit = self.initialservice
        
        self['version'] = Label(_('Versione %s') % Version)
        self['fittitle'] = Label(_('..:: pAnDaSAT sElEcT m3U ::..'))
        self['pndteam'] = Label('by tEaM dEvElOpEr pAnDa SaT\xae')
        self['Maintainer'] = Label(_('Maintainer') + ': ')
        self['Maintainer2'] = Label(_('@Lululla'))
        self['Grafic'] = Label(_('Grafica') + ': ')
        self['Grafic2'] = Label(_('@pAnDa'))  
        self['info'] = Label()
        pthm3uf = config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthm3uf.value + 'movie' 
        self['path'] = Label(_('Cartella Configurata in Config %s') % pthm3uf)
        self['fitred'] = Label(_('Esci'))
        self['fitgreen'] = Label(_('Rimuovi'))
        self['fitblue'] = Label(_('Converti'))
        self['fitblue2'] = Label(_('ExtePlayer3'))
        self['fityellow'] = Label(_('Converti'))
        self['fityellow2'] = Label(_('Gstreamer'))
        # self['menu'] = Label(_('Config'))        
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'MenuActions', 'TimerEditActions'], {'red': self.message1,
         #'green': self.scsetup,
         # 'menu': self.scsetup,
         'green': self.message1,
         'blue': self.crea_bouquet5002,
         'yellow': self.crea_bouquet,
         'cancel': self.cancel,
         'ok': self.runList}, -2)
        self.convert = False

        try:

            if not path.exists(config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthm3uf.value +  'movie/pAnDaSAT_Free_IPTV.m3u'):
                cmd15 = pnd_m3ulnk + config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthm3uf.value + 'movie/pAnDaSAT_Free_IPTV.m3u > /dev/null'
                system(cmd15)
            else:
                cmd66 = 'rm -f ' + config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthm3uf.value + 'movie/pAnDaSAT_Free_IPTV.m3u'
                system(cmd66)
                cmd15 = pnd_m3ulnk + config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthm3uf.value + 'movie/pAnDaSAT_Free_IPTV.m3u > /dev/null'
                system(cmd15)        
        
        except Exception as ex:
            print ex
            print 'ex download m3u player'      

        # name = config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthm3uf.value  + 'movie/'
        self['info'].setText(_('pAnDaSAT m3U: Open Select'))
        self.name = config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthm3uf.value  + 'movie' #'movie/' #name
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.openList)

        
    def scsetup(self):
        self.session.openWithCallback(self.close, cfgplgConfig)
        #self.close()
        
    def openList(self):
        self.names = []
        self.Movies = []
        path = self.name
        # AA = ['.mkv','.mp4','.avi','.m3u']
        AA = ['.m3u']        
        for root, dirs, files in os.walk(path):
            for name in files:
                for x in AA:
                    if not x in name:
                        continue
                    self.names.append(name)
                    self.Movies.append(root +'/'+name)
        pass
        m3ulist(self.names, self['list'])

        
    def message1(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return
        else:
            self.session.openWithCallback(self.callMyMsg1,pndMessageBox,_("Vuoi rimuovere?"), pndMessageBox.TYPE_YESNO)       

    def callMyMsg1(self, result):
        if result:
            idx = self['list'].getSelectionIndex()
            path = self.Movies[idx]
            dom = path #+ self.names[idx]
            
#            dom = self.name + self.names[idx]
            if fileExists(dom):
                os.remove(dom)
            self.session.open(pndMessageBox, dom +'   has been successfully deleted\nwait time to refresh the list...', pndMessageBox.TYPE_INFO, timeout=5)
            # self.session.open(Consolepnd, _('pAnDaSaT cOnSoLe Rimuovo: %s') % dom, ['rm -rf %s' % com], closeOnSuccess=True)          
            # self.onShown.append(self.openList)
            del self.Movies[idx]
            del self.names[idx]
            
            self.onShown.append(self.openList)
#            m3ulist(self.names, self['list'])
##        else:
##                self.session.open(MessageBox, dom +'   not exist!', MessageBox.TYPE_INFO, timeout=5)

    def runList(self):
        idx = self['list'].getSelectionIndex()
        path = self.Movies[idx]
        if idx == -1 or None:
            return
        else:
            name = path# + self.names[idx]
            if '.m3u' in name : 
                self.session.open(M3uPlay, name)
                return
            else:
                # name = self.names[idx]            
                # sref = eServiceReference(4097, 0, path)
                # sref.setName(name)
                # self.session.openWithCallback(self.backToIntialService,xc_Player, sref)       
                return
                
                
            
    def crea_bouquet(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return
        else:
            name = self.names[idx]
            self.create_bouquet()
            return

            
    def crea_bouquet5002(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return
        else:
            name = self.names[idx]
            self.create_bouquet5002()
            return
            
            
    def create_bouquet5002(self):
            idx = self['list'].getSelectionIndex()
            self.convert = True
            name = self.names[idx]
            pth = self.name
            PNDNAME = 'userbouquet.%s.tv' % name
            self['info'] = StaticText()
            self.iConsole = iConsole()
            self['info'].text = _('Converting %s' % name)
            desk_tmp = hls_opt = ''
            in_bouquets = 0
            if os.path.isfile('/etc/enigma2/%s' % PNDNAME):
                os.remove('/etc/enigma2/%s' % PNDNAME)
            with open('/etc/enigma2/%s' % PNDNAME, 'w') as outfile:
                outfile.write('#NAME %s\r\n' % name.capitalize())
                for line in open(pth + '/%s' % name):
                    if line.startswith('http://'):
                        outfile.write('#SERVICE 5002:0:1:1:0:0:0:0:0:0:%s' % line.replace(':', '%3a'))
                        outfile.write('#DESCRIPTION %s' % desk_tmp)
                    elif line.startswith('#EXTINF'):
                        desk_tmp = '%s' % line.split(',')[-1]
                    elif '<stream_url><![CDATA' in line:
                        outfile.write('#SERVICE 5002:0:1:1:0:0:0:0:0:0:%s\r\n' % line.split('[')[-1].split(']')[0].replace(':', '%3a'))
                        outfile.write('#DESCRIPTION %s\r\n' % desk_tmp)
                    elif '<title>' in line:
                        if '<![CDATA[' in line:
                            desk_tmp = '%s\r\n' % line.split('[')[-1].split(']')[0]
                        else:
                            desk_tmp = '%s\r\n' % line.split('<')[1].split('>')[1]
                outfile.close()
            self['info'].setText(_('pAnDaSAT m3U: Open Select'))
            self.mbox = self.session.open(pndMessageBox, _('CONTROLLA NELLA LISTA FAVORITI...'), pndMessageBox.TYPE_INFO, timeout=5)
            if os.path.isfile('/etc/enigma2/bouquets.tv'):
                for line in open('/etc/enigma2/bouquets.tv'):
                    if PNDNAME in line:
                        in_bouquets = 1

                if in_bouquets is 0:
                    if os.path.isfile('/etc/enigma2/%s' % PNDNAME) and os.path.isfile('/etc/enigma2/bouquets.tv'):
                        remove_line('/etc/enigma2/bouquets.tv', PNDNAME)
                        with open('/etc/enigma2/bouquets.tv', 'a') as outfile:
                            outfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % PNDNAME)
                            outfile.close()
            self.mbox = self.session.open(pndMessageBox, _('Riordino liste Favorite in Corso') + '\n' + _('Attendere prego ...'), pndMessageBox.TYPE_INFO, timeout=5)
            ReloadBouquet()
                            
            return
        # else:
            # return
        
            
    def create_bouquet(self):
            idx = self['list'].getSelectionIndex()
            self.convert = True
            name = self.names[idx]
            pth = self.name
            PNDNAME = 'userbouquet.%s.tv' % name
            self['info'] = StaticText()
            self.iConsole = iConsole()
            self['info'].text = _('Converting %s' % name)
            desk_tmp = hls_opt = ''
            in_bouquets = 0
            if os.path.isfile('/etc/enigma2/%s' % PNDNAME):
                os.remove('/etc/enigma2/%s' % PNDNAME)
            with open('/etc/enigma2/%s' % PNDNAME, 'w') as outfile:
                outfile.write('#NAME %s\r\n' % name.capitalize())
                for line in open(pth + '/%s' % name):
                    if line.startswith('http://'):
                        outfile.write('#SERVICE 4097:0:1:1:0:0:0:0:0:0:%s' % line.replace(':', '%3a'))
                        outfile.write('#DESCRIPTION %s' % desk_tmp)
                    elif line.startswith('#EXTINF'):
                        desk_tmp = '%s' % line.split(',')[-1]
                    elif '<stream_url><![CDATA' in line:
                        outfile.write('#SERVICE 4097:0:1:1:0:0:0:0:0:0:%s\r\n' % line.split('[')[-1].split(']')[0].replace(':', '%3a'))
                        outfile.write('#DESCRIPTION %s\r\n' % desk_tmp)
                    elif '<title>' in line:
                        if '<![CDATA[' in line:
                            desk_tmp = '%s\r\n' % line.split('[')[-1].split(']')[0]
                        else:
                            desk_tmp = '%s\r\n' % line.split('<')[1].split('>')[1]

                outfile.close()
            self['info'].setText(_('pAnDaSAT m3U: Open Select'))
            self.mbox = self.session.open(pndMessageBox, _('CONTROLLA NELLA LISTA FAVORITI...'), pndMessageBox.TYPE_INFO, timeout=5)
            if os.path.isfile('/etc/enigma2/bouquets.tv'):
                for line in open('/etc/enigma2/bouquets.tv'):
                    if PNDNAME in line:
                        in_bouquets = 1

                if in_bouquets is 0:
                    if os.path.isfile('/etc/enigma2/%s' % PNDNAME) and os.path.isfile('/etc/enigma2/bouquets.tv'):
                        remove_line('/etc/enigma2/bouquets.tv', PNDNAME)
                        with open('/etc/enigma2/bouquets.tv', 'a') as outfile:
                            outfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % PNDNAME)
                            outfile.close()
            self.mbox = self.session.open(pndMessageBox, _('Riordino liste Favorite in Corso') + '\n' + _('Attendere prego ...'), pndMessageBox.TYPE_INFO, timeout=5)
            ReloadBouquet()
            return
        

    def cancel(self):
        if self.convert == False:
            self['info'].setText(_('pAnDaSAT m3U: Open Select'))
            self.close()
        else:
            self['info'].setText(_('pAnDaSAT m3U: Open Select'))
            self.close()


class M3uPlay(Screen):
    def __init__(self, session, name):
        self.session = session
        skin = SKIN_PATH + '/M3uPlay.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()        
        Screen.__init__(self, session)
        self.list = []
        self['list'] = PNDM3UList([])
        self['info'] = Label()
        self['version'] = Label(_('Versione %s') % Version)
        self['fittitle'] = Label(_('..:: pLaYeR m3U ::..'))
        self['pndteam'] = Label('by tEaM dEvElOpEr pAnDa SaT\xae')
        self['Maintainer'] = Label(_('Maintainer') + ': ')
        self['Maintainer2'] = Label(_('@Lululla'))
        self['Grafic'] = Label(_('Grafica') + ': ')
        self['Grafic2'] = Label(_('@pAnDa'))        
        self['fitred'] = Label(_('Esci'))
        self['fitgreen'] = Label(_('Play'))
        self['okpreview'] = Label(_('OK: Anteprima'))        
        
        self['fityellow'] = Label(_('Add Stream to'))
        self['fityellow2'] = Label(_('Bouquet Tv'))
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'TimerEditActions'], {'red': self.cancel,
         'green': self.runChannel,
         'cancel': self.cancel,
         'yellow': self.AdjUrlFavo,
         #'blue': self.runChannel,
         # 'ok': self.runChannel}, -2)         
         
         'ok': self.runPreview}, -2)
        self['info'].setText(_('pAnDaSAT List m3U N.'))
        self['live'] = Label('')
        self['live'].setText('')
        self.name = name
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        
        self.onLayoutFinish.append(self.playList)

        
        
    def playList(self):
        self.names = []
        self.urls = []
        try:
            if fileExists(self.name):
                f1 = open(self.name, 'r+')
                fpage = f1.read()
                regexcat = 'EXTINF.*?,(.*?)\\n(.*?)\\n'
                match = re.compile(regexcat, re.DOTALL).findall(fpage)
                for name, url in match:
                    url = url.replace(' ', '')
                    url = url.replace('\\n', '')
                    self.names.append(name)
                    self.urls.append(url)
                m3ulist(self.names, self['list'])
                self['live'].setText(str(len(self.names)) + ' Stream')
        except Exception as ex:
            print ex
            print 'ex playList' 
            
            
            
    def runChannel(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return
        else:
            name = self.names[idx]
            url = self.urls[idx]
            self.session.open(M3uPlay2, name, url)
            return
        # else:
            # return

            
    def runPreview(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return
        else:
            name = self.names[idx]
            url = self.urls[idx]
            url = url.replace(':', '%3a')
            self.url = url
            self.name = name
        
            # url = self.url
            if ".ts" in self.url: 
                ref = '4097:0:1:0:0:0:0:0:0:0:' + url
                print "ref= ", ref        
        
            else:
         
                if config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.services.value == 'Gstreamer':
                    ref = '4097:0:1:0:0:0:0:0:0:0:' + url
                    print "ref= ", ref
                else:
                    ref = '5002:0:1:0:0:0:0:0:0:0:' + url
                    print "ref= ", ref
            sref = eServiceReference(ref)
            sref.setName(self.name)
            self.session.nav.stopService()
            self.session.nav.playService(sref)

        
            
    def AdjUrlFavo(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return
        else:
            name = self.names[idx]
            url = self.urls[idx]
            self.session.open(AddIpvStream, name, url)
            return
        # else:
            # return

    def cancel(self):
        # Screen.close(self, False)
        self.session.nav.stopService()
        #self.session.nav.playService(self.srefOld)
        self.session.nav.playService(srefInit)
        
        self.close()

class M3uPlay2(Screen, InfoBarMenu, InfoBarBase, InfoBarSeek, InfoBarNotifications, InfoBarShowHide, InfoBarAudioSelection, InfoBarSubtitleSupport):

    # STATE_IDLE = 0
    # STATE_PLAYING = 1
    # STATE_PAUSED = 2
    # ENABLE_RESUME_SUPPORT = True
    # ALLOW_SUSPEND = True

                
    def __init__(self, session, name, url):
        
        Screen.__init__(self, session)
        self.skinName = 'MoviePlayer'
        title = 'Play Stream'
        self['list'] = MenuList([])
        InfoBarMenu.__init__(self)
        InfoBarNotifications.__init__(self)
        InfoBarBase.__init__(self)
        InfoBarShowHide.__init__(self)
        # InfoBarSubtitleSupport.__init__(self)
        # InfoBarAudioSelection.__init__(self)
        self['actions'] = ActionMap(['WizardActions',
         'MoviePlayerActions',
         'MovieSelectionActions',
         'MediaPlayerActions',
         'EPGSelectActions',
         'MediaPlayerSeekActions',
         'SetupActions',
         'ColorActions',
         'InfobarShowHideActions',
         'InfobarActions',
         'InfobarSeekActions'], {'leavePlayer': self.cancel,
         'showEventInfo': self.showVideoInfo,
         'stop': self.leavePlayer,
         'back': self.cancel}, -1)
        self.allowPiP = False
#        InfoBarSeek.__init__(self, actionmap='MediaPlayerSeekActions')
        InfoBarSeek.__init__(self, actionmap='InfobarSeekActions')       
        url = url.replace(':', '%3a')
        self.url = url
        self.name = name
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.openPlay)

    # def openPlay(self):
        # url = self.url
        # if config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.services.value == 'Gstreamer':
            # ref = '4097:0:1:0:0:0:0:0:0:0:' + url
        # else:
            # ref = '5002:0:1:0:0:0:0:0:0:0:' + url   
        # # ref = '4097:0:1:0:0:0:0:0:0:0:' + url
        # sref = eServiceReference(ref)
        # sref.setName(self.name)
        # self.session.nav.stopService()
        # self.session.nav.playService(sref)
    #
    def openPlay(self):
        url = self.url
        if ".ts" or ".mp4" or ".avi" in self.url: 
            ref = '4097:0:1:0:0:0:0:0:0:0:' + url
            print "ref= ", ref        
        
        else:
        
            if config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.services.value == 'Gstreamer':
                ref = '4097:0:1:0:0:0:0:0:0:0:' + url
                print "ref= ", ref
            else:
                ref = '5002:0:1:0:0:0:0:0:0:0:' + url
                print "ref= ", ref
        sref = eServiceReference(ref)
        sref.setName(self.name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)
        
    def keyNumberGlobal(self, number):
        self['text'].number(number)

    def cancel(self):
        self.session.nav.stopService()
        self.session.nav.playService(srefInit)
        # self.session.nav.playService(self.srefOld)
        self.close()

    def ok(self):
        if self.shown:
            self.hideInfobar()
        else:
            self.showInfobar()

    def keyLeft(self):
        self['text'].left()

    def keyRight(self):
        self['text'].right()

    def showVideoInfo(self):
        if self.shown:
            self.hideInfobar()
        if self.infoCallback is not None:
            self.infoCallback()
        return

    def leavePlayer(self):
        self.close()

class AddIpvStream(Screen):

    def __init__(self, session, name, url):
        self.session = session
        skin = SKIN_PATH + '/AddIpvStream.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()          
        Screen.__init__(self, session)
        self['fittitle'] = Label(_('..:: pAnDaSAT Add Stream ::..'))        
        self['version'] = Label(_('Versione %s') % Version)
        self['Maintainer'] = Label(_('Maintainer') + ': ')
        self['Maintainer2'] = Label(_('@Lululla'))
        self['Grafic'] = Label(_('Grafica') + ': ')
        self['Grafic2'] = Label(_('@pAnDa'))        
        self['pndteam'] = Label('by tEaM dEvElOpEr pAnDa SaT')
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.keyOk,
         'cancel': self.keyCancel,
         'green': self.keyOk,
         'red': self.keyCancel}, -2)
        self['statusbar'] = StaticText(_('Seleziona i flussi da aggiungere al bouquet'))
        self.list = []
        self['menu'] = MenuList([])
        
        # self['menu'] = PNDM3UList([])        
        
        self.mutableList = None
        self.servicelist = ServiceList(None)
        self.onLayoutFinish.append(self.createTopMenu)
        self.namechannel = name
        self.urlchannel = url
        return

    def initSelectionList(self):
        self.list = []
        self['menu'].setList(self.list)

    def createTopMenu(self):
        self.setTitle(_('Add IPTV Channels'))
        self.initSelectionList()
        self.list = []
        tmpList = []
        self.list = self.getBouquetList()
        self['menu'].setList(self.list)

        
        
    def getBouquetList(self):
        self.service_types = service_types_tv
        if config.usage.multibouquet.value:
            self.bouquet_rootstr = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet'
        else:
            self.bouquet_rootstr = '%s FROM BOUQUET "userbouquet.favourites.tv" ORDER BY bouquet' % self.service_types
        self.bouquet_root = eServiceReference(self.bouquet_rootstr)
        bouquets = []
        serviceHandler = eServiceCenter.getInstance()
        if config.usage.multibouquet.value:
            list = serviceHandler.list(self.bouquet_root)
            if list:
                while True:
                    s = list.getNext()
                    if not s.valid():
                        break
                    if s.flags & eServiceReference.isDirectory:
                        info = serviceHandler.info(s)
                        if info:
                            bouquets.append((info.getName(s), s))

                return bouquets
        else:
            info = serviceHandler.info(self.bouquet_root)
            if info:
                bouquets.append((info.getName(self.bouquet_root), self.bouquet_root))
            return bouquets
        return None

    def keyOk(self):
        if len(self.list) == 0:
            return
        self.name = ''
        self.url = ''
        self.session.openWithCallback(self.addservice, VirtualKeyBoard, title=_('Enter name'), text=self.namechannel)

    def addservice(self, res):
        if res:
            self.url = res
            str = '4097:0:0:0:0:0:0:0:0:0:%s:%s' % (quote(self.url), quote(self.name))
            ref = eServiceReference(str)
            self.addServiceToBouquet(self.list[self['menu'].getSelectedIndex()][1], ref)
            self.close()

    def addServiceToBouquet(self, dest, service = None):
        mutableList = self.getMutableList(dest)
        if mutableList is not None:
            if service is None:
                return
            if not mutableList.addService(service):
                mutableList.flushChanges()
        return

    def getMutableList(self, root = eServiceReference()):
        if self.mutableList is not None:
            return self.mutableList
        else:
            serviceHandler = eServiceCenter.getInstance()
            if not root.valid():
                root = self.getRoot()
            list = root and serviceHandler.list(root)
            if list is not None:
                return list.startEdit()
            return
            return

    def getRoot(self):
        return self.servicelist.getRoot()

    def keyCancel(self):
        self.close()

class cfgplgConfig(Screen, ConfigListScreen):

    def __init__(self, session):
        self.session = session
        if fileExists(BRAND) or fileExists(BRANDP):
            skin = SKIN_PATH + '/cfgplgConfigOpen.xml'
        else:
            skin = SKIN_PATH + '/cfgplgConfig.xml'        
        
        ###########
        ###skin = SKIN_PATH + '/cfgplgConfig.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()  
        Screen.__init__(self, session)
        info = '***'
        self['fittitle'] = Label(_('..:: pAnDaSAT iPtV cOnFiG ::..'))
        self['version'] = Label(_('Versione %s') % Version)
        self['pndteam'] = Label('by tEaM dEvElOpEr pAnDa SaT\xae')
        self['Maintainer'] = Label(_('Maintainer') + ': ')
        self['Maintainer2'] = Label(_('@Lululla'))
        self['Grafic'] = Label(_('Grafica') + ': ')
        self['Grafic2'] = Label(_('@pAnDa'))        
        self['fitred'] = Label(_('Esci'))
        self['fityellow'] = Label(_('Aggiorna Plugin'))
        self['fitgreen'] = Label(_('Salva'))
        self['email'] = Label(_('Use email: panda@pandasat.info'))
        self['text'] = Label(info)
        self.setup_title = _("pAnDaSAT-cOnFiG")
        self.onChangedEntry = [ ]
        self.list = []
        ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)
        self.createSetup()
        self.cbUpdate = False
        self["setupActions"] = ActionMap(['OkCancelActions', 'DirectionActions', 'ColorActions', 'VirtualKeyboardActions', 'ActiveCodeActions'],
        {
                "red": self.extnok,
                "cancel": self.extnok,
                'yellow': self.msgupdt1,
                "green": self.cfgok,
                'showVirtualKeyboard': self.KeyText,
                "ok": self.Ok_edit

        }, -1)         
         
        self.onLayoutFinish.append(self.layoutFinished) 

        
        
    def layoutFinished(self):
        server_ref()
    
        self.setTitle(self.setup_title)        
        try:
            fp = urllib.urlopen(upd_fr_txt)
            count = 0
            self.labeltext = ''
            s1 = fp.readline()
            s2 = fp.readline()
            s3 = fp.readline()
            s1 = s1.strip()
            s2 = s2.strip()
            s3 = s3.strip()
            self.link = s2
            self.link = server + s2
            self.version = s1
            self.info = s3
            fp.close()
            if s1 == currversion:
                self['text'].setText(_('Free IPTV versione: ') + currversion + _('\nNessun aggiornamento online!') + _('\nGrazie a coloro che hanno lavorato al progetto') + _('\nPLEASE DONATE'))
                self.cbUpdate = False
            elif float(s1) < float(currversion):
                self['text'].setText(_('Free IPTV versione: ') + currversion + _('\nNessun aggiornamento online!') + _('\nGrazie a coloro che hanno lavorato al progetto') + _('\nPLEASE DONATE'))
                self.cbUpdate = False
            else:
                updatestr = (_('Free IPTV versione: ') + currversion + _('\nUltimo aggiornamento ') + s1 + _(' disponibile!  \nChangeLog:') + self.info)
                self.cbUpdate = True
                self['text'].setText(updatestr)
        except:
            self.cbUpdate = False
            self['text'].setText(_('Nessun aggiornamento disponibile') + _('\nNessuna connessione Internet o server OFF') + _('\nPrego riprova piu tardi o cambia SERVER in menu config.'))

        self.timerx = eTimer()
        try:
            self.timerx.callback.append(self.msgupdt2)
        except:
            self.timerx_conn = self.timerx.timeout.connect(self.msgupdt2)
        self.timerx.start(100, 1)

    def createSetup(self):
        self.editListEntry = None
        self.list = []

        self.list.append(getConfigListEntry(_('Server:'), config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.server))
        self.list.append(getConfigListEntry(_('Auto Update Plugin:'), config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.autoupd))
        self.list.append(getConfigListEntry(_('Password Personale:'), config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.code))
        self.list.append(getConfigListEntry(_('Percorso Picons:'), config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthpcns))
        self.list.append(getConfigListEntry(_('Percorso Scripts:'), config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthchs))
        self.list.append(getConfigListEntry(_("Posizione IPTV bouquets "), config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.bouquettop))
        self.list.append(getConfigListEntry(_('Liste Player <.m3u>:'), config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthm3uf))
        self.list.append(getConfigListEntry(_("Services Type"), config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.services))
        self.list.append(getConfigListEntry(_('Link in Extensions Menu:'), config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.strtext))
        self.list.append(getConfigListEntry(_('Link in Menu Principale:'), config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.strtmain))
        self['config'].list = self.list
        self["config"].setList(self.list)

        
#################

    def changedEntry(self):
        for x in self.onChangedEntry:
                x()        

        #
    def getCurrentEntry(self):
        return self["config"].getCurrent()[0]

        #
    def getCurrentValue(self):
        return str(self["config"].getCurrent()[1].getText())

        #
    def createSummary(self):
        from Screens.Setup import SetupSummary
        return SetupSummary
            
        #
    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        print "current selection:", self["config"].l.getCurrentSelection()
        self.createSetup()

        #
    def keyRight(self):
        ConfigListScreen.keyRight(self)
        print "current selection:", self["config"].l.getCurrentSelection()
        self.createSetup()
            
        #
    def Ok_edit(self):    
        ConfigListScreen.keyRight(self)
        print "current selection:", self["config"].l.getCurrentSelection()
        self.createSetup()
            
    def cfgok(self):
        self.save()

    def save(self):
        if not os.path.exists(config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthpcns.value):
            self.mbox = self.session.open(pndMessageBox, _('Cartella Picons non rilevato!'), pndMessageBox.TYPE_INFO, timeout=4)
            return
        if not os.path.exists(config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthchs.value):
            self.mbox = self.session.open(pndMessageBox, _('Cartella Scripts non rilevato!'), pndMessageBox.TYPE_INFO, timeout=4)
            return
        if not os.path.exists(config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthm3uf.value):
            self.mbox = self.session.open(pndMessageBox, _('Cartella Liste m3u non rilevato!'), pndMessageBox.TYPE_INFO, timeout=4)
            return
            
        if self['config'].isChanged():
            for x in self['config'].list:
                x[1].save()
            
            server_ref()
            
            config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.server.save()    
            configfile.save()
            plugins.clearPluginList()
            plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
            self.mbox = self.session.open(pndMessageBox, _('Impostazioni salvate correttamente !'), pndMessageBox.TYPE_INFO, timeout=5)
            # self.changedFinished()
            self.close()
        else:
           self.close()            

          
        
    def KeyText(self):
        sel = self['config'].getCurrent()
        if sel:
            self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=self['config'].getCurrent()[0], text=self['config'].getCurrent()[1].value)

    def VirtualKeyBoardCallback(self, callback = None):
        if callback is not None and len(callback):
            self['config'].getCurrent()[1].value = callback
            self['config'].invalidate(self['config'].getCurrent())
        return                

    #
    def cancelConfirm(self, result):
        if not result:
            return
        for x in self['config'].list:
            x[1].cancel()
        
        self.close()
        # self.session.openWithCallback(self.close, ABOUT) 
        
        
    def extnok(self):
        if self['config'].isChanged():
            self.session.openWithCallback(self.cancelConfirm, pndMessageBox, _('Veramente chiudere senza salvare le impostazioni?'))
        else:
            # self.session.openWithCallback(self.close, ABOUT)         
            self.close()
                
    def msgupdt2(self):
        if self.cbUpdate == False:
            return
        if config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.autoupd.value == False:
            return
        self.session.openWithCallback(self.runupdate, pndMessageBox, _('Nuova Versione Online!!!\n\nAggiornare Plugin alla Versione %s ?' % self.version), pndMessageBox.TYPE_YESNO)

    def msgupdt1(self):
        if self.cbUpdate == False:
            return
        self.session.openWithCallback(self.runupdate, pndMessageBox, _('Aggiornare Plugin ?'), pndMessageBox.TYPE_YESNO)

    def runupdate(self, result):
        if self.cbUpdate == False:
            return
        if result:
            com = self.link
            dom = 'Nuova versione ' + self.version
            self.session.open(Consolepnd, _('Aggiorno Plugin: %s') % dom, ['opkg install -force-overwrite %s' % com], finishedCallback=self.msgrstrt3, closeOnSuccess=True)
        
    def msgrstrt3(self):
        self.mbox = self.session.open(pndMessageBox, _('Plugin Aggiornato!\nRiavvio interfaccia utente'), pndMessageBox.TYPE_INFO, timeout=4)
        quitMainloop(3)
        
    # def changedFinished(self):
        # self.session.openWithCallback(self.ExecuteRestart, MessageBox, _("Per applicare le modifiche necessarie Riavviare la GUI") +"\n"+_("Vuoi riavviare adesso??"), MessageBox.TYPE_YESNO)

    # def ExecuteRestart(self, result):
        # if result:
            # quitMainloop(3)
        # else:
            # self.close()  
            
class EXTRA(Screen):

    def __init__(self, session):
        self.session = session
        skin = SKIN_PATH + '/EXTRA.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()          
        Screen.__init__(self, session)
        self.list = []
        self['list'] = PNDM3UList([])        
        self['fittitle'] = Label(_('..:: pAnDaSAT sCrIpT ::..'))
        self['pndteam'] = Label('by tEaM dEvElOpEr pAnDa SaT\xae')
        self['version'] = Label(_('Versione %s') % Version)
        self['Maintainer'] = Label(_('Maintainer') + ': ')
        self['Maintainer2'] = Label(_('@Lululla'))
        self['Grafic'] = Label(_('Grafica') + ': ')
        self['Grafic2'] = Label(_('@pAnDa'))        
        self['fitred'] = Label(_('Esci'))
        self['fitgreen'] = Label(_('Speed'))
        self['fitgreen2'] = Label(_('Test'))
        self['fityellow'] = Label(_('Picons'))
        self['fityellow2'] = Label(_('pAnDaSAT'))
        self['fitblue'] = Label(_('Player'))
        self['fitblue2'] = Label(_('List'))
        self['fitgrey'] = Label(_('Info'))
        
        server_ref()
        
        self.icount = 0
        self.timer1 = eTimer()
        _lstpnd = '/etc/pandasat/extra/TempClean'
        if not os.path.isfile(_lstpnd):
            try:
                self.timer1.callback.append(self.checkList)
            except:
                self.timer1_conn = self.timer1.timeout.connect(self.checkList)
            self.timer1.start(200, 1)        
        self['actions'] = ActionMap(['OkCancelActions',
         'DirectionActions',
         'ColorActions',
         'WizardActions',
         'NumberActions',
         'EPGSelectActions'], {'ok': self.messagerun,
         'red': self.close,
         'green': self.messagespeedtest,
         'info': self.close,
         'back': self.close,
         'yellow': self.picon,
         'blue': self.M3uPlay,
         #'blue': self.messagerun,
         'cancel': self.close}, -1)
        self.onLayoutFinish.append(self.openList)


    def openList(self):
        self.names = []
        path = config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthchs.value
        for root, dirs, files in os.walk(path):
            if files is not None:
                files.sort()  
                for name in files:
                    # if not '.sh' or '.pnd' in name: #'Info' or 'Setting' or 'Delete' or 'Update' or 'Temp' or 'Plugins' not in name:
                        # continue
                    self.names.append(name)

        m3ulist(self.names, self['list'])

    def run(self, result):
        pthchs2 = config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthchs.value      
        if result:
            idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return
        else:
            script = self.names[idx]
            
            if script is not None:
                system('chmod 755 %s/*' % pthchs2)
                self.prombt(pthchs2 + '/' + script)
            return
            # else:
                # return
        # else:
            # return
        
    def checkList(self):
        self.session.openWithCallback(self.update2, pndMessageBox, _('Nessuno script in Elenco!') + ' ' + _('Scaricare Script') + ' by pAnDa SAT ?', pndMessageBox.TYPE_YESNO)        

    def update2(self, answer):
        if answer is True:
            self.session.open(Updater)
            #infobox = self.session.open( pndMessageBox, _('Liste aggiornate con Successo !!!!!!'), pndMessageBox.TYPE_INFO, timeout=5)
            self.close()
        else:
            return

    def messagerun(self):
        self.session.openWithCallback(self.messagerun2, pndMessageBox, _('Esegui script selezionato') + ' ' + _('in Elenco') + ' by pAnDa SAT ?', pndMessageBox.TYPE_YESNO)

    def messagerun2(self, result):
        if result:
            self.session.openWithCallback(self.run, pndMessageBox, _('Recupero Informazioni in Corso') + '\n' + _('Attendere prego ...'), pndMessageBox.TYPE_INFO, timeout=3)

    def messagespeedtest(self):
        self.session.openWithCallback(self.speedtest, pndMessageBox, _('ATTENZIONE') + ':\n' + _('Utilizzando il test bisogna attendere') + '\n' + _('qualche minuto...') + '\n' + _('Continuare') + ' ?', pndMessageBox.TYPE_YESNO)

    def speedtest(self, result):
        if result:
            cmd17 = 'chmod 755 ' + plugin_path + 'res/script/speedtest.py'
            system(cmd17)
            self.session.open(SpeedtestS)
            return

    def prombtspeed(self, com):
        self.session.open(SpeedtestS)

    def prombt(self, com):
        self.session.open(Consolepnd, _('pAnDaSaT cOnSoLe'), ['%s' % com], closeOnSuccess=False)

    def picon(self):
        self.session.open(PICONS)
        
    def M3uPlay(self):
        self.session.open(SELECTPLAY)

class SpeedtestS(Screen):

    def __init__(self, session):
        self.session = session
        skin = SKIN_PATH + '/Speedtestpnd.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()          
        Screen.__init__(self, session)
        self['fittitle'] = Label(_('..:: pAnDaSAT sPeEdTeSt ::..'))        
        self['version'] = Label(_('Versione %s') % Version)
        self['pndteam'] = Label('by tEaM dEvElOpEr pAnDa SaT\xae')
        self['Maintainer'] = Label(_('Maintainer') + ': ')
        self['Maintainer2'] = Label(_('@Lululla'))
        self['Grafic'] = Label(_('Grafica') + ': ')
        self['Grafic2'] = Label(_('@pAnDa'))          
        self['fitping'] = Label(_('Ping'))
        self['fithost'] = Label(_('Host'))
        self['fitip'] = Label(_('IP'))
        self['fitdownload'] = Label(_('Download'))
        self['fitupload'] = Label(_('Upload'))
        self['fitred'] = Label(_('Esci'))
        self['text'] = Label(_('Speed Test in corso, attendere......'))
        self['ping'] = Label(' ')
        self['host'] = Label(' ')
        self['ip'] = Label(' ')
        self['download'] = Label(' ')
        self['upload'] = Label(' ')
        self['actions'] = ActionMap(['WizardActions',
         'OkCancelActions',
         'DirectionActions',
         'ColorActions'], {'ok': self.cancel,
         'back': self.cancel}, -1)
        cmd = 'python ' + plugin_path + 'res/script/speedtest.py'
        self.text = ''
        self.container = eConsoleAppContainer()
        try:
            self.container.appClosed.append(self.runtest)
        except:
            self.appClosed_conn = self.container.appClosed.connect(self.runtest)

        try:
            self.container.dataAvail.append(self.dataAvail)
        except:
            self.dataAvail_conn = self.container.dataAvail.connect(self.dataAvail)

        self.container.execute(cmd)

    def runtest(self, retval):
        print 'retval', retval
        print 'Test OK'
        self['text'].setText(_('\nSPEEDTEST\nCOMPLETATO\n\nby tEaM dEvElOpEr pAnDa SaT'))

        
    def cancel(self):
        try:
            self.container.appClosed.remove(self.runtest)
        except:
            self.appClosed_conn = None

        try:
            self.container.dataAvail.remove(self.dataAvail)
        except:
            self.dataAvail_conn = None

        self.close()
        return

    def dataAvail(self, rstr):
        if rstr:
            self.text = self.text + rstr
            parts = rstr.split('\n')
            for part in parts:
                if 'Hosted by' in part:
                    try:
                        host = part.split('Hosted by')[1].split('[')[0].strip()
                    except:
                        host = ''

                    self['host'].setText(str(host))
                if 'Testing from' in part:
                    ip = part.split('Testing from')[1].split(')')[0].replace('(', '').strip()
                    self['ip'].setText(str(ip))
                if 'Ping' in rstr:
                    try:
                        ping = rstr.split('Ping')[1].split('\n')[0].strip()
                    except:
                        ping = ''

                    self['ping'].setText(str(ping))
                    self.text = ''
                    self.text = 'Test speed download ....'
                if 'Download:' in rstr:
                    try:
                        download = rstr.split(':')[1].split('\n')[0].strip()
                    except:
                        download = ''

                    self['download'].setText(str(download))
                    self.text = ''
                    self.text = 'Test speed upload ....'
                if 'Upload:' in rstr:
                    try:
                        upload = rstr.split(':')[1].split('\n')[0].strip()
                    except:
                        upload = ''

                    self['upload'].setText(str(upload))
                    self.text = ''
                    self['text'].setText('Test OK')

            self['text'].setText(self.text)


class PICONS(Screen):

    def __init__(self, session):
        self.session = session
        skin = SKIN_PATH + '/PICONS.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()          
        Screen.__init__(self, session)
        self['fittitle'] = Label(_('..:: pAnDaSAT pIcOnS ::..'))
        self['version'] = Label(_('Versione %s') % Version)
        self['pndteam'] = Label('by tEaM dEvElOpEr pAnDa SaT\xae')        
        self['Maintainer'] = Label(_('Maintainer') + ': ')
        self['Maintainer2'] = Label(_('@Lululla'))
        self['Grafic'] = Label(_('Grafica') + ': ')
        self['Grafic2'] = Label(_('@pAnDa'))         
        self['fitred'] = Label(_('Elimina'))
        self['fitred2'] = Label(_('I Picons'))
        self['fitgreen'] = Label(_('Installa'))
        self['fitgreen2'] = Label(_('I Picons'))
        # self['fityellow'] = Label(_('Config'))
        self['fitgrey'] = Label(_('Info'))
        patchPcn = config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthpcns.value
        self['path'] = Label(_('Cartella Configurata in Config %s') % patchPcn)  
        self['actions'] = ActionMap(['OkCancelActions',
         'DirectionActions',
         'ColorActions',
         'WizardActions',
         'NumberActions',
         'EPGSelectActions'], {'ok': self.close,
         'red': self.messagedelpicon,
         'info': self.close,
         'back': self.close,
         'green': self.runpicons,
         # 'yellow': self.scsetup,
         'cancel': self.close}, -1)

    def messagedelpicon(self):
        patchPcn = config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthpcns.value
        self.session.openWithCallback(self.delpicon, pndMessageBox, _('ATTENZIONE:\n Eliminare i Picon by pAnDa SAT?') + '\n' + _('in %spicon') % patchPcn, pndMessageBox.TYPE_YESNO)

    def delpicon(self, result):
        if result:
            if config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthpcns.value == '/usr/share/enigma2/':
                system('opkg remove picons-pandasat-freeiptv-flash')
                
            if config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthpcns.value == '/media/hdd/':
                system('opkg remove picons-pandasat-freeiptv-hdd')
                
            if config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthpcns.value == '/media/usb/':
                system('opkg remove picons-pandasat-freeiptv-usb')
                
            #else:
            cmd17 = 'rm -f ' + config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthpcns.value + 'picon/4097_*'
            system(cmd17)
            time.sleep(100)
            self.endpicondel()
        else:
            return

    def endpicondel(self):
        self.mbox = self.session.open(pndMessageBox, _('Picons eliminati con successo'), pndMessageBox.TYPE_WARNING, timeout=4)

    def runpicons(self):
        if not os.path.isfile(config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthpcns.value + '/picon/4097_0_1_A1_998_9999_820000_0_0_0.png'):
            self.messagepcn()
        else:
            self.mbox = self.session.open(pndMessageBox, _("PICONS GIA' INSTALLATI.  ELIMINARE PRIMA."), pndMessageBox.TYPE_WARNING, timeout=4)            
            
    def messagepcn(self):
        
        server_ref()
    
        patchPcn = config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthpcns.value
        VerifyHost = self.Ver_URL(host)
        if VerifyHost == False :
            self.mbox = self.session.open(pndMessageBox, (_('Impossibile Installare Picon') + (_(' in %spicon' % patchPcn)) + _('\nServer off') ), pndMessageBox.TYPE_WARNING, timeout=5)  

        else:
            patchPcn = config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthpcns.value
            self.session.openWithCallback(self.messagepcn2, pndMessageBox, (_('ATTENZIONE:\n Installa i Picon by pAnDa SAT\n') + _('in %spicon') % patchPcn + _('\n al termine riavviare Enigma!') ), pndMessageBox.TYPE_YESNO)            

    def Ver_URL(self, url):
        req = urllib2.Request(url)
        try:
            response = urllib2.urlopen(req)
            the_page = response.read()
            print the_page 
            verifica = True
            
        except urllib2.HTTPError as e:
            print e.code
            the_page = '%s' % e.code
            verifica = False
            
        except urllib2.URLError as e:
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
            the_page = '%s' % e.reason
            verifica = False
        #return the_page
        return verifica            
            
    def messagepcn2(self, result):
        patchPcn = config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthpcns.value
        if result:
            self.session.openWithCallback(self.piconinst, pndMessageBox, _('Installazione Picons in Corso') + '\n' + _('in %spicon') % patchPcn + '\n' + _('Attendere prego ...'), pndMessageBox.TYPE_WARNING, timeout=3)            
            
    def piconinst(self, result):
        patchPcn = config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthpcns.value
        if result:
            if os.path.exists(patchPcn) is True and patchPcn == '/media/hdd/':
                self.link = picon_ipk_hdd
            if os.path.exists(patchPcn) is True and patchPcn == '/media/usb/':
                self.link = picon_ipk_usb
            if os.path.exists(patchPcn) is True and patchPcn == '/usr/share/enigma2/':
                self.link = picon_ipk_flash
            com = self.link
            dom = (_('in %s') % patchPcn + _('picon'))
            self.session.open(Consolepnd, _('Installazione Picons: %s') % dom, ['opkg install -force-overwrite %s' % com], finishedCallback=self.done(), closeOnSuccess=True)
            
        else:
            self.mbox = self.session.open(pndMessageBox, (_('Impossibile Installare Picon') + _(' in %spicon') % patchPcn), pndMessageBox.TYPE_WARNING, timeout=5)            
            
    def done(self):
        patchPcn = config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.pthpcns.value
        self.mbox = self.session.open(pndMessageBox, (_('Picons installati con successo') + _(' in %spicon') % patchPcn), pndMessageBox.TYPE_INFO, timeout=6)

    # def scsetup(self):
        # self.session.openWithCallback(self.close, cfgplgConfig)


class Consolepnd(Screen):

    def __init__(self, session, title = None, cmdlist = None, finishedCallback = None, closeOnSuccess = False):
        self.session = session
        skin = SKIN_PATH + '/Consolepnd.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()          
        Screen.__init__(self, session)
        self.finishedCallback = finishedCallback
        self.closeOnSuccess = closeOnSuccess
        self['text'] = ScrollLabel('')
        self['fittitle'] = Label(_('..:: pAnDaSAT cOnSoLe ::..'))
        self['Maintainer'] = Label(_('Maintainer') + ': ')
        self['Maintainer2'] = Label(_('@Lululla'))
        self['Grafic'] = Label(_('Grafica') + ': ')
        self['Grafic2'] = Label(_('@pAnDa'))
        self['pndteam'] = Label('by tEaM dEvElOpEr pAnDa SaT\xae')
        self['version'] = Label(_('Versione %s') % Version)        
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions'], {'ok': self.cancel,
         'back': self.cancel,
         'up': self['text'].pageUp,
         'down': self['text'].pageDown}, -1)
        self.cmdlist = cmdlist
        self.container = eConsoleAppContainer()
        self.run = 0
        try:
            self.container.appClosed.append(self.runFinished)
        except:
            self.appClosed_conn = self.container.appClosed.connect(self.runFinished)

        try:
            self.container.dataAvail.append(self.dataAvail)
        except:
            self.dataAvail_conn = self.container.dataAvail.connect(self.dataAvail)

        self.onLayoutFinish.append(self.startRun)

    def updateTitle(self):
        self.setTitle(self.newtitle)

    def startRun(self):
        self['text'].setText(_('Esecuzione in corso:') + '\n\n')
        print 'Console: executing in run', self.run, ' the command:', self.cmdlist[self.run]
        if self.container.execute(self.cmdlist[self.run]):
            self.runFinished(-1)

    def runFinished(self, retval):
        self.run += 1
        if self.run != len(self.cmdlist):
            if self.container.execute(self.cmdlist[self.run]):
                self.runFinished(-1)
        else:
            str = self['text'].getText()
            str += _('Esecuzione finita!!')
            self['text'].setText(str)
            self['text'].lastPage()
            if self.finishedCallback is not None:
                self.finishedCallback()
            if not retval and self.closeOnSuccess:
                self.cancel()
        return

    def cancel(self):
        if self.run == len(self.cmdlist):
            self.close()
        try:
            self.container.appClosed.remove(self.runFinished)
        except:
            self.appClosed_conn = None

        try:
            self.container.dataAvail.remove(self.dataAvail)
        except:
            self.dataAvail_conn = None

        return

    def dataAvail(self, str):
        self['text'].setText(self['text'].getText() + str)


class pndMessageBox(Screen):
    TYPE_YESNO = 0
    TYPE_INFO = 1
    TYPE_WARNING = 2
    TYPE_ERROR = 3
    TYPE_MESSAGE = 4

    def __init__(self, session, text, type = TYPE_YESNO, timeout = -1, close_on_any_key = False, default = True, enable_input = True, msgBoxID = None, picon = None, simple = False, list = [], timeout_default = None):
        self.type = type
        self.session = session
        skin = SKIN_PATH + '/pndMessageBox.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()          
        Screen.__init__(self, session)
        self.msgBoxID = msgBoxID
        self['fittitle'] = Label(_('..:: pAnDaSAT MeSsAgE ::..'))
        self['version'] = Label(_('Versione %s') % Version)
        self['pndteam'] = Label('by tEaM dEvElOpEr pAnDa SaT\xae')
        self['Maintainer'] = Label(_('Maintainer') + ': ')
        self['Maintainer2'] = Label(_('@Lululla'))
        self['Grafic'] = Label(_('Grafica') + ': ')
        self['Grafic2'] = Label(_('@pAnDa'))         
        self['text'] = Label(text)
        self['Text'] = StaticText(text)
        self['selectedChoice'] = StaticText()
        self.text = text
        self.close_on_any_key = close_on_any_key
        self.timeout_default = timeout_default
        self['ErrorPixmap'] = Pixmap()
        self['QuestionPixmap'] = Pixmap()
        self['InfoPixmap'] = Pixmap()
        self['WarningPixmap'] = Pixmap()
        self.timerRunning = False
        self.initTimeout(timeout)
        picon = picon or type
        if picon != self.TYPE_ERROR:
            self['ErrorPixmap'].hide()
        if picon != self.TYPE_YESNO:
            self['QuestionPixmap'].hide()
        if picon != self.TYPE_INFO:
            self['InfoPixmap'].hide()
        if picon != self.TYPE_WARNING:
            self['WarningPixmap'].hide()
        self.title = self.type < self.TYPE_MESSAGE and [_('Question'),
         _('Information'),
         _('Warning'),
         _('Error')][self.type] or _('Message')
        if type == self.TYPE_YESNO:
            if list:
                self.list = list
            elif default == True:
                self.list = [(_('Si'), True), (_('No'), False)]
            else:
                self.list = [(_('No'), False), (_('Si'), True)]
        else:
            self.list = []
        self['list'] = MenuList(self.list)
        if self.list:
            self['selectedChoice'].setText(self.list[0][0])
        else:
            self['list'].hide()
        if enable_input:
            self['actions'] = ActionMap(['MsgBoxActions', 'DirectionActions'], {'cancel': self.cancel,
             'ok': self.ok,
             'alwaysOK': self.alwaysOK,
             'up': self.up,
             'down': self.down,
             'left': self.left,
             'right': self.right,
             'upRepeated': self.up,
             'downRepeated': self.down,
             'leftRepeated': self.left,
             'rightRepeated': self.right}, -1)
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle(self.title)

    def initTimeout(self, timeout):
        self.timeout = timeout
        if timeout > 0:
            self.timer = eTimer()
            try:
                self.timer.callback.append(self.timerTick)
            except:
                self.timer_conn = self.timer.timeout.connect(self.timerTick)

            self.onExecBegin.append(self.startTimer)
            self.origTitle = None
            if self.execing:
                self.timerTick()
            else:
                self.onShown.append(self.__onShown)
            self.timerRunning = True
        else:
            self.timerRunning = False
        return

    def __onShown(self):
        self.onShown.remove(self.__onShown)
        self.timerTick()

    def startTimer(self):
        self.timer.start(1000)

    def stopTimer(self):
        if self.timerRunning:
            del self.timer
            self.onExecBegin.remove(self.startTimer)
            self.setTitle(self.origTitle)
            self.timerRunning = False

    def timerTick(self):
        if self.execing:
            self.timeout -= 1
            if self.origTitle is None:
                self.origTitle = self.instance.getTitle()
            self.setTitle(self.origTitle + ' (' + str(self.timeout) + ')')
            if self.timeout == 0:
                self.timer.stop()
                self.timerRunning = False
                self.timeoutCallback()
        return

    def timeoutCallback(self):
        print 'Timeout!'
        if self.timeout_default is not None:
            self.close(self.timeout_default)
        else:
            self.ok()
        return

    def cancel(self):
        self.close(False)

    def ok(self):
        if self.list:
            self.close(self['list'].getCurrent()[1])
        else:
            self.close(True)

    def alwaysOK(self):
        self.close(True)

    def up(self):
        self.move(self['list'].instance.moveUp)

    def down(self):
        self.move(self['list'].instance.moveDown)

    def left(self):
        self.move(self['list'].instance.pageUp)

    def right(self):
        self.move(self['list'].instance.pageDown)

    def move(self, direction):
        if self.close_on_any_key:
            self.close(True)
        self['list'].instance.moveSelection(direction)
        if self.list:
            self['selectedChoice'].setText(self['list'].getCurrent()[0])
        self.stopTimer()

    def __repr__(self):
        return str(type(self)) + '(' + self.text + ')'


# def main(session, **kwargs):
    # session.open(ABOUT)
# def main2(session, **kwargs):
    # session.open(SELECTPLAY)    
# def main3(session, **kwargs):
    # session.open(PICONS)    
    
def main(session, **kwargs):
    if checkInternet():
        session.open(ABOUT)
    else:
        session.open(MessageBox, "No Internet", MessageBox.TYPE_INFO)  
        
def main2(session, **kwargs):
    if checkInternet():
        session.open(SELECTPLAY)
    else:
        session.open(MessageBox, "No Internet", MessageBox.TYPE_INFO)  

def main3(session, **kwargs):
    if checkInternet():
        session.open(PICONS)
    else:
        session.open(MessageBox, "No Internet", MessageBox.TYPE_INFO)  

def mainmenu(session, **kwargs):
    main(session, **kwargs)


def cfgmain(menuid):
    if menuid == 'mainmenu':
        return [('pAnDaSAT fReE iPtV',
          main,
          'iPtV fReE fOr AlL by Lululla',
          44)]
    else:
        return []

def Plugins(**kwargs):
    icona = SKIN_PATH + '/logo.png'
    iconaplayer = SKIN_PATH + '/player.png'
    iconapicons = SKIN_PATH + '/picon.png'
    extDescriptor = PluginDescriptor(name='pAnDaSAT fReE iPtV', description=_('pAnDaSAT fReE iPtV'), where=PluginDescriptor.WHERE_EXTENSIONSMENU, icon=icona, fnc=main)
    mainDescriptor = PluginDescriptor(name='pAnDaSAT fReE iPtV', description=_('pAnDaSAT fReE iPtV v.' + currversion), where=PluginDescriptor.WHERE_MENU, icon=icona, fnc=cfgmain)
    result = [PluginDescriptor(name='pAnDaSAT fReE iPtV', description=_('pAnDaSAT fReE iPtV v.' + currversion), where=[PluginDescriptor.WHERE_PLUGINMENU], icon=icona, fnc=main), PluginDescriptor(name='pAnDaSAT fReE m3u pLaYeR', description='pAnDaSAT fReE m3u pLaYeR v.' + currversion, where=[PluginDescriptor.WHERE_PLUGINMENU], icon=iconaplayer, fnc=main2)] #, PluginDescriptor(name='pAnDaSAT fReE pIcOnS', description='pAnDaSAT fReE pIcOnS', where=[PluginDescriptor.WHERE_PLUGINMENU], icon=iconapicons, fnc=main3)
    if config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.strtext.value:
        result.append(extDescriptor)
    if config.plugins.fReE_iPtV_pAnDa_SaT_tEaM.strtmain.value:
        result.append(mainDescriptor)
    return result
    
#######thanks all friend 
