#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_employment_hero import SourceEmploymentHero

if __name__ == "__main__":
    source = SourceEmploymentHero()
    launch(source, sys.argv[1:])
