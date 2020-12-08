from django.shortcuts import render

#from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from .recipes import RECIPES, INGREDIENTS, images_map

IMAGES = images_map(INGREDIENTS)


class IntroPage(Page):
    def vars_for_template(self):
        return dict(
            BasePay = Constants.BasePay
        )

class IntroPage2(Page):
    def vars_for_template(self):
        return dict(
            employeepercent=100 * Constants.EmployeeRatio,
            managerpercent=100 * Constants.ManagerRatio
        )


class CultureCondition(Page):
    pass
class Randomization(Page):
    pass
class PlayerIntroPage(Page):
    def is_displayed(self):
        return self.player.id_in_group in (1,2,3)
    def vars_for_template(self):
        return dict(
            employeepercent=100 * Constants.EmployeeRatio,
            managerpercent=100 * Constants.ManagerRatio
        )

class GameIntro(Page):
    pass

class ComprehensionSurvey(Page):
    pass

class LocationChoice(Page):
    form_model = 'player'
    def get_form_fields(self):
        if self.player.id_in_group == 1:
            return ['NLocationChoice']
        else:
            return ['SLocationChoice']
    def is_displayed(self):
        return self.player.id_in_group in (1,2)

class Approval(Page):
    def is_displayed(self):
        return self.player.id_in_group in (1,2)

class SandwichIntro(Page):
    def is_displayed(self):
        return self.player.id_in_group in (1,2)

class Shop(Page):
    live_method = "handle_message"

    def vars_for_template(self):
        return dict(ingredients=INGREDIENTS, menu=RECIPES)

    def js_vars(self):
        return dict(duration=120, menu=RECIPES, images=IMAGES)

    def is_displayed(self):
        return self.player.id_in_group in (1, 2)

class AfterPractice(Page):
    def is_displayed(self):
        return self.player.id_in_group in (1, 2)

class Round1(Page):
    live_method = "handle_message"

    def vars_for_template(self):
        return dict(ingredients=INGREDIENTS, menu=RECIPES)

    def js_vars(self):
        return dict(duration=300, menu=RECIPES, images=IMAGES)

    def is_displayed(self):
        return self.player.id_in_group in (1, 2)

class AfterRound1Game(Page):
    def is_displayed(self):
        return self.player.id_in_group in (1, 2)

class RiskEvent(Page):
    def is_displayed(self):
        return self.player.id_in_group in (1,2)

class ReportingIntro(Page):
    def is_displayed(self):
        return self.player.id_in_group in (1, 2)

class ReportingScreen(Page):
    form_model = 'player'
    def get_form_fields(self):
        if self.player.id_in_group == 1:
            if self.group.reportingcondition ==  'mandatory':
                return ['NReportedPerf','NReportedRiskMan','NReportedRiskManD']
            else:
                return ['NReportedPerf','NReportedRiskVol']
        else:
            if self.group.reportingcondition ==  'mandatory':
                return ['SReportedPerf','SReportedRiskManD','SReportedRiskMan']
            else:
                return ['SReportedPerf','SReportedRiskVol']
    def is_displayed(self):
        return self.player.id_in_group in (1,2)

class ReminderAccess(Page):
    def is_displayed(self):
        return self.player.id_in_group in (1, 2)

class AfterRound1Report(Page):
    def is_displayed(self):
        return self.player.id_in_group in (1, 2)

class SPLocation1(Page):
    def is_displayed(self):
        return self.player.id_in_group == 3

class SPLocation2(Page):
    form_model = 'player'
    form_fields = ['Sloc','Nloc']
    def is_displayed(self):
        return self.player.id_in_group == 3

class SPBefReporting(Page):
    def is_displayed(self):
        return self.player.id_in_group == 3

class SPAllocation(Page):
    form_model = 'player'
    form_fields = ['Stime','Ntime','SEM', 'NEM']
    def is_displayed(self):
        return self.player.id_in_group == 3

class SPAfterAllocation(Page):
    def is_displayed(self):
        return self.player.id_in_group == 3


class expectancy1(Page):
    form_model = 'player'
    form_fields = ['extime']

    def is_displayed(self):
        return self.player.id_in_group in (1, 2)


class expectancy2(Page):
    form_model = 'player'
    form_fields = ['exbudget', 'exshort', 'exlong']

    def is_displayed(self):
        return self.player.id_in_group in (1, 2)


class riskperception1(Page):
    form_model = 'player'
    form_fields = ['riskiden']

    def is_displayed(self):
        return self.player.id_in_group in (1, 2)


class riskperception2(Page):
    form_model = 'player'
    form_fields = ['riskperc', 'riskcert', 'riskseri']

    def is_displayed(self):
        return self.player.id_in_group in (1, 2)


class riskimpexexp(Page):
    form_model = 'player'
    form_fields = ['riskimp1', 'riskimp2']


class AfterRound1Allocation(Page):
    pass
    def is_displayed(self):
        return self.player.id_in_group in (1, 2)

class riskimportpostexp(Page):
    form_model = 'player'
    form_fields = ['riskimp3', 'riskimp4', 'riskimp5']


class reportimp(Page):
    form_model = 'player'
    form_fields = ['repimp1', 'repimp2', 'repimp3', 'repimp4', 'repimp5', 'repimp6', 'repimp7']

    def is_displayed(self):
        return self.player.id_in_group in (1, 2)


