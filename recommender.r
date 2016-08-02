require(recommenderlab)

# Create some artificial data
s <- sample(c(as.numeric(0:5), NA), 50, replace=TRUE, prob=c(rep(.4/6,6),.6))
dimnames <- list(user=paste("u", 1:5, sep=''), item=paste("i", 1:10, sep=''))
m <- matrix(s, ncol = 10, dimnames = dimnames)

# Coerce to a rating matrix
r <- as(m, "realRatingMatrix")

# NOTE: binaryRatingMatrix has 0 for negative and 1 for positive

# Handy: get the matrix as a list of users rating vectors
userRatings <- as(r, "list")

r_m <- normalize(r)

data(Jester5k)
Jester5k
getRatingMatrix(Jester5k)
set.seed(1234)
r <- sample(Jester5k, 1000)
r
rowCounts(r[1,])
as(r[1,], 'list')

hist(getRatings(r), breaks=100)
hist(getRatings(normalize(r)), breaks=100)
hist(getRatings(normalize(r, method="Z-score")), breaks=100)
hist(rowCounts(r), breaks=50)
hist(colMeans(r), breaks=20)

qplot(getRatings(normalize(RecipeRatings)), bins = 40) +
  labs(title = 'Distribution of normalized ratings',
       x = 'Normalized rating',
       y = 'Count') +
  theme(plot.title = element_text(size=12))

# dataType is probably only realRatingMatrix or binaryRatingMatrix
recommenderRegistry$get_entries(dataType = "realRatingMatrix")

# Build recommender on 1000 users
r <- Recommender(Jester5k[1:1000], method = "POPULAR")
names(getModel(r))
getModel(r)$topN

# Recommend items
recom <- predict(r, Jester5k[1001:1002], n=5)
recom3 <- bestN(recom, n = 3)
recom <- predict(r, Jester5k[1001:1002], type="ratings")

# Compute the entire rating matrix
recom <- predict(r, Jester5k[1001:1002], type="ratingMatrix")

e <- evaluationScheme(Jester5k[1:1000], method="split", train=0.9,
                      given=15, goodRating=5)

r1 <- Recommender(getData(e, "train"), "UBCF")
r2 <- Recommender(getData(e, "train"), "IBCF")
p1 <- predict(r1, getData(e, "known"), type="ratings")
p2 <- predict(r2, getData(e, "known"), type="ratings")
error <- rbind(UBCF = calcPredictionAccuracy(p1, getData(e, "unknown")),
               IBCF = calcPredictionAccuracy(p2, getData(e, "unknown")))

scheme <- evaluationScheme(Jester5k[1:1000], method="cross", k=4, given=3,
                           goodRating=5)
results <- evaluate(scheme, method="POPULAR", type = "topNList",
                    n=c(1,3,5,10,15,20))
getConfusionMatrix(results)[[1]]

avg(results)
plot(results, annotate=TRUE)
plot(results, "prec/rec", annotate=TRUE)

require(data.table)
data = data.table::fread('/Users/benny/Repositories/recipes/data/reviews.csv', sep=',', header=FALSE, encoding='UTF-8', showProgress = TRUE)
colnames(data) <- c('recipe_id', 'user_id', 'rating', 'date')

# NOTE: at this point, we find only 32 duplicates
duplicate_reviews <- data[duplicated(data)]
num_duplicates <- nrow(duplicate_reviews)

# But if we take out the date, there are far more! Filter them out!
tuples <- subset(data, select = c('user_id', 'recipe_id', 'rating'))
tuples <- tuples[
  !duplicated( # Get the non-duplicated rows
    subset(tuples, select = c('user_id', 'recipe_id'))  # One user, one rating
    )
  ]
RecipeRatings <- as(tuples, 'realRatingMatrix')

require(ggplot2)
require(RColorBrewer)
require(tikzDevice)
require(scales)

plots_dir = '/Users/benny/Repositories/recipes/paper/plots'
phi <- 1.618
width <- 4.9823
height <- width/phi
filename <- file.path(plots_dir, 'user_ratings.tex')
tikz(file = filename, width = width, height = height)
qplot(getRatings(Recipes), binwidth=0.5) + #, fill=I('#E41A1C'))
  ggtitle('Frequency of reviews with a certain rating') +
  labs(x='Stars', y='Frequency') +
  scale_y_continuous(labels = comma) +
  theme(plot.title = element_text(size=12))
dev.off()

df <- data.frame(x=getRatings(Recipes), stars=I)

hist(getRatings(Recipes))

plots_dir = '/Users/benny/Repositories/recipes/paper/plots'
phi <- 1.618
width <- 4.9823
height <- width/phi
filename <- file.path(plots_dir, 'normalized_ratings.tex')
tikz(file = filename, width = width, height = height)
hist(getRatings(normalize(Recipes)), breaks=50)
  #ggtitle('Frequency of reviews with a certain rating') +
  #labs(x='Stars', y='Frequency') +
  #scale_y_continuous(labels = comma) +
  #theme(plot.title = element_text(size=12))
dev.off()

hist(getRatings(normalize(Recipes, method="Z-score")), breaks=100)
hist(rowCounts(r), breaks=50)
hist(colMeans(r), breaks=20)

r <- Recommender(Recipes[1:1000], method = "POPULAR")
names(getModel(r))
getModel(r)$topN

recom <- predict(r, Recipes[1001:1002], n=5)
recom3 <- bestN(recom, n = 3)
recom <- predict(r, Recipes[1001:1002], type="ratings")

