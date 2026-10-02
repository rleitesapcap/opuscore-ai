from opuscore_lider.plugin import PLUGIN


def test_manifesto_e_perfil():
    assert PLUGIN.manifesto.key == 'lider-tecnico' and PLUGIN.perfil().persona
