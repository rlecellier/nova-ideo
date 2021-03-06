# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# avalaible on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView

from novaideo.content.processes.proposal_management.behaviors import (
    SubmitProposal)
from novaideo.content.proposal import Proposal
from novaideo import _


@view_config(
    name='submitproposal',
    context=Proposal,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SubmitProposalView(BasicView):
    title = _('Submit the proposal')
    name = 'submitproposal'
    behaviors = [SubmitProposal]
    viewid = 'submitproposal'

    def update(self):
        results = self.execute(None)
        return results[0]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {SubmitProposal: SubmitProposalView})
