# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# avalaible on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from substanced.util import get_oid

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS

from novaideo.content.processes.novaideo_view_manager.behaviors import (
    SeeMySupports)
from novaideo.content.novaideo_application import NovaIdeoApplication
from novaideo import _
from novaideo.views.filter import (
    FILTER_SOURCES)
from .see_my_contents import SeeMyContentsView


CONTENTS_MESSAGES = {
    '0': _(u"""Aucun contenu apprécié """
          u"""et ${tokens} jeton(s) d'appréciation restant(s)"""),
    '1': _(u"""Un contenu apprécié """
            u"""et ${tokens} jeton(s) d'appréciation restant(s)"""),
    '*': _(u"""${nember} contenus appréciés """
            u"""et ${tokens} jeton(s) d'appréciation restant(s)""")
}


@view_config(
    name='seemysupports',
    context=NovaIdeoApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeMySupportsView(SeeMyContentsView):
    title = _('My supports')
    name = 'seemysupports'
    behaviors = [SeeMySupports]
    template = 'novaideo:views/novaideo_view_manager/templates/search_result.pt'
    viewid = 'seemysupports'
    contents_messages = CONTENTS_MESSAGES
    selected_filter = [('metadata_filter', ['negation', 'keywords', 'states']),
                       ('temporal_filter', ['negation', 'created_date']),
                       'text_filter', 'other_filter']
    include_archived = False
    content_types = ['idea', 'proposal']

    def _get_title(self, **args):
        return _(self.contents_messages[args.get('index')],
            mapping={'nember': args.get('len_result'),
                     'tokens': len(getattr(args.get('user'), 'tokens', []))})

    def _get_content_ids(self, user):
        return [get_oid(o) for o in getattr(user, 'supports', [])]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {SeeMySupports: SeeMySupportsView})


FILTER_SOURCES.update(
    {SeeMySupportsView.name: SeeMySupportsView})
