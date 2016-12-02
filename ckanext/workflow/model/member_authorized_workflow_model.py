import datetime
import logging
from ckan.model.domain_object import DomainObject
from ckan.model import meta
from ckan import model
from sqlalchemy import Column, UniqueConstraint, ForeignKeyConstraint, ForeignKey, Table, types, DateTime
from sqlalchemy import desc

log = logging.getLogger(__name__)

member_authorized_table = None


def setup():
    if member_authorized_table is None:
        define_member_authorized_table()
        log.debug('Member_authorized_workflow table defined in memory')

    if model.member_table.exists():
        if not member_authorized_table.exists():
            member_authorized_table.create()
            log.debug('Member_authorized_workflow table create')
        else:
            log.debug('Member_authorized_workflow table already exists')
    else:
        log.debug('Member_authorized_workflow table creation deferred')


class MemberAuthorizedWorkflowModel(object):
    @classmethod
    def filter(cls, session, **kwargs):
        return session.query(cls).filter_by(**kwargs)

    @classmethod
    def exists(cls, session, member_dict):
        if cls.filter(session, user_id=member_dict['table_id'], group_id=member_dict['group_id']).first():
            return True
        else:
            return False

    @classmethod
    def get(cls, session, **kwargs):
        instance = cls.filter(session, **kwargs).first()
        return instance

    @classmethod
    def create(cls, session, member_dict):
        instance = cls()
        instance.member_id = member_dict['id'],
        instance.user_id = member_dict['table_id'],
        instance.group_id = member_dict['group_id'],
        instance.state = member_dict['state']
                        
        session.add(instance)
        session.commit()
        return instance.as_dict()

    @classmethod
    def as_dict(self):
        return self.__dict__


class MemberAuthorizedWorkflow(MemberAuthorizedWorkflowModel):
    @classmethod
    def get_all(cls, session, **kwargs):
        instances = cls.filter(session, **kwargs).all()
        return instances


def define_member_authorized_table():
    global member_authorized_table

    member_authorized_table = Table(
        'member_authorized_workflow',
        meta.metadata,
        Column('member_id',
               types.UnicodeText,
               primary_key=True, 
               nullable=False),
        Column('user_id',
               types.UnicodeText,
               nullable=False),
        Column('group_id',
               types.UnicodeText,
               nullable=False),
        Column('state',
               types.UnicodeText,
               nullable=False),
        ForeignKeyConstraint(
                ['member_id'],
                ['member.id'],
                onupdate="CASCADE", ondelete="CASCADE"
        )
    )

    meta.mapper(MemberAuthorizedWorkflow, member_authorized_table)


def get_member_authorized_workflow(session, member_id, group_id):
    return session.query(MemberAuthorizedWorkflow).filter(
                    and_(MemberAuthorizedWorkflow.member_id == member_id, 
                         MemberAuthorizedWorkflow.group_id == group_id)).first()


def add_member_authorized_workflow(session, member_dict):
    model = MemberAuthorizedWorkflow()
    
    model.member_id = member_dict['id']
    model.user_id = member_dict['table_id']
    model.group_id = member_dict['group_id']
    model.state = member_dict['state']

    session.add(model)
    
    session.commit()  