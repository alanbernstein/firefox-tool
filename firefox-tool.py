#!/usr/bin/env python3
from collections import defaultdict
import datetime
import json
import os
import platform
import shutil
import sys

import jinja2
import lz4.block  # pip install lz4 --user
import sqlite3

from ipdb import iex, set_trace as db

time_fmt = '%Y/%m/%d %H:%M:%S'
now = datetime.datetime.now()
now_str = datetime.datetime.strftime(now, time_fmt)

# TODO: analyze domains
# TODO: domain-specific metadata: video length for youtube
# TODO: work for chrome too

overflow_mode = 'truncate'
if not os.isatty(1):
    # if piping output, then can't get real terminal width,
    # so truncating would be to 80 chars, too small.
    overflow_mode = 'wrap'
W, H = shutil.get_terminal_size()

@iex
def main():

    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help', 'help']:
        print_usage()
        return

    p = FirefoxProfile()

    if sys.argv[1] == 'tabs':
        p.print_session()
    if sys.argv[1] == 'tabs-history':
        p.print_session_history()
    if sys.argv[1] in ['tabs-synced', 'synced-tabs', 'synced']:
        pattern = None
        if len(sys.argv) > 2:
            pattern = sys.argv[2]
        p.print_synced_tabs(pattern, format='md')
    if sys.argv[1] == 'bookmarks':
        p.print_bookmarks()
    if sys.argv[1] == 'bookmarks-tree':
        p.print_bookmarks_tree()
    if sys.argv[1] == 'history':
        print('not yet implemented')
    if sys.argv[1] == 'search':
        pattern = None
        if len(sys.argv) > 2:
            pattern = sys.argv[2]
        p.multisearch(pattern)
    if sys.argv[1] in ['dedup', 'deduplicate']:
        p.find_dupes()
    if sys.argv[1] in ['profile-path', 'profile']:
        print(p.get_profile_path())
    if sys.argv[1] in ['render']:
        p.render_dashboard()

def print_usage():
    print("""firefox-tool
suggested alias: ff

usage:

ff tabs
ff tabs-history
ff tabs-synced [device-name-pattern]
ff bookmarks
ff bookmarks-tree
ff render
ff profile-path""")


class ChromeProfile(object):
    def __init__(self, profile_path=None):
        # https://github.com/JRBANCEL/Chromagnon?tab=readme-ov-file
        self.profile_path = profile_path or self.get_profile_path()
        self.load_bookmarks()

    def load_tabs(self):
        pass

    def get_profile_path(self):
        if platform.system() == 'Darwin':
            return os.path.expanduser('~/Library/Application Support/Google/Chrome/Default')
        if platform.system() == 'Linux':
            return os.path.expanduser('~/.config/google-chrome/Default')
        raise NotImplementedError('unknown profile path')

    def load_bookmarks(self):
        bookmarks_file = self.profile_path + '/Bookmarks'
        with open(bookmarks_file, 'r') as f:
            self.bookmarks_json = json.load(f)

