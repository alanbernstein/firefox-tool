The way I use browser tabs and bookmarks is heavily overloaded. I use them as todo list items, project notes, and link archives. Firefox's tab sync system is nice, but mobile tab management is not great for 10+ tabs, and the desktop bookmarking system is pretty bad for my use cases. This means tabs require a lot of management. This tool is meant to help with that management.

In particular, I keep too many tabs open, because I know that once they get relegated to bookmarks, I am much less likely to see them. In my workflow, tabs and bookmarks are not so much distinct concepts, but rather two points on a [https://firefox-source-docs.mozilla.org/browser/urlbar/ranking.html](frecency) spectrum. If I can access the whole spectrum of URLs with a unified interface, then the distinction between tabs and bookmarks becomes fuzzier. Then, when bookmarks are more useful it should become easier for me to close tabs, and tabs can return to the "working set" which is a better match for their intended usage.

## url frecency spectrum
single tab I'm currently looking at

---- 
stuff that i'm still using today

- pinned tabs like inbox, calendar, todo list
- reminders/notes/capture (ooh I have an idea -> mobile google search -> open one or two results -> eventually take action)
- task tab groups
  - current task
  - several other tasks in my working memory
  - "important" tasks that were interrupted by time-sensitive things

----
 stuff to save for later

- commonly used sites
- references
- random interesting links:
  - to read
  - to watch
  - to learn
  - to do

----
archives

- tab dumps
- project/task/shopping research archives
  - cool ideas
  - blocked ideas
  - abandoned ideas
  - completed ideas
  
---- 
stuff that wasn't worth saving at all (but if I change my mind, it's still there!)
- browser history

# how
long-term: I want to integrate this directly into the browser.

currently:

- render dashboard page on a cron job and serve it statically on my home server
- use [https://addons.mozilla.org/en-US/firefox/addon/custom-new-tab-page/](this extension) to view the dashboard on all new tabs in firefox.

# bookmark UI is broken

## my usage patterns
i have a large number of bookmarks, all saved to my browser toolbar, in a series of folders with bookmarks at depth levels 0 (toolbar), 1 (in a folder), 2. (in a subfolder).

## the ui mechanics (firefox desktop)
the firefox desktop interface for saving them feels completely uncoordinated with the interface for retrieving them from the toolbar.

For saving bookmarks, three options:
1. drag and drop the url bar to the toolbar. if it belongs in a folder, awkwardly navigate the hover-to-open gui to find the right folder. if you make a mistake, you have to start over, costing multiple seconds
2. press ctrl-d, then select the folder by awkwardly navigating the folder tree in a poorly implemented, undersized "filepicker"-like interface
3. press ctrl-d, then add TAGS by typing strings with autocomplete.

For viewing/browsing/retrieving bookmarks:
Visually navigate the toolbar, searching for the correct FOLDER sub tree where you saved the bookmark. note that TAGS are not used for viewing/browsing. even so, this may sound simple, but again it breaks down when the number of bookmarks and size of the directory tree gets large.

for saving, i need to:
1. be able to search, by keyboard, within the directory tree for where to save it.
2. have access to saving by tag more quickly

for retrieving, i need to be able to use tags, via text box (autocomplete fuzzy, full GUI dropdown), inside a first-class UI element on the main UI - perhaps in a text box in the bookmark bar. if it is a separate page, or hidden interface, it's not convenient enough for me to use. a keyboard shortcut might work, but alt-shift-L is a two-finger shortcut, i really want a one-left-hand shortcut - ideally by overriding ctrl-d
I want to use tags, HOWEVER, i don't want to use both folders/categories AND tags. when i save a bookmark, i want to type just 1, 2, maybe 3 DIFFERENT tag strings. i don't want to type a category and then also the same string for a tag. FURTHERMORE, i do like being able to browse bookmarks in a hierarchy. i like to imagine that tags can be automatically organized into the equivalent of a folder/category hierarchy. so i would want the bookmarks toolbar to be based on that.

## firefox mobile
saving: can't even remember how that works - wish i could save all there to a "capture" folder to review later on desktop
retrieving: also don't even remember how to do this

## questions
- am i missing some part of the firefox desktop UI?
- is there any firefox bookmarking extension with an interface that improves on, overrides, or otherwise affects these UI issues? either:
  - override the ctrl-d keyboard shortcut
  - add richer content to the bookmarks toolbar, or the URL bar, or whatever, to add a CLI-like text search component?
- i have a prototype of a better UI, as a webpage. what might be my options for using this, in current form or new form, as the UI within a fierfox extension that i can control?

