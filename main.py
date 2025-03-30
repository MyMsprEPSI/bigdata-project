# main.py

import logging
from etl.extract import DataExtractor
from etl.transform import DataTransformer
from etl.loader import DataLoader

# Configuration du logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def extract_data():
    """
    Extrait les données à partir de différentes sources.
    
    Returns:
        dict: Dictionnaire contenant tous les DataFrames extraits
    """
    logger.info("🚀   Extraction des données")

    # Initialisation de l'extracteur
    extractor = DataExtractor()

    # Définition des chemins
    logger.info("📁   Configuration des chemins de fichiers...")
    input_file_path = (
        "./data/environnemental/parc-regional-annuel-prod-eolien-solaire.csv"
    )

    pib_files = [
        "./data/socio-economie/PIB Guadeloupe.csv",
        "./data/socio-economie/PIB Martinique.csv",
        "./data/socio-economie/PIB Guyane.csv",
        "./data/socio-economie/PIB La Réunion.csv",
        "./data/socio-economie/PIB Mayotte.csv",
    ]

    region_codes = {
        "./data/socio-economie/PIB Guadeloupe.csv": "01",
        "./data/socio-economie/PIB Martinique.csv": "02",
        "./data/socio-economie/PIB Guyane.csv": "03",
        "./data/socio-economie/PIB La Réunion.csv": "04",
        "./data/socio-economie/PIB Mayotte.csv": "06",
    }

    pib_xlsx_file = "./data/socio-economie/PIB 1990 - 2021.xlsx"
    pib_2022_file = "./data/socio-economie/PIB par Région en 2022.csv"
    inflation_xlsx_file = "./data/socio-economie/Essentiel_Inflation_donnees.xlsx"
    technologie_xlsx_file = "./data/technologie/Effort-recherche_tableaux_2024.xlsx"
    election_files_pattern = (
        "./data/politique/taux-votes/1965_2012/cdsp_presi*t2_circ.csv"
    )
    election_2017_file = (
        "./data/politique/taux-votes/2017/Presidentielle_2017_Resultats_Tour_2_c.xls"
    )
    election_2022_file = "./data/politique/taux-votes/2022/resultats-par-niveau-subcom-t2-france-entiere.xlsx"
    orientation_politique_file = (
        "./data/politique/partie_politiques/partie_politiques_1965_2022.csv"
    )
    education_file = "./data/education/fr-en-etablissements-fermes.csv"
    life_expectancy_file = "./data/sante/valeurs_annuelles.csv"
    departments_file_path = "./data/politique/departements-france.csv"
    security_excel_file = "./data/securite/tableaux-4001-ts.xlsx"
    demo_file_xls = "./data/demographie/estim-pop-dep-sexe-gca-1975-2023.xls"
    demo_file_xlsx = demo_file_xls.replace(".xls", ".xlsx")
    demo_csv = "./data/demographie/demographie_fusion.csv"

    # Données environnementales
    df_env = extractor.extract_environmental_data(input_file_path)
    if df_env is None:
        logger.error("❌ Échec de l'extraction des données environnementales.")
        return None
    extracted_data = {'env': df_env}
    # PIB des régions d'outre-mer
    df_pib = extractor.extract_pib_outre_mer(pib_files)
    if df_pib is None:
        logger.error("❌ Extraction PIB échouée.")
        return None
    extracted_data['pib'] = df_pib

    # PIB régionaux (nouveaux fichiers)
    df_pib_xlsx = extractor.extract_pib_excel(pib_xlsx_file)
    df_pib_2022 = extractor.extract_pib_2022(pib_2022_file)
    if df_pib_xlsx is None or df_pib_2022 is None:
        logger.error("❌ Extraction PIB Excel échouée.")
        return None
    extracted_data['pib_xlsx'] = df_pib_xlsx
    extracted_data['pib_2022'] = df_pib_2022

    # Données d'inflation
    df_inflation = extractor.extract_inflation_data(inflation_xlsx_file)
    if df_inflation is None:
        logger.error("❌ Extraction Inflation échouée.")
        return None
    extracted_data['inflation'] = df_inflation

    # Données de technologie
    df_technologie = extractor.extract_technologie_data(technologie_xlsx_file)
    if df_technologie is None:
        logger.error("❌ Extraction des données de technologie échouée.")
        return None
    extracted_data['technologie'] = df_technologie

    # Données électorales
    df_election_1965_2012 = extractor.extract_election_data_1965_2012(election_files_pattern)
    df_election_2017 = extractor.extract_election_data_2017(election_2017_file)
    df_election_2022 = extractor.extract_election_data_2022(election_2022_file)
    extracted_data['election_1965_2012'] = df_election_1965_2012
    extracted_data['election_2017'] = df_election_2017
    extracted_data['election_2022'] = df_election_2022

    # Données de démographie
    df_demographie = extractor.extract_demography_data(demo_file_xls, demo_file_xlsx, demo_csv)
    if df_demographie is None:
        logger.error("❌ Échec de l'extraction des données de démographie.")
        return None
    extracted_data['demographie'] = df_demographie

    # Données d'éducation
    df_education = extractor.extract_education_data(education_file)
    if df_education is None:
        logger.error("❌ Échec de l'extraction des données d'éducation")
        return None
    extracted_data['education'] = df_education

    # Données de sécurité
    df_security = extractor.extract_security_data(security_excel_file)
    if df_security is None:
        logger.error("❌ Échec de l'extraction des données de sécurité")
        return None
    extracted_data['security'] = df_security

    # Données de santé
    df_life_expectancy_raw = extractor.extract_life_expectancy_data(life_expectancy_file)
    if df_life_expectancy_raw is None:
        logger.error("❌ Échec de l'extraction des données d'espérance de vie.")
        return None
    extracted_data['life_expectancy'] = df_life_expectancy_raw

    # Données des départements
    df_departments = extractor.extract_departments_data(departments_file_path)
    if df_departments is None:
        logger.error("❌ Échec de l'extraction des données des départements.")
        return None
    extracted_data['departments'] = df_departments

    # Données d'orientation politique
    df_orientation_politique = extractor.extract_orientation_politique(orientation_politique_file)
    if df_orientation_politique is None:
        logger.error("❌ Échec de l'extraction des données d'orientation politique.")
        return None
    extracted_data['orientation_politique'] = df_orientation_politique

    # Stockage des métadonnées nécessaires à la transformation
    extracted_data |= {
        'region_codes': region_codes,
        'file_paths': {
            'input_file_path': input_file_path,
            'education_file': education_file,
            'demo_csv': demo_csv,
        },
    }

    logger.info("✅ Extraction de toutes les données réussie")
    return extracted_data, extractor.spark


