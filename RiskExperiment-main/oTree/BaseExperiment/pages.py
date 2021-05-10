from django.shortcuts import render

# from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from .recipes import RECIPES, INGREDIENTS, images_map

IMAGES = images_map(INGREDIENTS)


class IntroPage(Page):
    def vars_for_template(self):
        return dict(BasePay=Constants.BasePay)

class IntroPage2(Page):
    pass

class Randomization(Page):
    timeout_seconds = 7

class PlayerIntroPage(Page):
    pass

class LocationChoice(Page):
    form_model = 'player'

    def get_form_fields(self):
        return ['NLocationChoice']

    def is_displayed(self):
        return self.player.id_in_group == 1

class LocationApproval(Page):
    def is_displayed(self):
        return self.player.id_in_group == 1

class SPLocation1(Page):
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

class CultureCondition(Page):
    pass

class GameIntro(Page):
    pass

class SandwichIntro(Page):
    def is_displayed(self):
        return self.player.id_in_group == 1

class Shop(Page):
    live_method = "handle_message"

    def vars_for_template(self):
        return dict(ingredients=INGREDIENTS, menu=RECIPES)

    def js_vars(self):
        return dict(duration=180, menu=RECIPES, images=IMAGES)

    def is_displayed(self):
        return self.player.id_in_group == 1

class AfterPractice(Page):
    def is_displayed(self):
        return self.player.id_in_group == 1

    def vars_for_template(self):
        return dict(BasePrice=Constants.BasePrice, BasePay=Constants.BasePay)

    # Reset Game Values
    def before_next_page(self):
        self.player.reset_after_practice()

class ComprehensionSurvey(Page):
    def is_displayed(self):
        return self.player.id_in_group == 1

class SPComprehensionSurvey(Page):
    def is_displayed(self):
        return self.player.id_in_group == 2

class SPBefReporting(Page):
    def is_displayed(self):
        return self.player.id_in_group == 2

class Round1(Page):
    live_method = "handle_message"

    def vars_for_template(self):
        return dict(ingredients=INGREDIENTS, menu=RECIPES)

    def js_vars(self):
        return dict(duration=300, menu=RECIPES, images=IMAGES)

    def is_displayed(self):
        return self.player.id_in_group == 1

class SPBefWait(Page):
    def is_displayed(self):
        return self.player.id_in_group == 2

class AfterRound1Game(Page):
    timeout_seconds = 15

    def is_displayed(self):
        return self.player.id_in_group == 1

class RiskEvent(Page):
    def is_displayed(self):
        return self.player.id_in_group == 1

class ReportingScreen(Page):
    form_model = 'player'

    def vars_for_template(self):
        revenue = self.player.revenue
        return dict(revenue=revenue)

    def get_form_fields(self):
        if self.group.reportingcondition == 'mandatory':
            return ['NReportedPerf', 'NReportedRiskManD']
        else:
            return ['NReportedPerf', 'NReportedRiskVol']

    def is_displayed(self):
        return self.player.id_in_group == 1

class AfterRound1Report(Page):
    def is_displayed(self):
        return self.player.id_in_group == 1

class WReport(WaitPage):
    template_name = 'global/RiskWaitPage.html'

    def is_displayed(self):
        return self.player.id_in_group == 2

class SPEvaluation(Page):
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

class expectancy1(Page):
    form_model = 'player'
    form_fields = ['extime']

    def is_displayed(self):
        return self.player.id_in_group == 1

class expectancy2(Page):
    form_model = 'player'
    form_fields = ['exbudget', 'exshort', 'exlong']

    def is_displayed(self):
        return self.player.id_in_group == 1

class expectancy3(Page):
    form_model = 'player'
    form_fields = ['expect1', 'expect2', 'expect3']

    def is_displayed(self):
        return self.player.id_in_group == 1
class riskperception1(Page):
    form_model = 'player'
    form_fields = ['riskiden']

    def is_displayed(self):
        return self.player.id_in_group == 1

class riskperception2(Page):
    form_model = 'player'
    form_fields = ['riskperc', 'riskcert', 'riskseri']

    def is_displayed(self):
        return self.player.id_in_group == 1

class riskimpexexp(Page):
    form_model = 'player'
    form_fields = ['riskimp1', 'riskimp2']
    def is_displayed(self):
        return self.player.id_in_group == 1

class Sriskimpexexp(Page):
    form_model = 'player'
    form_fields = ['riskimp1', 'riskimp2']
    def is_displayed(self):
        return self.player.id_in_group == 2

class PostExpQuest(Page):
    def is_displayed(self):
        return self.player.id_in_group == 1

class riskimportpostexp(Page):
    form_model = 'player'
    form_fields = ['riskimp3', 'riskimp4', 'riskimp5']

class factor1(Page):
    form_model = 'player'
    form_fields = ['factor1', 'factor2', 'factor3', 'factor4', 'factor5', 'factor6', 'factor7', "factor8"]

    def is_displayed(self):
        return self.player.id_in_group == 1


class factor2(Page):
    form_model = 'player'
    form_fields = ['factor9', 'factor10', 'factor11', 'factor12', 'factor13', 'factor14', 'factor15']

    def is_displayed(self):
        return self.player.id_in_group == 1


class supimpress1(Page):
    form_model = 'player'
    form_fields = ['sup1', 'sup2', 'sup3', 'sup4', 'sup5']

    def is_displayed(self):
        return self.player.id_in_group == 1


class supimpress2(Page):
    form_model = 'player'
    form_fields = ['sup6', 'sup7', 'sup8', 'sup9', 'sup10']

    def is_displayed(self):
        return self.player.id_in_group == 1


