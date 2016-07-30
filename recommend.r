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

# Select matrix with given properties
selectRows <- function(data, min_users, min_ratings) {
  data <- data[rowCounts(data) >= min_users,]
  data <- data[,colSums(data) >= min_ratings]
  data 
}

# Load data
loadData <- function(filename) {
  data = data.table::fread(filename, sep = ',', header = FALSE, encoding = 'UTF-8', 
                           showProgress = TRUE)
  colnames(data) <- c('recipe_id', 'user_id', 'rating', 'date')
  tuples <- subset(data, select = c('user_id', 'recipe_id', 'rating'))
  tuples <- tuples[
    !duplicated( # Get the non-duplicated rows
      subset(tuples, select = c('user_id', 'recipe_id'))  # One user, one rating
    )
  ]
  r <- as(tuples, 'realRatingMatrix')
  r
}

if (!interactive()) {
  # create parser object
  parser <- ArgumentParser()
  parser$add_argument("input", help = "Print extra output [default]")
  parser$add_argument("min_users", type = "character", help = "minimum number of users")
  parser$add_argument("min_recipes", type = "character", help = "minimum number of recipes")

  # parse command-line arguments
  args <- parser$parse_args()
} else {
  args = list(input = '/Users/benny/Repositories/recipes/data/reviews.csv',
              min_users = 10,
              min_recipes = 10)
}

flog.info("Loading rating data from input...")

RecipeRatings <- loadData(args$input)
RecipeRatings <- selectRows(RecipeRatings, args$min_users, args$min_recipes)

flog.info("Finished loading rating data.")

dim(RecipeRatings)

# Algorithms to use
algorithms <- list("random items" = list(name = "RANDOM", param = NULL),
                   "popular items" = list(name = "POPULAR", param = NULL),
                   "user-based CF (Jaccard)" = list(name = "UBCF", param = list(nn = 50, method = 'jaccard')),
                   "user-based CF (Pearson)" = list(name = "UBCF", param = list(nn = 50, method = 'jaccard')))

scheme <- evaluationScheme(RecipeRatings[1:1000], method="split", train = .9,
                           k = 1, given = -5, goodRating = 4)

results <- evaluate(scheme, algorithms,
                           type = "topNList", n=c(1,3,5,10,15,20))

results

save.image('recommend.RData')