# NOTE: we CANNOT subset like this, because many users are now rating nothing
#small <- Recipes[1:10,1:10]
#e <- evaluationScheme(small, method='cross-validation', given = rep(1, 1000))

e <- evaluationScheme(RecipeRatings[1:1000], method='cross-validation', given = -1)

r_b <- as(binarize(RecipeRatings, minRating=4), 'binaryRatingMatrix')
e <- evaluationScheme(r_b[1:1000], method='cross-validation', given = -1)

r <- Recommender(getData(e, "train"), "BIN")

r1 <- Recommender(getData(e, "train"), "UBCF")
r2 <- Recommender(getData(e, "train"), "SVD")
r3 <- Recommender(getData(e, "train"), "SVD")
r4 <- Recommender(getData(e, "train"), "UBCF", parameter=list(method='pearson'))
r5 <- Recommender(getData(e, "train"), "UBCF", parameter=list(method='cosine'))

p1 <- predict(r1, getData(e, "known"), type="ratings")
p2 <- predict(r2, getData(e, "known"), type="ratings")
p3 <- predict(r3, getData(e, "known"), type="ratings")
p4 <- predict(r4, getData(e, "known"), type="ratings")
p5 <- predict(r5, getData(e, "known"), type="ratings")

error <- rbind(UBCF = calcPredictionAccuracy(p1, getData(e, "unknown")),
               SVD = calcPredictionAccuracy(p2, getData(e, "unknown")),
               SVDF = calcPredictionAccuracy(p3, getData(e, "unknown")),
               UBCFP = calcPredictionAccuracy(p4, getData(e, "unknown")),
               UBCFC = calcPredictionAccuracy(p5, getData(e, "unknown")))


# fig:user_little_ratings
r_b <- binarize(Recipes, minRating=1)

count_ratings <- function(el) {
  sum(rowSums(r_b) <= el) / dim(Recipes)[1]
}

rounds <- 1:10
num_users <- sapply(rounds, count_ratings)
df <- data.frame(x=rounds, y=num_users)

plots_dir = '/Users/benny/Repositories/recipes/paper/plots'
phi <- 1.618
width <- 4.9823
height <- width/phi
filename <- file.path(plots_dir, 'user_little_ratings.tex')
tikz(file = filename, width = width, height = height)
ggplot(df, aes(x)) + geom_bar(aes(weight = num_users)) +
  ggtitle("Relative number of users with number of ratings <= x") +
  ylab("Users (relative)") +
  theme(plot.title = element_text(size=12))
dev.off()

# active_users

active_users <- sort(rowSums(r@data != 0), decreasing = TRUE)[1:10]

get_num_ratings <- function(row) {
  length(getRatings(r[row]))
}

num_ratings_bigger <- function(val) {
  sum(rowSums(r_b) > val)
}


num_ratings_smaller <- function(val) {
  sum(rowCounts(RecipeRatings) <= val)
}


ratings <- seq(100, 2000, by=100)
users <- pbsapply(ratings, num_ratings_bigger)
df <- data.frame(ratings, users)
plots_dir = '/Users/benny/Repositories/recipes/paper/plots'
phi <- 1.618
width <- 4.9823
height <- width/phi
filename <- file.path(plots_dir, 'users_many_ratings.tex')
tikz(file = filename, width = width, height = height)
ggplot(df) + aes(x=ratings, y=users) + geom_line() + geom_point() +
  ggtitle("Number of users with number of ratings >= x") +
  xlab("x") +
  ylab("Users") +
  theme(plot.title = element_text(size=12))
dev.off()


# Prepare data for decision tree

r_n <- normalize(Recipes)

# We want to obtain the reviews with a low normalized rating first
reviews_low <- which(r_n@data < 0, arr.ind = TRUE)
#reviews_neutral <- which(r_n@data == 0, arr.ind = TRUE)
reviews_high <- which(r_n@data > 0, arr.ind = TRUE)

hist(r_n@data[reviews_low])
hist(r_n@data[reviews_high])

r_m <- colMeans(r_n, na.rm = TRUE)

require(hashmap)

recipe_names <- Recipes@data@Dimnames[1:10][[2]]
map <- hashmap(recipe_names, 1:length(recipe_names))

# Remove recipes with small number of ratings

no_recipe_ratings <- colSums(r_b)

selectRecipes <- function(data, users.min_ratings, recipes.min_ratings) {
  data <- data[rowSums(data[, -1]) > users.min_ratings,
               colSums(data[-1,]) > recipes.min_ratings]
  recipes_num_rating <- colSums(r_b)
  vals <- recipes_num_rating[recipes_num_rating >= recipes.min_ratings]
  cols <- names(vals)
  data[,map[[cols]]]
}

s <- selectRecipes(RecipeRatings, recipes.min_ratings = 10)  # Select recipes >= 5 ratings

hist(getRatings(normalize(s)))

hist(getRatings(normalize(s, method="Z-score")))#, breaks=100)

r_n <- normalize(s, method="Z-score")  # Overwriting other attempt (clean this up)
r_m <- colMeans(r_n, na.rm = TRUE)

top_recipes <- sort(r_m, decreasing = TRUE)

hist(r_m)

# Select recipes based on average normalized rating
recipes_good <- RecipeRatings[,map[[names(r_m[r_m > 0])]]]
recipes_bad <- RecipeRatings[,map[[names(r_m[r_m < 0])]]]


nms <- c("random items", "popular items", "UBCF J10",
         "UBCF J20", "UBCF J30", "UBCF P10", "UBCF P20",
         "UBCF P30")

names(results) <- nms
