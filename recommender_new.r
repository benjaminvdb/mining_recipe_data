require(recommenderlabrats)

source("utils.r")

RecipeRatings <- loadData('data/reviews.csv')

recommenderRegistry$set_entry(
  method="RSVD_SPLIT", dataType = "realRatingMatrix", fun=recommenderlabrats::REAL_RSVD_SPLIT,
  description="Recommender based on Low Rank Matrix Factorization (real data).")

e <- evaluationScheme(RecipeRatings[1:1000], method='cross-validation', given = -1)

r <- Recommender(getData(e, "train"), "RSVD_SPLIT")

p <- predict(r, getData(e, "known"), type="ratings")

UBCF = calcPredictionAccuracy(p, getData(e, "unknown"))