# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# avalaible on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView

from novaideo.content.processes.idea_management.behaviors import  RecuperateIdea
from novaideo.content.idea import Idea
from novaideo import _


@view_config(
    name='recuperateidea',
    context=Idea,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RecuperateIdeaView(BasicView):
    title = _('Recuperate')
    name = 'recuperateidea'
    behaviors = [RecuperateIdea]
    viewid = 'recuperateidea'

    def update(self):
        results = self.execute(None)
        return results[0]


DEFAULTMAPPING_ACTIONS_VIEWS.update({RecuperateIdea:RecuperateIdeaView})
