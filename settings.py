from os import environ


SESSION_CONFIGS = [
    dict(
        name='fast_consensus_min',
        display_name='Fast Consensus',
        app_sequence=['fast_consensus_min'],
        num_demo_participants=3,
    ),

    dict(
        name='public_goods_testes',
        display_name='Jogo de Bens Públicos',
        app_sequence=['public_goods_testes'],
        num_demo_participants=2,
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    doc="",
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []


# Idioma geral da aplicação.
LANGUAGE_CODE = 'pt'


# Moeda utilizada quando houver conversão de pontos
# para dinheiro real.
REAL_WORLD_CURRENCY_CODE = 'BRL'


# Mantém os resultados apresentados como pontos.
USE_POINTS = True


ROOMS = [
    dict(
        name='turma_psicologia_social',
        display_name='Turma de Psicologia Social',
        participant_label_file='_rooms/econ101.txt',
    ),

    dict(
        name='demonstracao_ao_vivo',
        display_name='Sala para demonstração ao vivo',
    ),
]


ADMIN_USERNAME = 'admin'

# Por segurança, a senha pode ser configurada
# como variável de ambiente.
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')


DEMO_PAGE_INTRO_HTML = """
<h3>Experimentos de Psicologia Social</h3>
<p>Escolha abaixo o experimento que deseja executar.</p>
"""


SECRET_KEY = '7665810155469'


INSTALLED_APPS = ['otree']