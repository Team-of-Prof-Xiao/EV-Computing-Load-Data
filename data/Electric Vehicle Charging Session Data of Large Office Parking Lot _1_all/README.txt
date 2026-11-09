*** Electric vehicle charging data of the a.s.r. pilot location of the SmoothEMS met GridShield project ***
Authors: Project Consortium of SmoothEMS met GridShield (in alphabetical order, status October 2024)
	Amperapark: Richard Kokhuis, Fabian Kusche, Bart Nijenhuis
	a.s.r. verzekeringen: Jos de Ruijter
	ElaadNL: Marisca Zweistra
	MENNEKES eMobility: Axel Schubbel, Joep van der Velden
	Kropman Installatietechniek: Kevin de Bont
	University of Twente: Gerwin Hoogsteen, Johann Hurink, Bart Nijenhuis, Baver Ozceylan, Leoni Winschermann
Contact information:

L. Winschermann (l.winschermann@utwente.nl)
University of Twente - Faculty of Electrical Engineering, Mathematics and Computer Science 
P.O. Box 217
7500 AE Enschede
The Netherlands

J.L. Hurink (j.l.hurink@utwente.nl)
University of Twente - Faculty of Electrical Engineering, Mathematics and Computer Science 
P.O. Box 217
7500 AE Enschede
The Netherlands

G. Hoogsteen (g.hoogsteen@utwente.nl)
University of Twente - Faculty of Electrical Engineering, Mathematics and Computer Science
P.O. Box 217
7500 AE Enschede
The Netherlands

