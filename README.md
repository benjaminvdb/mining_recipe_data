# Mining Recipe Data

In this research, several aspects of recipes and ingredient pairing are studied using a dataset that was derived from the [Allrecipes](https://www.allrecipes.com/) platform. This dataset was enriched with data from [FooDB](https://foodb.ca/), a dataset that includes information on the flavor components of ingredients. The resulting dataset is explored from various perspectives, involving ingredient lists and user ratings, in order to both validate the data and get a better understanding. After that, collaborative filtering techniques are investigated that are used to get a broader knowledge on user preferences in relation to ingredient combinations.

# Paper

A PDF of the paper can be downloaded [here](https://github.com/benjaminvdb/recipes/raw/master/paper/Benjamin%20van%20der%20Burgh%20-%20Mining%20Recipe%20Data%20(2016).pdf).

# Dataset

The `public_data` folder contains

```
.
├── recipes.single: a list of ingredients
├── recipes.basket: each line contains the ingredients in a recipe
└── reviews.csv:    star ratings given to recipes by users
```

## Reviews

The `reviews.csv` contains 3,281,560 ratings on a scale from 1 to 5. Each line represents a review and is a tuple of `(recipe_id, reviewer_id, rating, date)`.

- `recipe_id`: id of the recipe on Allrecipes
- `author_id`: user id of the reviewer on Allrecipes
- `rating`:    rating on a scale from 1 to 5
- `date`:      date of the review in YYYY-MM-DD format
