// ************************* global variables **********************************
var viz, workbook, activeSheet;

// ************************* hide grid and load vizContainer **********************************
function myFunction(){
  var x = document.getElementById("latest");
  if (x.style.display === "block") {
    x.style.display = "none";
  } else {
    x.style.display = "none";
  }
  // ************************* here should decide what kind of dashboard to load in the container **********************************
  $(loadLineGraphVizContainer);
}

// ************************* loading vizContainer for tableau **********************************
function loadLineGraphVizContainer(){
  var placeholderDiv = document.getElementById("tableauIFrame");
  var url = //"https://public.tableau.com/views/WorldIndicators/GDPpercapita";
  "http://10.11.203.70:84/t/Praxis/views/LineGraphDashBoard/LineGraphDashBoard";
  var options = {
    hideTabs: true,
    showVizHome: false,
    width: "950px",
    height: "430px",
    "Gender": ["Male,Female"],
    "From Date": "06/01/2016", //new Date(Date.UTC(2016, 06, 1)),
    "To Date": "06/01/2016", //new Date(Date.UTC(2016, 06, 1)),
    "Measure Name": "Actual Win",
  };
  viz = new tableau.Viz(placeholderDiv, url, options);
  //$(filterSingleValue);
}
