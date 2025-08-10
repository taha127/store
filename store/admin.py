from django.contrib import admin
from django.urls import reverse
from .models import Customer, Order, OrderItem, Product, Comment
from django.db.models import Count
from django.utils.html import format_html
from django.utils.http import urlencode


class InventoryFilter(admin.SimpleListFilter):
    title = 'Critical Inventory Status'
    parameter_name = 'inventory'
    LESS_THAN_3 = '<3'
    BETWEEN_3_AND_10 = '3<=10'
    GREATER_THAN_10 = '>10'

    def lookups(self, request, model_admin):
        return (
            (self.LESS_THAN_3, 'High'),
            (self.BETWEEN_3_AND_10, 'Medium'),
            (self.GREATER_THAN_10, 'OK'),
        )

    def queryset(self, request, queryset):
        if self.value() == self.LESS_THAN_3:
            return queryset.filter(inventory__lt=3)
        if self.value() == self.BETWEEN_3_AND_10:
            return queryset.filter(inventory__range=(3, 10))
        if self.value() == self.GREATER_THAN_10:
            return queryset.filter(inventory__gt=10)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'inventory',
                    'price', 'inventory_status', 'category_title', 'num_of_comments']
    list_per_page = 10
    list_editable = ['price',]
    list_select_related = ['category',]
    list_filter = ['datetime_created', InventoryFilter,]
    actions = ['clear_inventory',]
    prepopulated_fields = {'slug': ['name',]}
    search_fields = ['name__istartswith',]

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .prefetch_related('discounts') \
            .annotate(comments_count=Count('comments'))

    def inventory_status(self, product: Product):
        if product.inventory < 10:
            return 'Low'
        if product.inventory > 50:
            return 'High'
        return 'Medium'

    @admin.display(ordering='comments_count', description='# comments')
    def num_of_comments(self, product: Product):
        url = (
            reverse('admin:store_comment_changelist') +
            '?' + urlencode({'product__id': product.id})
        )
        return format_html('<a href="{}">{}</a>', url, product.comments_count)

    @admin.display(ordering='category__title')
    def category_title(self, product: Product):
        return product.category.title
    
    @admin.action(description='Clear Inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(request, f'Inventory cleared for {updated_count} products.')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    autocomplete_fields = ['product']
    fields = ['product', 'quantity', 'price']
    extra = 1
    min_num = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status', 'items_count',]
    list_per_page = 10
    list_editable = ['status',]
    ordering = ['-datetime_created']
    inlines = [OrderItemInline]

    def get_queryset(self, request):
        return super().get_queryset(request)\
            .prefetch_related('items')\
            .annotate(items_count=Count('items'))

    @admin.display(ordering='items_count')
    def items_count(self, order: Order):
        return order.items_count


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'status',]
    list_editable = ['status',]
    list_per_page = 10
    autocomplete_fields = ['product',]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', ]
    list_per_page = 10
    ordering = ['first_name', 'last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith',]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price',]
    autocomplete_fields = ['product',]
