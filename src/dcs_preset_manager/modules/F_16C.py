from ..module import Module

class F_16C(Module):

    name = 'F_16C'

    dcs_types = ['F-16C_50']

    display_name = 'F-16CM bl.50'

    # Included in mission dict or not
    in_mission_dict = False

    # Order as per mission dict
    radios = [
        {
            'heading': 'UHF',
            'target_directory': 'UHF_RADIO',
            'description': 'AN/ARC-164',
            'modulation': False,
            'ranges': [
                [225, 399.975, 0.05],
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
            ]
        },
        {
            'heading': 'VHF',
            'target_directory': 'VHF_RADIO',
            'description': 'AN/ARC-222',
            'modulation': False,
            'ranges': [
                [30, 87.975, 0.05],
                [116, 155.975, 0.05],
            ],
            'defaults': [
                [127.5, 0],
                [135, 0],
                [136, 0],
                [127, 0],
                [125, 0],
                [121, 0],
                [141, 0],
                [128, 0],
                [126, 0],
                [133, 0],
                [130, 0],
                [129, 0],
                [123, 0],
                [131, 0],
                [134, 0],
                [132, 0],
                [138, 0],
                [122, 0],
                [124, 0],
                [137, 0],
            ],
        },
    ]
