﻿# coding=utf-8
class UserView:
    def __init__(self, id, tab_title, tab_description, page_title, view_name, template_file, data_size=0):
        self.id = id
        self.tab_title = tab_title
        self.tab_description = tab_description
        self.page_title = page_title
        self.view_name = view_name
        self.template_file = template_file
        self.data_size = data_size
        
        
USER_TEMPLATE_VIEWS = (
    UserView(
        id = 'stats',
        tab_title = u'Overview',
        tab_description = u'User Profile',
        page_title = u'Overview - User Profile',
        view_name = 'user_stats',
        template_file = 'user_stats.html'
    ),
    UserView(
        id = 'recent',
        tab_title = u'Recent activities',
        tab_description = u'User recent activity',
        page_title = u'Recent activities - Profile',
        view_name = 'user_recent',
        template_file = 'user_recent.html',
        data_size = 50
    ),
    UserView(
        id = 'responses',
        tab_title = u'Response',
        tab_description = u'Other users of the responses and comments',
        page_title = u'Response - Profile',
        view_name = 'user_responses',
        template_file = 'user_responses.html',
        data_size = 50
    ),
    UserView(
        id = 'reputation',
        tab_title = u'Points',
        tab_description = u'User community points',
        page_title = u'Points - Profile',
        view_name = 'user_reputation',
        template_file = 'user_reputation.html'
    ),
    UserView(
        id = 'favorites',
        tab_title = u'Favorites',
        tab_description = u'Collection of user issues',
        page_title = u'Collection - User Information',
        view_name = 'user_favorites',
        template_file = 'user_favorites.html',
        data_size = 50
    ),
    UserView(
        id = 'votes',
        tab_title = u'Vote',
        tab_description = u'Users of all voting',
        page_title = u'Vote - Profile',
        view_name = 'user_votes',
        template_file = 'user_votes.html',
        data_size = 50
    ),
    UserView(
        id = 'preferences',
        tab_title = u'Set',
        tab_description = u'User parameter setting',
        page_title = u'Settings - User Profile',
        view_name = 'user_preferences',
        template_file = 'user_preferences.html'
    )
)
