# what
A small tool to read some of your web browser user data, and present it for read-only access with a better UX than the existing tab/bookmark manager built into the browser. It has a CLI component and a (simple) webpage component. Works for Firefox on Mac and Linux.

# why
The way I use browser tabs and bookmarks is heavily overloaded. I use them as todo list items, project notes, and link archives. Firefox's tab sync system is nice, but mobile tab management is not great for 10+ tabs, and the desktop bookmarking system is pretty bad for my use cases. This means tabs require a lot of management. This tool is meant to help with that management.

In particular, I keep too many tabs open, because I know that once they get relegated to bookmarks, I am much less likely to see them. In my workflow, tabs and bookmarks are not so much distinct concepts, but rather two points on a [https://firefox-source-docs.mozilla.org/browser/urlbar/ranking.html](frecency) spectrum. If I can access the whole spectrum of URLs with a unified interface, then the distinction between tabs and bookmarks becomes fuzzier. Then, when bookmarks are more useful it should become easier for me to close tabs, and tabs can return to the "working set" which is a better match for their intended usage.

## url frecency spectrum
- single tab I'm currently looking at
----------------------------------------------------------------------------------- stuff that i'm still using today
- pinned tabs like inbox, calendar, todo list
- reminders/notes/capture (ooh I have an idea -> mobile google search -> open one or two results -> eventually take action)
- task tab groups
  - current task
  - several other tasks in my working memory
  - "important" tasks that were interrupted by time-sensitive things
  --------------------------------------------------------------------------------- stuff to save for later
- commonly used sites
- references
- random interesting links:
  - to read
  - to watch
  - to learn
  - to do
------------------------------------------------------------------------------------ archives
- tab dumps
- project/task/shopping research archives
  - cool ideas
  - blocked ideas
  - abandoned ideas
  - completed ideas
------------------------------------------------------------------------------------- stuff that wasn't worth saving at all
- browser history

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
ff render                             # create ff-dashboard.html, with interactive multi-search (WIP)
ff search pattern                     # run a single CLI search similar to the dashboard search (WIP)
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
