"""Explicit synthetic demonstration criteria; observations never self-authenticate."""
POLICIES = {
    'WATERLOGGING': {
        'BLOCKAGE': {'confirming': ['OBSTRUCTION_OBSERVED', 'FLOW_RESTRICTED'], 'falsifying': ['DRAIN_CLEAR']},
        'CAPACITY_DEFICIT': {'confirming': ['CAPACITY_TEST_EXCEEDED', 'DRAIN_CLEAR'], 'falsifying': ['CAPACITY_ADEQUATE']},
        'PUMP_FAILURE': {'confirming': ['PUMP_FAILURE_OBSERVED', 'POWER_TEST_FAILED'], 'falsifying': ['PUMP_TEST_NORMAL']},
    },
    'ROAD_DAMAGE': {
        'UTILITY_LEAK': {'confirming': ['LEAK_DETECTED', 'INFILTRATION_AT_DAMAGE'], 'falsifying': ['PRESSURE_TEST_NORMAL']},
        'SUBGRADE_FAILURE': {'confirming': ['SUBGRADE_FAILURE_OBSERVED', 'STRUCTURAL_TEST_FAILED'], 'falsifying': ['SUBGRADE_TEST_NORMAL']},
    },
    'WASTE_ACCUMULATION': {
        'MISSED_PICKUP': {'confirming': ['PICKUP_MISSED_CONFIRMED', 'WASTE_PERSISTED_AFTER_SCHEDULE'], 'falsifying': ['PICKUP_COMPLETED_CONFIRMED']},
        'CAPACITY_SHORTFALL': {'confirming': ['BIN_CAPACITY_EXCEEDED', 'EXPECTED_PICKUPS_COMPLETED'], 'falsifying': ['CAPACITY_ADEQUATE']},
        'ILLEGAL_DUMPING': {'confirming': ['DUMPING_OBSERVED', 'UNSCHEDULED_DEPOSIT_OBSERVED'], 'falsifying': ['SCHEDULED_ACCUMULATION_ONLY']},
    },
}

ASSET_LABELS = {'BLOCKAGE': ['DrainInlet', 'DrainSegment'], 'CAPACITY_DEFICIT': ['DrainInlet', 'DrainSegment'],
                'PUMP_FAILURE': ['PumpStation'], 'UTILITY_LEAK': ['WaterPipe'], 'SUBGRADE_FAILURE': ['RoadSegment'],
                'MISSED_PICKUP': ['WasteCollectionPoint'], 'CAPACITY_SHORTFALL': ['WasteCollectionPoint'],
                'ILLEGAL_DUMPING': ['WasteCollectionPoint']}
for rules in POLICIES.values():
    for cause, rule in rules.items():
        rule['asset_labels'] = ASSET_LABELS[cause]
        rule['requires_topology'] = cause == 'UTILITY_LEAK'


def classify(*, support, contradiction, reviewed, sufficient):
    # Compatibility adapter for existing internal callers; never give an unreviewed
    # negative claim stronger authority than the same unreviewed positive claim.
    return classify_reviewed(reviewed_support=support and reviewed, unreviewed_support=support and not reviewed,
        reviewed_contradiction=contradiction and reviewed, unreviewed_contradiction=contradiction and not reviewed,
        sufficient=sufficient and reviewed)


def classify_reviewed(*, reviewed_support, unreviewed_support, reviewed_contradiction, unreviewed_contradiction, sufficient):
    """Rule v2: equal authority for unreviewed positive and negative claims."""
    support = reviewed_support or unreviewed_support
    contrary = reviewed_contradiction or unreviewed_contradiction
    if support and contrary:
        return 'INCONCLUSIVE'
    if reviewed_contradiction:
        return 'CONTRADICTED'
    if reviewed_support:
        return 'VERIFIED' if sufficient else 'SUPPORTED'
    if unreviewed_support:
        return 'POSSIBLE'
    return 'INCONCLUSIVE'
