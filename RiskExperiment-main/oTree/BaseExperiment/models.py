import random
import itertools
import otreeutils
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
    players_per_group = 2
    num_rounds = 1
    BasePay = Currency(5)
    BasePrice = Currency(1)
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

    # revenues
    ownshare = models.CurrencyField()
    supervisorshare = models.CurrencyField()
    firmshare = models.CurrencyField()

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

    def calcrevenue(self):
        if self.riskmaterialized == 1:
            self.ownshare = self.revenue * 0.5 * 0.7 + self.revenueR1 * 0.5
            self.supervisorshare = self.revenue * 0.25 * 0.7 + self.revenueR1 * 0.25
            self.firmshare = self.revenue * 0.25 * 0.7 + self.revenueR1 * 0.25
        else:
            self.ownshare = self.revenue * 0.5 + self.revenueR1 * 0.5
            self.firmshare = self.revenue * 0.25 + self.revenueR1 * 0.25
            if (self.id_in_group == 1 and self.group.get_player_by_id(3).NEM):
                self.supervisorshare = self.revenue * 0.25 + self.revenueR1 * 0.25 - 0.1
            if (self.id_in_group == 2 and self.group.get_player_by_id(3).SEM):
                self.supervisorshare = self.revenue * 0.25 + self.revenueR1 * 0.25 - 0.1
            else:
                self.supervisorshare = self.revenue * 0.25 + self.revenueR1 * 0.25

    # All other parameters
    report_displayed = models.BooleanField(initial=False)

    NLocationChoice = models.IntegerField(
        label='',
        choices=[
            [1, 'Location A'],
            [2, 'Location B']],
        widget=widgets.RadioSelectHorizontal
    )
    Q1 = models.IntegerField(
        label='1. What is your role?',
        choices=[[1, 'Shop manager'], [2, 'Supervisor']],
        widget=widgets.RadioSelectHorizontal
    )
    Q2 = models.IntegerField(
        label='2. Who has access to the local market survey reports in the region?',
        choices=[[1, 'Only the shop manager'], [2, 'Only the supervisor'],
                 [3, 'Both the shop manager and the supervisor']],
        widget=widgets.RadioSelectHorizontal
    )
    Q3 = models.IntegerField(
        label='3. How much time does the shop manager have to make sandwiches?',
        choices=[[1, '10 minutes'], [2, '5 minutes']],
        widget=widgets.RadioSelectHorizontal
    )
    Q4 = models.IntegerField(
        label='4. What will the supervisor do?',
        choices=[[1, 'Decide the location of the new shop.'], [2, 'The supervisor will rate the performance of the shop manager '
                                            'based on his/her decision making and sales revenue '
                                            'in a range from 1 (Very poor) to 5 (Excellent)']],
        widget=widgets.RadioSelectHorizontal
    )
    Q5 = models.IntegerField(
        label='5. How is the sales revenue of the shop computed?',
        choices=[[1, 'Sales revenue is the number of clients attracted.'],
                 [2, 'Sales revenue is the number of sandwiches made.'],
                 [3, 'Sales revenue is the product of the number of sandwiches made '
                     'and the selling price of each sandwich. '
                     'The current selling price in this location is about 1 euro.']],
        widget=widgets.RadioSelectHorizontal
    )
    Q6 = models.IntegerField(
        label='6. Does AC Company adopt a mandatory risk reporting policy?',
        choices=[[1, 'Yes'], [2, 'No']],
        widget=widgets.RadioSelectHorizontal
    )
    Q7 = models.IntegerField(
        label='7. At AC Company, can people easily ask others for help in the face of difficulty?',
        choices=[[1, 'Yes'],
                 [2, 'No']],
        widget=widgets.RadioSelectHorizontal
    )
    Q8 = models.IntegerField(
        label='8. At AC Company, can people talk to others about what could go wrong without being criticized?',
        choices=[[1, 'Yes'],
                 [2, 'No']],
        widget=widgets.RadioSelectHorizontal
    )

    NReportedRiskManD = models.LongStringField(
        label='You are now obliged to report on risks to your sales revenue (if any) here.'
              ' Note that you cannot leave this box blank. '
              'In case you identified no risk, say so.'
    )

    NReportedRiskVol = models.LongStringField(
        label='You are now allowed to report on risks to your sales revenue (if any) here.'
              ' Note that you can leave this box blank and the supervisor will not receive your report.'
              'In case you identified no risk, you can say so, if you wish.',
        blank=True
    )

    Evaluation = models.IntegerField(
        label='Please rate the performance of the shop manager.',
        choices=[[1, 'Very Poor'], [2, 'Poor'], [3, 'Average'], [4, 'Good'], [5, 'Excellent']],
        widget=widgets.RadioSelectHorizontal
    )

    # PostQuestionnaire

    closure1 = models.IntegerField(
        label='I did not disclose all relevant risk information to the supervisor.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure2 = models.IntegerField(
        label='I did not devote much effort to reporting risks to the supervisor.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure3 = models.IntegerField(
        label='I honestly reported all the risk information that I had to the supervisor.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure4 = models.IntegerField(
        label='I reported the risk information that I had to the supervisor as objectively as possible.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure5 = models.IntegerField(
        label='I felt that my risk report was quite informative.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure6 = models.IntegerField(
        label='I did not give an accurate account of the risks that I faced to the supervisor.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure7 = models.IntegerField(
        label='I withheld some unfavorable information from the supervisor.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure8 = models.IntegerField(
        label='I focused on favorable information more than unfavorable information in my risk report.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure9 = models.IntegerField(
        label='I tried to cover up some unfavorable news by emphasizing the favorable information.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure10 = models.IntegerField(
        label='I did not include information that had negative implications for my performance evaluation.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure11 = models.IntegerField(
        label='I felt responsible to inform the supervisor about the risks I was exposed to.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    closure12 = models.IntegerField(
        label='It was my responsibility to provide the supervisor with '
              'the detailed information about the potential risks which I faced.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    S1 = models.IntegerField(
        label='How informative the risk report of the shop manager was?',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    S2 = models.IntegerField(
        label='To what extent do you think the shop manager provided all relevant risk information to you?',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    S3 = models.IntegerField(
        label='How detailed the risk report of the shop manager was?',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    S4 = models.IntegerField(
        label='How useful did you find the risk report of the shop manager for the risk management purposes? ',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    S5 = models.IntegerField(
        label='How accurate did you find the risk report of the shop manager?',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    S6 = models.IntegerField(
        label='How severe did you find the potential risks to the shop given the report of the shop manager?',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    importance1 = models.IntegerField(
        label='...placed importance on risk management?',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    importance2 = models.IntegerField(
        label='...placed emphasis on the timely communication of risk information?',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    importance3 = models.IntegerField(
        label='...placed value on open sharing of risk information?',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    importance4 = models.IntegerField(
        label='...facilitated communication of risk information?',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    image1 = models.IntegerField(
        label='the superior would have a negative image of me',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    image2 = models.IntegerField(
        label='my image in the eyes of the supervisor would be improved',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    image3 = models.IntegerField(
        label='I would look bad in the eyes of the supervisor',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    image4 = models.IntegerField(
        label='the supervisor would think better of me',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    image5 = models.IntegerField(
        label='the supervisor would think worse of me',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    image6 = models.IntegerField(
        label='the supervisor would appreciate it',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    image7 = models.IntegerField(
        label='the supervisor would penalize me',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    factor1 = models.IntegerField(
        label='..report the risks that you faced to the supervisor?',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    factor2 = models.IntegerField(
        label='..provide all the information that you had about your region to the supervisor?',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    factor3 = models.IntegerField(
        label='..be honest in your report?',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    factor4 = models.IntegerField(
        label='..show the supervisor that you made the right location choice?',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    factor5 = models.IntegerField(
        label='..report risks in such a way that could have positively impact your performance evaluation?',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    factor6 = models.IntegerField(
        label='..look good in the eyes of the supervisor?',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    factor7 = models.IntegerField(
        label='..look competent in the eyes of the supervisor?',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    factor8 = models.IntegerField(
        label='..avoid creating a negative impression on the supervisor?',
        choices=[[1, 'Little'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very much']],
        widget=widgets.RadioSelectHorizontal
    )
    trust1 = models.IntegerField(
        label='I felt that the company trusts me to report risks.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    trust2 = models.IntegerField(
        label='The firm risk reporting policy showed that the firm does not trust its employees.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    trust3 = models.IntegerField(
        label='The firm risk reporting policy was a clear sign of distrust in employees.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    oblig1 = models.IntegerField(
        label='I felt obliged to disclose the risk information that I had to the supervisor.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    oblig2 = models.IntegerField(
        label='I felt that I can easily share the risks to my sales revenue to the supervisor.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    oblig3 = models.IntegerField(
        label='I felt that I can openly share unfavorable risk information with the supervisor without being punished.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    oblig4 = models.IntegerField(
        label='I felt that the risks I faced were because of the decision that I had taken. ',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    oblig5 = models.IntegerField(
        label='I felt that I should manage the risks that I faced on my own. ',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    oblig6 = models.IntegerField(
        label='I felt that the risks were not so severe for the company. ',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    oblig7 = models.IntegerField(
        label='I felt that the potential impacts of a new competitor on the sales performance is serious.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
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
    manvol1 = models.IntegerField(
        label='The company requires its managers to report to their supervisors the risks they are exposed to.',
        choices=[[1, 'Very inaccurate'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very accurate']],
        widget=widgets.RadioSelectHorizontal
    )
    manvol2 = models.IntegerField(
        label='In this company, it is compulsory for managers to report the risks they face to the superior in their '
              'performance reports.',
        choices=[[1, 'Very inaccurate'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very accurate']],
        widget=widgets.RadioSelectHorizontal
    )
    manvol3 = models.IntegerField(
        label='In this company, managers are mandated to disclose the risks they face.',
        choices=[[1, 'Very inaccurate'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Very accurate']],
        widget=widgets.RadioSelectHorizontal
    )
    reason1 = models.IntegerField(
        label='To encourage honesty and trust.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    reason2 = models.IntegerField(
        label='To facilitate timely communication of risk information.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    reason3 = models.IntegerField(
        label='To collect important risk information and manage them at the firm level.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    reason4 = models.IntegerField(
        label='To fit the culture of the company.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    reason5 = models.IntegerField(
        label='To evaluate the decisions of the managers.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
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
        label='I am always very cautious and think of safety first.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    riskat4 = models.IntegerField(
        label='I always try to avoid situations involving a risk of getting into trouble with other people.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    riskat5 = models.IntegerField(
        label='I like to avoid doing things for which I run the risk of being criticized and blamed if I fail.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    opt1 = models.IntegerField(
        label='In uncertain times, I usually expect the best.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    opt2 = models.IntegerField(
        label='I rarely count on good things happening to me.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    opt3 = models.IntegerField(
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
        label='I cannot stand being taken by surprises.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, ''], [6, ''], [7, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    gender = models.IntegerField(
        label='What is your gender?',
        choices=[[1, 'Male'], [2, 'Female'], [3, 'Other']],
        widget=widgets.RadioSelectHorizontal
    )
    age = models.IntegerField(
        label='How old are you?',
        min=17, max=80)
    WorkExperience = models.IntegerField(
        label='How many months of work experience do you have?',
        min=0, max=100)
    gen1 = models.IntegerField(
        label='My task was boring.',
        choices=[[1, 'Strongly disagree'], [2, ''], [3, ''], [4, ''], [5, 'Strongly agree']],
        widget=widgets.RadioSelectHorizontal
    )
    gen2 = models.IntegerField(
        label='May task was difficult.',
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
    comment = models.LongStringField(
        label='Please share your comments about this study here.',
        blank = True
    )
