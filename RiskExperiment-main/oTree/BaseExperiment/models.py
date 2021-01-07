import random
import itertools
from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    ExtraModel,
    Currency,
    currency_range,
)

from .recipes import RECIPES

author = 'Dieter Smeulders'

doc = """
Experiment Sandwich Making and Risk Reporting
"""


class Constants(BaseConstants):
    name_in_url = 'BaseExperiment'
    players_per_group = 3
    num_rounds = 1
    BasePay = Currency(1)
    #    SellingPrice = Currency(1)
    EmployeeRatio = 0.5
    ManagerRatio = 0.25


class GameSession(ExtraModel):
    """Persistent game state linked to each player.
    Holds name of ordered sandwich and its price.
    Implements core game logic independant from other models.
    """
    # TODO: this is a temporary data and should be deleted afterwards
    player = models.Link('Player')
    ordered = models.StringField()
    price = models.CurrencyField()

    def next_order(self, price):
        """Generates and saves next random order"""
        self.ordered = random.choice(list(RECIPES.keys()))
        self.price = price

    def validate(self, sandwich):
        """Validates if submitted sandwich matches ordered
        Returns: valid, reward, errors
        """
        expected = RECIPES[self.ordered]
        mismatches = len(set(sandwich) ^ set(expected))
        if mismatches == 0:
            return True, self.price, 0
        else:
            return False, 0, mismatches


class Subsession(BaseSubsession):

    def creating_session(self):
        reportingconditions = ['voluntary', 'mandatory']
        cultureconditions = ['supportive', 'supportive', 'unsupportive', 'unsupportive']
        for group in self.get_groups():
            group.reportingcondition = random.choice(reportingconditions)
            print(group.reportingcondition)
            group.culturecondition = random.choice(cultureconditions)
            print(group.culturecondition)
        for player in self.get_players():
            self.configure_player(player)
            GameSession.objects.create(player=player)

#    MandatoryCondition = models.IntegerField(initial=1)
#    CultureCondition = models.IntegerField(initial=1)

    # setting gamesession variables

    # Game Related Logic
    def configure_player(self, player):
        p = player.id_in_group

        duration_min = self.session.config[f"P{p}_duration_min"]
        duration_max = self.session.config[f"P{p}_duration_max"]
        player.duration = random.randint(duration_min, duration_max)

        price_min = self.session.config[f"P{p}_price_min"]
        price_max = self.session.config[f"P{p}_price_max"]
        player.price = Currency(random.randint(price_min, price_max))

    def game(self, player):
        return GameSession.objects.get(player=player)

    def start(self, player):
        game = self.game(player)
        game.next_order(player.price)
        game.save()
        return game

    def play(self, player, sandwich):
        """Main gameplay logic:
        - validating submitted sandwich
        - updating metrics
        - advancing to next order
        """
        game = self.game(player)
        valid, reward, errors = game.validate(sandwich)

        if valid:
            player.performed += 1
            player.revenue += reward
        else:
            player.errors += 1
            player.mismatches = max(player.mismatches, errors)
        player.save()

        if valid:
            game.next_order(player.price)
            game.save()

        return game, valid, errors


class Group(BaseGroup):
    reportingcondition = models.StringField()
    culturecondition = models.StringField()


