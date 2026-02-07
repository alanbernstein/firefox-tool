*B*rowser *L*ink *A*rchive *M*anagement *P*rogram

# what
A small tool to read some of your web browser user data, and present it for read-only access with a better UX than the existing tab/bookmark manager built into the browser. It has a CLI component and a (simple) webpage component. Works for Firefox on Mac and Linux.

# why
I'm a digital hoarder, and I try to do too many things. Firefox's UI for managing tabs, bookmarks, and history does not work for me.

See [MANIFESTO.md](the manifesto) for painful details


# setup
roughly:
```
cd your-repo-folder
git clone git@github.com:alanbernstein/firefox-tool.git
pip install -r requirements.txt
cp example.env .env  # and then update values

# optional: create a config.json file for customization
cp config.json.example config.json  # and then update values

# suggested terse command line alias and/or symlink `ff`
cd your-command-folder
ln -s your-repo-folder/firefox-tool/firefox-tool.py ff
```


# Webpage usage (online)
`cp env.example .env` then update:
- `REMOTE_URL`

# Webpage usage (new browser tab)

`cp env.example .env` then update:
- `LOCAL_URL`: what IP it's served from locally
- `LOCAL_BASEDIR`: what directory it's served from locally

`make run` does this:
```
make render              # generate webpage
make deploy-local        # copy latest webpage to local server directory
make view-local-deploy   # opens the locally-served page in browser
```

## Local server
Serve the dashboard page somehow. I use [simpleserver](https://github.com/alanbernstein/simpleserver) on my desktop in docker.

## Custom new tab
Install [this extension](https://addons.mozilla.org/en-US/firefox/addon/custom-new-tab-page/) ([chrome](https://chromewebstore.google.com/detail/custom-new-tab/lfjnnkckddkopjfgmbcpdiolnmfobflj?hl=en-US&pli=1))

Then set the "New Tab URL" to `$LOCAL_URL`

## Crontab
cd 
```
0 * * * * /home/alan/Dropbox/src/py/firefox-tool/cron-run.sh >> /home/alan/ff-tool.log 2>&1
```

## Window Titler extension

Install [https://addons.mozilla.org/en-US/firefox/addon/window-titler/](this plugin) to add title prefixes to Firefox windows. BLAM reads these from the browser state directory.

# CLI usage
CLI viewing of data is still there, but I mostly use the webpage now. I don't have a great UI in either for "show results from all sections at once"

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
