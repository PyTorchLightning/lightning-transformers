import sys

import pytest


@pytest.mark.skipif(sys.platform == "win32", reason="Currently Windows is not supported")
def test_smoke_train_e2e(script_runner):
    script_runner.hf_train(task='multiple_choice', dataset='swag', model='prajjwal1/bert-tiny')


def test_smoke_predict_e2e(script_runner):
    script_runner.hf_predict(['+x=TODO'], task='multiple_choice', model='prajjwal1/bert-tiny')
    # TODO: no hf-task defined in model
