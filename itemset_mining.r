require(arules)
require(arulesViz)
require(tikzDevice)

base_dir = '/Users/benny/Repositories/recipes/paper'
tables_dir = file.path(base_dir, 'tables')
plots_dir = file.path(base_dir, 'plots')

saveTikz <- function(plt, filename, width = 4.9823, ratio = 1.618) {
  height <- width/ratio
  filename <- file.path(plots_dir, filename)
  tikz(file = filename, width = width, height = height)
  replayPlot(plt)
  dev.off()
}

# Load data
filename <- '/Users/benny/Repositories/recipes/data/recipes.single'
Recipes = read.transactions(filename, format='single', sep=',', cols=seq(1, 2))

# Create summary
summary(Recipes)

# Mine rules using Apriori
rules <- apriori(Recipes, parameter=list(support=0.02, confidence=0.5))

# Top 3 rules according to lift
inspect(head(sort(rules, by ="lift"), 10))

top10 <- as(head(sort(rules, by ="lift"), 10), 'data.frame')
write.table(top10, file.path(tables_dir, 'rules_top10.dat'), sep = ';', col.names = TRUE, row.names = FALSE)

# Scatter plot
plot(rules)

# The quality() function prints out quality scores for rules
head(quality(rules))

# Two-key plot plots support against confidence, with the 'order'
# indicated by color, which is the number of items
plot(rules, shading="order", control=list(main = "Two-key plot"))

# Interactive plot
sel <- plot(rules, measure=c("support", "lift"), shading="confidence", interactive=TRUE)

# Select rules with confidence > 0.9
subrules <- rules[quality(rules)$confidence > 0.9]

plot(subrules, method="matrix", measure="lift")

# reordering rows and columns in the matrix such that rules with similar values of the interest measure are presented closer together
plot(subrules, method="matrix", measure="lift", control=list(reorder=TRUE))

# Same thing, interactive
plot(subrules, method="matrix", measure="lift", control=list(reorder=TRUE), interactive=TRUE)

# Plot in 3D (less intuitive!)
plot(subrules, method="matrix3D", measure="lift", control=list(reorder=TRUE))

# Two measures combined in one coloring grid
plot(subrules, method="matrix", measure=c("lift", "support"), control=list(reorder=TRUE))

plot(subrules, method="matrix", measure=c("confidence", "support"), control=list(reorder=TRUE))

# Grouping statistically dependent consequents (LHS) allows to plot many more rules
many_rules <- apriori(Recipes, parameter=list(support=0.01, confidence=0.3))
plot(many_rules, method="grouped")

# Select some rules with high lift
subrules2 <- head(sort(rules, by="lift"), 20)

# Plotting makes things cluttered...
#plot(subrules2, method="graph")

# ... while vertices = itemsets and edges = rules is pretty nice
plot(subrules2, method="graph", control=list(type="itemsets"))

# Export to Gephi!!
# NOTE: here we quickly found there seem to be two clusterd ('hartig' en 'zoetig'?)
saveAsGraph(head(sort(rules, by="lift"),200), file="rules2.graphml")

plot(subrules2, method="paracoord", control=list(reorder=TRUE))

# Double decker plot
oneRule <- sample(rules, 1)
inspect(oneRule)
plot(oneRule, method="doubledecker", data = Recipes)

set.seed(1234)
s <- sample(Recipes, 2000)
d <- dissimilarity(s, method = "Jaccard")
library("cluster")
clustering <- pam(d, k = 16)
plot(clustering)

# Prediction based on clustering
allLabels <- predict(s[clustering$medoids], Recipes, method = "Jaccard")
cluster <- split(Recipes, allLabels)

itemFrequencyPlot(cluster[[1]], population = s, support = 0.05)
itemFrequencyPlot(cluster[[2]], population = s, support = 0.05) # Sweet pastries?
itemFrequencyPlot(cluster[[3]], population = s, support = 0.05) # Greek?
itemFrequencyPlot(cluster[[4]], population = s, support = 0.05)
itemFrequencyPlot(cluster[[5]], population = s, support = 0.05) # Apple based sweet pasties?
itemFrequencyPlot(cluster[[6]], population = s, support = 0.05)
itemFrequencyPlot(cluster[[7]], population = s, support = 0.05)
itemFrequencyPlot(cluster[[8]], population = s, support = 0.05)

clustering <- pam(d, k = 2)
allLabels <- predict(s[clustering$medoids], Recipes, method = "Jaccard")
cluster <- split(Recipes, allLabels)
itemFrequencyPlot(cluster[[1]], population = s, support = 0.05) # Hartig
itemFrequencyPlot(cluster[[2]], population = s, support = 0.05) # Zoet

# Supplement a recipe
chickenRules <- subset(rules, subset = rhs %in% "chicken")

# Cool result:
# 461 {carrot,celery stalks} => {chicken} 0.01029268 0.5436782 2.993976

require(ggplot2)
require(RColorBrewer)
require(plyr)


# Plot ingredient distribution
y <- sort(itemFrequency(Recipes, type = 'abs'), decreasing = TRUE)
n <- length(y)
x <- 1:n

# Data
data <- data.frame(x=x, y=y, group='Data')

# Fit linear line on logarithmic data
fit <- lm(log(y) ~ x, data=data.frame(x=x, y=y))
fitvals <- exp(fit$fitted.values)
data2 <- data.frame(x=x, y=fitvals, group='Regression')

