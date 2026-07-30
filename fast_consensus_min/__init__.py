import time
from otree.api import *


doc = """
Jogo mínimo de consenso para grupos fechados de 3 participantes.
Os participantes entram por código de grupo, respondem a 10 rodadas sincronizadas
e recebem um resumo final com download dos dados do próprio grupo.
"""


class C(BaseConstants):
    NAME_IN_URL = 'fast_consensus_min'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 10
    ROUND_TIME_SECONDS = 30

    QUESTIONS = [
        {
            'question': 'Escolha um objeto:',
            'options': ['Martelo', 'Garfo', 'Chave', 'Escova'],
        },
        {
            'question': 'Escolha um objeto:',
            'options': ['Guarda-chuva', 'Lanterna', 'Mochila', 'Relógio'],
        },
        {
            'question': 'Escolha um objeto:',
            'options': ['Tesoura', 'Panela', 'Toalha', 'Cadeado'],
        },
        {
            'question': 'Escolha um objeto:',
            'options': ['Copo', 'Almofada', 'Régua', 'Balde'],
        },
        {
            'question': 'Escolha um objeto:',
            'options': ['Estojo', 'Garrafa', 'Caderno', 'Boné'],
        },
        {
            'question': 'Escolha um objeto:',
            'options': ['Aspirador', 'Ventilador', 'Liquidificador', 'Ferro de passar'],
        },
        {
            'question': 'Escolha um objeto:',
            'options': ['Vela', 'Corda', 'Cadeira', 'Espelho'],
        },
        {
            'question': 'Escolha um objeto:',
            'options': ['Alicate', 'Furadeira', 'Trena', 'Serrote'],
        },
        {
            'question': 'Escolha um objeto:',
            'options': ['Bola', 'Trave', 'Chuteira', 'Apito'],
        },
        {
            'question': 'Escolha um objeto:',
            'options': ['Bicicleta', 'Patins', 'Skate', 'Patinete'],
        },
    ]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    consensus_reached = models.BooleanField(initial=False)
    consensus_choice = models.StringField(blank=True)
    round_start_timestamp = models.FloatField(blank=True)
    round_deadline_timestamp = models.FloatField(blank=True)


class Player(BasePlayer):
    group_code = models.StringField(label='Código do grupo', blank=True)
    question_text = models.StringField(blank=True)
    choice = models.StringField(label='Escolha uma alternativa:', blank=True)
    submission_status = models.StringField(blank=True)
    response_time = models.FloatField(min=0, blank=True)
    consensus_reached = models.BooleanField(initial=False)


def current_question(player: Player):
    return C.QUESTIONS[player.round_number - 1]


def normalize_group_code(value):
    return (value or '').strip().upper()


def form_groups_by_code(subsession: Subsession):
    """Reorganiza os participantes em trios de acordo com o código informado."""
    players_by_code = {}
    for player in subsession.get_players():
        code = normalize_group_code(player.participant.vars.get('group_code', ''))
        players_by_code.setdefault(code, []).append(player)

    invalid_codes = {
        code: len(players)
        for code, players in players_by_code.items()
        if not code or len(players) != C.PLAYERS_PER_GROUP
    }
    if invalid_codes:
        details = ', '.join(
            f'{code or "(sem código)"}: {count} participante(s)'
            for code, count in invalid_codes.items()
        )
        raise ValueError(
            'Cada código deve ser usado por exatamente 3 participantes. '
            f'Corrija os códigos e reinicie a sessão. Problemas encontrados: {details}'
        )

    matrix = [
        [player.id_in_subsession for player in players]
        for players in players_by_code.values()
    ]

    # Mantém os mesmos trios em todas as 10 rodadas.
    for subsession_in_round in subsession.in_all_rounds():
        subsession_in_round.set_group_matrix(matrix)


def start_round(group: Group):
    now = time.time()
    group.round_start_timestamp = now
    group.round_deadline_timestamp = now + C.ROUND_TIME_SECONDS


def set_results(group: Group):
    players = group.get_players()
    choices = [p.choice for p in players]

    consensus_reached = (
        len(players) == C.PLAYERS_PER_GROUP
        and all(choices)
        and len(set(choices)) == 1
    )

    group.consensus_reached = consensus_reached
    group.consensus_choice = choices[0] if consensus_reached else ''

    for player in players:
        player.consensus_reached = consensus_reached


class GroupCode(Page):
    form_model = 'player'
    form_fields = ['group_code']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def error_message(player: Player, values):
        code = normalize_group_code(values.get('group_code'))
        if not code:
            return 'Digite o código informado pela professora.'
        if len(code) > 20:
            return 'O código deve ter no máximo 20 caracteres.'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        code = normalize_group_code(player.group_code)
        player.group_code = code
        player.participant.vars['group_code'] = code


