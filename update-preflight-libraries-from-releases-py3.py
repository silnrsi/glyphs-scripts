#MenuTitle: Update the preflight libraries from releases (pysilfont from master) py3
# -*- coding: utf-8 -*-
__doc__="""
Update the preflight libraries from releases (pysilfont from master) py3
"""

__copyright__ = 'Copyright (c) 2018, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Nicolas Spalinger'

# if you installed pip via get-pip.py then you need to make the following configuration changes:
# we're targetting the following user folder for installation /Users/nameofyouruser/Library/Python/3.*/lib/python/site-packages
# and the scripts go to /Users/nameofyouruser/Library/Python/3.*/bin/ so this will need to be in your path
# if not add export PATH=~/Library/Python/3.*/bin:$PATH to your ~/.bash_profile
#
# if you installed (or updated) pip via brew (from brew.sh) then it will use /usr/local instead
# and so you don't have to change path configurations or add launchers manually. 

# note that this script tries to uninstall any previously installed libraries (which might be in other paths throughout the system)


import GlyphsApp
from subprocess import Popen, PIPE


def runAppleScript(scpt, args=[]):
	p = Popen(['osascript', '-'] + args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate(scpt)
	if stderr:
		print "AppleScript Error:"
		print stderr.decode('utf-8')
	return stdout


preflightupdate = """

tell application "Finder"

	tell application "Terminal"

		activate

		tell window 1

	        	do script "which python3; python3 --version; python3 -m pip --version; sudo python3 -m pip uninstall --yes pysilfont glyphsLib fontTools mutatorMath ufoLib defcon fontMath designSpaceDocument; python3 -m pip install --upgrade --user --no-cache-dir --no-warn-script-location git+https://github.com/silnrsi/pysilfont.git@master#egg=pysilfont git+https://github.com/googlei18n/GlyphsLib.git@v2.4.0#egg=glyphsLib fontTools mutatorMath ufoLib git+https://github.com/typesupply/defcon.git@0.3.5#egg=defcon fontMath git+https://github.com/LettError/designSpaceDocument.git@master#egg=designSpaceDocument ;  python3 -m pip list --format=columns --user"

		end tell

	end tell

end tell

tell application "Finder"
	display notification "Updating, enter your password." with title "Preflight dependencies" sound name "default"
end tell

tell application "Finder"
	display notification "Libraries versions: see output" with title "Preflight dependencies versions"
end tell

tell application "Finder"
	display notification "Watch for issues, when done close the window" with title "Installation issues"
end tell



"""

save   = runAppleScript( preflightupdate )
