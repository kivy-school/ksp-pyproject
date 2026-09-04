from ksp_pyproject.protocols.pyproject_toml import KivySchoolProtocol, AndroidProtocol, IosProtocol, MacOSProtocol, AppleProtocol
from ksp_pyproject.data.pyproject_toml import PyProjectToml


from pathlib import Path


py_project = PyProjectToml("")
_ks_data = py_project.tool.kivy_school
if _ks_data: 
    and_data = _ks_data.android
    if and_data:
        android_data: AndroidProtocol = and_data
    _apple_data = _ks_data.apple
    if _apple_data:  
        apple_data: AppleProtocol = _apple_data
        _ios_data = _apple_data.ios
        if _ios_data:
            ios_data: IosProtocol = _ios_data
        _macos_data = _apple_data.macos
        if _macos_data:
            macos_data: MacOSProtocol = _macos_data

    ks_data: KivySchoolProtocol = _ks_data

