from ..module import Module


class A_10C(Module):

    name = 'A_10C'

    dcs_types = [
        'A-10C',
        'A-10C_2',
    ]

    display_name = 'A-10C'

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
                [225, 0],
                [235, 0],
                [245, 0],
                [255, 0],
                [265, 0],
                [275, 0],
                [285, 0],
                [295, 0],
                [305, 0],
                [315, 0],
                [325, 0],
                [335, 0],
                [345, 0],
                [355, 0],
                [365, 0],
                [375, 0],
                [385, 0],
                [395, 0],
                [396, 0],
                [397, 0],
            ]
        },
        {
            'heading': 'VHF AM',
            'target_directory': 'VHF_AM_RADIO',
            'description': 'AN/ARC-186(V) VHF AM #1',
            'modulation': False,
            'ranges': [
                [116, 151.975, 0.05],
            ],
            'defaults': [
                [121.5, 0]
            ]*20,
        },
        {
            'heading': 'FM',
            'target_directory': 'VHF_FM_RADIO',
            'description': 'AN/ARC-186(V) VHF FM #2',
            'modulation': False,
            'ranges': [
                [30, 75.975, 0.05],
            ],
            'defaults': [
                [40.5, 0]
            ]*20,
        },
    ]

    def get_module_dials(self, radio_idx, coalition):

        # Selection dial defaults are is OFF, MAN, MAN
        selection_dial = [0, 2, 2]

        # SETTINGS.lua wants initial manual frequency in hz
        primary_freq = int(self['presets'][radio_idx][coalition.upper()][0]['frequency'] * 1000000)

        return {
            'mode_dial': 0,
            'manual_frequency': primary_freq,
            'selection_dial': selection_dial[radio_idx],
            'channel_dial': 0,
        }
