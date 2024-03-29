from __future__ import division, print_function
import sys, os, os.path, stat, shutil, subprocess, plistlib
from os.path import expanduser
plat = sys.platform


def Usage():
	print("\n\tUsage: python "+sys.argv[0]+" [<xrftomo script>]\n")
	sys.exit()

def RunPython(image,cmd):
	'Run a command in a python image'
	try:
		err=None
		p = subprocess.Popen([image,'-c',cmd],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		out = p.stdout.read()
		err = p.stderr.read()
		p.communicate()
		return out,err
	except Exception(err):
		return '','Exception = '+err

def install_menu():
	import os
	import sys
	if plat == "darwin":
		'''
		*makeMacApp: Create Mac Applet*
		===============================

		This script creates an AppleScript app bundle to launch xrftomo. The app is
		created in the directory where the xrftomo script (__main__.py) is located.
		A softlink to Python is created, but is named xrftomo, and placed inside
		the bundle so that xrftomo shows up as the name of the app rather than 
		Python in the menu bar, etc. A soft link named xrftomo.py, referencing 
		XRFT.py, is created so that appropriate menu items also are labeled with 
		xrftomo (but not the right capitalization, alas). 

		This has been tested with several versions of Python interpreters 
		from Anaconda and does not require pythonw (Python.app). It tests to 
		make sure that a wx python script will run inside Python and if not, 
		it searches for a pythonw image and tries that. 

		Run this script with no arguments or with one optional argument, 
		a reference to the XRFT.py, with a relative or absolute path. Either way 
		the path will be converted via an absolute path. If no arguments are 
		supplied, the XRFT.py script must be located in the same directory as 
		this file.

		'''
		AppleScript = ''
		'''Contains an AppleScript to start xrftomo, launching Python and the
		xrftomo python script
		'''

		project="xrftomo"
		scriptdir =  "/".join(os.path.abspath(project+".__file__").split("/")[:-1])+"/"
		script_path = scriptdir+"__main__.py"

		# where the app will be created
		appPath = os.path.abspath(os.path.join(scriptdir,project+".app"))
		py_env = os.environ['CONDA_DEFAULT_ENV']
		env = "source activate {}; ".format(py_env)

		AppleScript = '''(*   xrftomo AppleScript by Fabricio S.Marin (marinf@anl.gov)
		It can launch xrftomo by double clicking 
		It runs xrftomo in a terminal window.
		*)

		(* test if a file is present and exit with an error message if it is not  *)
		on TestFilePresent(appwithpath)
			tell application "System Events"
				if (file appwithpath exists) then
				else
					display dialog "Error: file " & appwithpath & " not found. If you have moved this file recreate the AppleScript with bootstrap.py." with icon caution buttons {{"Quit"}}
					return
				end if
			end tell
		end TestFilePresent

		(* 
		------------------------------------------------------------------------
		this section responds to a double-click. No file is supplied to xrftomo
		------------------------------------------------------------------------ 
		*)
		on run
			set env to "{:s}"
			set program to "{:s}"
			tell application "Terminal"
				activate
				do script env & program
			end tell
		end run
		'''

		if os.path.exists(appPath): # cleanup
			print("\nRemoving old "+project+" app ("+str(appPath)+")")
			shutil.rmtree(appPath)

		shell = os.path.join("/tmp/","appscrpt.script")
		f = open(shell, "w")
		f.write(AppleScript.format(env, "xrftomo gui"))
		f.close()

		try:
			subprocess.check_output(["osacompile","-o",appPath,shell],stderr=subprocess.STDOUT)
		except subprocess.CalledProcessError as msg:
			sys.exit()

		# find Python used to run xrftomo and set a new to use to call it inside the app that will be created
		pythonExe = os.path.realpath(sys.executable)
		newpython = os.path.join(appPath,"Contents","MacOS",project)
		if pythonExe.split("/")[-1] == "python3.6":
			pythonExe = "/".join(pythonExe.split("/")[:-1])+"/python"
		if pythonExe.split("/")[-1] == "python3.7":
			pythonExe = "/".join(pythonExe.split("/")[:-1])+"/python"
		if pythonExe.split("/")[-1] == "python3.9":
			pythonExe = "/".join(pythonExe.split("/")[:-1])+"/python"
		# create a link to the python inside the app, if named to match the project
		if pythonExe != newpython:
			os.symlink(pythonExe,newpython)

		# # change the icon !! IOS catalina wont change icon for some reason.
		# iconfile = scriptdir+"xrftomo.icns"
		# oldicon = os.path.join(appPath,"Contents","Resources","applet.icns")
		# if os.path.exists(iconfile):
		# 	shutil.copyfile(iconfile,oldicon)
		

		print("\nCreated "+project+" app ("+str(appPath)+").\nViewing app in Finder so you can drag it to the dock if, you wish.")
		subprocess.call(["open","-R",appPath])


	elif plat == "win32" or plat == "windows":

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
		import os, sys
		import datetime
		# import wx

		Script = '''@echo ========================================================================
		@echo                XRFtomo
		@echo ========================================================================
		@
		{:s} & {:s} {:s} {:s}"%~1"
		@REM To keep the window from disappearing with any error messages
		pause

		'''

		try:
			import _winreg as winreg
		except ImportError:
			import winreg
		import xrftomo 
		import platform
		py_version = ("").join(platform.python_version().split(".")[:2])
		package_version = xrftomo.__version__
		xrftomo_path = xrftomo.__file__
		home_dir = os.path.expanduser('~')
		go_home = os.system("cd {}".format(home_dir))

		if "egg" in xrftomo_path:
			pkg_name = xrftomo_path.split(".egg")[0].split("\\")[-1].replace(".","_")
			src_dir = xrftomo_path.split("envs")[0]+"pkgs\\"+pkg_name+"\\info\\recipe"
			menu_dir = os.path.join(src_dir,"Menu")
			entry_point = os.popen("where xrftomo")
			entry_point = entry_point.read().split("\n")[0]

		else:
			src_files = xrftomo_path.split("envs")[0]+"pkgs\\"
			src_files = os.listdir(src_files)
			src_files = list(filter(lambda k: 'xrftomo' in k, src_files))
			src_files = list(filter(lambda k: 'tar' not in k, src_files))
			src_files = list(filter(lambda k: py_version in k, src_files))
			src_files = list(filter(lambda k: package_version in k, src_files))

			if len(src_files)>1:
				print("number of possible source directories are greater than 1. Selecting the first one, hope for the best.")
 
			pkg_name = src_files[0]
			src_dir = xrftomo_path.split("envs")[0]+"pkgs\\"+pkg_name+"\\info\\recipe"
			menu_dir = os.path.join(src_dir,"Menu")
			entry_point = os.popen("where xrftomo")
			entry_point = entry_point.read().split("\n")[0]
			print(entry_point)

		app = None # delay starting wx until we need it. Likely not needed.
		#scriptpath = os.path.split(sys.argv[0])[0]
		# current_path = os.path.abspath(os.path.expanduser("menu_installer.py"))
		# print("this is the path", current_path)
		print("this is the path", src_dir)
		# scriptpath = "\\".join(current_path.split("\\")[:-1])+"\\"
		scriptpath = os.path.join(src_dir,"xrftomo")
		print("this is the script path", scriptpath)

		#if no path specified: "", scriptpath="."
		# scriptpath = os.path.abspath(os.path.expanduser(scriptpath))        #scriptpath = =current path
		XRFscript = os.path.join(scriptpath,"__main__.py")                #assuming path is where script is
		XRFbat = os.path.join(scriptpath,"RunXRFtomo.bat")
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
			try:
				AnacondaPathIndx = os.path.split(pythonexe)[0].split("\\").index("Anaconda3")
			except ValueError:
				try:
					AnacondaPathIndx = os.path.split(pythonexe)[0].split("\\").index("anaconda3")
				except ValueError:
					print("could not find Anaconda activate script")
			py_env = os.environ['CONDA_DEFAULT_ENV']
			activate = "\\".join(os.path.split(pythonexe)[0].split("\\")[:AnacondaPathIndx+1])+"\\Scripts\\activate {}".format(py_env)
			print("set activate path to {}".format(activate))
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
