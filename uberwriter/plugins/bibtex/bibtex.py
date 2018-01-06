from gi.repository import Gtk, Gio, Gdk, GObject

from . import bibtexparser
from . import fuzzywuzzy
from .fuzzywuzzy import process as fuzzyprocess

from .gi_composites import GtkTemplate

from uberwriter_lib import helpers
import os

PATH = os.path.dirname(os.path.realpath(__file__))

@GtkTemplate(ui=PATH + '/bibtex_item.glade')
class BibTexItem(Gtk.ListBoxRow):

    __gtype_name__ = 'BibTexItem'

    title_label = GtkTemplate.Child()
    author_label = GtkTemplate.Child()
    other_label = GtkTemplate.Child()

    def __init__(self, data): 
        super(Gtk.ListBoxRow, self).__init__()
        # This must occur *after* you initialize your base
        self.init_template()
        self.title_label.set_text(data['title'])
        self.author_label.set_text(data.get('author'))
        self.other_label.set_text(data.get('year') if data.get('year') else 'N/A')


class BibTex(object):
    """docstring for Handler"""

    def open_bibtex(self, event, *args):
        self.match()
        self.window.show_all()

    def get_widget_for_box(self, word):
        return Gtk.Label(word)

    def real_row_activated(self, row, data=None):
        self.app.TextBuffer.insert_at_cursor('[@' + data + ']')
        self.close()

    def row_activated(self, widget, row, data=None):
        # row.activate()
        return

    def match(self, filtered=None):
        self.rows = []

        # delete all children
        # for i in self.listview.children:
        #     self.listview.remove(i)
        # if not filter
        for i in self.bib_db.entries:
            if filtered and i not in filtered:
                continue
            # if i not in self.filtered:
            #     continue

            row  = Gtk.ListBoxRow()
            item = BibTexItem(i)
            row.add(item)
            row.set_activatable(True)
            row.connect('activate', self.real_row_activated, i['ID'])
            self.rows.append(row)
            self.listview.add(row)

        self.listview.show_all()

    def on_delete(self, event, data=None):
        # Don't delete this dialogs widgets
        self.window.hide()
        return True

    def on_search(self, widget, data=None):
        text = widget.get_text()
        print(text)
        matches = fuzzyprocess.extract(text, self.matchlist, limit=20)
        print(matches)
        matches_list = [i[0] for i in matches]
        self.match(matches)

    def sort_func(self, row1, row2):
        print(row1)

    def get_matchlist(self):
        l = {}
        for i in self.bib_db.entries:
            l[i['ID']] = i['ID'] + ' ' + i['author'] + ' ' + i['title']
        return l

    def __init__(self, app):

        self.app = app

        GObject.signal_new('toggle-bibtex', self.app, GObject.SIGNAL_ACTION, None, ())
        self.app.connect('toggle-bibtex', self.open_bibtex)

        with open('/home/wolfv/ownCloud/Studium/Semester Project/Report/listb.bib') as f:
            self.bib_db = bibtexparser.load(f)

        self.matchlist = self.get_matchlist()
        self.builder = Gtk.Builder()
        self.builder.add_from_file(PATH + '/bibtex.glade')

        self.window = self.builder.get_object('bibtex_window')
        self.window.set_name('bibtex_window')
        self.window.set_transient_for(self.app)
        self.window.set_modal(True)
        self.window.connect('delete-event', self.on_delete)
        self.listview = self.builder.get_object('listbox')

        self.searchbox = self.builder.get_object('searchentry1')
        self.searchbox.connect('search-changed', self.on_search)
        self.style_provider = Gtk.CssProvider()
        self.style_provider.load_from_path(PATH + '/bibtex.css')


        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), self.style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )