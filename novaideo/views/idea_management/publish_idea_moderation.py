# Copyright (c) 2014 by Ecreall under licence AGPL terms
# avalaible on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import deform
from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.form import FormView
from pontus.view_operation import MultipleView
from pontus.view import BasicView
from pontus.default_behavior import Cancel

from novaideo.content.processes.idea_management.behaviors import (
    PublishIdeaModeration)
from novaideo.content.idea import Idea
from novaideo import _


class PublishIdeaViewStudyReport(BasicView):
    title = _('Alert for publication')
    name = 'alertforpublication'
    template = 'novaideo:views/idea_management/templates/alert_idea_publish.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class PublishIdeaView(FormView):
    title = _('Publish')
    name = 'publishideamoderationform'
    formid = 'formpublishideamoderation'
    behaviors = [PublishIdeaModeration, Cancel]
    validate_behaviors = False

    def before_update(self):
        self.action = self.request.resource_url(
            self.context, 'novaideoapi',
            query={'op': 'update_action_view',
                   'node_id': PublishIdeaModeration.node_definition.id})
        self.schema.widget = deform.widget.FormWidget(
            css_class='deform novaideo-ajax-form')


@view_config(
    name='publishideamoderation',
    context=Idea,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class PublishIdeaViewMultipleView(MultipleView):
    title = _('Publish the idea')
    name = 'publishideamoderation'
    behaviors = [PublishIdeaModeration]
    viewid = 'publishideamoderation'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (PublishIdeaViewStudyReport, PublishIdeaView)
    validators = [PublishIdeaModeration.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {PublishIdeaModeration: PublishIdeaViewMultipleView})
