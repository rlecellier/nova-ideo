# Copyright (c) 2014 by Ecreall under licence AGPL terms
# avalaible on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from dace.objectofcollaboration.principal.role import (
    Collaborator, Role, Administrator, role)

from novaideo import _


@role(name='SiteAdmin',
      superiors=[Administrator])
class SiteAdmin(Role):
    pass


@role(name='Member',
      superiors=[Administrator, SiteAdmin],
      lowers=[Collaborator])
class Member(Role):
    pass


@role(name='PortalManager',
      superiors=[Administrator, SiteAdmin],
      lowers=[Collaborator, Member])
class PortalManager(Role):
    pass


@role(name='Observer',
      superiors=[Administrator, SiteAdmin],
      lowers=[Collaborator],
      islocal=True)
class Observer(Role):
    pass


@role(name='Moderator',
      superiors=[Administrator, SiteAdmin],
      lowers=[Collaborator, Member, PortalManager])
class Moderator(Role):
    pass


@role(name='Examiner',
      superiors=[Administrator, SiteAdmin],
      lowers=[Collaborator, Member, Moderator])
class Examiner(Role):
    pass


@role(name='OrganizationResponsible',
      superiors=[Administrator, SiteAdmin],
      lowers=[Collaborator],
      islocal=True)
class OrganizationResponsible(Role):
    pass


@role(name='Participant',
      superiors=[Administrator, SiteAdmin],
      lowers=[Collaborator, Observer],
      islocal=True)
class Participant(Role):
    pass


@role(name='Elector',
      islocal=True)
class Elector(Role):
    pass


@role(name='Certifier',
      superiors=[Administrator, SiteAdmin],
      lowers=[Collaborator])
class Certifier(Role):
    pass


DEFAULT_ROLES = ['Member']


APPLICATION_ROLES = {
    'Member': _('Member'),
    'Admin': _('Administrator'),
    'SiteAdmin': _('Site administrator'),
    'Moderator': _('Moderator'),
    'Examiner': _('Examiner'),
}
