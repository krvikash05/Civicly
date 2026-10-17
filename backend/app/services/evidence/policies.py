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
    if support and contradiction:
        return 'INCONCLUSIVE'
    if contradiction:
        return 'CONTRADICTED'
    if support:
        return 'VERIFIED' if sufficient else 'SUPPORTED' if reviewed else 'POSSIBLE'
    return 'INCONCLUSIVE'
