from ..module import Module


class FA_18C(Module):

    name = 'FA_18C'

    dcs_types = ['FA-18C_hornet']

    display_name = 'F/A-18C'

    # Included in mission dict or not
    in_mission_dict = True

    # Group uses COMM 1
    group_radio_preset = 0

    # Order as per mission dict
    radios = [
        {
            'heading': 'PRI',
            'description': 'COMM 1 AN/ARC-210',
            'modulation': False,
            'ranges': [
                [30, 87.995, 0.005],
                [118, 173.995, 0.005],
                [225, 399.975, 0.025],
            ],
            'defaults': [
                [305, 0],
                [264, 0],
                [265, 0],
                [256, 0],
                [254, 0],
                [250, 0],
                [270, 0],
                [257, 0],
                [255, 0],
                [262, 0],
                [259, 0],
                [268, 0],
                [269, 0],
                [260, 0],
                [263, 0],
                [261, 0],
                [267, 0],
                [251, 0],
                [253, 0],
                [266, 0],
            ],
        },
        {
            'heading': 'SEC',
            'description': 'COMM 2 AN/ARC-210',
            'modulation': False,
            'ranges': [
                [30, 88, 0.025],
                [108, 174, 0.025],
                [225, 399.975, 0.025],
            ],
            'defaults': [
                [305, 0],
                [264, 0],
                [265, 0],
                [256, 0],
                [254, 0],
                [250, 0],
                [270, 0],
                [257, 0],
                [255, 0],
                [262, 0],
                [259, 0],
                [268, 0],
                [269, 0],
                [260, 0],
                [263, 0],
                [261, 0],
                [267, 0],
                [251, 0],
                [253, 0],
                [266, 0],
            ],
        },
    ]
