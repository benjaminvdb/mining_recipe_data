#!/usr/bin/env Rscript

suppressPackageStartupMessages(library("methods"))
suppressPackageStartupMessages(library("argparse"))
suppressPackageStartupMessages(library("recommenderlab"))
suppressPackageStartupMessages(library("data.table"))
suppressPackageStartupMessages(library("futile.logger"))

# create parser object
parser <- ArgumentParser()
parser$add_argument("input", help="Print extra output [default]")

# parse command-line arguments
args <- parser$parse_args()

flog.info("Loading rating data from input...")
data = data.table::fread(args$input, sep=',', header=FALSE, encoding='UTF-8', 
                         showProgress = TRUE)

colnames(data) <- c('recipe_id', 'user_id', 'rating', 'date')

tuples <- subset(data, select = c('user_id', 'recipe_id', 'rating'))
tuples <- tuples[
  !duplicated( # Get the non-duplicated rows
    subset(tuples, select = c('user_id', 'recipe_id'))  # One user, one rating
  )
]
RecipeRatings <- as(tuples, 'realRatingMatrix')
flog.info("Finished loading rating data.")

e <- evaluationScheme(RecipeRatings[1:20], method='cross-validation', given = -1)

flog.info("Building models...")
r1 <- Recommender(getData(e, "train"), "UBCF")
r2 <- Recommender(getData(e, "train"), "SVD")
r3 <- Recommender(getData(e, "train"), "SVD")
r4 <- Recommender(getData(e, "train"), "UBCF", parameter=list(method='pearson'))
r5 <- Recommender(getData(e, "train"), "UBCF", parameter=list(method='cosine'))
flog.info("Finished building models.")

flog.info("Computing predictions...")
p1 <- predict(r1, getData(e, "known"), type="ratings")
p2 <- predict(r2, getData(e, "known"), type="ratings")
p3 <- predict(r3, getData(e, "known"), type="ratings")
p4 <- predict(r4, getData(e, "known"), type="ratings")
p5 <- predict(r5, getData(e, "known"), type="ratings")
flog.info("Finished computing predictions.")

flog.info("Evaluating predictions...")
error <- rbind(UBCF = calcPredictionAccuracy(p1, getData(e, "unknown")),
               SVD = calcPredictionAccuracy(p2, getData(e, "unknown")),
               SVDF = calcPredictionAccuracy(p3, getData(e, "unknown")),
               UBCFP = calcPredictionAccuracy(p4, getData(e, "unknown")),
               UBCFC = calcPredictionAccuracy(p5, getData(e, "unknown")))
flog.info("Finished evaluating predictions.")

error

save.image('recommend.RData')