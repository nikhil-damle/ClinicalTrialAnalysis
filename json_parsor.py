#!/usr/bin/env python
# coding: utf-8

# ### Code to parse the json file obtained from clinicaltrials.gov
# (Intrventional clinical trial data was downloaded from https://clinicaltrials.gov/search?aggFilters=studyType:int in Nov 2024)

# Author: Dr. Nikhil Damle<br>
# Company: PharmaLex GmbH<br>
# Date created: Nov 2024<br>
# Last Modified: 07 Apr 2025<br>
# Latest Modifications: Added comments to code

# ### Import Libraries

import json
import ijson
import requests
import os
import pandas as pd
from datetime import datetime


# ### Initialize Variables (order of columns is important)

study_count=0;interventional_study_count=0;df = []
col_arr = ['nctid','status', 'studyTitle', 'startDate', 'PrimaryCompletionDate', 'studyCompletionDate', 'results_status', 
           'sponsor_name', 'brief_summary', 'detailed_description', 'studyType', 'studyPhases', 'studyAllocation', 'interventionModel', 'primaryPurpose', 
           'interventions', 'drug_name', 'drug_description', 'primaryOutcomes', 'secondaryOutcomes', 'conditions', 'condition_keywords', 
           'eligibilityCriteria', 'genderBased','studyPopulation', 'samplingMethod', 'outcomeMeasureDict', 'AE_description', 'EventGroups', 
           'SeriousEvents', 'OtherEvents', 'LimitationsAndCaveats']
global_val_arr=[]
global_val_arr.append(col_arr)

drug_name=[];drug_description=[];studyType='NO_STUDY_TYPE';non_interventional_trials=[];secondaryOutcomes = [];
primaryOutcomes=[];outcomeMeasureDict={};non_empty_dict = 0

now = datetime.now()
date_str = now.strftime("%Y-%m-%d").replace('-','')
output_csv = 'interventional_treatments_output_' + date_str + '.csv'


# ### Extract Information
# (In general, fetch value if key exists. Some values are strings, others lists and dicts. Sometimes multiple values occur and all need to be captured.
# Sometimes multiple instances of lists and/or dicts appear as values of a key. So proper parsing is important)

