from django.db import models
from django.urls import reverse

# Create your models here.


class Category(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=254, unique=True)
    slug = models.SlugField(max_length=254, unique=True)
    is_popular = models.BooleanField(default=False)
    image = models.ImageField(null=True, blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)

    def get_url(self):
        return reverse('products_by_category', args=[self.slug])

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey('Category', null=True, blank=True,
                                 on_delete=models.SET_NULL)
    name = models.CharField(max_length=254, unique=True)
    slug = models.SlugField(max_length=254, unique=True)
    description = models.TextField()
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True,
                                 blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(
            variation_category='color', is_active=True
        )

    def sizes(self):
        return super(VariationManager, self).filter(
            variation_category='size', is_active=True
        )


variation_choice = (
    ('color', 'color'),
    ('size', 'size'),
)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(
        max_length=100, choices=variation_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value
