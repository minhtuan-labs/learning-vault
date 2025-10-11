@echo off
dotnet tool install -g dotnet-reportgenerator-globaltool
dotnet add package coverlet.msbuild
dotnet add package ReportGenerator
dotnet test /p:CollectCoverage=true /p:CoverletOutputFormat=opencover /p:CoverletOutput=./CoverageResults/
reportgenerator -reports:./CoverageResults/coverage.opencover.xml -targetdir:coverage-report -reporttypes:Html