class factor1(Page):
    form_model = 'player'
    form_fields = ['factor1', 'factor2', 'factor3', 'factor4', 'factor5', 'factor6', 'factor7', "factor8"]

    def is_displayed(self):
        return self.player.id_in_group in (1, 2)


class factor2(Page):
    form_model = 'player'
    form_fields = ['factor9', 'factor10', 'factor11', 'factor12', 'factor13', 'factor14', 'factor15']

    def is_displayed(self):
        return self.player.id_in_group in (1, 2)


class supimpress1(Page):
    form_model = 'player'
    form_fields = ['sup1', 'sup2', 'sup3', 'sup4', 'sup5']

    def is_displayed(self):
        return self.player.id_in_group in (1, 2)


class supimpress2(Page):
    form_model = 'player'
    form_fields = ['sup6', 'sup7', 'sup8', 'sup9']

    def is_displayed(self):
        return self.player.id_in_group in (1, 2)


class orgtrust(Page):
    form_model = 'player'
    form_fields = ['trust1', 'trust2', 'trust3', 'trust4', 'trust5', 'trust6']

    def is_displayed(self):
        return self.player.id_in_group in (1, 2)


class suptrust(Page):
    form_model = 'player'
    form_fields = ['suptrust1', 'suptrust2', 'suptrust3', 'suptrust4', 'suptrust5', 'suptrust6']

    def is_displayed(self):
        return self.player.id_in_group in (1, 2)


class manvoluntarycheck(Page):
    form_model = 'player'
    form_fields = ['manvol1', 'manvol2', 'manvol3']


class responsibility(Page):
    form_model = 'player'
    form_fields = ['resp1', 'resp2']

    def is_displayed(self):
        return self.player.id_in_group in (1, 2)


class reportquality(Page):
    form_model = 'player'
    form_fields = ['repq1', 'repq2']

    def is_displayed(self):
        return self.player.id_in_group in (1, 2)


class uncertaversion1(Page):
    form_model = 'player'
    form_fields = ['unc1', 'unc2', 'unc3', 'unc4', 'unc5', 'unc6']


class uncertaversion2(Page):
    form_model = 'player'
    form_fields = ['unc7', 'unc8', 'unc9', 'unc10', 'unc11', 'unc12']


class volexp(Page):
    form_model = 'player'
    form_fields = ['mandatory', 'voluntary']


class perf(Page):
    form_model = 'player'
    form_fields = ['perf1', 'perf2']

    def is_displayed(self):
        return self.player.id_in_group in (1, 2)

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
        return self.player.id_in_group == 3


class pclosure2(Page):
    form_model = 'player'
    form_fields = ['closure8', 'closure9', 'closure10', 'closure11', 'closure12', 'closure13', 'closure14', 'closure15']

    def is_displayed(self):
        return self.player.id_in_group == 3


class uncertainaversion1(Page):
    form_model = 'player'
    form_fields = ['unc1', 'unc2', 'unc3', 'unc4', 'unc5', 'unc6']

class uncertainaversion2(Page):
    form_model = 'player'
    form_fields = ['unc7', 'unc8', 'unc9', 'unc10', 'unc11', 'unc12']



class allocationfactor1(Page):
    form_model = 'player'
    form_fields = ['sfact1', 'sfact2', 'sfact3', 'sfact4', 'sfact5', 'sfact6']

    def is_displayed(self):
        return self.player.id_in_group == 3


class allocationfactor2(Page):
    form_model = 'player'
    form_fields = ['sfact7', 'sfact8', 'sfact9', 'sfact10', 'sfact11', 'sfact12']

    def is_displayed(self):
        return self.player.id_in_group == 3


class emergencyfactor(Page):
    form_model = 'player'
    form_fields = ['emfact1', 'emfact2', 'emfact3', 'emfact4', 'emfact5', 'emfact6']

    def is_displayed(self):
        return self.player.id_in_group == 3


class reportqual1(Page):
    form_model = 'player'
    form_fields = ['north1', 'north2', 'south1', 'south2']

    def is_displayed(self):
        return self.player.id_in_group == 3


class reportqual2(Page):
    form_model = 'player'
    form_fields = ['north3', 'north4', 'south3', 'south4']

    def is_displayed(self):
        return self.player.id_in_group == 3

class mansafetycheck(Page):
    form_model = 'player'
    form_fields = ['safety1', 'safety2', 'safety3', 'safety4', 'safety5', 'safety6', 'safety7']


class Results(Page):
    pass


page_sequence = [IntroPage, IntroPage2, CultureCondition, Randomization, PlayerIntroPage, GameIntro, ComprehensionSurvey,
                 LocationChoice, SPLocation1, SPLocation2, SandwichIntro, Shop, AfterPractice, Round1, AfterRound1Game,
                 RiskEvent, SPBefReporting, ReportingIntro, ReportingScreen, ReminderAccess, SPAllocation,
                 SPAfterAllocation, AfterRound1Report, expectancy1, expectancy2, riskperception1, riskperception2, riskimpexexp,
                 AfterRound1Allocation, allocationfactor1, allocationfactor2, responsibility, perf, riskimportpostexp, reportimp, factor1, factor2, reportqual1,
                 reportqual2, reportquality, orgtrust, suptrust,
                 emergencyfactor, supimpress1, supimpress2, riskattitude1, riskattitude2,
                 mansafetycheck, manvoluntarycheck, volexp, pclosure1, pclosure2,
                 uncertainaversion1, uncertainaversion2, optimism, dark, Results]
