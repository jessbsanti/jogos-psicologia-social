from otree.api import *

doc = "Lobby para coleta do código do grupo."


class C(BaseConstants):
    NAME_IN_URL = "lobby"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    group_code = models.StringField(
        label="Código do grupo"
    )
    categoria = models.StringField(
        label="Categoria",
        choices=["Objetos", "Dilemas"],
    )


def normalize_group_code(value):
    return (value or "").strip().upper()


class EnterGroupCode(Page):
    form_model = "player"
    form_fields = [
        "group_code",
        "categoria",
    ]

    @staticmethod
    def error_message(player, values):
        code = normalize_group_code(values["group_code"])

        if not code:
            return "Digite o código do grupo."

        if len(code) > 20:
            return "O código deve ter no máximo 20 caracteres."

    @staticmethod
    def before_next_page(player, timeout_happened):
        code = normalize_group_code(player.group_code)
        player.group_code = code
        player.participant.vars["group_code"] = code
        player.participant.vars["categoria"] = player.categoria


page_sequence = [EnterGroupCode]