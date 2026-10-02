from opuscore_integracao.plugin import PLUGIN


def test_manifesto_e_perfil():
    assert PLUGIN.manifesto.key == 'integracao' and PLUGIN.perfil().persona
