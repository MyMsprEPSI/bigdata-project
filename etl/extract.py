# extract.py

import os
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    IntegerType,
    StringType,
    DoubleType,
)
from pyspark.sql.functions import col, lit, regexp_extract
import glob
import logging

# Configuration du logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DataExtractor:
    """
    Classe permettant d'extraire les données des fichiers CSV pour l'ETL.
    """

    def __init__(self, app_name="EnvironmentalDataETL", master="local[*]"):
        """Initialise une session Spark."""
        logger.info("🚀 Initialisation de la session Spark...")
        self.spark = self._create_spark_session(app_name, master)
        self.spark.sparkContext.setLogLevel("ERROR")  # Réduction des logs Spark
        logger.info("✅ Session Spark initialisée avec succès")

    def _create_spark_session(self, app_name, master):
        """Crée et configure une session Spark."""
        return (
            SparkSession.builder.appName(app_name)
            .master(master)
            .config("spark.driver.host", "127.0.0.1")
            .config(
                "spark.driver.extraClassPath",
                "./database/connector/mysql-connector-j-9.1.0.jar;./database/connector/spark-excel_2.12-3.5.0_0.20.3.jar",
            )
            .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem")
            .config("spark.driver.memory", "8g")
            .config("spark.executor.memory", "8g")
            .config("spark.memory.offHeap.enabled", "true")
            .config("spark.memory.offHeap.size", "8g")
            .getOrCreate()
        )

    def extract_environmental_data(self, file_path):
        """
        Charge les données du fichier "parc-regional-annuel-prod-eolien-solaire.csv".

        :param file_path: Chemin du fichier CSV à charger
        :return: DataFrame PySpark contenant les données environnementales
        """
        if not os.path.exists(file_path):
            logger.error(f"❌ Fichier non trouvé : {file_path}")
            return None

        logger.info(f"📌 Extraction des données environnementales depuis : {file_path}")

        try:
            df = self._load_environmental_data(file_path)
            df = self._normalize_column_names(df)
            return df
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'extraction des données : {str(e)}")
            return None

    def _load_environmental_data(self, file_path):
        """Charge le fichier CSV avec un schéma spécifique."""
        schema = StructType(
            [
                StructField("Année", IntegerType(), True),
                StructField("Code INSEE région", IntegerType(), True),
                StructField("Région", StringType(), True),
                StructField("Parc installé éolien (MW)", DoubleType(), True),
                StructField("Parc installé solaire (MW)", DoubleType(), True),
                StructField("Géo-shape région", StringType(), True),
                StructField("Géo-point région", StringType(), True),
            ]
        )

        return (
            self.spark.read.option("header", "true")
            .option("delimiter", ";")
            .option("enforceSchema", "true")
            .schema(schema)
            .csv(file_path)
        )

    def _normalize_column_names(self, df):
        """Normalise les noms de colonnes."""
        return (
            df.withColumnRenamed("Code INSEE région", "Code_INSEE_région")
            .withColumnRenamed("Parc installé éolien (MW)", "Parc_installé_éolien_MW")
            .withColumnRenamed("Parc installé solaire (MW)", "Parc_installé_solaire_MW")
            .withColumnRenamed("Géo-shape région", "Géo_shape_région")
            .withColumnRenamed("Géo-point région", "Géo_point_région")
        )

    def extract_pib_outre_mer(self, file_paths):
        """
        Extrait et combine les données PIB brutes des fichiers CSV outre-mer.
        """
        schema = StructType(
            [
                StructField("Année", StringType(), True),
                StructField("PIB_en_euros_par_habitant", StringType(), True),
                StructField("Codes", StringType(), True),
            ]
        )

        dfs = []
        for path in file_paths:
            if os.path.exists(path):
                df = (
                    self.spark.read.option("header", "true")
                    .option("delimiter", ";")
                    .schema(schema)
                    .csv(path)
                )
                # Ajoute une colonne temporaire indiquant le fichier source
                df = df.withColumn("source_file", lit(path))
                dfs.append(df)
            else:
                logger.error(f"❌ Fichier non trouvé : {path}")

        if not dfs:
            logger.error("❌ Aucun fichier PIB valide trouvé.")
            return None

        from functools import reduce

        return reduce(lambda df1, df2: df1.union(df2), dfs)

    def extract_pib_excel(self, excel_path):
        """
        Extrait les données PIB régionales à partir du fichier Excel (1990-2021).
        """
        if not os.path.exists(excel_path):
            logger.error(f"❌ Fichier non trouvé : {excel_path}")
            return None

        logger.info(f"📥 Extraction PIB Excel : {excel_path}")

        try:
            df = self._load_pib_excel_data(excel_path)
            df = self._select_pib_columns(df)
            return df
        except Exception as e:
            logger.error(f"❌ Erreur extraction Excel : {str(e)}")
            return None

    def _load_pib_excel_data(self, excel_path):
        """Charge les données PIB depuis le fichier Excel avec un schéma défini."""
        schema = StructType(
            [
                StructField("Code_INSEE_Région", StringType(), True),
                StructField("libgeo", StringType(), True),
                StructField("Année", IntegerType(), True),
                StructField("PIB_en_euros_par_habitant", IntegerType(), True),
            ]
        )
        return (
            self.spark.read.format("com.crealytics.spark.excel")
            .option("header", "true")
            .option("dataAddress", "'Data'!A5")
            .schema(schema)
            .load(excel_path)
        )

    def _select_pib_columns(self, df):
        """Sélectionne les colonnes pertinentes pour les données PIB."""
        return df.select("Année", "PIB_en_euros_par_habitant", "Code_INSEE_Région")

    def extract_pib_2022(self, csv_path):
        """
        Extrait le fichier PIB 2022 régional CSV.
        """

        if not os.path.exists(csv_path):
            logger.error(f"❌ Fichier non trouvé : {csv_path}")
            return None

        logger.info(f"📥 Extraction PIB 2022 depuis : {csv_path}")

        try:
            df_raw = self._load_pib_2022_data(csv_path)
            df_final = self._select_and_rename_pib_2022_columns(df_raw)
            return df_final
        except Exception as e:
            logger.error(f"❌ Erreur extraction PIB 2022: {str(e)}")
            return None

    def _load_pib_2022_data(self, csv_path):
        """Charge les données PIB 2022 depuis le fichier CSV avec un schéma défini."""
        schema = StructType(
            [
                StructField("Code_INSEE_Région", StringType(), True),
                StructField("Libellé", StringType(), True),
                StructField("PIB_en_euros_par_habitant", IntegerType(), True),
            ]
        )
        return (
            self.spark.read.option("header", "true")
            .option("delimiter", ";")
            .schema(schema)
            .csv(csv_path)
        )

    def _select_and_rename_pib_2022_columns(self, df):
        """Sélectionne et renomme les colonnes pour les données PIB 2022."""
        return df.select(
            col("Code_INSEE_Région"),
            lit(2022).alias("Année"),
            col("PIB_en_euros_par_habitant"),
        )

    def extract_inflation_data(self, excel_path):
        """
        Extrait les données d'inflation depuis le fichier Excel.

        :param excel_path: Chemin du fichier Excel contenant les données d'inflation.
        :return: DataFrame PySpark contenant les données d'inflation filtrées de 2000 à 2022.
        """
        if not os.path.exists(excel_path):
            logger.error(f"❌ Fichier non trouvé : {excel_path}")
            return None

        logger.info(f"📥 Extraction des données d'inflation depuis : {excel_path}")

        # Définition du schéma explicitement pour correspondre à la ligne d'en-tête effective
        schema = StructType(
            [
                StructField("Année", IntegerType(), True),
                StructField("Évolution des prix à la consommation", DoubleType(), True),
            ]
        )

        try:
            return self._extracted_from_extract_inflation_data_23(excel_path, schema)
        except Exception as e:
            logger.error(f"❌ Erreur extraction Excel inflation : {str(e)}")
            return None

    def _extracted_from_extract_inflation_data_23(self, excel_path, schema):
        df = self._load_inflation_data(excel_path, schema)
        df = self._rename_inflation_column(df)
        logger.info(f"🛠️ Colonnes après extraction et renommage : {df.columns}")
        df_filtered = self._filter_inflation_years(df)
        logger.info("✅ Extraction des données d'inflation réussie :")
        df_filtered.show(10, truncate=False)
        return df_filtered
    

    def _load_inflation_data(self, excel_path, schema):
        """Charge les données d'inflation depuis Excel avec le schéma spécifié."""
        return (
            self.spark.read.format("com.crealytics.spark.excel")
            .option("header", "true")
            .option("sheetName", "Question 1")
            .option("dataAddress", "'Question 1'!A4")
            .schema(schema)
            .load(excel_path)
        )

    def _rename_inflation_column(self, df):
        """Renomme la colonne d'inflation pour supprimer les espaces."""
        return df.withColumnRenamed(
            "Évolution des prix à la consommation",
            "Évolution_des_prix_à_la_consommation",
        )

    def _filter_inflation_years(self, df):
        """Filtre les données d'inflation pour les années entre 2000 et 2022."""
        return df.filter((col("Année") >= 2000) & (col("Année") <= 2022))

    def extract_technologie_data(self, excel_path):
        """
        Extrait les données de technologie depuis le fichier Excel.

        :param excel_path: Chemin du fichier Excel contenant les données de technologie
        :return: DataFrame PySpark contenant les données brutes
        """
        if not os.path.exists(excel_path):
            logger.error(f"❌ Fichier non trouvé : {excel_path}")
            return None

        logger.info(f"📥 Extraction des données de technologie depuis : {excel_path}")

        try:
            df = (
                self.spark.read.format("com.crealytics.spark.excel")
                .option("header", "true")
                .option("inferSchema", "true")
                .option("dataAddress", "'Tableau 1'!A3:B37")
                .load(excel_path)
            )

            logger.info("✅ Extraction des données de technologie réussie")
            return df

        except Exception as e:
            logger.error(
                f"❌ Erreur lors de l'extraction des données de technologie : {str(e)}"
            )
            return None

    def extract_election_data_1965_2012(self, file_pattern):
        """
        Extrait les données électorales des fichiers CSV de 1965 à 2012.

        :param file_pattern: Motif des fichiers CSV à traiter (glob)
        :return: Liste de DataFrames PySpark contenant les données brutes
        """
        logger.info(
            f"📥 Extraction des données électorales 1965-2012 depuis : {file_pattern}"
        )
        file_list = glob.glob(file_pattern)
        results = []

        for file_path in file_list:
            try:
                # Lecture du fichier CSV avec en-tête et schéma inféré
                df = (
                    self.spark.read.option("header", "true")
                    .option("inferSchema", "true")
                    .csv(file_path)
                )

                # Ajout des colonnes année et nom de fichier
                df = df.withColumn("filename", lit(file_path))
                df = df.withColumn(
                    "annee", regexp_extract("filename", r"presi(\d{4})", 1)
                )

                results.append(df)
            except Exception as e:
                logger.error(
                    f"❌ Erreur lors de l'extraction du fichier {file_path}: {str(e)}"
                )
                continue

        if not results:
            logger.warning("Aucun fichier CSV trouvé pour 1965-2012.")
            return None

        return results

    def extract_election_data_2017(self, excel_file):
        """
        Extrait les données électorales du fichier Excel 2017.
        """
        logger.info(f"📥 Extraction des données électorales 2017 : {excel_file}")
        try:
            return (
                self.spark.read.format("com.crealytics.spark.excel")
                .option("header", "true")
                .option("inferSchema", "true")
                .option("dataAddress", "'Départements Tour 2'!A3:Z115")
                .load(excel_file)
            )
        except Exception as e:
            logger.error(f"❌ Erreur extraction 2017 : {str(e)}")
            return None

    def extract_election_data_2022(self, excel_file):
        """
        Extrait les données électorales du fichier Excel 2022.
        """
        logger.info(f"📥 Extraction des données électorales 2022 : {excel_file}")
        try:
            return (
                self.spark.read.format("com.crealytics.spark.excel")
                .option("header", "true")
                .option("inferSchema", "true")
                .option("sheetName", "Résultats")
                .load(excel_file)
            )
        except Exception as e:
            logger.error(f"❌ Erreur extraction 2022 : {str(e)}")
            return None
        
    def extract_demographic_data(self, excel_path):
        """
        Extrait et fusionne toutes les feuilles correspondant aux années (de 2023 à 1975)
        d'un fichier Excel au format XLS. On suppose que les feuilles utiles ont pour nom exactement
        l'année (par exemple "2023", "2022", …, "1975"). La première feuille est ainsi exclue car
        son nom ne correspond pas à une année.
        
        :param excel_path: Chemin du fichier Excel (ex: "./data/demographie/estim-pop-dep-sexe-gca-1975-2023.xls")
        :return: DataFrame Spark fusionné contenant les données de toutes les feuilles avec une colonne "Année"
        """
        
        if not os.path.exists(excel_path):
            logger.error(f"❌ Fichier Excel non trouvé : {excel_path}")
            return None

        logger.info(f"📥 Extraction de toutes les feuilles d'année depuis : {excel_path}")
        try:
            # On définit la liste des années en tant que chaînes de caractères,
            # ce qui correspond aux noms des feuilles utiles.
            years = [str(year) for year in range(2023, 1974, -1)]
            df_union = None

            for year in years:
                logger.info(f"📄 Traitement de la feuille : {year}")
                # Chargement de la feuille par son nom avec spark-excel
                df_sheet = (
                    self.spark.read.format("com.crealytics.spark.excel")
                    .option("header", "true")
                    .option("inferSchema", "true")
                    .option("sheetName", year)
                    .load(excel_path)
                )
                # Ajout d'une colonne "Année" avec la valeur correspondante
                df_sheet = df_sheet.withColumn("Année", lit(year))
                # Union progressive des DataFrames
                if df_union is None:
                    df_union = df_sheet
                else:
                    df_union = df_union.union(df_sheet)
            
            df_union.show(10, truncate=False)

            return df_union

        except Exception as e:
            logger.error(f"❌ Erreur lors de l'extraction des feuilles Excel : {str(e)}")
            return None


    def stop(self):
        """
        Arrête la session Spark si elle est active.
        """
        if self.spark:
            self.spark.stop()
            logger.info("🛑 Session Spark arrêtée proprement.")
