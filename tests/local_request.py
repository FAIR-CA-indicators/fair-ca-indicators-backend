import requests
import json

print("TESTING THE SERVER")

# Define the URL of the local server
url = 'http://localhost:8000/session'

# Define the data you want to send in the POST request (as a dictionary)
metadata = {
  "link": None,
  "resource": {
    "collection": [
      "COVID-19",
      "coverCHILD study platform"
    ],
    "ids": [
      {
        "identifier": "https://www.thieme-connect.com/products/ejournals/abstract/10.1055/a-1638-6053",
        "relation_type": "A is described by B",
        "resource_type_general": "Other",
        "type": "Other"
      }
    ],
    "ids_alternative": [
      {
        "identifier": "DRKS00027974",
        "type": "DRKS"
      }
    ],
    "provenance": {
      "data_source": "Automatically uploaded: DRKS"
    },
    "resource_acronyms": [
      {
        "language": "EN (English)",
        "text": "KICK-COVID"
      }
    ],
    "resource_classification": {
      "resource_type": "Study",
      "resource_type_general": "Other"
    },
    "resource_description_english": {
      "language": "EN (English)",
      "text": "In a prospective study, the long-term effects of the COVID-19 pandemic on medical and psychosocial characteristics in children and adolescents with chronic conditions will be investigated using a holistic approach. The included diseases are obesity, diabetes, and rheumatic diseases; both the affected individuals themselves and their parents will be interviewed.\nInterdisciplinary collaboration between pediatricians of various specialties, psychologists, and epidemiologists will allow a comprehensive evaluation of the effects of COVID-19 on health care and the physical and mental health of children and adolescents with chronic conditions and their families, as well as the complex interplay between health status and health care as well as environmental and personal contextual factors.\nFor this, questions for the children and adolescents and their parents will be implemented as part of the standard survey in the Diabetes-Patienten-Verlaufsdokumentation (DPV), the Adipositas-Patienten-Verlaufsdokumentation (APV) and the Kerndokumentation rheumakranker Kinder und Jugendlicher (KRhOKo). In addition, all participants are invited to participate in a further online survey on the psychosocial situation and available resources. After one year, a follow-up takes place for both surveys. The prospective design allows both the detection of short- and long-term effects of the COVID-19 pandemic on well-being and the analysis of mediator and moderator effects. The aim is to find approaches to help those families with children and adolescents affected by a chronic condition."
    },
    "resource_identifier": "DRKS00027974",
    "resource_keywords": [
      {
        "resource_keywords_label": "family"
      },
      {
        "resource_keywords_label": "Coronavirus Disease 2019 (COVID-19)"
      },
      {
        "resource_keywords_label": "mental health"
      },
      {
        "resource_keywords_label": "longitudinal study"
      },
      {
        "resource_keywords_label": "obesity"
      },
      {
        "resource_keywords_label": "rheumatic diseases"
      },
      {
        "resource_keywords_label": "health care"
      },
      {
        "resource_keywords_label": "medical care"
      },
      {
        "resource_keywords_label": "disease management"
      },
      {
        "resource_keywords_label": "children and adolescents"
      },
      {
        "resource_keywords_label": "chronic conditions"
      },
      {
        "resource_keywords_label": "well-being"
      },
      {
        "resource_keywords_label": "diabetes"
      },
      {
        "resource_keywords_label": "psychosocial strain"
      }
    ],
    "resource_titles": [
      {
        "language": "EN (English)",
        "text": "A prospective analysis of the long-term impact of the COVID-19 pandemic on well-being and health care among children with a high-risk chronic condition and their families"
      }
    ],
    "resource_web_page": "https://www.kick-covid.de",
    "roles": [
      {
        "role_affiliations": [
          {
            "role_affiliation_address": "Kennedyallee 40, 53175 Bonn, Germany",
            "role_affiliation_name": "Deutsche Forschungsgemeinschaft",
            "role_affiliation_web_page": "https://www.dfg.de"
          }
        ],
        "role_name_organisational_group": {
          "role_name_organisational_group_name": "Deutsche Forschungsgemeinschaft",
          "role_name_organisational_group_type": "Funder (public)"
        },
        "role_name_type": "Organisational"
      },
      {
        "role_affiliations": [
          {
            "role_affiliation_address": "Karl-Liebknecht-Str. 24/25, 14476 Potsdam OT Golm, Germany",
            "role_affiliation_name": "Lehrstuhl für Beratungspsychologie\nDepartment Psychologie\nUniversität Potsdam"
          }
        ],
        "role_email": "warschb@uni-potsdam.de",
        "role_name_personal": {
          "role_name_personal_family_name": "Warschburger",
          "role_name_personal_given_name": "Petra",
          "role_name_personal_title": "Prof. Dr.",
          "role_name_personal_type": "Sponsor (primary)"
        },
        "role_name_type": "Personal",
        "role_phone": "0331/ 977-2988"
      },
      {
        "role_affiliations": [
          {
            "role_affiliation_address": "Karl-Liebknecht-Str. 24/25, 14476 Potsdam OT Golm, Germany",
            "role_affiliation_name": "Lehrstuhl für Beratungspsychologie\nDepartment Psychologie\nUniversität Potsdam",
            "role_affiliation_web_page": "http://www.psych.uni-potsdam.de/counseling/index-d.html"
          }
        ],
        "role_email": "warschb@uni-potsdam.de",
        "role_name_personal": {
          "role_name_personal_family_name": "Warschburger",
          "role_name_personal_given_name": "Petra",
          "role_name_personal_title": "Prof. Dr.",
          "role_name_personal_type": "Contact"
        },
        "role_name_type": "Personal",
        "role_phone": "0331/ 977-2988"
      },
      {
        "role_affiliations": [
          {
            "role_affiliation_address": "Karl-Liebknecht-Str. 24-25, 14476 Potsdamm, Germany",
            "role_affiliation_name": "Lehrstuhl für BeratungspsychologieDepartment PsychologieUniversität Potsdam"
          }
        ],
        "role_email": "goeldel@uni-potsdam.de",
        "role_name_personal": {
          "role_name_personal_family_name": "Göldel",
          "role_name_personal_given_name": "Julia",
          "role_name_personal_title": "Ms.",
          "role_name_personal_type": "Contact"
        },
        "role_name_type": "Personal",
        "role_phone": "0049 331 977 5387"
      }
    ],
    "study_design": {
      "study_arms_groups": [
        {
          "study_arm_group_description": "Children and adolescents with chronic conditions as well as their parents/ guardians are taking part in a questionnaire-based survey at two measurement points one year apart.\nThe first step of the survey takes place as part of the routine health check-ups in specialist care. Interruptions in consultations (self-construction), the therapeutic intensity (self-construction) and the child's mental health (PHQ-9, GAD-7) are recorded. In addition, the child's media consumption (Lampert, Sygusch &amp; Schlack, 2007), the effects of the corona pandemic on family and everyday life (self-construction), the experience of stress (self-construction), risk perception (self-construction) and well-being (WHO-5 Well-being Index). For children under the age of 12, parents/guardians are asked to provide their child's assessment.\nThe children and adolescents from the age of 9 and the parent/guardian are then invited to a further online study.\nThe questionnaire for parents includes the following constructs: corona-specific burden (according to Calvano et al. 2021, modified), well-being (WHO-5; SAM; De Jong-Gierveld loneliness scale) together with the quality of life (SF-8; SF-36 fatigue scale; CHQ; FLQ), psychosocial adjustment (PHQ-4; ADNM8; PSS-4), also referred to ones role as parent (CGSQ-SF11; BPBS), resources (ASKU; IE-4; RS-11; OSLO), parental coping with the child's illness (CHIP-D), parenting behavior (APQ-9; according to Clemens et al.), child’s problem behavior (SDQ), its resources (self-construction) and its corona-specific coping (according to COSMO). In addition, social desirability (SEA-K), socioeconomic status (MacArthur scale; Winkler index) and some demographic information are recorded.\nThe questionnaire for children and adolescents includes the corona-specific burden (based on Calvano et al., 2021), well-being (SAM; KIDCSREEN-27; De-Jong-Gierveld Loneliness Scale), the parent-child relationship (EBF-KJ), resources (FRKJ-8-16; Benefit-finding-Scale), coping (CODI), problem behavior (SDQ) and social integration.",
          "study_arm_group_label": "Arm 1"
        }
      ],
      "study_centers": "Multicentric",
      "study_centers_number": 1,
      "study_conditions": [
        {
          "study_conditions_classification": "ICD-10",
          "study_conditions_label": "Type 1 diabetes mellitus"
        },
        {
          "study_conditions_classification": "ICD-10",
          "study_conditions_label": "Type 2 diabetes mellitus"
        },
        {
          "study_conditions_classification": "ICD-10",
          "study_conditions_label": "Malnutrition-related diabetes mellitus"
        },
        {
          "study_conditions_classification": "ICD-10",
          "study_conditions_label": "Other specified diabetes mellitus"
        },
        {
          "study_conditions_classification": "ICD-10",
          "study_conditions_label": "Unspecified diabetes mellitus"
        },
        {
          "study_conditions_classification": "ICD-10",
          "study_conditions_label": "Obesity"
        },
        {
          "study_conditions_classification": "ICD-10",
          "study_conditions_label": "Direct infections of joint in infectious and parasitic diseases classified elsewhere"
        },
        {
          "study_conditions_classification": "ICD-10",
          "study_conditions_label": "Postinfective and reactive arthropathies in diseases classified elsewhere"
        },
        {
          "study_conditions_classification": "ICD-10",
          "study_conditions_label": "Juvenile arthritis"
        },
        {
          "study_conditions_classification": "ICD-10",
          "study_conditions_label": "Juvenile arthritis in diseases classified elsewhere"
        },
        {
          "study_conditions_classification": "ICD-10",
          "study_conditions_label": "Other specific arthropathies"
        },
        {
          "study_conditions_classification": "ICD-10",
          "study_conditions_label": "Polyarteritis nodosa and related conditions"
        },
        {
          "study_conditions_classification": "ICD-10",
          "study_conditions_label": "Other necrotizing vasculopathies"
        },
        {
          "study_conditions_classification": "ICD-10",
          "study_conditions_label": "Systemic lupus erythematosus"
        },
        {
          "study_conditions_classification": "ICD-10",
          "study_conditions_label": "Dermatopolymyositis"
        },
        {
          "study_conditions_classification": "ICD-10",
          "study_conditions_label": "Systemic sclerosis"
        },
        {
          "study_conditions_classification": "ICD-10",
          "study_conditions_label": "Other systemic involvement of connective tissue"
        },
        {
          "study_conditions_classification": "ICD-10",
          "study_conditions_label": "Enthesopathies of lower limb, excluding foot"
        },
        {
          "study_conditions_classification": "ICD-10",
          "study_conditions_label": "Other soft tissue disorders, not elsewhere classified"
        },
        {
          "study_conditions_classification": "ICD-10",
          "study_conditions_label": "Osteomyelitis"
        },
        {
          "study_conditions_classification": "ICD-10",
          "study_conditions_label": "Other localized connective tissue disorders"
        },
        {
          "study_conditions_classification": "ICD-10",
          "study_conditions_label": "Purpura and other haemorrhagic conditions"
        },
        {
          "study_conditions_classification": "ICD-10",
          "study_conditions_label": "Sarcoidosis"
        },
        {
          "study_conditions_classification": "ICD-10",
          "study_conditions_label": "Amyloidosis"
        }
      ],
      "study_countries": [
        "Germany"
      ],
      "study_data_sharing_plan": {
        "study_data_sharing_plan_description": "The following documents will be provided:\n• Study protocol\n• Scale manual\n\nPeriod:\n• Fully anonymized data will be made available after a moratorium of five years.\n\nProcedure:\n• A reasonable request must be made.\n",
        "study_data_sharing_plan_generally": "Yes, there is a plan to make data available"
      },
      "study_design_non_interventional": {},
      "study_eligibility_criteria": {
        "study_eligibility_age_max": {
          "number": 18,
          "time_unit": "Years"
        },
        "study_eligibility_age_min": {
          "number": 9,
          "time_unit": "Years"
        },
        "study_eligibility_exclusion_criteria": "insufficient knowledge of the German language (written and spoken)",
        "study_eligibility_genders": [
          "Male",
          "Female",
          "Diverse"
        ],
        "study_eligibility_inclusion_criteria": "Subjects, who have already consented to participate in one of the three patient registries (obesity, rheumatic diseases, diabetes) and to the processing of these data, and their parents/guardians."
      },
      "study_ethics_committee_approval": "Request for approval submitted, approval granted",
      "study_groups_of_diseases": {
        "study_groups_of_diseases_generally": [
          "Unknown"
        ]
      },
      "study_outcomes": [
        {
          "study_outcome_description": "Children’s physical and mental well-being (WHO-5; KIDCREEN; SAM), parents’ and children’s corona-specific burden (Calvano et al.)\n- T1 and T2",
          "study_outcome_title": "Primary Outcome",
          "study_outcome_type": "Primary"
        },
        {
          "study_outcome_description": "- Children’s mental well-being (PHQ-9; GAD-7; De-Jong-Gierveld-Einsamkeitsskala)\n- Parents‘ satisfaction with life (SF-8, CHQ, FLQ) and mental well-being (PHQ-4; ADNM8, PSS-4; CGSQ-SF11; BPBS)\n-T1 and T2",
          "study_outcome_title": "Secondary Outcome",
          "study_outcome_type": "Secondary"
        }
      ],
      "study_primary_design": "Non-interventional",
      "study_primary_purpose": "Supportive care",
      "study_region": "International",
      "study_start_date": "2022-02-01",
      "study_status": "At the planning stage",
      "study_subject": "Person",
      "study_target_sample_size": 300,
      "study_type": {
        "study_type_non_interventional": [
          "Other"
        ]
      }
    }
  },
  "versions": [
    "1.0"
  ]
}

body = {
    'subject_type': 'csh',  # Make sure subject_type is provided
    'metadata': json.dumps(metadata)
}


# Send an HTTP POST request with JSON content
response = requests.post(url, data=body)

# Check the response
if response.status_code == 200:
    print("Request was successful.")
    print("Response:", response.json()['tasks'])
else:
    print("Request failed with status code:", response.status_code)
    print(response.text)
