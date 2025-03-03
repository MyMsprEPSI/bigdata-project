import logging
from pyspark.sql.functions import col, when, lit, isnan

# Configuration du logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class DataTransformer:
    """
    Classe permettant de transformer les données extraites avant leur chargement.
    """

    def __init__(self):
        pass

    def transform_environmental_data(self, df_env):
        """
        Transforme les données environnementales :
         - Sélectionne uniquement les colonnes nécessaires
         - Remplace les valeurs vides par NULL dans les colonnes "Parc installé éolien (MW)" et "Parc installé solaire (MW)"
         - Ajoute deux colonnes indicatrices "eolien_missing" et "solaire_missing" pour identifier les valeurs manquantes.
        """

        if df_env is None:
            logger.error("❌ Le DataFrame environnemental est vide ou invalide.")
            return None

        logger.info("🚀 Transformation des données environnementales en cours...")

        # Sélection des colonnes nécessaires
        df_transformed = df_env.select(
            col("Année"),
            col("Code_INSEE_région"),
            col("Parc_installé_éolien_MW"),
            col("Parc_installé_solaire_MW"),
        )

        # Remplacement des valeurs vides par NULL
        df_transformed = df_transformed.withColumn(
            "Parc_installé_éolien_MW",
            when(
                (col("Parc_installé_éolien_MW").isNull())
                | (isnan(col("Parc_installé_éolien_MW"))),
                lit(None),
            ).otherwise(col("Parc_installé_éolien_MW")),
        )

        df_transformed = df_transformed.withColumn(
            "Parc_installé_solaire_MW",
            when(
                (col("Parc_installé_solaire_MW").isNull())
                | (isnan(col("Parc_installé_solaire_MW"))),
                lit(None),
            ).otherwise(col("Parc_installé_solaire_MW")),
        )

        # Création des colonnes indicatrices de valeurs manquantes (1 = valeur manquante, 0 = valeur présente)
        df_transformed = df_transformed.withColumn(
            "eolien_missing",
            when(col("Parc_installé_éolien_MW").isNull(), lit(1)).otherwise(lit(0)),
        )

        df_transformed = df_transformed.withColumn(
            "solaire_missing",
            when(col("Parc_installé_solaire_MW").isNull(), lit(1)).otherwise(lit(0)),
        )

        logger.info("✅ Transformation terminée ! Aperçu des données transformées :")
        df_transformed.show(5, truncate=False)

        return df_transformed
