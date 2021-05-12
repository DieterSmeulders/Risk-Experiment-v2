from django.shortcuts import render

# from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from .recipes import RECIPES, INGREDIENTS, images_map

IMAGES = images_map(INGREDIENTS)


class M1IntroPage(Page):
    def vars_for_template(self):
        return dict(BasePay=Constants.BasePay)


class M2IntroPage2(Page):
    pass


class M3PlayerIntroPage(Page):
    pass


class M4LocationChoice(Page):
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
    pass

class SPLocation2(Page):
    form_model = 'player'

    def vars_for_template(self):
        return dict(northernlocation=self.group.get_player_by_id(1).NLocationChoice)

    def is_displayed(self):
        return self.player.id_in_group == 2

class M6CultureCondition(Page):
    pass

class M7GameIntro(Page):
    pass

class M8SandwichIntro(Page):
    def is_displayed(self):
        return self.player.id_in_group == 1


class M9Shop(Page):
    live_method = "handle_message"

    def vars_for_template(self):
        return dict(ingredients=INGREDIENTS, menu=RECIPES)

    def js_vars(self):
        return dict(duration=60, menu=RECIPES, images=IMAGES)

    def is_displayed(self):
        return self.player.id_in_group == 1


class M10AfterPractice(Page):
    def is_displayed(self):
        return self.player.id_in_group == 1

    def vars_for_template(self):
        return dict(BasePrice=Constants.BasePrice, BasePay=Constants.BasePay)

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
            return 'Only the regional manager has access to the local market report.'
    def Q3_error_message(self, value):
        print('Answer to Q3 is', value)
        if value != 2:
            return 'The regional manager has 5 minutes to make sandwiches.'
    def Q4_error_message(self, value):
        print('Answer to Q4 is', value)
        if value != 2:
            return 'The key responsibility of the regional manager is Increasing the sales performance in the region.'
    def Q5_error_message(self, value):
        print('Answer to Q5 is', value)
        if value != 3:
            return 'Sales performance is the multiplication of the number of saleable sandwiches made and the selling price of each sandwich in the region.The current selling price is 1 EUR.'


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


class M14RiskEvent(Page):
    def is_displayed(self):
        return self.player.id_in_group == 1


class M15ReportingScreen(Page):
    form_model = 'player'

    def vars_for_template(self):
        revenue = self.player.revenue
        return dict(revenue=revenue)

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

class WReport(WaitPage):
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
            northernreportedperformance=self.group.get_player_by_id(1).NReportedPerf,
            northernmandatoryrisk=self.group.get_player_by_id(1).NReportedRiskManD,
            northernvoluntaryrisk=self.group.get_player_by_id(1).NReportedRiskVol
        )

    def is_displayed(self):
        return self.player.id_in_group == 2


class Post1Quality1(Page):
    form_model = 'player'
    form_fields = ['closure1', 'closure2', 'closure3', 'closure4', 'closure5', 'closure6', 'closure7', 'closure8']

    def is_displayed(self):
        return self.player.id_in_group == 1


class Post1Quality2(Page):
    form_model = 'player'
    form_fields = ['closure9', 'closure10', 'closure11', 'closure12', 'closure13', 'closure14']

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
    form_fields = ['factor1', 'factor2', 'factor3', 'factor4', 'factor5', 'factor6', 'factor7', 'factor8', 'factor9']

    def is_displayed(self):
        return self.player.id_in_group == 1


class Post5trust(Page):
    form_model = 'player'
    form_fields = ['trust1', 'trust2', 'trust3', 'trust4']

    def is_displayed(self):
        return self.player.id_in_group == 1


class Post6oblig(Page):
    form_model = 'player'
    form_fields = ['oblig1', 'oblig2', 'oblig3', 'oblig4', 'oblig5', 'oblig6', 'oblig7', 'oblig8']

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
    form_fields = ['mandatory', 'voluntary']
    def get_form_fields(self):
        if self.group.reportingcondition == 'mandatory':
            return ['mandatory']
        else:
            return ['voluntary']


class Post11riskattitude1(Page):
    form_model = 'player'
    form_fields = ['riskat1', 'riskat2', 'riskat3', 'riskat4', 'riskat5', 'riskat6']


class Post11riskattitude2(Page):
    form_model = 'player'
    form_fields = ['riskat7', 'riskat8', 'riskat9', 'riskat10', 'riskat11']


class Post12optimism(Page):
    form_model = 'player'
    form_fields = ['opt1', 'opt2', 'opt3', 'opt4', 'opt5', 'opt6']


class Post13uncertainaversion1(Page):
    form_model = 'player'
    form_fields = ['unc1', 'unc2', 'unc3', 'unc4', 'unc5', 'unc6']


class Post13uncertainaversion2(Page):
    form_model = 'player'
    form_fields = ['unc7', 'unc8', 'unc9', 'unc10', 'unc11', 'unc12']


class Post14gender(Page):
    form_model = 'player'
    form_fields = ['gender', 'age', 'WorkExperience']


class Post15GenQuest(Page):
    form_model = 'player'
    form_fields = ['gen1', 'gen2', 'gen3', 'gen4', 'comment']


class Results(Page):
    def vars_for_template(self):
        return dict(Evaluation=self.group.get_player_by_id(2).get_Evaluation_display(), BasePay=Constants.BasePay)


page_sequence = [M1IntroPage, M2IntroPage2, M3PlayerIntroPage, M4LocationChoice, M5LocationApproval, WRAlloc, N1SPLocation,
                 M6CultureCondition, M7GameIntro, M8SandwichIntro, M9Shop, M10AfterPractice,
                 M11ComprehensionSurvey1, M11ComprehensionSurvey2, M12Round1, M13AfterRound1Game,
                 M14RiskEvent, M15ReportingScreen, WReport, N6SPEvaluation, M16PostExpQuest, Post1Quality1, Post1Quality2, Post2importance,
                 Post3image1, Post4factor, Post5trust, Post6oblig, Post7perf,
                 Post8mansafetycheck, Post9manvoluntarycheck, Post10volexp, Post11riskattitude1, Post11riskattitude2,
                 Post12optimism, Post13uncertainaversion1, Post13uncertainaversion2, Post14gender, Post15GenQuest, Results]
