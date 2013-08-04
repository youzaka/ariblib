#!/usr/bin/env python3.2
# coding: utf-8

import sys
from ariblib import tsopen
from ariblib.sections import *

with tsopen(sys.stdin.fileno()) as ts:
    for section in ts.sections(
        BroadcasterInformationSection,
        EventInformationSection,
        ServiceDescriptionSection,
        NetworkInformationSection
        ):
        section.dump()