#with open('./_archive/ctg-studies_20250221.json', encoding='utf-8') as file:
with open('./_archive/NovDec_2024/ctg-studies.json', encoding='utf-8') as file:
    array_items = ijson.items(file, 'item')
    for study in array_items:
        study_count = study_count + 1
        nctid = study['protocolSection']['identificationModule']['nctId'];#print('checking Trial: ', nctid)
        
        if 'designModule' in study['protocolSection']:
            studyType = study['protocolSection']['designModule']['studyType']
            if 'designInfo' in study['protocolSection']['designModule']:
                if 'primaryPurpose' in study['protocolSection']['designModule']['designInfo']:
                    primaryPurpose = study['protocolSection']['designModule']['designInfo']['primaryPurpose']
                    primaryPurpose = primaryPurpose.replace('\n', ' ').replace('\r', '')

        if studyType == 'INTERVENTIONAL' and primaryPurpose == 'TREATMENT':
            local_val_arr=[]
            status = study['protocolSection']['statusModule']['overallStatus']
            
            if 'startDateStruct' in study['protocolSection']['statusModule']:
                startDate = study['protocolSection']['statusModule']['startDateStruct']['date']
            else: startDate = 'NO_START_DATE'
            
            if 'primaryCompletionDateStruct' in study['protocolSection']['statusModule']:
                if 'date' in study['protocolSection']['statusModule']['primaryCompletionDateStruct']:
                    PrimaryCompletionDate = study['protocolSection']['statusModule']['primaryCompletionDateStruct']['date']
                    #PrimaryCompletionDateType = study['protocolSection']['statusModule']['primaryCompletionDateStruct']['type']
                else:
                    PrimaryCompletionDate = 'NOT_DEFINED';#PrimaryCompletionDateType='NOT_DEFINED'
            else: PrimaryCompletionDate = 'NOT_DEFINED';#PrimaryCompletionDateType='NOT_DEFINED'
            
            if 'completionDateStruct' in study['protocolSection']['statusModule']:
                if 'date' in study['protocolSection']['statusModule']['completionDateStruct']:
                    studyCompletionDate = study['protocolSection']['statusModule']['completionDateStruct']['date']
                    #studyCompletionDateType = study['protocolSection']['statusModule']['completionDateStruct']['type']
                else:
                    studyCompletionDate='NOT_DEFINED';#studyCompletionDateType='NOT_DEFINED'
            else: studyCompletionDate='NOT_DEFINED';#studyCompletionDateType='NOT_DEFINED'
                    
            if 'officialTitle' in study['protocolSection']['identificationModule']:
                studyTitle = study['protocolSection']['identificationModule']['officialTitle']
            else: studyTitle = 'NO_OFFICIAL_TITLE'
            
            if 'descriptionModule' in study['protocolSection']:
                if 'briefSummary' in study['protocolSection']['descriptionModule']:
                    brief_summary = study['protocolSection']['descriptionModule']['briefSummary'];
                    brief_summary = brief_summary.replace('\n', ' ').replace('\r', '')
                else: brief_summary = 'NO_BRIEF_SUMMARY'
                if 'detailedDescription' in study['protocolSection']['descriptionModule']:
                    detailed_description = study['protocolSection']['descriptionModule']['detailedDescription']
                    detailed_description = detailed_description.replace('\n', ' ').replace('\r', '')
                else: detailed_description = 'NO_DETAILED_DESCRIPTION'
            else:
                brief_summary = 'NO_BRIEF_SUMMARY';detailed_description = 'NO_DETAILED_DESCRIPTION'

            results_status = str(study['hasResults'])        
            sponsor_name = study['protocolSection']['sponsorCollaboratorsModule']['leadSponsor']['name']

            if 'designModule' in study['protocolSection']:
                if 'phases' in study['protocolSection']['designModule']:
                    studyPhases = study['protocolSection']['designModule']['phases']
                else: studyPhases = 'NO_PHASE_INFO'

                if 'designInfo' in study['protocolSection']['designModule']:
                    if 'allocation' in study['protocolSection']['designModule']['designInfo']: 
                        studyAllocation = study['protocolSection']['designModule']['designInfo']['allocation']
                    else: studyAllocation = 'NO_ALLOCATION_INFO'

                    if 'interventionModel' in study['protocolSection']['designModule']['designInfo']:
                        interventionModel = study['protocolSection']['designModule']['designInfo']['interventionModel']
                    else: interventionModel = 'NO_INTERVENTION_MODEL'
                    #interventionModelDescription = study['protocolSection']['designModule']['designInfo']['interventionModelDescription']
                    if 'primaryPurpose' in study['protocolSection']['designModule']['designInfo']:
                        primaryPurpose = study['protocolSection']['designModule']['designInfo']['primaryPurpose']
                        primaryPurpose = primaryPurpose.replace('\n', ' ').replace('\r', '')
                    else: primaryPurpose = 'NO_PRIMARY_PURPOSE'
                else: studyAllocation = 'NO_ALLOCATION_INFO'
            else: 
                studyPhases='NO_PHASE_INFO';studyAllocation='NO_ALLOCATION_INFO';interventionModel='NO_INTERVENTION_MODEL';primaryPurpose = 'NO_PRIMARY_PURPOSE'        

            if 'conditionsModule' in study['protocolSection']:
                conditions = study['protocolSection']['conditionsModule']['conditions'];
                if 'keywords' in study['protocolSection']['conditionsModule']:
                    condition_keywords = study['protocolSection']['conditionsModule']['keywords']
                else: condition_keywords = 'NO_KEYWORDS'
            else:
                conditions = 'NO_CONDITIONS';condition_keywords = 'NO_KEYWORDS'

            if 'eligibilityModule' in study['protocolSection']:
                if 'eligibilityCriteria' in study['protocolSection']['eligibilityModule']:
                    eligibilityCriteria = study['protocolSection']['eligibilityModule']['eligibilityCriteria']
                    eligibilityCriteria = eligibilityCriteria.replace('\n', ' ').replace('\r', '')
                else: eligibilityCriteria = 'NO_ELIGIBILITY_CRITERIA'
                if 'genderBased' in study['protocolSection']['eligibilityModule']:
                    genderBased = study['protocolSection']['eligibilityModule']['genderBased']
                else: genderBased = 'NOT_PROVIDED'
                if 'studyPopulation' in study['protocolSection']['eligibilityModule']:
                    studyPopulation = study['protocolSection']['eligibilityModule']['studyPopulation']
                else: studyPopulation = 'NO_POPULATION_INFO'
                if 'samplingMethod' in study['protocolSection']['eligibilityModule']:
                    samplingMethod = study['protocolSection']['eligibilityModule']['samplingMethod']
                else: samplingMethod = 'NO_SAMPLING_INFO'
            else: eligibilityCriteria = 'NO_ELIGIBILITY_CRITERIA';genderBased = 'NOT_PROVIDED';studyPopulation = 'NO_POPULATION_INFO';samplingMethod = 'NO_SAMPLING_INFO'

            if 'armsInterventionsModule' in study['protocolSection']:
                if 'interventions' in study['protocolSection']['armsInterventionsModule']:
                    interventions = study['protocolSection']['armsInterventionsModule']['interventions']
                    #print(interventions)
                    for each_intervention in interventions:
                        for k,v in each_intervention.items():
                            if k == 'type' and v == 'DRUG':
                                intervention_type = v
                                drug_name.append(each_intervention['name'])
                                if 'description' in each_intervention.keys():
                                    drug_description.append(each_intervention['description'].replace('\n', ' ').replace('\r', ''))
                                else:
                                    drug_description.append('NO_DRUG_DESCRIPTION_PROVIDED')
                else: interventions = 'NO_INTERVENTIONALS_FOUND'
            else:
                interventions = 'NO_INTERVENTIONALS_FOUND';drug_description.append('NO_DRUG_DESCRIPTION_PROVIDED');drug_name.append('NO_DRUG_NAME')

            if len(drug_name)==0 and len(drug_description)==0: drug_name.append('NO_DRUG_NAME');drug_description.append('NO_DRUG_DESCRIPTION')

            if 'outcomesModule' in study['protocolSection']:
                if 'primaryOutcomes' in study['protocolSection']['outcomesModule']:
                    primaryOutcomes = study['protocolSection']['outcomesModule']['primaryOutcomes'];
                else: primaryOutcomes.append('NOT_PROVIDED')
                if 'secondaryOutcomes' in study['protocolSection']['outcomesModule']:
                    secondaryOutcomes = study['protocolSection']['outcomesModule']['secondaryOutcomes']
                else: secondaryOutcomes.append('NOT_PROVIDED')
            else: primaryOutcomes.append('NOT_PROVIDED');secondaryOutcomes.append('NOT_PROVIDED')

            if "resultsSection" in study.keys():
                if 'outcomeMeasuresModule' in study['resultsSection'].keys():
                    if 'outcomeMeasures' in study['resultsSection']['outcomeMeasuresModule']:
                        outcomeMeasureDict={}
                        for outcomeMeasure in study['resultsSection']['outcomeMeasuresModule']['outcomeMeasures']:
                            OutcomeMeasureType = outcomeMeasure['type'];#print(OutcomeMeasureType)
                            outcomeMeasureDict[OutcomeMeasureType]=[]
                        for outcomeMeasure in study['resultsSection']['outcomeMeasuresModule']['outcomeMeasures']:
                            OutcomeMeasureType = outcomeMeasure['type'];
                            if 'analyses' in outcomeMeasure.keys():
                                outcomeMeasureDict[OutcomeMeasureType].append(outcomeMeasure['analyses'])
                #print(outcomeMeasureDict)
                for k, v in outcomeMeasureDict.items():
                    if len(outcomeMeasureDict[k])>0:
                        non_empty_dict = 1

                if 'adverseEventsModule' in study['resultsSection'].keys():
                    #print(study['resultsSection']['adverseEventsModule'])
                    if 'description' in study['resultsSection']['adverseEventsModule']:
                        AEDescription = study['resultsSection']['adverseEventsModule']['description']
                        AEDescription = AEDescription.replace('\n', ' ').replace('\r', '')
                    else: AEDescription = 'NO_DESCRIPTION_PROVIDED'

                    if 'eventGroups' in study['resultsSection']['adverseEventsModule']:
                        eventGrps = study['resultsSection']['adverseEventsModule']['eventGroups']
                    else: eventGrps = 'NO_EVENTGROUP_INFO'

                    if 'seriousEvents' in study['resultsSection']['adverseEventsModule']:
                        seriousEvents = study['resultsSection']['adverseEventsModule']['seriousEvents']
                        '''
                        if 'term' in seriousEvents:
                            seriousEventTerm = seriousEvents['term']
                        else: seriousEventTerm = "NOT_PROVIDED"
                        if 'organSystem' in seriousEvents:
                            organSyst = seriousEvents['organSystem']
                        else: organSyst = 'NO_ORG_SYST'
                        if sourceVocabulary in seriousEvents:
                            sourceVocab = seriousEvents['sourceVocabulary']
                        else: sourceVocab = 'NO_VOCAB'
                        if 'assessmentType' in seriousEvents:
                            assessmentType = seriousEvents['assessmentType']
                        else: assessmentType = 'NO_INFO'
                        '''
                    else:
                        #seriousEventTerm = "NOT_PROVIDED";organSyst = 'NO_ORG_SYST';sourceVocab = 'NO_VOCAB';assessmentType = 'NO_INFO';
                        seriousEvents = 'NO_SERIOUS_EVENT_INFO'

                    if 'otherEvents' in study['resultsSection']['adverseEventsModule']:
                        otherEvents = study['resultsSection']['adverseEventsModule']['otherEvents']
                    else: otherEvents = 'NO_OTHER_EVENT_INFO'
                else:
                    AEDescription = 'NO_DESCRIPTION_PROVIDED';eventGrps = 'NO_EVENTGROUP_INFO';seriousEvents = 'NO_SERIOUS_EVENT_INFO';otherEvents = 'NO_OTHER_EVENT_INFO';
                    #seriousEventTerm = "NOT_PROVIDED";organSyst = 'NO_ORG_SYST';sourceVocab = 'NO_VOCAB';assessmentType = 'NO_INFO';
                    
                if 'moreInfoModule' in study['resultsSection']:
                    if 'limitationsAndCaveats' in study['resultsSection']['moreInfoModule']:
                        LnC_description = study['resultsSection']['moreInfoModule']['limitationsAndCaveats']['description']
                    else: LnC_description = 'NO_DESCRIPTION_AVAILABLE'
                else:
                    LnC_description = 'NO_DESCRIPTION_AVAILABLE'
                
            else:
                AEDescription = 'NO_DESCRIPTION_PROVIDED';eventGrps = 'NO_EVENTGROUP_INFO';seriousEvents = 'NO_SERIOUS_EVENT_INFO';otherEvents = 'NO_OTHER_EVENT_INFO';
                LnC_description = 'NO_DESCRIPTION_AVAILABLE'

            interventional_study_count = interventional_study_count + 1
            #print(nctid,"\t",status,"\t",studyTitle,"\t",results_status,"\t",sponsor_name, "\t",brief_summary,"\t",detailed_description,"\t",studyType,"\t",\
            #  studyPhases,"\t",studyAllocation,"\t",interventionModel,"\t",primaryPurpose,"\t",interventions,"\t",drug_name,'\t',drug_description,"\t",primaryOutcomes,"\n")


            local_val_arr.append(nctid);local_val_arr.append(status);local_val_arr.append(studyTitle);local_val_arr.append(startDate);local_val_arr.append(PrimaryCompletionDate);
            #local_val_arr.append(PrimaryCompletionDateType);
            local_val_arr.append(studyCompletionDate);#local_val_arr.append(studyCompletionDateType);
            local_val_arr.append(results_status);
            local_val_arr.append(sponsor_name);local_val_arr.append(brief_summary);local_val_arr.append(detailed_description);local_val_arr.append(studyType);
            local_val_arr.append(studyPhases);local_val_arr.append(studyAllocation);local_val_arr.append(interventionModel);local_val_arr.append(primaryPurpose);
            local_val_arr.append(interventions);local_val_arr.append(drug_name);local_val_arr.append(drug_description);local_val_arr.append(primaryOutcomes);
            local_val_arr.append(secondaryOutcomes);local_val_arr.append(conditions);local_val_arr.append(condition_keywords);local_val_arr.append(eligibilityCriteria);
            local_val_arr.append(genderBased);local_val_arr.append(studyPopulation);local_val_arr.append(samplingMethod);

            if non_empty_dict == 1:
                local_val_arr.append(outcomeMeasureDict)
            else:
                local_val_arr.append('NO_OUTCOME_MEASURES')

            local_val_arr.append(AEDescription);local_val_arr.append(eventGrps);local_val_arr.append(seriousEvents);local_val_arr.append(otherEvents);
            local_val_arr.append(LnC_description);

            global_val_arr.append(local_val_arr);
        
            local_val_arr=[];drug_name=[];drug_description=[];secondaryOutcomes = [];primaryOutcomes=[];outcomeMeasureDict={};non_empty_dict = 0
        else:
            #print(nctid, ' is a ', studyType, ' i.e. NON-INTERVENTIONAL Trial and hence no information will be extracted')
            trialType = nctid + '_' + studyType
            non_interventional_trials.append(trialType)
            #break


# ### Write results to a file

df = pd.DataFrame(global_val_arr);#print(df)
df.to_csv(output_csv, sep='\t', index=False, header=False, mode='a')

#print("Total Studies = ", study_count, " Interventional Studies = ", interventional_study_count) # Total Studies =  514861  Interventional Studies =  394950 
print("Total Studies = ", study_count, " Interventional Studies w TREATMENT as primary focus = ", interventional_study_count) # Total Studies =  514861  Interventional Studies w TREATMENT as primary focus =  256718