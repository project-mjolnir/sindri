# Sindri Changelog


## Version 0.2.11 (2021-05-31)

Maintenance release with the following changes:

* Fix null values not being handled properly in JSON on recent pandas versions
* Use relative links in archive table to fix breakage when not at the site root
* Fix NumPy deprecations and handle pandas deprecation warning
* Add/update version constraints in dependency requirements
* Add missing Sindri 0.2.10 release in Changelog



## Version 0.2.10 (2021-09-07)

Maintenance release with the following changes:

* Re-order plot sections to match usage
* Modify color coding and thresholds to preferred values



## Version 0.2.9 (2020-10-23)

Maintenance release with the following changes:

* Improve performance of website generation
* Update default config to point to new server
* Ignore errors when parsing the sensor log file



## Version 0.2.8 (2020-05-15)

Bugfix release with the following changes:

* Fix incorrect calculation/rounding of CRC and trigger count values
* Change net charge calculation to use actual daily Ah values
* Lengthen refresh period from 5 min to 10 min for long-fuse data
* Improve compat of date parser



## Version 0.2.7 (2020-04-29)

Compat and bugfix release with the following changes:

* Handle bytes values as GB rather than B as used by Brokkr >=0.3.x
* Fix warning parsing dates with timezone offset appended



## Version 0.2.6 (2020-03-20)

Compat and bugfix release with the following changes:

* Update search paths to find Brokkr 0.3.0 telemetry and log data for hamma
* Automatically select latest log when multiple systems' logs are found
* Avoid requiring network-online service that incurs a large wait at startup



## Version 0.2.5 (2020-01-24)

Bugfix release with the following changes:

* Add net power and 24 hour net charge calculated columns to processed data
* Add net columns to raw data and color-code
* Add 24 h net charge to history plot
* Fix spurious Unicode BOM in Readme



## Version 0.2.4 (2019-12-11)

Bugfix release with the following changes:

* Ensure website template is properly packaged with source and binary dists
* Fix fragile paths to readme and version file in setup.py
* Remove no longer needed matplotlib spec in requirements file



## Version 0.2.3 (2019-11-18)

Bufix release with the following changes:

* Fix issue with archive table on sensor page not being updated with new data
* Add delay before first rebuild in test mode to avoid any concurrency issues



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
