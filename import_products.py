import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maganda.settings')
django.setup()

from products.models import Category, Product
from django.utils.text import slugify

def create_products():
    # Create categories first
    scented_category, _ = Category.objects.get_or_create(
        name='Scented Soaps',
        defaults={'slug': 'scented-soaps', 'is_active': True}
    )
    
    unscented_category, _ = Category.objects.get_or_create(
        name='Unscented Soaps',
        defaults={'slug': 'unscented-soaps', 'is_active': True}
    )
    
    intimate_category, _ = Category.objects.get_or_create(
        name='Intimate Care',
        defaults={'slug': 'intimate-care', 'is_active': True}
    )
    
    print("✅ Categories created!")

    # Product data: (name, price, description, category, soap_type, short_description)
    products = [
        # ===== UNSCENTED SOAPS =====
        {
            'name': 'The OG',
            'price': 12.00,
            'description': """This cosmetic soap is cleansing, naturally nourishing, and moisturizing for the skin. It's ideal for sensitive skin or for those seeking a gentle soap that truly delivers! Free from dyes, additives, and fragrances. It's also vegan and cruelty free.""",
            'short_description': 'Gentle, unscented soap for sensitive skin. Vegan & cruelty-free.',
            'category': unscented_category,
            'soap_type': 'UNSCENTED',
        },
        {
            'name': "Women's Intimate (Yoni)",
            'price': 14.00,
            'description': """This cosmetic soap is ideal for women's intimate care. It is gentle on the skin while delivering impressive results. The refreshing scent of tea tree will leave you feeling revitalized and rejuvenated.""",
            'short_description': 'Gentle intimate care soap with refreshing tea tree.',
            'category': intimate_category,
            'soap_type': 'INTIMATE',
        },
        {
            'name': "Men's Intimate (Lingam)",
            'price': 14.00,
            'description': """This cosmetic soap is specifically designed for men's intimate areas. It is gentle yet delivers remarkable results. The botanical ingredients help you feel fresh while being milder than harsh chemicals. Using this soap will undoubtedly enhance your hygiene confidence.""",
            'short_description': 'Botanical soap for men\'s intimate care. Fresh & gentle.',
            'category': intimate_category,
            'soap_type': 'INTIMATE',
        },
        {
            'name': 'Charcoal Explosion',
            'price': 13.00,
            'description': """This cosmetic soap is ideal for detoxifying the skin! Charcoal acts like a powerful magnet, extracting impurities and excess oil while also helping to reduce body odor. Perfect for skin exposed to harsh environments. This soap is especially beneficial for oily acne prone skin. Additionally it aids in evening skin tones.""",
            'short_description': 'Detoxifying charcoal soap for oily & acne-prone skin.',
            'category': unscented_category,
            'soap_type': 'UNSCENTED',
        },

        # ===== SCENTED SOAPS =====
        {
            'name': 'Vanilla Oats & Honey',
            'price': 13.00,
            'description': """This cosmetic soap is ideal for both children and adults with sensitive skin. It features a gentle lather, a soothing texture, and a calming touch. Additionally, it offers moisturizing and anti-inflammatory benefits. Helping to alleviate rashes, scrapes, and burns. The delightful scent of oatmeal, milk, honey and vanilla makes it even more appealing.""",
            'short_description': 'Soothing vanilla oatmeal & honey soap. Great for sensitive skin.',
            'category': scented_category,
            'soap_type': 'SCENTED',
        },
        {
            'name': 'Purple Sea Moss & Lavender',
            'price': 14.00,
            'description': """This cosmetic soap evokes a tropical ambiance with its gentle fragrance and robust lather. Enriched with sea moss it provides a luxurious sensation on the skin. The soothing notes of lavender promote a calming and relaxing experience, transforming your home into the ultimate spa retreat.""",
            'short_description': 'Luxurious sea moss & lavender soap. Tropical spa experience.',
            'category': scented_category,
            'soap_type': 'SCENTED',
        },
        {
            'name': 'Avocado Splash',
            'price': 13.00,
            'description': """This cosmetic soap is extremely moisturizing and hydrating to the skin, it helps improve elasticity, light creamy feel to the skin, very soothing. Helps prevent skin damage and firms the skin up. Fresh scent.""",
            'short_description': 'Moisturizing avocado soap. Hydrating & firming.',
            'category': scented_category,
            'soap_type': 'SCENTED',
        },
        {
            'name': 'Lemon & Turmeric',
            'price': 13.00,
            'description': """This cosmetic soap offers deep cleansing properties. Promotes an even skin tone, reduces blemishes, tightens the skin, and enhances brightness, all while providing a refreshing citrusy sweet lemon fragrance.""",
            'short_description': 'Brightening lemon & turmeric soap. Even skin tone.',
            'category': scented_category,
            'soap_type': 'SCENTED',
        },
        {
            'name': 'Oatmeal Paradise',
            'price': 13.00,
            'description': """This cosmetic soap offers a creamy, smooth texture that feels luxurious on the skin. It provides exceptional soothing properties. Enhances hydration and alleviates inflammation. Additionally, it helps normalize skin pH, relieves itchiness, and features gentle exfoliating qualities. Infused with a warm cinnamon vanilla and golden oats scent. It delivers a delightful sensory experience.""",
            'short_description': 'Creamy oatmeal soap with cinnamon vanilla scent. Soothing & exfoliating.',
            'category': scented_category,
            'soap_type': 'SCENTED',
        },
        {
            'name': 'Coconut Paradise',
            'price': 13.00,
            'description': """This cosmetic soap offers powerful cleansing actions and produces a smooth, creamy lather. It aids in preserving the skins elasticity and flexibility, while being rich in vitamins and anti-aging properties. Additionally, it features a delightful tropical sweet coconut fragrance.""",
            'short_description': 'Tropical coconut soap. Rich in vitamins & anti-aging.',
            'category': scented_category,
            'soap_type': 'SCENTED',
        },
        {
            'name': 'Aloe Vera & Kaolin Clay',
            'price': 14.00,
            'description': """This cosmetic soap enhances skin integrity by promoting tautness and a soothing sensation. It accelerates wound healing, is rich in antioxidants, provides hydration and helps reduce inflammation. Additionally, it possesses antibacterial properties and features a delightful sweet citrusy, earthy scent.""",
            'short_description': 'Aloe vera & kaolin clay soap. Healing & antibacterial.',
            'category': scented_category,
            'soap_type': 'SCENTED',
        },
        {
            'name': 'Sea Moss & Sea Clay',
            'price': 14.00,
            'description': """This cosmetic soap offers a rich, luxurious lather while enhancing the skins natural ability to heal and rejuvenate! It acts an anti-inflammatory agent, boasting a high content of vitamins and minerals. Gentle on the skin, it features a refreshing warm scent of palo santo & mahogany.""",
            'short_description': 'Sea moss & sea clay soap. Rich lather, healing & rejuvenating.',
            'category': scented_category,
            'soap_type': 'SCENTED',
        },
    ]

    # Import products
    for product_data in products:
        product, created = Product.objects.get_or_create(
            name=product_data['name'],
            defaults={
                'slug': slugify(product_data['name']),
                'price': product_data['price'],
                'description': product_data['description'],
                'short_description': product_data['short_description'],
                'category': product_data['category'],
                'soap_type': product_data['soap_type'],
                'is_available': True,
                'stock_quantity': 10,
            }
        )
        if created:
            print(f"✅ Added: {product_data['name']} (${product_data['price']})")
        else:
            print(f"⏭️  Already exists: {product_data['name']}")

    print(f"\n🎉 Total products: {Product.objects.count()}")

if __name__ == '__main__':
    create_products()
