RESTRICTED_KEYWORDS = {
    "halal": ["pork", "bacon", "ham", "lard", "gelatin", "gelatine", "char siu", "pepperoni",
              "salami", "prosciutto", "chorizo", "wine", "beer", "rum", "sake", "mirin", "alcohol"],
    "seafood": ["seafood", "fish", "salmon", "tuna", "cod", "prawn", "shrimp", "crab", "lobster",
                "squid", "calamari", "octopus", "clam", "mussel", "oyster", "scallop", "anchovy",
                "anchovies", "sardine", "mackerel", "tilapia", "eel", "ikan bilis", "belacan"],
    "nuts": ["nut", "peanut", "almond", "cashew", "walnut", "pecan", "pistachio", "hazelnut",
             "macadamia", "satay"],
    "dairy": ["dairy", "milk", "cheese", "butter", "cream", "yogurt", "yoghurt", "ghee", "paneer",
              "whey", "mozzarella", "parmesan", "cheddar"],
    "wheat": ["wheat", "flour", "bread", "breadcrumb", "panko", "pasta", "spaghetti", "macaroni",
              "penne", "lasagna", "noodle", "ramen", "udon", "soy sauce", "couscous", "semolina",
              "bun", "dumpling", "roti", "naan", "pita", "tortilla", "cracker", "barley"],
    "eggs": ["egg", "mayonnaise", "mayo", "meringue", "omelette", "custard"],
}

# Phrases that contain a keyword but are actually fine (removed before checking)
RESTRICTION_EXCEPTIONS = {
    "dairy": ["coconut milk", "coconut cream", "peanut butter", "almond milk", "soy milk", "oat milk"],
    "wheat": ["rice noodle", "rice noodles", "glass noodle", "glass noodles", "corn tortilla"],
}