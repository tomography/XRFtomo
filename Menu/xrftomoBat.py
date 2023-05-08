'''
*makeBat: Create XRFtomo Batch File*
====================================

This script creates a file named ``XRFtomo.bat`` and a desktop shortcut to that file.
Double-clicking on the shortcut opens XRFtomo.

Run this script with no arguments; the path to the ``xrftomoBat.py`` file
is assumed to be the the same as the path to the ``(xrftomo) __main__.py`` file
and the path to Python is determined from the version of Python
used to run this script. 

'''
from __future__ import division, print_function
import os, sys
import datetime
# import wx

Script = '''@echo ========================================================================
@echo                XRFtomo
@echo ========================================================================
@
{:s}{:s} {:s} {:s}"%~1"
@REM To keep the window from disappearing with any error messages
pause

'''

if __name__ == '__main__':
    try:
        import _winreg as winreg
    except ImportError:
        import winreg

		import xrftomo 
		xrftomo_path = xrftomo.__file__
		pkg_name = xrftomo_path.split(".egg")[0].split("\\")[-1].replace(".","_")
		src_dir = xrftomo_path.split("envs")[0]+"pkgs"+pkg_name+"\\info\\recipe"
		menu_dir = src_dir+"\\Menu\\"
		entry_point = os.popen("which xrftomo")
		entry_point = entry_point.read().split("\n")[0]


		app = None # delay starting wx until we need it. Likely not needed.
		#scriptpath = os.path.split(sys.argv[0])[0]
		# current_path = os.path.abspath(os.path.expanduser("menu_installer.py"))
		# print("this is the path", current_path)
		print("this is the path", src_dir)
		# scriptpath = "\\".join(current_path.split("\\")[:-1])+"\\"
		scriptpath = src_dir+"\\xrftomo\\"
		print("this is the scrpt path", scriptpath)

		#if no path specified: "", scriptpath="."
		# scriptpath = os.path.abspath(os.path.expanduser(scriptpath))        #scriptpath = =current path
		XRFscript = os.path.join(scriptpath,'__main__.py')                   #assuming path is where script is
		XRFbat = os.path.join(scriptpath,'RunXRFtomo.bat')                   #place bat alongside xrftomo ?
		# XRFicon = os.path.join(scriptpath,'xrftomo.ico')                     #place xrftomo.ico alongisde xrftomo.py ?
		XRFicon = os.path.join(menu_dir,'xrftomo.ico')                     #place xrftomo.ico alongisde xrftomo.py ?
		pythonexe = os.path.realpath(sys.executable)                        #python path, automatically detects python path
		print('Python installed at',pythonexe)
		# print('xrftomo installed at',scriptpath)
		print('xrftomo installed at',entry_point)
		# Bob reports a problem using pythonw.exe w/Canopy on Windows, so change that if used
		if pythonexe.lower().endswith('pythonw.exe'):
			print("  using python.exe rather than "+pythonexe)
			pythonexe = os.path.join(os.path.split(pythonexe)[0],'python.exe')
			print("  now pythonexe="+pythonexe)


    # create a xrftomo script
    fp = open(os.path.join(XRFbat),'w')
    fp.write("@REM created by run of bootstrap.py on {:%d %b %Y %H:%M}\n".format(datetime.datetime.now()))
    activate = os.path.join(os.path.split(pythonexe)[0],'Scripts','activate')
    print("Looking for",activate)
    if os.path.exists(activate):
        activate = os.path.realpath(activate)
        if ' ' in activate:
            activate = 'call "'+ activate + '"\n'
        else:
            activate = 'call '+ activate + '\n'
        print('adding activate to .bat file ({})'.format(activate))
    else:
        print('Anaconda activate not found')
        activate = ''
    pexe = pythonexe
    if ' ' in pythonexe: 
        pexe = '"'+pythonexe+'"'
    XRFs = XRFscript
    if ' ' in XRFs: 
        XRFs = '"'+XRFscript+'"'

    args = 'gui'
    fp.write(Script.format(activate,pexe,XRFs,args))
    fp.close()
    print('\nCreated xrftomo batch file xrftomo.bat in '+scriptpath)
    
    new = False
    oldBat = ''
    try:
        FileNotFoundError
    except NameError:
        FileNotFoundError = Exception
        
    try:
        import win32com.shell.shell, win32com.shell.shellcon, win32com.client
        desktop = win32com.shell.shell.SHGetFolderPath(
            0, win32com.shell.shellcon.CSIDL_DESKTOP, None, 0)
        shortbase = "xrftomo.lnk"
        shortcut = os.path.join(desktop, shortbase)
        save = True

        if save:
            shell = win32com.client.Dispatch('WScript.Shell')
            shobj = shell.CreateShortCut(shortcut)
            shobj.Targetpath = XRFbat
            #shobj.WorkingDirectory = wDir # could specify a default project location here
            shobj.IconLocation = XRFicon
            shobj.save()
            print('Created shortcut to start xrftomo on desktop')
        else:
            print('No shortcut for this xrftomo created on desktop')

    except ImportError:
        print('Module pywin32 not present, will not make desktop shortcut')
    except:
        print('Unexpected error making desktop shortcut. Please report:')
        import traceback
        print(traceback.format_exc())