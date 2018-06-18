# ABOUT

These are Python scripts for use with the [Glyphs font editor](http://glyphsapp.com/).


# INSTALLATION

Put the scripts into the *Scripts* folder which appears when you choose *Open Scripts Folder* from the *Scripts* menu.
(the path is ~/Library/Application Support/Glyphs/Scripts/).
We recommend you create a dedicated subfolder called SIL and put these scripts in there to help you distinguish them from any other scripts.

# USAGE
In Glyphs, hold Alt and go to Scripts->Reload Scripts. (New scripts are also picked up when your restart Glyphs). The various scripts then appear in submenus under Scripts. Scripts from this repository should ideally be in dedicated SIL subfolder.



# SCRIPTS

## LoadUFOFamily.py
Loads a family of UFOs. Choose the Regular face and all others in the same folder will loaded. Requires that files be named in __FontFamilyName-StyleName.ufo__ format. See recommendations in [Font Development Best Practices](http://silnrsi.github.io/FDBP/en-US/Font_Naming.html). At the moment, if 'Use Versions' is checked in Glyphs > Preferences > User Settings you will get error messages. Temporary solution is to turn off that feature.

## update-preflight-libraries-from-releases.py
Help you keep you preflight dependencies up to date more easily directly from Glyphs.

## run-preflightg.py
Helps you run your preflightg script directly from Glyphs.


Some scripts require other python modules.

# LICENSE

Copyright (c) 2018, SIL International (http://www.sil.org)
Released under the [MIT license](LICENSE)