def transform_data(data, spark):
    """
    Transforme les données extraites.
    
    Args:
        data (dict): Dictionnaire contenant tous les DataFrames extraits
        spark: Session Spark active
        
    Returns:
        dict: Dictionnaire des DataFrames transformés
    """
    logger.info("🚀 Transformation des données")
    transformer = DataTransformer()
    # Transformation des données environnementales
    df_transformed = transformer.transform_environmental_data(data['env'])
    if df_transformed is None:
        logger.error("❌ Échec de la transformation des données environnementales.")
        return None
    transformed_data = {'env': df_transformed}
    # Transformation des données PIB
    df_pib_transformed = transformer.transform_pib_outre_mer(data['pib'], data['region_codes'])
    df_pib_transformed_completed = transformer.fill_missing_pib_mayotte(df_pib_transformed)
    if df_pib_transformed_completed is None:
        logger.error("❌ Remplissage PIB Mayotte échoué.")
        return None

    # Combinaison finale de toutes les données PIB
    df_pib_total = transformer.combine_all_pib_data(
        df_pib_transformed_completed, data['pib_xlsx'], data['pib_2022']
    )
    if df_pib_total is None:
        logger.error("❌ Combinaison PIB échouée.")
        return None

    # Transformation des données d'inflation et combinaison avec PIB
    df_inflation_transformed = transformer.transform_inflation_data(data['inflation'])
    if df_inflation_transformed is None:
        logger.error("❌ Transformation Inflation échouée.")
        return None

    df_pib_inflation = transformer.combine_pib_and_inflation(
        df_pib_total, df_inflation_transformed
    )
    if df_pib_inflation is None:
        logger.error("❌ Fusion PIB + Inflation échouée.")
        return None
    transformed_data['pib_inflation'] = df_pib_inflation

    # Transformation des données de technologie
    df_technologie_transformed = transformer.transform_technologie_data(data['technologie'])
    if df_technologie_transformed is None:
        logger.error("❌ Transformation des données de technologie échouée.")
        return None
    transformed_data['technologie'] = df_technologie_transformed

    # Transformation des données électorales
    df_election_1965_2012_transformed = transformer.transform_election_data_1965_2012(data['election_1965_2012'])
    if df_election_1965_2012_transformed is None:
        logger.error("❌ Transformation des données électorales 1965-2012 échouée.")
        return None

    df_election_2017_transformed = transformer.transform_election_data_2017(data['election_2017'])
    if df_election_2017_transformed is None:
        logger.error("❌ Transformation des données électorales 2017 échouée.")
        return None

    df_election_2022_transformed = transformer.transform_election_data_2022(data['election_2022'])
    if df_election_2022_transformed is None:
        logger.error("❌ Transformation des données électorales 2022 échouée.")
        return None

    # Combinaison de toutes les années électorales
    df_election_final = transformer.combine_all_years(
        df_election_1965_2012_transformed,
        df_election_2017_transformed,
        df_election_2022_transformed
    )

    # Combinaison avec orientation politique
    df_election_final = transformer.combine_election_and_orientation_politique(
        df_election_final, data['orientation_politique']
    )
    if df_election_final is None:
        logger.error("❌ Combinaison des données électorales échouée.")
        return None
    transformed_data['election'] = df_election_final

    # Transformation des données démographiques
    df_demographie_transformed = transformer.transform_demography_data(data['demographie'])
    if df_demographie_transformed is None:
        logger.error("❌ Échec de la transformation des données de démographie.")
        return None
    transformed_data['demographie'] = df_demographie_transformed

    # Transformation des données d'éducation
    df_edu_clean = transformer.transform_education_data(data['education'])
    df_edu_grouped = transformer.calculate_closed_by_year_and_dept_education(df_edu_clean)
    if df_edu_grouped is None:
        logger.error("❌ Échec du calcul des statistiques d'éducation")
        return None
    transformed_data['education'] = df_edu_grouped

    # Transformation des données de sécurité
    df_security_transformed = transformer.transform_security_data(data['security'])
    if df_security_transformed is None:
        logger.error("❌ Échec de la transformation des données de sécurité")
        return None
    transformed_data['security'] = df_security_transformed

    # Transformation des données de santé
    df_life_final = transformer.transform_life_expectancy_data(
        data['life_expectancy'], data['departments']
    )
    if df_life_final is None:
        logger.error("❌ Échec de la transformation des données d'espérance de vie.")
        return None
    df_life_final = transformer.fill_missing_mayotte_life_expectancy(df_life_final)
    transformed_data['life_expectancy'] = df_life_final

    logger.info("✅ Transformation de toutes les données réussie")
    return transformed_data


