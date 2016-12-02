import datetime
import logging
from ckan.model.domain_object import DomainObject
from ckan.model import meta
from ckan import model
from sqlalchemy import Column, UniqueConstraint, ForeignKeyConstraint, ForeignKey, Table, types, DateTime
from sqlalchemy import desc

log = logging.getLogger(__name__)

process_state_table = None


def setup():
    if process_state_table is None:
        define_process_state_table()
        log.debug('Package_process_state table defined in memory')

    if model.package_table.exists():
        if not process_state_table.exists():
            process_state_table.create()
            log.debug('Package_process_state table create')
        else:
            log.debug('Package_process_state table already exists')
    else:
        log.debug('Package_process_state table creation deferred')


class PackageProcessStateBaseModel(object):
    @classmethod
    def filter(cls, session, **kwargs):
        return session.query(cls).filter_by(**kwargs)

    @classmethod
    def exists(cls, session, **kwargs):
        if cls.filter(session, **kwargs).first():
            return True
        else:
            return False

    @classmethod
    def get(cls, session, **kwargs):
        instance = cls.filter(session, **kwargs).first()
        return instance

    @classmethod
    def create(cls, session, **kwargs):
        instance = cls(**kwargs)
        session.add(instance)
        session.commit()
        return instance.as_dict()


class PackageProcessState(PackageProcessStateBaseModel):
    @classmethod
    def get_process_state_ids(cls, session):
        return [i for (i, ) in session.query(cls.package_id).all()]

    @classmethod
    def is_process_state_for_package(cls, session, package):
        if cls.get(session, package_id=package):
            return True
        else:
            return False


def define_process_state_table():
    global process_state_table

    process_state_table = Table(
        'package_process_state',
        meta.metadata,
        Column('package_id',
               types.UnicodeText,
               nullable=False),
        Column('revision_id',
               types.UnicodeText,
               nullable=False),
        Column('creator_id',
               types.UnicodeText,
               nullable=False),
        Column('modifior_id',
               types.UnicodeText,
               nullable=False),
        Column('process_state',
               types.UnicodeText,
               nullable=False),
        Column('reason',
               types.UnicodeText,
               nullable=True),
        Column('state',
               types.UnicodeText,
               nullable=False),
        Column('created_date', 
               DateTime, 
               primary_key=True, 
               default=datetime.datetime.utcnow),
        ForeignKeyConstraint(
                ['package_id'],
                ['package.id'],
                onupdate="CASCADE", ondelete="CASCADE"
        )
    )

    meta.mapper(PackageProcessState, process_state_table)


def get_package_last_process_state(session, package_id, modifior_id=''):
    return session.query(PackageProcessState).filter(
                     PackageProcessState.package_id == package_id
                  ).order_by(
                    desc(PackageProcessState.created_date)
                  ).first()

def add_package_process_state(session, pkg_dict, modifior_id):
    model = PackageProcessState()
    
    model.package_id = pkg_dict['id']
    model.process_state = pkg_dict['process_state']
    if pkg_dict.has_key("reason"):
        model.reason = pkg_dict['reason']
    model.revision_id = pkg_dict['revision_id']
    model.state = pkg_dict['state']
    model.created_date = datetime.datetime.now()
    model.creator_id = pkg_dict['creator_user_id']
    model.modifior_id = modifior_id
    
    session.add(model)
    session.commit()

