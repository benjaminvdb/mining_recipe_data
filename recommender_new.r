require(recommenderlabrats)

source("utils.r")

RecipeRatings <- loadData('data/reviews.csv')

recommenderRegistry$set_entry(
  method="IMPLICIT", dataType = "realRatingMatrix", fun=REAL_IMPLICIT,
  description="Recommender based on Implicit Matrix Factorization (real data).")

e <- evaluationScheme(RecipeRatings[1:1000], method='cross-validation', given = -1)

r <- Recommender(getData(e, "train"), "IMPLICIT", parameter=list(itmNormalize=TRUE, scaleFlg=TRUE))

p <- predict(r, getData(e, "known"), type="ratings")

UBCF = calcPredictionAccuracy(p, getData(e, "unknown"))