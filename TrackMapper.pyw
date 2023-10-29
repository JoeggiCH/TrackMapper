"""
schweizmobil.ch is a service to discover and plan (mostly) hiking/biking tracks in Switzerland. Viewing tracks does not require a paid subscription, drawing own tracks does. The schweizmobil.ch UI is great but unfortunately can only show one of the user-created tracks at a time. I have 300+ tracks and struggle to keep the overview of what I planned/did in a given region.

So, this project ..

- uses the schweizmobil.ch API described at https://github.com/JoeggiCH/schweizmobil.ch-API to download all tracks of a given user (with a paid subscription)
- allows users to filter tracks based on a number of criteria, such as the hike/bike length in kilometers, duration, meters uphill etc
- converts tracks into WGS84 coordinates and a GeoJSON FeatureCollection
- renders the FeatureCollection in a browser-viewable map (using python folium and leaflet.js)

"""
import PySimpleGUI as sg
from datetime import datetime
import ImportSchweizmobil as IS
import webbrowser
import PrepareMap as PM
import os
from os.path import isfile, isdir, expanduser
import sys
import encryption as en
import json

debug=0

def showFilter(fparam):

    limits=fparam

    tsize=(22, 1)
    insize=(12,1)

    layout = [
                [
                sg.Text('Min Duration [mins]', size=tsize), sg.InputText(limits["MinDuration"],size=insize),
                sg.Text('Max Duration [mins]', size=tsize), sg.InputText(limits["MaxDuration"],size=insize),
                ],
                [
                sg.Text('Min length [km]', size=tsize), sg.InputText(limits["MinLength"],size=insize),
                sg.Text('Max length [km]', size=tsize), sg.InputText(limits["MaxLength"],size=insize),
                ],
                [
                sg.Text('Min meters uphill', size=tsize), sg.InputText(limits["MinUp"],size=insize),
                sg.Text('Max meters uphill', size=tsize), sg.InputText(limits["MaxUp"],size=insize),
                ],
                [
                sg.Text('Track name includes', size=tsize), sg.InputText(limits["Nincludes"],size=insize),
                sg.Text('Track name excludes', size=tsize), sg.InputText(limits["Nexcludes"],size=insize),
                ],
                [
                sg.Text('Min Longitude', size=tsize), sg.InputText(limits["MinLon"],size=insize),
                sg.Text('Max Longitude', size=tsize), sg.InputText(limits["MaxLon"],size=insize),
                ],
                [
                sg.Text('Min Latitude', size=tsize), sg.InputText(limits["MinLat"],size=insize),
                sg.Text('Max Latitude', size=tsize), sg.InputText(limits["MaxLat"],size=insize),
                ],
                [
                sg.Text("Min mod'd date [dd/mm/yyyy]", size=tsize), sg.InputText(limits["MinMdate"],size=insize),
                sg.Text("Max mod'd date [dd/mm/yyyy]", size=tsize), sg.InputText(limits["MaxMdate"],size=insize),
                ],
                [                        
                sg.Text('Min User Date', size=tsize), sg.InputText(limits["MinUdate"],size=insize),
                sg.Text('Max User Date', size=tsize), sg.InputText(limits["MaxMdate"],size=insize),
                ],
                [
                sg.Text('Track id', size=tsize), sg.InputText(limits["id"],size=insize),
                ],
                [
                sg.Text('Hike', size=tsize), sg.Checkbox("",default=limits["hike"],size=insize),
                ],
                [
                sg.Text('Bike', size=tsize), sg.Checkbox("",default=limits["bike"],size=insize),
                               
                sg.Push(),sg.Button('Set Filter',key="Close")]]
    try:
        window = sg.Window('Filter schweizmobil.ch tracks',
            layout,  default_button_element_size=(4,2),
            use_default_focus=False,finalize=True)
        window.bind('<Return>', '+RETURN+')
        #window['Close'].set_tooltip(' Keyboard Shortcut: Return ')
    except:
        print ("Failed to initialize window"); sys.exit()

    # The SimpleGUI event loop
    while True:
        event, v = window.read()

        # return filter unmodified, if window X was clicked
        if (event ==sg.WIN_CLOSED):            
            return limits

        try:
            result={"MinDuration":float(v[0]),  "MaxDuration":float(v[1]),
                "MinLength":float(v[2]),        "MaxLength":float(v[3]),
                "MinUp":float(v[4]),            "MaxUp":float(v[5]),
                "Nincludes":v[6],               "Nexcludes":v[7],
                "MinLon":float(v[8]),           "MaxLon":float(v[9]),
                "MinLat":float(v[10]),          "MaxLat":float(v[11]),
                "MinMdate":v[12],               "MaxMdate":v[13],
                "MinUdate":v[14],               "MaxUdate":v[15],
                "id":v[16],
                "hike":v[17],
                "bike":v[18]
                }
            test=datetime.strptime(v[12],'%d/%m/%Y')
            test=datetime.strptime(v[13],'%d/%m/%Y')
            test=datetime.strptime(v[14],'%d/%m/%Y')
            test=datetime.strptime(v[15],'%d/%m/%Y')
        except:
            sg.popup_ok('invalid input!')
            continue
        
        if debug>=1: print (f"Event {event} {result}")

        if event=="Close" or event=="+RETURN+":
            window.close()
            return result

