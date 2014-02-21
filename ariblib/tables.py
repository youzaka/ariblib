"""セクションとテーブルの違いがわからない頃の実装の後方互換"""

from ariblib.sections import (
    Section,
    ProgramAssociationSection,
    ProgramMapSection,
    ConditionalAccessSection,
    NetworkInformationSection,
    ServiceDescriptionSection,
    BouquetAssociationSection,
    EventInformationSection,
    RunningStatusSection,
    TimeAndDateSection,
    TimeOffsetSection,
    LocalEventInformationSection,
    EventRelationSection,
    IndexTransmissionSection,
    PartialContentAnnouncementSection,
    StuffingSection,
    BroadcasterInformationSection,
    NetworkBoardInformationSection,
    CommonDataSection,
    LinkedDescriptionSection,
    SoftwareDownloadTriggerSection,
    DSMCCSection,
)

Table = Section
ProgramAssociationTable = ProgramAssociationSection
ProgramMapTable = ProgramMapSection
ConditionalAccessTable = ConditionalAccessSection
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
DSMCCTable = DSMCCSection
