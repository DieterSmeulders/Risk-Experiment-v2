from django.shortcuts import render

# from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from .recipes import RECIPES, INGREDIENTS, images_map

IMAGES = images_map(INGREDIENTS)

class _PreStartIntro(Page):
    pass
class _PrestartWait(WaitPage):
    pass

class M1IntroPage(Page):
    def vars_for_template(self):
        return dict(BasePay=Constants.BasePay)

class M2IntroPage2(Page):
    pass

class M3PlayerIntroPage(Page):
    pass

class M3Shop(Page):
    live_method = "handle_message"

    def vars_for_template(self):
        return dict(ingredients=INGREDIENTS, menu=RECIPES)

    def js_vars(self):
        return dict(duration=120, menu=RECIPES, images=IMAGES)

    def is_displayed(self):
        return self.player.id_in_group == 1


class M4LocationChoice1(Page):
    def is_displayed(self):
        return self.player.id_in_group == 1


class M4LocationChoice2(Page):
    form_model = 'player'

    def get_form_fields(self):
        return ['NLocationChoice']

    def is_displayed(self):
        return self.player.id_in_group == 1


class M5LocationApproval(Page):
    def is_displayed(self):
        return self.player.id_in_group == 1


class N1SPLocation(Page):
    def vars_for_template(self):
        return dict(northernlocation=self.group.get_player_by_id(1).NLocationChoice)

    def is_displayed(self):
        return self.player.id_in_group == 2

class WRAlloc(WaitPage):
    body_text = "The shop manager is getting familiar with her/his task, and is selecting a location for the new shop. Please wait. This may take up to 5 minutes."

class M6CultureCondition(Page):
    pass

class M7procedure(Page):
    pass

class M10AfterPractice(Page):
    def is_displayed(self):
        return self.player.id_in_group == 1

    def vars_for_template(self):
        return dict(BasePrice=Constants.BasePrice, BasePay=Constants.BasePay,northernlocation=self.group.get_player_by_id(1).NLocationChoice)

    # Reset Game Values
    def before_next_page(self):
        self.player.reset_after_practice()


class M11ComprehensionSurvey1(Page):
    form_model = 'player'
    form_fields = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']

    def Q1_error_message(self, value):
        print('Answer to Q1 is', value)
        if value != self.player.id_in_group:
            return 'Please check your role'
    def Q2_error_message(self, value):
        print('Answer to Q2 is', value)
        if value != 1:
            return 'Only the shop manager has access to the market assessment.'
    def Q3_error_message(self, value):
        print('Answer to Q3 is', value)
        if value != 2:
            return 'The shop manager has 5 minutes to make sandwiches.'
    def Q4_error_message(self, value):
        print('Answer to Q4 is', value)
        if value != 2:
            return 'The supervisor will rate the performance of the shop manager.'
    def Q5_error_message(self, value):
        print('Answer to Q5 is', value)
        if value != 3:
            return 'Sales revenue is the product of the number of sandwiches made ' \
                   'and the selling price of each sandwich. The current selling price is 1 EUR.'


class M11ComprehensionSurvey2(Page):
    form_model = 'player'
    form_fields = ['Q6', 'Q7', 'Q8']

    def Q6_error_message(self, value):
        print('Answer to Q6 is', value)
        if self.group.reportingcondition == 'mandatory':
            if value != 1:
                return 'The company has a mandatory risk reporting policy.'
        if self.group.reportingcondition == 'voluntary':
            if value != 2:
                return 'The company has a voluntary risk reporting policy.'
    def Q7_error_message(self, value):
        print('Answer to Q7 is', value)
        if self.group.culturecondition == 'supportive':
            if value != 1:
                return 'Please check your answer.'
        if self.group.culturecondition == 'unsupportive':
            if value != 2:
                return 'Please check your answer.'

    def Q8_error_message(self, value):
        print('Answer to Q8 is', value)
        if self.group.culturecondition == 'supportive':
            if value != 1:
                return 'Please check your answer.'
        if self.group.culturecondition == 'unsupportive':
            if value != 2:
                return 'Please check your answer.'

class M12Round1(Page):
    live_method = "handle_message"

    def vars_for_template(self):
        return dict(ingredients=INGREDIENTS, menu=RECIPES)

    def js_vars(self):
        return dict(duration=300, menu=RECIPES, images=IMAGES)

    def is_displayed(self):
        return self.player.id_in_group == 1


class N4SPBefWait(Page):
    def is_displayed(self):
        return self.player.id_in_group == 2

class AfterRound1Game(Page):
    timeout_seconds = 15

    def is_displayed(self):
        return self.player.id_in_group == 1

class N5SPBefReporting(Page):
    def is_displayed(self):
        return self.player.id_in_group == 2


class M13AfterRound1Game(Page):
    def is_displayed(self):
        return self.player.id_in_group == 1

    def vars_for_template(self):
        return dict(northernlocation=self.group.get_player_by_id(1).NLocationChoice)

class M14RiskEvent(Page):
    def vars_for_template(self):
        return dict(northernlocation=self.group.get_player_by_id(1).NLocationChoice)
    def is_displayed(self):
        return self.player.id_in_group == 1


class M15ReportingScreen(Page):
    form_model = 'player'

    def vars_for_template(self):
        revenue = self.player.revenue
        return dict(revenue=revenue,northernlocation=self.group.get_player_by_id(1).NLocationChoice)

    def get_form_fields(self):
        if self.group.reportingcondition == 'mandatory':
            return ['NReportedRiskManD']
        else:
            return ['NReportedRiskVol']

    def is_displayed(self):
        return self.player.id_in_group == 1

