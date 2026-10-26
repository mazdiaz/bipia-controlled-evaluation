from preflight.runner import plan


def tiny_plan():
    return plan([dict(case_id='1',task='email',context='hi',question='Q')],seed=1)
