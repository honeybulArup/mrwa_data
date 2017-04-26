library(shiny)
setwd("C://Users/Robert.Honeybul/Desktop/mrwa_data/")

data = read.csv("data/master_files/data.csv")

round2dec <- function(no){
  return(round(no, 2))
}

# Define UI for application that draws a histogram
ui <- fluidPage(
   
   # Application title
  
  HTML("<center><h4>Route Analysis</h4></center>"),
  HTML("<center>"),
  selectInput('routeSelect', label="Route", data$Route, width='400'),
  actionButton("run", "See Data for Route"),
  
  plotOutput('sectionVal'),
  
  plotOutput('journeyPlot'),
   
  plotOutput('amSpeed'),
   
  plotOutput('pmSpeed'),
   
  plotOutput('npi'),
  
  dataTableOutput("table"),
  HTML("</center>")
     
)

# Define server logic required to draw a histogram
server <- function(input, output) {
  
  observeEvent(input$run, {
    
    route_ii = input$routeSelect
    
    jt_rel = data$JT_Normal
    spd_am = data$Speed_am_Normal
    spd_pm = data$Speed_pm_Normal
    npi = data$NPI_Normal
    secVal = data$Section.Value
    
    jt_d <- density(jt_rel, na.rm=T)
    spd_am_d <- density(spd_am, na.rm=T)
    spd_pm_d <- density(spd_pm, na.rm=T)
    npi_d <- density(npi, na.rm=T)
    sec_d <- density(secVal, na.rm=T)
    
    index = grep(route_ii, data$Route)
    
    vals = data[index,]
    
    orderedData = data[order(data$Section.Value, decreasing = T),]
    orderedData = orderedData[-which(is.na(orderedData$Section.Value)),]
    
    orderedData[,3:ncol(orderedData)] <- apply(orderedData[, 3:ncol(orderedData)], 2, round2dec)
    
    colnames(orderedData) <- c("Route", "ROP", "Journey Reliability", "Speed % (am)", "Speed % (pm)", "NPI", "Section Value")
    
    output$sectionVal <- renderPlot({
      
      plot(sec_d, main="Route Performance")
      polygon(sec_d, col="red")
      abline(v=vals$Section.Value)
      
    })
    
    output$amSpeed <- renderPlot({
      
      plot(spd_am_d, main="Speed % Morning")
      polygon(spd_am_d, col="red")
      abline(v=vals$Speed_am_Normal)
      
    })
    
    output$pmSpeed <- renderPlot({
      
      plot(spd_pm_d, main="Speed % Afternoon")
      polygon(spd_pm_d, col="red")
      abline(v=vals$Speed_pm_Normal)
      
    })
    
    output$npi <- renderPlot({
      
      plot(npi_d, main="NPI")
      polygon(npi_d, col="red")
      abline(v=vals$NPI_Normal)
      
    })
    
    output$journeyPlot <- renderPlot({
      
      plot(jt_d, main="Journey Reliability")
      polygon(jt_d, col="red")
      abline(v=vals$JT_Normal)
      
    })    
    
    output$table <- renderDataTable({
      orderedData
    })
    
  })

}

# Run the application 
shinyApp(ui = ui, server = server)