class AfterRound1Report(Page):
    def is_displayed(self):
        return self.player.id_in_group == 1

class WReport(Page):
#    timer_text = 'The shop manager is making and selling sandwiches. Please Wait:'
#    timeout_seconds = 360
    timeout_seconds = 90

    def is_displayed(self):
        return self.player.id_in_group == 2

class WReport2(Page):
    timeout_seconds =  200

    def is_displayed(self):
        return self.player.id_in_group == 2

class WReport3(WaitPage):
    template_name = 'global/RiskWaitPage.html'

    def is_displayed(self):
        return self.player.id_in_group == 2


class M16PostExpQuest(Page):
    def is_displayed(self):
        return self.player.id_in_group == 1


class N6SPEvaluation(Page):
    form_model = 'player'
    form_fields = ['Evaluation']

    def vars_for_template(self):
        return dict(
            northernreportedperformance=self.group.get_player_by_id(1).revenue,
            northernmandatoryrisk=self.group.get_player_by_id(1).NReportedRiskManD,
            northernvoluntaryrisk=self.group.get_player_by_id(1).NReportedRiskVol
        )

    def is_displayed(self):
        return self.player.id_in_group == 2


class Post1Quality2temp (Page):
    form_model = 'player'
    form_fields = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']

    def is_displayed(self):
        return self.player.id_in_group == 2


class Post1Quality1(Page):
    form_model = 'player'
    form_fields = ['closure1', 'closure2', 'closure3', 'closure4', 'closure5', 'closure6']

    def is_displayed(self):
        return self.player.id_in_group == 1


class Post1Quality2(Page):
    form_model = 'player'
    form_fields = ['closure7', 'closure8', 'closure9', 'closure10', 'closure11', 'closure12']

    def is_displayed(self):
        return self.player.id_in_group == 1


class N7SAssess(Page):
    form_model = 'player'
    form_fields = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']

    def is_displayed(self):
        return self.player.id_in_group == 2


class Post2importance(Page):
    form_model = 'player'
    form_fields = ['importance1', 'importance2', 'importance3', 'importance4']


class Post3image1(Page):
    form_model = 'player'
    form_fields = ['image1', 'image2', 'image3', 'image4', 'image5', 'image6', 'image7']

    def is_displayed(self):
        return self.player.id_in_group == 1


class Post4factor(Page):
    form_model = 'player'
    form_fields = ['factor1', 'factor2', 'factor3', 'factor4', 'factor5', 'factor6', 'factor7']

    def is_displayed(self):
        return self.player.id_in_group == 1


class Post5trust(Page):
    form_model = 'player'
    form_fields = ['trust1', 'trust2', 'trust3']

    def is_displayed(self):
        return self.player.id_in_group == 1


class Post6oblig(Page):
    form_model = 'player'
    form_fields = ['oblig1', 'oblig2', 'oblig3', 'oblig4', 'oblig5', 'oblig6', 'oblig7']

    def is_displayed(self):
        return self.player.id_in_group == 1


class Post7perf(Page):
    form_model = 'player'
    form_fields = ['perf1', 'perf2']

    def is_displayed(self):
        return self.player.id_in_group == 1


class Post8mansafetycheck(Page):
    form_model = 'player'
    form_fields = ['safety1', 'safety2', 'safety3', 'safety4', 'safety5', 'safety6', 'safety7']


class Post9manvoluntarycheck(Page):
    form_model = 'player'
    form_fields = ['manvol1', 'manvol2', 'manvol3']


class Post10volexp(Page):
    form_model = 'player'
    form_fields = ['reason1', 'reason2', 'reason3', 'reason4', 'reason5']
#    form_fields = ['mandatory', 'voluntary']
#    def get_form_fields(self):
#        if self.group.reportingcondition == 'mandatory':
#            return ['mandatory']
#        else:
#            return ['voluntary']


class Post11riskattitude1(Page):
    form_model = 'player'
    form_fields = ['riskat1', 'riskat2', 'riskat3', 'riskat4', 'riskat5']


class Post12optimism(Page):
    form_model = 'player'
    form_fields = ['opt1', 'opt2', 'opt3', 'unc1', 'unc2', 'unc3']


class Post14gender(Page):
    form_model = 'player'
    form_fields = ['gender', 'age', 'WorkExperience']


class Post15GenQuest(Page):
    form_model = 'player'
    form_fields = ['gen1', 'gen2', 'gen3', 'gen4', 'comment']


class Results(Page):
    def vars_for_template(self):
        Partcode = self.participant.code[:3]
        return dict(Evaluation=self.group.get_player_by_id(2).get_Evaluation_display(), BasePay=Constants.BasePay,Code=Partcode)


page_sequence = [_PreStartIntro, _PrestartWait, M1IntroPage, M2IntroPage2, M3PlayerIntroPage, M3Shop, M4LocationChoice1,
                 M4LocationChoice2,
                 WRAlloc, N1SPLocation, M5LocationApproval,  M6CultureCondition, M7procedure, M10AfterPractice,
                 M11ComprehensionSurvey1, M11ComprehensionSurvey2, M12Round1, M13AfterRound1Game,
                 M14RiskEvent, M15ReportingScreen, WReport, WReport2, WReport3, N5SPBefReporting,
                 N6SPEvaluation, M16PostExpQuest, Post1Quality2temp, Post1Quality1, Post1Quality2, Post2importance,
                 Post3image1, Post4factor, Post5trust, Post6oblig, Post7perf,
                 Post8mansafetycheck, Post9manvoluntarycheck, Post10volexp, Post11riskattitude1,
                 Post12optimism, Post14gender, Post15GenQuest, Results]
