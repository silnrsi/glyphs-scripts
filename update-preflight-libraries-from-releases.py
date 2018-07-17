#MenuTitle: Update the preflight libraries from releases
# -*- coding: utf-8 -*-
__doc__="""
Update the preflight libraries from releases
"""

__copyright__ = 'Copyright (c) 2018, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Nicolas Spalinger'

# we are targetting the following user folder for installation /Users/nameofyouruser/Library/Python/2.7/lib/python/site-packages

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

			do script "cd /tmp; sudo pip install --upgrade --user --no-cache-dir git+https://github.com/silnrsi/pysilfont.git@master#egg=pysilfont git+https://github.com/googlei18n/GlyphsLib.git@v2.4.0#egg=glyphsLib fontTools MutatorMath ufoLib defcon fontMath git+https://github.com/LettError/designSpaceDocument.git@master#egg=designSpaceDocument ;  pip list --format=columns --user"

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
	display notification "Watch for errors, when done close the window" with title "Installation errors"
end tell



"""

save   = runAppleScript( preflightupdate )
