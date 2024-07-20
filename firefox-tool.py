#!/usr/bin/env python3
from collections import defaultdict
import datetime
import json
import os
import platform
import shutil
import sys

import lz4.block  # pip install lz4 --user
import sqlite3

from ipdb import iex, set_trace as db

time_fmt = '%Y/%m/%d %H:%M:%S'
now = datetime.datetime.now()
now_str = datetime.datetime.strftime(now, time_fmt)

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
        p.print_session_markdown()
    if sys.argv[1] == 'tabs-history':
        p.print_session_history()
    if sys.argv[1] in ['tabs-synced', 'synced-tabs', 'synced']:
        pattern = None
        if len(sys.argv) > 2:
            pattern = sys.argv[2]
        p.print_synced_tabs_markdown(pattern)
    if sys.argv[1] == 'bookmarks':
        p.print_bookmarks()
    if sys.argv[1] == 'bookmarks-tree':
        p.print_bookmarks_tree()
    if sys.argv[1] == 'history':
        print('not yet implemented')
    if sys.argv[1] == 'search':
        print('not yet implemented')
    if sys.argv[1] in ['profile-path', 'profile']:
        print(p.get_profile_path())

def print_usage():
    print("""firefox-tool
suggested alias: ff

usage:

ff tabs
ff tabs-history
ff tabs-synced [device-name-pattern]
ff bookmarks
ff bookmarks-tree
ff history
ff search
ff profile-path""")

