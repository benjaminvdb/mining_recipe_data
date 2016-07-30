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


# Select matrix with given properties
selectRows <- function(data, min_users, min_ratings) {
  data <- data[rowCounts(data) >= min_users,]
  data <- data[,colSums(data) >= min_ratings]
  data 
}