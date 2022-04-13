from ..module import Module


class Mi_8MT(Module):
    name = 'Mi_8MT'

    dcs_types = ['Mi-8MT']

    display_name = 'Mi-8MT'

    # Included in mission dict or not
    in_mission_dict = True

    # R863
    group_radio_preset = 0

    # Order as per mission dict
    radios = [
        {
            'heading': 'R-863',
            'description': 'R-863',
            'modulation': False,
            'ranges': [
                [100, 149.975, 0.025],
                [220, 399.975, 0.025],
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
        {
            'heading': 'R-828',
            'description': 'R-828',
            'modulation': False,
            'ranges': [
                [20, 59.9, 0.025],
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
    ]
