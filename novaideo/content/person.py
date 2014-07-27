import colander
from zope.interface import implementer

from substanced.content import content
from substanced.schema import NameSchemaNode
from substanced.util import renamer
from substanced.principal import UserSchema

from dace.util import getSite
from dace.objectofcollaboration.entity import Entity
from dace.objectofcollaboration.object import (
                SHARED_UNIQUE,
                COMPOSITE_MULTIPLE,
                COMPOSITE_UNIQUE)
from dace.objectofcollaboration.principal import User
from pontus.core import VisualisableElement, VisualisableElementSchema
from pontus.widget import RadioChoiceWidget, FileWidget, Select2Widget
from pontus.file import Image, ObjectData, Object as ObjectType
from .interface import IPerson


@colander.deferred
def organization_choice(node, kw):
    context = node.bindings['context']
    request = node.bindings['request']
    values = []
    root = getSite(context)
    if root is None:
        root = context.__parent__.__parent__

    prop = sorted(root.organizations, key=lambda p: p.title)
    values = [(i, i.title) for i in prop]
    return Select2Widget(values=values)


@colander.deferred
def titles_choice(node, kw):
    context = node.bindings['context']
    request = node.bindings['request']
    root = getSite(context)
    values = [(i, i) for i in root.titles]
    return Select2Widget(values=values)


def context_is_a_person(context, request):
    return request.registry.content.istype(context, 'person')


class PersonSchema(VisualisableElementSchema, UserSchema):

    name = NameSchemaNode(
        editing=context_is_a_person,
        )

    picture = colander.SchemaNode(
            ObjectData(Image),
            widget= FileWidget(),
            required = False
            )

    first_name =  colander.SchemaNode(
                    colander.String(),
                    title='First name' 
                    )

    last_name = colander.SchemaNode(
                    colander.String(),
                    title='Last name' 
                    )
  
    user_title = colander.SchemaNode(
                    colander.String(),
                    widget=titles_choice,
                    title='Title'
                )

    organization = colander.SchemaNode(
                ObjectType(),
                widget=organization_choice,
                missing=None
                )


@content(
    'person',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(IPerson)
class Person(VisualisableElement, User):
    name = renamer()
    properties_def = {'tokens':(COMPOSITE_MULTIPLE, 'owner', True),
                      'organization':(SHARED_UNIQUE, 'members', False),
                      'picture':(COMPOSITE_UNIQUE, None, False)}

    def __init__(self, **kwargs):
        super(Person, self).__init__(**kwargs)

    @property
    def tokens(self):
        return self.getproperty('tokens')

    def settokens(self, tokens):
        self.setproperty('tokens', tokens)

    @property
    def organization(self):
        return self.getproperty('organization')

    def setorganization(self, organization):
        self.setproperty('organization', organization)

