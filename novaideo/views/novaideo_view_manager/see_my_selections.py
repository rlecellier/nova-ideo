# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# avalaible on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from substanced.util import get_oid

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS

from novaideo.content.processes.novaideo_view_manager.behaviors import (
    SeeMySelections)
from novaideo.content.novaideo_application import NovaIdeoApplication
from novaideo import _
from novaideo.views.filter import (
    FILTER_SOURCES)
from .see_my_contents import SeeMyContentsView


CONTENTS_MESSAGES = {
    '0': _(u"""Aucun éléments suivi"""),
    '1': _(u"""Un élément suivi"""),
    '*': _(u"""${nember} éléments suivis""")}


@view_config(
    name='seemyselections',
    context=NovaIdeoApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeMySelectionsView(SeeMyContentsView):
    title = _('My following')
    name = 'seemyselections'
    behaviors = [SeeMySelections]
    template = 'novaideo:views/novaideo_view_manager/templates/search_result.pt'
    viewid = 'seemyselections'
    contents_messages = CONTENTS_MESSAGES
    include_archived = False
    content_types = ['all']

    def _get_content_ids(self, user):
        return [get_oid(o) for o in getattr(user, 'selections', [])]


DEFAULTMAPPING_ACTIONS_VIEWS.update({SeeMySelections: SeeMySelectionsView})

FILTER_SOURCES.update(
    {SeeMySelectionsView.name: SeeMySelectionsView})
