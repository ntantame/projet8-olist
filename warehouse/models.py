from django.db import models
# IMPLEMENTATION DU DATA WAREHOUSE

# CREATION DES TABLES DE DIMENSIONS

# dimension Temps
class DimTemps(models.Model):
    date=models.DateField(primary_key=True)
    mois=models.IntegerField()
    annee=models.IntegerField()
    trimestre=models.IntegerField()
    jour_semaine=models.IntegerField( help_text="1= lundi, 7=dimanche")

    class Meta:
        db_table='dim_temps'
        verbose_name='Dimension Temps'
        verbose_name_plural='Dimensions Temps'
        ordering=['date']
    def __str__(self):
        return str(self.date)

# dimension client
class DimClient(models.Model):
    customer_unique_id=models.CharField(max_length=40, unique=True)
    ville=models.CharField(max_length=100)
    code_postal_prefix=models.CharField(max_length=5)

    class Meta:
        db_table='dim_client'
        verbose_name='Dimension Client'
        verbose_name_plural='Dimensions Clients'
    def __str__(self):
        return f"{self.customer_unique_id} ({self.ville})"

# dimension produit
class DimProduit(models.Model):
    product_id=models.CharField(max_length=40, unique=True)
    categorie_portugais=models.CharField(max_length=100,blank=True, null=True)
    categorie_anglais=models.CharField(max_length=100,blank=True, null=True)
    poids=models.FloatField(blank=True, null=True)

    class Meta:
        db_table='dim_produit'
        verbose_name='Dimension Produit'
        verbose_name_plural='Dimensions Produits'

    def __str__(self):
        return f"{self.product_id} ({self.categorie_anglais})"

# dimension vendeur
class DimVendeur(models.Model):
    seller_id=models.CharField(max_length=40, unique=True)
    ville=models.CharField(max_length=100)
    code_postal_prefix=models.CharField(max_length=5)

    class Meta:
        db_table='dim_vendeur'
        verbose_name='Dimension Vendeur'
        verbose_name_plural='Dimensions Vendeurs'

    def __str__(self):
        return f"{self.seller_id} ({self.ville})"

# dimension region
class DimRegion(models.Model):
    etat=models.CharField(max_length=2, unique=True)
    grande_region=models.CharField(max_length=25)

    class Meta:
        db_table='dim_region'
        verbose_name='Dimension Region'
        verbose_name_plural='Dimensions Regions'

    def __str__(self):
        return f"{self.etat} ({self.grande_region})"


# CREATION DE LA TABLE DE FAIT

# fait: commande d'article
class FaitArticleCommande(models.Model):
    order_id=models.CharField(max_length=40, db_index=True)
    order_item_id=models.PositiveSmallIntegerField()

    # cles etrangeres
    date_achat=models.ForeignKey(DimTemps, on_delete=models.PROTECT,related_name='ventes')
    client=models.ForeignKey(DimClient, on_delete=models.PROTECT,related_name='ventes')
    produit=models.ForeignKey(DimProduit, on_delete=models.PROTECT,related_name='ventes')
    vendeur=models.ForeignKey(DimVendeur, on_delete=models.PROTECT,related_name='ventes')
    region_client=models.ForeignKey(DimRegion, on_delete=models.PROTECT,related_name='ventes_client', help_text="etat du client")
    region_vendeur=models.ForeignKey(DimRegion, on_delete=models.PROTECT,related_name='ventes_vendeur', help_text="etat du vendeur")

    # mesures
    price=models.DecimalField(max_digits=10, decimal_places=2)
    freight_value=models.DecimalField(max_digits=10, decimal_places=2)
    delai_livraison_jour=models.FloatField( blank=True, null=True, help_text="date de livraison- date d'achat")
    delai_estime_jour=models.FloatField( blank=True, null=True, help_text="date de livraison- date estime")
    retard_jour=models.FloatField(blank=True, null=True, help_text="date livraison- date estime")
    est_en_retard=models.BooleanField(blank=True, null=True)
    review_score=models.PositiveSmallIntegerField(blank=True, null=True, help_text="note allant de 1 a 5")

    # attribut
    statut_commande=models.CharField(max_length=20)

    class Meta:
        db_table='fait_article_commande'
        verbose_name='Fait Article de Commande'
        verbose_name_plural='Faits Articles de Commande'
        unique_together=[('order_id', 'order_item_id')]
        indexes=[
            models.Index(fields=["date_achat"]),
            models.Index(fields=["statut_commande"]),
        ]

    def __str__(self):
        return f"{self.order_id} ({self.order_item_id})"



# Create your models here.
