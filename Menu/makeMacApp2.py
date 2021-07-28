#!/usr/bin/env python
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
from __future__ import division, print_function
import sys, os, os.path, stat, shutil, subprocess, plistlib
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

AppleScript = ''
'''Contains an AppleScript to start xrftomo, launching Python and the
xrftomo python script
'''

if __name__ == '__main__':
    project="xrftomo"
    tmp_script_path = "/Users/fabriciomarin/conda/XRFtomo/xrftomo/__main__.py"
    script = tmp_script_path


    # set scriptdir: find the main xrftomo script if not on command line
#TMP comment  
    # if len(sys.argv) == 1:
    #     script = os.path.abspath(os.path.join(
    #             os.path.split(__file__)[0],
    #             "__main__.py"
    #             ))
    # elif len(sys.argv) == 2:
    #         script = os.path.abspath(sys.argv[1])
    # else:
    #     Usage()
    #     raise Exception
    # make sure we found it
#TMP comment

    # if not os.path.exists(script):
    #     print("\nFile "+script+" not found")
    #     Usage()
    # if os.path.splitext(script)[1].lower() != '.py':
    #     print("\nScript "+script+" does not have extension .py")
    #     Usage()

# where the app will be created
    py_env = os.environ['CONDA_DEFAULT_ENV']
    scriptdir = os.path.split(script)[0]
    appPath = os.path.abspath(os.path.join(scriptdir,project+".app"))
    iconfile = "/Users/fabriciomarin/conda/XRFtomo/xrftomo/xrftomo.icns"
    env  = "source activate {}; ".format(py_env)
    # iconfile = os.path.join(scriptdir,'tmp.icns') # optional icon file
    
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
	set python to "{:s}"
	set appwithpath to "{:s}"
	set env to "{:s}"
	TestFilePresent(appwithpath)
	TestFilePresent(python)
	tell application "Terminal"
		activate
		do script env & python & " " & appwithpath & " gui" &""
	end tell
end run
'''
    
# create a link named xrftomo.py to the script
    newScript = os.path.join(scriptdir,project+'.py')
    if os.path.exists(newScript): # cleanup
        print("\nRemoving sym link",newScript)
        os.remove(newScript)
    os.symlink(os.path.split(script)[1],newScript)
    script=newScript

# find Python used to run xrftomo and set a new to use to call it inside the app that will be created
    pythonExe = os.path.realpath(sys.executable)
    newpython = os.path.join(appPath,"Contents","MacOS",project)
    if pythonExe.split("/")[-1] == "python3.6":
        pythonExe = "/".join(pythonExe.split("/")[:-1])+"/python"

    if os.path.exists(appPath): # cleanup
        print("\nRemoving old "+project+" app ("+str(appPath)+")")
        shutil.rmtree(appPath)
        
    shell = os.path.join("/tmp/","appscrpt.script")
    f = open(shell, "w")
    # f.write(AppleScript.format(newpython,script,env))
    f.write(AppleScript.format("source activate {}; xrftomo gui".format(py_env),"",""))
    f.close()

    try:
        subprocess.check_output(["osacompile","-o",appPath,shell],stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as msg:
        sys.exit()
# create a link to the python inside the app, if named to match the project
    if pythonExe != newpython:
        os.symlink(pythonExe,newpython)

# change the icon
    oldicon = os.path.join(appPath,"Contents","Resources","applet.icns")
    if os.path.exists(iconfile):
        shutil.copyfile(iconfile,oldicon)

    print("\nCreated "+project+" app ("+str(appPath)+").\nViewing app in Finder so you can drag it to the dock if, you wish.")
    subprocess.call(["open","-R",appPath])
