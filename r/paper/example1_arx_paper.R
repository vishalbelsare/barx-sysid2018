setwd("~/src/barx-sysid2018")
library("jsonlite")
library("RColorBrewer")
library("HDInterval")
library("R.matlab")

#############################################################################
#############################################################################
# Load data and set up the model
plotColors = brewer.pal(8, "Dark2")
plotColors = c(plotColors, plotColors)

gridLimits <- c(-6, 6)
dataLimits <- c(-20, 20)
savePlotsToFile <- TRUE
result <- read_json("results/example1/example1_arx.json.gz", simplifyVector = TRUE)
result_matlab <- readMat("results/example1/example1_arx_workspace.mat")

#############################################################################
#############################################################################
# Compute quantities requried for plotting
# Posterior mean estimate of mixture components and the high posterior
# density intervals for the one-step ahead predictor
noBins <- floor(sqrt(result$noIterations))
noTrainData <- dim(result$regressorMatrixEstimation)[1]
noEvalData <- dim(result$regressorMatrixValidation)[1]
systemOrder <- sum(result$guessedOrder)

noComp <- dim(result$mixtureMeans)[2]
estMixComp <- matrix(0, nrow = length(result$gridPoints), ncol = noComp)

for (i in 1:length(result$gridPoints)) {
  for (j in 1:noComp) {
    compOnGrid <- dnorm(result$gridPoints[i],
                        mean = result$mixtureMeans[, j],
                        sd = sqrt(result$mixtureVariances[, j]))
    estMixComp[i, j] <- mean(result$mixtureWeights[, j] * compOnGrid)
  }
}

oneStepPredHPD <- matrix(0, nrow = dim(result$predictiveMean)[2], ncol = 4)
for (i in 1:dim(result$predictiveMean)[2]) {
  res <- hdi(density(result$predictiveMean[, i]), credMass = 0.95, allowSplit = TRUE)
  oneStepPredHPD[i, ] <- c(res[1], res[2])
}

#############################################################################
#############################################################################
# Code for plotting
if (savePlotsToFile) {cairo_pdf("results/example1_arx_paper.pdf", height = 8, width = 8)}
layout(matrix(c(1, 1, 1, 2, 2, 2, 3, 4, 5), 3, 3, byrow = TRUE))
par(mar = c(4, 5, 1, 1))

#############################################################################
## Plot of validation data together with one-step ahead predictor
grid <- seq(1, 300)

plot(grid,
  result$yValidation[1:300],
  col = plotColors[8],
  type = "p",
  pch = 19,
  cex = 1,
  bty = "n",
  xlab = "time",
  ylab = "observation",
  xlim = c(0, 300),
  ylim = dataLimits,
  cex.lab = 1.5,
  cex.axis = 1.5
)

polygon(
  c(grid, rev(grid)),
  c(oneStepPredHPD[1:300, 1], rev(oneStepPredHPD[1:300, 2])),
  border = NA,
  col = rgb(t(col2rgb(plotColors[2])) / 256, alpha = 0.5)
)

lines(grid, oneStepPredHPD[1:300, 1], col = plotColors[2], lwd = 0.5)
lines(grid, oneStepPredHPD[1:300, 2], col = plotColors[2], lwd = 0.5)

lines(grid,
      result_matlab$yhat[-c(1:6)][1:300],
      col = plotColors[3],
      lwd = 1
)

#############################################################################
# Plot of the the posterior estimate of the filter/model coefficients
hist(
  result$modelCoefficients[, 1],
  breaks = noBins,
  main = "",
  freq = F,
  col = rgb(t(col2rgb(plotColors[3])) / 256, alpha = 0.25),
  border = NA,
  xlab = "system coefficients",
  ylab = "posterior probability",
  xlim = c(-2, 1.5),
  ylim = c(0, 20),
  cex.lab = 1.5,
  cex.axis = 1.5
)

lines(density(result$modelCoefficients[, 1], kernel = "e"),
      lwd = 2,
      col = plotColors[3])

for (i in 2:systemOrder) {
  hist(
    result$modelCoefficients[, i],
    breaks = noBins,
    freq = F,
    col = rgb(t(col2rgb(plotColors[2 + i])) / 256, alpha = 0.25),
    border = NA,
    add = TRUE
  )
  lines(density(result$modelCoefficients[, i], kernel = "e"),
          lwd = 2,
          col = plotColors[2 + i])
}

for (i in 2:length(result_matlab$a)){
  abline(v = result_matlab$a[i], lty = "dotted")
}

for (i in 1:length(result_matlab$b)){
  abline(v = result_matlab$b[i], lty = "dotted")
}

#############################################################################
# Plot of the posterior estimate of priors
hist(
  result$modelCoefficientsPrior,
  breaks = noBins,
  main = "",
  freq = F,
  col = rgb(t(col2rgb(plotColors[8])) / 256, alpha = 0.25),
  border = NA,
  xlab = expression(sigma[f]),
  ylab = "posterior estimate",
  xlim = c(0.4, 1.4),
  ylim = c(0, 5),
  cex.lab = 1.5,
  cex.axis = 1.5
)

lines(
  density(
    result$modelCoefficientsPrior,
    kernel = "e",
    from = 0.4,
    to = 1.4
  ),
  lwd = 2,
  col = plotColors[8]
)

#############################################################################
# Plot of the posterior estimate of priors
hist(
  result$mixtureMeansPrior,
  breaks = noBins,
  main = "",
  freq = F,
  col = rgb(t(col2rgb(plotColors[8])) / 256, alpha = 0.25),
  border = NA,
  xlab = expression(sigma[mu]),
  ylab = "posterior estimate",
  xlim = c(-0.5, 1.5),
  cex.lab = 1.5,
  cex.axis = 1.5
)

lines(
  density(
    result$mixtureMeansPrior,
    kernel = "e",
    from = -0.5,
    to = 1.5
  ),
  lwd = 2,
  col = plotColors[8]
)

#############################################################################
# Plot of the posterior estimate of priors
hist(
  result$mixtureWeightsPrior,
  breaks = noBins,
  main = "",
  freq = F,
  col = rgb(t(col2rgb(plotColors[8])) / 256, alpha = 0.25),
  border = NA,
  xlab = expression(e[0]),
  ylab = "posterior estimate",
  xlim = c(0, 0.6),
  ylim = c(0, 10),
  cex.lab = 1.5,
  cex.axis = 1.5
)

lines(
  density(
    result$mixtureWeightsPrior,
    kernel = "e",
    from = 0,
    to = 0.6
  ),
  lwd = 2,
  col = plotColors[8]
)

if (savePlotsToFile) {
  dev.off()
}

#############################################################################
#############################################################################
# Compute model fits

predError <- sum((rowMeans(oneStepPredHPD) - result$yValidation) ^ 2)
evalObsVar <- sum((result$yValidation - mean(result$yValidation)) ^ 2)
(modelFitBARX <- 100 * (1 - predError / evalObsVar))

predError <- sum((result_matlab$yhat[-c(1:6)] - result$yValidation) ^ 2)
evalObsVar <- sum((result$yValidation - mean(result$yValidation)) ^ 2)
(modelFitARX <- 100 * (1 - predError / evalObsVar))
