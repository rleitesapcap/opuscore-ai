from opuscore_qualidade.plugin import PLUGIN


def test_manifesto_e_perfil():
    assert PLUGIN.manifesto.key == 'qualidade' and PLUGIN.perfil().persona
