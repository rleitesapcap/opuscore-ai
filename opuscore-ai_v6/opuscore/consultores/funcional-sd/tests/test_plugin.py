from opuscore_sd.plugin import PLUGIN


def test_manifesto_e_perfil():
    assert PLUGIN.manifesto.key == 'funcional-sd' and PLUGIN.perfil().persona
