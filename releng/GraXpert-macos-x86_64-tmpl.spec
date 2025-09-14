# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata


block_cipher = None


datas = []
datas += [('./img/*', './img/'), ('./graxpert-dark-blue.json', './')]
datas += copy_metadata('xisf')


a = Analysis(['./graxpert/main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['PIL._tkinter_finder', 'tkinter'],
    hookspath=['./releng'],
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
    name='GraXpert',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='x86_64',
    codesign_identity=None,
    entitlements_file=None , icon='./img/Icon.ico')

coll = COLLECT(
    exe,
    a.binaries,
    Tree('locales', prefix='locales/'),
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GraXpert')

app = BUNDLE(coll,
            name='GraXpert.app',
            icon='./img/Icon.ico',
            bundle_identifier=None,
            info_plist={
                'CFBundleShortVersionString': 'RELEASE (SNAPSHOT)',
                'NSHighResolutionCapable': 'True'
            }
            )