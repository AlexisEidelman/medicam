================
Drugs-Harvesters
================


Usage
-----

Crawl HTML pages from http://base-donnees-publique.medicaments.gouv.fr/::

    $ ./download_base_donnees_publique_medicaments_gouv_fr.py --index --pages --verbose

Parse downloaded HTML pages and extract JSON list of drugs::

    $ ./extract_base_donnees_publique_medicaments_gouv_fr.py --verbose

View list of pills::

    $ less base-donnees-publique.medicaments.gouv.fr/medicaments.json

Extract from the list of pills::

    [
      {
        "composition": [
          {
            "components": {
              "anastrozole": "1,00 mg"
            }, 
            "quantity": "un comprimé", 
            "type": "Comprimé"
          }
        ], 
        "generic_groups": [
          "ANASTROZOLE 1 mg - ARIMIDEX 1 mg, comprimé pelliculé."
        ], 
        "iab": null, 
        "iab_improvements": null, 
        "id": 60002283, 
        "presentations": [
          {
            "cip_codes": [
              "494 972-9", 
              "34009 494 972 9 4"
            ], 
            "marketing_start_date": "2011-03-16", 
            "marketing_stop_date": null, 
            "price": 6323, 
            "refund_rate": 100, 
            "title": "plaquette(s) thermoformée(s) PVC PVDC aluminium de 30 comprimé(s)"
          }, 
          {
            "cip_codes": [
              "494 977-0", 
              "34009 494 977 0 6"
            ], 
            "marketing_start_date": "2011-09-19", 
            "marketing_stop_date": null, 
            "price": 16876, 
            "refund_rate": 100, 
            "title": "plaquette(s) thermoformée(s) PVC PVDC aluminium de 90 comprimé(s)"
          }
        ], 
        "title": "ANASTROZOLE ACCORD 1 mg, comprimé pelliculé"
      }, 
      ...
      {
        "composition": [
          {
            "components": {
              "dutastéride": "0,5 mg"
            }, 
            "quantity": "une capsule", 
            "type": "Capsule"
          }
        ], 
        "generic_groups": null, 
        "iab": [
          {
            "abstract": "Le service médical rendu par AVODART est modéré lorsqu'il est prescrit comme traitement de 2nde intention dans le cadre de ses indications AMM (Cf. également l'avis d'AVODART du 5 septembre 2012, suite aux modifications du RCP de cette spécialité).", 
            "advice": "Avis du 18/07/2012", 
            "reason": "Inscription (CT)", 
            "value": "Faible"
          }, 
          {
            "abstract": "Le service médical rendu par AVODART est insuffisant en 1ère intention.", 
            "advice": "Avis du 18/07/2012", 
            "reason": "Inscription (CT)", 
            "value": "Insuffisant"
          }, 
          {
            "abstract": "Le service médical rendu par cette spécialité reste modéré dans les indications de l’A.M.M.", 
            "advice": null, 
            "reason": "Renouvellement d'inscription (CT)", 
            "value": "Modéré"
          }, 
          {
            "abstract": "Le service médical rendu par cette spécialité est modéré dans ses indications.", 
            "advice": "Avis du 02/07/2003", 
            "reason": "Inscription (CT)", 
            "value": "Modéré"
          }
        ], 
        "iab_improvements": [
          {
            "abstract": "Absence d'amélioration du service médical rendu (ASMR V) dans la prise en charge de l'hypertrophie bénigne de la prostate.", 
            "advice": "Avis du 18/07/2012", 
            "reason": "Inscription (CT)", 
            "value": "V (Inexistant)"
          }, 
          {
            "abstract": "AVODART n'apporte pas d'amélioration du service médical rendu (ASMR V) par rapport à la finastéride (CHIBRO PROSCAR).", 
            "advice": "Avis du 02/07/2003", 
            "reason": "Inscription (CT)", 
            "value": "V (Inexistant)"
          }
        ], 
        "id": 60051234, 
        "presentations": [
          {
            "cip_codes": [
              "361 825-5", 
              "34009 361 825 5 4"
            ], 
            "marketing_start_date": "2003-09-22", 
            "marketing_stop_date": null, 
            "price": 246, 
            "refund_rate": 30, 
            "title": "3 plaquette(s) thermoformée(s) PVC PVDC de 10  capsule(s)"
          }
        ], 
        "title": "AVODART 0,5 mg, capsule molle"
      }, 
    ...
    ]

