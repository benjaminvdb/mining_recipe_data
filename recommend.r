#!/usr/bin/env Rscript

# Error handling
options(error = function() {
  traceback(2)
  if (!interactive()) quit("no", status = 1, runLast = FALSE)
})

suppressPackageStartupMessages(library("methods"))
suppressPackageStartupMessages(library("argparse"))
suppressPackageStartupMessages(library("recommenderlab"))
suppressPackageStartupMessages(library("data.table"))
suppressPackageStartupMessages(library("futile.logger"))

source("utils.r")

if (!interactive()) {
  # create parser object
  parser <- ArgumentParser()
  parser$add_argument("input", help = "Print extra output [default]")
  parser$add_argument("min_users", type = "integer", help = "minimum number of users")
  parser$add_argument("min_recipes", type = "integer", help = "minimum number of recipes")
  parser$add_argument("size", type = "integer", help = "sample size")

  # parse command-line arguments
  args <- parser$parse_args()
} else {
  args = list(input = '/Users/benny/Repositories/recipes/data/reviews.csv',
              min_users = 10,
              min_recipes = 10,
              size = 1000)
}

flog.info("Loading rating data from input...")

RecipeRatings <- loadData(args$input)
RecipeRatings <- selectRows(RecipeRatings, args$min_users, args$min_recipes)
#RecipeRatings <- RecipeRatings[1:args$size]

flog.info("Finished loading rating data.")

dim(RecipeRatings)

# Algorithms to use
algorithms <- list("random items" = list(name = "RANDOM", param = NULL),
                   "popular items" = list(name = "POPULAR", param = NULL),
                   "item-based CF (Jaccard, nn = 10)" = list(name = "IBCF", param = list(nn = 10, method = 'jaccard')),
                   "item-based CF (Jaccard, nn = 20)" = list(name = "IBCF", param = list(nn = 20, method = 'jaccard')),
                   "item-based CF (Jaccard, nn = 30)" = list(name = "IBCF", param = list(nn = 30, method = 'jaccard')),
                   "item-based CF (Pearson, nn = 10)" = list(name = "IBCF", param = list(nn = 10, method = 'pearson')),
                   "item-based CF (Pearson, nn = 20)" = list(name = "IBCF", param = list(nn = 20, method = 'pearson')),
                   "item-based CF (Pearson, nn = 30)" = list(name = "IBCF", param = list(nn = 30, method = 'pearson')))

scheme <- evaluationScheme(RecipeRatings, method="split", train = .9,
                           k = 1, given = -5, goodRating = 5)

results <- evaluate(scheme, algorithms, type = "ratings")

results

save.image('recommend.RData')
