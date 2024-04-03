import random

from otree.api import *

import random
import time
import itertools
import math



author = 'Elman Torres'
doc = """
Actividad Transcribir
"""


class Constants(BaseConstants):
    name_in_url = 'Transcribir'
    players_per_group = None
    #num_game_rounds = 1
    num_practice_rounds = 2
    num_real_rounds = 100
    num_rounds = num_practice_rounds + num_real_rounds
    payment_correct_answer = 50
    pago_participacion = 10000


class Subsession(BaseSubsession):
    is_practice_round = models.BooleanField()
    real_round_number = models.IntegerField()


def creating_session(subsession):
    tratamientos = itertools.cycle(['Control', 'T1', 'T2'])
    for player in subsession.get_players():
        player.tratamiento = next(tratamientos)

    subsession.is_practice_round = (
            subsession.round_number <= Constants.num_practice_rounds
    )
    if not subsession.is_practice_round:
        subsession.real_round_number = (
             subsession.round_number - Constants.num_practice_rounds
         )



class Group(BaseGroup):
    pass


class Player(BasePlayer):
    palabras = models.StringField()
    texto = models.StringField()
    correctas = models.IntegerField()
    tratamiento = models.StringField()
    numsolinfo = models.IntegerField()
    timebegin = models.FloatField()
    timeround = models.FloatField()
    is_mobile = models.BooleanField()
    pago_estimado = models.FloatField()


# def creating_session(subsession):
#     tratamientos = itertools.cycle(['Control', 'T1', 'T2'])
#     for player in subsession.get_players():
#         player.tratamiento = next(tratamientos)




# FUNCTIONS
def listas(cadena1):
    list1=cadena1.split()
    return list1


def compara(list1,list2):
    comparacion=[]
    for item in list1:
        if item in list2:
            comparacion.append(item)
    if len(comparacion)>=0:
        return len(comparacion)


def genera():
    p=4
    q=9
    list1=[]
    for j in range(q):
        new = ""
        for i in range(p):
            num = random.randint(97,122)
            new += chr(num)
        list1.append(new)
    cadena = " ".join(list1)
    return cadena

# def formato_tiempo(segundos):
#     horas = int(segundos / 60 / 60)
#     segundos -= horas*60*60
#     minutos = int(segundos/60)
#     segundos -= minutos*60
#     segundos1 = math.floor(segundos)
#     cadena1 = str(horas)+"h:"+str(minutos)+"m:"+str(segundos1)+"s."
#     return cadena1


def get_timeout_seconds(player):
    participant = player.participant
    return participant.expiry - time.time()

# PAGES
class Inicio(Page):
    form_model = 'player'
    form_fields = ['is_mobile']

    def error_message(player: Player, values):
        if values['is_mobile']:
            return "Lo Lamentamos, este experimento no permite navegadores en telefonos celulares o tablets. Si quiere continuar, vuelva a ingresar en un computador con teclado.Gracias"


    def is_displayed(player):
        return player.round_number == 1

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.combined_payoff = Constants.pago_participacion
        participant.expiry = time.time() + 10*60






class Transcribir(Page):
    form_model = "player"
    form_fields = ["palabras","numsolinfo"]


    get_timeout_seconds = get_timeout_seconds



    @staticmethod
    def is_displayed(player):
            return get_timeout_seconds(player) > 3


    @staticmethod
    def vars_for_template(player: Player):
            player.texto = genera()
            player.timebegin = float(time.time())
            return {
            "texto": player.texto,
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        lista1 = listas(player.texto)
        lista2 = listas(player.palabras)
        player.correctas = compara(lista1, lista2)
        player.payoff = player.correctas * Constants.payment_correct_answer
        participant = player.participant
        participant.combined_payoff += player.payoff
        player.timeround = float(time.time()) - player.timebegin

        # player.numsolinfo += player.numsolinfo




class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        subsession = player.subsession
        return subsession.is_practice_round

class FinalizaPractica(Page):
    @staticmethod
    def is_displayed(player):
            return player.round_number == 2

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.combined_payoff = Constants.pago_participacion
        participant.expiry = time.time() + 10 * 60
        participant.pago_estimado = player.field_maybe_none('pago_estimado')
        player.pago_estimado = None




class Estimacion(Page):
    form_model = 'player'
    form_fields = ['pago_estimado']



    @staticmethod
    def is_displayed(player: Player):
        jugador = False
        if player.tratamiento != 'T1' and player.round_number == Constants.num_rounds:
            jugador = True
        return jugador

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.pago_estimado = player.pago_estimado



class ResultadosEst(Page):

    @staticmethod
    def is_displayed(player: Player):
        jugador = False
        if player.tratamiento != 'T1' and player.round_number == Constants.num_rounds:
            jugador = True
        return jugador

class CombineResults(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == Constants.num_rounds



page_sequence = [Inicio, Transcribir, Results, FinalizaPractica , Estimacion, ResultadosEst, CombineResults]