*** General information ***
The data in this dataset was collected during the SmoothEMS met GridShield project (subsidized by the Dutch ministries of EZK and BZK under MOOI32005; https://elaad.nl/projecten/smoothems-met-gridshield/). It is made publically available (though non-commercially) both as project output, supplementary data for (scientific) publication and the PhD thesis of Leoni Winschermann, as well as to serve as data for other researchers to use.
The dataset corresponds to the a.s.r. living lab of the project. The living lab is an office parking lot located in Utrecht, the Netherlands, that hosts EV charging infrastructure for employees and visitors. All datapoints describe electric vehicle charging sessions recorded on-site. During the data collection period, the lease fleet of the company that hosts the parking lot was in a process of electrification. Therefore, the fleet size and average number of sessions per day increases over time. 
The data was collected between August 25th, 2020 and October 2nd, 2024. 
At the end of the measurement period, about 300 charging points were installed on-site. 

*** Data collection ***
The dataset is a combination of two datasets. 
The first dataset consists of the recorded electric vehicle charging sessions. The data is retrieved from the local energy management system provided by Kropman Installatietechniek, via an API to ElaadNL. 
The second dataset is the result of a survey held among the electric vehicle driving employees in November 2022. The survey led to a total of 90 responses, 45 of which included a charging ID that could be used to match the responses to the session data of the first dataset. An overview with survey questions and timeline can be found in the folder Survey_supplementary/.
All survey participants agreed to the publication of data collected in the research, with the exception of data that can be linked to an individual. To this end, we replace identifiers by pseudonyms, and only provide aggregated ranges for the work-home commute of EV drivers. 

*** Charging equipment ***
During data collection, up to 300 EV charging points were installed on-site. The majority of charging points is part of a charger that has a double plug setup with a total charging power capacity of 22 kW, which is reduced to 11 kW per plug if two EVs are connected. 
Out of all chargers, 23 are Mennekes Amtron Professional+ Chargers, and the rest are WeDriveSolar Wallstation 2 Duo.
They can roughly be grouped into an employee parking deck (fed with electricity by Rails B, C, E, H, J, K, M, L; about 250 charging points), MENNEKES chargers (22 out of 23 in the charging pit where the managers park, 1 at facility management), shared cars (about 6 charging points, 2 more general employee charging points, and 2 for facility management) and visitors parking (big carport and small carport are in front of the building, 26 parking spots, plus 2 accessible parking spots)
The employee parking deck infrastructure is connected to 3 transformers. Here, Rails (E,M), (C,H,K) and (B,J,L) share a transformer connection.

*** Data disclaimers ***
The charging data was collected during years of parking lot expansion and roll-out of the charging infrastructure. 
Electric vehicles in the data set are identified based on their charging ID. In the initial roll-out of the parking lot, charging was free of charge and could be started with shared charging IDs. This concerns at least IDs EV107, EV191, EV132, EV148, EV342, EV242, EV130, EV173, EV131, EV384, EV318, EV127, EV257, EV192, EV129, EV211, EV323, EV343, EV161 and EV456. Those cannot be attributed to a unique user. Furthermore, to remove initial testing and outliers, data points of sessions charging less than 1 kWh, staying for less than 10 minutes, or staying longer than 24 hours are not included in the data set.
The data collection period includes periods of (partial) COVID-19 lockdowns where the number of days an employee would work in the office was heavily restricted. This leads to dips in parking lot occupation, notably after mid-March 2020 and December 2021. See https://www.rijksoverheid.nl/onderwerpen/coronavirus-tijdlijn for more information on the corona measures taken by the government in the Netherlands (in Dutch). 
The dataset includes missing data points. This has multiple reasons. First, the data points corresponding to surveyed questions were not filled by all users. Furthermore, the data retrieved by the API at ElaadNL stems from two different charge point management systems, whose information format does not match. Therefore, we do not provide Rail and EVSE information for all datapoints as this information is not recorded and/or available in one of these systems. 
Pricing for energy charged at the parking lot changed over the collection period. Originally, charging was free of charge for the employees frequenting the parking lot. After September 1st, 2022, the price changed to 37 cents/kWh (excl. taxes). Note that the Dutch government reduced the tax rate in 2022 to 9% to account for escalating energy prices, which was reversed back to 21% on January 1st, 2023.
As the dataset is oblivious to the state of charge of the EVs, it is important to specify the control policy applied in the parking lot. In the roll-out phase, charging would occur greedily everywhere (uncontrolled charging at maximum power demanded by the EV except when capped by the power limit of the charging infrastructure). As of March 2023, a model predictive controller was deployed for the employee parking deck (and only there!) for all rails except rail M. Independently of whether or not there was solar energy available, its aim would be to charge each EV (averaged out over the population; this works as the target values are above the global average) 21 kWh by 4pm, and 23.5 kWh by 11pm. Per August 23rd, 2023, this was increased to 21 kWh by 4pm and 26 kWh by 11pm, and again after December 11th, 2023 to 23 kWh by 4pm and 26 kWh by 11pm. 
We grant no warranty for those specifications, as the living lab may occasionally have been used as pilot location for field tests for this or other projects.

Lastly, these are some starting points for using this data: each row corresponds to a charging session. start_datetime gives the start time and date (in local time; note that the Netherlands know winter and summer time, that is the time zone is UTC+01:00 during winter and UTC+02:00 during summer). end_datetime is the end time and date of the session. A total of total_energy kWh were charged during the session. The EV identifier EV_id_x makes it possible to filter out the sessions for a single user. 

*** Published works using the data set ***
Some academic publications made use of (parts of) this data set before the data was published. Those are:

	- B. Nijenhuis, L. Winschermann, N. Bañol Arias, G. Hoogsteen and J.L. Hurink: "Protecting the distribution grid while maximizing EV energy flexibility with transparency and active user engagement," CIRED Porto Workshop 2022: E-mobility and power distribution systems, Hybrid Conference, Porto, Portugal, 2022, pp. 209-213
	- L. Winschermann, N. Bañol Arias, G. Hoogsteen, J. Hurink: "Assessing the value of information for electric vehicle charging strategies at office buildings," Renewable and Sustainable Energy Reviews, 185, p. 113600
	- N. B. Arias, J. S. Giraldo, J. C. López, G. Hoogsteen and J. Hurink: "EV Allocation and Charging within Parking Lots Using a Locational Marginal Pricing Mechanism," 2023 IEEE PES Innovative Smart Grid Technologies Europe (ISGT EUROPE), Grenoble, France, 2023, pp. 1-5
	- L. Winschermann, G. Hoogsteen, J.L. Hurink: "Integrating Guarantees and Veto-Buttons into the Charging of Electric Vehicles at Office Buildings," 2023 IEEE PES Innovative Smart Grid Technologies Europe (ISGT EUROPE), Grenoble, France, 2023, pp. 1-5
	- G. Hoogsteen, L. Winschermann, B. Nijenhuis, N. Bañol Arias, J.L. Hurink: "Robust and Predictive Charging of Large Electric Vehicle Fleets in Grid Constrained Parking Lots," 2023 IEEE International Conference on Communications, Control, and Computing Technologies for Smart Grids (SmartGridComm), Glasgow, United Kingdom, 2023, pp. 1-6
	- L. Winschermann, M.E.T. Gerards, A. Antoniadis, G. Hoogsteen, J.L. Hurink: "Relating Electric Vehicle Charging to Speed Scaling with Job-Specific Speed Limits," 2023 [available on arXiv https://arxiv.org/abs/2309.06174, at time of data publication under peer review]
	- L. Winschermann, M.E.T. Gerards, J.L. Hurink: "Improving the optimization in model predictive controllers: Scheduling large groups of electric vehicles," 2024 [available on arXiv https://arxiv.org/abs/2403.16622, at time of data publication under peer review]
	- B. Ozceylan, G. Hoogsteen, J.L. Hurink: "A Comparative Analysis of Early Departure Buttons in Coordinated Control of EV Charging," 2024 IEEE PES Innovative Smart Grid Technologies Europe (ISGT EUROPE), Croatia, 2024 [proceedings not available yet at time of data publication]
	- L. Winschermann, M. Günzel, K.-H. Chen, J. Hurink: "[title omitted]," [currently under (double blind) peer review]
	- L. Winschermann, G. Hoogsteen, J. Hurink: "Making Tough Choices: Picking Robust Electric Vehicle Schedules among Optimal Solutions," [currently under peer review]

We do not intend to regularly update this list, as future publications may cite the data set directly.

*** Dataset explanation ***
Each row in the dataset corresponds to a single EV charging session. Columns specify:

"EV":
EV_id_x    			: EV identifier pseudonym, based on the registered charging ID.

"measurement":
start_datetime			: Time of charger connection for this charging session in YYYY-MM-DDThh:mm:ss format. Times are according to local time, UTC+01:00 during winter and UTC+02:00 during summer.
end_datetime			: Time of charger disconnection for this charging session in YYYY-MM-DDThh:mm:ss format. Times are according to local time, UTC+01:00 during winter and UTC+02:00 during summer.
total_energy   			: Total energy the EV charged during the charging session, in kWh.

"charging infrastructure":
rail 				: Rail or group to which charger that EV connected to is connected to. See details above.
evse_id    			: Charging station identifier.
channel				: 1 or 2, socket of the (potentially double-socketed) charging station the EV is connected to.

"survey data":
capacity_kwh          		: Battery capacity, in kWh. Based on survey response 1*)
commute_km_range_min   		: The work-home commute, single trip, in km. Lower bound of applicable range. Based on survey response  2*)
commute_km_range_max   		: The work-home commute, single trip, in km. Upper bound of applicable range. Based on survey response  2*)
EV_brand_selfreported 		: Answer provided to question of EV brand. Direct input from survey.
EV_model_selfreported 		: Answer provided to question of EV model. Direct input from survey.
capacity_kWh_selfreported 	: Answer provided to question of EV battery capacity. Direct input from survey.
ownership			: Either 'Gekocht', 'Privaat geleased', 'Door werkgever geleased', 'Anders, namelijk' (=bought, privately leased, leased by employer, else namely). Multiple choice input from survey.

1*) Those datapoints were processed based on the survey input. See the comments in https://github.com/lwinschermann/OfficeEVparkingLot/blob/main/survey_data_process.py (commit bc4dd80) for details.
2*) Those datapoints were processed based on the survey input.

*** License ***
This data is shared under the Attribution-NonCommercial-ShareAlike (CC BY-NC-SA) License. Before distributing or sharing (remixes, tweaks or transforms of) this data, please consult any contact person of this dataset.