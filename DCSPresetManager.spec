# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['installer_entry.py'],
             pathex=['build\\lib'],
             binaries=[],
             datas=[('build\\lib\\dcs_preset_manager\\resources', 'dcs_preset_manager\\resources')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='DCSPresetManagerGUI',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='build\\lib\\dcs_preset_manager\\resources\\icon.ico')

cli = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='DCSPresetManager',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='build\\lib\\dcs_preset_manager\\resources\\icon.ico')

portable = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='DCSPresetManager',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None, icon='build\\lib\\dcs_preset_manager\\resources\\icon.ico')

coll = COLLECT(exe, cli,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='DCSPresetManager')
