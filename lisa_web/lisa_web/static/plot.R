library(data.table)
AR   <- fread('MC00468.pwm.1kb')
E2F2 <- fread('MS00712.pwm.1kb')
GR <-   fread('MC00170.pwm.1kb')

AE <- cbind(AR$V2, E2F2$V2)
AE <- AE[apply(AE, 1, function(x) all(x<10000)),]

AG <- cbind(AR$V2, GR$V2)
AG <- AG[apply(AG, 1, function(x) all(x<10000)),]

print(head(AE))
print(head(AG))

png('motif_scatterplot.png', width=1500, height=800)
par(mfrow=c(1,2), font=2, cex=1)
plot(AE[,1], AE[,2], pch=19, col='blue', xlab='AR', ylab='E2F2')
plot(AG[,1], AG[,2], pch=19, col='blue', xlab='AR', ylab='GR')
dev.off()

