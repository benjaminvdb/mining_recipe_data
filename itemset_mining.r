require(arules)
require(arulesViz)

# Load data
filename <- '/Users/benny/Repositories/recipes/data/recipes.basket'
Recipes = read.transactions(filename, format='basket', sep=',')

# Create summary
summary(Recipes)

# Mine rules using Apriori
rules <- apriori(Recipes, parameter=list(support=0.01, confidence=0.5))

# Top 3 rules according to lift
inspect(head(sort(rules, by ="lift"),100))

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
saveAsGraph(head(sort(rules, by="lift"),1000), file="rules.graphml")

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