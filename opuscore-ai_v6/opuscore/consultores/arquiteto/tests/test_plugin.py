from opuscore_arquiteto.plugin import PLUGIN


def test_manifesto_e_perfil():
    assert PLUGIN.manifesto.key == 'arquiteto' and PLUGIN.perfil().persona
