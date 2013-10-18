from sage import triggers

dg = triggers.create_group('dummy', app='dummyapp')


@dg.exact('test')
def decorator_trigger(trigger):
    pass


def api_trigger(trigger):
    pass

dg.create(
    name='api_trigger',
    pattern='test',
    mtype='exact',
    methods=[api_trigger]
)

sg = dg.create_group('subdummy')


@sg.substring('test')
def sg_trigger(trigger):
    pass