class Player(BasePlayer):
    name = models.StringField
    age = models.StringField

    # All Parameters for the sandwich making task
    """A player parameters and metrics

        Implements communication logic:

        received 'start':
        - send order

        received 'sandwich':
        - validate sandwich

        received valid sandwich:
        - send status (number of sandwiches sold)
        - send new order

        received invalid sandwish:
        - send error messages (with number of mismatches)
        """

    # duration of the round
    duration = models.FloatField()
    # sandwich price for the round
    price = models.CurrencyField()

    # number of valid sandwiches sold
    performed = models.IntegerField(initial=0)
    # total revenue
    revenue = models.CurrencyField(initial=0)
    # number of invalid sandwiches submitted
    errors = models.IntegerField(initial=0)
    # maximal number of mismatched components
    mismatches = models.IntegerField(initial=0)
    # time allocated
    time = models.IntegerField(initial=5)
    # first round performance
    performedR1 = models.IntegerField(initial=0)
    revenueR1 = models.CurrencyField(initial=0)
    errorsR1 = models.IntegerField(initial=0)
    mismatchesR1 = models.IntegerField(initial=0)
    # risk materialisation
    riskmaterialized = models.BooleanField()

    def handle_message(self, message):
        kind = message['type']
        if kind == 'start':
            return self.handle_start()
        elif kind == 'sandwich':
            return self.handle_sandwich(message['components'])
        else:
            raise ValueError("Invalid message received", kind)

    def handle_start(self):
        game = self.subsession.start(self)
        return self.reply(self.order_message(game))

    def handle_sandwich(self, components):
        game, valid, errors = self.subsession.play(self, components)
        if valid:
            return self.reply([self.status_message(), self.order_message(game)])
        else:
            return self.reply(self.errors_message(errors))

    def reply(self, message):
        return {self.id_in_group: message}

    def order_message(self, game):
        return {'type': 'order', 'order': game.ordered}

    def errors_message(self, errors):
        return {'type': 'error', 'mismatches': errors}

    def status_message(self):
        return {'type': 'status', 'performed': self.performed}

    def reset_after_practice(self):
        self.performed = 0
        self.revenue = 0
        self.errors = 0
        self.mismatches = 0

    def set_up_second_round(self):
        self.performedR1 = self.performed
        self.revenueR1 = self.revenue
        self.errorsR1 = self.errors
        self.mismatchesR1 = self.mismatches
        self.performed = 0
        self.revenue = 0
        self.errors = 0
        self.mismatches = 0
        manager = self.group.get_player_by_id(3)
        if self.id_in_group == 1:
            self.time = manager.Ntime
        if self.id_in_group == 2:
            self.time = manager.Stime

    def handleriskevent(self):
        manager = self.group.get_player_by_id(3)
        probability = random.random()
        if probability > 0.5:
            self.riskmaterialized = True
        else:
            self.riskmaterialized = False

        if (self.id_in_group == 1 and manager.NEM == 1 and self.riskmaterialized == True):
            self.price = 0.7
        if (self.id_in_group == 2 and manager.NEM == 1 and self.riskmaterialized == True):
            self.price = 0.7

    # All other parameters
    report_displayed = models.BooleanField(initial=False)

    NLocationChoice = models.IntegerField(
        label='',
        choices=[
            [1, 'Location A'],
            [2, 'Location B']],
        widget=widgets.RadioSelectHorizontal
    )
    SLocationChoice = models.IntegerField(
        label='',
        choices=[
            [1, 'Location A'],
            [2, 'Location B']],
        widget=widgets.RadioSelectHorizontal
    )
    NReportedPerf = models.IntegerField(
        label='Please report your sales performance below.',
        min=0, max=30)

    SReportedPerf = models.IntegerField(
        label='Please report your sales performance below.',
        min=0, max=30)

    NReportedRiskManD = models.LongStringField(
        label='You are now obliged to report on risks identified in your region (if any) here. '
              'Note that you cannot leave this box blank. '
              'When you did not identify any risk to report, say so.'
    )

    NReportedRiskVol = models.LongStringField(
        label='You are now allowed to report on risks identified in your region (if any) here. '
              'Note that you can leave this box blank. '
              'When you did not identify any risk to report, you can, if wish, say so.',
        blank=True
    )

    SReportedRiskManD = models.LongStringField(
        label='You are now obliged to report on risks identified in your region (if any). '
              'Note that you cannot leave this box blank. '
              'When you did not identify any risk to report, say so.'
    )

    SReportedRiskVol = models.LongStringField(
        label='You are now allowed to report on risks identified in your region (if any) here. '
              'Note that you can leave this box blank. '
              'When you did not identify any risk to report, you can, if wish, say so.',
        blank=True
    )
    Ntime = models.IntegerField(
        label='Northern regional manager:', min=0, max=10,
        initial=1
    )

    Stime = models.IntegerField(
        label='Southern regional manager:', min=0, max=10,
        initial=1
    )
    NEM = models.IntegerField(
        label='In the north:',
        choices=[[1, 'No'], [2, 'Yes']],
        widget=widgets.RadioSelectHorizontal
    )
    SEM = models.IntegerField(
        label='In the south:',
        choices=[[1, 'No'], [2, 'Yes']],
        widget=widgets.RadioSelectHorizontal
    )

    # PostQuestionnaire
    extime = models.IntegerField(
        label='How many minutes do you think the supervisor will offer you?',
        min=0, max=10
    )
    exbudget = models.IntegerField(
        label='...use the emergency budget if you reported the risks that you were exposed to?',
        choices=[[1, 'Little'], [2, 'To a small extent'], [3, 'To some extent'], [4, 'To a large extent'],
                 [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    exshort = models.IntegerField(
        label='...offer you a shorter production time if you reported the risks that you were exposed to?',
        choices=[[1, 'Little'], [2, 'To a small extent'], [3, 'To some extent'], [4, 'To a large extent'],
                 [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    exlong = models.IntegerField(
        label='...offer you a longer production time if you reported the risks that you were exposed to?',
        choices=[[1, 'Little'], [2, 'To a small extent'], [3, 'To some extent'], [4, 'To a large extent'],
                 [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    expect1 = models.IntegerField(
        label='... would be facing risks in her/his region?',
        choices=[[1, 'Little'], [2, 'To a small extent'], [3, 'To some extent'], [4, 'To a large extent'],
                 [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    expect2 = models.IntegerField(
        label='... would disclose all risks that she/he faces to the supervisor?',
        choices=[[1, 'Little'], [2, 'To a small extent'], [3, 'To some extent'], [4, 'To a large extent'],
                 [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    expect3 = models.IntegerField(
        label='When you were reporting to the supervisor, how well did you think you performed compared to the other regional manager?',
        choices=[[1, 'Way below the other regional manager'], [2, 'To a small extent'], [3, 'The same'], [4, 'To a large extent'],
                 [5, 'Way above the other regional manager']],
        widget=widgets.RadioSelectHorizontal
    )
    riskiden = models.IntegerField(
        label='Was there any risk to the sales performance of your region in the local market survey report?',
        choices=[[1, 'Yes'], [2, 'No']],
        widget=widgets.RadioSelectHorizontal
    )

    riskperc = models.IntegerField(
        label='What is the probability/likelihood that a new competitor come to your neighborhood? (min=0%, max=100%)', min=0, max=100)

    riskcert = models.IntegerField(
        label='How certain are you that a new competitor will come to your neighborhood?',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''],
                 [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )

    riskseri = models.IntegerField(
        label='How serious do you think the potential impacts of a new competitor on the sales performance of your '
              'region would be?',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''],
                 [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )

    riskimp1 = models.IntegerField(
        label='How much importance do you think the company places to risk management?',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''],
                 [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )

    riskimp2 = models.IntegerField(
        label='How much importance do you think the company places to internal communication of risk information?',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''],
                 [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )

    safety1 = models.IntegerField(
        label='If you make a mistake in this company, it is often held against you.',
        choices=[[1, 'Very inaccurate'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very accurate']],
        widget=widgets.RadioSelectHorizontal
    )
    safety2 = models.IntegerField(
        label='Members of this company are able to bring up problems and tough issues.',
        choices=[[1, 'Very inaccurate'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very accurate']],
        widget=widgets.RadioSelectHorizontal
    )
    safety3 = models.IntegerField(
        label='People in this organization sometimes reject others for being different.',
        choices=[[1, 'Very inaccurate'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very accurate']],
        widget=widgets.RadioSelectHorizontal
    )
    safety4 = models.IntegerField(
        label='It is safe to take risks in this company.',
        choices=[[1, 'Very inaccurate'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very accurate']],
        widget=widgets.RadioSelectHorizontal
    )
    safety5 = models.IntegerField(
        label='It is difficult to ask other members of this company for help.',
        choices=[[1, 'Very inaccurate'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very accurate']],
        widget=widgets.RadioSelectHorizontal
    )
    safety6 = models.IntegerField(
        label='No one in this company would deliberately act in a way that undermines my efforts.',
        choices=[[1, 'Very inaccurate'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very accurate']],
        widget=widgets.RadioSelectHorizontal
    )
    safety7 = models.IntegerField(
        label='Working with members of this company, my unique skills and talents are valued and utilized.',
        choices=[[1, 'Very inaccurate'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very accurate']],
        widget=widgets.RadioSelectHorizontal
    )
    riskimp3 = models.IntegerField(
        label='To what extent did the company place emphasis on the communication of risk information?',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    riskimp4 = models.IntegerField(
        label='To what extent did the company place emphasis on management of environmental risks?',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    riskimp5 = models.IntegerField(
        label='To what extent did the company value timely communication of risk information?',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    repimp1 = models.IntegerField(
        label='...show the supervisor that you made the right location choice',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )

    repimp2 = models.IntegerField(
        label='...provide all the information that you had about your region to the supervisor',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    repimp3 = models.IntegerField(
        label='...perform well',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    repimp4 = models.IntegerField(
        label='...report a high performance to the supervisor',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    repimp5 = models.IntegerField(
        label='...be honest in your report',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    repimp6 = models.IntegerField(
        label='...show the supervisor that you are competent',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )

    repimp7 = models.IntegerField(
        label='...report the risks that you faced to the supervisor',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    factor1 = models.IntegerField(
        label='1. Maximizing your payoff',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    factor2 = models.IntegerField(
        label='2. Receiving a higher production time for the next round',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    factor3 = models.IntegerField(
        label='3. Helping the company',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    factor4 = models.IntegerField(
        label='4. Helping the supervisor',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    factor5 = models.IntegerField(
        label='5. Being honest',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    factor6 = models.IntegerField(
        label='6. Seeking help from the supervisor',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    factor7 = models.IntegerField(
        label='7. Looking honest in the eyes of the supervisor',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    factor8 = models.IntegerField(
        label='8. Fulfilling your responsibilities as a regional manager',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    factor9 = models.IntegerField(
        label='1. Looking competent in the eyes of the supervisor',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    factor10 = models.IntegerField(
        label='2. Looking more competent than the other regional manager in the eyes of the supervisor',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    factor11 = models.IntegerField(
        label='3. Showing that you made a correct location decision',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    factor12 = models.IntegerField(
        label='4. Looking good in the eyes of the supervisor',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    factor13 = models.IntegerField(
        label='5. Outperforming the other regional manager',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    factor14 = models.IntegerField(
        label='6. Avoiding creating a negative impression on the supervisor',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    factor15 = models.IntegerField(
        label='7. Showing that you are in control of your region',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    sup1 = models.IntegerField(
        label='the superior would have a negative image of me',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    sup2 = models.IntegerField(
        label='my image in the eyes of the supervisor would be improved',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    sup3 = models.IntegerField(
        label='I would look bad in the eyes of the supervisor',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    sup4 = models.IntegerField(
        label='the supervisor would think better of me',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    sup5 = models.IntegerField(
        label='the supervisor would think worse of me',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    sup6 = models.IntegerField(
        label='the supervisor would give me less time',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    sup7 = models.IntegerField(
        label='the supervisor would give me more time',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    sup8 = models.IntegerField(
        label='the supervisor would help me',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    sup9 = models.IntegerField(
        label='the supervisor would appreciate it',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )

    sup10 = models.IntegerField(
        label='the supervisor would penalize me',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    resp1 = models.IntegerField(
        label='I felt responsible to inform the company about the risks that I faced.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    resp2 = models.IntegerField(
        label='It was my responsibility to inform the supervisor about the risks I was exposed to.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    repq1 = models.IntegerField(
        label='How much effort did you devote to reporting risk information to the supervisor?',
        choices=[[1, 'Minimum effort'], [2, ''], [3, ''], [4, ''], [5, 'Maximum effort']],
        widget=widgets.RadioSelectHorizontal
    )
    repq2 = models.IntegerField(
        label='How informative do you assess your risk report to the supervisor?',
        choices=[[1, 'Not at all informative'], [2, ''], [3, ''], [4, ''], [5, 'Very informative']],
        widget=widgets.RadioSelectHorizontal
    )
    manvol1 = models.IntegerField(
        label='The company requires its managers to report to their supervisors the risks they are exposed to.',
        choices=[[1, 'Very inaccurate'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very accurate']],
        widget=widgets.RadioSelectHorizontal
    )
    manvol2 = models.IntegerField(
        label='In this company, it is compulsory for managers to disclose the risks they face to the superior in their '
              'performance reports.',
        choices=[[1, 'Very inaccurate'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very accurate']],
        widget=widgets.RadioSelectHorizontal
    )
    manvol3 = models.IntegerField(
        label='In this company, managers are mandated to disclose the risks they face to their supervisors.',
        choices=[[1, 'Very inaccurate'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very accurate']],
        widget=widgets.RadioSelectHorizontal
    )
    trust1 = models.IntegerField(
        label='I trust this company.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    trust2 = models.IntegerField(
        label='I would recommend my friends to invest, buy, work for, or work with this company.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    trust3 = models.IntegerField(
        label='In general, I believe that this company’s motives and intentions are good.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    trust4 = models.IntegerField(
        label='I am trusted at this company.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    trust5 = models.IntegerField(
        label='My company fully trusts me.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    trust6 = models.IntegerField(
        label='My company trusts its employees.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    suptrust1 = models.IntegerField(
        label='The supervisor was fair in dealing with the regional managers.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    suptrust2 = models.IntegerField(
        label='The supervisor had a strong sense of justice.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    suptrust3 = models.IntegerField(
        label='I trust the supervisor.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    suptrust4 = models.IntegerField(
        label='The supervisor was caring.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    suptrust5 = models.IntegerField(
        label='I can count on the supervisor for help if I have difficulties with my job.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    suptrust6 = models.IntegerField(
        label='The supervisor was concerned about my welfare.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    mandatory = models.StringField(
        label='Why do you think your company chose a mandatory risk reporting policy?',
    )
    voluntary = models.StringField(
        label='Why do you think your company chose a voluntary risk reporting policy?',
    )
    perf1 = models.IntegerField(
        label='',
        choices=[[1, 'Way below the average'], [2, ''], [3, 'Average'], [4, ''], [5, 'Way above the average']],
        widget=widgets.RadioSelectHorizontal
    )
    perf2 = models.IntegerField(
        label='',
        choices=[[1, 'Way below my expectation'], [2, ''], [3, 'In line with my expectation'], [4, ''],
                 [5, 'Way above my expectation']],
        widget=widgets.RadioSelectHorizontal
    )
    riskat1 = models.IntegerField(
        label='I can be rather incautious and take big risks.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    riskat2 = models.IntegerField(
        label='I often dare to do risky things which other people are reluctant to do.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    riskat3 = models.IntegerField(
        label='I think that I am often less cautious than people in general.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    riskat4 = models.IntegerField(
        label='I am a bit of a coward.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    riskat5 = models.IntegerField(
        label='I am rather adventurous and like to take chances in various situations.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    riskat6 = models.IntegerField(
        label='I am always very cautious and think of safety first.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    riskat7 = models.IntegerField(
        label='I have never deliberately taken any big risks that I have been able to avoid in important situations.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    riskat8 = models.IntegerField(
        label='I never take any risks that I can avoid when it comes to important things.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    riskat9 = models.IntegerField(
        label='I always try to avoid situations involving a risk of getting into trouble with other people.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    riskat10 = models.IntegerField(
        label='I like to avoid doing things for which I run the risk of being criticized and blamed if I fail.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    riskat11 = models.IntegerField(
        label='I think I am often rather bold and fearless in my actions.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    opt1 = models.IntegerField(
        label='In uncertain times, I usually expect the best.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    opt2 = models.IntegerField(
        label='If something can go wrong for me, it will.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    opt3 = models.IntegerField(
        label='I am always optimistic about my future.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    opt4 = models.IntegerField(
        label='I hardly ever expect things to go my way.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    opt5 = models.IntegerField(
        label='I rarely count on good things happening to me.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    opt6 = models.IntegerField(
        label='Overall, I expect more good things to happen to me than bad.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    unc1 = models.IntegerField(
        label='Unforeseen events upset me greatly.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    unc2 = models.IntegerField(
        label='It frustrates me not having all information I need.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    unc3 = models.IntegerField(
        label='One should always look ahead so as to avoid surprises.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    unc4 = models.IntegerField(
        label='A small, unforeseen event can spoil everything, even with the best of planning.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    unc5 = models.IntegerField(
        label='I always want to know what the future has in store for me.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    unc6 = models.IntegerField(
        label='I cannot stand being taken by surprises.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    unc7 = models.IntegerField(
        label='I should be able to organize everything in advance.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    unc8 = models.IntegerField(
        label='Uncertainty keeps me from living a full life.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    unc9 = models.IntegerField(
        label='When it is time to act, uncertainty paralyses me.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    unc10 = models.IntegerField(
        label='When I am uncertain, I cannot function well.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    unc11 = models.IntegerField(
        label='The smallest doubt can stop me from acting.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    unc12 = models.IntegerField(
        label='I must get away from all uncertain situations.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    dark1 = models.IntegerField(
        label='I tend to want others to admire me.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    dark2 = models.IntegerField(
        label='I tend to want others to pay attention to me.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    dark3 = models.IntegerField(
        label='I tend to expect special favors from others.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    dark4 = models.IntegerField(
        label='I tend to seek prestige or status.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    dark5 = models.IntegerField(
        label='I tend to lack remorse.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    dark6 = models.IntegerField(
        label='I tend to be callous or insensitive.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    dark7 = models.IntegerField(
        label='I tend to not be too concerned with morality or the morality of my actions.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    dark8 = models.IntegerField(
        label='I tend to be cynical.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    dark9 = models.IntegerField(
        label='I have used deceit or lied to get my way.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    dark10 = models.IntegerField(
        label='I tend to manipulate others to get my way.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    dark11 = models.IntegerField(
        label='I tend to exploit others towards my own end.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    dark12 = models.IntegerField(
        label='I have used flattery to get my way.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    gen1 = models.IntegerField(
        label='The sandwich-making task was boring.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    gen2 = models.IntegerField(
        label='I wanted to maximize my payoff in this study.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    gen3 = models.IntegerField(
        label='I enjoyed participating in this study.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    gen4 = models.IntegerField(
        label='The instructions were clearly formulated.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    sperf = models.IntegerField(
        label='Which regional manager performed better in the first round',
        choices=[[1, 'Northern regional manager'], [2, 'Southern regional manager'],
                 [3, 'Both performed equally well']],
        widget=widgets.RadioSelectHorizontal
    )
    sfact1 = models.IntegerField(
        label='How well each regional manager performed in the first round',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    sfact2 = models.IntegerField(
        label='How honest each regional manager was',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    sfact3 = models.IntegerField(
        label='Risks that each regional manager faced',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    sfact4 = models.IntegerField(
        label='Maximizing your payoff',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    sfact5 = models.IntegerField(
        label='Acting in line with the company’s interests',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    sfact6 = models.IntegerField(
        label='Minimizing harm to the company',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    sfact7 = models.IntegerField(
        label='Allocating equal production time to regional managers',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    sfact8 = models.IntegerField(
        label='The extent to which detailed risk information about each region is provided',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    sfact9 = models.IntegerField(
        label='How informative is the report of each regional manager about the state of his/her own region.',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    sfact10 = models.IntegerField(
        label='Being supportive and helpful',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    sfact11 = models.IntegerField(
        label='Fulfilling your responsibilities as a supervisor',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    emfact1 = models.IntegerField(
        label='Maximizing your payoff',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    emfact2 = models.IntegerField(
        label='Helping the regional managers to maximize their payoffs',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    emfact3 = models.IntegerField(
        label='Being fair to the regional managers',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    emfact4 = models.IntegerField(
        label='Minimizing risk to the company',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    emfact5 = models.IntegerField(
        label='Fulfilling your responsibilities as a supervisor',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    emfact6 = models.IntegerField(
        label='Being supportive and helpful',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    north1 = models.IntegerField(
        label='The report of the northern regional manager was informative',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    north2 = models.IntegerField(
        label='The northern regional manager provided all relevant risk information',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    south1 = models.IntegerField(
        label='The report of the southern regional manager was informative',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    south2 = models.IntegerField(
        label='The southern regional manager provided all relevant risk information.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure1 = models.IntegerField(
        label='I don’t like situations that are uncertain.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure2 = models.IntegerField(
        label='I dislike questions which could be answered in many different ways.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure3 = models.IntegerField(
        label='I find that a well ordered life with regular hours suits my temperament.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure4 = models.IntegerField(
        label='I feel uncomfortable when I don’t understand the reason why an event occurred in my life.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure5 = models.IntegerField(
        label='I feel irritated when one person disagrees with what everyone else in a group believes.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure6 = models.IntegerField(
        label='I don’t like to go into a situation without knowing what I can expect from it.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure7 = models.IntegerField(
        label='When I have made a decision, I feel relieved.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure8 = models.IntegerField(
        label='When I am confronted with a problem, I’m dying to reach a solution very quickly.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure9 = models.IntegerField(
        label='I would quickly become impatient and irritated if I would not find a solution to a problem immediately.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure10 = models.IntegerField(
        label='I don’t like to be with people who are capable of unexpected actions.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure11 = models.IntegerField(
        label='I dislike it when a person’s statement could mean many different things.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure12 = models.IntegerField(
        label='I find that establishing a consistent routine enables me to enjoy life more.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure13 = models.IntegerField(
        label='I enjoy having a clear and structured mode of life.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure14 = models.IntegerField(
        label='I do not usually consult many different opinions before forming my own view.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure15 = models.IntegerField(
        label='I dislike unpredictable situations.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
