from otree.api import *


class C(BaseConstants):
    # Nome que aparecerá no endereço da sessão.
    NAME_IN_URL = 'public_goods_testes'

    # Quantidade de participantes em cada grupo.
    PLAYERS_PER_GROUP = 2

    # Quantidade de rodadas.
    NUM_ROUNDS = 2

    # Pontos iniciais recebidos por participante em cada rodada.
    ENDOWMENT = cu(100)

    # Valor pelo qual o total contribuído será multiplicado.
    MULTIPLIER = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    # Soma das contribuições dos participantes do grupo.
    total_contribution = models.CurrencyField()

    # Parcela do fundo comum recebida por cada participante.
    individual_share = models.CurrencyField()


class Player(BasePlayer):
    contribution = models.CurrencyField(
        min=0,
        max=C.ENDOWMENT,
        label='Quanto você deseja contribuir para o fundo comum?',
    )


# FUNÇÕES

def set_payoffs(group: Group):
    """Calcula o fundo comum e o pagamento de cada participante."""

    players = group.get_players()

    contributions = [
        participant.contribution
        for participant in players
    ]

    group.total_contribution = sum(contributions)

    group.individual_share = (
        group.total_contribution
        * C.MULTIPLIER
        / C.PLAYERS_PER_GROUP
    )

    for participant in players:
        participant.payoff = (
            C.ENDOWMENT
            - participant.contribution
            + group.individual_share
        )


# PÁGINAS

class Instructions(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class Contribute(Page):
    form_model = 'player'
    form_fields = ['contribution']


class ResultsWaitPage(WaitPage):
    title_text = 'Aguardando os demais participantes'
    body_text = 'Aguarde até que todos os participantes do grupo façam sua escolha.'

    after_all_players_arrive = set_payoffs


class Results(Page):
    pass


page_sequence = [
    Instructions,
    Contribute,
    ResultsWaitPage,
    Results,
]