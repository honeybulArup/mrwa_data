
df = read.csv("data/master_files/master.csv")

colnames(df)

# print(df$Route)

speed1 = as.numeric(as.character(df$SpeedPerc1))

d <- density(speed1, na.rm = T)

plot(d, main="Density Plot of Speed Percentage")
polygon(d, col='red', border='blue')
abline(v=0.5)

#Journey Time Reliablity 
#Speed Percentage AM
#Speed Percentage PM 
#NPI efficiency