class FirefoxProfile(object):
    old_device_names = ['Firefox on iPhone']
    def __init__(self, profile_path=None):
        self.profile_path = profile_path or self.get_profile_path()
        raw = mozlz4_to_text(self.get_session_file())
        self.session = json.loads(raw)
        self.connect_places_db()
        self.connect_sync_db()
        self.load_places_queries()
        self.load_sync_queries()
        self.filter_devices(self.old_device_names)

    def filter_devices(self, device_names):
        pass

    def get_profile_parent(self):
        if platform.system() == 'Darwin':
            return os.path.expanduser("~/Library/Application Support/Firefox/Profiles")
        if platform.system() == 'Linux':
            # Check for snap Firefox first (more common on modern Ubuntu)
            snap_path = os.path.expanduser("~/snap/firefox/common/.mozilla/firefox")
            if os.path.exists(snap_path):
                return snap_path
            # Fall back to traditional Firefox location
            return os.path.expanduser("~/.mozilla/firefox")
        raise NotImplementedError('unknown profile path')

    def get_profile_path(self):
        # find the thing that endswith .default-release
        fs = os.listdir(self.get_profile_parent())
        for f in fs:
            if f.endswith('.default-release'):
                return self.get_profile_parent() + '/' + f
        return 'unknown'

    def get_session_file(self):
        return self.profile_path + '/sessionstore-backups/recovery.jsonlz4'

    def get_places_file(self):
        return self.profile_path + '/places.sqlite'

    def get_sync_file(self):
        return self.profile_path + '/synced-tabs.db'

    def write_session_json(self, fout):
        with open(fout, "w") as f:
            json.dump(self.session)

    def connect_places_db(self):
        db_file = '/tmp/places.sqlite'
        shutil.copy2(self.get_places_file(), db_file)
        self.places_connection = None
        try:
            self.places_connection = sqlite3.connect(db_file)
        except Exception as exc:
            print(exc)
            db()

    def connect_sync_db(self):
        db_file = '/tmp/synced-tabs.db'
        shutil.copy2(self.get_sync_file(), db_file)
        self.sync_connection = None
        self.sync_connection = sqlite3.connect(db_file)

    def load_places_queries(self):
        cursor = self.places_connection.cursor()

        field_list = ['id', 'url', 'title']
        fields = ', '.join(field_list)
        sql = 'select %s from moz_places' % fields
        cursor.execute(sql)
        self.places_rows = cursor.fetchall()
        self.places_rows_by_id = {r[0]: {k: v for k, v in zip(field_list, r)} for r in self.places_rows}

        field_list = ['id', 'type', 'fk', 'parent', 'title', 'position']
        fields = ', '.join(field_list)
        sql = 'select %s from moz_bookmarks' % fields
        cursor.execute(sql)
        self.bookmarks_rows = cursor.fetchall()
        self.bookmarks_rows_by_id = {r[0]: {k: v for k, v in zip(field_list, r)} for r in self.bookmarks_rows}

        # https://old.reddit.com/r/firefox/comments/4lr4e3/extracting_bookmarks_from_command_line_linux/
        sql = 'select moz_places.title, dateAdded, url from moz_bookmarks, moz_places where moz_places.id=moz_bookmarks.fk;'
        field_list = ['title', 'dateAdded', 'url']
        cursor.execute(sql)
        self.bookmarks_join_rows = cursor.fetchall()
        self.bookmarks_join_rows_by_id = {r[0]: {k: v for k, v in zip(field_list, r)} for r in self.bookmarks_join_rows}

    def load_sync_queries(self):
        cursor = self.sync_connection.cursor()

        # get last sync time
        cursor.execute("select * from moz_meta where key='last_sync_time'")
        rows = cursor.fetchall()
        self.last_sync_time_ts = rows[0][1]
        print(f'last sync time row: {rows[0]}')
        if self.last_sync_time_ts > 4000000000000000:
            # Sentinel value (Dec 31 2099) - sync hasn't occurred or is being initialized
            # Fall back to using max tab modification time as proxy for last sync
            cursor.execute("SELECT MAX(last_modified) FROM tabs")
            max_tab_result = cursor.fetchone()
            if max_tab_result and max_tab_result[0]:
                max_tab_time = max_tab_result[0]
                # Store as seconds (not milliseconds) for JavaScript
                self.sync_timestamp = max_tab_time // 1000
                self.sync_suffix = ' [from tab data]'
            else:
                self.sync_timestamp = None
                self.sync_suffix = ' [never]'
        else:
            # Store as seconds (not milliseconds) for JavaScript
            self.sync_timestamp = self.last_sync_time_ts // 1000
            self.sync_suffix = ''

        # get device metadata (not really needed)
        cursor.execute("select * from moz_meta where key='remote_clients'")
        self.meta_rows = cursor.fetchall()
        remote_devices = json.loads(self.meta_rows[0][1])
        self.device_id_name_map = {k: v['device_name'] for k, v in remote_devices.items()}

        # get tab data
        cursor.execute('select * from tabs;')
        self.tab_rows = cursor.fetchall()

    def multisearch(self, pattern):
        print('not yet implemented')
        res1 = self.search_local_tabs(pattern)
        res2 = self.search_synced_tabs(pattern)
        res3 = self.search_bookmarks(pattern)
        # TODO present results in a useful way

    def search_local_tabs(self, pattern):
        res = []
        for tab in []:
            if pattern in tab.url or pattern in tab.title:
                res.append(tab)
        return res

    def search_synced_tabs(self, pattern):
        res = []
        for tab in []:
            if pattern in tab.url or pattern in tab.title:
                res.append(tab)
        return res

    def search_bookmarks(self, pattern):
        res = []
        # create 
        for bookmark in []:
            if pattern in bookmark.url or pattern in bookmark.title or pattern in bookmark.path:
                res.append(bookmark)
        return res

    def find_dupes(self):
        # TODO
        print('not yet implemented')

    def print_bookmarks(self):
        for row in self.bookmarks_join_rows:
            print(row)

    def print_bookmarks_folders(self):
        branch_node_rows = [r for r in self.bookmarks_rows if r[1] == 2]
        for row in branch_node_rows[:30]:
            print(row)

    def print_quick_bookmarks(self, filename=None):
        """Generate quick bookmarks from toolbar root (non-folder items)"""
        f = None if not filename else open(filename, 'w')

        # Find toolbar node
        TOOLBAR_NODE_ID = None
        for id, row in self.bookmarks_rows_by_id.items():
            if row['title'] == 'toolbar':
                TOOLBAR_NODE_ID = id
                break

        if not TOOLBAR_NODE_ID:
            return

        # Get toolbar children (only non-folder items)
        ROOT_NODE_ID = 1
        self.parent_to_children = defaultdict(list)
        for id, row in self.bookmarks_rows_by_id.items():
            self.parent_to_children[row['parent']].append(row['id'])

        toolbar_children = self.parent_to_children[TOOLBAR_NODE_ID]
        for child_id in toolbar_children:
            child_row = self.bookmarks_rows_by_id[child_id]
            # Type 1 = bookmark, Type 2 = folder
            if child_row['type'] == 1 and child_row['fk'] in self.places_rows_by_id:
                url = self.places_rows_by_id[child_row['fk']]['url']
                title = child_row['title']
                # For now, no favicons - just simple links
                write(f, '<a href="%s" class="quick-bookmark">%s</a>' % (url, title))

    def print_bookmarks_tree(self, filename=None, format=None):
        format = format or 'html'

        ROOT_NODE_ID = 1
        self.parent_to_children = defaultdict(list)
        for id, row in self.bookmarks_rows_by_id.items():
            self.parent_to_children[row['parent']].append(row['id'])

        if format == 'md':
            self.recurse_bookmarks_tree_mdlist(ROOT_NODE_ID)
        elif format == 'mddoc':
            self.recurse_bookmarks_tree_mddoc(ROOT_NODE_ID)
        elif format == 'html':
            if filename and os.path.exists(filename):
                os.remove(filename) # delete it here since all further writes must be in append mode
            self.recurse_bookmarks_tree_html(ROOT_NODE_ID, filename=filename)
        elif format == 'html-tabs':
            if filename and os.path.exists(filename):
                os.remove(filename)
            self.print_bookmarks_with_tabs(filename=filename)

    def print_bookmarks_with_tabs(self, filename=None):
        """Generate bookmarks with sub-tabs for toolbar folders"""
        f = None if not filename else open(filename, 'w')

        # Find toolbar node
        TOOLBAR_NODE_ID = None
        for id, row in self.bookmarks_rows_by_id.items():
            if row['title'] == 'toolbar':
                TOOLBAR_NODE_ID = id
                break

        if not TOOLBAR_NODE_ID:
            return

        # Get toolbar folder children
        toolbar_children = self.parent_to_children[TOOLBAR_NODE_ID]
        folders = []
        for child_id in toolbar_children:
            child_row = self.bookmarks_rows_by_id[child_id]
            # Type 2 = folder
            if child_row['type'] == 2:
                folders.append((child_id, child_row['title']))

        # Generate sub-tabs for folders
        write(f, '<div class="tabs sub-tabs">')
        for i, (folder_id, folder_name) in enumerate(folders):
            folder_slug = folder_name.replace(' ', '-').lower()
            active_class = ' active' if i == 0 else ''
            write(f, '  <button class="tab-button%s" data-subtab="bookmarks-%s">%s</button>' % (active_class, folder_slug, folder_name))
        write(f, '</div>')

        # Close the file to ensure tabs are written
        if f:
            f.close()

        # Generate content for each folder (using append mode since tabs were already written)
        for i, (folder_id, folder_name) in enumerate(folders):
            folder_slug = folder_name.replace(' ', '-').lower()
            active_class = ' active' if i == 0 else ''
            f = open(filename, 'a') if filename else None
            write(f, '<div id="bookmarks-%s-content" class="subtab-content%s" data-subtab="bookmarks-%s">' % (folder_slug, active_class, folder_slug))
            write(f, '  <h3>%s</h3>' % folder_name)
            # Render folder's children directly (not the folder itself)
            if folder_id in self.parent_to_children:
                child_ids = self.parent_to_children[folder_id]
                child_ids_sorted = sorted(child_ids, key=lambda x: self.bookmarks_rows_by_id[x]['position'])
                for child_id in child_ids_sorted:
                    self.recurse_bookmarks_tree_html(child_id, depth=2, filename=filename)
            write(f, '</div>')
            if f:
                f.close()

    def recurse_bookmarks_tree_mdlist(self, node_id, depth=0):
        row = self.bookmarks_rows_by_id[node_id]

        if row['fk'] in self.places_rows_by_id:
            url = self.places_rows_by_id[row['fk']]['url']

            line = '%s- [%s](%s)' % ('  ' * depth, row['title'], url)
            print(line)
        else:
            print('%s- %s' % ('  ' * depth, row['title']))
            if node_id in self.parent_to_children:
                for c in self.parent_to_children[node_id]:
                    self.recurse_bookmarks_tree_mdlist(c, depth+1)

    def recurse_bookmarks_tree_mddoc(self, node_id, depth=0):
        row = self.bookmarks_rows_by_id[node_id]

        if row['fk'] in self.places_rows_by_id:
            url = self.places_rows_by_id[row['fk']]['url']
            print('[%s](%s)' % (row['title'], url))
        else:
            print('%s %s' % ('#' * depth, row['title']))
            if node_id in self.parent_to_children:
                for c in self.parent_to_children[node_id]:
                    self.recurse_bookmarks_tree_mddoc(c, depth+1)

    def recurse_bookmarks_tree_html(self, node_id, depth=0, filename=None):
        row = self.bookmarks_rows_by_id[node_id]
        f = None if not filename else open(filename, 'a')

        #db()
        if row['fk'] in self.places_rows_by_id:
        #if row['type'] == 1
            url = self.places_rows_by_id[row['fk']]['url']
            write(f, '%s<a href="%s">%s</a>' % ('  ' * depth, url, row['title']))
        else:
            if node_id in self.parent_to_children:
            # if row['type'] == 2
                title = row['title']
                if node_id == 1:
                    title = "[root]"
                state = ''
                if title in ['toolbar', '[root]']:
                    state = 'open '
                # TODO: html escape
                write(f, '%s<details %sclass="folder"><summary class="folder-title">📁 %s</summary>' % ('  ' * (depth-1), state, title))

                child_ids = self.parent_to_children[node_id]
                child_ids.sort(key=lambda x: self.bookmarks_rows_by_id[x]['position'])
                for c in child_ids:
                    self.recurse_bookmarks_tree_html(c, depth+1, filename)
                write(f, '%s</details>' % ('  ' * depth))

    def print_synced_tabs(self, device_name_pattern=None, omit_name_patterns=None, filename=None, format=None):
        format = format or 'md'
        f = None if not filename else open(filename, 'w')

        # Collect devices first
        devices = []
        for row in self.tab_rows:
            id, record, last_modified = row
            data = json.loads(record)
            device_name = data['clientName']
            if device_name_pattern and device_name_pattern not in device_name.lower():
                print('omitting tabs from "%s"' % device_name)
                continue
            if omit_name_patterns:
                skip = False
                for p in omit_name_patterns:
                    if p.lower() in device_name.lower():
                        print('omitting tabs from "%s"' % device_name)
                        skip = True
                        continue
                if skip:
                    continue
            devices.append((device_name, data['tabs']))
            print('%4d tabs (%s)' % (len(data['tabs']), device_name))

        if format == 'html':
            # Generate sub-tabs for devices
            write(f, '<div class="tabs sub-tabs">')
            for i, (device_name, tabs) in enumerate(devices):
                device_id = 'synced-' + device_name.replace(' ', '-').replace("'", '').lower()
                active_class = ' active' if i == 0 else ''
                write(f, '  <button class="tab-button%s" data-subtab="%s">%s</button>' % (active_class, device_id, device_name))
            write(f, '</div>')

            # Generate content for each device
            for i, (device_name, tabs) in enumerate(devices):
                device_id = 'synced-' + device_name.replace(' ', '-').replace("'", '').lower()
                active_class = ' active' if i == 0 else ''
                write(f, '<div id="%s-content" class="subtab-content%s" data-subtab="%s">' % (device_id, active_class, device_id))
                write(f, '  <h3>%s (%s tabs)</h3>' % (device_name, len(tabs)))

                for tab in tabs:
                    urls = tab['urlHistory']
                    url = urls[0]
                    last_used_ts = tab['lastUsed']
                    last_used_time = datetime.datetime.fromtimestamp(last_used_ts)
                    last_used_delta = now - last_used_time

                    # TODO: html escape, jinja escape
                    if '{%' in tab['title']:
                        print('jinja conflict in tab title:')
                        print(tab['title'])
                        continue
                    write(f, '  <a href="%s">- %s (%s)</a>' % (url, tab['title'], last_used_delta.days))

                write(f, '</div>')
        elif format == 'md':
            for device_name, tabs in devices:
                print('')
                print('## %s (%s)' % (device_name, now_str))
                for tab in tabs:
                    urls = tab['urlHistory']
                    url = urls[0]
                    last_used_ts = tab['lastUsed']
                    last_used_time = datetime.datetime.fromtimestamp(last_used_ts)
                    last_used_delta = now - last_used_time

                    line = '[%s](%s) (%s days)' % (tab['title'], url, last_used_delta.days)
                    if overflow_mode == 'truncate':
                        if len(line) > W:
                            line = line[:W-3] + '...'
                        print(line)
                    elif overflow_mode == 'wrap':
                        print(line)

    def print_session(self, filename=None, format=None):
        format = format or 'md'
        f = None if not filename else open(filename, 'w')

        windows = self.session['windows']
        total_tabs = 0

        if format == 'html':
            # Generate sub-tabs for windows
            write(f, '<div class="tabs sub-tabs">')
            for wnum, w in enumerate(windows):
                active_class = ' active' if wnum == 0 else ''
                write(f, '  <button class="tab-button%s" data-subtab="tabs-window%d">Window %d</button>' % (active_class, wnum, wnum + 1))
            write(f, '</div>')

            # Generate content for each window
            for wnum, w in enumerate(windows):
                active_class = ' active' if wnum == 0 else ''
                write(f, '<div id="tabs-window%d-content" class="subtab-content%s" data-subtab="tabs-window%d">' % (wnum, active_class, wnum))
                write(f, '  <h3>window %d (%s tabs)</h3>' % (wnum + 1, len(w['tabs'])))
                for tnum, t in enumerate(w['tabs']):
                    total_tabs += 1
                    e0 = t['entries'][-1]
                    url = e0.get('url', None)
                    # TODO: html escape
                    write(f, '  <a href="%s">- %s</a>' % (url, e0['title']))
                write(f, '</div>')
        elif format == 'md':
            for wnum, w in enumerate(windows):
                print('')
                print('## window %s (%s tabs)' % (wnum, len(w['tabs'])))
                for tnum, t in enumerate(w['tabs']):
                    total_tabs += 1
                    e0 = t['entries'][-1]
                    url = e0.get('url', None)
                    print('- [%s](%s)' % (e0['title'], url))

        print('%4d tabs (local session (%d windows))' % (total_tabs, len(windows)))

    def print_session_history(self):
        for wnum, w in enumerate(self.session['windows']):
            print('window %d' % wnum)
            for tnum, t in enumerate(w['tabs']):
                for en_num, e in enumerate(reversed(t['entries'])):
                    url = e.get('url', None)
                    uri = e.get('originalURI', None)
                    if en_num == 0:
                        print('  %d: %s %s' % (tnum, url, e['title']))
                    else:
                        print('      %s%s %s' % (en_num*' ', url, e['title']))

    def render_dashboard(self):
        # render fragments with tab structure
        self.print_session(filename='tmp/tabs.html', format='html')
        self.print_synced_tabs(filename='tmp/synced.html', format='html', omit_name_patterns=self.old_device_names)
        self.print_bookmarks_tree(filename='tmp/bookmarks.html', format='html-tabs')
        self.print_quick_bookmarks(filename='tmp/quick-bookmarks.html')

        # render template
        template_file = 'ff-dashboard-template.html'
        output_file = 'ff-dashboard.html'

        templateLoader = jinja2.FileSystemLoader(searchpath="./")
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template(template_file)
        rendered = template.render(
            render_timestamp=int(now.timestamp()),
            sync_timestamp=self.sync_timestamp if self.sync_timestamp else 0,
            sync_suffix=self.sync_suffix
        )

        with open(output_file, 'w') as f:
            f.write(rendered)

        print('wrote %d bytes to %s' % (len(rendered), output_file))


    def inspect_session(self):
        for k in self.session.keys():
            print('%s: %s' % (k, type(self.session[k])))

        print('')
        print('len(windows) = %s' % len(self.session['windows']))
        w = self.session['windows'][0]
        for k in w.keys():
            print('%s: %s' % (k, type(w[k])))

        print('')
        t = w['tabs'][0]
        print('len(tabs) = %s' % len(t))
        for k in t.keys():
            print('%s: %s' % (k, type(t[k])))

        print('')
        e = t['entries']
        print('len(entries) = %s' % len(t['entries']))

        db()


def mozlz4_to_text(filepath):
    # https://gist.github.com/snorey/3eaa683d43b0e08057a82cf776fd7d83
    # Given the path to a "mozlz4", "jsonlz4", "baklz4" etc. file,
    # return the uncompressed text.
    bytestream = open(filepath, "rb")
    bytestream.read(8)  # skip past the b"mozLz40\0" header
    valid_bytes = bytestream.read()
    text = lz4.block.decompress(valid_bytes)
    return text


def write(file, line):
    if file:
        file.write(line + '\n')
        file.flush()
    else:
        print(line)


if __name__ == "__main__":
    main()


"""
sessionstore recovery.jsonlz4 top-level contents:
version: <class 'list'>         (small)
windows: <class 'list'>         (large)
selectedWindow: <class 'int'>   (small)
_closedWindows: <class 'list'>  (large)
session: <class 'dict'>         (small)
global: <class 'dict'>          (small)
cookies: <class 'list'>         (large)
"""