class FirefoxProfile(object):
    def __init__(self, profile_path=None):
        self.profile_path = profile_path or self.get_profile_path()
        raw = mozlz4_to_text(self.get_session_file())
        self.session = json.loads(raw)
        self.connect_bookmarks_db()
        self.connect_sync_db()

    def get_profile_parent(self):
        if platform.system() == 'Darwin':
            return os.path.expanduser("~/Library/Application Support/Firefox/Profiles")
        if platform.system() == 'Linux':
            return os.path.expanduser("~/.mozilla/firefox")

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

    def connect_bookmarks_db(self):
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

    def print_bookmarks(self):
        # https://old.reddit.com/r/firefox/comments/4lr4e3/extracting_bookmarks_from_command_line_linux/
        cursor = self.places_connection.cursor()
        # cursor.execute('select * from moz_bookmarks, moz_places where moz_places.id=moz_bookmarks.fk;')
        cursor.execute('select moz_places.title, dateAdded, url from moz_bookmarks, moz_places where moz_places.id=moz_bookmarks.fk;')
        rows = cursor.fetchall()
        for row in rows:
            print(row)

    def print_bookmarks_tree(self):
        cursor = self.places_connection.cursor()

        sql1 = "select id, url, title from moz_places"
        cursor.execute(sql1)
        self.places_rows = cursor.fetchall()
        self.places_rows_by_id = {r[0]: r for r in self.places_rows}

        sql2 = "select id, type, fk, parent, title from moz_bookmarks"
        cursor.execute(sql2)
        self.bookmarks_rows = cursor.fetchall()
        self.bookmarks_rows_by_id = {r[0]: r for r in self.bookmarks_rows}

        branch_node_rows = [r for r in self.bookmarks_rows if r[1] == 2]

        #for row in branch_node_rows[:30]:
        #    print(row)

        self.parent_to_children = defaultdict(list)
        for row in self.bookmarks_rows:
            self.parent_to_children[row[3]].append(row[0])

        self.recurse_bookmarks_tree(1)

    def recurse_bookmarks_tree(self, node_id, depth=0):
        if node_id in self.bookmarks_rows_by_id:
            row = self.bookmarks_rows_by_id[node_id]
        else:
            print('index error : %s' % node_id)
            return

        id_ = row[0]
        typ = row[1]
        fk = row[2]
        parent = row[3]
        title = row[4]
        if fk in self.places_rows_by_id:
            # leaf node with an associated url
            url = self.places_rows_by_id[fk][1]
            # print('%s(%s %s)%s (%s)' % (' ' * depth, id_, typ, title, url))
            #print('[%s](%s)' % (title, url))  # markdown, nested sections
            print('%s- [%s](%s)' % ('  ' * depth, title, url)) # markdown, nested list
        else:
            # print('%s(%s %s)%s' % (' ' * depth, id_, typ, title))
            # print('%s %s' % ('#' * depth, title)) # markdown, nested sections
            print('%s- %s' % ('  ' * depth, title)) # markdown, nested list
            if node_id in self.parent_to_children:
                for c in self.parent_to_children[node_id]:
                    self.recurse_bookmarks_tree(c, depth+1)


    def inspect_bookmarks_tree(self):
        cursor = self.places_connection.cursor()

        sql2 = "select id, type, fk, parent, title from moz_bookmarks"
        cursor.execute(sql2)
        rows = cursor.fetchall()

        parent_to_children = defaultdict(list)
        for row in rows:
            parent_to_children[row[3]].append(row[0])

        parents = parent_to_children.keys()
        for branch_node_id in sorted(parents)[:30]:
            fk = rows[branch_node_id][2]
            parent = rows[branch_node_id][3]
            title = rows[branch_node_id][4]
            print('%d: fk: %s, parent: %s, title: %s' % (branch_node_id, fk, parent, title))
            print('  children: %s' % (parent_to_children[branch_node_id]))


        db()

        # cursor.execute('select * from moz_bookmarks, moz_places where moz_places.id=moz_bookmarks.fk;')
        # SELECT moz_places.id, moz_places.url, moz_places.title, moz_bookmarks.parent FROM moz_places LEFT OUTER JOIN moz_bookmarks N moz_places.id = moz_bookmarks.fk WHERE moz_bookmarks.parent = N
        sql = ('SELECT moz_places.id, moz_places.url, moz_places.title, moz_bookmarks.parent'
               'FROM moz_places'
               'LEFT OUTER JOIN moz_bookmarks'
               'N moz_places.id = moz_bookmarks.fk'
               'WHERE moz_bookmarks.parent = N')

        sql1 = ("select moz_places.title, dateAdded, url"
                "from moz_bookmarks, moz_places"
                "where moz_places.id=moz_bookmarks.fk")
        sql1 = "select moz_places.id, fk, parent, moz_places.title, dateAdded, url from moz_bookmarks, moz_places where moz_places.id=moz_bookmarks.fk"

        cursor.execute(sql1)
        rows = cursor.fetchall()

        for row in rows:
            print(row)

        

    def print_bookmarks_tree_html(self):
        # print tree structure of bookmark folders to an html file
        # each level is show/hide-able
        # search box that searches all urls and titles, and hides non-match branches
        pass

    def print_synced_tabs_markdown(self, device_name_pattern):
        cursor = self.sync_connection.cursor()

        # get last sync time
        cursor.execute("select * from moz_meta where key='last_sync_time'")
        rows = cursor.fetchall()
        last_sync_time_ts = rows[0][1]
        last_sync_time = datetime.datetime.fromtimestamp(last_sync_time_ts//1000)
        last_sync_time_str = datetime.datetime.strftime(last_sync_time, time_fmt)
        last_sync_delta = now - last_sync_time
        print('last sync: %s (%s ago)' % (last_sync_time_str, last_sync_delta))

        # get device metadata (not really needed)
        cursor.execute("select * from moz_meta where key='remote_clients'")
        rows = cursor.fetchall()
        remote_devices = json.loads(rows[0][1])
        device_id_name_map = {k: v['device_name'] for k, v in remote_devices.items()}

        # get synced tabs
        cursor.execute('select * from tabs')
        rows = cursor.fetchall()
        for row in rows:
            id, record, last_modified = row
            data = json.loads(record)
            device_name = data['clientName']
            if device_name_pattern and device_name_pattern not in device_name.lower():
                print('')
                print('omitting tabs from "%s"' % device_name)
                continue
            print('')
            print('## %s (%s)' % (device_name, now_str))
            tabs = data['tabs']
            # these seem to be listed in ascending age, oldest at the bottom
            # this is what i would normally want, so no need to sort
            for tab in tabs:
                urls = tab['urlHistory']
                if len(urls) > 1:
                    db()
                url = urls[0]

                last_used_ts = tab['lastUsed']
                last_used_time = datetime.datetime.fromtimestamp(last_used_ts)
                last_used_time_str = datetime.datetime.strftime(last_used_time, time_fmt)
                last_used_delta = now - last_used_time

                line = '[%s](%s) (%s days)' % (tab['title'], url, last_used_delta.days)
                if overflow_mode == 'truncate':
                    if len(line) > W:
                        line = line[:W-3] + '...'
                    print(line)
                elif overflow_mode == 'wrap':
                    print(line)

    def print_session_markdown(self):
        for wnum, w in enumerate(self.session['windows']):
            print('')
            print('## window %s (%s tabs)' % (wnum, len(w['tabs'])))
            for tnum, t in enumerate(w['tabs']):
                e0 = t['entries'][-1]
                url = e0.get('url', None)
                uri = e0.get('originalURI', None)
                # print('  %d: %s %s (%d entries)' % (tnum, url, e0['title'], len(t['entries'])))
                print('- [%s](%s)' % (e0['title'], url))

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
