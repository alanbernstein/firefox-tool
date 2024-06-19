# what
a small CLI tool to read some of your firefox user data, and output it as usable lines of text. works on mac and linux

# setup
roughly:
```
cd your-repo-folder
git clone git@github.com:alanbernstein/firefox-tool.git
pip install -r requirements.txt

# suggested terse command line alias and/or symlink `ff`
cd your-command-folder
ln -s your-repo-folder/firefox-tool/firefox-tool.py ff
```

# usage
```
ff tabs                               # print all tabs open on current device, one per line, in markdown syntax
ff tabs-history                       # print all tabs including browser history for each one
ff tabs-synced [device-name-pattern]  # print all tabs on other devices connected to firefox sync, in markdown syntax
ff bookmarks                          # print all bookmarks (needs some work)
ff profile-path                       # print the profile directory
```
