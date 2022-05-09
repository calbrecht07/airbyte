#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_carlos_template_test import SourceCarlosTemplateTest

if __name__ == "__main__":
    source = SourceCarlosTemplateTest()
    launch(source, sys.argv[1:])
