# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['./graxpert/main.py'],
    pathex=[],
    binaries=[],
    datas=[('./img/*', './img/'), ('./graxpert-dark-blue.json', './')],
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
splash = Splash(
    'img/graXpert_Startbadge_Ariel.png',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,
    text_size=12,
    minify_script=True,
    always_on_top=True,
)

exe = EXE(pyz,
    a.scripts,
    splash,
    a.binaries,
    # Now included in python package
    # Tree('locales', prefix='locales/'),
    a.zipfiles,
    a.datas,  
    [],
    name='GraXpert-win64',
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
    entitlements_file=None , icon='./img/Icon.ico')
