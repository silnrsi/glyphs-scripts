#MenuTitle: Update the preflight libraries from releases
# -*- coding: utf-8 -*-
__doc__="""
Update the preflight libraries from releases
"""

__copyright__ = 'Copyright (c) 2018, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Nicolas Spalinger'

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

			do script "sudo -H  /usr/local/bin/pip install --no-warn-script-location --disable-pip-version-check --upgrade --user git+https://github.com/silnrsi/pysilfont.git@v1.3.0#egg=pysilfont git+https://github.com/googlei18n/GlyphsLib.git@v2.2.1#egg=glyphsLib fontTools MutatorMath ufoLib defcon fontMath git+https://github.com/LettError/DesignSpaceDocument.git@master#egg=DesignSpaceDocument ;  pip list --format=columns --disable-pip-version-check --user "

		end tell

	end tell

end tell

tell application "Finder"
	display notification "Updating your preflight dependencies, please enter your user password. The version numbers of the libraries will be indicated in the output. Watch for errors in the output, when done you can close the window" with title "Preflight dependencies update" sound name "default"
end tell


"""

save   = runAppleScript( preflightupdate )