class GroupFormationWait(WaitPage):
    wait_for_all_groups = True
    after_all_players_arrive = form_groups_by_code
    body_text = 'Aguardando todos os participantes entrarem e informarem seus códigos de grupo.'

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Instructions(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return {'group_code': player.participant.vars.get('group_code', '')}


class SynchronizeRound(WaitPage):
    after_all_players_arrive = start_round
    body_text = 'Aguardando todos os participantes para iniciar a rodada ao mesmo tempo.'


class Question(Page):
    form_model = 'player'
    form_fields = ['choice', 'submission_status']

    @staticmethod
    def get_timeout_seconds(player: Player):
        deadline = player.group.round_deadline_timestamp
        if not deadline:
            return C.ROUND_TIME_SECONDS
        return max(1, deadline - time.time())

    @staticmethod
    def vars_for_template(player: Player):
        item = current_question(player)
        player.question_text = item['question']
        remaining = max(0, player.group.round_deadline_timestamp - time.time())
        return {
            'question_text': item['question'],
            'options': item['options'],
            'remaining_seconds': remaining,
        }

    @staticmethod
    def error_message(player: Player, values):
        choice = values.get('choice')
        if choice and choice not in current_question(player)['options']:
            return 'Selecione uma das alternativas apresentadas.'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Uma alternativa apenas marcada não conta como resposta enviada.
        # Só preservamos a escolha quando houve confirmação explícita pelo botão.
        if timeout_happened or player.submission_status != 'confirmed':
            player.choice = ''
            player.submission_status = 'timeout'

        elapsed = time.time() - player.group.round_start_timestamp
        player.response_time = min(max(elapsed, 0), C.ROUND_TIME_SECONDS)


class WaitForGroup(WaitPage):
    after_all_players_arrive = set_results
    body_text = 'Aguardando os demais participantes do grupo.'


def group_export_rows(player: Player):
    rows = []
    code = player.participant.vars.get('group_code', '')
    for round_number in range(1, C.NUM_ROUNDS + 1):
        player_in_round = player.in_round(round_number)
        group_in_round = player_in_round.group
        for p in group_in_round.get_players():
            rows.append({
                'participante': f'P{p.id_in_group}',
                'codigo_grupo': code,
                'grupo_otree': group_in_round.id_in_subsession,
                'posicao_no_grupo': p.id_in_group,
                'rodada': round_number,
                'categoria': 'Objetos',
                'pergunta': p.question_text or '',
                'resposta': p.choice or '',
                'houve_consenso': 'Sim' if group_in_round.consensus_reached else 'Não',
                'resposta_do_consenso': group_in_round.consensus_choice or '',
                'tempo_segundos': round(p.response_time, 3) if p.response_time is not None else '',
                'timeout': 'Sim' if p.submission_status != 'confirmed' else 'Não',
            })
    return rows


def group_summary(player: Player):
    rows = []
    durations = []
    consensus_total = 0

    for round_number in range(1, C.NUM_ROUNDS + 1):
        group_in_round = player.in_round(round_number).group
        players = group_in_round.get_players()
        valid_times = [p.response_time for p in players if p.response_time is not None]
        duration = max(valid_times) if valid_times else 0
        durations.append(duration)

        if group_in_round.consensus_reached:
            consensus_total += 1

        rows.append({
            'rodada': round_number,
            'consenso': 'Sim' if group_in_round.consensus_reached else 'Não',
            'escolha_consenso': group_in_round.consensus_choice or '—',
            'tempo': round(duration, 2),
        })

    average_duration = sum(durations) / len(durations) if durations else 0
    return rows, consensus_total, round(average_duration, 2)


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        show_download = player.round_number == C.NUM_ROUNDS
        summary_rows = []
        consensus_total = 0
        average_duration = 0

        if show_download:
            summary_rows, consensus_total, average_duration = group_summary(player)

        return {
            'consensus_reached': player.group.consensus_reached,
            'consensus_choice': player.group.consensus_choice,
            'show_download': show_download,
            'group_code': player.participant.vars.get('group_code', ''),
            'summary_rows': summary_rows,
            'consensus_total': consensus_total,
            'average_duration': average_duration,
        }

    @staticmethod
    def js_vars(player: Player):
        if player.round_number != C.NUM_ROUNDS:
            return {'export_rows': [], 'group_code': ''}
        return {
            'export_rows': group_export_rows(player),
            'group_code': player.participant.vars.get('group_code', ''),
        }


page_sequence = [
    GroupCode,
    GroupFormationWait,
    Instructions,
    SynchronizeRound,
    Question,
    WaitForGroup,
    Results,
]
