"""
Tests for ConsoleMe on ECS main CloudFormation stack
"""

import pytest

from cdk.consoleme_ecs_service.constants import BASE_NAME
from app import app


@pytest.fixture(scope="module")
def cf_template():
    """
    Returns synthesized template from main stack
    """
    return app.synth().get_stack(BASE_NAME).template


def test_count_nested_stacks(cf_template):
    """
    Test if the main CloudFormation stack contains the correct number of nested stacks
    """
    assert len([resource for resource in cf_template['Resources']
                if cf_template['Resources'][resource]['Type'] == 'AWS::CloudFormation::Stack']) == 10