# Plot
library(tikzDevice)
plots_dir = '/Users/benny/Repositories/recipes/paper/plots'
phi <- 1.618
width <- 4.9823
height <- width/phi
filename <- file.path(plots_dir, 'ingredient_frequencies.tex')
tikz(file = filename, width = width, height = height)
ggplot() + aes(x=x, y=y, color=group) +
  geom_point(data=data, size=.5) +
  geom_line(data=data2, linetype='dashed', size=.8) +
  scale_y_log10() +
  scale_color_brewer(palette = 'Set1') +
  ggtitle('Ingredient frequencies on a logarithmic scale') +
  labs(x='Ingredients', y='Frequency') +
  theme(plot.title = element_text(size=12),
        legend.title = element_blank(),
        legend.justification=c(1,1),
        legend.position=c(1,1))
dev.off()

# Save table
mod_stargazer <- function(output.file, ...) {
  output <- capture.output(stargazer(...))
  cat(paste(output, collapse = "\n"), file=output.file, sep="\n", append=FALSE)
}

tables_dir <- '/Users/benny/Repositories/recipes/paper/tables'
top <- sort(itemFrequency(Recipes, type='abs'), decreasing = TRUE)
topN <- top[1:10]
t <- data.frame(Ingredient=names(topN), Frequency=unname(topN), Relative=unname(topN)/sum(top))
filename <- file.path(tables_dir, 'ingredients_top10.tex')
mod_stargazer(filename, t, summary=FALSE, digit.separator=' ')

filename <- filename <- file.path(tables_dir, 'ingredients_top10.dat')
write.table(t, file = filename, quote = FALSE, sep = ";",
            row.names = FALSE, col.names = TRUE)

library(party)

f <- function(v) {v <= 1000}

a <- as(Recipes[1:2000], 'matrix')
b <- cbind(a, sapply(1:2000, f))
dimnames <- attr(b, 'dimnames')
dimnames[[2]][404] <- 'class'
attr(b, 'dimnames') <- dimnames

data = data.frame(b)

#tree <- ctree(class ~ pepper + salt, data = data)

tinfo <- as(transactionInfo(Recipes), 'list')[[1]]  # Get list of index -> tid
tid_to_index <- hashmap(tinfo, sapply(1:length(tinfo), toString))
good_tids <- unlist(recipes_good@data@Dimnames[[2]])
bad_tids <- unlist(recipes_bad@data@Dimnames[[2]])

GoodRecipes <- Recipes[tid_to_index[[good_tids]]]
BadRecipes <- Recipes[tid_to_index[[bad_tids]]]

good <- as(GoodRecipes, 'matrix')
bad <- as(BadRecipes, 'matrix')

good <- cbind(good, 1)
bad <- cbind(bad, 2)

data <- rbind(good, bad)

dimnames <- attr(data, 'dimnames')
dimnames[[2]][404] <- 'class'
attr(data, 'dimnames') <- dimnames

write.csv(data, 'good_bad.csv')

# Frequency of item pairs
X <- as(Recipes, 'matrix')
X <- sapply(as.data.frame(X), as.numeric)
out <- crossprod(X)  # Same as: t(X) %*% X
diag(out) <- 0  

library("recommenderlab")
algorithms <- list("random items" = list(name = "RANDOM", param = NULL),
                   "popular items" = list(name = "POPULAR", param = NULL),
                   "association rules (0.001)" = list(name = "AR", param = list(support = 0.001,confidence=0.1, maxlen=3)))
                   
                  #"association rules (0.01)" = list(name = "AR", param = list(support = 0.01)),
                  #"association rules (0.05)" = list(name = "AR", param = list(support = 0.05)),
                  #"association rules (0.1)" = list(name = "AR", param = list(support = 0.1)),
                  #"item-based CF (k=3)" = list(name = "IBCF", param = list(k = 3)),
                  #"item-based CF (k=5)" = list(name = "IBCF", param = list(k = 5)),
                  #"item-based CF (k=10)" = list(name = "IBCF", param = list(k = 10)),
                  "item-based CF (k=20)" = list(name = "IBCF", param = list(k = 20)),
                  #"item-based CF (k=30)" = list(name = "IBCF", param = list(k = 30)),
                  "item-based CF (k=40)" = list(name = "IBCF", param = list(k = 40)),
                  #"item-based CF (k=50)" = list(name = "IBCF", param = list(k = 50)),
                  "item-based CF (k=200)" = list(name = "IBCF", param = list(k = 200)))
                  #"item-based CF (k=40)" = list(name = "IBCF", param = list(k = 40, method='dice')),
                  #"item-based CF (k=200)" = list(name = "IBCF", param = list(k = 200, method='dice')))
                  #"item-based CF (k=402)" = list(name = "IBCF", param = list(k = 402)))
                   #"user-based CF (Jaccard)" = list(name = "UBCF", param = list(nn = 50, method = 'jaccard')))
                   #"user-based CF (Pearson)" = list(name = "UBCF", param = list(nn = 50, method = 'pearson')))

Recipes_binary <- as(Recipes, 'binaryRatingMatrix')
Recipes_binary <- Recipes_binary[rowCounts(Recipes_binary) > 5]

scheme <- evaluationScheme(Recipes_binary, method="split", train=.9, k=1, given=2)

results2 <- evaluate(scheme, algorithms, progress = TRUE,
                    type = "topNList", n=c(1,3,5,10))


nms <- c('Random items', 'Popular items', 'AR s=0.01',
         'AR s=0.05', 'AR s=0.1', 'IBCF k=20', 'IBCF k=40',
         'IBCF k=200')
names(results2) <- nms

plot(results2, annotate=c(1,3,7))
title('ROC curve for ingredient recommendation')
plt <- recordPlot()
saveTikz(plt, 'ingredients_recommendations_given2.tex')
