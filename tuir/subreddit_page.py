# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import time

from . import docs
from .content import SubredditContent
from .page import Page, PageController, logged_in
from .objects import Navigator, Command
from .exceptions import TemporaryFileError


class SubredditController(PageController):
    character_map = {}


class SubredditPage(Page):
    BANNER = docs.BANNER_SUBREDDIT
    FOOTER = docs.FOOTER_SUBREDDIT

    name = 'subreddit'

    def __init__(self, reddit, term, config, oauth, name):
        """
        Params:
            name (string): Name of subreddit to open
        """
        super(SubredditPage, self).__init__(reddit, term, config, oauth)

        self.controller = SubredditController(self, keymap=config.keymap)
        self.content = SubredditContent.from_name(reddit, self.config, name, term.loader)
        self.nav = Navigator(self.content.get)
        self.toggled_subreddit = None

        if self.config['subreddit_format']:
            self.format = self._create_format(self.config['subreddit_format'])
        elif self.config['look_and_feel'] == 'compact':
            self.format = self._create_format(self.config.COMPACT_FORMAT)

    def handle_selected_page(self):
        """
        Open all selected pages in subwindows except other subreddit pages.
        """
        if not self.selected_page:
            pass
        elif self.selected_page.name in ('subscription', 'submission', 'inbox'):
            # Launch page in a subwindow
            self.selected_page = self.selected_page.loop()
        elif self.selected_page.name == 'subreddit':
            # Replace the current page
            self.active = False
        else:
            raise RuntimeError(self.selected_page.name)

    def refresh_content(self, order=None, name=None):
        """
        Re-download all submissions and reset the page index
        """
        order = order or self.content.order

        # Preserve the query if staying on the current page
        if name is None:
            query = self.content.query
        else:
            query = None

        name = name or self.content.name

        # Hack to allow an order specified in the name by prompt_subreddit() to
        # override the current default
        if order == 'ignore':
            order = None

        with self.term.loader('Refreshing page'):
            self.content = SubredditContent.from_name(
                self.reddit, self.config, name,
                self.term.loader, order=order, query=query)
        if not self.term.loader.exception:
            self.nav = Navigator(self.content.get)

    @SubredditController.register(Command('SORT_1'))
    def sort_content_hot(self):
        if self.content.query:
            self.refresh_content(order='relevance')
        else:
            self.refresh_content(order='hot')

    @SubredditController.register(Command('SORT_2'))
    def sort_content_top(self):
        order = self._prompt_period('top')
        if order is None:
            self.term.show_notification('Invalid option')
        else:
            self.refresh_content(order=order)

    @SubredditController.register(Command('SORT_3'))
    def sort_content_rising(self):
        if self.content.query:
            order = self._prompt_period('comments')
            if order is None:
                self.term.show_notification('Invalid option')
            else:
                self.refresh_content(order=order)
        else:
            self.refresh_content(order='rising')

    @SubredditController.register(Command('SORT_4'))
    def sort_content_new(self):
        self.refresh_content(order='new')

    @SubredditController.register(Command('SORT_5'))
    def sort_content_controversial(self):
        if self.content.query:
            self.term.flash()
        else:
            order = self._prompt_period('controversial')
            if order is None:
                self.term.show_notification('Invalid option')
            else:
                self.refresh_content(order=order)

    @SubredditController.register(Command('SORT_6'))
    def sort_content_gilded(self):
        if self.content.query:
            self.term.flash()
        else:
            self.refresh_content(order='gilded')

    @SubredditController.register(Command('SUBREDDIT_SEARCH'))
    def search_subreddit(self, name=None):
        """
        Open a prompt to search the given subreddit
        """
        name = name or self.content.name

        query = self.term.prompt_input('Search {0}: '.format(name))
        if not query:
            return

        with self.term.loader('Searching'):
            self.content = SubredditContent.from_name(
                self.reddit, self.config, name, self.term.loader, query=query)
        if not self.term.loader.exception:
            self.nav = Navigator(self.content.get)

    @SubredditController.register(Command('SUBREDDIT_FRONTPAGE'))
    def show_frontpage(self):
        """
        If on a subreddit, remember it and head back to the front page.
        If this was pressed on the front page, go back to the last subreddit.
        """

        if self.content.name != '/r/front':
            target = '/r/front'
            self.toggled_subreddit = self.content.name
        else:
            target = self.toggled_subreddit

        # target still may be empty string if this command hasn't yet been used
        if target is not None:
            self.refresh_content(order='ignore', name=target)

    @SubredditController.register(Command('SUBREDDIT_OPEN'))
    def open_submission(self, url=None):
        """
        Select the current submission to view posts.
        """
        if url is None:
            data = self.get_selected_item()
            url = data['permalink']
            if data.get('url_type') == 'selfpost':
                self.config.history.add(data['url_full'])

        self.selected_page = self.open_submission_page(url)

    @SubredditController.register(Command('SUBREDDIT_OPEN_IN_BROWSER'))
    def open_link(self):
        """
        Open a link with the webbrowser
        """

        data = self.get_selected_item()
        if data['url_type'] == 'selfpost':
            self.open_submission()
        elif data['url_type'] == 'x-post subreddit':
            self.refresh_content(order='ignore', name=data['xpost_subreddit'])
        elif data['url_type'] == 'x-post submission':
            self.open_submission(url=data['url_full'])
            self.config.history.add(data['url_full'])
        else:
            self.term.open_link(data['url_full'])
            self.config.history.add(data['url_full'])

    @SubredditController.register(Command('SUBREDDIT_POST'))
    @logged_in
    def post_submission(self):
        """
        Post a new submission to the given subreddit.
        """
        # Check that the subreddit can be submitted to
        name = self.content.name
        if '+' in name or name in ('/r/all', '/r/front', '/r/me', '/u/saved'):
            self.term.show_notification("Can't post to {0}".format(name))
            return

        submission_info = docs.SUBMISSION_FILE.format(name=name)
        with self.term.open_editor(submission_info) as text:
            if not text:
                self.term.show_notification('Canceled')
                return
            elif '\n' not in text:
                self.term.show_notification('Missing body')
                return

            title, content = text.split('\n', 1)
            with self.term.loader('Posting', delay=0):
                submission = self.reddit.submit(name, title, text=content,
                                                raise_captcha_exception=True)
                # Give reddit time to process the submission
                time.sleep(2.0)
            if self.term.loader.exception:
                raise TemporaryFileError()

        if not self.term.loader.exception:
            # Open the newly created submission
            self.selected_page = self.open_submission_page(submission=submission)

    @SubredditController.register(Command('SUBREDDIT_HIDE'))
    @logged_in
    def hide(self):
        data = self.get_selected_item()
        if not hasattr(data["object"], 'hide'):
            self.term.flash()
        elif data['hidden']:
            with self.term.loader('Unhiding'):
                data['object'].unhide()
                data['hidden'] = False
        else:
            with self.term.loader('Hiding'):
                data['object'].hide()
                data['hidden'] = True

    def _submission_attr(self, data):
        if data['url_full'] in self.config.history:
            return self.term.attr('SubmissionTitleSeen')
        else:
            return self.term.attr('SubmissionTitle')

    def _url_attr(self, data):
        if data['url_full'] in self.config.history:
            return self.term.attr('LinkSeen')
        else:
            return self.term.attr('Link')

    def _gold_str(self, data):
        if data['gold'] > 1:
            return self.term.gilded + 'x{} '.format(data['gold'])
        elif data['gold'] == 1:
            return self.term.gilded + ' '
        else:
            return ''

    def _create_format(self, format_string):
        """
        Returns a list of tuples of the format (datafield, attr, first) which
        will be used by _draw_item to output information in the proper order.
        It would be trivial to use the strings as simple format strings, but
        more must be done in order to associate strings with their Attribute.

        datafield = lambda that retrieves the proper field of the data
        dict

        attr = lambda that returns the proper attribute class associated with
        datafield. Sometimes this isn't known until drawtime; see above
        *_attr() functions for examples

        first = boolean that signifies whether or not term.add_line should be
        called with a col argument to start a line
        """
        form = []
        first = True

        # Split the list between %., newlines, and certain separator characters
        # to treat them separately
        format_list = re.split(r'(%.|[\n<>|\\])', format_string, re.DOTALL)

        for item in format_list:
            # Use lambdas because the actual data to be used is only known at
            # drawtime. This way the format list knows how to use the data,
            # and can simply be used when the data is available
            if item == "%i":
                form.append((lambda data: data['index'],
                    lambda data: self._submission_attr(data), first))
            elif item == "%t":
                form.append((lambda data: data['title'],
                    lambda data: self._submission_attr(data), first))
            elif item == "%s":
                # Need to cut off the characters that aren't the score number
                form.append((lambda data: data['score'][:-4],
                    lambda data: self.term.attr('Score'), first))
            elif item == "%v":
                # This isn't great, self.term.get_arrow gets called twice
                form.append((lambda data: self.term.get_arrow(data['likes'])[0],
                    lambda data: self.term.get_arrow(data['likes'])[1], first))
            elif item == "%c":
                form.append((
                    lambda data: '{0}'.format(data['comments'][:-9])
                        if data['comments'] else None, # Don't try to subscript null items
                    lambda data: self.term.attr('CommentCount'),
                    first))
            elif item == "%r":
                form.append((lambda data: data['created'],
                    lambda data: self.term.attr('Created'), first))
            elif item == "%R":
                raise NotImplementedError("'%R' subreddit_format specifier not yet supported")
            elif item == "%e":
                form.append((lambda data: data['edited'],
                    lambda data: self.term.attr('Created'), first))
            elif item == "%E":
                raise NotImplementedError("'%E' subreddit_format specifier not yet supported")
            elif item == "%a":
                form.append((lambda data: data['author'],
                    lambda data: self.term.attr('SubmissionAuthor'), first))
            elif item == "%S":
                form.append((lambda data: "/r/" + data['subreddit'],
                    lambda data: self.term.attr('SubmissionSubreddit'),
                    first))
            elif item == "%u":
                raise NotImplementedError("'%u' subreddit_format specifier not yet supported")
            elif item == "%U":
                form.append((lambda data: data['url'],
                    lambda data: self._url_attr(data), first))
            elif item == "%A":
                form.append((lambda data: '[saved]' if data['saved'] else '',
                    lambda data: self.term.attr('Saved'), first))
            elif item == "%h":
                form.append((lambda data: '[hidden]' if data['hidden'] else '',
                    lambda data: self.term.attr('Hidden'), first))
            elif item == "%T":
                form.append((lambda data: '[stickied]' if data['stickied'] else '',
                    lambda data: self.term.attr('Stickied'), first))
            elif item == "%g":
                form.append((lambda data: self._gold_str(data),
                    lambda data: self.term.attr('Gold'), first))
            elif item == "%n":
                form.append((lambda data: 'NSFW' if data['nsfw'] else '',
                    lambda data: self.term.attr('NSFW'), first))
            elif item == "%f":
                form.append((lambda data: data['flair'] if data['flair'] else '',
                    lambda data: self.term.attr('SubmissionFlair'), first))
            elif item == "%F":
                form.append((lambda data: data['flair'] + ' ' if data['flair'] else '',
                    lambda data: self.term.attr('SubmissionFlair'), first))

                form.append((lambda data: '[saved] ' if data['saved'] else '',
                    lambda data: self.term.attr('Saved'), first))

                form.append((lambda data: '[hidden] ' if data['hidden'] else '',
                    lambda data: self.term.attr('Hidden'), first))

                form.append((lambda data: '[stickied] ' if data['stickied'] else '',
                    lambda data: self.term.attr('Stickied'), first))

                form.append((lambda data: self._gold_str(data),
                    lambda data: self.term.attr('Gold'), first))

                form.append((lambda data: 'NSFW ' if data['nsfw'] else '',
                    lambda data: self.term.attr('NSFW'), first))
            elif item == "\n":
                form.append((item, None, first))
                first = True

                continue
            else: # Write something else that isn't in the data dict
                # Make certain "separator" characters use the Separator
                # attribute
                if item in r"<>|\\":
                    form.append((item,
                                 lambda data: self.term.attr('Separator'),
                                 first))
                else:
                    form.append((item, None, first))

            first = False

        return form

    def _draw_item_format(self, win, data, valid_rows, offset):
        last_attr = None
        for get_data, get_attr, first in self.format:
            # add_line wants strings, make sure we give it strings
            if callable(get_data):
                string = get_data(data)
            else:
                # Start writing to the next line if we hit a newline
                if get_data == "\n":
                    offset += 1
                    continue

                # Otherwise, proceed on the same line
                string = get_data

            # Don't try to write None strings to the screen. This happens in
            # places like user pages, where data['comments'] is None
            if not string and first is False:
                continue

            string = str(string)

            # We only want to print a maximum of one line of data
            # TODO - support line wrapping
            string = string.split('\n')[0]

            if string == ' ':
                # Make sure spaces aren't treated like normal strings and print
                # them to the window this way. This ensures they won't be drawn
                # with an attribute.
                self.term.add_space(win)
                continue

            # To make sure we don't try to write a None as an attribute,
            # we can use the one that was last used
            if get_attr is None:
                attr = last_attr
            else:
                attr = get_attr(data)

            if first:
                self.term.add_line(win, string, offset, 1, attr=attr)
            else:
                self.term.add_line(win, string, offset, attr=attr)

            last_attr = attr

    def _draw_item_default(self, win, data, n_rows, n_cols, valid_rows, offset):
        """
        Draw items with default look and feel
        """

        n_title = len(data['split_title'])

        if data['url_full'] in self.config.history:
            attr = self.term.attr('SubmissionTitleSeen')
        else:
            attr = self.term.attr('SubmissionTitle')

        for row, text in enumerate(data['split_title'], start=offset):
            if row in valid_rows:
                self.term.add_line(win, text, row, 1, attr)

        row = n_title + offset

        if data['url_full'] in self.config.history:
            attr = self.term.attr('LinkSeen')
        else:
            attr = self.term.attr('Link')

        if row in valid_rows:
            self.term.add_line(win, '{url}'.format(**data), row, 1, attr)

        row = n_title + offset + 1

        if row in valid_rows:
            attr = self.term.attr('Score')
            self.term.add_line(win, '{score}'.format(**data), row, 1, attr)
            self.term.add_space(win)

            arrow, attr = self.term.get_arrow(data['likes'])
            self.term.add_line(win, arrow, attr=attr)
            self.term.add_space(win)

            attr = self.term.attr('Created')
            self.term.add_line(win, '{created}{edited}'.format(**data), attr=attr)

            if data['comments'] is not None:
                attr = self.term.attr('Separator')
                self.term.add_space(win)
                self.term.add_line(win, '-', attr=attr)

                attr = self.term.attr('CommentCount')
                self.term.add_space(win)
                self.term.add_line(win, '{comments}'.format(**data), attr=attr)

            if data['saved']:
                attr = self.term.attr('Saved')
                self.term.add_space(win)
                self.term.add_line(win, '[saved]', attr=attr)

            if data['hidden']:
                attr = self.term.attr('Hidden')
                self.term.add_space(win)
                self.term.add_line(win, '[hidden]', attr=attr)

            if data['stickied']:
                attr = self.term.attr('Stickied')
                self.term.add_space(win)
                self.term.add_line(win, '[stickied]', attr=attr)

            if data['gold']:
                attr = self.term.attr('Gold')
                self.term.add_space(win)
                count = 'x{}'.format(data['gold']) if data['gold'] > 1 else ''
                text = self.term.gilded + count
                self.term.add_line(win, text, attr=attr)

            if data['nsfw']:
                attr = self.term.attr('NSFW')
                self.term.add_space(win)
                self.term.add_line(win, 'NSFW', attr=attr)

        row = n_title + offset + 2

        if row in valid_rows:
            attr = self.term.attr('SubmissionAuthor')
            self.term.add_line(win, '{author}'.format(**data), row, 1, attr)
            self.term.add_space(win)

            attr = self.term.attr('SubmissionSubreddit')
            self.term.add_line(win, '/r/{subreddit}'.format(**data), attr=attr)

            if data['flair']:
                attr = self.term.attr('SubmissionFlair')
                self.term.add_space(win)
                self.term.add_line(win, '{flair}'.format(**data), attr=attr)

    def _draw_item(self, win, data, inverted):
        n_rows, n_cols = win.getmaxyx()
        n_cols -= 1  # Leave space for the cursor in the first column

        # Handle the case where the window is not large enough to fit the data.
        valid_rows = range(0, n_rows)
        offset = 0 if not inverted else - (data['n_rows'] - n_rows)

        if self.config['look_and_feel'] == 'compact' or \
                self.config['subreddit_format']:
            self._draw_item_format(win, data, valid_rows, offset)
        else:
            self._draw_item_default(win, data, n_rows, n_cols, valid_rows, offset)

        attr = self.term.attr('CursorBlock')

        for y in range(n_rows):
            self.term.addch(win, y, 0, str(' '), attr)