def showSettings():
   
    tsize=(10, 1)
    insize=(28,1)

##    datafolder=[[sg.Button ('Select',key='folder'),sg.multiline(default_text=settings['data_path'],
##                    auto_size_text=True,write_only=True,k="ML",reroute_cprint=True,do_not_clear=False)]]

    datafolder=[[sg.Button ('Select',key='folder'),sg.Text(settings['data_path'],
                    auto_size_text=True,k="Txt")]]

    smcred=[[
                sg.Text('username', size=tsize), sg.InputText(settings['sm_username'],size=insize),
                sg.Text('password', size=tsize), sg.InputText(settings['sm_password'],size=insize)
                ]]

    layout = [
                [sg.Frame ("TrackMapper Data Folder",datafolder,expand_x=True)],
                [sg.Frame ("schweizmobil.ch credentials",smcred,expand_x=True)],
                [sg.Button('Change Settings Password', key='pass'),sg.Push(),
                 sg.Button('Apply Settings', key='apply')]]
                 
    try:
        window = sg.Window('Settings',
            layout,  default_button_element_size=(5,2),
            use_default_focus=False,finalize=True,modal=True)        
    except:
        print ("Failed to initialize window"); sys.exit()

    global passw
    npw=passw
    nfolder=settings['data_path']
    
    # The SimpleGUI event Loop
    while True:
        event, v = window.read()

        if (debug>0): print (e,v)
        
        # return filter unmodified, if window X was clicked
        if (event ==sg.WIN_CLOSED):
            DoSettings()
            return

        if (event=="folder"):
            folder=sg.popup_get_folder('Choose your folder', keep_on_top=True,
                default_path=nfolder,initial_folder=nfolder)
            if folder:
                nfolder=folder+'/'
                window['Txt'].Update(nfolder)

        if (event=="pass"):
            p = sg.popup_get_text('Enter password to decrypt settings: ',
                title="Password",default_text=npw,password_char="*")
            if p: npw=p

        if (event=="apply"):
            settings['sm_username']=v[0]
            settings['sm_password']=v[1]
            settings['data_path']=nfolder
            passw=npw
            en.wr_enc_dict(npw, SettingsFolder+'trackmapper.conf', settings)
            DoSettings()
            window.close()

def DoSettings():
    #assuming write perms
    if not isdir(settings['data_path']):
        os.mkdir(settings['data_path'])

    if not isdir(settings['data_path']+'cache'):
        os.mkdir(settings['data_path']+'cache')

    if not isdir(settings['data_path']+'cache/schweizmobil.ch/'):
        os.mkdir(settings['data_path']+'cache/schweizmobil.ch/')

    if not isdir(settings['data_path']+'GeoJSON'):
        os.mkdir(settings['data_path']+'GeoJSON')

    if not isdir(settings['data_path']+'html'):
        os.mkdir(settings['data_path']+'html')

    # derive the module settings from the main settings    
    IS.outfp  =settings['data_path']
    IS.creds = json.dumps({
                    "username": settings['sm_username'],
                    "password": settings['sm_password']
                })
    PM.infile =settings['data_path']+'GeoJSON/schweizmobil.GeoJSON'
    PM.outfile=settings['data_path']+'html/map.html'

    # those are currently not part of the main settings:
    IS.debug=1
    IS.opo=2


