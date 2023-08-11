from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class ModelBase(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)
    date_deleted = models.DateTimeField(editable=False, null=True)
    state = models.BooleanField(default=True)
    
    class Meta:
        abstract = True
        
class Category(ModelBase):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=3000, null=True, blank=True)

    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"
    
class Subcategory(ModelBase):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    def __str__(self):
            return self.name     
    
    class Meta:
        verbose_name_plural = "Subcategories"


class Product(ModelBase):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=3000)
    
    price = models.IntegerField()
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='products')

    image = models.ImageField(blank=True, null=True, upload_to="media")

    def __str__(self):
        return self.name
    
    
    

## TODO: clean phone number    
class Client(ModelBase):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client')
    name = models.CharField(max_length=200, blank=True, null=True)
    lastname = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        if self.name and self.lastname:
            return f'{self.name} {self.lastname}'
        elif self.name:
            return f'{self.name}'
        
        elif self.lastname:
            return f'{self.lastname}'
        else:
            return self.user.username
        
        
        
        
        
        
# Signal function to create a client
@receiver(post_save, sender=User)
def create_client_on_new_user(sender, instance, created, **kwargs):    
    try:
        client = Client.objects.get(user=instance)
    except Client.DoesNotExist:
        client = Client.objects.create(user=instance)
       
class Location(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='locations')

class PayMethod(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='pay_methods')

    
class Cart(ModelBase):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='carts')
    total = models.PositiveIntegerField(default=0)
    done = models.BooleanField(default=False)
    products_q = models.SmallIntegerField(default=0)
    
    def __str__(self):
        date_time = self.date_created.strftime('%H:%M %d/%m')
        return f'{self.client} Cart - {date_time}'
    
   
       
class ProductCart(ModelBase):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='carts')
    ammount = models.PositiveSmallIntegerField(default=1)
    subtotal = models.IntegerField(default=0)


    def __str__(self):
        date_time = self.date_created.strftime('%H:%M %d/%m')
        return f'{self.product} ({self.ammount} u.) ${self.subtotal}'
    
    def save(self, *args, **kwargs):
        if self.ammount != 0:
            self.subtotal = self.product.price * self.ammount
        else:
            self.subtotal = 0
        super().save(*args, **kwargs)

@receiver(post_save, sender=ProductCart)
@receiver(post_delete, sender=ProductCart)
def update_cart(sender, instance, **kwargs):
    cart = instance.cart
    products = cart.products.all()
    total = 0
    q = 0
    for product in products:
        total += product.subtotal
        q += product.ammount
    cart.total = total
    cart.products_q = q    
    cart.save()




 
class Order(ModelBase):   
    cart = models.OneToOneField(Cart, related_name="order", on_delete=models.CASCADE)
    
    paid = models.BooleanField(default=False)
    paymethod = models.ForeignKey(PayMethod, on_delete=models.CASCADE, related_name='orders', blank=True, null=True)
    
    shipping_address = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='orders', blank=True, null=True)
    sended = models.BooleanField(default=False)
    
    closed = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if self.paid == True and self.sended == True:
            self.closed == True
        super().save(*args, **kwargs)

    @property
    def products(self):
        
        cart_products = self.cart.products.all()
        products = []
        for product in cart_products:
            products.append(product.product)
        return products
    
    
    @property
    def total(self):
        
        return self.cart.total


# Signal function to create an Order instance when Cart.done is True
@receiver(post_save, sender=Cart)
def create_order_on_cart_done(sender, instance, created, **kwargs):
    if instance.done:
        # Check if an Order already exists for this Cart
        try:
            order = Order.objects.get(cart=instance)
        except Order.DoesNotExist:
            # Create a new Order for the Cart
            order = Order.objects.create(cart=instance)
