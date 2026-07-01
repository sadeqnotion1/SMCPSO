#=====================================================================================
#============ tests/test_interfaces/test_interfaces_package_init.py ===================
#=====================================================================================
"""Regression test for M7-S7: top-level src/interfaces/__init__.py.

The package uses PEP 562 module __getattr__ lazy imports. The port fixes a latent
bug where the loader hardcoded ``package='interfaces'`` which does not resolve under
the beta ``src`` layout (the real package is ``src.interfaces``). This test asserts:

* the package imports without pulling heavy optional deps at import time,
* get_framework_info() is self-consistent (total_components == len(__all__)),
* every name advertised in __all__ resolves through the lazy loader (no dangling
  references to symbols the ported submodules do not actually export).

If the package= regression returns, every getattr below raises AttributeError and
this test fails fast instead of silently shipping a dead package facade.
"""
import importlib

import src.interfaces as interfaces


def test_framework_info_is_self_consistent():
    info = interfaces.get_framework_info()
    assert info["version"] == interfaces.__version__
    assert info["total_components"] == len(interfaces.__all__)
    # the six ported submodules are all advertised
    assert set(info["modules"]) == {
        "hil", "data_exchange", "monitoring", "hardware", "network", "core"
    }


def test_every_public_name_resolves_via_lazy_loader():
    unresolved = []
    for name in interfaces.__all__:
        try:
            assert getattr(interfaces, name) is not None
        except Exception as exc:  # AttributeError if lazy import path is wrong
            unresolved.append((name, type(exc).__name__))
    assert not unresolved, f"lazy import failed for: {unresolved}"


def test_unknown_attribute_raises_attribute_error():
    try:
        interfaces.DefinitelyNotAThing
    except AttributeError:
        return
    raise AssertionError("expected AttributeError for unknown attribute")
