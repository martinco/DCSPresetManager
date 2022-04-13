from ..module import Module


class F_14B(Module):

    name = 'F_14B'

    dcs_types = ['F-14B']

    display_name = 'F-14B'

    # Included in mission dict or not
    in_mission_dict = True

    # F14 uses AFT radio preset 1 for group
    group_radio_preset = 1

    # Order as per mission dict
    radios = [
        {
            'heading': 'FWD',
            'description': 'UHF AN/ARC-159',
            'modulation': False,
            'ranges': [
                [225, 399.975, 0.025],
            ],
            'defaults': [
                [225, 0],
                [258, 0],
                [260, 0],
                [270, 0],
                [255, 0],
                [259, 0],
                [262, 0],
                [257, 0],
                [253, 0],
                [263, 0],
                [267, 0],
                [254, 0],
                [264, 0],
                [266, 0],
                [265, 0],
                [252, 0],
                [268, 0],
                [269, 0],
                [268, 0],
                [269, 0],
            ]
        },
        {
            'heading': 'AFT',
            'description': 'VHF/UHF AN/ARC-182',
            'modulation': False,
            'ranges': [
                [30, 88, 0.025],
                [108, 174, 0.025],
                [225, 399.975, 0.025],
            ],
            'defaults': [
                [225, 0],
                [258, 0],
                [260, 0],
                [270, 0],
                [255, 0],
                [259, 0],
                [262, 0],
                [257, 0],
                [253, 0],
                [263, 0],
                [267, 0],
                [254, 0],
                [264, 0],
                [266, 0],
                [265, 0],
                [252, 0],
                [268, 0],
                [269, 0],
                [268, 0],
                [269, 0],
                [225, 0],
                [258, 0],
                [260, 0],
                [270, 0],
                [255, 0],
                [259, 0],
                [262, 0],
                [257, 0],
                [253, 0],
                [263, 0],
            ],
        },
    ]
