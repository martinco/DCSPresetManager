from ..module import Module


class Ka50(Module):
    name = 'Ka50'

    dcs_types = ['Ka-50']

    display_name = 'Ka-50'

    # Included in mission dict or not
    in_mission_dict = True

    # Order as per mission dict
    radios = [
        {
            'heading': 'R-828',
            'description': 'VHF-1',
            'modulation': False,
            'ranges': [
                [20, 59.975, 0.025],
            ],
            'defaults': [
                [21.5, 0],
                [25.7, 0],
                [27, 0],
                [28, 0],
                [30, 0],
                [32, 0],
                [40, 0],
                [50, 0],
                [55.5, 0],
                [59.9, 0],
            ],
        },
        {
            'heading': 'ARK-22',
            'description': 'ADF',
            'modulation': False,
            'ranges': [
                [150, 1750, 1],
            ],
            'khz': True,
            'channel_names': [
                'Inner 1',
                'Outer 1',
                'Inner 2',
                'Outer 2',
                'Inner 3',
                'Outer 3',
                'Inner 4',
                'Outer 4',
                'Inner 5',
                'Outer 5',
                'Inner 6',
                'Outer 6',
                'Inner 7',
                'Outer 7',
                'Inner 8',
                'Outer 8',
            ],
            'defaults': [
                [0.625, 0],
                [0.303, 0],
                [0.289, 0],
                [0.591, 0],
                [0.408, 0],
                [0.803, 0],
                [0.443, 0],
                [0.215, 0],
                [0.525, 0],
                [1.065, 0],
                [0.718, 0],
                [0.35, 0],
                [0.583, 0],
                [0.283, 0],
                [0.995, 0],
                [1.21, 0],
            ],
        },
    ]
