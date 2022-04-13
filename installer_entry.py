import multiprocessing
from dcs_preset_manager.app import main

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