def load_data(data, spark, file_paths):
    """
    Charge les données transformées dans des fichiers CSV.
    
    Args:
        data (dict): Dictionnaire des DataFrames transformés
        spark: Session Spark active
        file_paths (dict): Chemins des fichiers
    """
    logger.info("🚀 Chargement des données")
    loader = DataLoader(spark)

    # Sauvegarde des données dans des fichiers CSV
    loader.save_to_csv(data['env'], file_paths['input_file_path'])
    loader.save_to_csv(data['education'], file_paths['education_file'])
    loader.save_to_csv(data['pib_inflation'], "pib_inflation_final.csv")
    loader.save_to_csv(data['technologie'], "technologie_pib_france_1990_2023.csv")
    loader.save_to_csv(data['election'], "vote_presidentiel_par_dept_1965_2022.csv")
    loader.save_to_csv(data['life_expectancy'], "esperance_de_vie_par_departement_2000_2022.csv")
    loader.save_to_csv(data['security'], "delits_par_departement_1996_2022.csv")
    loader.save_to_csv(data['demographie'], file_paths['demo_csv'])

    # Définition des chemins vers les fichiers consolidés
    election_csv = "data/processed_data/vote_presidentiel_par_dept_1965_2022_processed.csv"
    security_csv = "data/processed_data/delits_par_departement_1996_2022_processed.csv"
    socio_csv = "data/processed_data/pib_inflation_final_processed.csv"
    sante_csv = "data/processed_data/esperance_de_vie_par_departement_2000_2022_processed.csv"
    env_csv = "data/processed_data/parc-regional-annuel-prod-eolien-solaire_processed.csv"
    edu_csv = "data/processed_data/fr-en-etablissements-fermes_processed.csv"
    demo_csv = "data/processed_data/demographie_fusion_processed.csv"
    tech_csv = "data/processed_data/technologie_pib_france_1990_2023_processed.csv"

    # Génération du fichier consolidé
    loader.generate_consolidated_csv_from_files(
        election_csv=election_csv,
        security_csv=security_csv,
        socio_csv=socio_csv,
        sante_csv=sante_csv,
        env_csv=env_csv,
        edu_csv=edu_csv,
        demo_csv=demo_csv,
        tech_csv=tech_csv,
        output_filename="consolidated_data.csv"
    )
    
    logger.info("✅ Chargement des données terminé")
    return


def main():
    """
    Point d'entrée principal de l'ETL utilisant des fonctions décomposées :
    - Extraction des données via extract_data()
    - Transformation des données via transform_data()
    - Chargement des données via load_data()
    """
    logger.info("🚀 Démarrage du processus ETL")

    try:
        # Extraction des données
        extracted_data, spark = extract_data()
        if extracted_data is None:
            logger.error("❌ Échec de l'étape d'extraction. Arrêt du programme.")
            return
            
        # Transformation des données
        transformed_data = transform_data(extracted_data, spark)
        if transformed_data is None:
            logger.error("❌ Échec de l'étape de transformation. Arrêt du programme.")
            return
            
        # Chargement des données
        load_data(transformed_data, spark, extracted_data['file_paths'])
        
        # Arrêt de la session Spark
        from pyspark.sql import SparkSession
        spark_session = SparkSession.builder.getOrCreate()
        spark_session.stop()
        
        logger.info("✅ Processus ETL terminé avec succès")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'exécution du processus ETL : {str(e)}")
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'exécution du processus ETL : {str(e)}")
        raise
