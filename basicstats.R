library(data.table)
setwd("~/Documents/Northwestern/EECS349/steam-game-recommender/")
game.data <- fread("./data/final_train.csv", header = T)
setnames(game.data, paste("V", names(game.data), sep = ""))

game.count <- data.table(t(apply(game.data, 2, sum)))