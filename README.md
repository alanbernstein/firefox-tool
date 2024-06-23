# what
a small CLI tool to read some of your firefox user data, and output it as usable lines of text. works on mac and linux

# why
The way I use browser tabs and bookmarks is heavily overloaded. I use them as todo list items, project notes, and link archives. Firefox's tab sync system is nice, but mobile tab management is not great for 10+ tabs, and the bookmarking system is pretty bad for my use cases. This means tabs require a lot of management. This tool is meant to help with that management.

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


## examples
```
# list synced tabs on device with "pixel" in the name, filter for titls/urls including "ycomb"

$ ff synced pixel | grep -i ycomb
[Language is primarily a tool for communication rather than thought [pdf] | Hacker News](https://news.ycombinator.com/item?id=40756176) (0 days)
[Immersive Linear Algebra (2015) | Hacker News](https://news.ycombinator.com/item?id=40329388) (3 days)
[Indian Startup 3D Prints Rocket Engine in Just 72 Hours | Hacker News](https://news.ycombinator.com/item?id=40668088) (9 days)
[NoTunes is a macOS application that will prevent Apple Music from launching | Hacker News](https://news.ycombinator.com/item?id=40426621) (16 days)
[CADmium: A Local-First CAD Program Built for the Browser | Hacker News](https://news.ycombinator.com/item?id=40428827) (32 days)
```

This output can be copied into a markdown file for grouping, archiving, etc.
