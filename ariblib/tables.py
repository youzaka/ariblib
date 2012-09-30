#!/usr/bin/env python3.2
"""セクションとテーブルの違いがわからない頃の実装の後方互換"""
from ariblib.sections import *

Table = Section
ProgramAssociationTable = ProgramAssociationSection
ProgramMapTable = ProgramMapSection
NetworkInformationTable = NetworkInformationSection
ServiceDescriptionTable = ServiceDescriptionSection
BouquetAssociationTable = BouquetAssociationSection
EventInformationTable = EventInformationSection
RunningStatusTable = RunningStatusSection
TimeAndDateTable = TimeAndDateSection
TimeOffsetTable = TimeOffsetSection
LocalEventInformationTable = LocalEventInformationSection
EventRelationTable = EventRelationSection
IndexTransmissionTable = IndexTransmissionSection
PartialContentAnnouncementTable = PartialContentAnnouncementSection
StuffingTable = StuffingSection
BroadcasterInformationTable = BroadcasterInformationSection
NetworkBoardInformationTable = NetworkBoardInformationSection
CommonDataTable = CommonDataSection
LinkedDescriptionTable = LinkedDescriptionSection
SoftwareDownloadTriggerTable = SoftwareDownloadTriggerSection
CommonDataTable = CommonDataSection
DSMCCTable = DSMCCSection

