# Sindri Changelog


## Version 0.2.2 (2019-11-04)

Bufix release with the following changes:

* Fix serious pandas bug with not replacing NaN values correctly in plot data
* Harmonize bullet characters in changelog



## Version 0.2.1 (2019-11-02)

Bufix and refinement release with the following changes:

* Revise UI text to inform user about dynamic updates and increase discoverability
* Add button to data section with link to current day's data
* Increase and refine ranges and color tables based on increased charge targets
* Reduce update frequency to 10 minutes to align with Github cache time



## Version 0.2.0 Final (2019-10-29)

Final version of major upgrade incorporating additional new features, enhancements and numerous bug fixes and refactoring changes.

New frontend features and enhancements:
* Add interactive strip plot to daily data page
* Add responsive control UI to daily data page
* Add optional alert popup for when data cannot be loaded or is corrupted
* Add ability to request a temp or custom cache dir (eg for concurrent builds)
* Refine table styling, UI text and more

Backend improvements:
* Fix links to download raw CSVs
* Fix multiple bugs building and deploying on Pi 3 and 4
* Refine and fix bugs with Sindri service installation
* Improve error and NAN handling in both backend and frontend
* Numerous varied refactoring improvements
* Release packaging



## Version 0.2.0 Preview (2019-10-25)

Preview of major upgrade introducing numerous new features and capabilities, particularly for webserver.

New frontend features:
* Dynamic, interactive Javascript-based visualization with Plotly and D3.js
* Add dynamic status plot dashboard
* Add raw data status table
* Add plotly-powered interactive stripchart
* Add realtime log output
* Add archive data listing
* Add dynamic daily data pages with full data table
* Add expanded pages for log and archival

Backend improvements:
* Generate all data separately from generating site
* Seperate site configuration from backend processing
* Add data processing backend and numerous calculated columns
* Refine layout and styling
* Add site build information
* Improve command-line API and functionality
* Major refactoring in all areas
* Reorganize package for a cleaner layout



## Version 0.1.0 (2019-10-06)

Initial deployed release on the Pi for GHP, with the following features:

* Automatically, continuously generate Mjolnir website
* Output timestamp and formatted current status data table
* Render plots of all params over time
* Automate install of Sindri service
* Basic but functional command line interface