def showMain():

    tsize=(22, 1)
    insize=(12,1)

    frame1=[
        [sg.Button('Filter',key="FilterSM"),sg.Text("  =>  "),
         sg.Button('Fetch',key="FetchSM"),sg.Text("  =>  "),
         sg.Button('Publish',key="Publish")],
        [sg.Radio("Bounding Box",group_id='opo'),
         sg.Radio("Vias",group_id='opo'),
         sg.Radio("Detailed tracks",group_id='opo',default=True)]]

    frame2=[
        [sg.Button('Local',key="WriteLocal"),
        sg.Button('Local & Web',key="WriteWeb")]]

    frame3=[
        [sg.Button('Local',key="OpenLocal"),
         sg.Button('Web',key="OpenWeb")]]


    layout = [
        [sg.Frame ("schweizmobil.ch",frame1,expand_x=True)],
        [sg.Frame ("Open Map in browser",frame3,expand_x=True)],
        [sg.Output(size=(80, 10))],   
        [sg.Button('Settings',key='set'),sg.Push(),sg.Button('Exit',key="Exit")]]
    
    try:
        window = sg.Window('Show Tracks',
            layout,  default_button_element_size=(4,2),
            use_default_focus=False,finalize=True)
    except:
        print ("Failed to initialize window"); sys.exit()

    # The SimpleGUI event Loop
    while True:
        event, v = window.read()

        if debug>=1: print (f"Event {event}")
        
        if (event ==sg.WIN_CLOSED):            
            break

        if v[0]: IS.opo=0
        if v[1]: IS.opo=1
        if v[2]: IS.opo=2

        if event=="FilterSM":
            IS.Filter=showFilter(IS.Filter)
            continue

        if event=="FetchSM":
            IS.Import_Schweizmobil()
            PM.Prepare_Map()
            continue

        if event=="Publish":
            os.chdir(IS.outfp)
            script_dir = os.path.abspath( os.path.dirname( __file__ ) )
            winpath=IS.outfp.replace("/","\\")           
            cmd=f"\"\"{script_dir}\\update web.bat\" \"{winpath}\" >>\"{winpath}update web.log\"\""
            if debug>0: print (cmd)
            os.system(cmd)

            continue
        
        if event=="OpenLocal":
            webbrowser.open('file://' + os.path.realpath(PM.outfile))
            continue

        if event=="OpenWeb":
            webbrowser.open('https://joeggich.github.io/map.html')
            continue

        if event=="set":
            showSettings()
            continue

        if event=="Exit":
            window.close()
            break

    
# --------------------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------------------

# platform dependent defaults
# SettingsFolder is not user-configurable
# DataFolder is user-configurable
if sys.platform=="win32":
    #on Windows
    SettingsFolder=expanduser('~').replace("\\","/")+"/AppData/Local/TrackMapper/"
    DataFolder=expanduser('~').replace("\\","/")+'/Documents/TrackMapper/'
else:
    #unix assumed
    SettingsFolder=expanduser('~')+"/.TrackMapper/"
    DataFolder=expanduser('~')+"/TrackMapper/"

settings = {
          "sm_username": "",
          "sm_password": "",
          "data_path": DataFolder
        }

passw=""
sg.theme("SystemDefaultForReal")

if not isdir(SettingsFolder):
    # first time startup!
    os.mkdir(SettingsFolder)

try:
    if isfile(SettingsFolder+'trackmapper.conf'):
        #decrypt file
        p = sg.popup_get_text('Enter password to decrypt settings: ',
            title="Password",password_char="*")
        if p: passw=p
        else: passw="default"
        
        #read settings file and decrypt
        nsettings=en.rd_dec_dict(passw,SettingsFolder+'trackmapper.conf')
        if nsettings:
            settings=nsettings
            DoSettings()
        else:
            raise Exception ("wrong password; defaulting settings")
    else:
        raise Exception ("no trackmapper.conf file found")
except Exception as e:
    # no valid settings available, so let's ask the user
    print (e)
    passw='default'
    showSettings()

showMain()
