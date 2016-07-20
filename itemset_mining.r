require(arules)

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

head(quality(rules))

plot(rules, shading="order", control=list(main = "Two-key plot"))

sel <- plot(rules, measure=c("support", "lift"), shading="confidence", interactive=TRUE)