class orgtrust(Page):
    form_model = 'player'
    form_fields = ['trust1', 'trust2', 'trust3', 'trust4', 'trust5', 'trust6']

    def is_displayed(self):
        return self.player.id_in_group == 1


class suptrust(Page):
    form_model = 'player'
    form_fields = ['suptrust1', 'suptrust2', 'suptrust3', 'suptrust4', 'suptrust5', 'suptrust6']

    def is_displayed(self):
        return self.player.id_in_group == 1


class manvoluntarycheck(Page):
    form_model = 'player'
    form_fields = ['manvol1', 'manvol2', 'manvol3']


class responsibility(Page):
    form_model = 'player'
    form_fields = ['resp1', 'resp2']

    def is_displayed(self):
        return self.player.id_in_group == 1


class reportquality(Page):
    form_model = 'player'
    form_fields = ['repq1', 'repq2']

    def is_displayed(self):
        return self.player.id_in_group == 1


class uncertaversion1(Page):
    form_model = 'player'
    form_fields = ['unc1', 'unc2', 'unc3', 'unc4', 'unc5', 'unc6']


class uncertaversion2(Page):
    form_model = 'player'
    form_fields = ['unc7', 'unc8', 'unc9', 'unc10', 'unc11', 'unc12']


class volexp(Page):
    form_model = 'player'
    form_fields = ['mandatory', 'voluntary']

    def get_form_fields(self):
        if self.group.reportingcondition == 'mandatory':
            return ['mandatory']
        else:
            return ['voluntary']


class perf(Page):
    form_model = 'player'
    form_fields = ['perf1', 'perf2']

    def is_displayed(self):
        return self.player.id_in_group == 1


class riskattitude1(Page):
    form_model = 'player'
    form_fields = ['riskat1', 'riskat2', 'riskat3', 'riskat4', 'riskat5', 'riskat6']


class riskattitude2(Page):
    form_model = 'player'
    form_fields = ['riskat7', 'riskat8', 'riskat9', 'riskat10', 'riskat11']


class optimism(Page):
    form_model = 'player'
    form_fields = ['opt1', 'opt2', 'opt3', 'opt4', 'opt5', 'opt6']


class dark(Page):
    form_model = 'player'
    form_fields = ['dark1', 'dark2', 'dark3', 'dark4', 'dark5', 'dark6', 'dark7', 'dark8', 'dark9', 'dark10', 'dark11',
                   'dark12']


class pclosure1(Page):
    form_model = 'player'
    form_fields = ['closure1', 'closure2', 'closure3', 'closure4', 'closure5', 'closure6', 'closure7']

    def is_displayed(self):
        return self.player.id_in_group == 2


class pclosure2(Page):
    form_model = 'player'
    form_fields = ['closure8', 'closure9', 'closure10', 'closure11', 'closure12', 'closure13', 'closure14', 'closure15']

    def is_displayed(self):
        return self.player.id_in_group == 2


class uncertainaversion1(Page):
    form_model = 'player'
    form_fields = ['unc1', 'unc2', 'unc3', 'unc4', 'unc5', 'unc6']


class uncertainaversion2(Page):
    form_model = 'player'
    form_fields = ['unc7', 'unc8', 'unc9', 'unc10', 'unc11', 'unc12']


class allocationfactor1(Page):
    form_model = 'player'
    form_fields = ['sfact1', 'sfact2', 'sfact3', 'sfact4', 'sfact5']

    def is_displayed(self):
        return self.player.id_in_group == 2


class allocationfactor2(Page):
    form_model = 'player'
    form_fields = ['sfact7', 'sfact8', 'sfact9', 'sfact10', 'sfact6','sfact11']

    def is_displayed(self):
        return self.player.id_in_group == 2


class emergencyfactor(Page):
    form_model = 'player'
    form_fields = ['emfact1', 'emfact2', 'emfact3', 'emfact4', 'emfact5', 'emfact6']

    def is_displayed(self):
        return self.player.id_in_group == 2


class reportqual1(Page):
    form_model = 'player'
    form_fields = ['north1', 'north2', 'south1', 'south2']

    def is_displayed(self):
        return self.player.id_in_group == 2

class mansafetycheck(Page):
    form_model = 'player'
    form_fields = ['safety1', 'safety2', 'safety3', 'safety4', 'safety5', 'safety6', 'safety7']

class GenQuest(Page):
    form_model = 'player'
    form_fields = ['gen1', 'gen2', 'gen3', 'gen4']


class Results(Page):
    def vars_for_template(self):
        return dict(BasePay=Constants.BasePay)


page_sequence = [IntroPage, IntroPage2, Randomization, PlayerIntroPage, LocationChoice, LocationApproval, SPLocation1, WRAlloc, SPLocation2,
                 CultureCondition, GameIntro, SandwichIntro, Shop, AfterPractice,
                 ComprehensionSurvey, SPComprehensionSurvey, SPBefReporting, Round1, SPBefWait, AfterRound1Game,
                 RiskEvent, ReportingScreen, AfterRound1Report, WReport, SPEvaluation,
                 expectancy1, expectancy2, expectancy3, riskperception1, riskperception2,
                 riskimpexexp,
                 Sriskimpexexp, PostExpQuest,
                 allocationfactor1, allocationfactor2, responsibility,
                 riskimportpostexp, reportqual1, supimpress1, supimpress2,
                 reportquality, orgtrust, suptrust, perf,
                 emergencyfactor, factor1, factor2, riskattitude1, riskattitude2, pclosure1, pclosure2,
                 uncertainaversion1, uncertainaversion2, optimism, dark, mansafetycheck, manvoluntarycheck, volexp,
                 GenQuest, Results]
